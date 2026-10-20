# WaterCam v6 — Session Handoff

**Work performed:** 2026-09-09 · **Handoff written:** 2026-09-16
**Target fab:** OSHPark, 2-layer, 1.6 mm, ENIG
**Goal:** get the board to a DRC-clean state and ship sample gerbers.

---

## 1. Where things stand

| Check | State |
|---|---|
| Schematic ↔ PCB netlist parity | **identical**, all 33 nets |
| ERC | 58 items, **0 errors** (all warnings) |
| DRC | 17 violations, 26 unconnected |
| Shorts / solder-mask bridges | **0** (were 8 / 8) |
| Footprints on board | 22 (all 11 missing parts added) |

**Not orderable yet** — routing is unfinished (26 unconnected).

### Remaining DRC, itemised

| Type | Count | Action |
|---|---|---|
| `copper_edge_clearance` | 3 | `/WP_SW` tracks sit 0.27 mm from the bottom edge; OSHPark rule is 0.381 mm. Reroute inward. |
| `track_dangling` | 1 | `/WP_SW` stub orphaned when Q1 became SOT-23. Reroute. |
| `silk_over_copper` | 5 | Cosmetic. OSHPark tolerates it; clean up if you care. |
| `silk_overlap` | 2 | Cosmetic (includes `WaterCam_v6.0_OFM` text over R9). |
| `lib_footprint_issues` | 3 | Missing footprint libs in config. Not fab-blocking (footprints are embedded). |
| `lib_footprint_mismatch` | 3 | Embedded copies differ from libraries. Not fab-blocking. |

ERC's 58 warnings are dominated by **33 `lib_symbol_mismatch`** — pre-existing library
drift affecting *every* embedded symbol including `GND`, `+5V`, `C_Small`. One
`Tools → Update Symbols from Library` in eeschema clears most of it. Not blocking.

---

## 2. Next actions (resume here)

### Step 4 — Route (in pcbnew)

26 connections outstanding. Unrouted nets by pad count:
`GND` 14 · `+5V` 8 · `/WP_3V3` 6 · `/GPIO3/SCL1` 6 · `/GPIO2/SDA1` 6 ·
`Net-(U3-PB_1)` 4 · `Net-(Q1-G)` 4 · `+3V3` 4 · `Net-(U3-NRESET)` 2 · `/GPIO16` 2 · `/WP_SW` 2

Specific attention:

1. **Q1 gate chain** — stale copper was deleted, so this is bare:
   `Q1 pad 1 (G) → R8 pad 1`, and `R8 pad 2 → R3 pad 2 → U3 pad 19 (PB_1)`.
2. **`+3V3` has no copper at all** — must reach `J1.1`, `R6.1`, `R7.1`, `C3.1`, `C4.1`,
   `C5.1`, `U1.1`, `U2.6`. A small filled zone or tracks both work.
3. **Reroute `/WP_SW`** (Q1 pad 3 → J3 pin 5) away from the bottom board edge.
4. The `+5V` / `GND` zones **do not currently extend** over where the new parts sit, so
   they will not pick up zone connections there as-is.
5. `Edit → Fill All Zones` when done.

### Step 5 — Verify

`Inspect → Design Rules Checker`. Target: **0 unconnected**, and only the 6 library
warnings plus any silkscreen items remaining.

Also re-run **F8** once (idempotent). Some pad nets were set programmatically rather than
by F8 — see §4 — and F8 will confirm KiCad agrees.

### Step 6 — Fab package

Hand back and the outputs get generated: gerbers, Excellon drill, position file, BOM.
OSHPark accepts `.kicad_pcb` directly, so both will be produced.

---

## 3. Assembly decisions still open

1. **Leave JP2 unpopulated on the BNO055.** The footprint has no holes for the part's
   4-pin row. Adafruit ships headers loose so this costs nothing, but if that header is
   soldered on the part will not seat flush. Consequence: INT permanently unavailable
   (already no-connected in the schematic; GPIO20 is free).
2. **Consider R6/R7 unpopulated.** With everything on 3.3 V the bus is
   Pi 1.8 k ∥ R6/R7 4.7 k ∥ AHT20 10 k ∥ BNO055 10 k ≈ 1.03 kΩ → ~2.8 mA sink, right at
   the I2C 3 mA limit. The Pi's internal pull-ups plus the two breakouts' are sufficient.
