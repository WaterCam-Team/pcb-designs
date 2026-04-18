# WaterCam HAT — GPIO & Connector Pin Map

**Board:** WaterCam_mDot_WittyPi_AHT_BNO_Lepton  
**Target SBC:** Raspberry Pi 4B  
**Stack order (bottom→top):** Raspberry Pi 4B → WittyPi 4 (via stacking header) → WaterCam HAT  
**Schematic:** `WaterCam_mDot_WittyPi_AHT_BNO_Lepton.kicad_sch`  
**Software repo:** [mandeeps/SU-WaterCam](https://github.com/mandeeps/SU-WaterCam)

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ⛔ RESERVED | Pin claimed by WittyPi 4 hardware — do not connect to anything else |
| ⚠️ SHARED | Pin shared by multiple peripherals |
| — | Unassigned / not connected to any HAT signal |

---

## Raspberry Pi 40-Pin GPIO Header (J1)

Physical pin numbers follow the standard Raspberry Pi 40-pin header (odd column = pins 1–39, even column = pins 2–40, top to bottom).  
BCM numbering used throughout software (e.g., `gpiozero`, `libgpiod`, `/boot/config.txt`).

| Phys | BCM | Alt Function | Assigned To | Peripheral | Notes |
|------|-----|-------------|-------------|-----------|-------|
| 1 | — | 3.3 V | VCC rail | AHT20, BNO055 breakouts | Pi 3.3 V; cut when WittyPi shuts Pi off |
| 2 | — | 5 V | VCC rail | FLIR Lepton VIN (J2-P2) | |
| 3 | GPIO2 | SDA1 (I2C1) | I2C bus SDA | FLIR Lepton CCI, AHT20, BNO055, WittyPi RTC | Bus shared; see I2C address map below |
| 4 | — | 5 V | — | — | |
| 5 | GPIO3 | SCL1 (I2C1) | I2C bus SCL | FLIR Lepton CCI, AHT20, BNO055, WittyPi RTC | Bus shared |
| 6 | — | GND | GND | — | |
| 7 | GPIO4 | GPCLK0 | ⛔ RESERVED | WittyPi 4 | WittyPi MCU communication — do not use |
| 8 | GPIO14 | TXD0 (UART0) | NC | — | No-connect in schematic; UART5 used for mDot instead |
| 9 | — | GND | GND | — | |
| 10 | GPIO15 | RXD0 (UART0) | NC | — | No-connect in schematic |
| 11 | GPIO17 | — | ⛔ RESERVED | WittyPi 4 SYS_UP | **Must never be driven by HAT.** WittyPi monitors this line — LOW → WittyPi cuts power, causing boot loop. See [Design Notes](#design-notes). |
| 12 | GPIO18 | PCM.CLK / PWM0 | — | — | |
| 13 | GPIO27 | — | — | — | |
| 14 | — | GND | GND | — | |
| 15 | GPIO22 | — | — | — | |
| 16 | GPIO23 | — | — | — | |
| 17 | — | 3.3 V | — | — | |
| 18 | GPIO24 | — | FLIR Lepton GPIO2 / VSYNC | FLIR Lepton J2-P15 | Rerouted from GPIO17 in v7 schematic fix |
| 19 | GPIO10 | SPI0.MOSI | SPI0 MOSI | FLIR Lepton J2-P5 | |
| 20 | — | GND | GND | — | |
| 21 | GPIO9 | SPI0.MISO | SPI0 MISO | FLIR Lepton J2-P12 | |
| 22 | GPIO25 | — | — | — | |
| 23 | GPIO11 | SPI0.SCLK | SPI0 Clock | FLIR Lepton J2-P3 | |
| 24 | GPIO8 | SPI0.CE0 | SPI0 Chip Select | FLIR Lepton J2-P8 | |
| 25 | — | GND | GND | — | |
| 26 | GPIO7 | SPI0.CE1 | — | — | |
| 27 | GPIO0 | ID_SDA (I2C0) | NC | — | No EEPROM fitted; overlays loaded via config.txt |
| 28 | GPIO1 | ID_SCL (I2C0) | NC | — | No EEPROM fitted |
| 29 | GPIO5 | — | ⚠️ SHARED: mDot PA_6 + manual capture button | mDot remote-start input + pushbutton | Pi drives HIGH when running (PA_6 reads this); button also pulls to GND for manual capture |
| 30 | — | GND | GND | — | |
| 31 | GPIO6 | — | FLIR Lepton RESET_L | FLIR Lepton J2-P17 | HIGH by default; pulse LOW to reset Lepton; used by `lepton_reset.py` |
| 32 | GPIO12 | TXD5 (UART5) | UART5 TX → mDot RX | mDot PA_3 | Enabled via `dtoverlay=uart5`; /dev/ttyAMA5 |
| 33 | GPIO13 | RXD5 (UART5) | UART5 RX ← mDot TX | mDot PA_2 | Enabled via `dtoverlay=uart5`; /dev/ttyAMA5 |
| 34 | — | GND | GND | — | |
| 35 | GPIO19 | PCM.FS / SPI1.MISO | — | — | |
| 36 | GPIO16 | — | BNO055 RST | BNO055 breakout U2 | Active-low reset; hold HIGH normally; pulse LOW to reset IMU |
| 37 | GPIO26 | — | — | — | |
| 38 | GPIO20 | PCM.DIN / SPI1.MOSI | BNO055 INT | BNO055 breakout U2 | Interrupt-driven IMU reads; active-low output from BNO055 |
| 39 | — | GND | GND | — | |
| 40 | GPIO21 | PCM.DOUT | IR-CUT filter control | NIR optical camera | Driven by `take_nir_photos.py`; HIGH/LOW toggles IR-CUT filter |

---

## FLIR Lepton Breakout Board v2 — Connector J2 (2×10, 20-pin)

J2 is a 2×10 male header on the HAT mating to the FLIR Lepton Breakout Board v2.  
Pin convention: odd pins (P1, P3, …, P19) on one row; even pins (P2, P4, …, P20) on the other.  
Reference: [FLIR Lepton Raspberry Pi Guide](https://github.com/FLIR/Lepton/blob/main/docs/RaspberryPiGuide.md)

| J2 Pin | Breakout Board Signal | Pi BCM | Pi Physical | Notes |
|--------|----------------------|--------|-------------|-------|
| P1 | SDA (CCI / I2C) | GPIO2 | 3 | I2C1 SDA; shared with AHT20 and BNO055 |
| P2 | VIN (+5 V) | — | 2 or 4 | Lepton core power |
| P3 | SPI CLK | GPIO11 | 23 | SPI0.SCLK — Lepton SPI clock (not I2C SCL) |
| P4 | NC | — | — | |
| P5 | MOSI | GPIO10 | 19 | SPI0 MOSI |
| P6 | NC (GND) | — | — | |
| P7 | NC (GND) | — | — | Internally tied to Lepton ground plane |
| P8 | CS (SPI chip select) | GPIO8 | 24 | SPI0.CE0 |
| P9 | NC (GND) | — | — | |
| P10 | NC | — | — | |
| P11 | NC | — | — | |
| P12 | MISO | GPIO9 | 21 | SPI0 MISO |
| P13 | NC | — | — | |
| P14 | NC | — | — | |
| P15 | GPIO2 / VSYNC | GPIO24 | 18 | Lepton frame-sync output; was GPIO17 in v6 — **fixed** |
| P16 | VPROG | NC | — | Programming voltage — not used |
| P17 | RESET_L | GPIO6 | 31 | Active-low reset; GPIO6 is HIGH by default; script pulses LOW |
| P18 | PW_DWN_L | +3.3 V direct | — | Tied HIGH → Lepton always powered; no software power-down |
| P19 | SCL (CCI / I2C) | GPIO3 | 5 | I2C1 SCL; shared with AHT20 and BNO055 |
| P20 | NC | — | — | |

> **I2C note:** P1 and P19 connect to the shared I2C1 bus. Use Y-splitter cables when wiring the breakout board directly (pre-HAT assembly). The HAT PCB handles this internally.

---

## Multitech mDot LoRaWAN Module (U3, MTDOT-915) — Connector J1 on mDot

The mDot is powered from the WittyPi 4 P3 auxiliary header (J3), **not** from the Pi's 3.3 V rail, so it stays alive while the Pi is off (required for LoRa receive and remote-start functionality).  
UART interface: `dtoverlay=uart5` in `/boot/config.txt`; serial port `/dev/ttyAMA5`; 115200 8N1.

| mDot Pin | mDot Signal | Connected To | Notes |
|----------|------------|-------------|-------|
| 1 | VDD | J3 Pin 2 (WittyPi 3.3 V always-on) | **Not** Pi 3.3 V — survives Pi shutdown |
| 2 | PA_2 (UART TX) | GPIO13 / RXD5 (Pi pin 33) | mDot transmits → Pi receives |
| 3 | PA_3 (UART RX) | GPIO12 / TXD5 (Pi pin 32) | mDot receives ← Pi transmits |
| 10 | GND | J3 Pin 7 (WittyPi GND) | |
| PA_6 | Digital input | GPIO5 (Pi pin 29) | Pi drives HIGH when running; mDot reads to confirm Pi state |
| PB_1 | Digital output | Q1 MOSFET gate + R3 pull-down | mDot drives HIGH to trigger remote start via MOSFET |

**Remote-start circuit:**  
`mDot PB_1` → Q1 gate (10 kΩ pull-down R3 to GND) → Q1 drain → `WittyPi J3-SW` (pin 5). When mDot asserts PB_1 HIGH via LoRa command, Q1 pulls the WittyPi switch pin LOW, waking the Pi.

---

## Adafruit BNO055 STEMMA QT Breakout (U2, 10-pin header)

BNO055 is an Adafruit breakout board connected via a 10-pin 0.1" header. PS0, PS1, and ADR are pulled to GND by resistors on the breakout board (I2C mode, address 0x28 by default); they need no connections from the HAT.

| Breakout Pin | Signal | Connected To | Notes |
|-------------|--------|-------------|-------|
| VIN | Power in | Pi 3.3 V (J1 pin 1) | Onboard regulator; breakout accepts 3.3–5 V |
| GND | Ground | GND | |
| SDA | I2C1 SDA | GPIO2 (J1 pin 3) | Shared I2C1 bus |
| SCL | I2C1 SCL | GPIO3 (J1 pin 5) | Shared I2C1 bus |
| RST | Reset (active low) | GPIO16 (J1 pin 36) | Pi drives HIGH normally; pulse LOW to reset |
| INT | Interrupt (active low) | GPIO20 (J1 pin 38) | Configure Pi GPIO as input with pull-up |
| PS0 | Protocol select | NC | Pulled to GND on breakout (I2C mode) |
| PS1 | Protocol select | NC | Pulled to GND on breakout (I2C mode) |
| ADR | Address select | NC | Pulled to GND on breakout (I2C addr 0x28) |
| 3V3 | Regulated out | NC | 3.3 V output from breakout regulator; not used |

---

## Adafruit AHT20 Breakout (U1, 4-pin STEMMA QT / header)

AHT20 is a temperature and humidity sensor on a breakout board. Connected via I2C1.

| Breakout Pin | Signal | Connected To | Notes |
|-------------|--------|-------------|-------|
| VIN | Power in | Pi 3.3 V (J1 pin 1) | |
| GND | Ground | GND | |
| SDA | I2C1 SDA | GPIO2 (J1 pin 3) | Shared I2C1 bus |
| SCL | I2C1 SCL | GPIO3 (J1 pin 5) | Shared I2C1 bus |

---

## WittyPi 4 P3 Auxiliary Header (J3 on HAT, 7-pin)

The WittyPi 4 exposes a 7-pin P3 header. The HAT connects to it to draw always-on 3.3 V for the mDot.

| J3 Pin | WittyPi Signal | HAT Connection | Notes |
|--------|---------------|----------------|-------|
| 1 | VOUT | NC | |
| 2 | 3V3 | mDot VDD (U3 pin 1) | Always-on; active even when Pi is off |
| 3 | LED | NC | |
| 4 | ALM | NC | |
| 5 | SW | Q1 Drain | MOSFET switches this to GND for remote start |
| 6 | CATH | NC | |
| 7 | GND | mDot GND + Q1 Source | Common ground for mDot and remote-start circuit |

---

## I2C Device Address Map (I2C1, GPIO2/GPIO3)

All addresses are 7-bit. No conflicts.

| Address | Device | Component | Notes |
|---------|--------|-----------|-------|
| 0x2A | FLIR Lepton CCI | Lepton 3.5 | Camera Command Interface; requires I2C for configuration |
| 0x38 | AHT20 | Temp/humidity sensor | Fixed address; no configurable bits |
| 0x28 or 0x29 | BNO055 | 9-DOF IMU (U2) | Address set by ADDR pin; ADDR=GND → 0x28 (breakout default) |
| 0x48 | LM75B | On-board WittyPi 4 temperature sensor | WittyPi internal component |
| 0x51 | PCF85063A | WittyPi 4 RTC | WittyPi internal component |

### I2C0 (GPIO0/GPIO1)

Not used. No EEPROM fitted. Device-tree overlays loaded manually via `/boot/firmware/config.txt`.

---

## Software / Kernel Configuration

Add the following to `/boot/firmware/config.txt` (Bookworm path; `/boot/config.txt` on older releases):

```ini
# UART5 for mDot LoRa module (GPIO12=TX, GPIO13=RX)
enable_uart=1
dtoverlay=uart5

# I2C clock stretching — enable if BNO055 causes I2C errors
# dtparam=i2c_arm_baudrate=10000

# FLIR Lepton SPI buffer size (add to /boot/cmdline.txt, not config.txt)
# spidev.bufsiz=131072
```

Serial port for mDot: `/dev/ttyAMA5` — use `tio /dev/ttyAMA5` at 115200 baud.

**BNO055 GPIO setup (add to boot script or `/etc/rc.local`):**

```bash
# Hold BNO055 out of reset (GPIO16 must be HIGH before I2C init)
raspi-gpio set 16 op dh

# Optional: configure BNO055 INT as input with pull-up
raspi-gpio set 20 ip pu
```

Or with `gpiozero`:
```python
from gpiozero import OutputDevice, Button
bno_rst = OutputDevice(16, initial_value=True)   # HIGH = not in reset
bno_int = Button(20, pull_up=True)               # active-low interrupt
```

---

## Design Notes

### GPIO17 — WittyPi 4 SYS_UP (CRITICAL)

GPIO17 (Pi physical pin 11) is monitored by the WittyPi 4 to determine whether the Raspberry Pi OS is running. The Pi drives this line HIGH when it is up. **If any peripheral drives GPIO17 LOW** — even briefly during initialization — the WittyPi will interpret it as a shutdown event and cut power, causing a boot loop or preventing boot entirely.

**v6.0 failure:** The Lepton Breakout Board J2-P15 (a GPIO output from the Lepton) was routed to GPIO17. Once the Lepton initialized and asserted P15, it pulled GPIO17 LOW → WittyPi cut power. **Fixed in current schematic:** J2-P15 is now routed to GPIO24 (pin 18), which is otherwise unallocated.

GPIO17 has **no connection** on the HAT PCB and must remain that way.

### GPIO4 — WittyPi 4 Communication

GPIO4 (Pi physical pin 7) is used by WittyPi 4 hardware for MCU communication. Do not assign to other purposes.

### J2-P1 — SDA, Not GND (v6.0 Fixed)

In v6.0, J2-P1 was wired to GND instead of SDA. GPIO2 has a 47 kΩ internal pull-up that is active from reset. Shorting it to GND through the Lepton connector permanently kills I2C1, preventing HAT EEPROM reads and WittyPi RTC communication.

### J2-P8 — SPI CS, Not I2C SCL (v6.0 Fixed)

In v6.0, J2-P8 (Lepton SPI CS) was wired to GPIO3/SCL1 instead of GPIO8/SPI0.CE0. Every SPI transaction would assert CS LOW → pull SCL LOW → freeze the I2C bus mid-transaction.

### BNO055/BNO085 INT and RST Pins

INT is connected to GPIO20 (pin 38) and RST to GPIO16 (pin 36). INT is active-low output from the BNO055; configure as input with pull-up for interrupt-driven IMU reads. RST is active-low input to the BNO055; hold HIGH normally and pulse LOW to reset. (Design issue #10 resolved.)

### mDot VSYNC / SPI note

The Lepton VSYNC signal (J2-P15, now GPIO24) is wired but not currently used by the capture software. The `lepton.c` / `capture.c` tools use SPI polling rather than VSYNC interrupts.

### Manual Capture Button

A pushbutton between GPIO5 (pin 29) and GND is supported by `button-service-gpiozero.py`. GPIO5 is also the line the mDot reads (PA_6) to detect that the Pi is powered on. Brief LOW pulses from button presses are transient and acceptable; the mDot PA_6 input is not time-critical.
