import pandas as pd
from kafka import KafkaProducer
from json import dumps
from time import sleep

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=['13.233.201.101:9092'],
    value_serializer=lambda x: dumps(x).encode('utf-8')
)
# Load CSV file
df = pd.read_csv(r"C:\Users\Welcome\Documents\clevelanda.csv")

# Send multiple messages
for record in df.sample(10).to_dict(orient="records"):
    producer.send('kafka-demo_testing', value=record)
    print(f"Sent: {record}")
    sleep(2)  # Optional delay for testing

print("All messages sent successfully.")
