"""
Questo microservizio serve per interagire con gli utenti 
tramite i messaggi del bot telegram
"""
from confluent_kafka import Consumer, Producer, KafkaError
import requests
import json
from prometheus_client import start_http_server,Summary,Counter
import time
from lib import telegram_data
from lib import kafka_data
api_request= telegram_data.API_REQUEST
from lib import network_port as np
# funzione per invio di messaggi a un utente registrato
# tramite bot telegram 

consumer = None
request_url = api_request + "sendMessage"
sendingTelegram = Summary('dspw_telegram_bot_writer_send_processing_time',
'Tempo impiegato per mandare un messaggio con la API REST telegram')
messagesArrived = Counter('dspw_telegram_bot_writer_msg_arrived',
'Quanti messaggi per utenti sono arrivati al microservizio dal suo avvio')
messagesSended = Counter('dspw_telegram_bot_writer_msg_sended',
'Quanti messaggi ha inoltrato il microservizio dal suo avvio')
kafkaError = Counter('dspw_telegram_bot_writer',
'Quanti errori ha registrato nella ricezione di messaggi kafka dal suo avvio')

@sendingTelegram.time()
def send_message(dati):
    loaded = json.loads(dati)
    params = {
        'chat_id' : loaded["chat_id"],
        'text' : loaded["text"]
    }
    response = requests.get(request_url,params)
    sendingTelegram.inc()
    return response.json()

def run():
    while True:
        msg = consumer.poll(1.0)
        if msg is not None:
            error = msg.error()
            if error is not None:
                kafkaError.inc()
                print("errore")
                print(error) # comunicazione a prometheus che non ha letto bene il messaggio
            else:
                dati = msg.value() # comunicazione a prometheus che ha letto il messaggio
                sendingTelegram.inc()
                print("messaggio")
                print(dati)
                messagesSended.inc()
                send_message(dati)
        else:
            pass # nessun messaggio arrivato
       
if __name__ == "__main__":
    start_http_server(np.TBW)
    consumer_conf = {
        'bootstrap.servers': 'host.docker.internal:29092,host.docker.internal:29093,host.docker.internal:29094',
        'group.id': 'filter-consumer-group',
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(consumer_conf)
    consumer.subscribe([kafka_data.TOPIC_BOTMESSAGE])
    run()