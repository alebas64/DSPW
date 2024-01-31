"""
Questo microservizio serve per interagire con il server mysql:

aggiunta constraint utente
rimozione constraint
"""
import requests
import atexit
import json
import mysql.connector
from pymongo.errors import ConnectionFailure
from mysql.connector import errorcode
from confluent_kafka import Consumer, Producer, KafkaError
from lib import kafka_data
from prometheus_client import start_http_server,Summary,Counter
from lib import network_port as np
from lib import sql_data

producer = None
consumer = None

c_ac = Counter('dspw_sql_operation_constraint_addconstraint_processing_time',
'Quanti messaggi di addConstraint sono arrivati al microservizio dal suo avvio')
c_rc = Counter('dspw_sql_operation_constraint_removeconstraint_processing_time',
'Quanti messaggi di deleteConstraint sono arrivati al microservizio dal suo avvio')
s_ac = Summary('dspw_sql_operation_constraint_addconstraint_processing_time',
'Tempo impiegato per inserire in sql un nuovo constraint utente')

def database_connection():
    try:mydb = mysql.connector.connect(
        host=sql_data.MYSQLDB_HOST,
        user=sql_data.MYSQLDB_USER,
        password=sql_data.MYSQLDB_PASSWORD,
        database=sql_data.MYSQLDB_DATABASE
        )
    except ConnectionFailure as e:
        print(f"Errore di connessione a MongoDB: {e}")
    except Exception as e:
        print(f"Si è verificato un errore generico: {e}")
    return mydb

def database_cursor(mydb):
    return mydb.cursor()

def close(mycursor,mydb):
    mycursor.close()
    mydb.close()

# questa funzione aggiunge una notifica di un evento metereologico per un determinato utente
@s_ac.time()
def addConstraint(mydb,mycursor,chat_id,citta,cod_legenda,valore):

    sql_citta="SELECT id FROM cittainserted WHERE nome = '"+citta+"'"
    mycursor.execute(sql_citta)
    try:risultato=mycursor.fetchall()[0]
    except IndexError:
        risultato=''
    except Exception as e:
         print(f"Si è verificato un errore generico: {e}")
    
    if len(risultato)==0:
        # in questo caso la città non è mai stata richiesta da nessuno
        # bisogna richiedere le coordinate alla api di openweather
        consumer.subscribe([kafka_data.TOPIC_COORDSRESULT])

        try:
            producer.produce(kafka_data.TOPIC_APIPARAMS,value=citta,key=kafka_data.KEY_SOC_OW,partition=kafka_data.PARTITION_SOC_OW)
            producer.poll(0)
        except BufferError as e:
            print ("Buffer full, waiting for free space on the queue") 
            producer.poll(10)                   
            producer.produce(kafka_data.TOPIC_APIPARAMS,value=citta,key=kafka_data.KEY_SOC_OW,partition=kafka_data.PARTITION_SOC_OW) 
        
        producer.flush()

        while(msg is not None):
            msg = consumer.poll(1.0)
    
        coordinate=msg.value
        lat=coordinate['lat']
        lng=coordinate['lon']
        valori_citta=[citta,lat,lng]
        sql_citta_new = "INSERT INTO `cittainserted` ( `nome`, `latitudine`, `longitudine`) VALUES (%s,%s,%s);"
        try:mycursor.execute(sql_citta_new,valori_citta)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DUP_ENTRY:
                print("Errore: Chiave primaria duplicata.")
        except Exception as e: 
            print(f"Errore codice errore: {e}")  
        mydb.commit()
        sql_citta="SELECT id FROM cittainserted WHERE nome = %s"
        city=[citta]
        mycursor.execute(sql_citta,city)
        risultato=mycursor.fetchall()[0]

    if valore==0:

        sql_sub = 'INSERT INTO constraintsinserted(cod_legenda,cod_utente,cod_citta) VALUES (%s,%s,%s)'
        dati=(cod_legenda,chat_id,risultato[0])
        try:mycursor.execute(sql_sub,dati) 
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DUP_ENTRY:
                print("Errore: Chiave primaria duplicata.")
        except Exception as e: 
            print(f"Errore,codice errore: {e}")   

        mydb.commit()
        y = {
            "command": "userConstraint",
            "chat_id": chat_id,
            "constraints":{
                "valore":None,
                "cod_legenda":cod_legenda,
                "cod_citta":risultato[0],
                "cod_utente":chat_id
            }
        }
        producer.produce(kafka_data.TOPIC_RESPONSECONSTRAINT,value=json.dumps(y),key=kafka_data.KEY_SOC_SOL)
        y = {
            "command": "/addConstraint",
            "chat_id": chat_id,
            "status":"SUCCESS"
        }
        producer.produce(kafka_data.TOPIC_BOTNOTIFIER,value=json.dumps(y),key=kafka_data.KEY_SOC_TBC)
        producer.flush()

    else:
        sql_sub = 'INSERT INTO constraintsinserted(valore,cod_legenda,cod_utente,cod_citta) VALUES (%s,%s,%s,%s)'
        dati=[valore,cod_legenda,chat_id,risultato[0]]
        try:mycursor.execute(sql_sub,dati)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DUP_ENTRY:
                print("Errore: Chiave primaria duplicata.")
        except Exception as e: 
            print(f"Errore codice errore: {e}")  
        mydb.commit()
        y = {
            "command": "userConstraint",
            "chat_id": chat_id,
            "constraints":{
                "valore":valore,
                "cod_legenda":cod_legenda,
                "cod_citta":risultato[0],
                "cod_utente":chat_id
            }
        }
        producer.produce(kafka_data.TOPIC_RESPONSECONSTRAINT,value=json.dumps(y),key=kafka_data.KEY_SOC_SOL)
        y = {
            "command": "/addConstraint",
            "chat_id": chat_id,
            "status":"SUCCESS"
        }
        producer.produce(kafka_data.TOPIC_BOTNOTIFIER,value=json.dumps(y),key=kafka_data.KEY_SOC_TBC)
        producer.flush()
    

