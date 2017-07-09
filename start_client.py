#!/usr/bin/env python

import paho.mqtt.client as mqtt


mqtt_client = mqtt.Client(client_id="tsmqtt", clean_session=True)

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.tls_set("./ca-cert.pem", certfile="./device-certificate.pem.crt", keyfile="./device-private.pem.key", tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)

mqtt_client.connect("a2solub2re3n8u.iot.us-west-2.amazonaws.com", port=8883)

mqtt_client.loop_forever()

def on_connect(mqttc, obj, flags, rc):
    if rc==0:
        payload = "(\"state\":{\"reported\":{\"light\":\"on\"}}}"
        mqtt_client.subscribe("$aws/things/
