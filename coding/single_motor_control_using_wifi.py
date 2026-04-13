import network
import socket
from machine import Pin, PWM
from time import sleep

# -------- MOTOR SETUP --------
rpwm_pin = Pin(25, Pin.OUT)
lpwm_pin = Pin(26, Pin.OUT)
ren_pin = Pin(27, Pin.OUT)
len_pin = Pin(14, Pin.OUT)

ren_pin.value(1)
len_pin.value(1)

sleep(1)

rpwm = PWM(rpwm_pin, freq=1000)
lpwm = PWM(lpwm_pin, freq=1000)

rpwm.duty(0)
lpwm.duty(0)

speed = 800

def forward():
    lpwm.duty(0)
    rpwm.duty(speed)

def backward():
    rpwm.duty(0)
    lpwm.duty(speed)

def stop():
    rpwm.duty(0)
    lpwm.duty(0)

# -------- WIFI --------
ssid = "ng"
password = "ngvasava45"

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)

print("Connecting...")
while not wifi.isconnected():
    sleep(0.5)

print("Connected:", wifi.ifconfig()[0])

# -------- SERVER --------
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(addr)
server.listen(1)

print("Server Ready")

while True:
    try:
        client, addr = server.accept()
        request = client.recv(512).decode()

        # Extract first line only
        request_line = request.split("\r\n")[0]

        print("Request:", request_line)

        if request_line == "GET /f HTTP/1.1":
            forward()

        elif request_line == "GET /b HTTP/1.1":
            backward()

        elif request_line == "GET /s HTTP/1.1":
            stop()

        response = """HTTP/1.1 200 OK
Content-Type: text/html
Connection: close

<html>
<body>
<h2>Motor Control</h2>
<a href="/f">Forward</a><br><br>
<a href="/b">Backward</a><br><br>
<a href="/s">Stop</a>
</body>
</html>
"""

        client.send(response)
        client.close()

    except Exception as e:
        print("Error:", e)