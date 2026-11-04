#!/usr/bin/env python3
"""E166 (Q141(h), the fix pass): the parent run's registered verdicts, re-derived before any E166 data (E166.md.dated-note-2.md).

Section 26 of the round's rules: "Each scorer is self-tested on its parent run's committed data. The self-test must reproduce the parent's
registered verdicts, and its output is committed." score_e166.py's self-test gives back Q140(e)'s posthoc.json E154 figures exactly, but not
E154's own registered verdicts (scored.json's eleven, all PASS, on Q139(e)'s predictions). This script adds that:
  (1) E154's registered scorer, tools/claims-v3/e154/score_e154.py, unchanged, run exactly as E154's data README gives the command, on
      E154's committed pass (docs/reports/data/2026-11-03-e154-heat-e2e-aifoundry3/aifoundry3/e154/p15420), into a temporary file: it must
      equal the committed scored.json byte for byte, and its eleven verdicts must read as registered (every one PASS);
  (2) score_e166.py --self-test, unchanged, re-run: it must pass and equal the committed logs/selftest-e166-kit.json byte for byte.
Nothing is fitted; nothing in the repo is written (the outputs go to a temporary directory, removed after).

    /usr/bin/python3 tools/claims-v3/e166/selftest_parent_e166.py [--json <out>]
numpy 1.26.4, Python 3.9 (the Intel's /usr/bin/python3), as both scorers need.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
E154D = "docs/reports/data/2026-11-03-e154-heat-e2e-aifoundry3"
PASS_DIR = f"{E154D}/aifoundry3/e154/p15420"
FROZEN = {
    "tools/claims-v3/e154/score_e154.py": "c911d4d9e6b2cc5769e6824c332e17299718ba3fcd409011be9c16e73ffb0369",
    f"{E154D}/scored.json": "9dc62828bd10d8469a1420ae547f40bbab16d2391bfb8234d206267925b560a8",
    "tools/claims-v3/e166/score_e166.py": "752dc6b15d618d7d0b8d894628ee877532d357d62a231d9b8d09b81f8a95bba0",
    "tools/claims-v3/e166/logs/selftest-e166-kit.json": "76708f57133b91a353b38b5f44364b69d4d0eb1aa806eb0cf4097a8bb8e0b5e0",
}
WANT_VERDICTS = {"H_M b": "PASS", "H_M c_replicate": "PASS", "H_M A": "PASS", "K_S E": "PASS", "K_S A": "PASS", "K_Q E": "PASS",
                 "K_Q A": "PASS", "K_L E": "PASS", "K_L A": "PASS", "K_O E": "PASS", "K_O A": "PASS"}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def run(cmd, timeout):
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", VECLIB_MAXIMUM_THREADS="1",
               PYTHONDONTWRITEBYTECODE="1")
    p = subprocess.run(cmd, cwd=TREE, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    return p.returncode, p.stderr.decode("utf-8", "replace")[-600:]


def main():
    jout = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None
    res = {"note": __doc__.split("\n\n")[1].strip(), "frozen_sha256": {}, "problems": []}
    for rel, h in FROZEN.items():
        got = sha(os.path.join(TREE, rel)) if os.path.exists(os.path.join(TREE, rel)) else "missing"
        res["frozen_sha256"][rel] = got[:16]
        if got != h:
            res["problems"].append(f"{rel}: {got[:16]} != {h[:16]}")
    if res["problems"]:
        print(json.dumps(res, indent=1))
        raise SystemExit("REFUSED: a frozen input differs")
    td = tempfile.mkdtemp(prefix="e166-parent-")
    try:
        out1 = os.path.join(td, "scored.json")
        rc, err = run([sys.executable, "tools/claims-v3/e154/score_e154.py", PASS_DIR, "--json", out1], 900)
        same = os.path.exists(out1) and open(out1, "rb").read() == open(os.path.join(TREE, E154D, "scored.json"), "rb").read()
        v = json.load(open(out1)).get("verdicts") if os.path.exists(out1) else None
        res["E154_registered_scorer"] = {"command": f"python3 tools/claims-v3/e154/score_e154.py {PASS_DIR} --json <tmp>/scored.json", "rc": rc,
                                         "byte_identical_to_committed_scored_json": same, "verdicts": v,
                                         "verdicts_as_registered": v == WANT_VERDICTS, "n_verdicts": len(v or {}),
                                         "n_PASS": sum(1 for x in (v or {}).values() if x == "PASS")}
        if rc != 0:
            res["problems"].append(f"score_e154.py rc {rc}: {err}")
        if not same:
            res["problems"].append("score_e154.py's output differs from the committed scored.json")
        if v != WANT_VERDICTS:
            res["problems"].append(f"E154's verdicts {v} != the registered {WANT_VERDICTS}")
        out2 = os.path.join(td, "selftest-e166.json")
        rc2, err2 = run([sys.executable, "tools/claims-v3/e166/score_e166.py", "--self-test", "--json", out2], 900)
        same2 = os.path.exists(out2) and open(out2, "rb").read() == open(os.path.join(HERE, "logs", "selftest-e166-kit.json"), "rb").read()
        st = json.load(open(out2)) if os.path.exists(out2) else {}
        res["score_e166_self_test"] = {"rc": rc2, "self_test_ok": st.get("self_test_ok"),
                                       "byte_identical_to_committed_selftest_e166_kit_json": same2}
        if rc2 != 0 or not st.get("self_test_ok"):
            res["problems"].append(f"score_e166.py --self-test rc {rc2}: {err2}")
        if not same2:
            res["problems"].append("score_e166.py --self-test differs from logs/selftest-e166-kit.json")
    finally:
        shutil.rmtree(td, ignore_errors=True)
    res["self_test_ok"] = not res["problems"]
    txt = json.dumps(res, indent=1)
    if jout:
        open(jout, "w").write(txt + "\n")
    print(txt)
    sys.exit(0 if res["self_test_ok"] else 1)


if __name__ == "__main__":
    main()
