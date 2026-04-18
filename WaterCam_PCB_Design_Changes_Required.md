# WaterCam PCB HAT — Design Changes Required

**Prepared:** 2026-03-26  
**Last updated:** 2026-04-18  
**Board version analyzed:** WaterCam_v6.0_OFM  
**Current schematic:** WaterCam_mDot_WittyPi_AHT_BNO_Lepton.kicad_sch (v7, fixes applied)  
**Stack:** Raspberry Pi 4B → WittyPi 4 (40-pin stacking HAT) → This PCB (on top via stacking header)

---

## Issue Status Summary

| # | Issue | Priority | Status |
|---|-------|----------|--------|
| 1 | J2 connector pinout wrong | Critical | ✅ Fixed in schematic |
| 2 | GPIO17 conflict (WittyPi SYS_UP) | Critical | ✅ Fixed — J2-P15 → GPIO24 |
| 3 | mDot UART connection | Critical | ✅ Was already correct |
| 4 | mDot antenna connection | Critical | ✅ N/A — mDot has built-in u.FL |
| 5 | IR-CUT camera GPIO circuit | High | ⏸ Deferred — circuit is external to HAT PCB |
| 6 | WittyPi CATH/VOUT unconnected | High | ⏸ Deferred — not needed for current use case |
| 7 | HAT EEPROM missing | High | ⏸ N/A — EEPROM not needed on this board |
| 8 | No decoupling capacitors | High | ⚠️ Open — PCB layout change needed |
| 9 | No I2C pull-up resistors | High | ⚠️ Open — PCB layout change needed |
| 10 | BNO055/085 ambiguity + INT/RST | Medium | ✅ Fixed — BNO055 confirmed; INT→GPIO20, RST→GPIO16 |
| 11 | Q1 MOSFET oversized | Medium | ⚠️ Open — functional but inefficient |
| 12 | Stacking header height | Medium | ⚠️ Open — BOM note only; verify before fab |
| 13 | mDot duplicate pad "24" | Medium | ⚠️ Open — footprint edit needed |
| 14 | Q1 gate resistor missing | Medium | ⚠️ Open — add R8 100Ω |
| 15 | mDot VDD decoupling | Low | ⚠️ Open — same as #8 |
| 16 | mDot nReset unconnected | Low | ⚠️ Open — tie HIGH or connect GPIO26 |
| 17 | Lepton PW_DWN_L unconnected | Low | ✅ Fixed — P18 tied to +3.3V |
| 18 | Board-level 3.3V rail | Low | ⚠️ Open — deferred |

---

## Critical — Hardware Will Not Function Without These Fixes

### 1. ~~FLIR Lepton Breakout v2 (J2) Connector Pinout Is Wrong~~ — FIXED

**Problem:** The J2 connector (FLIR Lepton Breakout Board v2 host interface, 2×10 20-pin) has signals assigned to wrong pins. Almost all SPI and I2C connections are misrouted.

**FLIR Lepton Breakout v2 J2 Correct Pinout** (from FLIR document 250-0577-24):

| Pin | Signal | Direction | Raspberry Pi GPIO |
|-----|--------|-----------|-------------------|
| P1  | SDA    | Bidirectional (I2C) | GPIO2/SDA1 (Pi pin 3) |
| P2  | VIN    | Power in (3.3V–5V)  | 5V (Pi pin 2) |
| P3  | SPI_CLK | Input to Lepton    | GPIO11/SPI0.SCLK (Pi pin 23) |
| P4  | SPI_CLK | (parallel/redundant) | — |
| P5  | SPI_MOSI | Input to Lepton   | GPIO10/SPI0.MOSI (Pi pin 19) |
| P6  | GND    | —                   | GND |
| P7  | GND    | —                   | GND |
| P8  | SPI_CS | Input (active low)  | GPIO8/SPI0.CE0 (Pi pin 24) |
| P9  | —      | NC                  | — |
| P10 | SPI_CS_L | Input (active low) | (same net as P8 or alternate CS) |
| P11 | GPIO3  | Lepton GPIO         | NC or free GPIO |
| P12 | SPI_MISO | Output from Lepton | GPIO9/SPI0.MISO (Pi pin 21) |
| P13 | GPIO0  | Lepton GPIO         | NC or free GPIO |
| P14 | SPI_CS | (duplicate/alt)     | — |
| P15 | GPIO2  | Lepton GPIO         | Use GPIO24 or GPIO25 (NOT GPIO17) |
| P16 | VPROG  | Programming voltage | NC (leave floating or connect to 3.3V) |
| P17 | RESET_L | Input (active low) | GPIO6 (Pi pin 31) — kept |
| P18 | PW_DWN_L | Input (active low) | Assign free GPIO (e.g., GPIO25) |
| P19 | SCL    | Bidirectional (I2C) | GPIO3/SCL1 (Pi pin 5) |
| P20 | GPIO1  | Lepton GPIO         | NC |

