#!/usr/bin/env python3
"""E180's scorer, v3 (the kit's dated note 2, KIT.md.dated-note-2.md sections 1, 4 and 5).

    python3 tools/claims-v3/e180/score_e180_v3.py --reduced reduced-e180-v3.json --out scored-e180 [--card aifoundry3]
        --elfcheck-v2 <logs/elfcheck-e180-v2.txt>     check_elf_e180_v2.py's reading at the desk of the box's own kernel listing (binding)
        [--elfcheck-box <logs/elfcheck-e180.txt>]     the box's own check_elf_e180.py line from step 6 v2 (kept beside, never read for a verdict)
    writes scored-e180.json and scored-e180.md; prints one line a rule

score_e180_v2.py (which stays as committed) is imported and run unchanged: every registered rule is v1's code on v1's D, and A1's rules
A1-1, A1-5 and A1-7 and its reported arms are v2's code. Three changes, each made before any E180 datum:
  1. A1-7 reads check_elf_e180_v2.py's lines, the walk read at the desk on the listing step 22 v3 copies back, with A1-7's words binding
     (note 2 section 1). The box's own v1 line is kept beside in "reported_v3", with its lines, and is never read for a verdict.
  2. A1-7's per-kind mark (the kit verifier's nit, fault 6): every fadd.ps.acc kind's reported reading carries 261's walk label and every
     fadd.pi.acc kind's 262's ("the sums do not walk as registered" on a FAIL; "walk not verified" on UNREAD; "walk verified by
     disassembly" on PASS), as A1 section 7 says, beside v2's one summary line.
  3. A1-5's band test is named (the verifier's fault 5): E180-A's SIZE is read "not separated from the harts' start offset" when the
     measured interval MEETS P's offset band (overlaps it), as v2's code reads it; note 2 section 4 binds that reading of A1-5's "inside".
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_e180 as s1  # noqa: E402  (v1's rules, unchanged)
import score_e180_v2 as s2  # noqa: E402  (v2, unchanged)

LAB = {"PASS": "walk verified by disassembly", "UNREAD": "walk not verified", "FAIL": "the sums do not walk as registered"}
BAND_TEST = ("meets: the measured interval overlaps P's offset band (score_e180_v2.py's test); the binding reading of A1-5's "
             "'inside' (KIT.md.dated-note-2.md section 4)")
MD_V2 = ("(A1-7; check_elf_e180.py read).", "(A1-7; check_elf_e180.py not found).")


def walk_lines(path):
    """the PASS / FAIL / UNREAD lines of a walk's output file, and its count line"""
    if not path or not os.path.exists(path):
        return []
    return [ln.rstrip("\n")[:400] for ln in open(path, errors="replace")
            if ln.split()[:1] and (ln.split()[0] in ("PASS", "FAIL", "UNREAD") or ln.startswith("ELFCHECK"))]


def score(red, fc, card, foot, offset, elf2_path, box_path, noise):
    elf = s2.elf_reading(elf2_path)
    out = s2.score(red, fc, card, foot, offset, elf, noise)          # every registered rule and A1's, v2's code
    box = s2.elf_reading(box_path)
    marks = {}
    for nm, rep in out.get("reported", {}).get("kinds", {}).items():
        mode = nm.split("/")[0]
        if mode in ("fadd.ps.acc", "fadd.pi.acc"):
            rep["walk"] = LAB[elf["261" if mode == "fadd.ps.acc" else "262"]]
            marks[nm] = rep["walk"]
    out["reported_v3"] = {
        "what": "score_e180_v3.py (KIT.md.dated-note-2.md): v2's scorer, with A1-7 read from check_elf_e180_v2.py at the desk",
        "elfcheck_binding": {"reader": "check_elf_e180_v2.py at the desk, on the box's own kernel listing (note 2 section 1)",
                             "file": elf["file"], "261": elf["261"], "262": elf["262"], "lines": walk_lines(elf2_path)},
        "elfcheck_box_v1": {"reader": "check_elf_e180.py on the box at step 6 v2, kept beside, never read for a verdict",
                            "file": box["file"], "261": box["261"], "262": box["262"], "lines": walk_lines(box_path)},
        "walk_marks_per_kind": marks,
        "a1_5_band_test": BAND_TEST,
        "reduction": red.get("v3", {}).get("what", "not reduce_e180_v3.py"),
        "unreadable_passes": red.get("v3", {}).get("unreadable_passes", {}),
    }
    return out


def md(s):
    text = s2.md(s)
    v3 = s["reported_v3"]
    b, x = v3["elfcheck_binding"], v3["elfcheck_box_v1"]
    new = (f"(A1-7, read by check_elf_e180_v2.py at the desk on the box's own kernel listing, "
           f"{'read' if b['file'] else 'not found'}: KIT.md.dated-note-2.md section 1).")
    for old in MD_V2:
        if old in text:
            text = text.replace(old, new, 1)
            break
    L = [text.rstrip("\n")]
    L.append(f"- The box's own walk line (check_elf_e180.py at step 6 v2), kept beside and never read for a verdict: "
             f"{'261 ' + x['261'] + ', 262 ' + x['262'] if x['file'] else 'not found'}.")
    acc = {}
    for nm, lab in v3["walk_marks_per_kind"].items():
        acc.setdefault((nm.split("/")[0], lab), []).append(nm.split("/", 1)[1])
    for (mode, lab), kinds in sorted(acc.items()):
        L.append(f"- A1-7's mark on every {mode} kind's reported reading ({len(kinds)}: {', '.join(sorted(kinds))}): {lab}.")
    L.append(f"- A1-5's band test: {v3['a1_5_band_test']}.")
    if v3["unreadable_passes"]:
        L.append("- Set aside as unreadable by reduce_e180_v3.py: " +
                 "; ".join(f"{p}: {w}" for p, w in sorted(v3["unreadable_passes"].items())) + ".")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reduced", required=True)
    ap.add_argument("--out", required=True, help="prefix: writes <out>.json and <out>.md")
    ap.add_argument("--card", default="aifoundry3")
    ap.add_argument("--forecast", default=os.path.join(HERE, "forecast-e180.json"))
    ap.add_argument("--footing", default=os.path.join(HERE, "footing-e180-a1.json"))
    ap.add_argument("--offset", default=os.path.join(HERE, "offset-e180-a1.json"))
    ap.add_argument("--noise", default=os.path.join(HERE, "noise", "noise-e180.json"))
    ap.add_argument("--elfcheck-v2", required=True, help="check_elf_e180_v2.py's output for the box's listing (binding)")
    ap.add_argument("--elfcheck-box", default=None, help="the box's own check_elf_e180.py output (kept beside)")
    a = ap.parse_args()
    s = score(s1.load(a.reduced), s1.load(a.forecast), a.card, s1.load(a.footing), s1.load(a.offset), a.elfcheck_v2, a.elfcheck_box,
              s1.load(a.noise))
    json.dump(s, open(a.out + ".json", "w"), indent=1, sort_keys=True)
    open(a.out + ".md", "w").write(md(s))
    for k, r in s["rules"].items():
        print(f"{k}: {r['verdict']}")


if __name__ == "__main__":
    main()
