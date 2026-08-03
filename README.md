# eDNA Sniffer (v1.1)

An open-source, low-cost, ESP32-S3/ Rapsberry-Pi powered airborne environmental DNA (eDNA) sampling and monitoring station. 

Developed as part of decentralized biotechnology and open hardware initiatives (Developed by **Glyxon BioLabs** and **BioOlympia**), this project integrates physical air filtration, environmental sensor telemetry (temperature, humidity, pressure, gas quality, and light), and a streamlined molecular biology protocol for downstream 16S rRNA gene amplification and taxonomic profiling. This project is presented at DEFCON 34. 

Contact the creators: 

Dr. David Castillo · glyxonbiolabs@gmail.com  ·  +52 (55) 4140 7607​
BioOlympia (Matt + Zee) · BioOlympia@gmail.com  ·  +1 (971) 319-2665​


---

## 🛠️ System Overview & Architecture


The eDNA Sniffer combines an **ESP32 microcontroller** (Ideaspark board) with an environmental sensor hub, an air sampling chamber driven by a brushless fan, and an optimized dual-capture physics configuration.

```
[Air Intake] → [Membrane Filter / Fine Mesh] → [3010 Fan] → [Silica Gel Chamber] → [Air Exhaust]
```

Airflow Diagram (Sampling Enclosure)

To build the physical collector using your boards and the fan, you need to design or adapt a small airtight container (this could be a 3D-printed enclosure or a modified plastic container):


1.	The fan pulls or pushes outdoor air, forcing it through a small chamber (Venturi collector)  where you position your eDNA collection membrane.
2.	The filtered, dried air then flows past rate is monitored by different sensors (AHT21/BME280 and ENS160) to log precise environmental sampling parameters (humidity, background volatile organic compounds, and temperature).



Implementing a dual-capture mechanism within this Venturi geometry leverages fluid dynamics beautifully to sort particles by size and mass. In aerosol science and environmental sampling, this is conceptually similar to a simplified cascade impactor.
Here is how the physics of this dual-capture setup benefits your eDNA sampling:
1. Intake Pre-Filter (Coarse eDNA Capture)
•	The Mechanism: At the wide base, the air velocity entering from the 3010 fan is relatively slow, but the surface area is at its largest.
•	What it Captures: Large biological vectors such as whole pollen grains, fungal spores, insect fragments, and heavy environmental dust particles that contain cellular material.
•	The Benefit: It acts as a primary filter. If these massive particles reached the narrow throat or the fine filter, they would immediately clog the system (causing severe back pressure) and reduce the sampler's operational lifespan in the field.



2. Venturi Throat / Upper Trap (High-Velocity Fine eDNA Capture)
•	The Mechanism: As the air is forced through the constriction, its velocity peaks.
•	What it Captures: Micro-droplets, fine aerosolized particles, single bacteria, and naked/free-floating extracellular DNA strands bound to microscopic dust (PM2.5 or smaller). The higher momentum allows these tiny particles to be driven forcefully into a fine-pore membrane (like glass fiber or nylon).
•	The Benefit: This is where you isolate the highly integrated, long-range eDNA signals traveling through the air mass rather than just localized debris.
How to Read Sensors in this Dual Setup
By utilizing the different sensor placement options shown in the diagram, you can monitor the physical performance of this dual-capture chamber in real-time with your ESP32:
•	Monitoring Clogging (Differential Pressure): If you place the BME280/BMP280 at Location 2 (Venturi Throat) or Location 1 (Post-Filter), you can track the static pressure drop over time. As filters capture eDNA and start to saturate, the pressure values will shift drastically. When the pressure drop levels off or hits a critical threshold, the ESP32 LCD can alert you that the filters are full and the device has completed its run.
•	Correlating Environmental Data: The ENS160 gas readings (eCO2/TVOC) will help you cross-reference your biological collection with environmental context—letting you know if a high yield of eDNA correlates with sudden spikes in organic volatiles or stale air masses.



### Key Hardware Components

* **Microcontroller:** ESP32-WROOM-32E (Ideaspark development board with built-in display).
* **Air Sampling Mechanism:** 3010 Brushless Fan (5V) paired with a Venturi geometry sampling chamber.
* **Desiccant Chamber:** Indicating silica gel to maintain low humidity and prevent DNA degradation post-collection.
* **Capture Media:** Nitrocellulose filter paper (0.2 to 1 µm) for fine eDNA trapping, supported by optional bacterial cellulose matrices (`Komagataeibacter xylinus`) can be provided by Glyxon BioLabs if you need some.