3. **R3 is still a vertical through-hole 0207** while R6–R9 are 0402 — height risk under
   the HAT stack and inconsistent. Offered switch to `R_0402_1005Metric`, not yet done.
4. **HAT EEPROM** — J1 pins 27/28 (ID_SD/ID_SC) are unconnected; no U4 in the schematic.
   Board works but will not auto-identify. Deferred.

## Unverified risk — check before ordering

**The U2 BNO055 footprint has no silkscreen, no outline and no orientation marking.**
Symbol and footprint appear self-consistent, but nothing confirms which physical end is
VIN. Reversed, it would put 3.3 V on RST and the reset signal on VIN. **Verify pad 1
against the physical breakout.**

Also: the `MDOT:MTDOT` footprint has a **duplicate pad 24 and no pad 28**. Both PC_1 and
PA_7 are unconnected in the schematic so there is no electrical impact today, but one
physical mDot pad is mis-numbered.

---

## 4. What changed in this session

### Schematic fixes (four were boot-blockers)

| Fix | Detail |
|---|---|
| GPIO17 / WittyPi SYS_UP | J2-P15 (Lepton GPIO3/VSYNC) was on GPIO17, which WittyPi owns. VSYNC is unused by SU-WaterCam, so P15 was **disconnected entirely**. GPIO17 now fully NC on the HAT. |
| J2-P18 MASTER_CLK | Was tied to `/WP_3V3`, shorting the breakout's 25 MHz oscillator output to a rail. Now NC. |
| WittyPi SW shorted to GND | `J3.5(SW)`, `Q1.1(D)` and `Q1.3(S)` had all been merged into `GND` — FET shorted across itself *and* WittyPi's button held permanently low. Now net `/WP_SW`. |
| Q1 mis-pinned | Used `Simulation_SPICE:NMOS` (D=1,G=2,S=3); every SOT-23 MOSFET is G=1,S=2,D=3. Drain was landing on the gate pad. Swapped to `Transistor_FET:BSS138`. |
| BNO055 I2C crossed | Pi SDA went to U2's SCL pin and vice-versa. Uncrossed. |
| Sensor rails | `U1.1`/`U2.6` VIN moved `+5V` → `+3V3`; C3/C4/C5 moved back to `+3V3`. See §5. |
| U2 INT | No-connected (footprint has no pad); GPIO20 freed. |

### PCB changes

- 11 GPIO17 track segments and 2 pad net assignments removed.
- Via on `/GPIO6` resized 0.9/0.6 → 0.9/0.5 (annular ring was 0.15 mm, under OSHPark's
  0.178 mm). Both netclass via definitions corrected the same way.
- 8 stale `Net-(Q1-G)` tracks deleted — they were the pre-R8 topology and shorted R3
  pad 2 and U3 pad 19.
- Zones refilled under the new 0.381 mm edge clearance (fixed a GND zone at 0.05 mm).
- 4 mounting holes flagged **board-only** so F8 cannot delete them.
- Pad nets for `U2.2`, `U2.3`, `U2.6`, `U1.1`, `C3.1`, `C4.1`, `C5.1` set
  programmatically to match the schematic (what F8 would do — re-run F8 to confirm).

### Design rules — now OSHPark 2-layer

| Rule | Was | Now |
|---|---|---|
| Min clearance | 0.0 | 0.1524 mm (6 mil) |
| Min track width | 0.2 | 0.1524 mm (6 mil) |
| Min drill | 0.30 | 0.3302 mm (13 mil) |
| Min annular ring | 0.05 | 0.1778 mm (7 mil) |
| Copper to edge | 0.05 | 0.381 mm (15 mil) |
| Hole to hole | 0.25 | 0.5 mm |

### Documentation

`pin-notes.txt` — J2 table replaced with the verified FLIR pinout; Pi-side rows
corrected; Q1 section now names BSS138 and warns about G-S-D pad order.

---

## 5. Two corrections worth remembering

**The Lepton J2 pinout.** Two long-recorded "bugs" — "J2-P1 shorted to GND" and "J2-P8
wired to SCL instead of SPI_CS" — were **false alarms** from an incorrect J2 table in
`pin-notes.txt`. P1 *is* GND and P8 *is* SCL on the FLIR Lepton Breakout v2.0. The
authoritative pinout was traced from `References/FLIR_Lepton_Breakout_Board_V2_Schematic-16912.pdf`
by extracting its vector geometry (text positions alone are ambiguous). Applying the
previously recorded "fixes" would have broken a working bus.

