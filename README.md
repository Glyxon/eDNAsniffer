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

### Key Hardware Components
* **Microcontroller:** ESP32-WROOM-32E (Ideaspark development board with built-in display).
* **Air Sampling Mechanism:** 3010 Brushless Fan (5V) paired with a Venturi geometry sampling chamber.
* **Desiccant Chamber:** Indicating silica gel to maintain low humidity and prevent DNA degradation post-collection.
* **Capture Media:** Nitrocellulose filter paper (0.2 to 1 µm) for fine eDNA trapping, supported by optional bacterial cellulose matrices (`Komagataeibacter xylinus`) provided by Glyxon BioLabs.

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

### Required Libraries
Install the following libraries via the Arduino Library Manager:
1. `Adafruit BME280 Library` (or BMP280)
2. `ScioSense ENS160` (for eCO2 and TVOC air quality metrics)
3. TFT / GFX graphics libraries compatible with your specific Ideaspark display.

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
