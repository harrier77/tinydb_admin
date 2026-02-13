from flask import Flask, render_template, jsonify, request
from tinydb import TinyDB, Query
import json

app = Flask(__name__)

@app.template_filter('tojson_pretty')
def tojson_pretty(value):
    return json.dumps(value, indent=2, ensure_ascii=False)

def get_db():
    return TinyDB('database.json')

def get_array_fields(doc):
    """Ritorna i campi del documento che sono array di oggetti (sottocollezioni)"""
    arrays = {}
    for key, value in doc.items():
        if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
            arrays[key] = value
    return arrays

def build_breadcrumb(path, current_doc=None):
    """
    Costruisce la lista breadcrumb [(url, label), ...] dal path /browse/...
    Nasconde 'doc' e 'field' nei label, ma mantiene 'doc' nell'URL.
    Usa 'nome' del documento se disponibile.
    """
    if not path:
        return [('/', 'Home')]
    
    parts = path.split('/')
    breadcrumb = [('/', 'Home')]
    
    current_path_parts = []
    i = 0
    
    while i < len(parts):
        part = parts[i]
        if not part:
            i += 1
            continue
        
        # Aggiungi la parte al path corrente (per URL)
        current_path_parts.append(part)
        
        # Salta 'doc' e 'field' solo per la LABEL (non per l'URL)
        if part in ('doc', 'field'):
            i += 1
            continue
        
        # Costruisci l'URL corretto
        current_url = '/browse/' + '/'.join(current_path_parts)
        
        # Determina la label
        if i == 0:
            # Prima parte: nome collezione
            label = part
        elif i >= 2 and parts[i-1] == 'doc':
            # Dopo 'doc' viene l'ID - cerca 'nome' nel documento corrente
            if current_doc and isinstance(current_doc, dict) and 'nome' in current_doc:
                label = current_doc['nome']
            else:
                label = f'#{part}'
        else:
            # Campi, array names, index, ecc.
            label = part
        
        # L'ultimo elemento non ha URL (è la pagina corrente)
        if i == len(parts) - 1:
            breadcrumb.append((None, label))
        else:
            breadcrumb.append((current_url, label))
        
        i += 1
    
    return breadcrumb

@app.route('/')
def index():
    db = get_db()
    tables = list(db.tables())
    return render_template('base.html', tables=tables)

