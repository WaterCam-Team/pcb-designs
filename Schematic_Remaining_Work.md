# WaterCam HAT — Schematic Remaining Work

**Board:** WaterCam_mDot_WittyPi_AHT_BNO_Lepton  
**Schematic:** `WaterCam_mDot_WittyPi_AHT_BNO_Lepton.kicad_sch` (KiCad 9)  
**Prepared:** 2026-05-10  
**Scope:** Schematic-only fixes. PCB layout work tracked separately.

---

## Status Summary

| # | Issue | Schematic Fix | Status |
|---|-------|--------------|--------|
| 7 | EEPROM artifacts (labels + wires) | Remove ID_SDA/ID_SCL labels and wires | ✅ Done |
| 9 | No I2C pull-up resistors | Add R6, R7 (4.7 kΩ each) | ✅ Done |
| 11 | Q1 MOSFET oversized (IRLB8721 TO-252) | Swap to 2N7002 SOT-23 | ✅ Done |
| 14 | Q1 gate resistor missing | Add R8 (100 Ω) in gate net | ✅ Done |
| 16 | mDot NRESET unconnected | Add 10 kΩ pull-up to 3.3 V | ✅ Done |
| 17 | J2-P18 PW_DWN_L not tied | Verify +3V3 tie; add if missing | ✅ Done |
| 8/15 | Decoupling caps missing | Add C1–C6 (100µF/100nF/10µF) | ✅ Done |
| ERC | +3V3 net power flag | Add #FLG04 (PWR_FLAG) on +3V3 | ✅ Done |

Issues #1–6, #10, #12, #13 are either fixed, N/A, or PCB-layout-only.

**Schematic complete. All issues resolved. Ready for ERC + PCB update.**

---

## Issue #7 — Remove EEPROM Artifacts

**Background:** U4 (CAT24C256 EEPROM) was added in an earlier session then deemed unnecessary (overlays loaded via config.txt). U4 was removed from the schematic but the schematic still has dangling ID_SDA/ID_SCL net labels and their connecting wires at J1 GPIO0 (Pi pin 27) and GPIO1 (Pi pin 28). These conflict with the no_connect marks already placed at the same points, causing ERC errors.

**Elements to remove:**
| Element | Location | Action |
|---------|----------|--------|
| Label `ID_SDA` | (31.75, 60.96, 0°) | Delete |
| Label `ID_SCL` | (100.33, 60.96, 180°) | Delete |
| Wire J1-GPIO0 → label | (60.96, 60.96) → (31.75, 60.96) | Delete |
| Wire J1-GPIO1 → label | (73.66, 60.96) → (100.33, 60.96) | Delete |
| `no_connect` at label end | (31.75, 60.96) UUID `41ad66df-...` | Delete |
| `no_connect` at label end | (100.33, 60.96) UUID `bb504bb4-...` | Delete |

**Elements to add:**
| Element | Location | Reason |
|---------|----------|--------|
| `no_connect` | (60.96, 60.96) | Mark J1 pin 27 (GPIO0/ID_SDA) as intentionally NC |
| `no_connect` | (73.66, 60.96) | Mark J1 pin 28 (GPIO1/ID_SCL) as intentionally NC |

**Verification:** After edit, ERC should show no error for J1 pins 27/28. Both should appear as clean no-connects in the netlist.

---

## Issue #9 — I2C Pull-Up Resistors (R6, R7)

**Background:** The I2C1 bus (GPIO2/SDA1, GPIO3/SCL1) has no board-level pull-ups. The Adafruit AHT20 and BNO055 breakout boards include their own 10 kΩ pull-ups, but having multiple boards in parallel on a shared bus weakens the effective pull-up strength. The Lepton CCI interface (I2C at 0x2A) requires pull-ups to be present. Adding 4.7 kΩ on the HAT provides a stable bus regardless of which breakouts are populated.

**Design:**
- R6: 4.7 kΩ, 0402, from GPIO2/SDA1 to +3.3 V
- R7: 4.7 kΩ, 0402, from GPIO3/SCL1 to +3.3 V

**Schematic approach:** Place R6 and R7 as vertical stubs branching off the SDA1 and SCL1 wires near J1. Each resistor connects between the signal net (via net label or T-junction on the existing wire) and a `power:+3V3` power symbol.

**Placement strategy:**
- Locate the SDA1 wire (y ≈ 30.48) and SCL1 wire (y ≈ 33.02) to the left of J1
- Add a junction on each wire at a free x-coordinate (e.g., x ≈ 20.32)
- Run a short vertical wire stub upward from each junction
- Place R6 / R7 vertically (90°) above the junction
- Connect top pin of each resistor to a `power:+3V3` symbol

**Net labels:** SDA1 net = `GPIO2{slash}SDA1`, SCL1 net = `GPIO3{slash}SCL1`