**Sensors must be on 3.3 V, not 5 V.** Both Adafruit breakouts reference their I2C logic
level to VIN:
- `Adafruit BNO055.sch` (in repo): MOSFET level shifters Q1/Q2 with high-side pull-ups
  R8/R9 tied to the `5.0V` net = JP1 pin 1 = VIN; gates to the 3.3 V regulator output.
- AHT20 datasheet: *"SCL — the logic level is the same as VIN and it has a 10K pullup."*

With VIN = 5 V they would pull the Pi's 3.3 V-only I2C pins to ~3.6 V. An earlier decision
in this session moved C3/C4/C5 *to* `+5V` to match the VIN wiring — that was wrong, and
was reversed. The original `+3V3` cap placement reflected the correct intent.

Verified Adafruit BNO055 pinout: **JP1 (1×6)** VIN, 3.3V, GND, SDA, SCL, RST ·
**JP2 (1×4)** PS0, PS1, INT, I2CADDR.

---

## 6. Tooling notes

KiCad is **Flatpak-only** here (`org.kicad.KiCad` 10.0.6). There is no native
`kicad-cli`, so anything shelling out to it — including the KiCad MCP server — fails
until a shim exists. **Shim at `~/.local/bin/kicad-cli`** (survives reboot):

```bash
exec flatpak run --command=kicad-cli \
  --filesystem=/tmp --filesystem=/var/tmp org.kicad.KiCad "$@"
```

The `/tmp` grants matter — the sandbox does not share `/tmp` and callers write reports
and renders there.

`pcbnew` Python works inside the sandbox and is the safe way to modify a board:

```bash
flatpak run --filesystem=/tmp --command=python3 org.kicad.KiCad -c "import pcbnew; ..."
```

### Not scriptable

- **Update PCB from Schematic (F8)** — no CLI subcommand, and the SWIG bindings expose no
  `NETLIST` / `BOARD_NETLIST_UPDATER`. Must be done in the pcbnew GUI.
- MCP server is **read-only** — all 16 tools are analysis/export, no mutation.
- MCP `generate_pcb_thumbnail` returns an un-serialized object; use
  `kicad-cli pcb render` and read the PNG.
- MCP `extract_schematic_netlist` cannot resolve connectivity (reports 0 pin
  connections). Use `kicad-cli sch export netlist --format kicadxml`.
- MCP `list_projects` returns empty; pass explicit paths.

**Close KiCad before editing project files externally** — it holds a `.lck` and
overwrites external changes on save.

---

## 7. Artifacts

`kicad-session-artifacts/` (copied out of `/tmp`, which the reboot wipes):

| File | What |
|---|---|
| `netlist-current.xml` | Authoritative schematic netlist at handoff |
| `drc-current.json` | DRC at handoff (17 violations, 26 unconnected) |
| `erc-current.rpt` | ERC at handoff (58 warnings, 0 errors) |
| `board-top-current.png` | F.Cu + silkscreen + outline render |
| `evidence-flir-j2-*.png` | 600 dpi crops of the FLIR J2 header used to derive the pinout |
| `tool-symbol-pin-positions.py` | Computes absolute schematic pin coords (validated) |
| `tool-pdf-vector-extract.py` | Pulls line geometry out of a PDF schematic |
| `backup-pcb-before-gpio17-copper-removal.kicad_pcb` | Pre-edit PCB |
| `backup-sch-before-bno055-fixes.kicad_sch` | Pre-edit schematic |

### Git state at handoff

Last commit `a026a16` "Fix GPIO17, MASTER_CLK, WittyPi SW short, Q1 mis-pinning; OSHPark
rules" captures the state **before** F8/placement. Uncommitted on top of it:

- `WaterCam_mDot_WittyPi_AHT_BNO_Lepton.kicad_pcb` — F8 + placement + the PCB fixes above
- `WaterCam_mDot_WittyPi_AHT_BNO_Lepton.kicad_sch` — BNO055 fixes, sensor rails, U2 INT
- `pin-notes.txt` — untracked, rewritten

**These are uncommitted.** Files survive a reboot, but committing is the safer checkpoint.
