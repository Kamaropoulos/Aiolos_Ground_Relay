import RYLR896Py
from _thread import *
import threading
import json
import requests

# 1. Setup serial connection
lora = RYLR896Py.RYLR896("/dev/ttyS0", 115200)
lora.SetRFParamsLessThan3KM()

def dataHandler(data):
    # Split data on '|' separator character
    dataSplit = data["message"].split("|")

    dataToSend = {}

    dataToSend["drone_id"] = dataSplit[0]
    dataToSend["GPRMC"] = dataSplit[1]
    dataToSend["sensorReadings"] = {}

    for sensorReading in dataSplit[2:]:
        name = sensorReading.split("=")[0]
        reading = sensorReading.split("=")[1]
        dataToSend["sensorReadings"][name] = reading

    jsonData = json.dumps(dataToSend)

    url = 'http://192.168.100.11:3000/logs'

    try:
        req = requests.post(url, json = dataToSend)
        print(req.text)
    except Exception as e:
        print(e)

# 2. Listen for data
while True:
    data = lora.Receive()
    if data is not None:
        # On data:
        #   a. Check if valid
        #   b. Parse into object
        #   c. Prepare server request
        #   d. Send request to REST API
        start_new_thread(dataHandler, (data,))

# Split packet and structure into a JSON object
# Send Post request to REST API with JSON object in request body
