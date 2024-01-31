"""
Questo microservizio serve per interagire con il server mysql:

restituire lista codici legenda per creazione constraint
lista constraint per utente
lista città di cui fare la previsione
lista utenti
"""
import requests
import time
import mysql.connector
import json
from datetime import datetime, date, timedelta
from confluent_kafka import Consumer, Producer, KafkaError
from lib import sql_data
from lib import kafka_data
from prometheus_client import start_http_server,Summary,Counter
from lib import network_port as np

consumerTelegram = None # utilizzato per consumare messaggi : TelegramBotReader => Sql_operationList
consumerPrev = None     # utilizzato per consumare messaggi: UserPrevision => SqlOperationList

# il producer in questione deve produrre messaggi per:
producer = None
# topic               -- direzione messaggio
# Response_Constraint -- SqlOperationList => UserPrevision
# Bot_Notifier        -- SqlOperationList => TelegramBotConstructor
# Api_Params          -- SqlOperationList => Openweather
# Meteo_Commands      -- SqlOperationList => MongoClear

c_dc = Counter('dspw_telegram_bot_reader_msg_deleteconstraint',
'Quanti messaggi di deleteConstraint sono arrivati al microservizio dal suo avvio')
s_t = Summary('dspw_sql_operation_list_workert_processing_time',
'Tempo impiegato per ottenere lista di tutti i constraint possibili o di tutti i constraint utente')
s_m = Summary('dspw_sql_operation_list_workerm_processing_time',
'Tempo impiegato per inviare le notifiche di tutte le città di cui fare la previsione')
s_p = Summary('dspw_sql_operation_list_workerp_processing_time',
'Tempo impiegato per creare tutte le liste dei constraint di ogni utente')
s_ps = Summary('dspw_sql_operation_list_workerps_processing_time',
'Tempo impiegato per inviare le notiche delle liste di constraint degli utenti')

def database_connection():
    mydb = mysql.connector.connect(
        host=sql_data.MYSQLDB_HOST,
        user=sql_data.MYSQLDB_USER,
        password=sql_data.MYSQLDB_PASSWORD,
        database=sql_data.MYSQLDB_DATABASE
    )
    return mydb

def database_cursor(mydb):
    return mydb.cursor()

def close(mycursor,mydb):
    mycursor.close()
    mydb.close()

# questa funzione restituisce tutte le notifiche degli eventi 
# metereologici di un determinato utente (messaggio interno per microservizi)
def listAllConstraint(mydb,mycursor,chat_id):
    mycursor.clear_attributes()
    sql = "SELECT cod_legenda,valore,citta.id,citta.nome,constraints.id FROM constraints join citta ON constraints.cod_citta = citta.id WHERE cod_utente=%s"
    val = [chat_id]
    mycursor.execute(sql,val)
    query_results = mycursor.fetchall()
    no_results = len(query_results) # numero di risultati della query
    if no_results == 0:
        y = {
            "command": "/listConstraint",
            "chat_id": chat_id,
            "status": "FAILED_NOENTRIES" # "Errore constraint: tabella vuota"
        }
        return y
    else:
        y = {
            "command": "/listConstraint",
            "chat_id": chat_id,
            "status":"SUCCESS",
            "constraints": query_results
        }
        return y

#restituisce tutti i codici dei constraint che è possibile fare
def showPossibleConstraint(mydb,mycursor,chat_id):
    mycursor.execute("SELECT * from legenda")
    query_results = mycursor.fetchall()
    no_results = len(query_results) # numero di risultati della query
    if no_results == 0:
        y = {
            "command": "/showPossibleConstraint",
            "chat_id": chat_id,
            "status": "FAILED_NOENTRIES" # "Errore constraint: tabella vuota"
        }
        return y
    else:
        y = {
            "command": "/showPossibleConstraint",
            "chat_id": chat_id,
            "status":"SUCCESS",
            "constraints": query_results
        }
        return y

