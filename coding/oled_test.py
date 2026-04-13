from machine import Pin, I2C
import ssd1306
import time

# --- NEW PIN CONFIGURATION ---
SCK_PIN = 5   # Connected to D5
SDA_PIN = 18  # Connected to D18
WIDTH = 128
HEIGHT = 64

# Initialize I2C
# We use freq=100000 (100kHz) first for better stability during testing
i2c = I2C(0, scl=Pin(SCK_PIN), sda=Pin(SDA_PIN), freq=100000)

print("Scanning I2C bus on GPIO 5 and 18...")
devices = i2c.scan()

if not devices:
    print("Error: No I2C device found. Check your jumper wires!")
else:
    addr = devices[0]
    print("Success! Found device at address:", hex(addr))
    
    try:
        # Initialize OLED with the address found by the scanner
        oled = ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr)
        
        # Test drawing
        oled.fill(0)
        oled.rect(0, 0, 128, 64, 1) # Border
        oled.text("ESP32 NEW PINS", 10, 15)
        oled.text("SCK: D5", 10, 35)
        oled.text("SDA: D18", 10, 45)
        oled.show()
        print("Display should now be ON.")
        
    except Exception as e:
        print("Failed to initialize SSD1306:", e)