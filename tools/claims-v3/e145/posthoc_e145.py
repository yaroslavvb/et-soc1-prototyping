#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E145, POST HOC (written after E145's data were reduced and scored; no rule reads it, never a verdict): card 1's minion-rail
glitches. In E145's primary three single runs read the rail 0.5-2 W high in their power windows while the board did not move; each
holds one or two telemetry samples whose sp.minion_w[0] (the rail's current reading) equals sp.minion_w[2] (the service processor's
running maximum, 34.50 W on this card all session) while its neighbours read about 13.5 W. This script

  (a) counts such samples in every E145 block and, for comparison, in E138's and E130's aifoundry3 blocks and E137's card-1 blocks of
      the same afternoon: a SPIKE is a sample with minion_w[0] > max(minion_w[0] two samples before, two after) + 4.0 W (E82 A2's
      board-dip rule mirrored), and AT_MAX says whether it equals minion_w[2];
  (b) reduces E145's blocks again with the board's dips AND the rail's spikes removed (E145's reducer, reduce_e145.py, unchanged except
      that its dip filter also drops the spike samples; E78's reduce_e78.py unchanged), and scores the result with score_e145.py
      unchanged, as a labelled post-hoc arm.

    PY=<python with numpy> python3 tools/claims-v3/e145/posthoc_e145.py <E145 raw root> <out dir>
SPDX-License-Identifier: Apache-2.0
"""
import glob
import gzip
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
SPIKE_W = 4.0


def spikes(rows):
    R = []
    for r in rows:
        try:
            R.append(float(r["sp"]["minion_w"][0]))
        except (KeyError, IndexError, TypeError, ValueError):
            R.append(None)
    bad = set()
    for i in range(2, len(rows) - 2):
        if None not in (R[i], R[i - 2], R[i + 2]) and R[i] > max(R[i - 2], R[i + 2]) + SPIKE_W:
            bad.add(i)
    return bad


def count(pattern):
    out = {}
    for f in sorted(glob.glob(pattern)):
        rows = [json.loads(x) for x in gzip.open(f, "rt") if x.startswith("{")]
        bad = spikes(rows)
        at_max = sum(1 for i in bad if rows[i]["sp"]["minion_w"][0] == rows[i]["sp"]["minion_w"][2])
        out[os.path.basename(os.path.dirname(f))] = {"samples": len(rows), "spikes": len(bad), "spikes_at_max_register": at_max,
                                                     "values": sorted({rows[i]["sp"]["minion_w"][0] for i in bad})}
    tot = {"blocks": len(out), "samples": sum(v["samples"] for v in out.values()), "spikes": sum(v["spikes"] for v in out.values()),
           "spikes_at_max_register": sum(v["spikes_at_max_register"] for v in out.values())}
    return {"total": tot, "per_block": out}


def main():
    raw, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    py = os.environ.get("PY", sys.executable)
    D = "docs/reports/data"
    census = {
        "E145 (aifoundry1 card 1)": count(os.path.join(raw, "kinds", "p145*", "telemetry.jsonl.gz")),
        "E137 (aifoundry1 card 1, 15:38-16:11 PST)": count(f"{ROOT}/{D}/2026-11-02-e137-fp16-sign-rest/aifoundry1-c1/e137/p137*/telemetry.jsonl.gz"),
        "E138 (aifoundry3 card 0)": count(f"{ROOT}/{D}/2026-11-02-e138-int8-b-rail/aifoundry3/kinds/p138*/telemetry.jsonl.gz"),
        "E130 (aifoundry3 card 0)": count(f"{ROOT}/{D}/2026-11-02-e130-int8-netlists/aifoundry3/kinds/p130*/telemetry.jsonl.gz"),
    }
    json.dump(census, open(os.path.join(out, "rail-spikes.json"), "w"), indent=1)
    for k, v in census.items():
        print(f"(a) {k}: {json.dumps(v['total'])}")
    # (b) the post-hoc reduction: reduce_e145.py's dip filter also drops the rail's spike samples
    blocks = sorted(d for d in glob.glob(os.path.join(raw, "kinds", "p145*")) if os.path.exists(os.path.join(d, "block.json"))
                    and '"status":"ok"' in open(os.path.join(d, "block.json")).read())
    runner = os.path.join(out, "_reduce_posthoc.py")
    open(runner, "w").write(
        "import sys\n"
        f"sys.path.insert(0, {HERE!r})\n"
        "import reduce_e145 as r\n"
        "import posthoc_e145 as ph\n"
        "orig = r.drop_dips\n"
        "def drop_both(rows):\n"
        "    kept, idx = orig(rows)\n"
        "    gone = set(idx) | ph.spikes(rows)\n"
        "    return [x for i, x in enumerate(rows) if i not in gone], sorted(gone)\n"
        "r.drop_dips = drop_both\n"
        "r.main()\n")
    rc = subprocess.run([py, runner] + blocks + ["--drop-dips", "--no-refit", "--out", os.path.join(out, "e145-posthoc.json"),
                                                 "--csv", os.path.join(out, "runs-posthoc.csv"), "--txt", os.path.join(out, "reduce-posthoc.txt")],
                        capture_output=True, text=True, cwd=ROOT)
    os.remove(runner)
    print("(b) post-hoc reduction rc", rc.returncode, rc.stderr[-300:] if rc.returncode else "")
    D130, D138 = f"{D}/2026-11-02-e130-int8-netlists", f"{D}/2026-11-02-e138-int8-b-rail"
    sc = subprocess.run([py, os.path.join(HERE, "score_e145.py"), "--primary", f"{out}/runs-posthoc.csv,{out}/e145-posthoc.json",
                         "--arm", f"board={out}/runs-posthoc.csv,{out}/e145-posthoc.json,p_raw,on",
                         "--pool", f"E130={D130}/runs.csv,{D130}/e130.json", "--pool", f"E138={D138}/runs.csv,{D138}/e138.json",
                         "--md", f"{out}/results-posthoc.md", "--json", f"{out}/scored-posthoc.json"], capture_output=True, text=True, cwd=ROOT)
    print("(b) post-hoc score rc", sc.returncode)
    print(sc.stdout[-2000:], sc.stderr[-500:])


if __name__ == "__main__":
    main()
