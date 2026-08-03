# eDNA Sniffer: Open-Source Airborne Environmental DNA Sampler

> **Version:** 1.0v / 1.1v  
> **Status:** Open Hardware & Frugal Molecular Biology Protocol

The **eDNA Sniffer** is an open-hardware air sampling node designed to capture airborne environmental DNA (eDNA) bound to water micro-droplets, spores, pollen, or PM2.5/PM10 suspended particulate matter. By combining a Venturi fluid-dynamics capture enclosure with ESP32 sensor telemetry and a 16S rRNA molecular pipeline, the system allows simultaneous collection of biological material and environmental parameters (humidity, pressure, eCO2, TVOC, ambient light).

---

## Table of Contents
1. [Physical Concept & Fluid Dynamics](#1-physical-concept--fluid-dynamics)
2. [Hardware & Wiring Matrix](#2-hardware--wiring-matrix)
3. [Firmware & ESP32 Implementation](#3-firmware--esp32-implementation)
4. [Molecular Biology Protocol (Extraction & 16S PCR)](#4-molecular-biology-protocol-extraction--16s-pcr)
5. [Bioinformatics & Taxonomic Pipeline](#5-bioinformatics--taxonomic-pipeline)
6. [Troubleshooting Guide](#6-troubleshooting-guide)
7. [Reporting Potential Biological Threats](#7-reporting-potential-biological-threats)

---

## 1. Physical Concept & Fluid Dynamics

The sampling enclosure forces ambient air through a physical trap using a 3010 cooling fan/blower, preserving the sample with an integrated desiccant chamber.

### Airflow Architecture
