# -*- coding: utf-8 -*-

# AWS 設定
AWS_IOT_ENDPOINT = 'a28cnexnh6oazg-ats.iot.ap-northeast-1.amazonaws.com'
AWS_IOT_THING_NAME = 'RaspberryPi'

# Certificates 設定
HOME_DIR = '/home/pi'
AWS_CERTS_PATH_BASE = HOME_DIR
AWS_CERTS_PATH_ROOTCA = AWS_CERTS_PATH_BASE + '/' + 'root-CA.crt'
AWS_CERTS_PATH_PRIVATEKEY = AWS_CERTS_PATH_BASE + '/' + AWS_IOT_THING_NAME + '.private.key'
AWS_CERTS_PATH_CERTIFICATE = AWS_CERTS_PATH_BASE + '/' + AWS_IOT_THING_NAME + '.cert.pem'

# MQTT 設定
MQTT_DEVICE_ID = 'RaspberryPi'
MQTT_TOPIC = 'iot/device/sensordata'
MQTT_QOS = 0

# Raspberry Pi 設定
I2C_BUS = 0x1

# DHT11 の DATA pin をつないだ GPIO pin 番号
# https://www.raspberrypi.org/documentation/usage/gpio-plus-and-raspi2/
DHT11_GPIO_PIN = 14  

# センサデータの送信間隔（秒）
SEND_SENSORDATA_INTERVAL_SEC = 60
