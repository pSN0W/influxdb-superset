from kafka import KafkaProducer
from kafka.errors import KafkaError

class Producer:
    def __init__(self, topic):
        self.producer = KafkaProducer(bootstrap_servers=['localhost:29092'],retries=10)
        self.topic = topic

    def send_message(self,message):
        encoded_message = message.encode('utf-8')
        future = self.producer.send(self.topic, encoded_message)
        
        try:
            record_metadata = future.get(timeout=10)
            print(f"Message has been sent to topic {record_metadata.topic} with offset {record_metadata.offset}\n")

        except KafkaError as e:
            print(f"Failed to send message to topic {self.topic}")
            print(e)