**Current (wrong) mapping:**
| J2 Pin | Current net | Correct net |
|--------|-------------|-------------|
| P1     | GND         | SDA/GPIO2 ← CRITICAL |
| P5     | SDA/GPIO2   | SPI_MOSI/GPIO10 ← CRITICAL |
| P7     | SPI_CLK/GPIO11 | GND ← CRITICAL |
| P8     | SCL/GPIO3   | SPI_CS/GPIO8 ← CRITICAL |
| P9     | SPI_MOSI/GPIO10 | NC/GND ← CRITICAL |
| P12    | SPI_MISO/GPIO9  | SPI_MISO/GPIO9 ✓ CORRECT |
| P15    | GPIO17      | GPIO24 (GPIO17 reserved for WittyPi!) |
| P19    | NC          | SCL/GPIO3 ← CRITICAL |

**Action:** Rewire J2 in schematic:
- Remove GND from P1; connect P1 → GPIO2/SDA1
- Change P5 from SDA → SPI_MOSI/GPIO10
- Change P7 from SPI_CLK → GND
- Change P8 from SCL → SPI_CS/GPIO8
- Change P9 from SPI_MOSI → NC
- Keep P12 → SPI_MISO (correct)
- Change P15 from GPIO17 → GPIO24 (VSYNC or Lepton GPIO)
- Change P19 from NC → SCL/GPIO3
- Keep P17 → GPIO6 (RESET_L)

> **Note:** Verify the P2 power connection against physical board. The schematic shows P2 as an internal VCC28 (2.8V) net which may be an output; the correct host connection is VIN (5V) input. Current design has +5V → P2 which appears correct based on the breakout's power circuit topology.

### 2. ~~GPIO17 Conflict — WittyPi SYS_UP vs Lepton~~ — FIXED

**Problem:** GPIO17 is claimed by WittyPi 4. It is the SYS_UP signal that the Pi writes HIGH when running (WittyPi reads this). The current schematic also routes GPIO17 to J2-P15 (a Lepton GPIO output pin). This creates a bus conflict: Pi driving GPIO17 HIGH (SYS_UP) while Lepton may be driving J2-P15 as output → **potential damage**.

**Action:** Change J2-P15 from GPIO17 to GPIO24 (free GPIO, Pi pin 18). GPIO17 must remain exclusively for WittyPi.

### 3. mDot UART Connection ~~RESOLVED~~

**Resolution:** The Raspberry Pi uses **UART5** for the mDot connection. UART5 uses GPIO12 (TXD5, Pi pin 32) and GPIO13 (RXD5, Pi pin 33) — the pins the schematic already connects to the mDot. The original schematic was correct for UART5; the document previously misidentified these as "PWM-only" pins.

GPIO12 and GPIO13 are alternate-function pins:
- GPIO12: ALT0 = PWM0, **ALT5 = TXD5** ← UART5 TX
- GPIO13: ALT0 = PWM1, **ALT5 = RXD5** ← UART5 RX

**mDot USART2 Pins:**
- PA_2 (mDot pad 2) = USART2_TX (mDot transmits) → GPIO13/RXD5 (Pi receives) ✓
- PA_3 (mDot pad 3) = USART2_RX (mDot receives) → GPIO12/TXD5 (Pi transmits) ✓

**Current schematic (correct):**
- mDot PA_2 → GPIO13/RXD5 ✓
- mDot PA_3 → GPIO12/TXD5 ✓
- J1 GPIO14 (pin 8): no_connect ✓
- J1 GPIO15 (pin 10): no_connect ✓

