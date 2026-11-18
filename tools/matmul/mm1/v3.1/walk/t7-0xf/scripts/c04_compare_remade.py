#!/usr/bin/env python3
"""t7-0xf (Q221) c04: compare what the landed code re-made with what is landed (desk; standard library):
  - work/recheck/walk_predictions_remade.json (the landed predict_v31.py with the landed walk_v31.py and plan.json) against the FROZEN
    walk/walk_predictions.json: every top-level key and every run and hart;
  - work/recheck/layout_table_v31.json (the landed, scrubbed layout_table_v31.py, LAB from ET_LAB) against walk/layout_table_v31.json;
  - the 10 re-check outputs (the landed check_v31.py on the scrubbed summaries) against the original check files, byte for byte.
Writes predict-compare.json and remade-compare.json into the recheck dir.
    /usr/bin/python3 -I -B c04_compare_remade.py <recheck dir> <land walk dir> <pairs.json>"""
import hashlib
import json
import os
import sys


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    rd, lw, pairs = sys.argv[1], sys.argv[2], json.load(open(sys.argv[3]))
    fz_p, rm_p = os.path.join(lw, "walk", "walk_predictions.json"), os.path.join(rd, "walk_predictions_remade.json")
    a, b = json.load(open(fz_p)), json.load(open(rm_p))
    keys = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
    nh = sum(len(r["harts"]) for r in a["runs"].values())
    neq = sum(1 for n, r in a["runs"].items() for h, v in r["harts"].items() if b["runs"].get(n, {}).get("harts", {}).get(h) == v)
    pc = {"frozen_sha256": sha(fz_p), "remade_sha256": sha(rm_p), "top_level_keys_differing": keys,
          "frozen_walk_sha256": a["walk_sha256"], "remade_walk_sha256": b["walk_sha256"], "frozen_made_pst": a["made_pst"],
          "remade_made_pst": b["made_pst"], "plan_sha256_equal": a["plan_sha256"] == b["plan_sha256"], "runs_equal": a["runs"] == b["runs"],
          "harts_equal": neq, "harts": nh, "walk_summaries_equal": all(a["runs"][n]["walk_summary"] == b["runs"][n]["walk_summary"] for n in a["runs"])}
    json.dump(pc, open(os.path.join(rd, "predict-compare.json"), "w"), indent=1)
    lt_l, lt_r = os.path.join(lw, "walk", "layout_table_v31.json"), os.path.join(rd, "layout_table_v31.json")
    rc = {"layout_table": {"landed_sha256": sha(lt_l), "remade_sha256": sha(lt_r), "bytes_equal": open(lt_l, "rb").read() == open(lt_r, "rb").read()},
          "checks": {}}
    for name, orig in pairs:
        p = os.path.join(rd, "check-%s.json" % name)
        rc["checks"][name] = {"original_sha256": sha(orig), "recheck_sha256": sha(p), "bytes_equal": open(orig, "rb").read() == open(p, "rb").read()}
    json.dump(rc, open(os.path.join(rd, "remade-compare.json"), "w"), indent=1)
    print("predictions: keys differing %s; runs equal %s; harts equal %d of %d; plan equal %s" % (keys, pc["runs_equal"], neq, nh, pc["plan_sha256_equal"]))
    print("layout table bytes equal %s" % rc["layout_table"]["bytes_equal"])
    print("checks byte-equal to the originals: %d of %d" % (sum(1 for v in rc["checks"].values() if v["bytes_equal"]), len(rc["checks"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
