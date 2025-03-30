from paho.mqtt import client as mqtt_client
import json
import time
from my_schema.aggregated_data_schema import AggregatedDataSchema
from file_datasource import FileDatasource
import config
from my_schema.parking_schema import ParkingSchema

def connect_mqtt(broker, port):
    """Create MQTT client"""
    print(f"CONNECT TO {broker}:{port}")
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to MQTT Broker ({broker}:{port})!")
        else:
            print("Failed to connect {broker}:{port}, return code %d\n", rc)
            exit(rc) # Stop execution
    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.connect(broker, port)
    client.loop_start()
    return client

def publish(client, topic, topic_parking, datasource, delay):
    datasource.startReading()
    while True:
        time.sleep(delay)
        aggregated_data = datasource.read_aggregated_data()
        print("aggregated_data\n----")
        print(aggregated_data)
        print("=------")
        parking_data = datasource.read_parking_data()
        print("parking-data\n----")
        print(parking_data)
        print("=------")

        aggregated_msg = AggregatedDataSchema().dumps(aggregated_data)
        parking_msg = ParkingSchema().dumps(parking_data)
        result = client.publish(topic, aggregated_msg)
        result2 = client.publish(topic_parking, parking_msg)

        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{aggregated_msg}` to topic `{topic}`\n")
        else:
            print(f"Failed to send message to topic {topic}")

def run():
    # Prepare mqtt client
    client = connect_mqtt(config.MQTT_BROKER_HOST, config.MQTT_BROKER_PORT)
    # Prepare datasource
    datasource = FileDatasource("data/accelerometer.csv", "data/gps.csv", "data/parking.csv")
    # Infinity publish data
    publish(client, config.MQTT_TOPIC,config.MQTT_TOPIC2, datasource, config.DELAY)


if __name__ == '__main__':
    run()