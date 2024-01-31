"""
Questo microservizio serve per gestire l'api di openweather,
interrogando il server sulle previsioni meteo

"""
import requests
import json
from lib import openweather_data
from lib import kafka_data
from confluent_kafka import Consumer, Producer, KafkaError
params = openweather_data.params
from prometheus_client import start_http_server,Summary,Counter
from lib import network_port as np

producer_conf = {'bootstrap.servers': 'host.docker.internal:29092,host.docker.internal:29093,host.docker.internal:29094'}
producer =Producer(producer_conf)

consumer_conf = {'bootstrap.servers': 'host.docker.internal:29092,host.docker.internal:29093,host.docker.internal:29094', 'group.id': 'filter-consumer-group', 'auto.offset.reset': 'earliest'}
consumer = Consumer(consumer_conf)

geo_api_url = "http://api.openweathermap.org/geo/1.0/direct"

c_c = Counter('dspw_openwheater_coords_requests',
'Quante richieste di coordinate sono arrivate al microservizio dal suo avvio')
c_p = Counter('dspw_openwheater_previsions_requests',
'Quante richieste di previsioni sono arrivate al microservizio dal suo avvio')

geo_params = {
    'q':'',
    'limit': 5,
    'appid': '241cf7e334517a031d31287144b10f1a'
}

def coords(city,country_code="IT"):
    geo_params["q"] = '{'+city+'},{'+country_code+'}'
    json_response = requests.get(geo_api_url,geo_params).json()
    city_selected = json_response[0]
    for x in json_response:
        if x["country"] == country_code:
            city_selected = x
            city_selected.pop("country",None)
            city_selected.pop("state",None)
            city_selected.pop("local_names",None)
            break
    return city_selected


def f(city):
    
        city_coords = coords(city)
        params['lat'] = city_coords[0]
        params['lon'] = city_coords[1]

        return city_coords[0],city_coords[1]
#previsione meteo di una città


def city_prevision(lat,lon):
    params['lat'] = lat
    params['lon'] = lon
    response = requests.get(openweather_data.api_url,params).json()
    response = rimuovi_campi(response,openweather_data.campi_da_rimuovere)
    return response

def richiesta_coordinate_citta(dati):
    print("messaggio:"+dati)
    coordinate=f(dati(0)) 
    producer.produce(kafka_data.TOPIC_COORDSRESULT,value=coordinate)
    producer.poll(10)
    

def richiesta_previsione_citta(dati):
    print("messaggio:"+dati)
    json_risultato=json.loads(city_prevision(f(dati["city"])))
    json_risultato['city'] = dati["city"]
    json_risultato = json.dumps(json_risultato)
    producer.produce(kafka_data.TOPIC_METEORESULTS,value=rimuovi_campi(json_risultato,openweather_data.campi_da_rimuovere))
    producer.poll(10)
   

# funzione per filtrare i messaggi raw ottenuti da openweather
def rimuovi_campi(json_data, campi_da_rimuovere):
    if isinstance(json_data, dict):
        for campo in campi_da_rimuovere:
            json_data.pop(campo, None)

        for chiave, valore in json_data.items():
            if isinstance(valore, (dict, list)):
                rimuovi_campi(valore, campi_da_rimuovere)
    elif isinstance(json_data, list):
        for elemento in json_data:
            if isinstance(elemento, (dict, list)):
                rimuovi_campi(elemento, campi_da_rimuovere)
    return json_data


def run():
    consumer.subscribe(kafka_data.TOPIC_APIPARAMS)
    while True:
        msg = consumer.poll(1.0)
        if msg is not None:
            if msg.key==kafka_data.KEY_SOC_OW:
                c_c.inc()
                richiesta_coordinate_citta(json.load(msg.value))
            if msg.key==kafka_data.KEY_SOL_OW:
                c_p.inc()
                richiesta_previsione_citta(json.load(msg.value))
        error = msg.error()
        if error is not None:
            print("errore:"+error) # comunicazione a prometheus che non ha letto bene il messaggio



if __name__ == '__main__':    
    start_http_server(np.OW)
    run()
