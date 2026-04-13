import network
import socket
from machine import Pin, PWM
import time

# --- CONFIGURATION ---
SSID = "ng"
PASSWORD = "ngvasava45"
SPEED = 800  # PWM duty (0-1023)

# --- BTS7960 DRIVER SETUP ---
# Left Driver Enable Pins (L_EN / R_EN)
en_l = [Pin(27, Pin.OUT), Pin(14, Pin.OUT)]
# Right Driver Enable Pins (L_EN / R_EN)
en_r = [Pin(12, Pin.OUT), Pin(13, Pin.OUT)]

# Activate all drivers
for p in en_l + en_r: p.value(1) 

# PWM Pins (RPWM and LPWM)
lpwm_l = PWM(Pin(25), freq=1000)
rpwm_l = PWM(Pin(26), freq=1000)
lpwm_r = PWM(Pin(32), freq=1000)
rpwm_r = PWM(Pin(33), freq=1000)

pump = Pin(23, Pin.OUT, value=1) # High = Off (Relay logic)

# --- CORE MOTOR FUNCTION ---
def drive(l_f, l_b, r_f, r_b):
    """
    l_f: Left Forward, l_b: Left Backward
    r_f: Right Forward, r_b: Right Backward
    """
    lpwm_l.duty(l_f)
    rpwm_l.duty(l_b)
    lpwm_r.duty(r_f)
    rpwm_r.duty(r_b)

# --- FINAL MAPPED ACTIONS ---
# Left/Right were perfect, Forward/Reverse now swapped to fix orientation
ACTIONS = {
    "f":    lambda: drive(SPEED, 0, 0, SPEED),    # Forward (Corrected)
    "b":    lambda: drive(0, SPEED, SPEED, 0),    # Reverse (Corrected)
    "l":    lambda: drive(0, SPEED, 0, SPEED),    # Spin Left (Kept from previous)
    "r":    lambda: drive(SPEED, 0, SPEED, 0),    # Spin Right (Kept from previous)
    "s":    lambda: drive(0, 0, 0, 0),            # Stop
    "pon":  lambda: pump.value(0),
    "poff": lambda: pump.value(1)
}

# --- NETWORK ---
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)
while not wlan.isconnected(): 
    time.sleep(0.5)
print("Robot Live at:", wlan.ifconfig()[0])

# --- WEB UI ---
html = """HTTP/1.1 200 OK
Content-Type: text/html

<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0">
<style>
    body { text-align: center; font-family: sans-serif; background: #1a1a1a; color: white; touch-action: none; }
    #joy { width: 220px; height: 220px; background: #333; border: 4px solid #555; border-radius: 50%; margin: 30px auto; position: relative; }
    #stick { width: 70px; height: 70px; background: #00ff88; border-radius: 50%; position: absolute; top: 75px; left: 75px; box-shadow: 0 0 15px #00ff88; }
    .btn { padding: 20px; width: 140px; border-radius: 10px; border: none; font-weight: bold; cursor: pointer; margin: 10px; }
    .on { background: #ff4444; color: white; } .off { background: #444; color: white; }
</style></head>
<body>
    <h2>BTS7960 PRO CONTROL</h2>
    <div id="joy" ontouchmove="move(event)" ontouchend="stopJoy()">
        <div id="stick"></div>
    </div>
    <button class="btn on" onclick="fetch('/?cmd=pon')">PUMP ON</button>
    <button class="btn off" onclick="fetch('/?cmd=poff')">PUMP OFF</button>
    <script>
        const s = document.getElementById("stick");
        let last = "";
        function send(c) { if(c!==last) { fetch("/?cmd="+c); last=c; } }
        function move(e) {
            const r = document.getElementById("joy").getBoundingClientRect();
            const x = e.touches[0].clientX - r.left - 110;
            const y = e.touches[0].clientY - r.top - 110;
            s.style.transform = `translate(${x}px, ${y}px)`;
            if(y < -45) send("f"); 
            else if(y > 45) send("b");
            else if(x < -45) send("l"); 
            else if(x > 45) send("r");
        }
        function stopJoy() { s.style.transform = "translate(0,0)"; send("s"); }
    </script>
</body></html>"""

# --- SERVER ---
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(1)

while True:
    try:
        conn, addr = s.accept()
        request = conn.recv(1024).decode()
        if "cmd=" in request:
            cmd = request.split("cmd=")[1].split(" ")[0]
            if cmd in ACTIONS: ACTIONS[cmd]()
            conn.send("HTTP/1.1 204 No Content\r\n\r\n")
        else:
            conn.send(html)
        conn.close()
    except:
        if 'conn' in locals(): conn.close()