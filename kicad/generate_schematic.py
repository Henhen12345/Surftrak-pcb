#!/usr/bin/env python3
"""
SurfTrak Carrier PCB — KiCad Schematic Generator
Generates surftrak_carrier.kicad_sch for KiCad 7 or 8.

Usage:
    python3 generate_schematic.py

Output:
    surftrak_carrier.kicad_sch  (open in KiCad, run ERC, then File > Export > Netlist)

After opening in KiCad:
1. Tools > Update PCB from Schematic  (or open surftrak_carrier.kicad_pcb)
2. Place footprints per docs/PCB_LAYOUT_GUIDE.md
3. Route traces, add GND pours
4. File > Fabrication Outputs > Gerbers
"""

import uuid
import os

# ---------------------------------------------------------------------------
# UUID helpers
# ---------------------------------------------------------------------------
_uid_counter = [1]

def uid():
    u = f"00000000-0000-4000-8000-{_uid_counter[0]:012d}"
    _uid_counter[0] += 1
    return u

# ---------------------------------------------------------------------------
# Schematic coordinate grid  (KiCad uses mm)
# All X/Y positions below are schematic canvas mm coords.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Component database
# Each entry: ref, value, lib_id, footprint, lcsc, (x, y), rotation, pins
# pins maps pin_number -> net_name  (used to place global labels on pin ends)
# ---------------------------------------------------------------------------

# Pin endpoint offsets for common symbols (KiCad standard library pin layout)
# These tell us where each pin stub ends relative to component origin.
# Positive X = right, Positive Y = DOWN in KiCad schematic coords.

