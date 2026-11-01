#!/usr/bin/env python3
"""E110 AFTER THE DATA, labelled: the encoded wide-path residual E_w by the formula the registration states, because the frozen reducer's
contrast omits two of its terms. Written Sun 1 Nov 2026, after the registered reduction was read; departure D1 of the data README.

    python3 tools/claims-v3/e110/amend_e110.py <E110 data dir> > <E110 data dir>/ew-readme-formula.txt   (+ ew-readme-formula.json)

The registration (tools/claims-v3/e110/README.md, sections 3 and 4, and the frozen predictions) defines
    E_w = (vl_w - dm_u4) - (wl_w - dm_l08) - (n_w/31) * [(dm_a44 - dm_u4) - (dm_a08 - dm_l08)],   n = 15, 7, 3, 1 for w = 32, 64, 128, 256,
and reduce_e110.py's CONTRASTS["E<w>"] holds {vl_w: 1, dm_u4: -1, wl_w: -1, dm_l08: 1, dm_a44: -k, dm_a08: +k}, which lacks +k*dm_u4 and
-k*dm_l08: it subtracts (n_w/31)(dm_a44 - dm_a08) instead of the pins' share, so it is lower by (n_w/31)(dm_u4 - dm_l08), about 0.08 W at w = 64.
This recomputes E_w both ways from the reducer's own per-pass item values (per_pass.<p>.items.board), in every arm, with E81's class rule
(present: mean >= 0.25 W and the 95 % interval above 0; absent: the interval inside +-0.30 W), and the R3 and R4 readings under each.
Nothing else is recomputed, and no registered file changes.
"""
import json
import math
import os
import sys

T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365}
N = {32: 15, 64: 7, 128: 3, 256: 1}
ARMS = ("e110.json", "e110-leak0.2936.json", "e110-leak0.3803.json", "e110-unfiltered.json")


def ci(v):
    n = len(v)
    m = sum(v) / n
    s = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
    h = T975[n - 1] * s / math.sqrt(n)
    return {"mean": m, "lo": m - h, "hi": m + h, "n": n}


def cls(c):
    if c["mean"] >= 0.25 and c["lo"] > 0:
        return "present"
    if c["lo"] >= -0.30 and c["hi"] <= 0.30:
        return "absent"
    return "unresolved"


def main():
    D = sys.argv[1]
    out = {}
    print("E110 AFTER THE DATA, labelled: E_w by the registration's formula against the frozen reducer's, every arm (W, 95 % t over the headline passes)")
    for fn in ARMS:
        d = json.load(open(os.path.join(D, fn)))
        passes = [str(p) for p in d["passes_headline"]]
        row = {}
        for w, n in N.items():
            k = n / 31.0
            spec, code = [], []
            for p in passes:
                I = d["per_pass"][p]["items"]["board"]
                V = I["vl_%d" % w] - I["dm_u4"]
                S = I["wl_%d" % w] - I["dm_l08"]
                pins = (I["dm_a44"] - I["dm_u4"]) - (I["dm_a08"] - I["dm_l08"])
                spec.append(V - S - k * pins)
                code.append(d["per_pass"][p]["contrasts"]["board"]["E%d" % w])
            cs, cc = ci(spec), ci(code)
            cs["class"], cc["class"] = cls(cs), cls(cc)
            row["E%d" % w] = {"readme_formula": cs, "frozen_code": cc}
        s64 = d["classes"]["S64"]
        c256 = d["classes"]["c256"]
        for key in ("readme_formula", "frozen_code"):
            e64 = row["E64"][key]["class"]
            r3 = ("RAW" if (s64 == "present" and e64 == "absent") else "ENCODED" if (e64 == "present" and s64 == "absent") else
                  "BOTH" if (e64 == "present" and s64 == "present") else "NEITHER" if (e64 == "absent" and s64 == "absent") else "UNRESOLVED")
            e256 = row["E256"][key]["class"]
            r4 = ("RAW256" if (c256 == "present" and e256 != "present") else "NO256" if c256 == "absent" else
                  "ENCODED256" if e256 == "present" else "UNRESOLVED")
            row["R3_" + key], row["R4_" + key] = r3, r4
        out[fn] = row
        print("\n%s (S64 %s, c256 %s)" % (fn, s64, c256))
        for w in N:
            a, b = row["E%d" % w]["readme_formula"], row["E%d" % w]["frozen_code"]
            print("  E%-4d README formula %+.3f [%+.3f, %+.3f] %-10s | frozen code %+.3f [%+.3f, %+.3f] %s"
                  % (w, a["mean"], a["lo"], a["hi"], a["class"], b["mean"], b["lo"], b["hi"], b["class"]))
        print("  R3: README formula %s, frozen code %s (as registered: %s);  R4: README formula %s, frozen code %s (as registered: %s)"
              % (row["R3_readme_formula"], row["R3_frozen_code"], d["verdicts"]["R3_raw_or_encoded"]["reading"],
                 row["R4_readme_formula"], row["R4_frozen_code"], d["verdicts"]["R4_half_line"]["reading"]))
    json.dump(out, open(os.path.join(D, "ew-readme-formula.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
