# code_climate_fsm.py  -  Climate-triggered eDNA sampling FSM
# CircuitPython port of the colleague's MicroPython node.
# Adafruit Feather ESP32-S3 TFT.
#
# What changed from the MicroPython original:
#   machine            -> board + digitalio      (CircuitPython has no 'machine')
#   bme280 (strings)   -> adafruit_bme280 (floats; no more .replace('C',''))
#   machine.I2C(0,...) -> board.STEMMA_I2C()
#   time.ticks_ms/diff -> time.monotonic() seconds
#
# Requires in /lib:  adafruit_bme280

import time
import board
import digitalio
from analogio import AnalogIn
import adafruit_bmp280
import adafruit_ahtx0
import adafruit_ens160

# --- Pin Definitions ------------------------------------------------------
FAN_PIN = board.D5            # gate of the logic-level MOSFET (was GPIO14)
PHOTORESISTOR_PIN = board.A0

# --- Hardware -------------------------------------------------------------
i2c = board.STEMMA_I2C()      # built-in Qwiic; use board.I2C() for header pins
pressure_sensor = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, 0x76)
temp_hum_sensor = adafruit_ahtx0.AHTx0(i2c)
gas_sensor = adafruit_ens160.ENS160(i2c)

fan = digitalio.DigitalInOut(FAN_PIN)
fan.direction = digitalio.Direction.OUTPUT
fan.value = False            # force safe state on boot

light_sensor = AnalogIn(PHOTORESISTOR_PIN)

# --- Target environmental thresholds -------------------------------------
TEMP_MAX_THRESHOLD = 30.0    # do not sample if ambient temp exceeds this (C)
HUM_MIN_THRESHOLD  = 50.0    # only sample if RH >= this (%)
HYSTERESIS_TEMP    = 1.5     # temp offset to damp jitter on shut-down
HYSTERESIS_HUM     = 3.0     # RH offset to damp jitter on shut-down

# --- Timing (seconds; MicroPython used ms) -------------------------------
POLL_INTERVAL     = 5.0      # poll telemetry every 5 s
COOLDOWN_DURATION = 10.0    # 15-minute hardware lock-out
SAMPLING_DURATION = 20.0    # 15-minute hardware lock-out

# --- FSM states -----------------------------------------------------------
STATE_IDLE     = 0
STATE_SAMPLING = 1
STATE_COOLDOWN = 2

current_state  = STATE_IDLE
prev_t         = time.monotonic()
cooldown_start = 0.0
sampling_start = 0.0

print("Glyxon eDNA Node Active [CircuitPython Core]. Commencing climate monitoring...")

while True:
    now = time.monotonic()

    # Non-blocking telemetry poll
    if now - prev_t >= POLL_INTERVAL:
        prev_t = now

        try:
            current_temp = temp_hum_sensor.temperature          # float, degrees C
            current_hum = temp_hum_sensor.relative_humidity     # float, %RH
            current_pressure = pressure_sensor.pressure

            gas_sensor.temperature_compensation = current_temp
            gas_sensor.humidity_compensation = current_hum

            # current_gas_aqi = gas_sensor.AQI
            # current_gas_tvoc = gas_sensor.TVOC
            current_gas_eco2 = gas_sensor.eCO2

            current_ldr = light_sensor.value / 65536 * 100

        except Exception as e:                       # keep the node alive
            print("Error reading Sensors:", e)
            continue

        print("Temp: %.1f C | Hum: %.1f %% | Pressure: %.1f hPa | eCO2: %.1f ppm | Light: %f %% | State: %d" % (current_temp, current_hum, current_pressure, current_gas_eco2, current_ldr, current_state))

        if current_state == STATE_IDLE:
            # Trigger: cool AND humid
            if current_temp <= TEMP_MAX_THRESHOLD and current_hum >= HUM_MIN_THRESHOLD:
                print("-> [BIOLOGICAL ALERT] Target window hit. Commencing capture...")
                fan.value = True
                sampling_start = time.monotonic()
                current_state = STATE_SAMPLING

        elif current_state == STATE_SAMPLING:
            # Shut down (with hysteresis) once conditions drift out of window
            if (current_temp > (TEMP_MAX_THRESHOLD + HYSTERESIS_TEMP) or
                    current_hum < (HUM_MIN_THRESHOLD - HYSTERESIS_HUM)):
                print("-> [NOTICE] Conditions degrading. Aborting sampling run...")
                fan.value = False
                cooldown_start = time.monotonic()
                current_state = STATE_COOLDOWN

            elif time.monotonic() - sampling_start >= SAMPLING_DURATION:
                print("-> Sampling complete. Entering cooldown.")
                fan.value = False
                cooldown_start = time.monotonic()
                current_state = STATE_COOLDOWN

        elif current_state == STATE_COOLDOWN:
            if time.monotonic() - cooldown_start >= COOLDOWN_DURATION:
                print("-> Cooldown complete. Re-entering IDLE surveillance loop.")
                current_state = STATE_IDLE
