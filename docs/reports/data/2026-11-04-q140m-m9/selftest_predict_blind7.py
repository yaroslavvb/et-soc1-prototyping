#!/usr/bin/env python3
"""Q140(m): self-test of predict_blind7.py. Run on blind pool 6 (tools/claims-v3/kinds/blind6, with its committed counts) for the three
cards into a scratch dir, M8's, M7's and M6's predictions must equal Q139(x)'s committed predictions-blind6-<card>.json field for field;
M9's are printed beside (pool 6 is in M9's fit, so they test nothing).

    python3 selftest_predict_blind7.py <scratch dir>
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
B6 = os.path.join(ROOT, "tools", "claims-v3", "kinds", "blind6")


def flat(x, pre=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from flat(v, f"{pre}.{k}" if pre else k)
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from flat(v, f"{pre}[{i}]")
    else:
        yield pre, x


def main():
    od = os.path.abspath(sys.argv[1])
    os.makedirs(od, exist_ok=True)
    total_n, total_bad = 0, 0
    for card in ("aifoundry3", "aifoundry1c1", "aifoundry2"):
        r = subprocess.run([sys.executable, "-B", os.path.join(HERE, "predict_blind7.py"), B6, card,
                            "--counts", os.path.join(B6, "counts-blind6.json"), "--out", od], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"{card}: predict_blind7.py exit {r.returncode}\n{r.stderr[-2000:]}")
            sys.exit(1)
        new = json.load(open(os.path.join(od, f"predictions-{card}.json")))["tiles"]
        ref = json.load(open(os.path.join(B6, f"predictions-blind6-{card}.json")))["tiles"]
        n, bad, ex = 0, 0, []
        for tile, rr in ref.items():
            for lab in ("M8", "M7", "M6"):
                a = dict(flat(rr[lab]))
                b = dict(flat(new[tile][lab]))
                for k, v in a.items():
                    n += 1
                    if b.get(k) != v:
                        bad += 1
                        if len(ex) < 5:
                            ex.append((tile, lab, k, v, b.get(k)))
        m9 = [new[t]["M9"] for t in sorted(new) if "M9" in new[t]]
        print(f"{card}: {n} M8/M7/M6 fields compared with Q139(x)'s committed predictions-blind6-{card}.json, {bad} differ"
              + (f" e.g. {ex}" if ex else "") + f"; M9 predicted for {len(m9)} tiles")
        total_n += n
        total_bad += bad
        if card == "aifoundry3":
            # the M9 path: the features the predictor recomputes from the counts and the bytes equal the fit's rows-m9.json ones
            m9j = json.load(open(os.path.join(HERE, "m9.json")))
            rows = {r["key"]: r for r in json.load(open(os.path.join(HERE, "rows-m9.json"))) if r["exp"] == "E153"}
            n2, bad2 = 0, 0
            for tile, rr in rows.items():
                fam = "int8" if rr["type"] == "int8" else "float"
                for q in m9j["families"][fam]["terms"]:
                    n2 += 1
                    a, b = float(rr["f"][q]), float(new[tile]["features"][q])
                    if abs(a - b) > 1e-9 * max(1.0, abs(a)):
                        bad2 += 1
            print(f"{card}: {n2} M9 feature values of pool 6's {len(rows)} new kinds compared with rows-m9.json, {bad2} differ")
            total_n += n2
            total_bad += bad2
    print(f"SELFTEST {'PASS' if total_bad == 0 else 'FAIL'}: {total_n} fields, {total_bad} differ")
    sys.exit(0 if total_bad == 0 else 1)


if __name__ == "__main__":
    main()
