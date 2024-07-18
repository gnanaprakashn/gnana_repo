pip install kafka-python
import pandas as pd
from kafka import KafkaProducer
from time import sleep
from json import dumps
import json


pip install sleep



producer = KafkaProducer(bootstrap_servers=[':9092'], #change ip here
                         value_serializer=lambda x: 
                         dumps(x).encode('utf-8'))

df = pd.read_csv("bepec_learning\kafka\indexProcessed.csv")



while True:
    dict_stock = df.sample(1).to_dict(orient="records")[0]
    producer.send('demo_test', value=dict_stock)
    sleep(1)
