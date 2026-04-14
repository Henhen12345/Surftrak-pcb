# SurfTrak Carrier PCB — Design Decisions and Rationale

## Power Architecture Decisions

### Why two separate MP2307 converters instead of one?
- Isolates 5V loads (Pi Zero 2W, WS2812B, TMC2209 logic) from 3.3V loads (UWB modules)
- UWB DWM3000 is sensitive to supply noise from switching regulators
- Allows independent enable/disable of each rail in software
- Separate output capacitors improve transient response for each domain

### Why MP2307 instead of TPS54xxx or LM2596?
- MP2307 is JLCPCB basic part (lower cost, always in stock)
- 23V input range handles fully charged LiPo (4.2V) with margin
- 3A output handles Pi Zero 2W peak (750mA) + LED (350mA) + TMC2209 logic (50mA) with headroom
- SOP-8 package is easy to hand-rework if needed

### Output Voltage Accuracy
- 5V rail: R1=100kΩ, R2=22.6kΩ → Vout = 0.925 × (1 + 100/22.6) = **5.02V** ✓
- 3.3V rail: R3=68kΩ, R4=27.4kΩ → Vout = 0.925 × (1 + 68/27.4) = **3.22V**
  - 3.22V is within ±5% of 3.3V and within DWM3000 VCC tolerance (1.71V–3.6V)
  - If tighter regulation is required, change R4 to 26.7kΩ for 3.30V

### Why SS24 and not SS34 or B5819W?
- SS24 (2A, 40V) provides adequate reverse voltage margin above BATT_SW
- DO-214AA (SMB) package handles the continuous diode current without thermal issues
- SS24 is a JLCPCB basic part (C8598)

### Battery Input Protection (D3)
- D3 placed in series on BAT+ from J3 to prevent reverse polarity damage
- Vf ≈ 0.4V at 1A — acceptable drop from 3.7V LiPo
- Alternative: use a P-channel MOSFET for near-zero Vf drop if efficiency is critical

### Charge Current Setting
- R5 = 1.2kΩ → Ichg = 1000/1.2 = **833mA**
- Most LiPo packs for this application are 1000–2000mAh
- 833mA = ~0.83C for 1000mAh pack — safe and within TP4056 limit
- For larger packs (2000mAh), consider R5=0.5kΩ for 2000mA — but TP4056 max is 1000mA
  - TP4056 max charge current is 1A; R5 minimum is 1kΩ

## Power Switch Design

### Why P-channel MOSFET instead of a dedicated power path IC?
- Simpler BOM, lower cost
- AO3401A (SOT-23) handles 4A continuous — well above system consumption
- Trade-off: non-latching by default; a maintained rocker switch at J5 solves this for v1

### Power-on Default State
- Q1 gate pulled HIGH by R6 (10kΩ) → MOSFET OFF by default (safe for battery)
- Pressing J5 (connected to gate) pulls gate LOW → MOSFET turns ON
- A maintained (latching) switch at J5 keeps the gate LOW continuously while on

### Future Improvement (v2)
Consider adding TPS27082L (load switch with enable input) or a dedicated power button IC
with soft-start and load detection for a latching press-to-on / long-press-to-off behavior.

## Pi Zero 2W Mounting

### Why castellated pads instead of pin headers?
- Lower profile — Pi sits flush on the carrier board without standoffs
- More mechanically stable inside a rotating camera housing
- Castellated solder joints are SMT-compatible (can be PCBA'd in theory)
- Trade-off: no easy disconnect; Pi and carrier are semi-permanently joined

### Power Delivery to Pi
- Pi is powered via castellated pads on 5V pins (pin 2 and pin 4)
- DO NOT power both pin 1 (3.3V) from the carrier and pin 2 (5V) simultaneously
- Pin 1/17 (3.3V) outputs from the Pi's own regulator — do not back-drive from carrier 3V3
- Only supply 5V on pins 2 and 4

## TMC2209 Integration

### Why through-hole headers instead of soldering TMC2209 directly?
- Allows swapping TMC2209 modules in the field without reflowing carrier board
- Easier to tune VREF for different stepper motor current requirements
- Module includes onboard protection circuitry that would add cost/complexity on carrier

### UART Mode vs Step/Dir Only
- PDN_UART (single-wire UART) used for advanced tuning (StealthChop, microstepping, diagnostics)
- Step/Dir used for motion commands (simpler, deterministic)
- This hybrid approach gives full configurability while keeping motion code simple

### Motor Supply (VM) from Battery
- TMC2209 VM accepts 4.75V–29V
- LiPo at 3.7–4.2V is technically at the lower edge of the TMC2209 VM range
- **Resolution**: Many LiPo cells with high-C discharge hold 4.0V+ under load
- If motor performance is insufficient, add a 2S configuration or a boost converter to VM
- Alternatively, feed VM from the 5V rail (U2 output) — 5V is within TMC2209 VM spec

## UWB Module Connectivity

### Why shared SPI bus?
- DWM3000 supports SPI up to 20MHz
- Both modules share MOSI/MISO/SCK; chip-selects (CS) are independent
- Total data rate per module is low (ranging packets); no bus contention issues
- Reduces Pi GPIO consumption

### 3.3V Supply for UWB
- DWM3000 VCC: 1.71V – 3.6V (from datasheet)
- 3.22V output from U3 is within spec
- Add 100nF bypass caps C11, C12 at each JST connector — critical for UWB stability

## Camera (Arducam IMX519) Connection

### Why FPC connector on carrier board?
- Provides a strain-relief anchor point for the camera cable
- Camera cable terminates at the carrier board rather than routing freely inside the housing
- Reduces stress on the Pi's mini-CSI connector during mechanical vibration

### CSI Signal Routing
- CSI-2 differential pairs (D0N/D0P, D1N/D1P, CLN/CLP) are NOT routed on the carrier board
- Pi Zero 2W's 22-pin mini-CSI connector accepts a direct flat flex cable from camera
- The carrier board FPC (J10) is electrically isolated from Pi CSI in this design
- Use: Arducam 22-to-15-pin adapter cable from Pi mini-CSI to camera module directly
- J10 is a physical mount point only, or populate only if routing through carrier is required

## WS2812B LED

### Why on-board LED AND external JST?
- On-board LED1 for system status indication
- J6 provides expansion for an external LED strip if needed
- Both share GPIO18; avoid driving simultaneously without buffering

### Hand Solder Only
- WS2812B (C52917433) must be excluded from JLCPCB PCBA
- Reason: JLCPCB PCBA often has issues with WS2812B orientation and reflow sensitivity
- Hand solder after board arrives; test with 1kHz PWM on GPIO18 before full integration

## Design Rule Compliance Notes

### JLCPCB 2-Layer Standard Constraints
- Copper-to-edge: minimum 0.3mm (we use 2mm for safety)
- Drill-to-edge: minimum 0.4mm
- Via-to-via (drill-to-drill): minimum 0.5mm
- Silkscreen-to-pad: minimum 0.1mm
- Minimum soldermask-defined pad: not recommended (use copper-defined pads)

### EMC Considerations
- Switching node (MP2307 SW, inductor, diode triangle): minimize loop area
- Pour GND under switching section on bottom layer
- UART and SPI traces: route away from power section
- Add ferrite bead on 3V3 before UWB connectors if EMI is a concern (footprint only, 0Ω default)
