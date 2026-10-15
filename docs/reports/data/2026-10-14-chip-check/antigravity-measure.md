# Text past a frame or the screen, and texts whose ink meets: before and after the Antigravity fixes

Made by `tools/antigravity/compare.py` from `measure.mjs` runs over all 104 scales of the chip diagram (headless Chrome, reduced motion, the scale at rest, Noto Sans):
before is the build of `814d519c` (the morning's check, measured by the topic 4 checker), after is this commit's build. `over` lists a text past the frame's border (fr right, fl left, fb bottom) or past the visible area (vr, vl, vb, vt), in CSS pixels; `pair` lists two texts whose ink boxes meet (width x height of the overlap, in CSS pixels).
The labels that stay past the frame on the I/O, PCIe and memory shires are their links to the neighbouring cells, set round the frame on purpose (`cellLinks`). The 29th Street pair is two rotated street names whose boxes, not their ink, meet; on a phone the street's two end names graze the view's edges by 2 and 4 px, their glyphs whole. The two lines of the wire scenes at 1280 x 720 touch by a pixel, a descender on a capital.

```
== 1440x900: 104 scales before, 104 after
  fma.tree.col: fixed  over (['fr'], 25) 'a bit passes'
  io: stays  over (['fr'], 30.5) -> (['fr'], 30.5) 'die edge'
  io: stays  over (['fl'], 30.5) -> (['fl'], 30.5) '← PCIe shire'
  io: stays  over (['fb'], 20.8) -> (['fb'], 20.8) '↓ shire 28'
  memshire: stays  over (['fl'], 30.5) -> (['fl'], 30.5) 'die edge'
  memshire: stays  over (['fr'], 30.5) -> (['fr'], 30.5) '→ shire 24'
  memshire: stays  over (['fb'], 22.9) -> (['fb'], 22.9) '↓ memory shire 1'
  pcie: stays  over (['fl'], 30.5) -> (['fl'], 30.5) '← master shire'
  pcie: stays  over (['fr'], 30.5) -> (['fr'], 30.5) '→ I/O shire'
  pcie: stays  over (['fb'], 20.8) -> (['fb'], 20.8) '↓ shire 20'
  st29: stays  pair (5.1, 55.4) -> (5.1, 55.4) 'Mission St' x 'San Jose Ave'
== over: 1 fixed, 9 stay, 0 new; pairs: 0 fixed, 1 stay, 0 new
```

```
== 1280x720: 104 scales before, 104 after
  fma.tree.col: fixed  over (['fr'], 33.8) 'a bit passes'
  io: stays  over (['fr'], 26.7) -> (['fr'], 26.7) 'die edge'
  io: stays  over (['fl'], 26.7) -> (['fl'], 26.7) '← PCIe shire'
  io: stays  over (['fb'], 17) -> (['fb'], 17) '↓ shire 28'
  l1d: fixed  over (['fr'], 3.1) '39.0 cycles at 768 B (cycles)'
  lib.booth: fixed  over (['fr'], 31.9) 'A. Booth (1951), O. MacSorley (1961, radix 4); Koren, Computer Arithme'
  lib.booth: fixed  over (['fr', 'vr'], 150.2) 'a signed 8-bit multiplier makes 4 rows (drawn; an unsigned one, one mo'
  lib.booth: fixed  over (['fr'], 11.5) 'row: 0, ±X or ±2X'
  lib.buck: fixed  over (['fr'], 24.8) "the card's core regulator (TI TPSM831D31): 3 phases of this, up to 120"
  lib.buck: fixed  over (['fr', 'vr'], 156.7) 'two transistors connect an inductor to the input or to ground, hundred'
  lib.cmp42: fixed  over (['fr'], 1.6) 'cin comes from the 4:2 of the column on the right;'
  lib.diffamp: fixed  over (['fr', 'vr'], 169.8) 'two matched transistors share one tail current: the higher input takes'
  lib.ecc: fixed  over (['fr'], 51.7) '64 data bits take 8 check bits: one flipped bit corrected, two detecte'
  lib.icg: fixed  over (['fr', 'vr'], 114.4) "the multiply-add's first stage clock-gates its operands while the unit"
  lib.logic: fixed  over (['fr', 'vr'], 159.7) "synthesis turns a block's description (its RTL) into thousands of cell"
  lib.lzd: fixed  over (['fr'], 55.4) 'V. Oklobdzija, IEEE Trans. VLSI 1994; M. Schmookler and K. Nowka, ARIT'
  lib.lzd: fixed  over (['fr'], 27.4) 'log₂ n levels: 3 for 8 bits, 6 for 64. An anticipator guesses the coun'
  lib.powerfet: fixed  over (['fr'], 36) 'B. J. Baliga, Fundamentals of Power Semiconductor Devices, ch. 6; the '
  lib.powerfet: fixed  over (['fr', 'vr'], 145.1) 'a trench MOSFET: thousands of cells side by side; when the gates are o'
  lib.regfile: fixed  over (['fr'], 5.3) "a minion's registers are of this kind: the core's integer file is 64 w"
  lib.rom: fixed  over (['fr'], 67.1) '4 words of 4 bits drawn: precharged bitlines; a transistor where a bit'
  lib.rom: fixed  over (['fr'], 19.3) 'describes them as look-up tables in the RTL ("RTL LUTs", §2.3.7), not '
  lib.rom: fixed  over (['fr'], 10.5) "the vector unit's transcendental functions (2ˣ, log₂ x, 1/x) read coef"
  lib.round: fixed  over (['fr', 'vr'], 90.1) 'IEEE Std 754-2019 §4.3; Koren, Computer Arithmetic Algorithms, ch. 4; '
  lib.shifter: fixed  over (['fr'], 52.2) '3 stages shift 8 bits by any amount from 0 to 7; 6 stages shift 64. In'
  lib.shifter: fixed  over (['fr'], 25.3) 'another moves the sum back (normalises it). Weste and Harris, CMOS VLS'
  lib.strap: fixed  over (['fr', 'vr'], 127.9) "a switch on the card holds one of the chip's pins at 0, or lets a resi"
  lib.wire: fixed  over (['fr', 'vr'], 127.6) 'the finest wires: about 20 nm wide, 40 nm apart (TSMC N7), copper in a'
  memshire: stays  over (['fl'], 26.7) -> (['fl'], 26.7) 'die edge'
  memshire: stays  over (['fr'], 26.7) -> (['fr'], 26.7) '→ shire 24'
  memshire: stays  over (['fb'], 19.3) -> (['fb'], 19.3) '↓ memory shire 1'
  mesh.link.wire: stays  pair (99.3, 1.2) -> (99.3, 1.2) 'a 0 → 1 costs ≈ C · V²' x 'energy per bit'
  pcie: stays  over (['fl'], 26.7) -> (['fl'], 26.7) '← master shire'
  pcie: stays  over (['fr'], 26.7) -> (['fr'], 26.7) '→ I/O shire'
  pcie: stays  over (['fb'], 17) -> (['fb'], 17) '↓ shire 20'
  pcie.lane: fixed  over (['fr', 'vr'], 138.6) '16 GT/s each way on a pair of wires: the transmitter serialises and sh'
  shire.meshstop.xing: stays  pair (99.3, 1.2) -> (99.3, 1.2) 'a 0 → 1 costs ≈ C · V²' x 'energy per bit'
  shire.panel: fixed  pair (4.1, 9.8) '?' x 'inside: if m4b4 in'
  shire.subbank: fixed  pair (2.4, 11) 'dc: data complete → the response mux and' x 'the example line (0x80_1234_5340) is in '
  st29: stays  pair (4.2, 45.2) -> (4.2, 45.2) 'Mission St' x 'San Jose Ave'
  vpu.lane.fma: fixed  over (['fr'], 21.5) 'textbook stages; the blocks are the RTL’s modules'
== over: 27 fixed, 9 stay, 0 new; pairs: 2 fixed, 3 stay, 0 new
```

```
== 390x844: 104 scales before, 104 after
  fma.tree.col: fixed  over (['fr'], 14.2) 'a bit passes'
  io: stays  over (['fb'], 63.2) -> (['fb'], 63.2) '← PCIe shire'
  io: stays  over (['fb'], 22) -> (['fb'], 22) '↑ die edge'
  io: stays  over (['fb'], 66) -> (['fb'], 66) '→ die edge'
  io: stays  over (['fb'], 19.7) -> (['fb'], 19.7) '↓ shire 28'
  l1d: fixed  over (['fr'], 1.3) '39.0 cycles at 768 B (cycles)'
  lib.booth: fixed  over (['fr'], 13.4) 'A. Booth (1951), O. MacSorley (1961, radix 4); Koren, Computer Arithme'
  lib.booth: fixed  over (['fr', 'vr'], 62.8) 'a signed 8-bit multiplier makes 4 rows (drawn; an unsigned one, one mo'
  lib.booth: fixed  over (['fr'], 4.8) 'row: 0, ±X or ±2X'
  lib.buck: fixed  over (['fr'], 10.4) "the card's core regulator (TI TPSM831D31): 3 phases of this, up to 120"
  lib.buck: fixed  over (['fr', 'vr'], 65.5) 'two transistors connect an inductor to the input or to ground, hundred'
  lib.cmp42: fixed  over (['fr'], 0.7) 'cin comes from the 4:2 of the column on the right;'
  lib.diffamp: fixed  over (['fr', 'vr'], 71) 'two matched transistors share one tail current: the higher input takes'
  lib.ecc: fixed  over (['fr', 'vr'], 21.6) '64 data bits take 8 check bits: one flipped bit corrected, two detecte'
  lib.icg: fixed  over (['fr', 'vr'], 47.8) "the multiply-add's first stage clock-gates its operands while the unit"
  lib.logic: fixed  over (['fr', 'vr'], 66.8) "synthesis turns a block's description (its RTL) into thousands of cell"
  lib.lzd: fixed  over (['fr', 'vr'], 23.2) 'V. Oklobdzija, IEEE Trans. VLSI 1994; M. Schmookler and K. Nowka, ARIT'
  lib.lzd: fixed  over (['fr'], 11.5) 'log₂ n levels: 3 for 8 bits, 6 for 64. An anticipator guesses the coun'
  lib.powerfet: fixed  over (['fr'], 15.1) 'B. J. Baliga, Fundamentals of Power Semiconductor Devices, ch. 6; the '
  lib.powerfet: fixed  over (['fr', 'vr'], 60.6) 'a trench MOSFET: thousands of cells side by side; when the gates are o'
  lib.regfile: fixed  over (['fr'], 2.2) "a minion's registers are of this kind: the core's integer file is 64 w"
  lib.rom: fixed  over (['fr', 'vr'], 28) '4 words of 4 bits drawn: precharged bitlines; a transistor where a bit'
  lib.rom: fixed  over (['fr'], 8.1) 'describes them as look-up tables in the RTL ("RTL LUTs", §2.3.7), not '
  lib.rom: fixed  over (['fr'], 4.4) "the vector unit's transcendental functions (2ˣ, log₂ x, 1/x) read coef"
  lib.round: fixed  over (['fr', 'vr'], 37.7) 'IEEE Std 754-2019 §4.3; Koren, Computer Arithmetic Algorithms, ch. 4; '
  lib.shifter: fixed  over (['fr', 'vr'], 21.8) '3 stages shift 8 bits by any amount from 0 to 7; 6 stages shift 64. In'
  lib.shifter: fixed  over (['fr'], 10.6) 'another moves the sum back (normalises it). Weste and Harris, CMOS VLS'
  lib.strap: fixed  over (['fr', 'vr'], 53.5) "a switch on the card holds one of the chip's pins at 0, or lets a resi"
  lib.wire: fixed  over (['fr', 'vr'], 53.3) 'the finest wires: about 20 nm wide, 40 nm apart (TSMC N7), copper in a'
  memshire: stays  over (['fb'], 66) -> (['fb'], 66) '← die edge'
  memshire: stays  over (['fb'], 22) -> (['fb'], 22) '↑ die edge'
  memshire: stays  over (['fb'], 63.2) -> (['fb'], 63.2) '→ shire 24'
  memshire: stays  over (['fb'], 22) -> (['fb'], 22) '↓ memory shire 1'
  mesh: fixed  over (['fr'], 16.5) '+ RID, RRESP, RLAST; a header of unknown width'
  mesh: fixed  pair (79.3, 1) '+ RID, RRESP, RLAST; a header of unknown' x 'reply: one 512-bit data beat'
  pcie: stays  over (['fb'], 63.2) -> (['fb'], 63.2) '← master shire'
  pcie: stays  over (['fb'], 22) -> (['fb'], 22) '↑ die edge'
  pcie: stays  over (['fb'], 63.2) -> (['fb'], 63.2) '→ I/O shire'
  pcie: stays  over (['fb'], 19.7) -> (['fb'], 19.7) '↓ shire 20'
  pcie.lane: fixed  over (['fr', 'vr'], 57.9) '16 GT/s each way on a pair of wires: the transmitter serialises and sh'
  shire.panel: fixed  pair (1.7, 4.1) '?' x 'inside: if m4b4 in'
  st29: stays  over (['vl'], 1.9) -> (['vl'], 1.9) 'Diamond St'
  st29: stays  over (['vr'], 4.2) -> (['vr'], 4.2) 'Mission St'
  st29: fixed  over (['vr'], 45.2) 'sea level'
  vpu.lane.fma: fixed  over (['fr'], 9) 'textbook stages; the blocks are the RTL’s modules'
== over: 29 fixed, 14 stay, 0 new; pairs: 2 fixed, 0 stay, 0 new
```