COMPONENTS = [
    # ── POWER INPUT ──────────────────────────────────────────────────────────
    dict(ref="J4", value="USB-C JST PH2.0",
         lib_id="Connector_Generic:Conn_01x02",
         footprint="Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical",
         lcsc="C152168", x=22, y=22,
         pins={"1": "VBUS", "2": "GND"}),

    dict(ref="J3", value="Battery JST PH2.0",
         lib_id="Connector_Generic:Conn_01x02",
         footprint="Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical",
         lcsc="C152168", x=22, y=40,
         pins={"1": "BAT+", "2": "GND"}),

    dict(ref="J5", value="Power Button",
         lib_id="Connector_Generic:Conn_01x02",
         footprint="Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical",
         lcsc="C152168", x=22, y=58,
         pins={"1": "GATE_NODE", "2": "GND"}),

    # ── TP4056 CHARGER ────────────────────────────────────────────────────────
    dict(ref="U1", value="TP4056",
         lib_id="SurfTrak:TP4056",
         footprint="Package_SO:ESOP-8_3.9x4.9mm_P1.27mm",
         lcsc="C16254", x=60, y=25,
         pins={"1": "PROG_U1", "2": "GND", "3": "VBUS",
               "4": "VBUS",   "5": "BAT+", "6": "NC",
               "7": "NC",     "8": "VBUS"}),

    dict(ref="R5", value="1.2k",
         lib_id="Device:R",
         footprint="Resistor_SMD:R_0402_1005Metric",
         lcsc="C25752", x=48, y=35,
         pins={"1": "PROG_U1", "2": "GND"}),

    dict(ref="C9", value="100nF",
         lib_id="Device:C",
         footprint="Capacitor_SMD:C_0402_1005Metric",
         lcsc="C14663", x=68, y=18,
         pins={"1": "VBUS", "2": "GND"}),

    dict(ref="C16", value="4.7uF",
         lib_id="Device:C",
         footprint="Capacitor_SMD:C_0805_2012Metric",
         lcsc="C1779", x=78, y=25,
         pins={"1": "BAT+", "2": "GND"}),

    # ── REVERSE PROTECTION + POWER SWITCH ────────────────────────────────────
    dict(ref="D3", value="SS24",
         lib_id="Device:D_Schottky",
         footprint="Diode_SMD:D_SMB",
         lcsc="C8598", x=38, y=42,
         pins={"A": "BAT+", "K": "BATT_PRE_Q1"}),

    dict(ref="Q1", value="AO3401A",
         lib_id="Device:Q_PMOS_SGD",
         footprint="Package_TO_SOT_SMD:SOT-23",
         lcsc="C15127", x=58, y=50,
         pins={"S": "BATT_PRE_Q1", "G": "GATE_NODE", "D": "BATT_SW"}),

    dict(ref="R6", value="10k",
         lib_id="Device:R",
         footprint="Resistor_SMD:R_0402_1005Metric",
         lcsc="C25744", x=48, y=55,
         pins={"1": "BATT_PRE_Q1", "2": "GATE_NODE"}),

    dict(ref="R7", value="100k",
         lib_id="Device:R",
         footprint="Resistor_SMD:R_0402_1005Metric",
         lcsc="C25741", x=38, y=62,
         pins={"1": "GATE_NODE", "2": "GND"}),

    dict(ref="R8", value="100k",
         lib_id="Device:R",
         footprint="Resistor_SMD:R_0402_1005Metric",
         lcsc="C25741", x=58, y=62,
         pins={"1": "GATE_NODE", "2": "GND"}),

    # ── 5V BUCK (MP2307 #1) ───────────────────────────────────────────────────
    dict(ref="U2", value="MP2307DN 5V",
         lib_id="SurfTrak:MP2307DN",
         footprint="Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
         lcsc="C14335", x=35, y=95,
         pins={"1": "GND", "2": "BATT_SW", "3": "SW1",
               "4": "FB1",  "5": "BATT_SW", "6": "BATT_SW",
               "7": "GND",  "8": "BST1"}),

    dict(ref="C_BST1", value="100nF",
         lib_id="Device:C",
         footprint="Capacitor_SMD:C_0402_1005Metric",
         lcsc="C14663", x=54, y=88,
         pins={"1": "SW1", "2": "BST1"}),

    dict(ref="L1", value="4.7uH",
         lib_id="Device:L",
         footprint="Inductor_SMD:L_Bourns_SRR1260",
         lcsc="C1046", x=55, y=95,
         pins={"1": "SW1", "2": "5V"}),

    dict(ref="D1", value="SS24",
         lib_id="Device:D_Schottky",
         footprint="Diode_SMD:D_SMB",
         lcsc="C8598", x=55, y=102,
         pins={"A": "GND", "K": "SW1"}),

    dict(ref="C1", value="100uF/16V",
         lib_id="Device:C_Polarized",
         footprint="Capacitor_SMD:CP_Elec_6.3x5.8",
         lcsc="C16643", x=24, y=105,
         pins={"~": "BATT_SW", "~": "GND"}),

    dict(ref="C3", value="10uF",
         lib_id="Device:C",
         footprint="Capacitor_SMD:C_0805_2012Metric",
         lcsc="C15850", x=32, y=105,
         pins={"1": "BATT_SW", "2": "GND"}),

    dict(ref="C2", value="100uF/16V",
         lib_id="Device:C_Polarized",
         footprint="Capacitor_SMD:CP_Elec_6.3x5.8",
         lcsc="C16643", x=70, y=95,
         pins={"~": "5V", "~": "GND"}),

    dict(ref="C4", value="10uF",
         lib_id="Device:C",
         footprint="Capacitor_SMD:C_0805_2012Metric",
         lcsc="C15850", x=78, y=95,
         pins={"1": "5V", "2": "GND"}),

    dict(ref="R1", value="100k",
         lib_id="Device:R",
         footprint="Resistor_SMD:R_0402_1005Metric",
         lcsc="C25741", x=35, y=112,
         pins={"1": "5V", "2": "FB1"}),

    dict(ref="R2", value="22.6k",
         lib_id="Device:R",
         footprint="Resistor_SMD:R_0402_1005Metric",
         lcsc="C25900", x=35, y=120,
         pins={"1": "FB1", "2": "GND"}),

    # ── 3.3V BUCK (MP2307 #2) ─────────────────────────────────────────────────
    dict(ref="U3", value="MP2307DN 3V3",
         lib_id="SurfTrak:MP2307DN",
         footprint="Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
         lcsc="C14335", x=35, y=145,
         pins={"1": "GND", "2": "BATT_SW", "3": "SW2",
               "4": "FB2",  "5": "BATT_SW", "6": "BATT_SW",
               "7": "GND",  "8": "BST2"}),

    dict(ref="C_BST2", value="100nF",
         lib_id="Device:C",
         footprint="Capacitor_SMD:C_0402_1005Metric",
         lcsc="C14663", x=54, y=138,
         pins={"1": "SW2", "2": "BST2"}),

    dict(ref="L2", value="4.7uH",
         lib_id="Device:L",
         footprint="Inductor_SMD:L_Bourns_SRR1260",
         lcsc="C1046", x=55, y=145,
         pins={"1": "SW2", "2": "3V3"}),

    dict(ref="D2", value="SS24",
         lib_id="Device:D_Schottky",
         footprint="Diode_SMD:D_SMB",
         lcsc="C8598", x=55, y=152,
         pins={"A": "GND", "K": "SW2"}),

    dict(ref="C5", value="100uF/16V",
         lib_id="Device:C_Polarized",
         footprint="Capacitor_SMD:CP_Elec_6.3x5.8",
         lcsc="C16643", x=24, y=155,
         pins={"~": "BATT_SW", "~": "GND"}),

    dict(ref="C7", value="10uF",
         lib_id="Device:C",
         footprint="Capacitor_SMD:C_0805_2012Metric",
         lcsc="C15850", x=32, y=155,
         pins={"1": "BATT_SW", "2": "GND"}),

    dict(ref="C6", value="100uF/16V",
         lib_id="Device:C_Polarized",
         footprint="Capacitor_SMD:CP_Elec_6.3x5.8",
         lcsc="C16643", x=70, y=145,
         pins={"~": "3V3", "~": "GND"}),

    dict(ref="C8", value="10uF",
         lib_id="Device:C",
         footprint="Capacitor_SMD:C_0805_2012Metric",
         lcsc="C15850", x=78, y=145,
         pins={"1": "3V3", "2": "GND"}),

    dict(ref="R3", value="68k",
         lib_id="Device:R",
         footprint="Resistor_SMD:R_0402_1005Metric",
         lcsc="C25867", x=35, y=162,
         pins={"1": "3V3", "2": "FB2"}),

    dict(ref="R4", value="27.4k",
         lib_id="Device:R",
         footprint="Resistor_SMD:R_0402_1005Metric",
         lcsc="C25902", x=35, y=170,
         pins={"1": "FB2", "2": "GND"}),

    # ── PI ZERO 2W ────────────────────────────────────────────────────────────
    # Represented as a 2x20 connector. Pin numbering matches Pi Zero 2W GPIO header.
    # Odd pins on left (1,3,5,...,39), even pins on right (2,4,...,40)
    dict(ref="J1", value="Pi Zero 2W",
         lib_id="Connector_Generic:Conn_02x20_Odd_Even",
         footprint="SurfTrak:RPi_Zero2W_Castellated",
         lcsc="", x=125, y=100,
         pins={
             "1":  "3V3_PI_OUT",  "2":  "5V",
             "3":  "PI_GPIO2",    "4":  "5V",
             "5":  "PI_GPIO3",    "6":  "GND",
             "7":  "PI_GPIO4",    "8":  "UART_TX",
             "9":  "GND",         "10": "UART_RX",
             "11": "PI_GPIO17",   "12": "LED_DATA_RAW",
             "13": "PI_GPIO27",   "14": "GND",
             "15": "PI_GPIO22",   "16": "PI_GPIO23",
             "17": "3V3_PI_OUT",  "18": "TMC_EN",
             "19": "SPI_MOSI",    "20": "GND",
             "21": "SPI_MISO",    "22": "PI_GPIO25",
             "23": "SPI_SCK",     "24": "UWB1_CS",
             "25": "GND",         "26": "UWB2_CS",
             "27": "PI_ID_SD",    "28": "PI_ID_SC",
             "29": "PI_GPIO5",    "30": "GND",
             "31": "PI_GPIO6",    "32": "PI_GPIO12",
             "33": "PI_GPIO13",   "34": "GND",
             "35": "PI_GPIO19",   "36": "PI_GPIO16",
             "37": "PI_GPIO26",   "38": "STEP",
             "39": "GND",         "40": "DIR",
         }),

    # Decoupling caps for Pi supply
    dict(ref="C13", value="100nF",
         lib_id="Device:C",
         footprint="Capacitor_SMD:C_0402_1005Metric",
         lcsc="C14663", x=112, y=88,
         pins={"1": "3V3_PI_OUT", "2": "GND"}),

    dict(ref="C14", value="100nF",
         lib_id="Device:C",
         footprint="Capacitor_SMD:C_0402_1005Metric",
         lcsc="C14663", x=112, y=95,
         pins={"1": "5V", "2": "GND"}),

    # LED_DATA series resistor
    dict(ref="R_LED", value="33R",
         lib_id="Device:R",
         footprint="Resistor_SMD:R_0402_1005Metric",
         lcsc="C25744", x=112, y=102,
         pins={"1": "LED_DATA_RAW", "2": "LED_DATA"}),

    # ── TMC2209 MODULE HEADERS ────────────────────────────────────────────────
    dict(ref="J2A", value="TMC2209 Left",
         lib_id="Connector_Generic:Conn_01x08",
         footprint="Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical",
         lcsc="C2337", x=118, y=215,
         pins={"1": "TMC_EN", "2": "GND", "3": "GND",
               "4": "UART_TX", "5": "GND", "6": "STEP",
               "7": "DIR",     "8": "GND"}),

    dict(ref="J2B", value="TMC2209 Right",
         lib_id="Connector_Generic:Conn_01x08",
         footprint="Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical",
         lcsc="C2337", x=140, y=215,
         pins={"1": "TMC_VREF", "2": "MOT_B2", "3": "MOT_B1",
               "4": "MOT_A1",   "5": "MOT_A2", "6": "3V3",
               "7": "BATT_SW",  "8": "GND"}),

    dict(ref="R9", value="10k",
         lib_id="Device:R",
         footprint="Resistor_SMD:R_0402_1005Metric",
         lcsc="C25744", x=115, y=225,
         pins={"1": "3V3", "2": "UART_TX"}),

    dict(ref="C15", value="100nF",
         lib_id="Device:C",
         footprint="Capacitor_SMD:C_0402_1005Metric",
         lcsc="C14663", x=152, y=208,
         pins={"1": "3V3", "2": "GND"}),

    dict(ref="R_VREF1", value="10k",
         lib_id="Device:R",
         footprint="Resistor_SMD:R_0402_1005Metric",
         lcsc="C25744", x=152, y=220,
         pins={"1": "3V3", "2": "TMC_VREF"}),

    dict(ref="R_VREF2", value="10k",
         lib_id="Device:R",
         footprint="Resistor_SMD:R_0402_1005Metric",
         lcsc="C25744", x=152, y=228,
         pins={"1": "TMC_VREF", "2": "GND"}),

    dict(ref="C_VREF", value="100nF",
         lib_id="Device:C",
         footprint="Capacitor_SMD:C_0402_1005Metric",
         lcsc="C14663", x=160, y=225,
         pins={"1": "TMC_VREF", "2": "GND"}),

    # ── MOTOR CONNECTOR ───────────────────────────────────────────────────────
    dict(ref="J7", value="Motor JST PH2.0 4P",
         lib_id="Connector_Generic:Conn_01x04",
         footprint="Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical",
         lcsc="C9757", x=170, y=215,
         pins={"1": "MOT_A1", "2": "MOT_A2",
               "3": "MOT_B1", "4": "MOT_B2"}),

    # ── UWB MODULE CONNECTORS ─────────────────────────────────────────────────
    dict(ref="J8", value="UWB Module 1",
         lib_id="Connector_Generic:Conn_01x06",
         footprint="Connector_JST:JST_PH_B6B-PH-K_1x06_P2.00mm_Vertical",
         lcsc="C9754", x=200, y=35,
         pins={"1": "3V3", "2": "GND", "3": "SPI_MOSI",
               "4": "SPI_MISO", "5": "SPI_SCK", "6": "UWB1_CS"}),

    dict(ref="C11", value="100nF",
         lib_id="Device:C",
         footprint="Capacitor_SMD:C_0402_1005Metric",
         lcsc="C14663", x=212, y=35,
         pins={"1": "3V3", "2": "GND"}),

    dict(ref="J9", value="UWB Module 2",
         lib_id="Connector_Generic:Conn_01x06",
         footprint="Connector_JST:JST_PH_B6B-PH-K_1x06_P2.00mm_Vertical",
         lcsc="C9754", x=200, y=68,
         pins={"1": "3V3", "2": "GND", "3": "SPI_MOSI",
               "4": "SPI_MISO", "5": "SPI_SCK", "6": "UWB2_CS"}),

    dict(ref="C12", value="100nF",
         lib_id="Device:C",
         footprint="Capacitor_SMD:C_0402_1005Metric",
         lcsc="C14663", x=212, y=68,
         pins={"1": "3V3", "2": "GND"}),

    # ── WS2812B LED ───────────────────────────────────────────────────────────
    dict(ref="LED1", value="WS2812B ***HAND SOLDER***",
         lib_id="SurfTrak:WS2812B",
         footprint="LED_SMD:LED_WS2812B_PLCC4_5.0x5.0mm_P3.2mm",
         lcsc="C52917433", x=185, y=100,
         pins={"1": "5V", "2": "NC_DOUT", "3": "GND", "4": "LED_DATA"}),

    dict(ref="J6", value="LED JST PH2.0 3P",
         lib_id="Connector_Generic:Conn_01x03",
         footprint="Connector_JST:JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical",
         lcsc="C9752", x=200, y=100,
         pins={"1": "5V", "2": "LED_DATA", "3": "GND"}),

    # ── ARDUCAM FPC ───────────────────────────────────────────────────────────
    dict(ref="J10", value="CSI FPC 15P 1.0mm",
         lib_id="Connector_Generic:Conn_01x15",
         footprint="Connector_FFC-FPC:Hirose_FH12-15S-0.5SH_1x15-1MP_P0.50mm_Horizontal",
         lcsc="C77004", x=200, y=140,
         pins={"1": "GND",  "2": "CSI_D0N", "3": "CSI_D0P",
               "4": "GND",  "5": "CSI_D1N", "6": "CSI_D1P",
               "7": "GND",  "8": "CSI_CLN", "9": "CSI_CLP",
               "10": "GND", "11": "CAM_GPIO","12": "GND",
               "13": "PI_GPIO3","14": "PI_GPIO2","15": "3V3"}),
]

