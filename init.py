#!/usr/bin/env python
import requests
import os
import paho.mqtt.client as paho
import socket
import ssl
import json
from time import sleep
from random import uniform

api_endpoint = 'http://test-env.vdxd9zppmk.us-west-2.elasticbeanstalk.com/api/devices/create_device' 
aws_iot_endpoint = 'a2solub2re3n8u.iot.us-west-2.amazonaws.com'
aws_port = 8883
client_id = None
device_name = None
ca_path = 'ca-cert.crt'
cert_path = 'device-certificate.pem.crt'
key_path = 'device-private.pem.key'
serial_number = None
conn_flag = False

print('hello world')

def initialize_device():
    # Get device name from user and clean it up
    global device_name
    global client_id
    device_name = input('Enter a device name (no_spaces allowed): ')
    device_name = device_name.strip().replace(' ', '_')
    client_id = device_name


    # Get serial number from device
    with open('/factory/serial_number', 'r') as f:
        serial_number = f.read()

    # Clean up serial number
    if serial_number is not None:
        serial_number = serial_number.strip()

    # Log
    print(f"Attempting to create device instance on server with device name '{device_name}' and serial number '{serial_number}'")

    # Send request to server to create the device
    payload = { 'deviceName': device_name, 
            'serialNumber': serial_number }

    print("Issuing request...")

    response = requests.post(api_endpoint, data=payload).json()

    print(response)

    # Setup files...
    with open('device-certificate.pem.crt', 'w') as f:
        f.write(response["certs"]["certificate_pem"])

    with open('device-private.pem.key', 'w') as f: 
        f.write(response['certs']['private_key'])

    # Get the ca-cert
    response = requests.get('https://www.symantec.com/content/en/us/enterprise/verisign/roots/VeriSign-Class%203-Public-Primary-Certification-Authority-G5.pem')

    # Write ca-cert to file
    with open('ca-cert.crt', 'w') as f:
        f.write(response.text)

    # Create a confirmation file, with device name and serial number
    with open('device.txt', 'w') as f:
        f.write(device_name+"\n")
        f.write(serial_number+"\n")

def on_connect(client, data, flags, rc):
#    if rc==0:
#       payload= "{\"state\":{\"reported\":{\"status\":\"active\"}}}"
#        mqtt_client.subscribe('$aws/things/' + device_name + 'shadow/update/delta', qos=0)
#        mqtt_client.publish('$aws/things/' + device_name + '/shadow/update',payload,0,True)
    global conn_flag
    conn_flag = True
    print("Connection returned result: " + str(rc))

def on_message(client, data, msg):
#    print("Message received: " +msg.topic+" | QoS: " +str(msg.qos)+" | Data Received: " +str(msg.payload))
    print(msg.topic+" "+str(msg.payload))

# Check to see if the system is already initialized
# If device.txt exists, means this is not the first time
# this file has been run. Read info from it. Otherwise,
# run initialize_device()
if os.path.exists('device.txt'):
    with open('device.txt', 'r') as f:
        device_name = f.readline().strip()
        serial_number = f.readline().strip()
        print(f"Starting messaging for {device_name}, {serial_number}")
else:
    initialize_device()


mqtt_client = paho.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.tls_set(ca_path, certfile=cert_path, keyfile=key_path, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)

mqtt_client.connect(aws_iot_endpoint, aws_port, keepalive=60)

mqtt_client.loop_start()
a = 0
while 1 == 1:
    sleep(3.0)
    if conn_flag == True:
#        payload = f"{\"state\":{\"reported\":{\"status\":\"{message}\"}}}"
        payload = { "state": {
            "reported": {
                "status": f"count = {a}" 
                }
            }
        }
        payload = json.dumps(payload)
        print('debug ' + device_name)
        mqtt_client.publish('$aws/things/' + device_name + '/shadow/update',payload,0,True)
#        mqtt_client.publish("Count: " + "a", qos=1)
        print(f"msg sent: count = {payload}")
        a = a +1
    else:
        print("waiting for connection...")

