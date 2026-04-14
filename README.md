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
├── BOM/
│   └── BOM.csv                  # Full BOM with LCSC part numbers
├── docs/
│   ├── SCHEMATIC_DESIGN.md      # Schematic block descriptions and net list
│   ├── PCB_LAYOUT_GUIDE.md      # Placement and routing guide
│   └── DESIGN_DECISIONS.md      # Design rationale and trade-offs
├── schematic/
│   └── surftrak_schematic.json  # EasyEDA Standard schematic JSON
├── pcb/
│   └── surftrak_pcb.json        # EasyEDA Standard PCB JSON
└── gerber_guide/
    └── EXPORT_INSTRUCTIONS.md   # How to export Gerbers for JLCPCB
```

## Quick Start

1. Import `schematic/surftrak_schematic.json` into EasyEDA Standard
2. Review and verify all connections against `docs/SCHEMATIC_DESIGN.md`
3. Import `pcb/surftrak_pcb.json` into EasyEDA Standard PCB editor
4. Verify board outline is exactly 88mm circle
5. Run DRC, resolve any errors
6. Export Gerbers following `gerber_guide/EXPORT_INSTRUCTIONS.md`
7. Upload to JLCPCB with BOM for PCBA service (exclude WS2812B per BOM notes)

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