@app.route('/browse/<path:path>')
def browse(path):
    db = get_db()
    tables = list(db.tables())
    
    # Parsing del path
    # Formati supportati:
    # - /tabella
    # - /tabella/doc/id
    # - /tabella/doc/id/array_name
    # - /tabella/doc/id/array_name/array_index
    parts = path.split('/')
    
    current_table = parts[0] if parts else None
    current_doc_id = None
    current_doc = None
    documents = []
    nested_levels = []
    table = None
    
    
    # Carica documenti della tabella
    if current_table:
        table = db.table(current_table)
        documents = table.all()
    
    # Analisi del path
    if len(parts) >= 2 and table is not None:
        if parts[1] == 'doc' and len(parts) >= 3:
            # Navigazione: /tabella/doc/id
            try:
                current_doc_id = int(parts[2])
            except:
                current_doc_id = parts[2]
            
            current_doc = table.get(doc_id=current_doc_id)
            
            # Controlla se è richiesto un elemento di un array
            if current_doc and isinstance(current_doc, dict) and len(parts) >= 5:
                array_name = parts[3]
                array_data = current_doc.get(array_name) if hasattr(current_doc, 'get') else None
                
                if isinstance(array_data, list):
                    try:
                        array_index = int(parts[4])
                        if 0 <= array_index < len(array_data):
                            array_item = array_data[array_index]
                            nested_levels.append({
                                'type': 'array_document',
                                'index': array_index,
                                'document': array_item,
                                'array_name': array_name
                            })
                            
                            # Navigazione nei campi dell'elemento array
                            if len(parts) >= 6:
                                field_path = parts[5:]
                                current_value = array_item
                                field_name = field_path[0]
                                
                                # Naviga nel path dei campi
                                for i, field in enumerate(field_path):
                                    if isinstance(current_value, dict) and field in current_value:
                                        current_value = current_value[field]
                                    elif isinstance(current_value, list) and field.isdigit():
                                        idx = int(field)
                                        if 0 <= idx < len(current_value):
                                            current_value = current_value[idx]
                                        else:
                                            current_value = None
                                            break
                                    else:
                                        current_value = None
                                        break
                                
                                if current_value is not None:
                                    # Determina il tipo di campo
                                    field_type = 'simple'
                                    if isinstance(current_value, dict):
                                        field_type = 'object'
                                    elif isinstance(current_value, list):
                                        field_type = 'array'
                                    
                                    nested_levels.append({
                                        'type': 'field_value',
                                        'field_name': field_name,
                                        'field_value': current_value,
                                        'field_type': field_type,
                                        'parent_name': f"{array_name}[{array_index}]"
                                    })
                    except:
                        pass
                
                # Navigazione nei campi del documento principale (non array)
                if len(parts) >= 5 and parts[3] == 'field':
                    field_path = parts[4:]
                    current_value = current_doc
                    field_name = field_path[0]
                    
                    # Naviga nel path dei campi
                    for i, field in enumerate(field_path):
                        if isinstance(current_value, dict) and field in current_value:
                            current_value = current_value[field]
                        elif isinstance(current_value, list) and field.isdigit():
                            idx = int(field)
                            if 0 <= idx < len(current_value):
                                current_value = current_value[idx]
                            else:
                                current_value = None
                                break
                        else:
                            current_value = None
                            break
                    
                    if current_value is not None:
                        # Determina il tipo di campo
                        field_type = 'simple'
                        if isinstance(current_value, dict):
                            field_type = 'object'
                        elif isinstance(current_value, list):
                            field_type = 'array'
                        
                        nested_levels.append({
                            'type': 'field_value',
                            'field_name': field_name,
                            'field_value': current_value,
                            'field_type': field_type,
                            'parent_name': f"Documento {current_doc_id}"
                        })
    
    # Trova array di oggetti nel documento corrente (per mostrare come sottocollezioni)
    array_collections = {}
    if current_doc:
        array_collections = get_array_fields(current_doc)
    
    # Rileva se siamo su un item di array finale
    # È un array item solo se l'ultima parte è un numero preceduto da un nome (non 'doc' o 'field')
    # Es: /collezione/doc/4/personaggi/0 → è array item (0 è indice di 'personaggi')
    # Es: /collezione/doc/4 → NON è array item (4 è doc_id)
    is_array_item = False
    item_index = None
    item_parent_name = None
    current_array = None  # Lista completa degli elementi array
    current_array_name = None
    
    if parts and parts[-1].isdigit() and len(parts) >= 2:
        prev_part = parts[-2]
        # È array item solo se il precedente NON è 'doc' o 'field'
        if prev_part not in ('doc', 'field'):
            is_array_item = True
            try:
                item_index = int(parts[-1])
                item_parent_name = prev_part
                # Estrai l'array completo dal documento
                if current_doc and isinstance(current_doc, dict):
                    current_array = current_doc.get(item_parent_name)
                    current_array_name = item_parent_name
            except (ValueError, IndexError):
                is_array_item = False
    
    # Genera breadcrumb con accesso al documento corrente per il nome
    breadcrumb = build_breadcrumb(path, current_doc)
    
    return render_template('browser.html',
                         tables=tables,
                         current_table=current_table,
                         current_doc_id=current_doc_id,
                         current_doc=current_doc,
                         documents=documents,
                         nested_levels=nested_levels,
                         array_collections=array_collections,
                         breadcrumb=breadcrumb,
                         is_array_item=is_array_item,
                         item_index=item_index,
                         item_parent_name=item_parent_name,
                         current_array=current_array,
                         current_array_name=current_array_name)

# Route API
@app.route('/api/tables')
def api_tables():
    db = get_db()
    return jsonify(list(db.tables()))

@app.route('/api/table/<path:table_name>')
def api_table(table_name):
    db = get_db()
    table = db.table(table_name)
    documents = table.all()
    return jsonify(documents)

@app.route('/api/table/<path:table_name>/doc/<doc_id>')
def api_document(table_name, doc_id):
    db = get_db()
    table = db.table(table_name)
    try:
        doc_id = int(doc_id)
    except:
        pass
    doc = table.get(doc_id=doc_id)
    if doc:
        return jsonify(doc)
    return jsonify({'error': 'Document not found'}), 404

# Legacy routes per retrocompatibilità
@app.route('/table/<path:table_name>')
def view_table(table_name):
    return browse(table_name)

@app.route('/table/<path:table_name>/doc/<doc_id>')
def view_document(table_name, doc_id):
    return browse(f"{table_name}/doc/{doc_id}")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
