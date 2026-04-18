# SU WaterCam PCB

Custom KiCad HAT for the **SU-WaterCam** project. Stacks on a Raspberry Pi 4B via a WittyPi 4 RTC/power-manager board, adding thermal imaging, LoRaWAN telemetry, IMU orientation, and environmental sensing.

**Software repo:** [mandeeps/SU-WaterCam](https://github.com/mandeeps/SU-WaterCam)  
**Schematic/pin map:** [PIN_MAP.md](PIN_MAP.md)

---

## Stack Order

Raspberry Pi 4B → WittyPi 4 (stacking header) → WaterCam HAT

---

## Components

| Reference | Part | Interface | Notes |
|-----------|------|-----------|-------|
| U2 | Adafruit BNO055 STEMMA QT | I2C1 (0x28) | 9-DOF IMU; INT→GPIO20, RST→GPIO16 |
| U3 | Multitech MTDOT-915 | UART5 (GPIO12/13) | LoRaWAN; always-on 3.3 V from WittyPi J3 |
| U1 | Adafruit AHT20 | I2C1 (0x38) | Temp/humidity |
| J2 | FLIR Lepton Breakout v2 | SPI0 + I2C1 | 2×10 header; SPI for image data, I2C for CCI |
| J3 | WittyPi 4 P3 header | — | Taps always-on 3.3 V and SW pin for mDot |
| Q1 | MOSFET | — | mDot PB_1 pulls WittyPi SW low for remote wake |

---

## Power Domains

| Rail | Source | Powers |
|------|--------|--------|
| 3.3 V (Pi) | Pi J1 pin 1 | AHT20, BNO055 breakout |
| 5 V (Pi) | Pi J1 pin 2/4 | FLIR Lepton VIN (J2-P2) |
| 3.3 V (always-on) | WittyPi J3 pin 2 | mDot VDD — survives Pi shutdown |

---

## PCB Details

- **Layers:** 2 (F.Cu, B.Cu)
- **Signal traces:** 0.25 mm
- **Power traces:** 0.5 mm
- **Clearance:** 0.20 mm (default net class)

---

## PCB Images

- **Wiring/Layout Diagram**  
  <img src="https://github.com/user-attachments/assets/d6411cc1-ba6d-43ef-b311-78df43dfbbb7" width="600" alt="Wiring/Layout Diagram of SU-WaterCam PCB" />

- **PCB Render**  
  <img src="https://github.com/user-attachments/assets/2e79f4ec-2771-4074-9adf-4b85ffbe03e6" width="600" alt="3D Render of SU-WaterCam PCB" />
