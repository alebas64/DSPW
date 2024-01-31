from confluent_kafka import Consumer, Producer, KafkaError
import json


# Consuamatore dati grezzi
consumer_conf = {'bootstrap.servers': 'localhost:9092', 'group.id': 'filter-consumer-group', 'auto.offset.reset': 'earliest'}


consumer = Consumer(consumer_conf)

consumer.subscribe(['lista-città'])
while True:
    msg = consumer.poll(1.0)

    if msg is not None:
        preferenze = json.loads(msg.value())

    break


consumer.subscribe(['raw-weather-data'])

# Produttore per i dati filtrati
producer_conf = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(producer_conf)

# Simula il filtraggio e invia dati filtrati al topic corrispondente per ogni città
while True:
    msg = consumer.poll(1.0)

    if msg is not None:
        raw_data = json.loads(msg.value())
        città = raw_data['città']

        # Simulazione: applica logica di filtraggio
        if raw_data['temperature'] < 30 or raw_data['pioggia'] < 5:
            filtered_data = {'temperature': raw_data['temperature'], 'rainfall': raw_data['rainfall']}
            filtered_data_topic = f'filtered-weather-data-{città}'

            # Invia dati filtrati al topic corrispondente
            producer.produce(filtered_data_topic, key=città, value=json.dumps(filtered_data))
            producer.flush()
