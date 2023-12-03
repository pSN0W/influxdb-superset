from kafka import KafkaConsumer

class Consumer:

    def __init__(self, topic):
        self.topic = topic
        self.consumer = KafkaConsumer(bootstrap_servers=['localhost:29092'])
        self.consumer.subscribe([topic])
    
    def consume_message(self):
        for message in self.consumer:
            print(f"Topic: {self.topic} | Message: {message.value.decode('utf-8')}")

consumer = Consumer("SparkInfluxConnector")
consumer.consume_message()