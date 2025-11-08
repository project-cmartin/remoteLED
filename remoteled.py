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



def get_unique_client_id():
    """Generates a unique MQTT client ID based on the ESP32's MAC address."""
    mac = ubinascii.hexlify(network.WLAN().config('mac'), ':').decode()
    client_id = b"esp32_led_controller_" + mac.encode('utf-8')
    return client_id

def set_led_and_publish_status(client, new_state_bool):
    """Sets the LED state and publishes the corresponding status message."""
    global led_state

    led_value = 1 if new_state_bool else 0
    led.value(led_value)
    led_state = new_state_bool

    status_message = b"ON" if led_state else b"OFF"
    print(f"LED set to: {status_message.decode()}, Publishing status to {STATUS_TOPIC.decode()}")
    client.publish(STATUS_TOPIC, status_message, retain=True)



   # --- MQTT CALLBACK ---

def sub_callback(topic, msg):
    """Handles incoming MQTT messages on the command topic."""
    
    # Note: Topic is not strictly needed here but is provided by MQTTClient
    print(f"Received command: Topic='{topic.decode()}', Message='{msg.decode()}'")
    
    command = msg.decode().strip().upper()
    
    # Case-insensitive ON/OFF control logic
    if command == "ON":
        set_led_and_publish_status(mqtt_client, True)
    elif command == "OFF":
        set_led_and_publish_status(mqtt_client, False)
    else:
        print(f"Invalid command received: {command}. Must be ON or OFF.")




# --- MAIN EXECUTION ---

# Connect Wi-Fi
wifi_connect(WIFI_SSID, WIFI_PASSWORD)


# Prepare MQTT Client
client_id = get_unique_client_id()
print(f"MQTT Client ID: {client_id.decode()}")

try:
    # Initialize and connect MQTT
    mqtt_client = MQTTClient(
        client_id=client_id,
        server=MQTT_BROKER,
        port=1883,
        user=None,
        password=None,
        keepalive=60
    )
    mqtt_client.set_callback(sub_callback)
    
    print(f"Connecting to MQTT broker {MQTT_BROKER}...")
    mqtt_client.connect()
    print("MQTT connected.")
    
    # Subscribe to the command topic
    mqtt_client.subscribe(COMMAND_TOPIC)
    print(f"Subscribed to command topic: {COMMAND_TOPIC.decode()}")
    
    # Initialize and publish the current OFF state
    set_led_and_publish_status(mqtt_client, False)

    # Main Loop
    while True:
        # Check for new messages on the subscribed topic
        mqtt_client.check_msg() 
        time.sleep(1) # Keep the loop responsive but not overly demanding
        
except Exception as e:
    print(f"An error occurred: {e}")
    print("Attempting to reconnect in 10 seconds...")
    time.sleep(10)