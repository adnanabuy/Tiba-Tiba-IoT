from machine import ADC, Pin
import network
import urequests
import time
from dht import DHT11


dht_sensor = DHT11(Pin(4))  
soil_sensor = ADC(Pin(34))
soil_sensor.atten(ADC.ATTN_11DB)

# Fungsi normalisasi nilai ke rentang 0 - 100
def normalize(value, min_val=0, max_val=4095):
    return round((value - min_val) / (max_val - min_val) * 100, 2)

# Koneksi WiFi
SSID = "Internet"
PASSWORD = "wates001"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        pass
    print("Terhubung ke WiFi:", wlan.ifconfig())

# Token dan URL Ubidots
UBIDOTS_TOKEN = "BBUS-sO7jcowJflRiYQo1if0D9r9BEEy4rJ"
DEVICE_LABEL = "esp-tti"
DEVICE_URL = f"https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}/"
FLASK_URL = f"http://192.168.0.104:8080/save"

# Mengirim data ke Ubidots
def send_data(temp, air_hum, soil_hum):
    headers = {"X-Auth-Token": UBIDOTS_TOKEN, "Content-Type": "application/json"}
    data = {
        "temperature": temp,
        "air humidity": air_hum,
        "soil humidity": soil_hum
    }
    response = urequests.post(DEVICE_URL, json=data, headers=headers)
    response2 = urequests.post(FLASK_URL, json=data, headers=headers) 
    print(response.text)
    print(response2.text)
    response.close()
    response2.close()

# Inisialisasi nilai awal
temperature = None
humidity = None
dht_counter = 0

# Main loop
connect_wifi()
while True:
    try:
        if dht_counter % 5 == 0:
            print("Reading DHT11...")  
            dht_sensor.measure()
            time.sleep(3) 
            temp_reading = dht_sensor.temperature()
            humidity_reading = dht_sensor.humidity()
            
            if temp_reading is not None and humidity_reading is not None:
                temperature = temp_reading
                humidity = humidity_reading
        if temperature is None:
            temperature = 0 
        if humidity is None:
            humidity = 0

      
        soil_value = normalize(soil_sensor.read())

        print(f"Temperature: {temperature}°C, Air Humidity: {humidity}%, Soil Humidity: {soil_value}")

        send_data(temperature, humidity, soil_value)

    except Exception as e:
        print("Error:", e)

    dht_counter += 1
    time.sleep(10)