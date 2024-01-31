"""
Questo microservizio serve per interagire con il bot telegram. Il suo unico scopo
è leggere tutti i messaggi che riceve e passarli ai microservizi che li devono
gestire/elaborare
"""

import requests
from lib import telegram_data
from lib import kafka_data
from lib import network_port
import json
from confluent_kafka import Consumer, Producer, KafkaError
from prometheus_client import start_http_server,Summary,Counter
from lib import network_port as np

producer = None

c_sc = Counter('dspw_telegram_bot_reader_msg_start',
'Quanti messaggi di start sono arrivati al microservizio dal suo avvio')
c_lc = Counter('dspw_telegram_bot_reader_msg_listconstraint',
'Quanti messaggi di listConstraint sono arrivati al microservizio dal suo avvio')
c_lcs = Counter('dspw_telegram_bot_constructor_msg_listcommands',
'Quanti messaggi di listCommands sono arrivati al microservizio dal suo avvio')
c_spc = Counter('dspw_telegram_bot_reader_msg_showpossibleconstraint',
'Quanti messaggi di showPossibleConstraint sono arrivati al microservizio dal suo avvio')
c_ac = Counter('dspw_telegram_bot_reader_msg_addconstraint',
'Quanti messaggi di addConstraint sono arrivati al microservizio dal suo avvio')
c_dc = Counter('dspw_telegram_bot_reader_msg_deleteconstraint',
'Quanti messaggi di deleteConstraint sono arrivati al microservizio dal suo avvio')
s_m = Summary('dspw_telegramBotWriter_getUpdates_processing_time',
'Tempo impiegato per smistare il messaggio al corretto microservizio')

@s_m.time()
def getUpdates(request_url,params):
    response = requests.get(request_url,params).json()
    results = response["result"]
    if len(results) == 0:
        return
    else:
        params["offset"]=results[0]["update_id"]+len(results)

    for x in results:
        x = x["message"]
        elements = x["text"].split(" ")
        match elements[0]:
            case "/start":
                c_sc.inc()
                x = {
                    "command":  "/start",
                    "nome":     x["from"]["first_name"],
                    "cognome":  x["from"]["last_name"],
                    "username": x["from"]["username"],
                    "chat_id":  x["from"]["id"]
                }
                producer.produce(kafka_data.TOPIC_BOTCOMMANDS,json.dumps(x),kafka_data.KEY_TBR_SU,kafka_data.PARTITION_TBR_SU)

            case "/listCommands":
                c_lcs.inc()
                x = {
                    "command":  "/listCommands",
                    "chat_id":  x["from"]["id"]
                }
                producer.produce(kafka_data.TOPIC_BOTNOTIFIER,json.dumps(x),kafka_data.KEY_TBR_TBC)

            case "/listConstraint":
                c_lc.inc()
                x = {
                    "command": "/listConstraint",
                    "chat_id": x["from"]["id"]
                }
                producer.produce(kafka_data.TOPIC_BOTCOMMANDS,json.dumps(x),kafka_data.KEY_TBR_SOL,kafka_data.PARTITION_TBR_SOL)
            
            case "/showPossibleConstraint":
                c_spc.inc()
                x = {
                    "command": "/showPossibleConstraint",
                    "chat_id": x["from"]["id"]
                }
                message = json.dumps(x)
                #'Ad esempio:{"command": "/showPossibleConstraint", "chat_id": 778721331}'
                producer.produce(kafka_data.TOPIC_BOTCOMMANDS, message, kafka_data.KEY_TBR_SOL,kafka_data.PARTITION_TBR_SOL)

            case "/addConstraint":
                c_ac.inc()
                if(len(elements)!=5):
                    x = {
                        "command": "/addConstraint",
                        "chat_id": x["from"]["id"],
                        "status": "FAILED" # "errore comando, probabilmente errore di battitura"
                    }
                    producer.produce(kafka_data.TOPIC_BOTNOTIFIER,value=json.dumps(x),key=kafka_data.KEY_TBR_TBC)
                else:
                    x = {
                        "command": "/addConstraint",
                        "chat_id": x["from"]["id"],
                        "city": elements[1],
                        "const_type" : elements[2],
                        "prev_day": elements[3],
                        "value": elements[4]
                    }
                    producer.produce(kafka_data.TOPIC_BOTCOMMANDS,json.dumps(x),kafka_data.KEY_TBR_SOC,kafka_data.PARTITION_TBR_SOC)

            case "/deleteConstraint":
                c_dc.inc()
                if(len(elements)!=2):
                    x = {
                        "command": "/deleteConstraint",
                        "chat_id": x["from"]["id"],
                        "status": "FAILED" # "errore comando, probabilmente errore di battitura"
                    }
                    producer.produce(kafka_data.TOPIC_BOTNOTIFIER,value=json.dumps(x),key=kafka_data.KEY_TBR_TBC)
                else:
                    x = {
                        "command": "/deleteConstraint",
                        "chat_id": x["from"]["id"],
                        "subscription": elements[1]
                    }
                    producer.produce(kafka_data.TOPIC_BOTCOMMANDS,json.dumps(x),kafka_data.KEY_TBR_SOC,kafka_data.PARTITION_TBR_SOC)
            case _:
                pass # comunica a prometheus che è arrivato un messaggio che non ha compreso
            
    producer.flush()

def worker():
    request_url = telegram_data.API_REQUEST+"getUpdates"
    params = {
        "offset": 0,
        "limit": 15
    }
    while True:
        getUpdates(request_url,params)


if __name__ == "__main__":
    start_http_server(np.TBR)
    producer_conf = {'bootstrap.servers': 'host.docker.internal:29092,host.docker.internal:29093,host.docker.internal:29094'}
    producer = Producer(producer_conf)
    worker()

    