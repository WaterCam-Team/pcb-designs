# WaterCam HAT — PCB Layout Remaining Work

**Schematic:** WaterCam_mDot_WittyPi_AHT_BNO_Lepton.kicad_sch — all schematic issues resolved  
**PCB file:** WaterCam_mDot_WittyPi_AHT_BNO_Lepton.kicad_pcb  
**Prepared:** 2026-05-10  

---

## Prerequisites Before Opening PCB Editor

1. **Run ERC** on the schematic (KiCad Schematic Editor → Inspect → Electrical Rules Checker).  
   Expected warnings:
   - `+3V3` net "Power pin not driven" — add PWR_FLAG (#FLG04) at any +3V3 node (e.g., (60.96, 27.94) alongside the +3V3 at J1 pin 1) to silence it.
   - Any remaining unconnected pin warnings from the no_connects should pass cleanly.

2. **Update PCB from Schematic** (KiCad PCB Editor → Tools → Update PCB from Schematic, or Schematic Editor → Tools → Update PCB from Schematic).  
   This syncs all schematic changes into the PCB netlist:
   - R6, R7 (new I2C pull-ups) will appear as unplaced footprints
   - R8, R9 (gate resistor + nReset pull-up) will appear if not already placed
   - Q1 footprint change (IRLB8721 TO-252 → 2N7002 SOT-23) will need re-placement
   - +3V3 power net will be defined

---

## Issue #8 / #15 — Decoupling Capacitors C1–C6

**Why:** The mDot generates LoRa TX current spikes up to 600 mA peak on a 3.3V always-on rail that also powers WittyPi's MCU/RTC. Without local bulk capacitance, these spikes propagate back onto the WittyPi P3-3V3 rail and may cause the RTC to reset or glitch. The Lepton and I2C sensors also benefit from local bypass caps.

**Schematic step first:** Add C1–C6 to the schematic before updating the PCB.

| Ref | Value | Type | Location in schematic | Purpose |
|-----|-------|------|-----------------------|---------|
| C1 | 100 µF, 6.3V | Electrolytic (radial or SMD) | mDot VDD (179.07, 83.82) | mDot bulk — absorbs LoRa TX spikes |
| C2 | 100 nF, 10V | Ceramic 0402 | mDot VDD (179.07, 83.82) | mDot bypass |
| C3 | 100 nF, 10V | Ceramic 0402 | AHT20 VDD (U1 pin VDD) | AHT20 bypass |
| C4 | 10 µF, 10V | Ceramic 0402 or 0603 | AHT20 VDD | AHT20 bulk |
| C5 | 100 nF, 10V | Ceramic 0402 | BNO055 VIN (U2 pin VDD) | BNO055 bypass |
| C6 | 100 nF, 10V | Ceramic 0402 | J2-P2 (Lepton VIN) | Lepton bypass |

**Schematic additions for each cap:**
- `lib_id`: `Device:C_Small` (0402 ceramic) or `Device:C` (electrolytic C1)
- Value and footprint per table above
- One pin to the relevant VDD net (via junction on existing wire or net label)
- Other pin to `power:GND`

**PCB placement rules:**
- C1 (100 µF bulk): within 8 mm of mDot U3 VDD pad (castellated pad on mDot left edge)
- C2 (100 nF bypass): within 3 mm of mDot U3 VDD pad, closer than C1
- C3, C4: within 5 mm of U1 (AHT20) VDD pin
- C5: within 5 mm of U2 (BNO055) VIN pin
- C6: within 5 mm of J2 (Lepton) P2 pin (5V power pin)
- Orient all caps so GND pad faces the nearest GND pour or via

---

## Issue #12 — Stacking Header J1 Height

**Why:** The WittyPi 4 stacks on the Pi 4B and its tallest components sit ~12 mm above the WittyPi PCB surface. The HAT PCB must sit above these components, so J1 must be a tall female stacking socket.

**Recommended part:** 2×20 female tall stacking header, 13.5 mm body height (e.g., Adafruit 1979 or equivalent). This gives ~2 mm clearance over WittyPi components and mates over the WittyPi's protruding male header pins.

**Schematic/BOM action only — no PCB layout change:**
- J1 footprint in PCB file should remain as `Connector_PinHeader_2.54mm:PinHeader_2x20_P2.54mm_Vertical` (through-hole, 2×20)
- Add a BOM note: J1 = tall stacking female socket, 2×20, 13.5 mm or 11 mm height
- Verify physical clearance by measuring WittyPi component heights before ordering

**Check:** Does the PCB have adequate standoff hole placement (M2.5 mounting holes at Pi corner positions)? Verify all four mounting holes are present and unobstructed.

---

## Issue #13 — MTDOT Footprint Duplicate Pad "24"

**Why:** The mDot MTDOT-915 footprint has two pads both numbered "24." KiCad assigns both pads to the same net, which means one pad may be unrouted or mis-netted. Manufacturing may flag this as a DRC error.

**Investigation steps:**
1. Open `WaterCam_mDot_WittyPi_AHT_BNO_Lepton.kicad_pcb` in KiCad PCB editor
2. Select U3 (mDot footprint) → Edit Footprint → inspect pad numbers
3. The mDot MTDOT-915 physical package: 20 castellated edge pads (10 per side, numbered 1–20) + bottom RF ground pad

**MTDOT-915 correct pad numbering** (from mDot datasheet, pads numbered left-right, top row first):
- Top edge (pads 1–10 odd, or sequential — verify from datasheet)
- Bottom edge (pads 11–20)
- RF pad: "RF" or pad 21
- GND pad (bottom center): pad 22 or "GND"

**Action:**
- Identify which two pads share number "24" in the footprint
- Determine which pad is correctly "24" from the datasheet pad map
- Renumber the other pad to its correct number
- Update the net assignment in the PCB if the corrected pad was on the wrong net
- Run DRC after fix to confirm no pad errors remain

**Note:** This is a PCB-file-only fix. The schematic U3 symbol uses pin numbers mapped by the mDot lib_symbol; changing footprint pad numbers does not change schematic pin assignments as long as the pin→pad mapping is consistent.

---

## Order of Operations

1. Add ERC PWR_FLAG for +3V3 net in schematic (optional — silences ERC warning)
2. Add C1–C6 to schematic (Device:C_Small / Device:C, connected to correct nets)
3. Run ERC — should pass cleanly
4. Open PCB editor → Tools → Update PCB from Schematic
5. Resolve any footprint changes (Q1 SOT-23, R6, R7, R8, R9, C1–C6 appear as new)
6. Place new components:
   - Q1 (SOT-23) near R3 / J3 SW signal area
   - R6, R7 near J1 (I2C lines) — small footprints, place on free copper area
   - R8 (0402) inline on gate trace between R3 and mDot PB_1 pad
   - R9 (0402) between mDot NRESET pad and 3V3 supply
   - C1–C6 per placement rules above
7. Fix duplicate pad #24 on U3 (mDot footprint)
8. Verify J1 header footprint is through-hole 2×20 — no PCB change, BOM note only
9. Run DRC — fix any clearance or unrouted net errors
10. Generate Gerbers

---

## Component Reference Summary (Post-Schematic)

| Ref | Part | Footprint | Value | Status |
|-----|------|-----------|-------|--------|
| R3 | Pull-down | Resistor_THT:R_Axial... | 10 kΩ | Existing — keep |
| R6 | SDA1 pull-up | Resistor_SMD:R_0402_1005Metric | 4.7 kΩ | New — needs placement |
| R7 | SCL1 pull-up | Resistor_SMD:R_0402_1005Metric | 4.7 kΩ | New — needs placement |
| R8 | Q1 gate resistor | Resistor_SMD:R_0402_1005Metric | 100 Ω | New — needs placement |
| R9 | mDot NRESET pull-up | Resistor_SMD:R_0402_1005Metric | 10 kΩ | New — needs placement |
| Q1 | Remote-wake MOSFET | Package_TO_SOT_SMD:SOT-23 | 2N7002 | Changed footprint — re-place |
| C1 | mDot bulk cap | (TBD — electrolytic or large SMD) | 100 µF | New |
| C2 | mDot bypass | Capacitor_SMD:C_0402_1005Metric | 100 nF | New |
| C3 | AHT20 bypass | Capacitor_SMD:C_0402_1005Metric | 100 nF | New |
| C4 | AHT20 bulk | Capacitor_SMD:C_0402_1005Metric or 0603 | 10 µF | New |
| C5 | BNO055 bypass | Capacitor_SMD:C_0402_1005Metric | 100 nF | New |
| C6 | Lepton bypass | Capacitor_SMD:C_0402_1005Metric | 100 nF | New |