# ---------------------------------------------------------------------------
# Custom symbol definitions (inline in lib_symbols)
# ---------------------------------------------------------------------------

def sym_tp4056():
    return """\
    (symbol "SurfTrak:TP4056"
      (pin_names (offset 1.016))
      (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 9.525 0) (effects (font (size 1.27 1.27))))
      (property "Value" "TP4056" (at 0 -9.525 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_SO:ESOP-8_3.9x4.9mm_P1.27mm" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "TP4056_0_1"
        (rectangle (start -5.08 -8.89) (end 5.08 8.89)
          (stroke (width 0.254) (type default)) (fill (type background))))
      (symbol "TP4056_1_1"
        (pin input line (at -7.62 6.35 0) (length 2.54)
          (name "PROG" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin power_in line (at 7.62 3.81 180) (length 2.54)
          (name "GND" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
        (pin power_in line (at -7.62 3.81 0) (length 2.54)
          (name "VIN" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
        (pin power_in line (at -7.62 1.27 0) (length 2.54)
          (name "VIN" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))
        (pin power_out line (at 7.62 6.35 180) (length 2.54)
          (name "BAT" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))
        (pin open_collector line (at 7.62 1.27 180) (length 2.54)
          (name "CHRG" (effects (font (size 1.27 1.27)))) (number "6" (effects (font (size 1.27 1.27)))))
        (pin open_collector line (at 7.62 -1.27 180) (length 2.54)
          (name "STDBY" (effects (font (size 1.27 1.27)))) (number "7" (effects (font (size 1.27 1.27)))))
        (pin power_in line (at -7.62 -6.35 0) (length 2.54)
          (name "VIN" (effects (font (size 1.27 1.27)))) (number "8" (effects (font (size 1.27 1.27)))))))"""

