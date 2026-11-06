#!/usr/bin/env python3
"""E178 (Q146; the kit's dated note 1, KIT.md.dated-note-1.md section 4): the desk test of collect_e178_v2.sh, end to end, on the same
relabelled real session as selftest_collect_e178.py (E171's committed session, lab 91f8ae40, relabelled by that test's own rule into
E178's registered order: a plumbing test, whose verdicts mean nothing about one-number kinds and are never quoted). Three collector runs,
each from an empty output, with the check of C handed in by desktest_ccheck_standin_e178.py as v1's test does:
  V1   collect_e178.sh, v1 as committed: the reference;
  V2   collect_e178_v2.sh with no arm failing: scored.json, results.md, e178.json and runs.csv equal V1's byte for byte; "arms dropped: 0"
       and no arms-dropped.txt;
  V2X  collect_e178_v2.sh with two arms broken (E178_DESKTEST=1 only): gates_off's reduction made to fail (it is handed a pass directory,
       outside e178/, whose one telemetry line lacks its fields, so reduce_e78.py stops with a traceback) and auto_dips_removed's reduction overwritten so the scorer
       cannot read it. Both are dropped (arms-dropped.txt names each with
       its reason and no path), the session is scored again without them, the primary's rules and verdicts equal V1's, five arms are
       scored and none is in error, and the dropped arms' files sit in build/e178-dropped-arms/, outside the output;
  P    the desk-path gate as step 22 runs it (v3.1's nopath_q142s.py, forbidding the lab clone, over the whole output) on V1's, V2's and
       V2X's outputs: no hit in any; and on V2X's dropped files, to show what the drop keeps out of the data directory;
  R    each of the three stand-ins set without E178_DESKTEST=1: refused, exit 10, before anything runs.
It writes under the lab clone's build/ (ignored by git: the collector's own place), as selftest_collect_e178.py does, and removes what
it wrote.

    /usr/bin/python3 -B tools/claims-v3/e178/selftest_collect_e178_v2.py [--txt <out>] [--json <out>]
Exit 0 when every check passes. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e178_common as E  # noqa: E402
import selftest_collect_e178 as V1T  # noqa: E402  (its relabel and its constants, unchanged; nothing runs at import)

TOP = V1T.TOP
NOPATH = os.path.join(TOP, "tools", "claims-v3", "q141k-runbook", "v3.1", "nopath_q142s.py")
DROP = os.path.join(TOP, "build", "e178-dropped-arms")
LINES, RES = [], {}
KEEP = ("scored.json", "results.md", "e178.json", "runs.csv")


def check(name, ok, detail):
    RES[name] = {"pass": bool(ok), "detail": detail}
    LINES.append(f"{name}: {'PASS' if ok else 'FAIL'} - {detail}")


def strip(s):
    return s.replace(TOP + os.sep, "").replace(TOP, "<repo>")


def nopath(paths):
    r = subprocess.run(["/usr/bin/python3", "-B", NOPATH, "--forbid", TOP, *paths], capture_output=True, text=True, timeout=300)
    hits = [ln for ln in (r.stdout + r.stderr).splitlines() if ln.startswith(("HIT", "MISSING"))]
    return r.returncode, hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--txt")
    ap.add_argument("--json")
    a = ap.parse_args()
    raw = os.path.join(TOP, V1T.RAW_REL)
    out = os.path.join(TOP, V1T.OUT_REL)
    work = os.path.join(TOP, "build", "e178-desktest-work-v2")
    gone = (raw, os.path.join(TOP, "build", "e178-out"), work, DROP)
    for d in gone:
        shutil.rmtree(d, ignore_errors=True)
    items = {it["name"]: it for it in E.load_items()}
    snap = {}
    try:
        info = {}
        for po, pn in V1T.PASSMAP.items():
            info[pn] = V1T.relabel_pass(os.path.join(V1T.SRC, "aifoundry3", "e171", f"p{po}"), os.path.join(raw, "e178", f"p{pn}"), po, pn,
                                        items)
        shutil.copytree(os.path.join(V1T.SRC, "aifoundry3", "e171-smoke", "p17101"), os.path.join(raw, "e178-smoke", "p17801"))
        shutil.copytree(os.path.join(V1T.SRC, "aifoundry3", "e171-stoptest", "p17102"), os.path.join(raw, "e178-stoptest", "p17802"))
        os.makedirs(os.path.join(raw, "logs"))
        open(os.path.join(raw, "logs", "README.txt"), "w").write("desk test: no session logs\n")
        os.makedirs(os.path.join(raw, "desktest-broken", "p17819"))   # V2X: the pass directory a broken arm's reduction is handed: one
        open(os.path.join(raw, "desktest-broken", "p17819", "telemetry.jsonl"), "w").write('{"t_ms": 0}\n')   # sample, no fields
        ren = {f"c-log-p{po}.jsonl": f"c-log-p{pn}.jsonl" for po, pn in V1T.PASSMAP.items()}
        ren["c-log-p17101.jsonl"] = "c-log-p17801.jsonl"
        v = json.load(open(os.path.join(V1T.SRC, "ccheck", "ccheck-all.json")))
        for x in v["launches"]:
            x["log"] = ren.get(x["log"], x["log"])
        os.makedirs(work)
        vf = os.path.join(work, "verdicts-relabelled.json")
        json.dump(v, open(vf, "w"))
        check("R1 the relabel (selftest_collect_e178.py's rule)", all(i["runs_mapped"] == 76 for i in info.values()),
              "; ".join(f"p{p}: {i['runs_mapped']} slots from {i['e171_run_marks']} E171 runs" for p, i in info.items()))
        base = dict(os.environ, E178_DESKTEST="1", E178_CCHECK_STANDIN=os.path.join(HERE, "desktest_ccheck_standin_e178.py"),
                    E178_DESKTEST_VERDICTS=vf, E178_DATE="desktest", PY="/usr/bin/python3")
        base.pop("E178_DESKTEST_FAIL_REDUCE", None)
        base.pop("E178_DESKTEST_BREAK_JSON", None)

        def run(case, script, **extra):
            r = subprocess.run(["nice", "-n", "10", "bash", os.path.join(HERE, script), V1T.RAW_REL], cwd=TOP, env=dict(base, **extra),
                               capture_output=True, text=True, timeout=1500)
            log = strip(r.stdout + r.stderr)
            d = os.path.join(work, case)
            os.makedirs(d)
            open(os.path.join(d, "collect.log"), "w").write(log)
            for f in KEEP + ("arms-dropped.txt",):
                if os.path.exists(os.path.join(out, f)):
                    shutil.copyfile(os.path.join(out, f), os.path.join(d, f))
            prc, hits = nopath([out])
            files = sorted(os.listdir(out))
            snap[case] = {"rc": r.returncode, "log": log, "dir": d, "nopath_rc": prc, "nopath_hits": hits, "files": files}
            return snap[case]

        s1 = run("V1", "collect_e178.sh")
        check("V1 collect_e178.sh (v1, the reference)", s1["rc"] == 0 and "results.md written" in s1["log"],
              f"exit {s1['rc']}; " + "; ".join(ln for ln in s1["log"].splitlines() if ln.startswith(("passes reduced", "primary rc", "results.md"))))
        s2 = run("V2", "collect_e178_v2.sh")
        same = {f: open(os.path.join(s1["dir"], f), "rb").read() == open(os.path.join(s2["dir"], f), "rb").read() for f in KEEP}
        arm_rc = [ln for ln in s2["log"].splitlines() if " rc=" in ln and ln.split(" rc=")[0] in (
            "session-own", "auto, dips removed", "k frozen, dips kept", "leak-arm 0.1994", "leak-arm 0.3803", "leak-arm 0", "gates-off arm")]
        check("V2 collect_e178_v2.sh, no arm failing: equal to v1", s2["rc"] == 0 and all(same.values()) and "arms dropped: 0" in s2["log"]
              and not os.path.exists(os.path.join(s2["dir"], "arms-dropped.txt")) and len(arm_rc) == 7 and all(x.endswith("rc=0") for x in arm_rc),
              f"exit {s2['rc']}; byte for byte against V1: {same}; 'arms dropped: 0' {'arms dropped: 0' in s2['log']}; the 7 arms' reductions: "
              f"{len(arm_rc)} read, all rc 0 {all(x.endswith('rc=0') for x in arm_rc)}")
        s3 = run("V2X", "collect_e178_v2.sh", E178_DESKTEST_FAIL_REDUCE="gates_off", E178_DESKTEST_BREAK_JSON="auto_dips_removed")
        sj1 = json.load(open(os.path.join(s1["dir"], "scored.json")))
        sj3 = json.load(open(os.path.join(s3["dir"], "scored.json"))) if os.path.exists(os.path.join(s3["dir"], "scored.json")) else {}
        ad = open(os.path.join(s3["dir"], "arms-dropped.txt")).read() if os.path.exists(os.path.join(s3["dir"], "arms-dropped.txt")) else ""
        adl = [ln for ln in ad.splitlines()[1:] if ln.strip()]
        arms3 = sorted((sj3.get("arms") or {}).keys())
        want3 = sorted(n for n in sj1["arms"] if n not in ("gates_off", "auto_dips_removed"))
        prim_same = sj3.get("verdicts") == sj1["verdicts"] and (sj3.get("primary") or {}).get("rules") == sj1["primary"]["rules"]
        moved = sorted(os.listdir(DROP)) if os.path.isdir(DROP) else []
        moved_files = {n: sorted(os.listdir(os.path.join(DROP, n))) for n in moved}
        in_out = [f for f in s3["files"] if "gatesoff" in f or "auto-nodips" in f]
        dprc, dhits = nopath([DROP]) if os.path.isdir(DROP) else (None, [])
        check("V2X two arms broken: both dropped, the session scored again without them",
              s3["rc"] == 0 and "results.md written" in s3["log"] and len(adl) == 2
              and adl[0].startswith("gates_off: its reduction exited ") and adl[1].startswith("auto_dips_removed: the scorer could not read it (")
              and "scored again without the dropped arm(s): auto_dips_removed (rc 0)" in s3["log"] and arms3 == want3
              and not any("error" in x for x in sj3["arms"].values()) and prim_same and not in_out
              and moved == ["auto_dips_removed", "gates_off"] and "arms dropped: 2" in s3["log"],
              f"exit {s3['rc']}; arms-dropped.txt: {adl}; scored again: "
              f"{[ln for ln in s3['log'].splitlines() if ln.startswith('scored again')]}; arms scored {arms3} (none in error: "
              f"{not any('error' in x for x in (sj3.get('arms') or {}).values())}); the primary's verdicts and rules equal V1's: {prim_same}; "
              f"the dropped arms' files in the output: {in_out or 'none'}; moved to build/e178-dropped-arms/: {moved_files}")
        check("P the desk-path gate (nopath_q142s.py, step 22's) over each whole output",
              all(snap[c]["nopath_rc"] == 0 for c in ("V1", "V2", "V2X")),
              "; ".join(f"{c}: rc {snap[c]['nopath_rc']}, {len(snap[c]['nopath_hits'])} hit(s) {snap[c]['nopath_hits'][:3]}" for c in ("V1", "V2", "V2X"))
              + f"; beside it, the dropped files V2X kept out of the output: rc {dprc}, {len(dhits)} hit(s) "
              + f"({'the failed reduction carries a desk path, so the drop is what keeps the gate clean' if dprc == 3 else 'no desk path in them'})")
        refused = {}
        for var in ("E178_CCHECK_STANDIN", "E178_DESKTEST_FAIL_REDUCE", "E178_DESKTEST_BREAK_JSON"):
            env = {k: x for k, x in os.environ.items() if not k.startswith("E178_")}
            env.update({var: "x", "PY": "/usr/bin/python3"})
            st = subprocess.run(["bash", os.path.join(HERE, "collect_e178_v2.sh"), V1T.RAW_REL], cwd=TOP, capture_output=True, text=True,
                                timeout=120, env=env)
            refused[var] = (st.returncode, "read only with E178_DESKTEST=1" in st.stdout)
        check("R the stand-ins refused outside the desk test", all(v == (10, True) for v in refused.values()),
              "; ".join(f"{k} set without E178_DESKTEST=1: exit {v[0]}" for k, v in refused.items()))
    finally:
        for d in gone:
            shutil.rmtree(d, ignore_errors=True)
    ok = all(v["pass"] for v in RES.values())
    LINES.append(f"SELFTEST-COLLECT-E178-V2 {'PASS' if ok else 'FAIL'}: {sum(1 for v in RES.values() if v['pass'])} of {len(RES)} checks "
                 f"(build/e178-raw-desktest, build/e178-out, build/e178-dropped-arms and the work directory removed)")
    txt = "\n".join(LINES) + "\n"
    print(txt, end="")
    if a.txt:
        open(a.txt, "w").write(txt)
    if a.json:
        open(a.json, "w").write(json.dumps(RES, indent=1, sort_keys=True) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
