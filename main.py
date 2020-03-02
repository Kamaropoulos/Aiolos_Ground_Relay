import RYLR896Py
from _thread import *
import threading
import json
import requests
import pynmea2

from dotenv import load_dotenv
load_dotenv()

import os

# 1. Setup serial connection
lora = RYLR896Py.RYLR896("/dev/ttyS0", 115200)
lora.SetRFParamsLessThan3KM()
lora.SetAESPassword("FABC0002EEDCAA90FABC0002EEDCAA90")

def dataHandler(data):
    # Split data on '|' separator character
    dataSplit = data["message"].split("|")

    # Create object to store the data we want to send to the API
    dataToSend = {}

    # Get the ID of the Drone we got the data from
    dataToSend["drone_id"] = dataSplit[0]

    # Get GPRMC NMEA sentence
    dataToSend["GPRMC"] = dataSplit[1]

    # Create object to store procesed NMEA sentence data
    dataToSend["gps_data"] = {}

    try:
        # Parse GPRMC sentence to get processed data out of it
        gprmc_nmea2 = pynmea2.parse(dataToSend["GPRMC"])

        # Get GPS status. Will be A if GPS is locked and V if not.
        dataToSend["gps_data"]["status"] = gprmc_nmea2.status

        # Get GPS time
        dataToSend["gps_data"]["timestamp"] = str(gprmc_nmea2.timestamp)

        # Get GPS date
        dataToSend["gps_data"]["datestamp"] = str(gprmc_nmea2.datestamp)

        # Get longitude in degrees, minutes and seconds
        dataToSend["gps_data"]["longitude"] = str(gprmc_nmea2.longitude)
        dataToSend["gps_data"]["longitude_minutes"] = str(gprmc_nmea2.longitude_minutes)
        dataToSend["gps_data"]["longitude_seconds"] = str(gprmc_nmea2.longitude_seconds)

        # Get latitude in degrees, minutes and seconds
        dataToSend["gps_data"]["latitude"] = str(gprmc_nmea2.latitude)
        dataToSend["gps_data"]["latitude_minutes"] = str(gprmc_nmea2.latitude_minutes)
        dataToSend["gps_data"]["latitude_seconds"] = str(gprmc_nmea2.latitude_seconds)
        
    except Exception as e:
        # If parse failed, print error and move on
        print(e)

    # Create object to store sensor values
    dataToSend["sensorReadings"] = {}

    # For each sensor value in the message:
    # (we assume the rest of the string only contains sensor readings)
    for sensorReading in dataSplit[2:]:
        # Split on the '=' character.
        # The string before it should be the sensor name and
        # the one after it should be the sensor value
        name = sensorReading.split("=")[0]
        reading = sensorReading.split("=")[1]

        # Store name and value to the object we are going to send
        dataToSend["sensorReadings"][name] = reading

    # Convert data object to a JSON string
    jsonData = json.dumps(dataToSend)

    # Get URL to hit for the POST request
    url = os.getenv("BACKEND_LOG_ENDPOINT")

    try:
        # Send POST request with JSON data
        req = requests.post(url, json = dataToSend)
        # Print POST request response
        print(req.text)
    except Exception as e:
        # Print error message if we get an exception
        print(e)

# 2. Listen for data
while True:
    data = lora.Receive()
    if data is not None:
        # Start a new thread to run the dataHandler method
        start_new_thread(dataHandler, (data,))
