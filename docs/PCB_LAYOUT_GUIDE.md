# SurfTrak Carrier PCB — PCB Layout Guide

## Board Setup

### Board Outline
- Shape: Circle, diameter = **88.0mm exactly**
- In EasyEDA: Draw the board outline on the **BoardOutline layer** using a circle
- Center the circle at coordinate (0, 0) or at (100, 100)mm for convenience
- Board outline line width: 0.1mm (JLCPCB requirement for routing)

### Design Rules (JLCPCB 2-layer Standard)

| Parameter | Value |
|-----------|-------|
| Min trace width (signal) | 0.2mm |
| Min trace width (power) | 0.5mm |
| Min clearance | 0.2mm |
| Min via drill | 0.3mm |
| Min via annular ring | 0.25mm (via pad diameter ≥ 0.8mm) |
| Min silkscreen width | 0.1mm |
| Copper pour | GND fill both layers, tied to GND net |

Configure these in EasyEDA: Design → Design Rule Settings.

### Layer Stack
| Layer | EasyEDA Name | Use |
|-------|-------------|-----|
| Top | TopCopper | Signal + power routing |
| Bottom | BottomCopper | Signal + GND pour |
| Top Silkscreen | TopSilkscreen | Component labels |
| Top Paste | TopPaste | SMD paste mask |
| Top Mask | TopSolderMask | SMD solder mask |
| Board Outline | BoardOutline | Board shape |

---

## Component Placement

### Priority Zones

The 88mm circle is divided into zones for placement clarity:

```
         ┌─────────────────────────────────┐
         │           TOP EDGE              │  ← JST connectors (J3 Battery, J4 USB-C, J5 Btn)
         │  ┌──────────────────────────┐   │
         │  │  U2/U3 (bucks)  TP4056  │   │  ← Power management (left of center)
         │  │  L1,L2  D1,D2   Q1,D3   │   │
         │  │                          │   │
         │  │     Pi Zero 2W           │   │  ← Pi centered (castellated pads)
         │  │   (J1 footprint)         │   │  Pi = 65mm×30mm, sits in board center
         │  │                          │   │
         │  │  J2 TMC2209 headers      │   │  ← TMC2209 below Pi, accessible
         │  │  J7 Motor JST            │   │
         │  └──────────────────────────┘   │
         │    J8,J9 UWB JSTs   J6 LED JST │  ← Bottom edge connectors
         │           BOTTOM EDGE           │
         └─────────────────────────────────┘

Left edge:  J10 (FPC Arducam) — if populated
Right edge: Free for airwire routing
```

### Detailed Placement Instructions

#### 1. Pi Zero 2W Castellated Pads (J1)
- **Position:** Board center (0,0)
- **Orientation:** Pi USB/CSI end toward bottom of board
- Footprint: 40 castellated pads in 2×20 grid, 2.54mm pitch
- Castellated pad size: 1.6mm × 1.2mm, with 0.8mm drill for through-hole castellated variant
- Pad 1 (3V3): top-left when viewed from top
- Verify pad 1 corner matches Pi Zero 2W mechanical drawing (Raspberry Pi drawing v1.1)

#### 2. Buck Converters U2 & U3 (MP2307)
- **Position:** Upper-left quadrant, near BAT+ input
- U2 (5V) at ~(-25mm, +20mm) from center
- U3 (3.3V) at ~(-25mm, +5mm) from center
- Orient SW pin toward inductor side (away from center)
- Place input caps (C1,C3 and C5,C7) on BATT_SW side of IC
- Place output caps (C2,C4 and C6,C8) on 5V/3V3 output side

#### 3. Inductors L1 & L2 (4.7µH)
- Adjacent to SW pin of respective MP2307
- L1: ~(-35mm, +20mm) — between U2 and D1
- L2: ~(-35mm, +5mm) — between U3 and D2
- Orient so current flows in a short loop: IN → IC → L → output cap

#### 4. Schottky Diodes D1, D2 (SS24)
- Anode → GND plane via pour
- Cathode → SW node of each buck (between inductor and output)
- Keep as close as possible to the SW node

#### 5. TP4056 (U1)
- **Position:** Upper-right quadrant, near J4 (USB-C JST)
- U1 at ~(+25mm, +25mm) from center
- VIN pins toward J4
- BAT pin faces Pi (connects to BAT+ net)
- Place C9 (100nF) right at pin 3/4/8 VIN pads
- Place C16 (4.7µF) right at pin 5 BAT pad

#### 6. MOSFET Q1 and D3
- Q1 at ~(+15mm, +25mm), between BAT+ input and buck converters
- D3 (reverse polarity protection) on J3 BAT+ output, before Q1 source

#### 7. TMC2209 Module Headers (J2_A, J2_B)
- **Position:** Below Pi, in lower-center area
- Two parallel 1×8 socket rows, 15.24mm apart (standard DIP spacing for Stepstick)
- J2_A: center at ~(-7.62mm, -20mm)
- J2_B: center at ~(+7.62mm, -20mm)
- Leave at least 15mm clearance above for Pi castellated edge pads
- Ensure module doesn't extend beyond board edge when plugged in

#### 8. Motor JST (J7)
- Adjacent to TMC2209 headers J2_B (right side)
- Position at ~(+30mm, -20mm), oriented toward right edge
- Motor current traces must be at least 0.8mm wide (1A+ per phase)

