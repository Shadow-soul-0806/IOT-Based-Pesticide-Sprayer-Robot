from machine import Pin, PWM
from time import sleep

# ===============================
# MOTOR DRIVER SETUP
# ===============================

# ----- LEFT DRIVER -----
rpwm_l = PWM(Pin(25))
lpwm_l = PWM(Pin(26))
ren_l = Pin(27, Pin.OUT)
len_l = Pin(14, Pin.OUT)

# ----- RIGHT DRIVER -----
rpwm_r = PWM(Pin(32))
lpwm_r = PWM(Pin(33))
ren_r = Pin(12, Pin.OUT)
len_r = Pin(13, Pin.OUT)

# ----- PUMP RELAY -----
pump = Pin(23, Pin.OUT)

# ===============================
# SAFETY: ENABLE H-BRIDGES FIRST
# ===============================

ren_l.value(1)
len_l.value(1)
ren_r.value(1)
len_r.value(1)

sleep(1)

# Set PWM frequency
rpwm_l.freq(1000)
lpwm_l.freq(1000)
rpwm_r.freq(1000)
lpwm_r.freq(1000)

# Initial motor state
rpwm_l.duty(0)
lpwm_l.duty(0)
rpwm_r.duty(0)
lpwm_r.duty(0)

# Pump OFF initially (Active LOW relay assumed)
pump.value(1)
pump_state = False

speed = 800  # Speed 0–1023

# ===============================
# MOTOR FUNCTIONS
# ===============================

def left_forward():
    lpwm_l.duty(0)
    rpwm_l.duty(speed)

def left_backward():
    rpwm_l.duty(0)
    lpwm_l.duty(speed)

def left_stop():
    rpwm_l.duty(0)
    lpwm_l.duty(0)

def right_forward():
    lpwm_r.duty(0)
    rpwm_r.duty(speed)

def right_backward():
    rpwm_r.duty(0)
    lpwm_r.duty(speed)

def right_stop():
    rpwm_r.duty(0)
    lpwm_r.duty(0)

def forward():
    left_forward()
    right_forward()
    print("Moving Forward")

def backward():
    left_backward()
    right_backward()
    print("Moving Backward")

def turn_left():
    left_stop()
    right_forward()
    print("Turning Left")

def turn_right():
    right_stop()
    left_forward()
    print("Turning Right")

def stop():
    left_stop()
    right_stop()
    print("Motors Stopped")

# ===============================
# PUMP FUNCTION
# ===============================

def toggle_pump():
    global pump_state

    if pump_state == False:
        pump.value(0)  # Relay ON (active LOW)
        pump_state = True
        print("Pump ON")
    else:
        pump.value(1)  # Relay OFF
        pump_state = False
        print("Pump OFF")

# ===============================
# COMMAND LOOP
# ===============================

print("System Ready")
print("Commands: f b l r s p q")

while True:
    try:
        cmd = input("Enter Command: ")

        if cmd == 'f':
            forward()

        elif cmd == 'b':
            backward()

        elif cmd == 'l':
            turn_left()

        elif cmd == 'r':
            turn_right()

        elif cmd == 's':
            stop()

        elif cmd == 'p':
            toggle_pump()

        elif cmd == 'q':
            stop()
            print("Program Exit (Drivers Still Enabled)")
            break

        else:
            print("Invalid Command")

    except:
        print("Input Error")