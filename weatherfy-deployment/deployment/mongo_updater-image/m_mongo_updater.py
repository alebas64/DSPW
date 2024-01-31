import pymongo
from pymongo.errors import ConnectionFailure


def run():
        while True:
               
                try:    
                        client = pymongo.MongoClient("mongodb+srv://aldo:9GPcA34idtB1C0p2@cluster0.hcqdqwz.mongodb.net/")
                        db = client["dati_previsione"]
                        collezione_di_sola_lettura = db["previsioni_only_read"]
                        collezione=db["previsioni"]
                        # Configura il change stream sulla collection di sola scrittura
                        change_stream = client.collezione.watch(full_document='updateLookup')

                        # Monitora le modifiche e aggiorna la collection di sola lettura
                        for change in change_stream:
                                if change['operationType'] == 'insert':
                                        collezione_di_sola_lettura .insert_one(change['fullDocument'])
                                elif change['operationType'] == 'update':
                                        collezione_di_sola_lettura .update_one({'_id': change['documentKey']['_id']}, {'$set': change['updateDescription']['updatedFields']})
                                elif change['operationType'] == 'delete':
                                        collezione_di_sola_lettura .delete_one({'_id': change['documentKey']['_id']})

                except ConnectionFailure as e:
                                print(f"Errore di connessione a MongoDB: {e}")
                except Exception as e:
                                print(f"Si è verificato un errore generico: {e}")

