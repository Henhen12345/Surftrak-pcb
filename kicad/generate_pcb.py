#!/usr/bin/env python3
"""
SurfTrak Carrier PCB — KiCad PCB Template Generator
Generates surftrak_carrier.kicad_pcb with:
  - 88mm circular board outline on Edge.Cuts
  - JLCPCB 2-layer design rules
  - GND copper pour zones on F.Cu and B.Cu
  - Net class rules

Usage:
    python3 generate_pcb.py

After opening surftrak_carrier.kicad_pcb in KiCad:
  1. Tools > Update PCB from Schematic  (imports footprints from kicad_sch)
  2. Place footprints per docs/PCB_LAYOUT_GUIDE.md
  3. Route traces
  4. Run DRC
  5. File > Fabrication Outputs > Gerbers + Drill Files
"""

import math
import uuid as _uuid
import os

_uid_n = [1]
def uid():
    u = f"aabbccdd-0000-4000-8000-{_uid_n[0]:012d}"
    _uid_n[0] += 1
    return u

# Board parameters
CX, CY = 100.0, 80.0   # board center (mm)
R_BOARD = 44.0          # board radius (mm)
R_ZONE  = 43.0          # GND pour radius (1mm inside edge)

def circle_pts(cx, cy, r, n=72):
    """Return n points on a circle as KiCad (xy ...) strings."""
    pts = []
    for i in range(n):
        angle = 2 * math.pi * i / n
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        pts.append(f"      (xy {x:.4f} {y:.4f})")
    return "\n".join(pts)