# crea e restituisce una lista delle città per fare la previsione
# restituisce id,latitudine e longitudine di una città
def listCities(mydb,mycursor):
    mycursor.clear_attributes()
    sql = "SELECT id,nome,latitudine,longitudine FROM citta"
    mycursor.execute(sql)
    query_results = mycursor.fetchall()
    no_results = len(query_results) #numero di risultati della query
    if no_results == 0:
        return []
    column_names = mycursor.column_names
    description = mycursor.description
    list_return =[]
    for x in query_results:
        list_return.append([x])
    return list_return

def updateDate(mydb,mycursor,citiesToDo):
    x = datetime.today().date()
    sql = "UPDATE citta SET last_update = %s WHERE citta.id = %s"
    val = [x,None]
    for element in citiesToDo:
        val[1]=element[0]
        mycursor.execute(sql,val)
        mydb.commit()

#restituisce una lista di città che non hanno la previsione aggiornata da più di un giorno

def listCitiesToUpdate(mydb,mycursor):
    sql = "SELECT id,nome,latitudine,longitudine,last_update FROM citta"
    mycursor.execute(sql)
    query_results = mycursor.fetchall()
    no_results = len(query_results)
    citiesN = []
    i = 0
    x = datetime.today().date()
    while i < no_results:
        if query_results[i][4] == None or (x - query_results[i][4]).days >= 1:
            citiesN.append([query_results[i]])
        i = i + 1
    return citiesN

def citiesRefresher(mydb,mycursor):
    citiesToDo = listCitiesToUpdate(mydb,mycursor)
    if len(citiesToDo)>0:
        #invia a mongoInput la richiesta di clear
        workerM(citiesToDo)
        updateDate(mydb,mycursor,citiesToDo)


@s_t.time()
def workerT(mydb,mycursor,msg):
    x = json.loads(msg)
    match x["command"]:
        case "/listConstraint": #comunica a prometheus che è arrivato un messaggio di start
            y = listAllConstraint(mydb,mycursor,x["chat_id"])
            producer.produce(kafka_data.TOPIC_BOTNOTIFIER,value=json.dumps(y),key=kafka_data.KEY_SOL_TBC)
        
        case "/showPossibleConstraint":
            y = showPossibleConstraint(mydb,mycursor,x["chat_id"])
            producer.produce(kafka_data.TOPIC_BOTNOTIFIER,value=json.dumps(y),key=kafka_data.KEY_SOL_TBC)
            
        case _:
            pass # comunicazione a prometheus che è arrivato un messaggio non aspettato

# worker che lavora per openweather
@s_m.time()
def workerM(citiesToDo):
    y = {
    "command": "effettuaPrevisione",
    "latitudine": 0.0,
    "longitudine": 0.0,
    "Nome": ""
    }
    for element in citiesToDo:
        y["Nome"] = element[1]
        y["latitudine"] = element[2]
        y["longitudine"] = element[3]
        producer.produce(kafka_data.TOPIC_APIPARAMS,value=json.dumps(y),key=kafka_data.KEY_SOL_OW)

# worker che lavora per userPrevision
@s_p.time()
def workerP(mydb,mycursor,msg):
    x = json.loads(msg)
    match x["command"]:
        #comunicazione a prometheus che è arrivata una richiesta di lista di constraint per utente
        case "userPrevision":
            citiesToDo = listCities(mydb,mycursor)
            if len(citiesToDo)>0:
                # invia a mongoInput la richiesta di clear
                y = {
                    "command": "clear"
                }
                producer.produce(kafka_data.TOPIC_METEOCOMMANDS,value=json.dumps(y),key=kafka_data.KEY_SOL_MI,partition=kafka_data.PARTITION_SOL_MI)
                workerM(citiesToDo)
                updateDate(mydb,mycursor,citiesToDo) # aggiorna last_update delle città di cui si sta facendo la previsione

                sql="select constraints.id,valore,cod_legenda,cod_utente,citta.nome from constraints join citta on constraints.cod_citta = citta.id order by cod_utente"
                mycursor.execute(sql)
                query_results = mycursor.fetchall()
                no_results = len(query_results)
                if(no_results==0):
                    pass
                else:
                    workerP_sending(query_results,no_results)
        case _:
            pass # comunicazione a prometheus che è arrivato un messaggio non aspettato