**Action:** No schematic change needed for UART routing. Ensure UART5 is enabled in `/boot/config.txt` (`dtoverlay=uart5`) and the kernel serial port is `/dev/ttyAMA5`.

> **Note:** GPIO14/GPIO15 (UART0) remain free. UART0 maps to the Bluetooth controller by default on Pi 4B; no conflict with mDot on UART5.

### 4. ~~mDot Has No Antenna Connection~~ — N/A

**Resolution:** The Multitech MTDOT-915 module includes a built-in u.FL connector on the module itself. No separate antenna footprint is needed on the HAT PCB. Connect an external antenna directly to the mDot's u.FL port. Maintain a 5mm copper keepout zone on the HAT PCB in the area directly above/below the mDot module to avoid detuning the antenna.

### 5. Missing IR CUT Camera GPIO Control Circuit

**Problem:** The modified IR CUT camera requires GPIO control for its filter. No connector or control circuit exists in the current design.

**How the IR CUT control mechanism works:**

The Dorhea IR CUT camera module contains an internal IR CUT controller IC that drives the filter motor.  The controller decides which filter position to use by reading a photoresistor (LDR) voltage divider:

- LDR high resistance (dark scene) → divider node voltage high → controller switches to night mode (removes IR cut filter)
- LDR low resistance (bright scene) → divider node voltage low → controller switches to day mode (inserts IR cut filter)

The modification for Pi control removes the LDR and connects the divider node to a Pi GPIO.

**Why direct GPIO connection is unreliable:**

The GPIO is a low-impedance voltage source.  When it drives HIGH into the LDR divider node, the fixed pull-down resistor in the divider loads the pin below the Pi's logic HIGH threshold (~1.6 V).  In testing, `GPIO.input()` read 0 in both HIGH and LOW states even though the motor did move — because the camera comparator threshold is lower than the Pi's logic threshold, and the voltage swing at the node (0 V to ~1 V) was enough for the camera but not enough for the Pi to read back.  This margin is unreliable across temperature, supply voltage variation, and camera module tolerances.

**Correct PCB circuit: NPN transistor open-collector switch**

Replace the direct wire with an NPN transistor (2N3904 or BSS138 SOT-23) to present the high/low impedance the camera comparator was designed for:

```
GPIO22 ──[R1: 1 kΩ]── Base
                       Collector ── LDR node (camera connector pin)
                       Emitter  ── GND

R2: 10 kΩ from Base to GND  (ensures transistor is off when GPIO floats at boot)
```

- GPIO22 LOW → transistor off → node floats up through camera's internal pull-up → controller sees "dark" → night mode (IR cut filter removed)
- GPIO22 HIGH → transistor saturates, ~10–50 Ω collector-emitter → node pulled to GND → controller sees "bright" → day mode (IR cut filter inserted)

The transistor presents the same impedance characteristic the comparator expects, regardless of GPIO drive strength.

**Action:** Add the following to the schematic and PCB:

1. Connector J4 — 3-pin JST-PH or 2.54mm THT:
   - Pin 1: LDR node signal (to camera photoresistor pin)
   - Pin 2: GND (to camera photoresistor GND reference)
   - Pin 3: Camera 5V power (if powering camera from board; otherwise NC)

2. Transistor Q2 — 2N3904 or BSS138 (SOT-23):
   - Collector → J4 pin 1 (LDR node)
   - Emitter → GND
   - Base → R1

3. R1 = 1 kΩ (0402) — GPIO22 to Q2 base
4. R2 = 10 kΩ (0402) — Q2 base to GND (pull-down, prevents floating gate at boot)

GPIO22 (Pi pin 15) is used — one GPIO only.  GPIO27 is not needed and remains free.

---

## High Priority — Functional But Broken

### 6. WittyPi P3 Header: VOUT and CATH Unconnected

