# A plain repeated 7 nm wire at the ET-SoC-1's mesh voltage: first-principles estimate

All values here are estimates; `wire_calc.py` in this folder does the arithmetic. (An earlier copy of this file was,
by mistake, OpenROAD's "Parasitics estimation" manual page; this replaces it.)

| Quantity | Value | Basis |
|---|---|---|
| Heat per transition, either direction | ½CV² | Half of the CV² drawn on a 0→1 transition is dissipated then, half on the following 1→0 |
| Total switched C of a repeated 7 nm wire | 200–400 fF/mm, central 300 | ASAP7 0.166 fF/µm × 1.34 (EDP-optimal repeaters, Ho 2003) = 222, up to 0.2 fF/µm × 1.87 (delay-optimal) = 374; on top metal (ASAP7 M8/M9, 0.093–0.104 fF/µm) as low as about 125 |
| Mesh voltage | 0.485 V, V² = 0.2352 V² | telemetry `reg_mv.noc` 485, `die_mv.noc` 484 |
| Per transition·mm (½CV²) | 35 fJ (24–47) | 0.5 × 300 fF × 0.2352 V² |
| Per random bit·mm (half the bits change: CV²/4) | 17.6 fJ (12–24) | the range used on the page |
| Per transition per 3.72 mm hop, wire only | 131 fJ (88–175) | |
| The same wire at 0.9 V, per random bit·mm | 41–81 fJ | × (0.9/0.485)² = 3.44 |
| Keckler 2011 (40 nm, 0.9 V) moved to 0.485 V | 69.7 fJ per transition·mm; 35.1 per random bit·mm | 240 × 0.290; 121 × 0.290 |

Constant-capacitance V² scaling assumes full-swing CMOS. For low-swing links the energy goes as V_supply × V_swing,
and gate capacitance is somewhat lower near threshold. Sources: ASAP7 predictive PDK (`asap7_ao_tt.lib`, the Harris
ASAP7 notes), Ho's 2003 thesis Table 4.2, Keckler et al. IEEE Micro 2011 Table 1; see `../SYNTHESIS.md` §1e–1f.