@s_ps.time()
def workerP_sending(query_results,no_results):
    i=0
    x = {
        "command":"userConstraint",
        "chat_id":0,
        "constraints":[]
    }

    last_chat_id = query_results[0][4]
    x["chat_id"]=last_chat_id

    while i<no_results:
        if(last_chat_id==query_results[i][4]):
            x["constraints"].append({
                "id":query_results[i][0],
                "valore":query_results[i][1],
                "cod_legenda":query_results[i][2],
                "cod_citta":query_results[i][4],
                "cod_utente":query_results[i][3]
            })
        else:
            producer.produce(kafka_data.TOPIC_RESPONSECONSTRAINT,value=json.dumps(x),key=kafka_data.KEY_SOL_UP,partition=kafka_data.PARTITION_SOL_UP)
            x["constraints"]=[]
            x["constraints"].append({
                "id":query_results[i][0],
                "valore":query_results[i][1],
                "cod_legenda":query_results[i][2],
                "cod_citta":query_results[i][4],
                "cod_utente":query_results[i][3]
            })
            x["chat_id"]=query_results[i][4]
            last_chat_id = query_results[i][4]
        i=i+1
    producer.produce(kafka_data.TOPIC_RESPONSECONSTRAINT,value=json.dumps(x),key=kafka_data.KEY_SOL_UP,partition=kafka_data.PARTITION_SOL_UP)

def run():
    mydb = database_connection()
    mycursor = database_cursor(mydb)
    consumer_conf = {
        'bootstrap.servers': 'host.docker.internal:29092,host.docker.internal:29093,host.docker.internal:29094',
        'group.id': 'filter-consumer-group',
        'auto.offset.reset': 'earliest'
    }
    consumerTelegram = Consumer(consumer_conf)
    consumerTelegram.subscribe([kafka_data.TOPIC_BOTCOMMANDS])
    consumerTelegram.assign([kafka_data.PARTITION_TBR_SOL])

    consumerPrev = Consumer(consumer_conf)
    consumerPrev.subscribe([kafka_data.TOPIC_REQUESTCONSTRAINT])

    producer_conf = {'bootstrap.servers': 'host.docker.internal:29092,host.docker.internal:29093,host.docker.internal:29094'}
    producer = Producer(producer_conf)

    last_update = time.time()

    while True:
        
        msgT = consumerTelegram.poll(1.0)
        if msgT is not None:
            errorT = msgT.error()
            if errorT is not None:
                print("errore")
                print(errorT) # comunicazione a prometheus che non ha letto bene il messaggio
            else:
                datiT = msgT.value() # comunicazione a prometheus che ha letto il messaggio
                print("messaggio")
                print(datiT)
                workerT(mydb, mycursor, datiT)
        else:
            pass # nessun messaggio arrivato
        
        msgP = consumerPrev.poll(1.0)
        if msgP is not None:
            errorP = msgP.error()
            if errorP is not None:
                print("errore")
                print(errorP) # comunicazione a prometheus che non ha letto bene il messaggio
            else:
                datiP = msgP.value() # comunicazione a prometheus che ha letto il messaggio
                print("messaggio")
                print(datiP)
                workerP(mydb,mycursor,datiP)
        else:
            pass # nessun messaggio arrivato

        # qui viene fatto un check se ci sono nuove città aggiunte e se si effettua la previsione
        if time.time()-last_update>10.0:
            citiesRefresher(mydb,mycursor)
            last_update = time.time()
        




if __name__ == '__main__':
    start_http_server(np.SOL)
    run()
   