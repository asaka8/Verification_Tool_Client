import time
from src.conmunicator.INS401_Ethernet import Ethernet_Dev

logf = open('test.bin', 'wb')
eth = Ethernet_Dev()
eth.find_device()
eth.start_listen_data()
start_time = time.time()
while time.time() - start_time <= 1800:
    data = eth.read_data()
    if data is not None:
        logf.write(data)
eth.stop_listen_data()
print("finished")