def sym_mp2307():
    return """\
    (symbol "SurfTrak:MP2307DN"
      (pin_names (offset 1.016))
      (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 9.525 0) (effects (font (size 1.27 1.27))))
      (property "Value" "MP2307DN" (at 0 -9.525 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "MP2307DN_0_1"
        (rectangle (start -5.08 -8.89) (end 5.08 8.89)
          (stroke (width 0.254) (type default)) (fill (type background))))
      (symbol "MP2307DN_1_1"
        (pin input line (at -7.62 6.35 0) (length 2.54)
          (name "SS" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin input line (at -7.62 3.81 0) (length 2.54)
          (name "EN" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
        (pin output line (at 7.62 3.81 180) (length 2.54)
          (name "SW" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
        (pin input line (at -7.62 1.27 0) (length 2.54)
          (name "FB" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))
        (pin power_in line (at 7.62 6.35 180) (length 2.54)
          (name "IN" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))
        (pin power_in line (at 7.62 1.27 180) (length 2.54)
          (name "IN" (effects (font (size 1.27 1.27)))) (number "6" (effects (font (size 1.27 1.27)))))
        (pin power_in line (at -7.62 -6.35 0) (length 2.54)
          (name "GND" (effects (font (size 1.27 1.27)))) (number "7" (effects (font (size 1.27 1.27)))))
        (pin input line (at 7.62 -3.81 180) (length 2.54)
          (name "BST" (effects (font (size 1.27 1.27)))) (number "8" (effects (font (size 1.27 1.27)))))))"""

