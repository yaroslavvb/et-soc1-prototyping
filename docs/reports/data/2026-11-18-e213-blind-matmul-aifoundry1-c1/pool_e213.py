#!/usr/bin/python3
"""E213, the pooled rules' input (arm B's data directory, dated note 3): one data file holding both arms, for the frozen scorer.

E213's registered scorer (tools/claims-v3/e213/score_e213.py, sha256 a4eece29...) reads ONE data file, {"experiment": "E213", "arms":
{"A": ARM, "B": ARM}}, and scores the pooled rules HP1-HP5 only when that file holds both arms (E213.md section 7: "H1-H5 pooled over both
arms, each case or point once with its own arm's tie; NO DATA unless both arms scored"). Each arm's committed data file holds one arm, so the
kit's step 13 printed HP1-HP5 NO DATA for each arm. This script copies each arm's ARM object, unchanged, from its committed data directory
into one file, and each arm's committed step-6n labels into one labels file:

  arm A: docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry3/data-e213.json and labels-e213.json (data commit c69a12aa)
  arm B: docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry1-c1/data-e213.json and labels-e213.json (data commit b0c727c5)

Each input is checked first against its directory's SHA256SUMS line and against the sha256 pinned below. The two outputs are written in the
scorer's own dump form (indent 1, sorted keys, no trailing newline) and read back: each arm in the output equals its input arm, value for
value, and nothing else of an arm is added or dropped. The output's "pooled_from" names the inputs (the scorer reads only "arms").

    /usr/bin/python3 -I -B pool_e213.py build OUTDIR   write OUTDIR/pooled-data-e213-AB.json and OUTDIR/pooled-labels-e213-AB.json
    /usr/bin/python3 -I -B pool_e213.py check          rebuild in memory and compare with the two files beside this script (exit 0: equal)

Then, from the top level of the repository, the frozen scorer as the kit's step 13 runs it (rb/s24_score_e213.sh), on the pooled file:
    /usr/bin/python3 -I -B tools/claims-v3/e213/score_e213.py \\
        docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry1-c1/pooled-data-e213-AB.json \\
        --labels docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry1-c1/pooled-labels-e213-AB.json --out SCORED.json

Python's own modules only; it reads committed files and changes none. Exit 4: an input is not its pinned bytes; 5: an input's form is not
one arm of E213; 6: a read-back differs; 1 (check): the files beside this script differ from the rebuild.

SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.dirname(HERE)
ARMS = {
    "A": {"folder": "2026-11-18-e213-blind-matmul-aifoundry3", "data_commit": "c69a12aa946cef6bdf7b00ae8e478f6c691d65b1",
          "data_sha256": "d53caacb98e8bcf251073714926742886f6629725779dd0b9a6828ecb164c05f",
          "labels_sha256": "f664a2ce771d754f9e57015a5ac063037cfa305e32c8ec57ed12a5c48f7dbac1"},
    "B": {"folder": "2026-11-18-e213-blind-matmul-aifoundry1-c1", "data_commit": "b0c727c54eaadc6711d4b9b1085e3f1eaaf037a3",
          "data_sha256": "93fe3e7ec189faecde16cb89aea751b5a150a64286bbd4c3e3854ddacaafc3f1",
          "labels_sha256": "d801cae792a59f2e20cb92724310d46436605421a856a9bd34b1cd1f9f161184"},
}
OUT_DATA = "pooled-data-e213-AB.json"
OUT_LABELS = "pooled-labels-e213-AB.json"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def listed(folder, name):
    with open(os.path.join(DATA, folder, "SHA256SUMS"), encoding="utf-8") as fh:
        for ln in fh:
            h, _, p = ln.rstrip("\n").partition("  ")
            if p == name:
                return h
    return None


def dump(obj):
    return json.dumps(obj, indent=1, sort_keys=True).encode()


def build():
    data = {"arms": {}, "pooled_from": {}}
    labels = {}
    srcs = {}
    for tag in sorted(ARMS):
        a = ARMS[tag]
        raw = {}
        for name, key in (("data-e213.json", "data_sha256"), ("labels-e213.json", "labels_sha256")):
            b = open(os.path.join(DATA, a["folder"], name), "rb").read()
            got, lst = sha(b), listed(a["folder"], name)
            if got != a[key] or lst != a[key]:
                print(f"POOL REFUSED: {a['folder']}/{name} is {got}; pinned {a[key]}; its SHA256SUMS line {lst}")
                sys.exit(4)
            raw[name] = b
            print(f"input, arm {tag}: docs/reports/data/{a['folder']}/{name} sha256 {got} (= the pin and its directory's SHA256SUMS line)")
        src = json.loads(raw["data-e213.json"])
        lab = json.loads(raw["labels-e213.json"])
        if src.get("experiment") != "E213" or set((src.get("arms") or {})) != {tag} or set(lab) != {tag}:
            print(f"POOL REFUSED: arm {tag}'s data or labels are not one arm of E213 (arms {sorted(src.get('arms') or {})}, labels {sorted(lab)})")
            sys.exit(5)
        for k in ("experiment", "reducer"):
            if k not in data:
                data[k] = src.get(k)
            elif data[k] != src.get(k):
                print(f"POOL REFUSED: the two data files differ in '{k}' ({data[k]!r} and {src.get(k)!r})")
                sys.exit(5)
        extra = sorted(set(src) - {"arms", "experiment", "reducer"})
        if extra:
            print(f"POOL REFUSED: arm {tag}'s data file has top-level keys this script does not carry: {extra}")
            sys.exit(5)
        data["arms"][tag] = src["arms"][tag]
        labels[tag] = lab[tag]
        data["pooled_from"][tag] = {"data": f"docs/reports/data/{a['folder']}/data-e213.json", "data_sha256": a["data_sha256"],
                                    "labels": f"docs/reports/data/{a['folder']}/labels-e213.json", "labels_sha256": a["labels_sha256"],
                                    "data_commit": a["data_commit"]}
        srcs[tag] = (src, lab)
        arm = src["arms"][tag]
        npts = len(arm.get("points") or {})
        nruns = sum(len(p.get("runs") or []) for p in (arm.get("points") or {}).values())
        print(f"  arm {tag}: {npts} points with {nruns} point runs; smoke runs {len((arm.get('smoke') or {}).get('runs') or [])}; "
              f"tie runs {len((arm.get('ties') or {}).get('runs') or [])}; labels {json.dumps(lab[tag], sort_keys=True)}")
    bd, bl = dump(data), dump(labels)
    back, backl = json.loads(bd), json.loads(bl)
    for tag in sorted(ARMS):
        if back["arms"][tag] != srcs[tag][0]["arms"][tag] or backl[tag] != srcs[tag][1][tag]:
            print(f"POOL REFUSED: arm {tag} read back from the output differs from its input")
            sys.exit(6)
    if sorted(back["arms"]) != ["A", "B"] or sorted(backl) != ["A", "B"]:
        print("POOL REFUSED: the output does not hold exactly arms A and B")
        sys.exit(6)
    print(f"read back: each arm of the output equals its input arm (A and B); labels likewise")
    return bd, bl


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "build" and len(sys.argv) == 3:
        bd, bl = build()
        out = sys.argv[2]
        open(os.path.join(out, OUT_DATA), "wb").write(bd)
        open(os.path.join(out, OUT_LABELS), "wb").write(bl)
        print(f"wrote {OUT_DATA} ({len(bd)} bytes, sha256 {sha(bd)}) and {OUT_LABELS} ({len(bl)} bytes, sha256 {sha(bl)})")
        return 0
    if len(sys.argv) == 2 and sys.argv[1] == "check":
        bd, bl = build()
        ok = True
        for name, b in ((OUT_DATA, bd), (OUT_LABELS, bl)):
            p = os.path.join(HERE, name)
            have = open(p, "rb").read() if os.path.exists(p) else None
            same = have == b
            ok = ok and same
            print(f"{name}: {'equal to the rebuild' if same else 'DIFFERS from the rebuild'} (sha256 {sha(b)})")
        print("POOL-CHECK OK" if ok else "POOL-CHECK DIFFERS")
        return 0 if ok else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
