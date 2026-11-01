#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E112b, POST HOC (written after the data, Sun 1 Nov 2026 ~13:55 PST; never a registered reading, no verdict rests on it):
the registered reduction with ONE gate limit raised, E78's zeros-line departure from 0.25 W to 0.26 W, so that pass 11252,
which the registered gate set aside for `fp32.zeros departs -0.253 W from its straight line`, is kept. Everything else is
reduce_e112b.py as frozen (E95's items, card 1's 65/65 read, dips removed, leakage auto) and score_e112b.py as frozen.

    [E112A=<(a)'s e91.json>] python3 tools/claims-v3/e112/posthoc_gate_e112b.py <out dir> <pass dir> ...

Writes <out>/e112b-posthoc-gate026.json (+ .csv, .txt) and <out>/scored-posthoc-gate026.json / results-posthoc-gate026.md.
It exists because the registered (b) keeps two of three passes and so scores nothing; this view says what the third pass would
add if a 0.003 W excess on one zeros line were ignored. It is reported as that, labelled, beside the registered NOT SCORED.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(HERE, "..", "kinds")
sys.path.insert(0, K)
sys.path.insert(0, HERE)


def main():
    out, dirs = sys.argv[1], sys.argv[2:]
    os.makedirs(out, exist_ok=True)
    j = os.path.join(out, "e112b-posthoc-gate026.json")
    import e95_common as e95  # noqa: E402
    e95.install()
    import reduce_e78  # noqa: E402
    reduce_e78.GATES["zero_mid_departure_w"] = 0.26      # the one change (registered: 0.25)
    import reduce_e112b  # noqa: E402
    sys.argv = ["reduce_e112b.py", *dirs, "--out", j, "--csv", os.path.join(out, "runs-posthoc-gate026.csv"),
                "--txt", os.path.join(out, "reduce-posthoc-gate026.txt")]
    reduce_e112b.main()
    s = os.path.join(out, "scored-posthoc-gate026.json")
    extra = ["--e112a", os.environ["E112A"]] if os.environ.get("E112A") else []
    r = subprocess.run([sys.executable, os.path.join(HERE, "score_e112b.py"), "--e112b", j, *extra, "--json", s,
                        "--md", os.path.join(out, "results-posthoc-gate026.md")], capture_output=True, text=True)
    print(r.stdout[-3000:], r.stderr[-3000:])
    if r.returncode:
        sys.exit("score_e112b.py failed")


if __name__ == "__main__":
    main()
