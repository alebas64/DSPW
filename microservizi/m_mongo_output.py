"""
Questo microservizio serve per interagire con il server
mongo per il prelievo dei vari json dal database
"""

import json
import pymongo
import time
from pymongo.errors import ConnectionFailure
from confluent_kafka import Consumer, Producer, KafkaError
from lib import kafka_data


numeri_constraint_maggiorati=[1,6,8,10]
numeri_constraint_minorati=[2,5]


consumer_conf = {'bootstrap.servers': 'host.docker.internal:29092,host.docker.internal:29093,host.docker.internal:29094', 'group.id': 'filter-consumer-group', 'auto.offset.reset': 'earliest'}
consumer=Consumer(consumer_conf)
consumer.assign([Consumer.TopicPartition(kafka_data.TOPIC_METEOCOMMANDS, kafka_data.PARTITION_UP_MO)])

def run():
    while True:
        try:
            client = pymongo.MongoClient("mongodb+srv://aldo:wpw_T3w@ADvD@j7@cluster0.hcqdqwz.mongodb.net/") 
            break
        
        except ConnectionFailure as e:
                print(f"Errore di connessione a MongoDB: {e}")
                time.sleep(3)
       
        


    while True:
        msg = consumer.poll(1.0)

        if (msg.key()=="do_query"):
            try:
                db = client["dati_previsione"]
                collezione = db["previsioni_only_read"]
                

                try:

                    producer_conf = {'bootstrap.servers': 'localhost:9092'}
                    producer = Producer(producer_conf)

                    

                    constraints_json=json.load(msg.value)
                    codice=0
                    for constraint in constraints_json:
                        if(constraint["cod_legenda"]in numeri_constraint_minorati ): codice=1
                        elif(constraint["cod_legenda"]in numeri_constraint_maggiorati ): codice=2
                        else: codice=3
                        if(constraint["cod_legenda"]==1 or constraint["cod_legenda"]==3 ): 
                            caratteristica_meteo="[daily[temp[max]]]"
                        elif(constraint["cod_legenda"]==2 or constraint["cod_legenda"]==4 ):
                            caratteristica_meteo="[daily[temp[min]]]"
                        elif(constraint["cod_legenda"]==5):
                            caratteristica_meteo="[daily[feels_like[humidity]]]"
                        elif(constraint["cod_legenda"]==6):
                            caratteristica_meteo="[daily[rain]]]"
                        elif(constraint["cod_legenda"]==7):
                            caratteristica_meteo="[daily[snow]]"
                        elif(constraint["cod_legenda"]==8):
                            caratteristica_meteo="[daily[feels_like[wind_speed]]]"
                        elif(constraint["cod_legenda"]==10):
                            caratteristica_meteo="[daily[cloudy]]"
                        elif(constraint["cod_legenda"]==11):
                            caratteristica_meteo="[daily[uv]]"
                        elif(constraint["cod_legenda"]==12):
                            caratteristica_meteo="[daily[sunrise]]"
                        elif(constraint["cod_legenda"]==13):
                            caratteristica_meteo="[daily[sunset]]"
                        elif(constraint["cod_legenda"]==14):
                            caratteristica_meteo="[daily[moonrise]]"
                        elif(constraint["cod_legenda"]==15):
                            caratteristica_meteo="[daily[moonset]]"
                    
                        
                        if codice==1:
                            query= {
                                "cod_citta": constraint["cod_citta"],
                                caratteristica_meteo:{"$gt":constraint["valore"]}
                            } 
                        elif codice==2:
                            query= {
                                "cod_citta": constraint["cod_citta"],
                                caratteristica_meteo:{"$lt":constraint["valore"]}
                            } 
                        elif codice==3:
                            query= {
                                "cod_citta": constraint["cod_citta"],
                                caratteristica_meteo:constraint["valore"]
                            } 
                        else: print("errore")

                        risultati += collezione.find(query)
                    
                    for risultato in risultati:
                        print (risultato)
                        json_risultato = json.dumps(risultato, default=str)
                        print(json_risultato)
                        producer.produce(kafka_data.TOPIC_METEORESULTS,value=json.dumps(json_risultato),key=kafka_data.KEY_MO_UP)
                        producer.flush()
                
                except Exception as e:
                    print(f"Si è verificato un errore durante il recupero dei dati: {e}")

                client.close()
            except ConnectionFailure as e:
                print(f"Errore di connessione a MongoDB: {e}")
            except Exception as e:
                print(f"Si è verificato un errore generico: {e}")
        


run()