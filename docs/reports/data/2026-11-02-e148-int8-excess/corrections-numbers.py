#!/usr/bin/env python3
"""E148, corrections after verification (Mon 2 Nov 2026, about 23:40 PST; desk only: no card, no device command, nothing re-run).

    python3 docs/reports/data/2026-11-02-e148-int8-excess/corrections-numbers.py > docs/reports/data/2026-11-02-e148-int8-excess/corrections-numbers.txt

Prints the numbers the README's corrections C4 and C7 quote that posthoc/posthoc.txt does not (C1, C2, C3, C5 and C6 quote posthoc.txt's
sections 1 and 4-6):
  C4  the telemetry field named `pmic` against the shire mean minshire[0], over every committed sample (aifoundry1-c1/*/p*/telemetry.jsonl.gz),
      the margins the stops row cites (telemetry-max.json), and the records row that says what the field is (docs/findings/14-card-behaviour.md);
  C7  the in-run watcher's test (tools/claims-v3/e148/run_e148.py, _check_line: the line's age is computed and only printed), run_e78's
      between-launch stale limit (tools/claims-v3/kinds/run_e78.py, --stale-s), and the largest gap between two samples in each block.
Standard library only. SPDX-License-Identifier: Apache-2.0"""
import collections
import glob
import gzip
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))


def main():
    print("E148 corrections after verification: numbers for C4 and C7 (from committed files only)")
    diff = collections.Counter()
    n = 0
    gaps = {}
    for f in sorted(glob.glob(os.path.join(HERE, "aifoundry1-c1", "*", "p*", "telemetry.jsonl.gz"))):
        blk = "/".join(f.split(os.sep)[-3:-1])
        prev, big = None, 0
        with gzip.open(f, "rt") as fh:
            for line in fh:
                if not line.startswith("{"):
                    continue
                s = json.loads(line)
                t = s.get("temp_c") or {}
                if "pmic" in t and t.get("minshire"):
                    diff[t["pmic"] - t["minshire"][0]] += 1
                    n += 1
                if prev is not None:
                    big = max(big, s["t_ms"] - prev)
                prev = s["t_ms"]
        gaps[blk] = big
    print(f"C4  samples with both fields: {n}; pmic - minshire[0] (the shire mean): " + ", ".join(f"{k:+d} in {v}" for k, v in sorted(diff.items())))
    tm = json.load(open(os.path.join(HERE, "telemetry-max.json")))["blocks"]
    print(f"C4  over the {len(tm)} blocks (telemetry-max.json): board_w max {max(b['board_w_max'] for b in tm.values())} W;"
          f" shire mean {min(b['shire_mean_c_min'] for b in tm.values())}-{max(b['shire_mean_c_max'] for b in tm.values())} C;"
          f" hottest-shire field max {max(b['hottest_shire_c_max'] for b in tm.values())} C; the field named pmic max"
          f" {max(b['pmic_c_max'] for b in tm.values())} C")
    cb = open(os.path.join(REPO, "docs", "findings", "14-card-behaviour.md")).read().splitlines()
    rows = [i + 1 for i, x in enumerate(cb) if x.startswith("| `temp_c.pmic` |")]
    print(f"C4  docs/findings/14-card-behaviour.md, the `temp_c.pmic` row at line(s) {rows}: "
          + ("'not the PMIC's temperature' " + ("present" if rows and "not the PMIC's temperature" in cb[rows[0] - 1] else "ABSENT")))
    src = open(os.path.join(REPO, "tools", "claims-v3", "e148", "run_e148.py")).read().splitlines()
    a = next(i for i, x in enumerate(src) if x.startswith("def _check_line"))
    b = next(i for i in range(a + 1, len(src)) if src[i].startswith("def "))
    body = src[a:b]
    uses = [a + 1 + j for j, x in enumerate(body) if re.search(r"\bage\b", x)]
    tests = [a + 1 + j for j, x in enumerate(body) if re.search(r"\bage\b\s*(>|>=|<|<=)|(>|>=|<|<=)\s*\bage\b", x)]
    print(f"C7  tools/claims-v3/e148/run_e148.py _check_line, lines {a + 1}-{b}: 'age' on lines {uses}; compared on lines {tests or 'none'}")
    r78 = open(os.path.join(REPO, "tools", "claims-v3", "kinds", "run_e78.py")).read().splitlines()
    st = [(i + 1, x.strip()) for i, x in enumerate(r78) if "--stale-s" in x and "add_argument" in x]
    ck = [i + 1 for i, x in enumerate(r78) if "age > a.stale_s" in x]
    print(f"C7  tools/claims-v3/kinds/run_e78.py: {st[0][1] if st else 'no --stale-s'} (line {st[0][0] if st else '-'}); tested at line(s) {ck}")
    print(f"C7  the largest gap between two samples, ms, by block: " + ", ".join(f"{k} {v}" for k, v in sorted(gaps.items()))
          + f"; overall {max(gaps.values())}")


if __name__ == "__main__":
    main()
