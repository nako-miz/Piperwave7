# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder

import bme280_sample2
import json
import datetime
import time

# Define ENDPOINT, CLIENT_ID, PATH_TO_CERT, PATH_TO_KEY, PATH_TO_ROOT, MESSAGE, TOPIC, and RANGE
ENDPOINT = 'xxxxxx'
CLIENT_ID = 'xxxx'
PATH_TO_ROOT = '.pem'
PATH_TO_CERT = '-certificate.pem.crt'
PATH_TO_KEY = '.-private.pem.key'
TOPIC = 'pub/myhome'

# Spin up resources
event_loop_group = io.EventLoopGroup(1)
host_resolver = io.DefaultHostResolver(event_loop_group)
client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=ENDPOINT,
            cert_filepath=PATH_TO_CERT,
            pri_key_filepath=PATH_TO_KEY,
            client_bootstrap=client_bootstrap,
            ca_filepath=PATH_TO_ROOT,
            client_id=CLIENT_ID,
            clean_session=False,
            keep_alive_secs=6
            )
print("Connecting to {} with client ID '{}'...".format(
        ENDPOINT, CLIENT_ID))
# Make the connect() call
connect_future = mqtt_connection.connect()
# Future.result() waits until a result is available
connect_future.result()
print("Connected!")
# Publish message to server desired number of times.
while True:
    date = str(datetime.date.today())
    nowtime = datetime.datetime.now()
    get_time = str(nowtime.hour) + ':' + str(nowtime.minute) + ':' + str(nowtime.second)
    sensor_data = bme280_sample2.readData()
    temp = "%6.2f" % (sensor_data[0])
    press = "%7.2f" % (sensor_data[1])
    hum = "%6.2f" % (sensor_data[2])
    data = {
        'raspiId' : CLIENT_ID,
        'temperature' : temp,
        'pressure' : press,
        'humidity' : hum,
        'get_date' : date,
        'get_time' : get_time,
    }
    # client.publish(TOPIC, json.dumps(data), 1)
    mqtt_connection.publish(topic=TOPIC, payload=json.dumps(data), qos=mqtt.QoS.AT_LEAST_ONCE)
    time.sleep(600)
disconnect_future = mqtt_connection.disconnect()
disconnect_future.result()
