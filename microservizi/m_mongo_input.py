"""
Questo microservizio serve per interagire con il server
mongo per la memorizzazione delle previsioni metereologiche
"""

import pymongo
import time
from pymongo.errors import ConnectionFailure
from confluent_kafka import Consumer, Producer, KafkaError
from lib import kafka_data
consumer_conf = {'bootstrap.servers': 'host.docker.internal:29092,host.docker.internal:29093,host.docker.internal:29094', 'group.id': 'filter-consumer-group', 'auto.offset.reset': 'earliest'}

def run():
    consumer = Consumer(consumer_conf)
    consumer.subscribe([kafka_data.TOPIC_METEOPREVISION])
    consumer.assign([Consumer.TopicPartition(kafka_data.TOPIC_METEOCOMMANDS, kafka_data.PARTITION_SOL_MI)])

    while True:
        try:
            client = pymongo.MongoClient("mongodb+srv://aldo:wpw_T3w@ADvD@j7@cluster0.hcqdqwz.mongodb.net/") 
            break
        
        except ConnectionFailure as e:
                print(f"Errore di connessione a MongoDB: {e}")
                time.sleep(3)


    
    while True:

        msg = consumer.poll(1.0)

        if msg is not None:
            try:
                db = client["dati_previsione"]
                collezione = db["previsioni"]
                
                if(msg.key==kafka_data.KEY_SOL_MI):
                    risultati = collezione.delete_many({})
                    print(risultati)
                    
                if (msg.error is not None):
                    print(f"Si è verificato un errore nel messaggio: {e}")

                else:
                    documento_json=msg.json()
                    risultato = collezione.insert_one(documento_json)
                    print(f"Documento inserito con ID: {risultato.inserted_id}")
                    print(risultato)

                    
            except ConnectionFailure as e:
                print(f"Errore di connessione a MongoDB: {e}")
            except Exception as e:
                print(f"Si è verificato un errore generico: {e}")
        
        break


run()



   
