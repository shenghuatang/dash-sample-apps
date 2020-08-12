'''

(py37) C:\newproject\2020\dash-sample-apps\apps\dash-study-browser>conda install -c conda-forge kafka-python

don’t forget to start your Zookeeper server and Kafka broker before executing the example code below. In this example we assume that
 Zookeeper is running default on localhost:2181 and Kafka on localhost:9092.
We are also using a topic called numtest in this example, you can create a new topic by opening a new command prompt, navigating to …/kafka/bin/windows and execute:
kafka-topics.bat --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic numtest
'''

from time import sleep
from json import dumps
import pprint
from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers='localhost:9092',)
metrics = producer.metrics()
pprint.pprint(metrics)
for _ in range(5):
    producer.send('test_topic', b'some_message_bytes')
producer.close()