**Problem:** The WittyPi P3 header (J3) VOUT and CATH pins are floating (no_connect). Per WittyPi 4 manual, **the Raspberry Pi is powered between VOUT and CATHODE**, not between VOUT and GND. The CATH pin has a 0.05Ω sampling resistor between it and GND (for current measurement). If this board needs to draw 5V power from WittyPi's regulated output (for the mDot bulk capacitors, for example), it must connect to VOUT and CATH, not VOUT and GND.

**Key facts:**
- VOUT = +5V switched output (same as Pi GPIO header pin 2)
- CATH = the "ground" for the Pi (not the WittyPi board GND)
- GND in P3 = WittyPi board ground (power supply ground, NOT Pi ground)
- 3V3 in P3 = WittyPi internal 3.3V (powers MCU/RTC, NOT same as Pi 3.3V)
- SW/SWITCH = connects to GPIO4 AND to the physical button
- ALM = RTC alarm signal (HIGH normally, goes LOW on alarm)
- LED = LED anode (add 1K series resistor)

**Current connections:**
- J3-2 (3V3) → mDot VDD ← WRONG: this is WittyPi internal 3V3, NOT suitable for mDot
- J3-5 (SW) → Q1 Drain (MOSFET) ← Correct concept, see notes on Q1
- J3-7 (GND) → GND ← Technically correct for WittyPi board GND

**Action:**
- mDot VDD (U3 pad 1) must remain on WittyPi P3-3V3.  The mDot must stay powered when the Pi is off so it can receive an inbound LoRa wake command and assert the WittyPi SW line via Q1 to restart the Pi.  The Pi's 3.3 V GPIO rail (pins 1/17) goes off when the Pi is powered down — connecting mDot VDD there would break the remote wake path entirely.
- The problem with P3-3V3 is current, not voltage: the mDot draws up to ~127 mA peak during LoRa TX, which exceeds what the WittyPi's MCU/RTC rail is rated to supply continuously.  Resolve this with decoupling capacitors at the mDot VDD pin: C1 = 100 µF electrolytic + C2 = 100 nF ceramic, placed within 5 mm of U3 pad 1.  TX current spikes will then be sourced from the local caps rather than drawn from the WittyPi rail.
- J3-VOUT (pin 1): Connect to a test point or the HAT's 5V power input rail
- J3-CATH (pin 6): Connect to board GND reference (monitoring point)
- J3-ALM (pin 4): Connect to a free Pi GPIO if alarm detection is needed (e.g., GPIO26)
- J3-LED (pin 3): Leave NC or connect to GPIO via 1K resistor for status LED

### 7. ~~HAT EEPROM Missing~~ — N/A

**Decision:** EEPROM not needed on this board. HAT EEPROM is optional per Pi spec; required only for automatic device-tree overlay loading by the Pi firmware. This board loads its overlays manually via `/boot/firmware/config.txt`. GPIO0/GPIO1 (ID_SDA/ID_SCL) remain unconnected. U4, R4, R5 should be removed from schematic.

### 8. No Decoupling Capacitors

**Problem:** No bypass/decoupling capacitors exist anywhere on the board. This is particularly critical for the mDot (LoRa TX generates large current spikes up to 600mA peak) and the Lepton breakout (150mA switching).

**Action:** Add at minimum:
- C1 = 100µF electrolytic (6.3V or 10V) near mDot VDD → GND
- C2 = 100nF ceramic (0402 or 0603) near mDot VDD → GND
- C3 = 100nF ceramic near AHT20 VDD → GND
- C4 = 10µF ceramic near AHT20 VDD → GND
- C5 = 100nF ceramic near BNO055/BNO085 VIN → GND
- C6 = 100nF ceramic near J2-P2 (Lepton VIN) → GND
- Place all caps as close to the device VDD/GND pins as possible

### 9. No I2C Pull-Up Resistors on Board

**Problem:** The I2C bus (GPIO2/SDA1, GPIO3/SCL1) has no pull-up resistors. While the Adafruit breakout boards include their own pull-ups, having multiple boards in parallel weakens the effective pull-up. For reliability (especially with longer traces to the Lepton and mDot), add board-level pull-ups.

**Action:** Add R6 = 4.7kΩ from SDA1 to 3.3V, R7 = 4.7kΩ from SCL1 to 3.3V.

---

## Medium Priority — Improvements

### 10. ~~BNO055 vs BNO085 Ambiguity~~ — FIXED

