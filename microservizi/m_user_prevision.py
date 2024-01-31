import json
import schedule
from lib import openweather_data
from lib import kafka_data
from confluent_kafka import Consumer, Producer, KafkaError

richiesta="richiesta_lista_completa_constraints"
consumer_conf = {'bootstrap.servers': 'host.docker.internal:29092,host.docker.internal:29093,host.docker.internal:29094', 'group.id': 'filter-consumer-group', 'auto.offset.reset': 'earliest'}
consumer = Consumer(consumer_conf)
consumer_giornaliero=Consumer(consumer_conf)
producer_conf = {'bootstrap.servers': 'host.docker.internal:29092,host.docker.internal:29093,host.docker.internal:29094'}
producer =Producer(producer_conf)

def verifica_constraint(dato):
    print ("devo verificare i constraint")

    constraint_verificato=dato #va fatta una operazione vera non ritornarlo e basta /////////////////////////////////////

    return constraint_verificato
          
def aggiornamento_giornaliero():
    #produce verso SqlOperationList inviando una richiesta di tutti i constraint per i vari utenti sul topic Request_constraint
    x = {
        "command": "userPrevision"
    }
    try:
            producer.produce(kafka_data.TOPIC_REQUESTCONSTRAINT,value=json.dumps(x))
            producer.poll(1)
    except BufferError as e:
            print ("Buffer full, waiting for free space on the queue") 
            producer.poll(1.0)                   
            producer.produce(kafka_data.TOPIC_REQUESTCONSTRAINT,value=json.dumps(x)) 
    producer.flush()
    
    
#Il run funziona cosi:
#In run vengono svolte 2 funzionalità diverse, la prima è verificare che la funzione schedulata sia già stata volta e in caso negativo
#svolgerla
#La seconda è prendere in loop i messaggi nei topic a cui è iscritta. Se sono messaggi da Mongo Output verranno elaborati
#e inviati al constructor di messaggi. Se sono da SQlOperationList saranno 1 o più constraint di cui poi verrà richiesta la 
#verifica dal Mongo Output

def run():
    #riceve da SqlOperationList la lista di uno o più constraint per i vari utenti sul topic response_constraint (partizioni)
    # Serve una struttura che abbia per ogni utente 1 o più oggetti constraint
    consumer_giornaliero.assign([Consumer.TopicPartition(kafka_data.TOPIC_RESPONSECONSTRAINT, kafka_data.PARTITION_SOL_UP)]) # qui arriva la lista di constraint da verificare 
    consumer.subscribe([kafka_data.TOPIC_NEWCONSTRAINTS]) # qui arriva la richiesta di un nuovo constraint da verificare
    consumer.subscribe([kafka_data.TOPIC_METEORESULTS]) # qui arrivano i risultati dei constraint verificati

    schedule.every().day.at("7:00").do(aggiornamento_giornaliero)

    while(True):
        schedule.run_pending()
        msg = consumer.poll(1.0)
        if msg is not None:
            error = msg.error()
            if error is not None:
                print("errore")
                print(error)
            else:
                if (msg.key==kafka_data.KEY_MO_UP):
                    #Elabora e produce verso telegramBotConstructor i risultati dei constraint richiesti dai vari utenti sul topic BOT_notifier (key)
                    for dato in json.loads(msg.value()):
                        constraint_verificato=verifica_constraint(dato)
                        producer.produce(kafka_data.TOPIC_BOTNOTIFIER,value=constraint_verificato,key=kafka_data.KEY_UP_TBC)
                        producer.flush

                if (msg.key==kafka_data.KEY_SOL_UP):
                    # produce verso mongooutput i vincoli per i quali dovrà fare la query su mongo sul topic MeteoCommands(partizioni)
                    # cosa importante va deciso se si invia un vincolo per produce o tutti insieme.
                    producer.produce(kafka_data.TOPIC_METEOCOMMANDS,value=msg.value(),partition=kafka_data.PARTITION_UP_MO)
        
        msg = consumer_giornaliero.poll(1.0)
        if msg is not None:
            error = msg.error()
            if error is not None:
                print("errore")
                print(error)
            else:
                dati = msg.value()
                print("messaggio")
                print(dati)
                producer.produce(kafka_data.TOPIC_METEOCOMMANDS,value=dati,partition=kafka_data.PARTITION_UP_MO)
        else:
            pass # nessun messaggio arrivato