**New component definitions:**
```
R6: lib_id = Device:R_Small, value = "4.7kΩ", footprint = Resistor_SMD:R_0402_1005Metric
R7: lib_id = Device:R_Small, value = "4.7kΩ", footprint = Resistor_SMD:R_0402_1005Metric
```

**Note on +3.3 V source:** The Pi's 3.3 V rail appears at J1 pins 1 and 17 but is currently no-connect in the schematic (the HAT draws 3.3 V from the Pi only via breakout boards' own regulators). To add I2C pull-ups, add `power:+3V3` symbols connected directly to the J1 pin 1 (60.96, 27.94) and route pin 1 to a +3V3 power net. This also resolves the inconsistency where J1 pin 1 is no_connect while the schematic claims 3.3 V powers the breakouts.

**Alternative (simpler):** If the +3V3 net conflict is undesirable, use the `power:+5V` net and add a dedicated 3.3 V LDO (Issue #18) — but this is out of scope for schematic-only work. Use `power:+3V3` for now; verify J1 pin 1 drives it.

---

## Issue #11 — Q1 MOSFET Replacement (IRLB8721 → 2N7002)

**Background:** Q1 is an IRLB8721PBF (30 V / 62 A, TO-252 package) used as a small-signal switch to pull the WittyPi SW line LOW when the mDot asserts PB_1. This is severe overkill. The correct device is a 2N7002 (60 V / 300 mA, SOT-23) or BSS138.

**Gate drive:** mDot PB_1 = 3.3 V logic. Both 2N7002 (Vgs(th) ≈ 1.0–2.5 V) and BSS138 (Vgs(th) ≈ 0.8–1.5 V) fully saturate with 3.3 V gate drive.

**Schematic changes (properties only — no rewiring):**
| Property | Current | New |
|----------|---------|-----|
| `lib_id` | `Simulation_SPICE:NMOS` | `Transistor_FET:2N7002` |
| `Value` | `NMOS` | `2N7002` |
| `Footprint` | `IRLB8721PBF Model:TO254P1067X483X2057-3` | `Package_TO_SOT_SMD:SOT-23` |
| `Datasheet` | ngspice URL | `https://www.vishay.com/docs/70226/70226.pdf` |

**Pin mapping for 2N7002 in SOT-23:**
- Pin 1 = Gate (G)
- Pin 2 = Source (S)  
- Pin 3 = Drain (D)

**Note:** The `Transistor_FET:2N7002` KiCad symbol uses pin names G/D/S. Verify the lib_symbol pin orientation matches the existing wiring before saving. If the pin mapping differs from the current NMOS simulation symbol, the drain/source/gate connections must be reconciled.

**Alternative:** Keep the `Simulation_SPICE:NMOS` schematic symbol (generic N-MOSFET) and only update the footprint and value. This avoids a pin-mapping conflict. A BOM note can specify 2N7002/BSS138.

---

## Issue #14 — Q1 Gate Resistor (R8, 100 Ω)

**Background:** mDot PB_1 drives Q1 gate directly with only a 10 kΩ pull-down (R3). No series gate resistor exists. At 3.3 V / 10 kΩ, gate current is 330 µA, which is fine for steady state. The concern is ringing at turn-on/off: the LoRa module's GPIO transitions can excite the gate-source capacitance (Ciss ≈ 50–100 pF for 2N7002) causing ringing on the gate that may cause spurious switching.

**Fix:** Add R8 = 100 Ω in series between the mDot PB_1 signal and Q1 gate. The R3 10 kΩ pull-down remains connected at the Q1 gate side (after R8), which is correct — it provides DC bias when mDot is unpowered.

**Circuit topology:**
```
mDot PB_1 ── R8 (100Ω) ─┬─ Q1 Gate
                          │
                         R3 (10kΩ)
                          │
                         GND
```

**Schematic changes:**
1. Identify the gate wire segment (the wire running at y ≈ 172.72 from Q1 gate toward the mDot PB_1 side)
2. Break this wire at a point approximately 10–15 mm from Q1 gate (to leave room for R8 symbol)
3. Add R8 (`Device:R_Small`, value `100Ω`, footprint `Resistor_SMD:R_0402_1005Metric`) in the gap, oriented horizontally (0°)
4. Connect R8 pin 1 to the mDot-PB_1-side wire stub
5. Connect R8 pin 2 to the Q1 gate-side wire stub

**R3 stays:** The existing R3 (10 kΩ at position ~177.8, 161.29, vertical) is the gate pull-down. Its connection to the Q1 gate net is correct and unchanged.

---

## Issue #16 — mDot NRESET Pull-Up

**Background:** mDot NRESET (active-low, pin 5 of U3) is currently no_connect at (243.84, 81.28). Leaving NRESET floating can cause spurious resets if the line picks up noise. The mDot datasheet recommends tying NRESET HIGH via a 10 kΩ resistor to VDD (3.3 V) with an optional 100 nF capacitor to GND.

**Fix:** Add R9 = 10 kΩ pull-up from NRESET to 3.3 V (WittyPi always-on 3.3 V, same supply as mDot VDD).

**Schematic changes:**
1. Remove `no_connect` at (243.84, 81.28)
2. Add a short wire stub from (243.84, 81.28) going LEFT (decreasing x) to approximately (234.95, 81.28)
3. Place R9 (`Device:R_Small`, value `10kΩ`, footprint `Resistor_SMD:R_0402_1005Metric`) horizontally (0°) with pin 1 at (234.95, 81.28)
4. Add a wire from R9 pin 2 (left side) going left to approximately (228.6, 81.28)
5. Add a `power:+3V3` symbol at the end OR use the WittyPi J3-3V3 label to connect to the always-on 3.3 V supply

**Power domain note:** mDot VDD is already on WittyPi J3-3V3 (always-on). NRESET must also be on this rail — if tied to Pi 3.3 V (which goes off when WittyPi shuts the Pi), NRESET would assert LOW during Pi shutdown and hold the mDot in reset. Use WittyPi J3-3V3 for this pull-up.

**Schematic label:** The J3-3V3 wire chain already exists. Connect R9 top to the same net using a `power:+3V3` symbol OR a local wire to J3 pin 2 (at (231.14, 35.56)).

---

## Issue #17 — J2-P18 PW_DWN_L Verification

**Background:** Fix 5 was supposed to tie J2-P18 (Lepton PW_DWN_L) to +3.3 V so the Lepton is always powered. Verify this fix is actually present in the current schematic.

**Check:**
- J2-P18 position: even pin at (121.92, 128.27)
- Expected: wire from (121.92, 128.27) to a `power:+3V3` symbol (or at minimum, a wire to the +3V3 rail)
- Current state: `no_connect` found at (121.92, 128.27) — **Fix 5 may not be applied**

**Action:** If no_connect is the only thing at (121.92, 128.27):
1. Remove the `no_connect` at (121.92, 128.27)
2. Add a short wire from (121.92, 128.27) going LEFT to ~(113.03, 128.27)
3. Add `power:+3V3` symbol at (113.03, 128.27)
4. Add a 10 kΩ pull-up resistor between this +3V3 and the signal for cleaner design (optional; direct tie is acceptable per Issue #17 note in the main change doc)

---

## PCB Layout Work (Out of Scope for This Document)

These require the PCB editor (not the schematic):

| # | Action |
|---|--------|
| 8/15 | Add decoupling caps C1–C6 (see WaterCam_PCB_Design_Changes_Required.md §8) |
| 12 | Verify stacking header J1 height (11–13 mm female socket) |
| 13 | Fix MTDOT footprint duplicate pad "24" |

All PCB changes should be deferred until schematic issues #7, #9, #11, #14, #16, #17 are resolved and the schematic passes ERC.

---

## KiCad Coordinate Reference

Key known positions in schematic space:

| Component | Position | Notes |
|-----------|----------|-------|
| J1 (Pi header) | (66.04, 50.8, 0°) | `Conn_02x20_Odd_Even`; left col x=60.96, right col x=73.66 |
| J2 (Lepton) | (129.54, 118.11, 0°, mirror y) | Even pins x=121.92, Odd pins x=134.62; y=107.95–130.81 |
| J3 (WittyPi P3) | (195.58, 57.15, 0°) | Pin 2 (3V3) at (231.14, 35.56) |
| U3 (mDot) | (274.32, 83.82, 90°, mirror x) | x_abs = 274.32 − ly_local; y_abs = 83.82 + lx_local |
| U2 (BNO055) | (153.67, 29.21, 180°) | x_abs = 153.67 − lx_local; y_abs = 29.21 + ly_local |
| Q1 (NMOS) | (82.55, 172.72, 0°) | Gate net wire runs at y=172.72 |
| R3 (10kΩ pull-down) | (177.8, 161.29, 90°) | Gate pull-down; keep in place |
| J1-GPIO0 pin | (60.96, 60.96) | Currently has wire+label "ID_SDA" (to be removed) |
| J1-GPIO1 pin | (73.66, 60.96) | Currently has wire+label "ID_SCL" (to be removed) |
| J1-GPIO2/SDA1 | (60.96, 30.48) | Wire goes left to label at (31.75, 30.48) |
| J1-GPIO3/SCL1 | (60.96, 33.02) | Wire goes left to label at (31.75, 33.02) |
| mDot NRESET | (243.84, 81.28) | Currently no_connect; add 10kΩ pull-up |
| J2-P18 PW_DWN_L | (121.92, 128.27) | Currently no_connect; should tie +3V3 |
