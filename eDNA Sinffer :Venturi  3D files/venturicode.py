import time
import machine
import bme280  # Assumes a standard MicroPython BME280 I2C library is present

# Hardware Interface Configuration
FAN_PIN = 14
i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))  # Adjust pins for your hardware
bme = bme280.BME280(i2c=i2c, address=0x76)

# Setup low-side N-Channel MOSFET switch
fan = machine.Pin(FAN_PIN, machine.Pin.OUT)
fan.value(0)  # Force absolute safe state on boot

# Target Environmental Thresholds (Adjustable)
TEMP_MAX_THRESHOLD = 25.0  # Do not sample if ambient temp exceeds 25.0°C
HUM_MIN_THRESHOLD = 65.0   # Only initiate sampling if humidity is >= 65%
HYSTERESIS_TEMP = 1.5      # Temperature safety offset
HYSTERESIS_HUM = 3.0       # Humidity safety offset

# Asynchronous Polling Interval
POLL_INTERVAL = 5000       # Poll telemetry metrics every 5000ms (5 seconds)
COOLDOWN_DURATION = 900000 # 15-minute hardware lock-out period in milliseconds

# FSM State Definitions
STATE_IDLE = 0
STATE_SAMPLING = 1
STATE_COOLDOWN = 2

# Initial Tracking States
current_state = STATE_IDLE
prev_millis = time.ticks_ms()
cooldown_start = 0

print("Glyxon eDNA Node Active [MicroPython Core]. Commencing climate monitoring...")

while True:
    current_millis = time.ticks_ms()

    # Non-blocking Asynchronous Telemetry Loop
    if time.ticks_diff(current_millis, prev_millis) >= POLL_INTERVAL:
        prev_millis = current_millis

        # Read sensor matrices
        try:
            temp_str, press_str, hum_str = bme.values
            current_temp = float(temp_str.replace('C', ''))
            current_hum = float(hum_str.replace('%', ''))
        except Exception as e:
            print("Error parsing I2C sensor data:", e)
            continue

        print(f"Temp: {current_temp}°C | Hum: {current_hum}%")

        # Finite State Machine Execution
        if current_state == STATE_IDLE:
            # Core Trigger Condition: Cool temperature AND high relative humidity
            if current_temp <= TEMP_MAX_THRESHOLD and current_hum >= HUM_MIN_THRESHOLD:
                print("➔ [BIOLOGICAL ALERT] Target environmental window hit. Commencing capture...")
                fan.value(1)  # Saturate the MOSFET Gate to spin up the fan
                current_state = STATE_SAMPLING

        elif current_state == STATE_SAMPLING:
            # Safe Shut-down Sequence using Hysteresis to damp jitter/fluctuations
            if (current_temp > (TEMP_MAX_THRESHOLD + HYSTERESIS_TEMP) or 
                current_hum < (HUM_MIN_THRESHOLD - HYSTERESIS_HUM)):
                print("➔ [NOTICE] Atmospheric conditions degrading. Aborting sampling run...")
                fan.value(0)  # Cut motor power line
                cooldown_start = time.ticks_ms()
                current_state = STATE_COOLDOWN

        elif current_state == STATE_COOLDOWN:
            # Hardware recovery lock-out phase
            if time.ticks_diff(time.ticks_ms(), cooldown_start) >= COOLDOWN_DURATION:
                print("➔ Cooldown complete. Re-entering IDLE surveillance loop.")
                current_state = STATE_IDLE