# Gerber Export Instructions for JLCPCB

## Prerequisites
- PCB DRC passes with 0 errors
- All components have correct footprints assigned
- Board outline is exactly 88.0mm circle on BoardOutline layer
- GND copper pour added to both layers

---

## Step 1 — Run Final DRC

In EasyEDA Standard:
1. Design → Design Rule Check
2. Resolve all errors before continuing
3. Verify Ratsnest shows 0 unconnected nets

---

## Step 2 — Export Gerbers

1. Fabrication → Generate Gerber
2. In the Gerber export dialog, ensure all layers are checked:
   - **TopCopper** (GTL)
   - **BottomCopper** (GBL)
   - **TopSolderMask** (GTS)
   - **BottomSolderMask** (GBS)
   - **TopSilkscreen** (GTO)
   - **BottomSilkscreen** (GBO)
   - **TopPaste** (GTP) — needed for PCBA stencil
   - **BoardOutline** (GKO)
   - **DrillFile** (DRL / TXT)
3. Click **Generate** — EasyEDA downloads a `.zip` file

---

## Step 3 — Export BOM and CPL for PCBA

### BOM (Bill of Materials)
1. Fabrication → BOM
2. Export as CSV
3. Verify LCSC part numbers match `BOM/BOM.csv`
4. **Remove WS2812B (LED1) from the PCBA BOM** — it must be hand-soldered

### CPL (Component Placement List)
1. Fabrication → Pick and Place File
2. Export as CSV
3. This is the centroid file JLCPCB needs for PCBA placement

---

## Step 4 — Upload to JLCPCB

### PCB Order
1. Go to jlcpcb.com → Order Now
2. Upload the Gerber `.zip`
3. Settings:
   - **Layers:** 2
   - **Dimensions:** will auto-detect from Gerbers (verify 88×88mm)
   - **PCB Thickness:** 1.6mm
   - **Surface Finish:** HASL(with lead) or LeadFree HASL
   - **Copper Weight:** 1oz
   - **Min Hole Size:** 0.3mm
   - **Solder Mask:** Green (or preference)
   - **Silkscreen:** White
   - **Edge connector / Castellated holes:** YES — required for Pi Zero 2W pads
     - Select "Castellated Holes: Yes" when prompted
   - **Remove order number:** specify location in silkscreen or pay extra

### PCBA Add-on
1. After PCB settings, enable **SMT Assembly**
2. Select **Top Side only** (all SMD components are on top)
3. Upload BOM CSV (with WS2812B removed)
4. Upload CPL CSV
5. Match each BOM line to a confirmed LCSC part
6. Confirm component placement preview
7. Add to cart

---

## Step 5 — Pre-submission Gerber Verification

Before uploading, verify your Gerbers using a free viewer:

- **JLCPCB Gerber Viewer** (built into upload flow)
- **gerbv** (open source, offline)
- **Tracespace** at tracespace.io/view

Check:
- [ ] Board outline is a clean 88mm circle, no gaps
- [ ] All pads visible on copper layers
- [ ] Silkscreen text readable and not overlapping pads
- [ ] Drill hits are centered on pads
- [ ] Castellated holes on Pi Zero 2W edge appear as half-holes on board edge
- [ ] No copper within 0.3mm of board edge (except castellated pads by design)

---

## Castellated Holes Note (Pi Zero 2W)

JLCPCB requires you to explicitly enable castellated holes if any pads fall on the board edge.
- The Pi Zero 2W footprint has 40 castellated edge pads
- These are on the **interior** of the board (not the board perimeter), so no special castellated option is needed for this specific design
- Standard PCB fabrication handles interior through-hole pads normally
- Only check "Castellated Holes: Yes" if any Pi pads actually fall on the 88mm board outline circle

---

## Drill File Settings

EasyEDA exports drill files in Excellon format.
JLCPCB accepts:
- Excellon `.drl` or `.txt`
- Units: mm or inches (either works)
- Format: 2.4 or 2.5 (EasyEDA default is fine)

---

## Hand-Soldering After Assembly

After PCBA boards arrive:
1. **LED1 (WS2812B)** — solder manually, pad 1 (GND) is marked on silkscreen
   - Use a temperature-controlled iron at 280°C max
   - Pre-heat pad, solder quickly, avoid prolonged heat
   - Test with 5V / GPIO18 PWM signal before final assembly

2. **Pi Zero 2W** — align castellated pads to carrier board, solder all 40 pads
   - Recommend solder paste + hot air for best results
   - Verify 5V on pins 2 & 4, GND on pins 6/9/14/20/25/30/34/39

3. **TMC2209 module** — press into J2 socket headers, verify orientation
