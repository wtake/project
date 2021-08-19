# -*- coding: utf-8 -*-
# standard
import pytz
import json
import socket
import time
from datetime import datetime
import sys

# pip
import click

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

EMULATE_HX711=False

referenceUnit = 455

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711

# local
import settings
from lib import util

MQTTClient = None


class Sensor:

    def __init__(self, pin_dht11=4, demo=False):
        self.demo = demo
        if self.demo:
            return
        

    def is_demo(self):
        return self.demo
#AWS接続設定
def init_awsiot_client():
    device_id = settings.MQTT_DEVICE_ID
    endpoint = settings.AWS_IOT_ENDPOINT
    my_mqtt_client = AWSIoTMQTTClient(device_id)
    my_mqtt_client.configureEndpoint(endpoint, 8883)
    my_mqtt_client.configureCredentials(
        settings.AWS_CERTS_PATH_ROOTCA,
        settings.AWS_CERTS_PATH_PRIVATEKEY,
        settings.AWS_CERTS_PATH_CERTIFICATE
    )
    my_mqtt_client.configureAutoReconnectBackoffTime(1, 32, 20)
    my_mqtt_client.configureOfflinePublishQueueing(-1)
    my_mqtt_client.configureDrainingFrequency(2)
    my_mqtt_client.configureConnectDisconnectTimeout(10)
    my_mqtt_client.configureMQTTOperationTimeout(5)
    return my_mqtt_client

#AWSへデータを送信
def get_sensordata_and_send_to_aws(my_mqtt_client, sensor, flag):
    payload = {
        'device_id': settings.MQTT_DEVICE_ID,
        'timestamp': None,
        'weight': None,
	    'flag': None
    }

    now = datetime.now(pytz.timezone('Asia/Tokyo'))

    payload['timestamp'] = str(util.datetime_to_unixtime_ms(now))
    payload['weight'] = sensor
    payload['flag'] = flag
    payload_json = json.dumps(payload, indent=4)
    print(payload_json)
    result = my_mqtt_client.publish(
        settings.MQTT_TOPIC,
        payload_json,
        settings.MQTT_QOS
    )
    if result:
        print('Publish result: OK')
    else:
        print('Publish result: NG')

#終了処理
def cleanAndExit():
    print("Cleaning...")

    if not EMULATE_HX711:
        GPIO.cleanup()
        
    print("Bye!")
    sys.exit()

@click.command()
@click.option('--demo', '-d', is_flag=True, help='Demo mode. (Send dummy data)')
def main(demo=False):
    my_mqtt_client = init_awsiot_client()
    my_mqtt_client.connect()
    print('MQTT connect.')

    sensor = Sensor(pin_dht11=settings.DHT11_GPIO_PIN, demo=demo)

    hx = HX711(5, 6)
    hx.set_reading_format("MSB", "MSB")
    hx.set_reference_unit(referenceUnit)
    hx.reset()
    hx.tare()
    print("Tare done! Add weight now...")
    preval = hx.get_weight(5)
    while True:
        try:
            val = hx.get_weight(5)
            hx.power_down()
            hx.power_up()
            print(val)
            preval = int(preval)
            val = int(val)
            if (preval - val) > 10:
                print("hetta")
		flag = 1
                get_sensordata_and_send_to_aws(my_mqtt_client, val, flag)
            elif (val - preval) > 10:
                print("hueta")
		flag = 0
                get_sensordata_and_send_to_aws(my_mqtt_client, val, flag)
            preval = val
            time.sleep(10)
        except (KeyboardInterrupt, SystemExit):
            cleanAndExit()


if __name__ == '__main__':
    main()
