# SurfTrak Carrier PCB

Carrier board for the SurfTrak autonomous surf-tracking camera system.
Integrates all electronics except motor, batteries, camera, and UWB modules
(those connect via on-board connectors).

## Board Specs

| Parameter | Value |
|-----------|-------|
| Shape | Circle, 88mm diameter |
| Clearance | 3.5mm to 95mm housing interior |
| Layers | 2-layer, 1.6mm FR4 |
| Manufacturer | JLCPCB |
| Software | EasyEDA Standard |

## Repository Layout

```
├── kicad/
│   ├── generate_schematic.py    # Run this → surftrak_carrier.kicad_sch
│   ├── generate_pcb.py          # Run this → surftrak_carrier.kicad_pcb
│   ├── surftrak_carrier.kicad_sch   (generated)
│   └── surftrak_carrier.kicad_pcb  (generated)
├── BOM/
│   └── BOM.csv                  # Full BOM with LCSC part numbers
├── docs/
│   ├── SCHEMATIC_DESIGN.md      # Pin-by-pin wiring reference for all ICs
│   ├── PCB_LAYOUT_GUIDE.md      # Component placement and routing guide
│   └── DESIGN_DECISIONS.md      # Design rationale and trade-offs
├── schematic/
│   └── surftrak_schematic.json  # EasyEDA Standard reference (fallback)
├── pcb/
│   └── surftrak_pcb.json        # EasyEDA Standard reference (fallback)
└── gerber_guide/
    └── EXPORT_INSTRUCTIONS.md   # Gerber + BOM + CPL export for JLCPCB
```

## Quick Start — KiCad Workflow (Recommended)

```bash
cd kicad
python3 generate_schematic.py   # → surftrak_carrier.kicad_sch
python3 generate_pcb.py         # → surftrak_carrier.kicad_pcb
```

Then in KiCad 7 or 8:

1. **Open** `kicad/surftrak_carrier.kicad_sch`
2. **Tools → Update Symbols from Library** (resolves `Device:R`, `Connector_Generic:*`, etc.)
3. **Wire up pins** in the schematic GUI — all global net labels are already placed; connect each component's pin stubs to the matching label. Use `docs/SCHEMATIC_DESIGN.md` as the pin-by-pin reference.
4. **Run ERC** (Inspect → Electrical Rules Checker), fix all errors
5. **Open** `kicad/surftrak_carrier.kicad_pcb` in KiCad PCB editor
6. **Tools → Update PCB from Schematic** — footprints appear in a pile
7. **Place footprints** per `docs/PCB_LAYOUT_GUIDE.md`
8. **Route traces** (press `X` for interactive router)
9. **Fill zones** (press `B`) — GND pours are pre-defined on both layers
10. **Inspect → Design Rules Checker** — must pass with 0 errors
11. **File → Fabrication Outputs → Gerbers + Drill Files + Component Placement**
12. Upload to JLCPCB per `gerber_guide/EXPORT_INSTRUCTIONS.md`

## EasyEDA Alternative

The `schematic/` and `pcb/` folders contain EasyEDA Standard JSON files as a
reference/fallback, but the KiCad files above are the primary design files.

## Power Architecture

```
USB-C (Panel) ──► JST 2P ──► TP4056 ──► BAT+ / BAT-
                                              │
Battery Pack ──► JST 2P ──────────────────────┤
                                              │
                                    Power Button (MOSFET)
                                              │
                              ┌───────────────┤
                              │               │
                         MP2307 #1       MP2307 #2
                              │               │
                            5V rail        3.3V rail
                         (Pi, LED,        (UWB modules,
                          TMC2209)         sensors)
                                              │
                         Battery ──► TMC2209 VM (motor voltage)
```

## GPIO Assignments (Pi Zero 2W)

| GPIO | Function | Destination |
|------|----------|-------------|
| 7 (CE1) | SPI CS | UWB Module #2 |
| 8 (CE0) | SPI CS | UWB Module #1 |
| 9 (MISO) | SPI | Both UWB |
| 10 (MOSI) | SPI | Both UWB |
| 11 (SCK) | SPI | Both UWB |
| 14 (TXD) | UART TX | TMC2209 UART RX |
| 15 (RXD) | UART RX | TMC2209 UART TX |
| 18 | PWM | WS2812B Data |
| 20 | GPIO | TMC2209 STEP |
| 21 | GPIO | TMC2209 DIR |
| 24 | GPIO | TMC2209 EN |

## Important Notes

- **WS2812B (LCSC C52917433)** is hand-soldered only — exclude from JLCPCB PCBA order
- **Pi Zero 2W** castellated pads: verify orientation against Pi mechanical drawing before routing
- **TMC2209 module** uses 2.54mm pin headers — verify exact module pinout before ordering PCB
- **Arducam IMX519** connects via 15-pin CSI FPC to a short adapter cable to the Pi's 22-pin mini-CSI
