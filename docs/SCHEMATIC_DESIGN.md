# SurfTrak Carrier PCB — Schematic Design Reference

Use this document as the authoritative schematic blueprint when building in EasyEDA Standard.
Every net name, pin connection, and power flag described here must appear in the schematic.

---

## Net Names (global labels)

| Net | Description |
|-----|-------------|
| VBUS | USB-C input, +5V from panel USB-C port |
| BAT+ | Battery positive (raw LiPo, ~3.7–4.2V) |
| BAT- | Battery ground |
| BATT_SW | Battery switched output (after Q1 power switch) |
| 5V | Regulated 5V rail (MP2307 #1 output) |
| 3V3 | Regulated 3.3V rail (MP2307 #2 output) |
| GND | Common ground |
| UART_TX | Pi GPIO14 → TMC2209 PDN_UART (TX) |
| UART_RX | Pi GPIO15 ← TMC2209 PDN_UART (RX) |
| STEP | Pi GPIO20 → TMC2209 STEP |
| DIR | Pi GPIO21 → TMC2209 DIR |
| TMC_EN | Pi GPIO24 → TMC2209 ENN |
| SPI_MOSI | Pi GPIO10 → UWB1, UWB2 |
| SPI_MISO | Pi GPIO9 ← UWB1, UWB2 |
| SPI_SCK | Pi GPIO11 → UWB1, UWB2 |
| UWB1_CS | Pi GPIO8 → UWB Module 1 CS |
| UWB2_CS | Pi GPIO7 → UWB Module 2 CS |
| LED_DATA | Pi GPIO18 → WS2812B DIN |
| MOT_A1 | TMC2209 OA1 → Motor A1 |
| MOT_A2 | TMC2209 OA2 → Motor A2 |
| MOT_B1 | TMC2209 OB1 → Motor B1 |
| MOT_B2 | TMC2209 OB2 → Motor B2 |

---

## Block 1 — USB-C Input and TP4056 Charger

### Connector J4 (USB-C JST PH 2.0 2-pin)
```
J4 pin 1 → VBUS
J4 pin 2 → GND
```

### IC U1 — TP4056 (ESOP-8)

| Pin | Name | Connection |
|-----|------|------------|
| 1 | PROG | R5 (1.2kΩ) → GND  — sets charge current 833mA |
| 2 | GND | GND |
| 3 | VIN | VBUS |
| 4 | VIN | VBUS (both VIN pins tied together) |
| 5 | BAT | BAT+ (through C16 4.7µF to GND) |
| 6 | CHRG | LED indicator (optional: 1kΩ to GND) |
| 7 | STDBY | No connect (or LED indicator) |
| 8 | VIN | VBUS |

Bypass caps:
- C9 (100nF 0402) from VBUS to GND, placed adjacent to U1 pin 3
- C16 (4.7µF 0805) from BAT+ to GND, placed adjacent to U1 pin 5

**Power flag:** Place PWR_FLAG on VBUS and GND nets.

---

## Block 2 — Power Switch (P-Channel MOSFET)

### Q1 — AO3401A (SOT-23, P-channel)

```
Q1 Source → BAT+          (battery direct)
Q1 Drain  → BATT_SW       (switched battery, feeds buck converters)
Q1 Gate   → Gate node
```

Gate resistor network:
```
BAT+ → R6 (10kΩ) → Gate node   (pulls gate to BAT+ = MOSFET OFF by default)
Gate node → R8 (100kΩ) → R7 (100kΩ) → GND  (voltage divider, holds gate floating stable)
```

Power button:
```
J5 pin 1 → Gate node
J5 pin 2 → GND
```
When button is pressed: Gate node pulled to GND through J5 → Gate–Source voltage goes negative → MOSFET turns ON.
When button released: R6 pulls gate back toward BAT+ → MOSFET turns OFF.

> NOTE: This is a simple non-latching press-to-hold circuit. For a latching power button,
> add an SR latch (two NAND gates, e.g. SN74LVC2G00) or use a dedicated IC like the TPS27082L.
> For initial prototype, a maintained (latching) rocker switch at J5 is simplest.

---

## Block 3 — MP2307 Buck Converter #1 (5V Rail)

### IC U2 — MP2307DN (SOP-8)

MP2307 reference circuit (from datasheet):
```
BATT_SW ──── IN (pin 5) ──── also BST cap: C_bst (100nF) from SW to BST
                │
              C1 (100µF) to GND   [input bulk cap]
              C3 (10µF) to GND    [input ceramic]
                │
              SW (pin 3) ──── L1 (4.7µH) ──── 5V output
                                  │
                              D1 (SS24) anode to GND, cathode to SW node
                              C2 (100µF) to GND  [output bulk]
                              C4 (10µF) to GND   [output ceramic]
                                  │
                                  ├──── 5V net (to Pi 5V, J6, TMC2209)
                                  │
                              FB divider:
                              R1 (100kΩ) from 5V to FB (pin 4)
                              R2 (22.6kΩ) from FB to GND
                                  │
                              FB (pin 4) → voltage divider node
```

| Pin | Name | Connection |
|-----|------|------------|
| 1 | SS | Soft-start: 10nF cap to GND |
| 2 | EN | Pulled to BATT_SW via 100kΩ (always-on when powered) |
| 3 | SW | To L1 and D1 cathode |
| 4 | FB | R1/R2 divider node |
| 5 | IN | BATT_SW |
| 6 | IN | BATT_SW |
| 7 | GND | GND |
| 8 | BST | 100nF cap to SW pin |

Output: **5.02V** nominal (Vout = 0.925 × (1 + 100k/22.6k))

---

## Block 4 — MP2307 Buck Converter #2 (3.3V Rail)

### IC U3 — MP2307DN (SOP-8)

Identical circuit to U2 with different FB resistors:

| Pin | Connection |
|-----|------------|
| 1 (SS) | 10nF to GND |
| 2 (EN) | Pulled to BATT_SW via 100kΩ |
| 3 (SW) | L2 (4.7µH) + D2 (SS24) anode to GND |
| 4 (FB) | R3 (68kΩ) from 3V3 to FB; R4 (27.4kΩ) from FB to GND |
| 5,6 (IN) | BATT_SW |
| 7 (GND) | GND |
| 8 (BST) | 100nF to SW |

Capacitors:
- C5 (100µF) + C7 (10µF) on BATT_SW input, before U3
- C6 (100µF) + C8 (10µF) on 3V3 output

Output: **~3.22V** nominal (Vout = 0.925 × (1 + 68k/27.4k))

---

## Block 5 — Raspberry Pi Zero 2W Castellated Pads

Create a custom footprint with 40 castellated pads matching the Pi Zero 2W
mechanical drawing. Pin 1 is at top-left when Pi is viewed component-side up.

### Power connections (Pi must receive 5V on pin 2 or 4, NOT 3.3V)

| Pi Pin | Signal | Carrier Net |
|--------|--------|-------------|
| 1 | 3V3 power | 3V3 (output from Pi's own regulator — do NOT drive) |
| 2 | 5V power | 5V (INPUT: carrier 5V rail powers Pi) |
| 4 | 5V power | 5V |
| 6 | GND | GND |
| 9 | GND | GND |
| 14 | GND | GND |
| 17 | 3V3 power | 3V3 (output — can use to power small loads) |
| 20 | GND | GND |
| 25 | GND | GND |
| 30 | GND | GND |
| 34 | GND | GND |
| 39 | GND | GND |

### GPIO connections

| Pi Pin | GPIO | Signal | Destination |
|--------|------|--------|-------------|
| 8 | GPIO14 / TXD | UART_TX | TMC2209 PDN_UART |
| 10 | GPIO15 / RXD | UART_RX | TMC2209 PDN_UART |
| 12 | GPIO18 | LED_DATA | WS2812B DIN |
| 18 | GPIO24 | TMC_EN | TMC2209 ENN |
| 19 | GPIO10 / MOSI | SPI_MOSI | UWB1 & UWB2 |
| 21 | GPIO9 / MISO | SPI_MISO | UWB1 & UWB2 |
| 23 | GPIO11 / SCK | SPI_SCK | UWB1 & UWB2 |
| 24 | GPIO8 / CE0 | UWB1_CS | UWB Module 1 CS |
| 26 | GPIO7 / CE1 | UWB2_CS | UWB Module 2 CS |
| 38 | GPIO20 | STEP | TMC2209 STEP |
| 40 | GPIO21 | DIR | TMC2209 DIR |

### Unused GPIO
All remaining GPIO pins should be connected to labeled test points or left as NC.
Connect ID_SD (pin 27) and ID_SC (pin 28) to GND via 1kΩ if unused.

---

## Block 6 — TMC2209 Module Headers

### J2 — 2x 1×8 pin sockets, 2.54mm pitch (Stepstick-compatible)

The TMC2209 module sits across two 1×8 sockets.
Verify against your specific module (BIGTREETECH, Watterott, etc.) — pinouts vary.

**Left socket (J2_A) — common Stepstick layout:**

| Socket Pin | Signal | Connection |
|------------|--------|------------|
| 1 | ENN | TMC_EN (Pi GPIO24) — active LOW enables driver |
| 2 | MS2 | GND (UART mode: MS1=0, MS2=0 or both to 3V3 per module) |
| 3 | MS1 | GND |
| 4 | PDN_UART | UART_TX from Pi (also R9 10kΩ pull-up to 3V3) |
| 5 | CLK / PDN | GND (use internal clock) |
| 6 | STEP | STEP (Pi GPIO20) |
| 7 | DIR | DIR (Pi GPIO21) |
| 8 | GND | GND |

**Right socket (J2_B) — common Stepstick layout:**

| Socket Pin | Signal | Connection |
|------------|--------|------------|
| 1 | VREF | Analog voltage for current ref — see note |
| 2 | OB2 | MOT_B2 |
| 3 | OB1 | MOT_B1 |
| 4 | OA1 | MOT_A1 |
| 5 | OA2 | MOT_A2 |
| 6 | VIO | 3V3 (TMC2209 logic supply) |
| 7 | VM | BATT_SW (motor supply — direct battery voltage) |
| 8 | GND | GND |

VREF: Connect to a voltage divider (or potentiometer) from 3V3 to set motor current limit.
For fixed current: R_top=10kΩ, R_bottom=10kΩ gives VREF=1.65V → Imax ≈ 1.77A (RMS).
Bypass VREF pin with 100nF to GND.

> IMPORTANT: Check your TMC2209 module datasheet. Some modules swap OA1/OA2 or OB1/OB2,
> and some combine MS1/MS2/CLK differently. Motor phase order affects direction only.

---

## Block 7 — Motor JST Connector

### J7 — JST PH 2.0 4-pin

| Pin | Signal | Net |
|-----|--------|-----|
| 1 | A1 | MOT_A1 |
| 2 | A2 | MOT_A2 |
| 3 | B1 | MOT_B1 |
| 4 | B2 | MOT_B2 |

Route from J2_B socket pins 2-5 directly to J7. Keep traces short and at least 0.5mm wide.

---

## Block 8 — UWB Modules (DWM3000 × 2)

Both UWB modules share the SPI bus. CS lines are independent.

### J8 — UWB Module 1 (JST PH 2.0 6-pin)

| Pin | Signal | Net |
|-----|--------|-----|
| 1 | VCC | 3V3 |
| 2 | GND | GND |
| 3 | MOSI | SPI_MOSI |
| 4 | MISO | SPI_MISO |
| 5 | SCK | SPI_SCK |
| 6 | CS | UWB1_CS |

### J9 — UWB Module 2 (JST PH 2.0 6-pin)

| Pin | Signal | Net |
|-----|--------|-----|
| 1 | VCC | 3V3 |
| 2 | GND | GND |
| 3 | MOSI | SPI_MOSI |
| 4 | MISO | SPI_MISO |
| 5 | SCK | SPI_SCK |
| 6 | CS | UWB2_CS |

Add 100nF bypass caps (C11, C12) on 3V3 at each UWB connector.

---

## Block 9 — WS2812B LED

### LED1 — WS2812B 5050 (hand-soldered)

| Pin | Connection |
|-----|------------|
| VDD | 5V |
| GND | GND |
| DIN | LED_DATA (Pi GPIO18) — add 33Ω series resistor to DIN |
| DOUT | NC (only one LED) |

### J6 — WS2812B JST PH 2.0 3-pin (for external LED if needed)

| Pin | Signal |
|-----|--------|
| 1 | 5V |
| 2 | LED_DATA |
| 3 | GND |

> NOTE: LED1 is hand-soldered. J6 is an alternative connector for external LED strip.
> Do not populate both simultaneously without additional buffers.

---

## Block 10 — Arducam IMX519 FPC Connector

### J10 — 15-pin FPC, 1.0mm pitch, bottom contact

Standard Pi CSI-2 15-pin pinout:

| Pin | Signal | Notes |
|-----|--------|-------|
| 1 | GND | |
| 2 | CSI_D0N | Differential pair |
| 3 | CSI_D0P | Differential pair |
| 4 | GND | |
| 5 | CSI_D1N | Differential pair |
| 6 | CSI_D1P | Differential pair |
| 7 | GND | |
| 8 | CSI_CLN | Differential clock pair |
| 9 | CSI_CLP | Differential clock pair |
| 10 | GND | |
| 11 | CAM_GPIO | GPIO for camera enable (connect to free Pi GPIO) |
| 12 | GND | |
| 13 | SCL | I2C clock (Pi GPIO3) |
| 14 | SDA | I2C data (Pi GPIO2) |
| 15 | VCC | 3V3 |

> IMPORTANT: The Pi Zero 2W has a 22-pin mini-CSI connector. Connect J10 to Pi CSI
> via a 15-to-22-pin adapter ribbon cable (Arducam sells these). Do NOT route CSI
> differential pairs through the carrier board — use a direct flex cable to the Pi.
> J10 is provided as a strain-relief mounting point on the carrier board only.
> For a cleaner design, consider omitting J10 and routing the camera cable directly
> to the Pi via its own connector above the carrier board.

---

## Decoupling Summary

Place all bypass caps as close as possible to the IC they serve.

| Cap | Value | Location |
|-----|-------|----------|
| C9 | 100nF | TP4056 VIN, adjacent to U1 |
| C10 | 100nF | TP4056 PROG |
| C16 | 4.7µF | TP4056 BAT output |
| C1,C3 | 100µF + 10µF | MP2307 #1 input |
| C2,C4 | 100µF + 10µF | MP2307 #1 output (5V) |
| C5,C7 | 100µF + 10µF | MP2307 #2 input |
| C6,C8 | 100µF + 10µF | MP2307 #2 output (3.3V) |
| C11 | 100nF | UWB1 3V3 |
| C12 | 100nF | UWB2 3V3 |
| C13 | 100nF | Pi 3V3 pin 1/17 |
| C14 | 100nF | Pi 5V pin 2/4 |
| C15 | 100nF | TMC2209 VIO |

---

## Power Flags (EasyEDA)

Place a PWR_FLAG symbol on the following nets to satisfy ERC:
- VBUS
- BAT+
- BATT_SW
- 5V
- 3V3
- GND (one per schematic sheet if multi-sheet)
