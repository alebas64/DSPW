from confluent_kafka import Consumer, Producer, KafkaError
from lib import kafka_data
import json
from prometheus_client import start_http_server,Summary,Counter
from lib import network_port as np

producer = None
consumer = None

c_sc = Counter('dspw_telegram_bot_constructor_msg_start',
'Quanti messaggi di start sono arrivati al microservizio dal suo avvio')
c_lc = Counter('dspw_telegram_bot_constructor_msg_listconstraint',
'Quanti messaggi di listConstraint sono arrivati al microservizio dal suo avvio')
c_lcs = Counter('dspw_telegram_bot_constructor_msg_listcommands',
'Quanti messaggi di listCommands sono arrivati al microservizio dal suo avvio')
c_spc = Counter('dspw_telegram_bot_constructor_msg_showpossibleconstraint',
'Quanti messaggi di showPossibleConstraint sono arrivati al microservizio dal suo avvio')
c_ac = Counter('dspw_telegram_bot_constructor_msg_addconstraint',
'Quanti messaggi di addConstraint sono arrivati al microservizio dal suo avvio')
c_dc = Counter('dspw_telegram_bot_constructor_msg_deleteconstraint',
'Quanti messaggi di deleteConstraint sono arrivati al microservizio dal suo avvio')
s_m = Summary('dspw_telegram_bot_constructor_messageConstructor_processing_time',
'Tempo impiegato per smistare il messaggio al corretto microservizio')

@s_m.time()
def messageConstructor(key,value):
    loaded = json.loads(value)
    msg = {
        "chat_id" : loaded["chat_id"],
        "text": ""
    }
    match(key):
        case kafka_data.KEY_SU_TBC:
            if(loaded["command"]=="/start"):
                c_sc.inc()
                if(loaded["status"]=="SUCCESS"):
                    msg["text"] = "Ciao e benvenuto!"
                    return msg
            c_lcs.inc()
            if(loaded["command"]=="/listCommands"):
                if(loaded["status"]=="SUCCESS"):
                    msg["text"] = testo_listCommands
                    return msg
        
        case kafka_data.KEY_SOL_TBC:
            if(loaded["command"] == "/showPossibleConstraint"):
                c_spc.inc()
                if(loaded["status"] == "FAILED_NOENTRIES"):
                    msg["text"] = "Qualcosa è andato storto, non trovo i constraint!"
                elif(loaded["status"] == "SUCCESS"):
                    for element in loaded["constraints"]:
                        msg = 'Ecco i constraint che puoi richiedere. Se viene specificato "NoValue" non serve specificare un valore di soglia.\nID - Nome - Spiegazione breve\n'
                        msg = msg + element[0]+" - "+element[1]+" - "+element[2]+"\n"
                return msg

            if(loaded["command"] == "/listConstraint"):
                c_lc.inc()
                if(loaded["status"] == "FAILED_NOENTRIES"):
                    msg["text"] = "Non hai ancora memorizzato nessun constraint, perché non ne crei uno con /addConstraint ?"
                elif(loaded["status"] == "SUCCESS"):
                    for element in loaded["constraints"]:
                        msg = 'Ecco i constraint hai registrato. \nID - Città - ID Legenda - Valore\n'
                        msg = msg + element[4]+" - "+element[3]+" - "+element[0]+" - "+element[1]+"\n"
                return msg

        case kafka_data.KEY_UP_TBC:
            # inserire procedure per costruire i messaggi di risposta di userPrevision/////////////////////
            # userPrevision manda a bot constructor una lista con tutti i risultati dei constraint //////////////////////
            # di un utente. Se ci sono n utenti arrivano n messaggi///////////////////////
            pass

        case kafka_data.KEY_TBR_TBC:
            if(loaded["command"] == "/addConstraint"):
                c_ac.inc()
                if(loaded["status"] == "FAILED"):
                    loaded["text"] = "Hai scritto male il comando. Riprova"
                    return msg
                if(loaded["status"] == "SUCCESS"):
                    loaded["text"] = "Constraint inserito correttamente"
                    return msg
                
            if(loaded["command"] == "/deleteConstraint"):
                c_dc.inc()
                if(loaded["status"] == "FAILED"):
                    loaded["text"] = "Hai scritto male il comando. Riprova"
                    return msg
                if(loaded["status"]== "NOID"):
                    loaded["text"] = "Hai scritto male, non hai un constraint con questo ID. Riprova"
                    return msg
                if(loaded["status"]== "SUCCESS"):
                    loaded["text"] = "Constraint cancellato con successo"
                    return msg

        case None:
            pass #nessuna chiave presente

        case _:
            pass #messaggio con chiave non aspettata

def run():
    while True:
        msg = consumer.poll(1.0)
        if msg is not None:
            error = msg.error()
            if error is not None:
                print(error)
            else:
                dati = msg.value()
                result = messageConstructor(msg.key(),msg.value())
                producer.produce(kafka_data.TOPIC_BOTMESSAGE,value=result)

if __name__ == "__main__":
    start_http_server(np.TBC)
    producer_conf = {'bootstrap.servers': 'host.docker.internal:29092,host.docker.internal:29093,host.docker.internal:29094'}
    producer = Producer(producer_conf)

    consumer_conf = {
        'bootstrap.servers': 'host.docker.internal:29092,host.docker.internal:29093,host.docker.internal:29094',
        'group.id': 'filter-consumer-group',
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(consumer_conf)
    consumer.subscribe([kafka_data.TOPIC_BOTNOTIFIER])
    run()
    

testo_listCommands = """/start
Primo comando che un utente può usare. Questo comando serve al servizio per effettuare la registrazione
utente e generare un chat id (in questo modo è possibile inviare le notifiche all'utente)


/listConstraint
Crea una lista di tutti i constraint dell'utente e la visualizza tramite testo:
<ID> <Città> <Tipo constraint> <giorno attuale o giorno successivo> <confronto, minore o maggiore> <valore per il confronto> <unità di misura>


/deleteConstraint <ID>
il comando serve per eliminare un constraint, passandogli l'id di riferimento

/showPossibleConstraint
Crea una lista di tutti i constraint che è possibile fare e li visualizza tramite testo (mostra tabella legenda del db sql)


/addConstraint <Città> <Tipo constraint> <giorno attuale o giorno successivo> <valore per il confronto>
con questo comando è possibile aggiungere un nuovo constraint per l'utente. I valori tra '<>' possono essere scelti secondo la legenda
<Città>: Inserire la città come testo semplice
<Tipo constraint>: campo numerico intero, valori possibili restituiti da /showPossibleConstraint

P.S.: i constraint 7, 10, 11, 12, 13, 14, 15 <valore per il confronto> deve essere 0

<giorno attuale o giorno successivo>: 0 attuale, 1 successivo

<valore per il confronto>: valore numerico intero o decimale, a seconda della preferenza dell'utente dove il '.' indica
il punto decimale. Es: 13 oppure 318.39 oppure 4.41279823

/listCommands
Comando per elencare tutti i possibili comandi che è possibile fare"""