#### 9. Battery JST (J3)
- **Position:** Top edge or top-left, closest to J4 and power components
- At ~(-35mm, +35mm) — pointing toward board top edge
- Short, direct path to D3 → Q1 → BATT_SW

#### 10. USB-C JST (J4)
- **Position:** Top edge, right side
- At ~(+25mm, +35mm)
- Short path to TP4056 VIN

#### 11. Power Button JST (J5)
- Adjacent to Q1 gate circuit
- At ~(+10mm, +35mm), top edge

#### 12. WS2812B LED (LED1) and JST (J6)
- LED1: on-board, lower-right area at ~(+30mm, -10mm)
- J6: adjacent, at ~(+35mm, -10mm) — for external LED option
- LED_DATA trace: 33Ω series resistor close to Pi GPIO18 pad

#### 13. UWB JSTs (J8, J9)
- Bottom edge, flanking TMC2209 headers
- J8: at ~(-30mm, -35mm)
- J9: at ~(0mm, -35mm)
- Route 3V3 and SPI bus traces from Pi to here (keep SPI traces matched length if possible)

#### 14. Arducam FPC (J10)
- Left edge, at ~(-40mm, 0mm)
- Bottom-contact type — component on top layer, connects from below
- If J10 is only a cable anchor, route no signals through the carrier board (cable goes direct to Pi CSI)

---

## Routing Guide

### Critical Routing Order
Route in this order to minimize DRC errors:

1. **GND pour** — set up last but plan for it from the start; all GND connections via vias
2. **Power rails first**: BAT+ → Q1 → BATT_SW → U2/U3 inputs → 5V/3V3 outputs
3. **Switching nodes** (MP2307 SW pins): keep loop area MINIMUM
   - Loop: IN cap → IC → L → output cap → GND. This loop must be as small as possible.
4. **UART lines** (GPIO14/15 to TMC2209): route together, avoid crossing power traces
5. **SPI bus** (GPIO 7–11 to UWB JSTs): route as a bundle, keep traces similar length
6. **Motor outputs** (J2_B → J7): wide traces, short path, away from SPI/UART
7. **LED_DATA** (Pi GPIO18 → 33Ω → LED1): short trace
8. **Signal wiring** (STEP, DIR, EN to TMC2209): short and direct

### Trace Width Rules

| Net Type | Min Width | Recommended |
|----------|-----------|-------------|
| Signal (UART, SPI, GPIO) | 0.2mm | 0.25mm |
| Power (5V, 3V3) | 0.5mm | 0.8mm |
| Battery (BAT+, BATT_SW) | 0.8mm | 1.0mm |
| Motor outputs | 0.8mm | 1.0mm |
| Ground fills | Pour | Pour (both layers) |

### Via Rules

| Parameter | Value |
|-----------|-------|
| Drill diameter | 0.3mm minimum, use 0.4mm for reliability |
| Pad diameter | 0.8mm minimum |
| GND stitching vias | Place around board perimeter and between pour sections |

### Switching Node Rules (Critical for EMC)

For each MP2307 buck converter:
- The loop: IN_cap(+) → IC_pin5 → IC_pin3_SW → L → output → IC_pin7_GND → IN_cap(-) must be TIGHT
- Place Schottky diode D1/D2 cathode directly at the SW node pad
- Avoid routing other signals near SW node traces
- Keep inductor L1/L2 footprint oriented so current flows in a short, direct path
- Add GND copper pour on the BOTTOM layer beneath the switching section

### Copper Pour Setup

| Pour | Layer | Net | Notes |
|------|-------|-----|-------|
| Top GND | TopCopper | GND | Fill around all components, connect to GND net |
| Bottom GND | BottomCopper | GND | Solid pour underneath entire board |
| Thermal relief | Both | GND | Use for through-hole pads; solid for SMD GND pads |

GND stitching: Place vias every ~10mm around the perimeter and across the board to connect top and bottom pours.

### Clearance Zones

- Keep 2mm clearance from board edge to any copper (JLCPCB requirement)
- Keep 3mm clearance between switching nodes (L, SW, D) and UART/SPI signals
- Keep inductors L1, L2 at least 5mm apart to avoid magnetic coupling

---

## Silkscreen

Label all JST connectors with their function and pin 1 polarity:
- J3: BAT+ / BAT-
- J4: VBUS / GND
- J5: BTN / GND
- J6: 5V / DATA / GND
- J7: A1 / A2 / B1 / B2
- J8: 3V3 / GND / MOSI / MISO / SCK / CS1
- J9: 3V3 / GND / MOSI / MISO / SCK / CS2

Add board version text: "SurfTrak Carrier v1.0" on silkscreen.
Add "JLCPCB" logo placeholder if required by JLCPCB for free boards.

---

## DRC Checklist

Before submitting Gerbers, verify:
- [ ] Board outline is exactly 88.000mm circle on BoardOutline layer
- [ ] All SMD pads have paste openings (TopPaste layer)
- [ ] Minimum trace width: 0.2mm (signal), 0.5mm (power)
- [ ] Minimum clearance: 0.2mm
- [ ] No unconnected nets (check Ratsnest = 0)
- [ ] All power nets have bypass caps placed adjacent to IC pins
- [ ] Switching node loops are tight and verified visually
- [ ] All JST connectors oriented toward board edge
- [ ] Pi castellated pads align with Pi Zero 2W mechanical drawing
- [ ] GND pour on both layers, stitching vias placed
- [ ] 2mm edge clearance maintained
- [ ] DRC passes with 0 errors, 0 warnings
