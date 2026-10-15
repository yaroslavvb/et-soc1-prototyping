#!/usr/bin/env python3
"""residual_edits.py : the four small edits left after the fixers (14 Oct 2026), each an exact replacement that must
match once: the shire's voltage domains (facts-arch.json and its record), the unused memory-shire mirror flag, the
crossing's reuse note, and the outside levels' research note (88 W budget, 76 GB/s, idle range)."""
R = '/home/yaroslavvb/claude/et-soc1-prototyping/'
CD = R + 'docs/reports/data/2026-09-27-chip-diagram/research/'
VD_OLD = ("the SRAM arrays (shire cache, and the I-cache data memory, placed in the shire channel because it must run at "
          "high voltage) on the SRAM rail, the mesh stop on the NoC rail.")
VD_NEW = ("the shire cache's SRAM arrays on the SRAM rail, the L1 I-cache data memory in the Shire Channel because it must "
          "run at high voltage (the description names no rail for it), the mesh stop on the NoC rail.")
EDITS = [
    (CD + 'facts-arch.json', VD_OLD, VD_NEW),
    (CD + 'build_facts_arch.py', VD_OLD, VD_NEW),
    (R + 'docs/reports/sources/ladder-mem.js',
     "// (mirror: memory shires 0-3 sit on the west edge, their PHY and pins toward the die edge at the left; ex: the instance\n// holds the example line; review of 14 Oct)",
     "// (ex: the instance holds the example line; review of 14 Oct)"),
    (R + 'docs/reports/sources/ladder-mem.js',
     "  mirror: p.ms < 4, ex: p.ms === DRX().ms",
     "  ex: p.ms === DRX().ms"),
    (CD + 'build_inside.py',
     "its wire scale the mesh-rail level shifter and the 2-flop synchroniser;",
     "its wire scale the mesh-rail level shifter and the VC FIFO whose counts cross by 2-flop synchronisers;"),
    (CD + 'research-outside.md',
     "tensor loads measured at 75 GB/s). 12 V in, at most 7.3 A / 88 W (p. 5); highest draw on record 87.8 W;\nidle 19-36 W by card.",
     "tensor loads stream 76 GB/s, bw-dram). 12 V in, a 7.3 A / 88 W budget (p. 5); highest draw under load 87.8 W,\n134 W in aifoundry2's idle runaways (2 and 7 Oct); idle 19-50 W by card."),
]
for path, old, new in EDITS:
    s = open(path).read()
    n = s.count(old)
    if n != 1:
        raise SystemExit(f'{path}: old text found {n} times')
    open(path, 'w').write(s.replace(old, new))
    print('edited', path.replace(R, ''))