def sym_ws2812b():
    return """\
    (symbol "SurfTrak:WS2812B"
      (pin_names (offset 1.016))
      (in_bom yes) (on_board yes)
      (property "Reference" "LED" (at 0 6.35 0) (effects (font (size 1.27 1.27))))
      (property "Value" "WS2812B" (at 0 -6.35 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "LED_SMD:LED_WS2812B_PLCC4_5.0x5.0mm_P3.2mm" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "WS2812B_0_1"
        (rectangle (start -3.81 -5.08) (end 3.81 5.08)
          (stroke (width 0.254) (type default)) (fill (type background))))
      (symbol "WS2812B_1_1"
        (pin power_in line (at -6.35 3.81 0) (length 2.54)
          (name "VDD" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin output line (at 6.35 1.27 180) (length 2.54)
          (name "DOUT" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
        (pin power_in line (at -6.35 -1.27 0) (length 2.54)
          (name "VSS" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
        (pin input line (at -6.35 1.27 0) (length 2.54)
          (name "DIN" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))))"""

# ---------------------------------------------------------------------------
# Schematic element generators
# ---------------------------------------------------------------------------

def fmt_xy(x, y):
    return f"{x:.4f} {y:.4f}"

def power_symbol(net, x, y, rotation=0, pwr_id=None):
    """Emit a power symbol (GND or named rail) at x,y."""
    pid = pwr_id or uid()
    # Map net names to standard KiCad power symbols
    kicad_power = {"GND": "power:GND", "5V": "power:+5V", "3V3": "power:+3.3V"}
    lib = kicad_power.get(net, f"power:{net}")
    pwrref_id = uid()
    return f"""
  (power_symbol (lib_id "{lib}") (at {fmt_xy(x,y)} {rotation}) (unit 1)
    (in_bom no) (on_board no) (uuid "{pid}")
    (property "Reference" "#PWR" (at {fmt_xy(x, y+3)} 0) (effects (font (size 1.27 1.27)) hide))
    (property "Value" "{net}" (at {fmt_xy(x, y+2)} 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "{pwrref_id}")))"""