2. Sensor Connection Architecture (I2C)
Both the ENS160+AHT21 module and the BME280/BMP280 operate primarily via the I2C communication protocol. This means they can share the same data (SDA) and clock (SCL) lines, drastically simplifying the circuit layout on your green prototyping PCB.
Pin Mapping (ESP32 Ideaspark):
By default, most ESP32 boards configure the I2C protocol on the following pins, though you can redefine them in your Arduino dependencies.

Watch out for I2C addresses! If your pressure chip turns out to be a BMP280 instead of a BME280, keep in mind that its default I2C address usually shifts between 0x76 and 0x77. The ENS160 typically uses address 0x53. They will not collide on the bus.
The LDR (GL5516 Light Sensor):
To measure ambient light, you need to build a voltage divider using one of your 10kΩ resistors. This translates the varying resistance of the LDR into a voltage the ESP32 can read:
1.	Connect one end of the LDR to 3.3V.
2.	Connect the other end of the LDR to an analog pin on the ESP32 (e.g., GPIO 34 or 35).
3.	From that same middle connection point, connect a 10kΩ resistor to GND.

Controlling the Fan (3010 Fan):
The fan runs on 5V. Do not connect it directly to an ESP32 data pin because you will burn out the chip (ESP32 pins only output 3.3V and about 20-40mA).
•	Simple Option: Connect it directly to the 5V/VIN and GND pins on the ESP32 so that it draws air continuously as soon as the system powers up.



---

## 🔌 Wiring & Pin Mapping

Both sensor modules operate on the **I2C protocol**, allowing them to share a common data bus (`SDA` on GPIO 21, `SCL` on GPIO 22).

### Complete Wiring Matrix

| Component | Pin | Connects To (ESP32) | Purpose / Notes |
| :--- | :--- | :--- | :--- |
| **ENS160+AHT21 Module** | `VCC` | `3V3` | 3.3V Power Supply |
| | `GND` | `GND` | Common Ground |
| | `SCL` | `GPIO 22` | I2C Clock Line (Shared) |
| | `SDA` | `GPIO 21` | I2C Data Line (Shared) |
| **BME280/BMP280 Module** | `VCC` | `3V3` | 3.3V Power Supply |
| | `GND` | `GND` | Common Ground |
| | `SCL` | `GPIO 22` | I2C Clock Line (Shared) |
| | `SDA` | `GPIO 21` | I2C Data Line (Shared) |
| **GL5516 Photoresistor (LDR)** | `Pin 1` | `3V3` | Voltage Source |
| | `Pin 2` | `GPIO 34` | Analog Input & Divider Junction |
| **10kΩ Resistor** | `Lead A` | `GPIO 34` | Connected to Ldr Pin 2 |
| | `Lead B` | `GND` | Pulls signal to Ground |
| **3010 Brushless Fan (5V)** | `Red Wire` | `5V / VIN` | Direct power from USB/Power Bank source |
| | `Black Wire` | `GND` | Continuous ground connection |

> ⚠️ **Important Safety Check:** Keep the 5V brushless fan strictly connected to the `5V / VIN` pin. Connecting 5V inductive loads directly to the 3.3V digital rail can permanently damage the ESP32 internal voltage regulator.

---

## 💻 Firmware & Arduino IDE Setup

Basic Code Logic (Arduino IDE)
For ESP32 boards with built-in LCD screens, you will need to install these libraries from the Arduino Library Manager:
•	Adafruit BME280 Library (or BMP280)
•	ScioSense_ENS160 (for the advanced air quality sensor)
•	Specific graphics libraries for your Ideaspark display (usually TFT_eSPI or Adafruit_GFX, depending on the exact LCD model it uses).

### Required Libraries
Install the following libraries via the Arduino Library Manager:
1. `Adafruit BME280 Library` (or BMP280)
2. `ScioSense ENS160` (for eCO2 and TVOC air quality metrics)
3. TFT / GFX graphics libraries compatible with your specific Ideaspark display.

Recommended Steps
•	Identify the pressure sensor: Use a magnifying glass to check the tiny silver pressure chip. If it is tiny and perfectly square with 4 internal pins, it is a BME280 (it measures humidity). If it is rectangular, it is a BMP280. Knowing this will let you fine-tune the code.
•	Field Power Supply: Since this is an environmental sampling device, you will need a portable power source. The ESP32 draws a fair amount of current if Wi-Fi is active, but by keeping it turned off or using a standard 5V power bank connected to the USB port, you can easily run both the microcontroller and the fan during your field trips.

To connect all your components together safely using your green prototyping PCB, you can map out your wiring based on the functional groups.
Because the ESP32 operates on 3.3V logic, we must power the logic lines of the sensors with 3.3V, while running the 5V fan directly from the main power input pin (5V or VIN).


