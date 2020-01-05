import RYLR896Py
from _thread import *
import threading 

# 1. Setup serial connection
lora = RYLR896Py.RYLR896("/dev/ttyS0", 115200)
lora.SetRFParamsLessThan3KM()

def dataHandler(data):
    print(data["message"])

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
