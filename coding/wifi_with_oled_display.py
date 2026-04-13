import network
import socket
from machine import Pin, PWM, I2C
import time
import ssd1306

# --- CONFIGURATION ---
SSID = "ABCD"
PASSWORD = "12345678"
SPEED = 800  

# --- OLED SETUP (UPDATED PINS) ---
# SCL on D5 (GPIO 5), SDA on D18 (GPIO 18)
WIDTH = 128
HEIGHT = 64
i2c = I2C(0, scl=Pin(5), sda=Pin(18), freq=100000)

# Initialize Display
oled = None
try:
    devices = i2c.scan()
    if devices:
        oled = ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, devices[0])
        oled.fill(0)
        oled.text("Robot Booting", 0, 0)
        oled.show()
    else:
        print("OLED not found on I2C bus")
except Exception as e:
    print("OLED Init Error:", e)

def update_display(line1, line2=""):
    if oled:
        oled.fill(0)
        oled.text(line1, 0, 0)
        oled.text(line2, 0, 16)
        oled.show()

# --- BTS7960 DRIVER SETUP ---
en_l = [Pin(27, Pin.OUT), Pin(14, Pin.OUT)]
en_r = [Pin(12, Pin.OUT), Pin(13, Pin.OUT)]

for p in en_l + en_r: p.value(1) 

lpwm_l = PWM(Pin(25), freq=1000)
rpwm_l = PWM(Pin(26), freq=1000)
lpwm_r = PWM(Pin(32), freq=1000)
rpwm_r = PWM(Pin(33), freq=1000)

pump = Pin(23, Pin.OUT, value=1) 

# --- CORE MOTOR FUNCTION ---
def drive(l_f, l_b, r_f, r_b):
    lpwm_l.duty(l_f)
    rpwm_l.duty(l_b)
    lpwm_r.duty(r_f)
    rpwm_r.duty(r_b)

# --- ACTIONS ---
ACTIONS = {
    "f":    lambda: drive(SPEED, 0, 0, SPEED),
    "b":    lambda: drive(0, SPEED, SPEED, 0),
    "l":    lambda: drive(0, SPEED, 0, SPEED),
    "r":    lambda: drive(SPEED, 0, SPEED, 0),
    "s":    lambda: drive(0, 0, 0, 0),
    "pon":  lambda: [pump.value(0), update_display("PUMP: ON", wlan.ifconfig()[0])],
    "poff": lambda: [pump.value(1), update_display("PUMP: OFF", wlan.ifconfig()[0])]
}

# --- NETWORK ---
update_display("WiFi Connecting")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected(): 
    time.sleep(0.5)

ip_addr = wlan.ifconfig()[0]
print("Robot Live at:", ip_addr)
update_display("Robot Online", ip_addr)

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