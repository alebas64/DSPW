"""
Questo microservizio serve per interagire con il server mysql:
creazione utente
rimozione utente (per ora opzionale)
"""
import mysql.connector
import json
import atexit
from pymongo.errors import ConnectionFailure
from confluent_kafka import Consumer, Producer, KafkaError
from lib import kafka_data
from prometheus_client import start_http_server,Summary,Counter
from lib import network_port as np
from lib import sql_data

consumer = None
producer = None

c_au = Counter('dspw_sql_user_msg_add_user',
'Quanti nuovi utenti sono stati registrati dal microservizio dal suo avvio')
s_m = Summary('dspw_sql_user_msg_add_user_processing_time',
'Tempo impiegato per memorizzare nel database un nuovo utente')

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

# salva un nuovo utente nel database mysql
@s_m.time()
def addUser(mydb,mycursor,nome,cognome,telegram,chat_id=0):
    sql = "INSERT INTO utente (nome,cognome,telegram,chat_id) VALUES (%s,%s,%s,%s)"
    val = (nome,cognome,telegram,chat_id)
    result = False
    try:
        mycursor.execute(sql,val)
        result = True
    except Exception as e: 
        print(f"Errore nell'inserimento dell'utente, controllare non sia già presente,codice errore:{e}")
    mydb.commit()
    return result

def exe(mydb,mycursor,msg):
    x = json.load(msg)
    match x["command"]:
        case "/start": #comunica a prometheus che è arrivato un messaggio di start
            result = addUser(mydb,mycursor,x["nome"],["cognome"],x["telegram"],x["chat_id"])
            if result == True:
                y = {
                    "command":"/start",
                    "chat_id": x["chat_id"],
                    "status": "SUCCESS"
                }
                c_au.inc()
                producer.produce(kafka_data.TOPIC_BOTCOMMANDS,value=json.dumps(y),key=kafka_data.KEY_SU_TBC)
        case _: 
            # comunicazione a prometheus che è arrivato un messaggio non aspettato
            pass
    
def run():
    atexit.register(close(mycursor,mydb))
    mydb = database_connection()
    mycursor = database_cursor(mydb)
    
    while True:
        msg = consumer.poll(1.0)
        if msg is not None:
            dati = msg.value() # comunicazione a prometheus che ha letto il messaggio
            print("messaggio:"+dati)
            exe(mydb,mycursor,dati)

            error = msg.error()
            if error is not None:
                print("errore")
                print("errore:"+error) # comunicazione a prometheus che non ha letto bene il messaggio
        else:
            pass


if __name__ == '__main__':
    start_http_server(np.SU)
    producer_conf = {'bootstrap.servers': 'host.docker.internal:29092,host.docker.internal:29093,host.docker.internal:29094'}
    producer = Producer(producer_conf)

    consumer_conf = {
        'bootstrap.servers': 'host.docker.internal:29092,host.docker.internal:29093,host.docker.internal:29094',
        'group.id': 'filter-consumer-group',
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(consumer_conf)
    consumer.subscribe([kafka_data.TOPIC_BOTCOMMANDS])
    consumer.assign([kafka_data.PARTITION_TBR_SU])
    
    run()
    
    