# questa funzione rimuove una notifica specifica di un evento 
# metereologico per un determinato utente
def removeConstraint(mydb,mycursor,chat_id,id):
    query="SELECT id from constraintsinserted where id=%s and cod_utente=%s"
    dati_per_execute=[chat_id,id]
    if(len(mycursor.fetchall())==1):
        query="DELETE from constraintsinserted where id=%s and cod_utente=%s"
        mycursor.execute(query,dati_per_execute)
        mydb.commit()
        y = {
            "command": "/deleteConstraint",
            "chat_id": chat_id,
            "status":"SUCCESS"
        }
    else:
        y = {
            "command": "/deleteConstraint",
            "chat_id": chat_id,
            "status":"NOID"
        }
    producer.produce(kafka_data.TOPIC_BOTNOTIFIER,value=json.loads(y),key=kafka_data.KEY_SOC_TBC)

def run():
    atexit.register(close(mycursor,mydb))
    mydb = database_connection()
    mycursor = database_cursor(mydb)
    
    while True:
        msg = consumer.poll(1.0)
        constraint=json.loads(msg.value())

        if constraint["command"]=="/addConstraint":
            c_ac.inc()
            addConstraint(mydb,mycursor,constraint["chat_id"],constraint["city"],constraint["const_type"],constraint["value"])

        if constraint["command"]=="/deleteConstraint":
            c_rc.inc()
            removeConstraint(mydb,mycursor,constraint["chat_id"],constraint["subscription"])
    
    
        


if __name__ == "__main__":
    start_http_server(np.SOC)
    producer_conf = {'bootstrap.servers': 'host.docker.internal:29092,host.docker.internal:29093,host.docker.internal:29094'}
    producer = Producer(producer_conf)

    consumer_conf = {'bootstrap.servers': 'host.docker.internal:29092,host.docker.internal:29093,host.docker.internal:29094', 'group.id': 'filter-consumer-group', 'auto.offset.reset': 'earliest'}
    consumer = Consumer(consumer_conf)
    consumer.assign([Consumer.TopicPartition(kafka_data.TOPIC_BOTCOMMANDS, kafka_data.PARTITION_TBR_SOL)])
    run()