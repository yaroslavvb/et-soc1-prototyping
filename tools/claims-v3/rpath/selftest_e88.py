#!/usr/bin/env python3
"""E88 self-test of the reduction and scoring plumbing, before any E88 data: E82's committed card-1 passes are
relabelled with E88 item names (a stand-in, not a measurement: e.g. E82's fp32.pi run plays fp32.c_abs) and their
tile dumps replaced by E88's tiles, then reduce_e88.py (both dip arms) and score_e88.py run on them. It checks that
every stage runs, that the registered gates see the stand-in passes, and that every rule gets a verdict.

    /usr/bin/python3 tools/claims-v3/rpath/selftest_e88.py <scratch dir>
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
E82RAW = os.path.join(ROOT, "docs/reports/data/2026-10-31-e82-kinds-aifoundry1/aifoundry1-c1/kinds")
MAP = {"fp32.zeros": "fp32.zeros", "fp32.randn": "fp32.randn", "fp16.zeros": "fp16.zeros", "fp16.randn": "fp16.randn",
       "int8.zeros": "int8.zeros", "int8.full": "int8.full", "anchor_pi": "anchor_pi",
       "fp32.ones": "fp32.ones", "fp16.ones": "fp16.ones", "int8.ones": "int8.ones",
       "fp32.pi": "fp32.c_abs", "fp32.uniform01": "fp32.r_walk", "fp32.bf16trunc": "fp32.r_abs",
       "fp32.fp16grid": "fp32.r_het", "fp32.pow2": "fp32.s_walk", "fp32.neg_ones": "fp32.s_abs",
       "fp16.neg_ones": "fp16.c_cancel", "fp16.uniform01": "fp16.r_walk", "fp16.fp8grid": "fp16.r_cancel",
       "fp16.pair_half_zero": "fp16.r_abs", "int8.neg_ones": "int8.c_cancel", "int8.pos": "int8.r_walk",
       "int8.highbit": "int8.r_cancel"}


def relabel(src, dst, items):
    os.makedirs(os.path.join(dst, "tiles"), exist_ok=True)
    for f in ("block.json", "config_start.json", "config_end.json", "configs.json", "telemetry.jsonl.gz"):
        shutil.copy(os.path.join(src, f), os.path.join(dst, f))
    p = os.path.basename(src)[1:]
    for f in ("marks.jsonl", "runs.jsonl"):
        out = []
        for line in open(os.path.join(src, f)):
            r = json.loads(line)
            if r.get("item") in MAP:
                r["item"] = MAP[r["item"]]
                out.append(json.dumps(r))
            elif r.get("kind") in ("heater", "burnin"):
                out.append(line.strip())
        open(os.path.join(dst, f), "w").write("\n".join(out) + "\n")
    for it in items:
        if it["tile"]:
            shutil.copy(os.path.join(ROOT, it["tile"]), os.path.join(dst, "tiles", f"{it['name']}.b{p}.bin"))
    pi = os.path.join(src, "tiles", f"anchor_pi.b{p}.bin")
    if os.path.exists(pi):
        shutil.copy(pi, os.path.join(dst, "tiles", f"anchor_pi.b{p}.bin"))


def main():
    out = os.path.abspath(sys.argv[1])
    sys.path.insert(0, HERE)
    import e88_common
    items = e88_common.load_items()
    dirs = []
    for p in ("p8211", "p8212", "p8213"):
        d = os.path.join(out, "passes", p)
        shutil.rmtree(d, ignore_errors=True)
        relabel(os.path.join(E82RAW, p), d, items)
        dirs.append(d)
    py = sys.executable
    ok = True
    for arm, extra in (("primary", []), ("keepdips", ["--keep-dips"])):
        r = subprocess.run([py, os.path.join(HERE, "reduce_e88.py"), *dirs, "--out", os.path.join(out, f"red-{arm}.json"),
                            "--txt", os.path.join(out, f"red-{arm}.txt"), "--no-refit", *extra],
                           capture_output=True, text=True)
        print(f"reduce {arm}: rc {r.returncode}; {r.stdout.strip().splitlines()[0] if r.stdout else r.stderr[-400:]}")
        ok &= r.returncode == 0
    r = subprocess.run([py, os.path.join(HERE, "score_e88.py"), "--e88", os.path.join(out, "red-primary.json"),
                        "--arm", f"keepdips={os.path.join(out, 'red-keepdips.json')}",
                        "--json", os.path.join(out, "scored.json"), "--md", os.path.join(out, "results.md")],
                       capture_output=True, text=True)
    print(f"score: rc {r.returncode}{'' if r.returncode == 0 else ' ' + r.stderr[-600:]}")
    ok &= r.returncode == 0
    if r.returncode == 0:
        sc = json.load(open(os.path.join(out, "scored.json")))
        red = json.load(open(os.path.join(out, "red-primary.json")))
        print("passes kept", red["passes"], "set aside", red["passes_set_aside"], "dips removed",
              red["reducer"]["dip_samples_removed"])
        print("tally (stand-in data, meaningless as a result):", sc["primary"]["tally"])
        unscored = [k for k, v in sc["primary"]["rules"].items() if v["verdict"] == "not scored"]
        print("rules not scored:", unscored)
        ok &= not unscored and len(red["passes"]) == 3
    print("SELFTEST", "OK" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
