#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E92 reduction (Q132): E78's registered reduction, reduce_e78.py, run UNCHANGED on E92's passes, with E92's items
(E78's 51 kinds and the tie plus E92's thirty-two tiles) installed on the shared e78_common module, so that the
per-run gates (the dumped tile equal to the item's registered sha256 among them), the pass gates (E78's six anchors,
three times a pass, and the tie), the interpolation of each type's zeros, D, D32, S, the rail, pJ per op / MAC /
flop, the heat column and every statistic are E78's own. Registration: tools/claims-v3/kinds/E92.md.

    python3 tools/claims-v3/kinds/reduce_e92.py <pass dir> ... --out e92.json [--csv] [--txt] [--leak auto|<k>]
        [--tau 0.95] [--delay 0.2] [--c-rb 0.81] [--no-refit]          (every reduce_e78.py option, unchanged)

Before it runs it checks reduce_e78.py, e78_common.py and kinds.json against predictions-e92.json (E78's freeze
values) and e92.json against E92's freeze, and refuses on any difference. After reduce_e78 writes --out, its
"experiment" becomes "E92" and a "reducer" block records the code and the hashes; the --txt file gets a header line.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
REG = os.path.join(HERE, "predictions-e92.json")


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    reg = json.load(open(REG))
    want = reg["harness"]["reused_unchanged_sha256"]
    bad = []
    for rel in ("tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/e78_common.py",
                "tools/claims-v3/kinds/kinds.json"):
        have = sha(os.path.join(ROOT, rel))
        if have != want[rel]:
            bad.append(f"{rel}: sha256 {have} != registered {want[rel]}")
    import e92_common as e92  # noqa: E402
    e = e92.check_e92_json()
    if e:
        bad.append(e)
    if bad:
        raise SystemExit("refusing to reduce - the reused E78 code or e92.json changed:\n  " + "\n  ".join(bad))
    e92.install()
    import reduce_e78 as r  # noqa: E402  (after the check and the install)
    out_path = txt_path = None
    for i, x in enumerate(sys.argv):
        if x == "--out" and i + 1 < len(sys.argv):
            out_path = sys.argv[i + 1]
        if x == "--txt" and i + 1 < len(sys.argv):
            txt_path = sys.argv[i + 1]
    r.main()
    if out_path and os.path.exists(out_path):
        res = json.load(open(out_path))
        res["experiment"] = "E92"
        res["reducer"] = {
            "code": "tools/claims-v3/kinds/reduce_e78.py (E78's registered reduction, unchanged)",
            "reduce_e78_sha256": sha(os.path.join(HERE, "reduce_e78.py")),
            "e78_common_sha256": sha(os.path.join(HERE, "e78_common.py")),
            "kinds_json_sha256": sha(os.path.join(HERE, "kinds.json")),
            "e92_json_sha256": sha(e92.E92_JSON),
            "e92_common_sha256": sha(os.path.join(HERE, "e92_common.py")),
            "wrapper": "tools/claims-v3/kinds/reduce_e92.py", "wrapper_sha256": sha(os.path.abspath(__file__)),
            "substitution": "e78_common.load_items returns E78's items plus E92's thirty-two tiles (e92_common); "
                            "nothing else changes",
        }
        json.dump(res, open(out_path, "w"), indent=1, default=lambda o: None)
    if txt_path and os.path.exists(txt_path):
        body = open(txt_path).read()
        open(txt_path, "w").write("E92: reduce_e78.py unchanged, E92's items installed (reduce_e92.py)\n" + body)


if __name__ == "__main__":
    main()