def global_label(net, x, y, shape="bidirectional", rotation=0):
    glid = uid()
    prop_id = uid()
    return f"""
  (global_label "{net}" (shape {shape}) (at {fmt_xy(x,y)} {rotation})
    (effects (font (size 1.27 1.27)))
    (uuid "{glid}")
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {fmt_xy(x+5,y)} 0)
      (effects (font (size 1.27 1.27)) hide)))"""

def wire(x1, y1, x2, y2):
    wid = uid()
    return f"""
  (wire (pts (xy {fmt_xy(x1,y1)}) (xy {fmt_xy(x2,y2)}))
    (stroke (width 0) (type default)) (uuid "{wid}"))"""

def component(ref, value, lib_id, footprint, lcsc, x, y, rotation=0):
    """Emit a symbol instance. Pins connected via global labels placed nearby."""
    cid = uid()
    ref_id = uid()
    val_id = uid()
    fp_id  = uid()
    ds_id  = uid()
    lc_id  = uid()
    # Offset reference and value labels
    rx, ry = x + 2, y - 1.5
    vx, vy = x + 2, y + 1.5
    return f"""
  (symbol (lib_id "{lib_id}") (at {fmt_xy(x,y)} {rotation}) (unit 1)
    (in_bom yes) (on_board yes) (fields_autoplaced yes)
    (uuid "{cid}")
    (property "Reference" "{ref}" (at {fmt_xy(rx,ry)} 0)
      (effects (font (size 1.27 1.27))))
    (property "Value" "{value}" (at {fmt_xy(vx,vy)} 0)
      (effects (font (size 1.27 1.27))))
    (property "Footprint" "{footprint}" (at {fmt_xy(x,y)} 0)
      (effects (font (size 1.27 1.27)) hide))
    (property "Datasheet" "~" (at {fmt_xy(x,y)} 0)
      (effects (font (size 1.27 1.27)) hide))
    (property "LCSC" "{lcsc}" (at {fmt_xy(x,y)} 0)
      (effects (font (size 1.27 1.27)) hide)))"""

