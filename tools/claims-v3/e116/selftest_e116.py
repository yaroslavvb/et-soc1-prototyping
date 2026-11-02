#!/usr/bin/env python3
"""E116 self-test (desk, standard library only): score_e116.py on E88's own card-1 data and on made-up read-backs.

    python3 tools/claims-v3/e116/selftest_e116.py <scratch dir>

1. a read-back equal to accum.c on all 22 tiles -> R0 PASS; one word changed in one tile -> R0 FAIL; 21 reads -> not scored;
2. E88's own reduction and score_e88 output as if they were E116's: S PASS in all three formats (the same shares), W PASS
   (E88's watts against themselves x 1.03), H PASS 13 of 13, P 17 of 19 (E88's own tally);
3. E88's reduction cut to three passes -> S, W, H, P, T not scored.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
E88 = os.path.join(ROOT, "docs/reports/data/2026-10-31-e88-result-path")


def fake_readback(path, spoil=None, drop=None):
    e = json.load(open(os.path.join(HERE, "expect-e116.json")))
    with open(path, "w") as f:
        for k, v in e["tiles"].items():
            if k == drop:
                continue
            hx = v["accum_hex"]
            if k == spoil:
                hx = ("%08x" % (int(hx[:8], 16) ^ 1)) + hx[8:]
            import hashlib
            h = hashlib.sha256(bytes.fromhex(hx)).hexdigest()
            f.write(json.dumps({"tile": k, "n": v["n"], "rc": 0, "distinct_c": 1, "groups": {h: {"minions": 1024, "first_minion": 0, "hex": hx}},
                                "equal_accum": h == v["accum_sha256"], "sparsity": {"ok": True}}) + "\n")


def run(args):
    p = subprocess.run([sys.executable, os.path.join(HERE, "score_e116.py")] + args, capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr[-600:]


def main():
    s = sys.argv[1]
    os.makedirs(s, exist_ok=True)
    ok = True
    for name, kw, want in (("all", {}, "PASS"), ("spoil", {"spoil": "fp16.r_abs"}, "FAIL"), ("drop", {"drop": "int8.r_walk"}, "not scored")):
        rb = os.path.join(s, f"rb-{name}.jsonl")
        fake_readback(rb, **kw)
        rc, out, err = run(["--red", os.path.join(E88, "e88.json"), "--e88rules", os.path.join(E88, "scored.json"),
                            "--readback", rb, "--json", os.path.join(s, f"sc-{name}.json")])
        got = json.load(open(os.path.join(s, f"sc-{name}.json")))["E116-R0"]["verdict"] if rc == 0 else f"rc {rc} {err}"
        print(f"read-back {name}: R0 {got} (want {want})")
        ok &= got == want
    sc = json.load(open(os.path.join(s, "sc-all.json")))["power"]
    S = {f: v["verdict"] for f, v in sc["E116-S"].items()}
    W = {f: v["verdict"] for f, v in sc["E116-W"].items()}
    print("E88 as E116: S", S, "W", W, "H", sc["E116-H"]["verdict"], sc["E116-H"]["same"], "P", sc["E116-P"]["pass"], "of", sc["E116-P"]["of"],
          "T", sc["E116-T"]["verdict"], "kept", sc["kept_passes"])
    ok &= all(v == "PASS" for v in S.values()) and all(v == "PASS" for v in W.values()) and sc["E116-H"]["verdict"] == "PASS" and sc["E116-P"]["pass"] == 17
    red = json.load(open(os.path.join(E88, "e88.json")))
    keep = sorted(red["per_pass"])[:3]
    red["per_pass"] = {k: red["per_pass"][k] for k in keep}
    json.dump(red, open(os.path.join(s, "red3.json"), "w"))
    rc, out, err = run(["--red", os.path.join(s, "red3.json"), "--json", os.path.join(s, "sc-3.json"), "--md", os.path.join(s, "sc-3.md")])
    v = json.load(open(os.path.join(s, "sc-3.json")))["power"]["E116-S"]["verdict"] if rc == 0 else f"rc {rc} {err}"
    print("three passes: S", v, "(want not scored)")
    ok &= v == "not scored"
    rc, out, err = run(["--red", os.path.join(E88, "e88.json"), "--e88rules", os.path.join(E88, "scored.json"), "--readback", os.path.join(s, "rb-all.jsonl"),
                        "--arm", "leak0=" + os.path.join(E88, "e88-leak0.json"), "--json", os.path.join(s, "sc-md.json"), "--md", os.path.join(s, "sc-md.md")])
    print("with an arm and the markdown:", "rc", rc, out[:300], err[-300:])
    ok &= rc == 0
    print("SELFTEST", "PASS" if ok else "FAIL")


if __name__ == "__main__":
    main()