### Basic Sketch Template
```cpp
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h> // Change to BMP280 if needed
#include <ScioSense_ENS160.h>

Adafruit_BME280 bme;
ScioSense_ENS160 ens160(ENS160_I2CADDR_0); // Typical address 0x53

const int ldrPin = 34; // Analog pin for light sensor

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22); // Initialize I2C on pins 21 (SDA) and 22 (SCL)
  
  if (!bme.begin(0x76)) {
    Serial.println("Could not find a valid BME280/BMP280 sensor!");
  }
  if (!ens160.begin()) {
    Serial.println("Could not find a valid ENS160 sensor!");
  }
  ens160.setMode(ENS160_OPMODE_STANDARD);
}

void loop() {
  // 1. Read basic environmental data
  float temp = bme.readTemperature();
  float pres = bme.readPressure() / 100.0F;
  float hum = bme.readHumidity(); 

  // 2. Read air quality
  if (ens160.available()) {
    ens160.measure(true);
    uint16_t eco2 = ens160.getECO2();
    uint16_t tvoc = ens160.getTVOC();
    Serial.printf("eCO2: %d ppm | TVOC: %d ppb\n", eco2, tvoc);
  }

  Serial.printf("Temp: %.2f°C | Pres: %.2fhPa | Hum: %.2f%%\n", temp, pres, hum);

  // 3. Read ambient light
  int lightRaw = analogRead(ldrPin);
  Serial.printf("Light (Raw): %d\n", lightRaw);

  delay(2000);
}
```

Prototyping PCB Layout Instructions
When soldering these pieces onto a Mingjinda Electronics perfboard, follow these spatial layout and structural tips:
1. Create Power and Ground Rails
Dedicate two long continuous rows of holes on your PCB to act as your Power Rails.
•	Run a jumper wire from the ESP32 3V3 pin to your positive rail.
•	Run a jumper wire from the ESP32 GND pin to your negative ground rail.
•	Connect the VCC and GND pins of all your sensors directly to these rails.


The Shared I2C Bus
You do not need separate pins on the ESP32 for your two sensor boards. Solder a wire connecting the SDApin of the ENS160 to the SDA pin of the BME280, then run a single wire from that junction to GPIO 21. Do exactly the same for the SCL pins, running them to GPIO 22.
3. Assembling the LDR Circuit
Solder one leg of the photoresistor and one leg of your 10kΩ resistor into the same electrical track (or bridge them with solder). From that exact same joint, run a wire to GPIO 34. Connect the remaining free leg of the photoresistor to your 3V3 rail, and the remaining free leg of the resistor to your GND rail.
⚠️ Important Safety Check: Ensure your brushless fan wires do not accidentally touch the 3.3V rail. Connecting a 5V inductive load directly to the 3.3V digital rail can permanently destabilize or burn out the ESP32 inner voltage regulator. Keep the fan connections strictly on the 5V/VIN pin.






---

## 🧬 Downstream Molecular Workflow (16S eDNA)

Captured air filters undergo standard molecular processing to extract and amplify bacterial communities:

1. **Harvesting & Lysis:** Section the nitrocellulose filter using sterile tools. Apply a co-extraction strategy (mild detergent incubation followed by short 30s bead-beating) to release intracellular DNA from spores without destroying free extracellular strands.
2. **Purification:** Use a silica spin-column architecture (e.g., Omega Bio-tek) via **Bind-Wash-Elute** protocols to clear airborne PCR inhibitors (soot, humic acids).
3. **Amplification (Pfu Polymerase):** Target the universal 16S rRNA gene (approx. 1.5 kb using 27F/1492R primers) with high-fidelity Pfu DNA Polymerase.
   * *Initial Denaturation:* 95°C for 2–5 min
   * *30–35 Cycles:* 95°C (30s) → 52–55°C (30s) → 72°C (2–3 min extension)
   * *Final Extension:* 72°C for 5–10 min
4. **Verification:** Run a 5 µL aliquot on a 1% agarose gel to confirm a clean target band at ~1,500 bp.

---

## 📊 Bioinformatics & Taxonomic Analysis

* **Quality Control:** Inspect reads using **FastQC** (filter Q-scores < 15).
* **Alignment & Classification:** Utilize free open-source reference databases (**SILVA** or **GreenGenes2**) via local tools like **QIIME 2** / **DADA2** or cloud platforms like **Galaxy**.
* **Visualization:** Generate relative abundance stacked bar charts, homology heatmaps, and phylogenetic trees via **ITOL** or **Microreact**.

---