**Problem:** The schematic and PCB show the Adafruit BNO055 STEMMA QT breakout (U2), but the project description mentions BNO085. These are different physically (different Adafruit board ID, different I2C register sets).

**Resolution:** BNO055 Adafruit STEMMA QT breakout (U2) is confirmed. INT connected to GPIO20 (pin 38); RST connected to GPIO16 (pin 36). I2C address 0x28 (ADDR=GND default on breakout). GPIO21 is reserved for IR-CUT filter and was not used for RST.

### 11. MOSFET Q1 Choice Is Inappropriate

**Problem:** Q1 is an IRLB8721PBF, a 30V/62A power MOSFET in TO-252 package. This is a massive power device for a signal-level switch (the WittyPi SW line is a logic signal, not a power switch). The footprint is large (TO-252) and wastes PCB space.

**Correct use case:** Q1 gate is driven by mDot PB_1 to pull the WittyPi SW line LOW (simulating a button press to start/stop the Pi). This is a small-signal application.

**Action:** Replace Q1 with a small-signal N-MOSFET such as 2N7002 (SOT-23) or BSS138 (SOT-23). The gate drive from mDot PB_1 (3.3V logic) is sufficient for these devices. Add R8 = 100Ω gate resistor in series (currently missing) to prevent gate ringing. Keep R3 (10kΩ pull-down) as-is.

### 12. WittyPi 40-Pin Stacking Header Required

**Problem:** The board occupies the Pi's 40-pin GPIO header. The WittyPi 4 also needs the Pi's 40-pin header (it stacks on top). For a Pi → WittyPi → This HAT stack to work, this PCB needs both:
- A female 2×20 header (socket) on the BOTTOM to mate with WittyPi's male header
- A male 2×20 header (pins) on the TOP if any further stacking is needed, OR all connections terminate here

The current design uses a single 2×20 header (J1) with `MODULE_RASPBERRY_PI_4B_4GB` footprint on B.Cu. This is designed as a direct-to-Pi connection, not a WittyPi stacking connection.

**Action:**
- J1 should be a tall stacking female socket (e.g., 2×20, 11mm or 13mm height) to mate over the WittyPi's protruding pins
- Verify standoff heights: WittyPi sits on Pi at ~19mm height; this HAT needs ~5mm clearance above WittyPi components
- Consider using 2×20 stackable header (GPIO female-bottom, pins-top) if further stacking needed

### 13. Footprint Error — Duplicate Pad "24" on mDot

**Problem:** The mDot MTDOT footprint has two pads both numbered "24" at different positions with different nets. This is a footprint error that may cause manufacturing issues.

**Action:** Correct the MTDOT footprint — verify against the mDot physical dimensions. The mDot has 20 castellated pads (10 each side) plus bottom RF pad and GND pad. Pads should be numbered 1–20 plus RF/GND pads with unique numbers.

### 14. MOSFET Q1 Gate Resistor Missing

**Action:** Add R8 = 100Ω in series between mDot PB_1 and Q1 gate. This limits ringing on gate drive from the LoRa module output. The current design connects mDot PB_1 directly to Q1 gate with only the 10kΩ pull-down.

---

## Low Priority — Nice to Have

### 15. mDot Power Supply Decoupling

The mDot requires 100µF bulk + 100nF bypass at VDD for reliable LoRa operation. The mDot VDD connects to J3-3V3 (WittyPi internal 3V3), which is the correct always-on power domain (see item 6). Add the decoupling capacitors within 5mm of the mDot VDD pin so that LoRa TX current spikes are sourced locally rather than drawn from the WittyPi MCU/RTC rail.

### 16. mDot nReset Connection

The mDot has an active-low nReset pin (pin 5). Currently it is no_connect. For reliable firmware operation, connect nReset to a free GPIO (e.g., GPIO26) via a 10kΩ pull-up to 3.3V and a 100nF cap to GND. Or tie nReset HIGH via 10kΩ to 3.3V if software reset control is not needed.

### 17. ~~Lepton PWREN Control~~ — FIXED

