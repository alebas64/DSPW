"""
Questo microservizio serve per interagire con il server
mongo per la memorizzazione delle previsioni metereologiche
"""


# -----------------------------------------------------------
# I codici sottostanti sono test per verificare il corretto
# funzionamento delle funzioni sviluppate 
# -----------------------------------------------------------

#Mongo
import pymongo

# Connessione al server MongoDB (assicurati di avere MongoDB in esecuzione)
client = pymongo.MongoClient("mongodb+srv://aldo:9GPcA34idtB1C0p2@cluster0.hcqdqwz.mongodb.net/")

# Seleziona o crea un database
db = client["dati_previsione"]

# Crea una collezione (tabella)
collezione = db["previsioni"]

#print("Collezione creata!")

# Inserisci un documento nella collezione
documento = {"campo1": "valore1", "campo2": "valore2"}
collezione.insert_one(documento)

print("Documento inserito!")

documento_json = {
    "campo1": "valore1",
    "campo2": "valore2",
    "campo3": "valore3",
    # ... altri campi
}

# Inserisci il documento nella collezione
risultato = collezione.insert_one(documento_json)

print(f"Documento inserito con ID: {risultato.inserted_id}")

client.close()

if __init__ == '__main__':    
    debug_procedures() # solo per debug. Non sarà presente nella versione definitiva

def debug_procedures():
    pass