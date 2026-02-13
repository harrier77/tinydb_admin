import os
import json
from tinydb import TinyDB, Query

def inizializza():
    db = TinyDB('database.json')
    riassunti = db.table('riassunti')
    
    documento = {
        'nome': 'riassunto_prova'
    }
    doc_id = riassunti.insert(documento)
    
    print(f"Database creato con successo!")
    print(f"Documento 'riassunto_prova' creato con ID: {doc_id}")
    print(f"Totale documenti nella collezione 'riassunti': {len(riassunti)}")
    
    return db, riassunti

def popola(db=None, riassunti=None):
    if db is None:
        db = TinyDB('database.json')
    if riassunti is None:
        riassunti = db.table('riassunti')
    
    cartella_riassunti = 'riassunti_H'
    
    if not os.path.exists(cartella_riassunti):
        print(f"Errore: la cartella '{cartella_riassunti}' non esiste")
        return db, riassunti
    
    file_inseriti = 0
    
    for filename in os.listdir(cartella_riassunti):
        if filename.endswith('.json'):
            filepath = os.path.join(cartella_riassunti, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    contenuto = json.load(f)
                
                documento = {
                    'nome': filename,
                    'contenuto': contenuto
                }
                riassunti.insert(documento)
                file_inseriti += 1
                print(f"Inserito: {filename}")
            except Exception as e:
                print(f"Errore nel leggere {filename}: {e}")
    
    print(f"\nTotale file inseriti: {file_inseriti}")
    print(f"Totale documenti nella collezione 'riassunti': {len(riassunti)}")
    
    return db, riassunti

def crea_disneyland(db=None):
    if db is None:
        db = TinyDB('database.json')
    
    print("\n=== Creazione collezione Disneyland ===")
    
    # Collezione principale Disneyland
    disneyland = db.table('Disneyland')
    
    # Aree tematiche
    aree = [
        {
            'nome': 'Main Street USA',
            'tipo': 'area',
            'descrizione': 'La via principale ispirata all America di fine 800',
            'attrazioni_principali': ['Treno Disney', 'Teatro Town Square']
        },
        {
            'nome': 'Fantasyland',
            'tipo': 'area',
            'descrizione': 'Il regno delle fiabe e della magia',
            'attrazioni_principali': ['Castello della Bella Addormentata', 'Peter Pan']
        },
        {
            'nome': 'Adventureland',
            'tipo': 'area',
            'descrizione': 'Terre esotiche e avventure tropicali',
            'attrazioni_principali': ['Pirati dei Caraibi', 'Indiana Jones']
        }
    ]
    
    for area in aree:
        doc_id = disneyland.insert(area)
        print(f"  Area creata: {area['nome']} (ID: {doc_id})")
    
    # Crea Paperopoli con personaggi come array dentro il documento
    print("\n  → Creazione città con personaggi come array nidificato:")
    
    paperopoli_doc = {
        'nome': 'Paperopoli',
        'tipo': 'città',
        'descrizione': 'La città natale di Paperino e della sua famiglia',
        'paese': 'Stati Uniti (Calisota)',
        'personaggi': [
            {
                'id': 'paperino',
                'nome': 'Paperino',
                'specie': 'Anatra',
                'personalita': 'Irritabile ma dal cuore d oro',
                'occupazione': 'Disoccupato occasionale',
                'prima_apparizione': '1934',
                'alleati': ['Paperina', 'Qui Quo Qua', 'Paperone'],
                'nemici': ['Gastone', 'Rockoo']
            },
            {
                'id': 'paperina',
                'nome': 'Paperina',
                'specie': 'Anatra',
                'personalita': 'Dolce ma determinata',
                'occupazione': 'Sarta',
                'prima_apparizione': '1937',
                'alleati': ['Paperino'],
                'nemici': ['Regina dell erba amara']
            },
            {
                'id': 'paperone',
                'nome': 'Paperon de Paperoni',
                'specie': 'Anatra',
                'personalita': 'Avaro ma affettuoso con i nipotini',
                'occupazione': 'Uomo più ricco del mondo',
                'prima_apparizione': '1947',
                'patrimonio': '5 multiplikationilioni',
                'alleati': ['Qui Quo Qua', 'Batta', 'Tabacca'],
                'nemici': ['Brigitta', 'Rockerduck']
            },
            {
                'id': 'quiquoqua',
                'nome': 'Qui Quo Qua',
                'specie': 'Anatroccoli',
                'personalita': 'Vivaci, curiosi e combinaguai',
                'occupazione': 'Scolaretti',
                'prima_apparizione': '1937',
                'zio': 'Paperino',
                'zio_rico': 'Paperone',
                'squadra': 'Giovani Marmotte'
            },
            {
                'id': 'gastone',
                'nome': 'Gastone',
                'specie': 'Anatra',
                'personalita': 'Presuntuoso, vanitoso, cattivo',
                'occupazione': 'Scocciatore professionista',
                'prima_apparizione': '1952',
                'interesse': 'Paperina',
                'rivale': 'Paperino'
            },
            {
                'id': 'rockoo',
                'nome': 'Rockoo',
                'specie': 'Cane',
                'personalita': 'Malandrino, furbo, bastiancontrario',
                'occupazione': 'Bullo del quartiere',
                'prima_apparizione': '1951',
                'vittima_preferita': 'Paperino'
            }
        ]
    }
    
    paperopoli_id = disneyland.insert(paperopoli_doc)
    print(f"    Paperopoli creata con {len(paperopoli_doc['personaggi'])} personaggi (ID: {paperopoli_id})")
    
    # Crea Topolinia con personaggi come array dentro il documento
    topolinia_doc = {
        'nome': 'Topolinia',
        'tipo': 'città',
        'descrizione': 'La città dove vivono Topolino e i suoi amici',
        'paese': 'Stati Uniti (Mouseton)',
        'personaggi': [
            {
                'id': 'topolino',
                'nome': 'Topolino',
                'specie': 'Topo',
                'personalita': 'Allegra, ottimista, coraggiosa',
                'occupazione': 'Tutto fare',
                'prima_apparizione': '1928',
                'fidanazata': 'Minnie',
                'amico_migliore': 'Pippo',
                'mascotte_disney': True
            },
            {
                'id': 'minnie',
                'nome': 'Minnie',
                'specie': 'Topa',
                'personalita': 'Dolce, elegante, creativa',
                'occupazione': 'Maestra di musica',
                'prima_apparizione': '1928',
                'fidanazato': 'Topolino',
                'passione': 'Fiori e musica'
            },
            {
                'id': 'pippo',
                'nome': 'Pippo',
                'specie': 'Cane',
                'personalita': 'Goofy, maldestro, buon cuore',
                'occupazione': 'Disoccupato felice',
                'prima_apparizione': '1932',
                'amico_migliore': 'Topolino',
                'frase_famosa': 'Gawrsh!'
            },
            {
                'id': 'pluto',
                'nome': 'Pluto',
                'specie': 'Cane',
                'personalita': 'Fedele, giocherellone, vivace',
                'occupazione': 'Cane da compagnia di Topolino',
                'prima_apparizione': '1930',
                'padrone': 'Topolino',
                'nemico_giurato': 'Gatto Butch'
            },
            {
                'id': 'clarabella',
                'nome': 'Clarabella',
                'specie': 'Mucca',
                'personalita': 'Pomposa, elegante, pettegola',
                'occupazione': 'Socialite',
                'prima_apparizione': '1928',
                'interesse_romantico': 'Pippo'
            },
            {
                'id': 'cicoe',
                'nome': 'Cico e Cico',
                'specie': 'Scoiattoli',
                'personalita': 'Combinaguai, golosi, vivaci',
                'occupazione': 'Troublemakers',
                'prima_apparizione': '1943',
                'amati': 'Noci e noccioline',
                'frase_famosa': 'Cico!'
            }
        ]
    }
    
    topolinia_id = disneyland.insert(topolinia_doc)
    print(f"    Topolinia creata con {len(topolinia_doc['personaggi'])} personaggi (ID: {topolinia_id})")
    
    print(f"\n✓ Collezione Disneyland creata con successo!")
    print(f"  - Documenti in Disneyland: {len(disneyland.all())}")
    print(f"    • 3 Aree tematiche")
    print(f"    • Paperopoli con {len(paperopoli_doc['personaggi'])} personaggi")
    print(f"    • Topolinia con {len(topolinia_doc['personaggi'])} personaggi")
    
    return db

if __name__ == "__main__":
    # Solo per inizializzazione se necessario
    print("Usa: python -c \"from popolamento import crea_disneyland; crea_disneyland()\"")
