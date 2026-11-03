#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E151 (desk, before any E151 data): the registered rail filter tested on E145's committed data. E145's own reducer,
tools/claims-v3/e145/reduce_e145.py, UNCHANGED (it runs E78's reduce_e78.py unchanged, with E145's items and card 1's configuration
gate), is run on E145's 16 committed blocks with its dip filter (E82 A2) extended to drop E151's rail glitches as well
(railfilter_e151.flags: F1 or F2, read on the raw sample sequence, as E145's post-hoc posthoc_e145.py did with F1 alone). The output is
E145's per-run table under E151's filter, which score_e151.py --selftest scores with E145's scorer unchanged, and from which
make_predictions_e151.py freezes card 1's per-bit prices (card1_prices_rail_fJ_filtered) before E151's first launch.

    PY=<python with numpy> python3 tools/claims-v3/e151/e145_under_filter.py [<E145 data dir>] [<out dir>]
Defaults: docs/reports/data/2026-11-02-e145-int8-b-card1, tools/claims-v3/e151/e145-filtered.
SPDX-License-Identifier: Apache-2.0
"""
import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "docs/reports/data/2026-11-02-e145-int8-b-card1")
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "e145-filtered")
    os.makedirs(out, exist_ok=True)
    py = os.environ.get("PY", sys.executable)
    blocks = sorted(d for d in glob.glob(os.path.join(src, "aifoundry1-c1", "kinds", "p145[1-3][0-9]"))
                    if os.path.exists(os.path.join(d, "block.json")) and '"status":"ok"' in open(os.path.join(d, "block.json")).read())
    blocks = [os.path.relpath(b, ROOT) for b in blocks]          # relative to the tree root (the reducer runs there): no host path in the output
    runner = os.path.join(out, "_reduce_e145_filtered.py")
    open(runner, "w").write(
        "import sys\n"
        f"sys.path.insert(0, {os.path.join(ROOT, 'tools/claims-v3/e145')!r})\n"
        f"sys.path.insert(0, {HERE!r})\n"
        "import reduce_e145 as r\n"
        "import railfilter_e151 as rf\n"
        "orig = r.drop_dips\n"
        "def drop_both(rows):\n"
        "    kept, idx = orig(rows)\n"
        "    gone = set(idx) | rf.flags(rows)['union']\n"
        "    return [x for i, x in enumerate(rows) if i not in gone], sorted(gone)\n"
        "r.drop_dips = drop_both\n"
        "r.main()\n")
    o = os.path.relpath(out, ROOT)
    rc = subprocess.run([py, runner] + blocks + ["--drop-dips", "--no-refit", "--out", os.path.join(o, "e145-filtered.json"),
                                                 "--csv", os.path.join(o, "runs.csv"), "--txt", os.path.join(o, "reduce.txt")],
                        capture_output=True, text=True, cwd=ROOT)
    os.remove(runner)
    open(os.path.join(out, "reduce.log"), "w").write(rc.stdout[-20000:] + rc.stderr[-20000:])
    print(json.dumps({"blocks": [os.path.basename(b) for b in blocks], "rc": rc.returncode}))
    return rc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
