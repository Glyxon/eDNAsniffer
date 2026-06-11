# eDNA Sniffer v1.0 🔬💨

An open-source, low-cost autonomous environmental monitoring station and biological aerosol sampler. The eDNA Sniffer pairs a Smart Citizen-like telemetry suite (VOCs, eCO2, Temperature, Humidity, Barometric Pressure) with a microfluidic Venturi-effect active trap to capture and preserve environmental DNA (eDNA) for 16S rRNA microbiome profiling.

Developed at Glyxon Biolabs (Mexico City) and BioOlympia (Washington)

---

## 📁 Repository Structure

```text
eDNA-Sniffer/
├── firmware/             # MicroPython source code for ESP32
│   ├── boot.py           # Device initialization and WiFi setup
│   ├── main.py           # Main asynchronous execution loop & sensor logging
│   └── drivers/          # Hardware driver scripts for I2C sensors
│       ├── ens160.py     # Driver for ENS160 (VOC / eCO2)
│       ├── aht2x.py      # Driver for AHT21 (Temp / Hum)
│       └── bmp280.py     # Driver for BMP280 (Barometric Pressure)
│
├── hardware/             # Schematics and PCB layouts
│   ├── schematics/       # Wiring diagrams (Fritzing / KiCad)
│   └── pinout_map.md     # GPIO allocation table for ESP32
│
├── 3d_models/            # CAD files for digital manufacturing
│   ├── venturi_tube.stl  # Monolithic Venturi colector (PLA)
│   ├── trap_housing.stl  # Filter holder (0.22um membrane) & Silica bed enclosure
│   └── main_case.stl     # Weatherproof main enclosure for electronics
│
└── docs/                 # Methodology, protocols, and BOM
    ├── protocol_16S.md   # Post-capture lysis and PCR amplicons protocol
    └── bill_of_materials.md # Flat cost matrix for electronic components

---

## 🛠️ System Overview & Logic

The eDNA Sniffer operates as an autarkic, state-solid device:
1. **Telemetry Loop:** The ESP32 continuously polls the sensor suite via a shared I2C bus.
2. **Conditional Capture:** The software triggers the 5V blower fan via a MOSFET switch only when targeted environmental conditions (e.g., specific humidity/temperature thresholds or VOC spikes) are met.
3. **Aerodynamic Impact:** Air is forced through a 3D-printed Venturi tube, accelerating particles and stamping bioaerosols directly onto a 0.22 µm Nitrocellulose membrane.
4. **In-situ Preservation:** An orange-indicating silica gel bed immediately dehydrates the chamber post-impact, halting nuclease degradation without the need for active refrigeration.

---

## ⚡ Pinout Mapping (ESP32 DevKit v1)

| ESP32 GPIO | Component Pin | Description |
| :--- | :--- | :--- |
| **3.3V** | VCC (Sensors) | Power line for ENS160, AHT21, BMP280 |
| **GND** | GND (All) | Common Ground reference |
| **VIN (5V)**| V+ (MOSFET) | Raw USB 5V rail to power the 4010 Blower Fan |
| **GPIO 21** | SDA | Shared I2C Data line (ENS160 / AHT21 / BMP280) |
| **GPIO 22** | SCL | Shared I2C Clock line (ENS160 / AHT21 / BMP280) |
| **GPIO 23** | SIG / GATE | MOSFET Gate trigger to activate the fan |
| **GPIO 34** | ADC1_CH6 | Analog input from GL5516 LDR / 10kΩ voltage divider |

---

## 📜 License
This project is licensed under the **CERN Open Hardware Licence Version 2 - Strongly Reciprocal (CERN-OHL-S)**. Anyone can manufacture, modify, and distribute this design, provided all derivative works remain open-source under the same terms.

**Glyxon Biolabs - 2026**
