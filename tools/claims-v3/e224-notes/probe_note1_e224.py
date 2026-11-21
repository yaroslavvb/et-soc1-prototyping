#!/usr/bin/env python3
"""E224's REGISTRATION DATED NOTE 1 (lane fix-e224, round Q237, Fri 20 Nov 2026, before any E224 datum): the two desk readings the note
states, standard library only, reading only committed files (and, for 'xcheck', two re-made copies of desk/xcheck-cands-e224.json):

  compare <lab> <out.json> <out.txt>
      verify-e224's finding 2. reg-e224's pre-hash probe (probe-p01-kinds-as-run.py, run 15:20:04-15:20:05 PST, before the point rule's hash
      at 15:40:51) priced MM1-v3.2's W over idle for every format and data kind at gemmL1x1x1 and gemmL2x2x4 on aifoundry1 card 1 at 600 MHz
      (neither shape is an E224 point). Family P's registered rule (POINT-RULE-e224.md section 2) draws, at each P shape, the E212 kind and the
      E217 kind with the largest |ln(W_counts / W_null)| by the same model, W_null the mean of its W at zeros, ones and random, each W at 3 W or
      more. This prints, beside each registered P slot, (a) the rule's own ranking at the drawn shape (desk/candidates-e224.json), and (b) the
      probe's ranking of the E212 kinds of that format at each probed shape by the same quantity, the kinds drawn by an earlier P slot left
      out as the rule leaves them out (POST HOC: made now, from the copy of the probe's output kept here, probe-p01-kinds-e224.json). The probe held no E217
      kind (it read E212's tiles only).

  xcheck <registered json> <made with desk/l3s-extra-e224.json absent> <made with the tree as registered> <out.json> <out.txt>
      verify-e224's finding 4: every field of each re-made copy against the registered desk/xcheck-cands-e224.json (the paths compared leaf
      by leaf; a list compared item by item).

    /usr/bin/python3 -I -B tools/claims-v3/e224-notes/probe_note1_e224.py compare <lab> <out.json> <out.txt>
    /usr/bin/python3 -I -B tools/claims-v3/e224-notes/probe_note1_e224.py xcheck <reg.json> <a.json> <b.json> <out.json> <out.txt>
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = os.path.join(HERE, "probe-p01-kinds-e224.json")
SHAPES = ("gemmL1x1x1", "gemmL2x2x4")


def compare(lab, oj, ot):
    E = os.path.join(lab, "tools", "claims-v3", "e224")
    probe = json.load(open(PROBE))
    cand = json.load(open(os.path.join(E, "desk", "candidates-e224.json")))["candidates"]["P"]
    pts = json.load(open(os.path.join(E, "points-e224.json")))["points"]["A"]
    W = {}
    for q in probe["probe"]:
        W.setdefault((q["fmt"], q["arm"]), {})[q["kind"]] = q["W_over_idle"]
    drawn_e212 = []
    rows, lines = [], []
    lines.append("Family P: the registered picks beside reg-e224's pre-hash probe (POST HOC; MM1-v3.2's W over idle, aifoundry1 card 1, 600 MHz)")
    for slot in cand:
        fmt, sid = slot["fmt"], slot["slot"]
        drawn = [t for t in slot["tried"] if t.get("verdict") == "drawn"][0]
        token = drawn["token"]
        pa = [p for p in pts if p["id"] == sid + "a"][0]
        pb = [p for p in pts if p["id"] == sid + "b"][0]
        rule = [{"kind": k, "source": s, "abs_ln": round(-sc, 4), "W_counts": round(wc, 3), "W_null": round(wn, 3)}
                for sc, k, s, wc, wn in drawn["scores"]]
        r212 = [r["kind"] for r in rule if r["source"] == "E212"]
        probe_rank = {}
        for shape in SHAPES:
            d = W.get((fmt, shape), {})
            wn = (d["random"] + d["zeros"] + d["ones"]) / 3.0
            rk = sorted(((abs(math.log(w / wn)), k) for k, w in d.items()
                         if k.startswith("pattern:") and w is not None and w >= 3.0 and k not in drawn_e212), reverse=True)
            order = [k for _, k in rk]
            probe_rank[shape] = {"W_null": round(wn, 3), "order": [[k, round(s, 4)] for s, k in rk],
                                 "rank_of_registered_e212_pick": (order.index(pa["kind"]) + 1) if pa["kind"] in order else None}
        rows.append({"slot": sid, "format": fmt, "shape": token, "registered_e212_pick": pa["kind"], "registered_e217_pick": pb["kind"],
                     "rule_ranking_at_the_drawn_shape": rule, "rule_order_e212": r212, "probe": probe_rank})
        lines.append(f"{sid} {fmt} at {token}: registered E212 pick {pa['kind']}, E217 pick {pb['kind']}; the rule's E212 order there: "
                     + ", ".join(r212[:4]))
        for shape in SHAPES:
            pr = probe_rank[shape]
            lines.append(f"   the probe at {shape} (W_null {pr['W_null']} W; kinds drawn by an earlier slot left out): "
                         + ", ".join(f"{k} {s}" for k, s in pr["order"][:4])
                         + f" -> the registered E212 pick ranks {pr['rank_of_registered_e212_pick']}")
        drawn_e212.append(pa["kind"])
    first = all(r["probe"][s]["rank_of_registered_e212_pick"] == 1 for r in rows for s in SHAPES)
    lines.append(f"Every registered E212 pick is the probe's first E212 kind at both probed shapes: {first}. The probe priced no E217 kind, so "
                 f"the E217 picks ({', '.join(r['registered_e217_pick'] for r in rows)}) were not in it.")
    out = {"what": "E224 registration dated note 1: family P's picks beside reg-e224's pre-hash probe (POST HOC)",
           "probe_file": "tools/claims-v3/e224-notes/probe-p01-kinds-e224.json", "slots": rows, "every_e212_pick_first_in_the_probe": first}
    json.dump(out, open(oj, "w"), indent=1, sort_keys=True)
    open(ot, "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


def leaves(x, p=""):
    if isinstance(x, dict):
        for k in sorted(x):
            yield from leaves(x[k], f"{p}/{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from leaves(v, f"{p}[{i}]")
    else:
        yield p, x


def xcheck(reg, a, b, oj, ot):
    R = dict(leaves(json.load(open(reg))))
    out, lines = {"what": "E224 registration dated note 1: desk/xcheck-cands-e224.json re-made, field by field against the registered file",
                  "registered_leaves": len(R)}, []
    for tag, f in (("a_l3s_extra_absent", a), ("b_tree_as_registered", b)):
        M = dict(leaves(json.load(open(f))))
        diff = sorted(k for k in set(R) | set(M) if R.get(k, "<absent>") != M.get(k, "<absent>"))
        out[tag] = {"leaves": len(M), "differing": [{"path": k, "registered": R.get(k, "<absent>"), "made": M.get(k, "<absent>")} for k in diff],
                    "verdict": M.get("/verdict")}
        lines.append(f"{tag}: {len(M)} leaves (registered {len(R)}); verdict {M.get('/verdict')}; differing leaves {len(diff)}"
                     + (": " + "; ".join(f"{k} registered {R.get(k, '<absent>')} made {M.get(k, '<absent>')}" for k in diff) if diff else ""))
    json.dump(out, open(oj, "w"), indent=1, sort_keys=True)
    open(ot, "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


def main(argv):
    if len(argv) >= 4 and argv[0] == "compare":
        return compare(*argv[1:4])
    if len(argv) >= 6 and argv[0] == "xcheck":
        return xcheck(*argv[1:6])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
