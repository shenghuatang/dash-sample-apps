from kafka import KafkaConsumer
consumer = KafkaConsumer('test_topic',group_id='my_favorite_group')
for msg in consumer:
   print (msg)
   print (msg.value)