P18 (PW_DWN_L) is tied directly to +3.3V in the schematic (Fix 5). The Lepton is always powered. No software power-down is used in the current design. If software power control is needed in future, replace the direct 3.3V tie with a GPIO via a 10kΩ pull-up.

### 18. Board-Level 3.3V Rail

Currently the board has no explicit 3.3V rail from the Pi. All sensors operating at 3.3V rely on their own breakout board regulators accepting 5V input. Consider adding a small 3.3V LDO (e.g., MCP1700-3302E) powered from the Pi's 5V rail to provide a clean local 3.3V for the mDot and pull-up resistors.

---

## I2C Address Map (No Conflicts)

### I2C1 bus (GPIO2/GPIO3) — shared

| Device | Address | Notes |
|--------|---------|-------|
| FLIR Lepton CCI | 0x2A | Fixed |
| AHT20 | 0x38 | Fixed |
| BNO055 (U2) | 0x28 | ADDR=GND (breakout default); solder jumper → 0x29 |
| WittyPi LM75B | 0x48 | On WittyPi board |
| WittyPi PCF85063A RTC | 0x51 | On WittyPi board |

### I2C0 bus (GPIO0/GPIO1)

Not used. GPIO0/GPIO1 are unconnected (no EEPROM fitted).

No address conflicts in default configuration.

---

## GPIO Allocation (Current — v7 schematic)

See `PIN_MAP.md` for the authoritative and complete pin table. Summary of assigned pins:

| GPIO | Pi Pin | Assigned To | Notes |
|------|--------|-------------|-------|
| GPIO0 / ID_SDA | 27 | NC | No EEPROM fitted |
| GPIO1 / ID_SCL | 28 | NC | No EEPROM fitted |
| GPIO2 / SDA1 | 3 | I2C1 SDA (shared bus) | Lepton CCI P1, BNO055, AHT20 |
| GPIO3 / SCL1 | 5 | I2C1 SCL (shared bus) | Lepton CCI P19, BNO055, AHT20 |
| GPIO4 | 7 | ⛔ WittyPi MCU | Reserved — do not use |
| GPIO5 | 29 | mDot PA_6 + manual button | Pi drives HIGH when running |
| GPIO6 | 31 | Lepton RESET_L (J2-P17) | Active-low; pulse LOW to reset |
| GPIO8 / CE0 | 24 | Lepton SPI CS (J2-P8) | SPI0.CE0 |
| GPIO9 / MISO | 21 | Lepton SPI MISO (J2-P12) | SPI0.MISO |
| GPIO10 / MOSI | 19 | Lepton SPI MOSI (J2-P5) | SPI0.MOSI |
| GPIO11 / SCLK | 23 | Lepton SPI CLK (J2-P3) | SPI0.SCLK |
| GPIO12 / TXD5 | 32 | mDot PA_3 (mDot RX) | UART5 TX; dtoverlay=uart5 |
| GPIO13 / RXD5 | 33 | mDot PA_2 (mDot TX) | UART5 RX |
| GPIO16 | 36 | BNO055 RST | Active-low; hold HIGH at boot |
| GPIO17 | 11 | ⛔ WittyPi SYS_UP | Reserved — never drive LOW |
| GPIO20 | 38 | BNO055 INT | Active-low output; configure pull-up |
| GPIO21 | 40 | IR-CUT filter (external) | External circuit; not on HAT PCB |
| GPIO24 | 18 | Lepton VSYNC (J2-P15) | Lepton GPIO2 output |
| Free | 12,13,15,16,22,25,26,29,35,37 | — | Available for future use |

---

## PCB Layout Notes

- **mDot antenna keepout:** 5mm zone around u.FL connector, no copper pour
- **AHT20 placement:** Keep away from mDot (RF heat), Q1, and Lepton
- **BNO055/085:** Mount on flat plane; no vibration-inducing mounting near sensor
- **Decoupling caps:** Place within 5mm of each device's VDD pin
- **I2C trace length:** Keep SDA/SCL traces short (< 100mm) and matched
- **Lepton J2 connector:** Ensure the 2×10 header footprint matches the Breakout v2 physical connector orientation (verify pin 1 marker before sending to fab)
- **Stack height:** Confirm M2.5 standoff heights accommodate WittyPi (19mm) + clearance
