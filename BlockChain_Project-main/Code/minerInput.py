import urllib.request
import time

# List of device URLs
device_links = ["http://192.168.28.134:8080", "http://192.168.28.134:8081"]
numDevices = len(device_links)

while True:
    for i in range(numDevices):
        try:
            f = urllib.request.urlopen(device_links[i], timeout=5)
            myfile = f.read()
            mystr = "".join(chr(b) for b in myfile)

            with open("sensorRequests" + str(i) + ".txt", "w+") as file:
                file.write(mystr.strip())

            print("IP Address: " + device_links[i] + " | Firmware: " + mystr)

        except Exception as e:
            print(f"Error accessing {device_links[i]}: {e}")

    time.sleep(5)    
