# --- Import libraries ---
import time
import network
import machine
import ubinascii
from umqtt.simple import MQTTClient

# --- Define Variables ---
WIFI_SSID = "YOUR_SSID_HERE"        # <--- CHANGE THIS
WIFI_PASSWORD = "YOUR_PASSWORD_HERE"  # <--- CHANGE THIS
YOUR_NAME = "UNIQUE_ID_HERE"         # <--- CHANGE THIS (Use your actual name or a unique ID)

MQTT_BROKER = "broker.hivemq.com"
LED_PIN = 14 

COMMAND_TOPIC = b"wyohack/" + YOUR_NAME.encode('utf-8') + b"/led/command"
STATUS_TOPIC = b"wyohack/" + YOUR_NAME.encode('utf-8') + b"/led/status"

# Initialize LED Pin (set to output, initially off/high for active-low LEDs)
led = machine.Pin(LED_PIN, machine.Pin.OUT)
# Check your board's LED. If ON=low, use: led.value(1)
# Assuming active-low LED (GPIO 2): value(0) is ON, value(1) is OFF
# We will invert this logic below to be human-readable (True/False)
led_state = False # False means LED is currently OFF (high value)

# --- UTILITY FUNCTIONS ---

def wifi_connect(WIFI_SSID, WIFI_PASSWORD):
    """Connects to the Wi-Fi network."""

# Create a WLAN interface object for Station mode (connecting to a router)

    wlan = network.WLAN(network.STA_IF)

# Activate the Wi-Fi interface

    print("Activating WiFi interface...")

    wlan.active(True)

    time.sleep(1) # Allow some time for activation

# Check if already connected (useful if script restarts)

    if not wlan.isconnected():

        print("Connecting to network:", WIFI_SSID)

# Start the connection attempt

        wlan.connect (WIFI_SSID, WIFI_PASSWORD)

# Wait for connection with a timeout (e.g., 20 seconds)

        max_wait_seconds = 20

        start_time = time.ticks_ms() # Get start time in milliseconds

        print("Waiting for connection", end="")

        while not wlan.isconnected() and time.ticks_diff(time.ticks_ms(), start_time) < max_wait_seconds * 1000:

            print(".", end="")

            time.sleep(1) # Wait 1 second between checks

        print() # Print a newline after the dots/timeout

    else:

        print("Already connected to:", WIFI_SSID)

 
# Verify Connection and Print IP Address

    if wlan.isconnected():

        print("-" * 40) # Print a separator line

        print("WiFi Connection Successful!")

        network_config = wlan.ifconfig() # Get network configuration tuple

        # network_config contains: (IP Address, Subnet Mask, Gateway, DNS Server)

        print("Device IP Address:", network_config[0])

        print("Subnet Mask:", network_config[1])

        print("Gateway:", network_config[2])

        print("DNS Server:", network_config[3])

        print("-" * 40)

    else:

        print("-" * 40)

        print("!!! WiFi Connection Failed !!!")

        print("Please check:")

        print("- Correct SSID and Password?")

        print("- Correct Wi-Fi band (2.4 GHz)?")

        print("- Wi-Fi signal strength?")

        print("-" * 40)



# --- MAIN EXECUTION ---

# Connect Wi-Fi
wifi_connect(WIFI_SSID, WIFI_PASSWORD)

