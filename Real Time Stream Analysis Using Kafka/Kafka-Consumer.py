from kafka import KafkaConsumer
from time import sleep
from json import loads, dumps
import json
from s3fs import S3FileSystem

consumer = KafkaConsumer(
    'kafka-demo_testing',
    bootstrap_servers=['13.233.201.101:9092'],  # Replace with your Kafka broker IP
    value_deserializer=lambda x: loads(x.decode('utf-8')),
    auto_offset_reset='earliest',              # Consume from the beginning
    enable_auto_commit=True                    # Commit offsets automatically
)

s3 = S3FileSystem()

for count, message in enumerate(consumer):
    file_path = f"s3://kafkapratical1/files/stock_market_{count}.json"
    with s3.open(file_path, 'w') as file:
        file.write(json.dumps(message.value))  # Write JSON string to file
    print(f"Saved message {count} to {file_path}")
