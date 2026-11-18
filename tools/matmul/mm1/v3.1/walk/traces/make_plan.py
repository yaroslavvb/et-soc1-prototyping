#!/usr/bin/env python3
"""v31-trace (Q217): the traced runs' plan (names, kernels, arms, masks, sys_emu log selections) -> traces/plan.json. Desk.
Logged per active shire: hart 0 of the 'diagonal' minions m = dim0 + 8 dim1 with dim1 = dim0 mod 4 (0, 9, 18, 27, 4, 13, 22, 31: every
neighbourhood twice, every position once, so every A tile and every B tile the shire reads is seen) and hart 1 of all 32 minions (enter and
return); one shire outside the mask: harts 0 and 1 of its minion 0 (never launched). The '-all' runs log all 64 harts of every active shire."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
DIAG = [0, 9, 18, 27, 4, 13, 22, 31]
H0 = sum(1 << (2 * m) for m in DIAG)
H1 = 0xAAAAAAAAAAAAAAAA
def sels(mask, allharts=False):
    sh = [s for s in range(32) if (int(mask, 16) >> s) & 1]
    out = ["%d,%x" % (s, 0xFFFFFFFFFFFFFFFF if allharts else (H0 | H1)) for s in sh]
    off = next(s for s in range(31, -1, -1) if s not in sh)
    out.append("%d,%x" % (off, 0x3))
    return out
runs = []
def add(name, kernel, arm, mask, allharts=False, prio=1):
    runs.append({"name": name, "kernel": kernel, "arm": arm, "shape": arm.split("L")[-1].lstrip("nc") if False else arm[arm.index("L") + 1:].lstrip("nc"),
                 "mask": mask, "log_sel": sels(mask, allharts), "all_harts": allharts, "priority": prio})
add("t1-gemmL-2x4x16-0xf", "rgm136.gemmL", "gemmL2x4x16", "0xf")
add("t2-gemmL-2x4x16-0x1111", "rgm136.gemmL", "gemmL2x4x16", "0x1111")
add("t3-gemmLn-2x4x16-0xf", "rgm211.gemmLn", "gemmLn2x4x16", "0xf")
add("t4-gemmLn-2x4x16-0x1111", "rgm211.gemmLn", "gemmLn2x4x16", "0x1111")
add("t5-gemmLnc-2x4x16-0xf", "rgm136.gemmLnc", "gemmLnc2x4x16", "0xf", prio=2)
add("t6-gemmLnc-2x4x16-0x1111", "rgm136.gemmLnc", "gemmLnc2x4x16", "0x1111", prio=2)
add("t7-gemmL-1x1x16-0xf-all", "rgm136.gemmL", "gemmL1x1x16", "0xf", allharts=True, prio=3)
add("t8-gemmL-1x1x16-0x1111-all", "rgm136.gemmL", "gemmL1x1x16", "0x1111", allharts=True, prio=3)
json.dump({"what": "v31-trace's traced runs (E212's layout pair 0xf / 0x1111 at n = 4, shape 2x4x16 as E212 ran it on aifoundry1 card 1 in a1c1-S3; 1x1x16 as E212 ran it in three sessions)",
           "diag_minions": DIAG, "runs": runs}, open(os.path.join(HERE, "plan.json"), "w"), indent=1)
for r in runs:
    print(r["name"], r["kernel"], r["arm"], r["shape"], r["mask"], " ".join(r["log_sel"]))
