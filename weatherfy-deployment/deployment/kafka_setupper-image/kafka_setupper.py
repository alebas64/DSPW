from confluent_kafka.admin import AdminClient, NewTopic
import time





def partition_equation(num_partizioni,high_producer_throughput=False):
    bootstrap_servers='host.docker.internal:29092'
    admin_client = AdminClient({'bootstrap.servers': bootstrap_servers})
    metadata = admin_client.list_topics().brokers
    num_brokers = len(metadata)
    if(num_brokers)<=6 |high_producer_throughput==True:
        num_partizioni=num_brokers*3
    if(num_brokers)>=12  & (high_producer_throughput==False):
        num_partizioni=num_brokers*2
    if 6<(num_brokers)<12:
        num_partizioni=(num_brokers*2)+2

 
    return num_partizioni

    


def replication_equation():
    bootstrap_servers = 'host.docker.internal:29092'
    admin_client= AdminClient({'bootstrap.servers': bootstrap_servers})
    metadata = admin_client.list_topics().brokers
    num_brokers = len(metadata)
    if(num_brokers)>3:
        return 3
    if(num_brokers<3):
        return num_brokers 
    
    
    




def create_kafka_topic(bootstrap_servers, topic_name,high_producer_throughput=False, partitions=1):
    admin_client = AdminClient({'bootstrap.servers': bootstrap_servers})
    
    topics_metadata = admin_client.list_topics(timeout=5)
    if topic_name in topics_metadata.topics:
        print(f"Il topic '{topic_name}' esiste già.")
        return
    
    numero_partizioni_dinamico=partition_equation(partitions,high_producer_throughput)
    numero_replication_dinamico=replication_equation()


    new_topic = NewTopic(topic=topic_name, num_partitions=numero_partizioni_dinamico, replication_factor=numero_replication_dinamico)
    create_result = admin_client.create_topics([new_topic])

    for topic, result in create_result.items():
        try:
            result.result()
            print(f"Topic '{topic}' creato con successo.")
        except Exception as e:
            print(f"Errore durante la creazione del topic '{topic}': {e}")
    


def delete_all_topics(bootstrap_servers):
    admin_conf = {'bootstrap.servers': bootstrap_servers}
    admin_client = AdminClient(admin_conf)

    topics_metadata = admin_client.list_topics(timeout=10)
    topics = topics_metadata.topics.keys()

    for topic in topics:
        print(f"Deleting topic: {topic}")
        admin_client.delete_topics([topic])
    
  




def run():
        
   
        time.sleep(10)  #tempo necessario perchè il server kafka sia attivo

        bootstrap_servers = 'host.docker.internal:29092'
        print(bootstrap_servers)
        #Penultimo parametro indica il numero di partizioni, 
        #l'ultimo il replication factor,il numero di repliche per ciascuna partizione, 
        #inferiore o uguale al numero di broker nel cluster Kafka.
        delete_all_topics(bootstrap_servers)
        create_kafka_topic(bootstrap_servers, "Bot_Command",3)
        create_kafka_topic(bootstrap_servers, "Bot_Message",1)
        create_kafka_topic(bootstrap_servers, "Bot_Notifier",1)
        create_kafka_topic(bootstrap_servers, "Api_Params",1)
        create_kafka_topic(bootstrap_servers, "Meteo_Prevision",1)
        create_kafka_topic(bootstrap_servers, "Meteo_Results",1)
        create_kafka_topic(bootstrap_servers, "Meteo_Commands",2)
        create_kafka_topic(bootstrap_servers, "Request_Constraint",1)
        create_kafka_topic(bootstrap_servers, "Response_Constraint",2)  
        create_kafka_topic(bootstrap_servers, "Coords_Result",1)
        create_kafka_topic(bootstrap_servers, "New_Constraints",1)
        


run()
   

   



    
    