def generate():
    lines = []

    lines.append("(kicad_pcb")
    lines.append("  (version 20231120)")
    lines.append('  (generator "surftrak_generate_pcb")')
    lines.append('  (generator_version "1.0")')
    lines.append("")
    lines.append("  (general")
    lines.append("    (thickness 1.6)")
    lines.append("    (legacy_teardrops no)")
    lines.append("  )")
    lines.append("")
    lines.append('  (paper "A1")')
    lines.append("")

    # ── Title block ──────────────────────────────────────────────────────────
    lines.append("  (title_block")
    lines.append('    (title "SurfTrak Carrier PCB")')
    lines.append('    (date "2026-04-14")')
    lines.append('    (rev "v1.0")')
    lines.append('    (company "SurfTrak")')
    lines.append('    (comment 1 "88mm circular, JLCPCB 2-layer 1.6mm FR4")')
    lines.append("  )")
    lines.append("")

    # ── Layers ───────────────────────────────────────────────────────────────
    lines.append("  (layers")
    for num, name, typ in [
        (0,  "F.Cu",          "signal"),
        (31, "B.Cu",          "signal"),
        (32, "B.Adhes",       "user \"B.Adhesive\""),
        (33, "F.Adhes",       "user \"F.Adhesive\""),
        (34, "B.Paste",       "user"),
        (35, "F.Paste",       "user"),
        (36, "B.SilkS",       "user \"B.Silkscreen\""),
        (37, "F.SilkS",       "user \"F.Silkscreen\""),
        (38, "B.Mask",        "user"),
        (39, "F.Mask",        "user"),
        (40, "Dwgs.User",     "user \"User.Drawings\""),
        (41, "Cmts.User",     "user \"User.Comments\""),
        (42, "Eco1.User",     "user \"User.Eco1\""),
        (43, "Eco2.User",     "user \"User.Eco2\""),
        (44, "Edge.Cuts",     "user"),
        (45, "Margin",        "user"),
        (46, "B.CrtYd",       "user \"B.Courtyard\""),
        (47, "F.CrtYd",       "user \"F.Courtyard\""),
        (48, "B.Fab",         "user \"B.Fabrication\""),
        (49, "F.Fab",         "user \"F.Fabrication\""),
    ]:
        lines.append(f'    ({num} "{name}" {typ})')
    lines.append("  )")
    lines.append("")

    # ── Setup / design rules ─────────────────────────────────────────────────
    lines.append("  (setup")
    lines.append("    (pad_to_mask_clearance 0)")
    lines.append("    (allow_soldermask_bridges_in_footprints no)")
    lines.append("    (pcbplotparams")
    lines.append("      (layerselection 0x00010fc_ffffffff)")
    lines.append("      (plot_on_all_layers_selection 0x0000000_00000000)")
    lines.append("      (disableapertmacros no)")
    lines.append("      (usegerberextensions no)")
    lines.append("      (usegerberattributes yes)")
    lines.append("      (usegerberadvancedattributes yes)")
    lines.append("      (creategerberjobfile yes)")
    lines.append("      (dashed_line_dash_ratio 12.0)")
    lines.append("      (dashed_line_gap_ratio 3.0)")
    lines.append("      (svgprecision 4)")
    lines.append("      (plotframeref no)")
    lines.append("      (viasonmask no)")
    lines.append("      (mode 1)")
    lines.append("      (useauxorigin no)")
    lines.append("      (hpglpennumber 1)")
    lines.append("      (hpglpenspeed 20)")
    lines.append("      (hpglpendiameter 15.0)")
    lines.append("      (dxfpolygonmode yes)")
    lines.append("      (dxfimperialunits yes)")
    lines.append("      (dxfusepcbnewfont yes)")
    lines.append("      (psnegative no)")
    lines.append("      (psa4output no)")
    lines.append("      (plotreference yes)")
    lines.append("      (plotvalue no)")
    lines.append("      (plotfptext yes)")
    lines.append("      (plotinvisibletext no)")
    lines.append("      (sketchpadsonfab no)")
    lines.append("      (subtractmaskfromsilk yes)")
    lines.append("      (outputformat 1)")
    lines.append("      (mirror no)")
    lines.append("      (drillshape 1)")
    lines.append("      (scaleselection 1)")
    lines.append('      (outputdirectory "../gerbers/")')
    lines.append("    )")
    lines.append("  )")
    lines.append("")

    # ── Nets ─────────────────────────────────────────────────────────────────
    nets = [
        "", "GND", "+5V", "+3V3", "BATT_SW", "BAT+", "VBUS",
        "UART_TX", "UART_RX", "STEP", "DIR", "TMC_EN",
        "SPI_MOSI", "SPI_MISO", "SPI_SCK", "UWB1_CS", "UWB2_CS",
        "LED_DATA", "MOT_A1", "MOT_A2", "MOT_B1", "MOT_B2",
        "SW1", "SW2", "FB1", "FB2", "GATE_NODE", "BATT_PRE_Q1",
    ]
    for i, net in enumerate(nets):
        lines.append(f'  (net {i} "{net}")')
    lines.append("")

    # ── Net classes ──────────────────────────────────────────────────────────
    lines.append("  (net_class \"Default\" \"Standard signal traces\"")
    lines.append("    (clearance 0.2)")
    lines.append("    (trace_width 0.25)")
    lines.append("    (diff_pair_width 0.25)")
    lines.append("    (diff_pair_gap 0.25)")
    lines.append("    (via_drill 0.4)")
    lines.append("    (via_dia 0.8)")
    lines.append("    (uvia_drill 0.1)")
    lines.append("    (uvia_dia 0.3)")
    lines.append("  )")
    lines.append("")
    lines.append("  (net_class \"Power\" \"Power rails — wider traces\"")
    lines.append("    (clearance 0.2)")
    lines.append("    (trace_width 0.8)")
    lines.append("    (diff_pair_width 0.8)")
    lines.append("    (diff_pair_gap 0.2)")
    lines.append("    (via_drill 0.4)")
    lines.append("    (via_dia 0.8)")
    lines.append("    (uvia_drill 0.1)")
    lines.append("    (uvia_dia 0.3)")
    lines.append('    (add_net "GND")')
    lines.append('    (add_net "+5V")')
    lines.append('    (add_net "+3V3")')
    lines.append('    (add_net "BATT_SW")')
    lines.append('    (add_net "BAT+")')
    lines.append('    (add_net "VBUS")')
    lines.append("  )")
    lines.append("")
    lines.append("  (net_class \"Motor\" \"Motor output traces — 1mm minimum\"")
    lines.append("    (clearance 0.3)")
    lines.append("    (trace_width 1.0)")
    lines.append("    (diff_pair_width 1.0)")
    lines.append("    (diff_pair_gap 0.3)")
    lines.append("    (via_drill 0.4)")
    lines.append("    (via_dia 0.8)")
    lines.append("    (uvia_drill 0.1)")
    lines.append("    (uvia_dia 0.3)")
    lines.append('    (add_net "MOT_A1")')
    lines.append('    (add_net "MOT_A2")')
    lines.append('    (add_net "MOT_B1")')
    lines.append('    (add_net "MOT_B2")')
    lines.append("  )")
    lines.append("")

    # ── Board outline: 88mm diameter circle ──────────────────────────────────
    outline_id = uid()
    lines.append(f'  (gr_circle (center {CX} {CY}) (end {CX + R_BOARD} {CY})')
    lines.append(f'    (stroke (width 0.05) (type solid)) (layer "Edge.Cuts")')
    lines.append(f'    (uuid "{outline_id}"))')
    lines.append("")

    # ── Board center cross-hair (Dwgs layer, for reference) ───────────────────
    for dx, dy, ex, ey in [
        (CX-3, CY, CX+3, CY),
        (CX, CY-3, CX, CY+3),
    ]:
        chid = uid()
        lines.append(f'  (gr_line (start {dx} {dy}) (end {ex} {ey})')
        lines.append(f'    (stroke (width 0.1) (type dash)) (layer "Dwgs.User")')
        lines.append(f'    (uuid "{chid}"))')
    lines.append("")

    # ── Dimension annotation: 88mm diameter ───────────────────────────────────
    lines.append(f'  (gr_text "88mm DIA" (at {CX} {CY + R_BOARD + 3}) (layer "F.SilkS")')
    lines.append(f'    (effects (font (size 1.5 1.5) (thickness 0.2))))')
    lines.append("")

    # ── Component placement zone annotations (Dwgs.User) ─────────────────────
    # These are text notes on the drawing layer to guide footprint placement.
    notes = [
        # (x,   y,    text)
        (70,   68,   "U1 TP4056"),
        (58,   78,   "U2 MP2307 5V"),
        (58,   88,   "U3 MP2307 3V3"),
        (70,   78,   "Q1 AO3401A"),
        (100,  80,   "J1 Pi Zero 2W  65x30mm"),
        (100,  110,  "J2A J2B TMC2209"),
        (118,  110,  "J7 Motor"),
        (130,  68,   "J8 UWB1"),
        (130,  78,   "J9 UWB2"),
        (130,  88,   "J6+LED1"),
        (130,  98,   "J10 FPC"),
        (72,   52,   "J3 Bat"),
        (82,   52,   "J4 USB"),
        (92,   52,   "J5 Btn"),
    ]
    for nx, ny, txt in notes:
        nid = uid()
        lines.append(f'  (gr_text "{txt}" (at {nx} {ny}) (layer "Dwgs.User")')
        lines.append(f'    (effects (font (size 1.0 1.0) (thickness 0.15))))')
    lines.append("")

    # ── GND copper pour — F.Cu ───────────────────────────────────────────────
    zone_f_id = uid()
    lines.append(f'  (zone (net 1) (net_name "GND") (layer "F.Cu") (uuid "{zone_f_id}")')
    lines.append(f'    (hatch edge 0.508)')
    lines.append(f'    (priority 0)')
    lines.append(f'    (connect_pads (clearance 0.2))')
    lines.append(f'    (min_thickness 0.25)')
    lines.append(f'    (filled_areas_thickness no)')
    lines.append(f'    (fill yes (thermal_gap 0.5) (thermal_bridge_width 0.25))')
    lines.append(f'    (polygon (pts')
    lines.append(circle_pts(CX, CY, R_ZONE))
    lines.append(f'    ))')
    lines.append(f'  )')
    lines.append("")

    # ── GND copper pour — B.Cu ───────────────────────────────────────────────
    zone_b_id = uid()
    lines.append(f'  (zone (net 1) (net_name "GND") (layer "B.Cu") (uuid "{zone_b_id}")')
    lines.append(f'    (hatch edge 0.508)')
    lines.append(f'    (priority 0)')
    lines.append(f'    (connect_pads (clearance 0.2))')
    lines.append(f'    (min_thickness 0.25)')
    lines.append(f'    (filled_areas_thickness no)')
    lines.append(f'    (fill yes (thermal_gap 0.5) (thermal_bridge_width 0.25))')
    lines.append(f'    (polygon (pts')
    lines.append(circle_pts(CX, CY, R_ZONE))
    lines.append(f'    ))')
    lines.append(f'  )')
    lines.append("")

    lines.append(")")
    # Filter out None from accidental append()
    return "\n".join(str(l) for l in lines if l is not None)

if __name__ == "__main__":
    out_path = os.path.join(os.path.dirname(__file__), "surftrak_carrier.kicad_pcb")
    content = generate()
    with open(out_path, "w") as f:
        f.write(content)
    print(f"Written: {out_path}")
    print()
    print("Next steps:")
    print("  1. Open KiCad, open surftrak_carrier.kicad_sch")
    print("  2. Tools > Update PCB from Schematic → opens surftrak_carrier.kicad_pcb")
    print("     (or open the .kicad_pcb directly and do Tools > Update PCB from Schematic)")
    print("  3. Footprints appear as a pile — place them per docs/PCB_LAYOUT_GUIDE.md")
    print("  4. Route traces: Interactive Router (X key)")
    print("  5. Zone fills: B key to fill GND pours")
    print("  6. DRC: Inspect > Design Rules Checker")
    print("  7. Gerbers: File > Fabrication Outputs > Gerbers")
    print("              File > Fabrication Outputs > Drill Files")
    print("              File > Fabrication Outputs > Component Placement (CPL for PCBA)")
    print("  8. Upload to jlcpcb.com")
