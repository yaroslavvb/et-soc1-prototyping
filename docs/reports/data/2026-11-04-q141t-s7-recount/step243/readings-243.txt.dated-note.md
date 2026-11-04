# Dated note beside step243/readings-243.txt (Wed 4 Nov 2026, about 14:55 PST; Q141(t2)'s fix pass)

*`readings-243.txt` and `readings-243.json` (`5e1bb309`) stay as committed.*

- **Line 19 (G4 aifoundry1c1)** prints the 243-point k as −0.150.
  - [`readings-243.json`](readings-243.json) holds −0.1505 (`G4_arm_b20_pi.aifoundry1c1.k243_w`), and the unrounded value is
    −0.15052. `readings_243.py` rounds to 4 decimals and then prints 3.
  - Quote **−0.1505 ± 0.053 W** (−0.151 at 3 decimals).
- **The same line's "−0.299 ± 0.190 at 27 (frozen)"** copies the frozen arm. [`../arm-s7.json`](../arm-s7.json) holds `k_w` −0.2995,
  and the unrounded value is −0.29953. Quote −0.2995.
- **Every other figure in the file** rounds once to what it prints, from an unrounded value or from a frozen file's own figure.
- The detail is in [`README.md.dated-note.md`](README.md.dated-note.md).