def no_connect(x, y):
    ncid = uid()
    return f"""
  (no_connect (at {fmt_xy(x,y)}) (uuid "{ncid}"))"""

# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def generate():
    lines = []

    lines.append('(kicad_sch')
    lines.append('  (version 20231120)')
    lines.append('  (generator "surftrak_generate_schematic")')
    lines.append('  (generator_version "1.0")')
    lines.append('  (paper "A1")')
    lines.append('  (title_block')
    lines.append('    (title "SurfTrak Carrier PCB")')
    lines.append('    (date "2026-04-14")')
    lines.append('    (rev "v1.0")')
    lines.append('    (company "SurfTrak")')
    lines.append('    (comment 1 "88mm circular, JLCPCB 2-layer 1.6mm FR4")')
    lines.append('    (comment 2 "WS2812B (LED1) HAND SOLDER ONLY - exclude from PCBA")')
    lines.append('  )')

    # ── lib_symbols ──────────────────────────────────────────────────────────
    lines.append('  (lib_symbols')
    lines.append(sym_tp4056())
    lines.append(sym_mp2307())
    lines.append(sym_ws2812b())
    lines.append('  )')

    # ── Component instances ───────────────────────────────────────────────────
    for comp in COMPONENTS:
        lines.append(component(
            comp["ref"], comp["value"], comp["lib_id"],
            comp["footprint"], comp.get("lcsc",""), comp["x"], comp["y"]))

    # ── Global labels at every named pin ─────────────────────────────────────
    # We emit a global_label for every net that is not GND/5V/3V3 (those get
    # power symbols).  Each label is placed offset from the component position
    # so it doesn't stack.  The offset is approximate — adjust in KiCad GUI.
    POWER_NETS = {"GND", "5V", "3V3"}
    gl_offset = 8   # mm offset from component center for label placement

    label_positions = {}   # net -> (x,y) of first occurrence, for dedup display

    for comp in COMPONENTS:
        cx, cy = comp["x"], comp["y"]
        for i, (pin_num, net) in enumerate(comp["pins"].items()):
            if not net or net.startswith("NC"):
                lines.append(no_connect(cx + gl_offset, cy + i * 2.54))
                continue
            if net in POWER_NETS:
                lines.append(power_symbol(net, cx + gl_offset + 2, cy + i * 2.54))
            else:
                lx = cx + gl_offset
                ly = cy + i * 2.54 - (len(comp["pins"]) * 2.54 / 2)
                lines.append(global_label(net, lx, ly))

    # ── Power flags (suppresses ERC warnings) ────────────────────────────────
    for net, x, y in [
        ("GND",   10, 10), ("5V",    20, 10), ("3V3",  30, 10),
        ("BATT_SW", 40, 10), ("BAT+", 50, 10), ("VBUS", 60, 10),
    ]:
        lines.append(power_symbol(net, x, y))

    # ── Sheet instances ───────────────────────────────────────────────────────
    lines.append('  (sheet_instances')
    lines.append('    (path "/" (page "1"))')
    lines.append('  )')

    lines.append(')')
    return "\n".join(lines)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    out_path = os.path.join(os.path.dirname(__file__), "surftrak_carrier.kicad_sch")
    content = generate()
    with open(out_path, "w") as f:
        f.write(content)
    print(f"Written: {out_path}")
    print()
    print("Next steps:")
    print("  1. pip install kicad-skip   # optional validator")
    print("  2. Open surftrak_carrier.kicad_sch in KiCad 7 or 8")
    print("  3. Tools > Update Symbols from Library  (resolves Device:R, Connector_Generic:*, etc.)")
    print("  4. Run ERC — fix any pin-unconnected warnings by wiring pins in KiCad GUI")
    print("  5. Assign footprints: Tools > Assign Footprints")
    print("  6. File > Export > Netlist, then open KiCad PCB editor")
    print("  7. Tools > Update PCB from Schematic")
    print("  8. Place footprints per docs/PCB_LAYOUT_GUIDE.md")
    print("  9. Route traces, add GND copper pour, run DRC")
    print(" 10. File > Fabrication Outputs > Gerbers + Drill Files")
