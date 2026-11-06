#!/usr/bin/env python3
"""E178 (Q146, the kit): the desk test of the collection, end to end: collect_e178.sh (the check of C's gate, the primary reduction and
its seven arms through reduce_e178.py, score_e178.py with every arm, the copies) on REAL card files in E178's layout. No E178 datum exists,
so the session is E171's committed one (aifoundry3, 5 Nov 2026, lab 91f8ae40) RELABELLED into E178's registered order: a plumbing test,
whose verdicts mean nothing about one-number kinds and are never quoted as E178's.

THE RELABEL (each of E171's four kept passes 17110-17113 becomes 17810-17813; the smoke 17101 becomes 17801, the stop-path test 17102
17802): every E178 slot of plan-e178.json takes one E171 run, by rule, never by its value: the tie its tie (first and last); an anchor
slot E171's run of the same anchor in the same segment; any other slot the next unused E171 pool run of the same format, in E171's order.
The E171 runs left over (8 a pass; 7 in 17110, where E78's launch rule skipped one) are dropped with their marks and launch records. Every launch record, mark, telemetry sample, config
read and C log is E171's, byte for byte, but for the item, pos, segment and block fields of the relabelled runs; each relabelled run's
tile dump is the registered tile of its new item (so E78's per-run dump gate reads the tile the label names). The check of C is not
recomputed (6 minutes on 2 cores, more than section 28 allows here): desktest_ccheck_standin_e178.py hands collect_e178.sh the verdicts
ccheck.py wrote for these very launches on 5 Nov, with each verdict's log name relabelled.

It writes under the lab clone's build/ (ignored by git: the collector's own place) build/e178-raw-desktest/ and the collector's
build/e178-out/desktest-e178-one-number-aifoundry3/, reads the outputs, writes its record, and removes both.

    /usr/bin/python3 -B tools/claims-v3/e178/selftest_collect_e178.py [--txt <out>] [--json <out>] [--keep <dir outside the repo>]
Exit 0 when every check passes. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import json
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e178_common as E  # noqa: E402

SRC = os.path.join(TOP, "docs", "reports", "data", "2026-11-05-e171-blind8-aifoundry3")
RAW_REL = "build/e178-raw-desktest"
OUT_REL = "build/e178-out/desktest-e178-one-number-aifoundry3"
PASSMAP = {17110: 17810, 17111: 17811, 17112: 17812, 17113: 17813}
LINES, RES = [], {}


def jl(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as f:
        return [json.loads(x) for x in f if x.strip().startswith("{")]


def wjl(path, rows):
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def relabel_pass(src, dst, p_old, p_new, items):
    marks = jl(os.path.join(src, "marks.jsonl"))
    runs = jl(os.path.join(src, "runs.jsonl"))
    rmarks = [m for m in marks if m["kind"] == "run"]
    typ = {(r["item"], r["pos"]): r["type"] for r in runs}
    ties = [m for m in rmarks if m["item"] == "anchor_pi"]
    anc = {(m["item"], m.get("segment")): m for m in rmarks if m["item"] in E.ANCHORS}
    pool = {t: [m for m in rmarks if m["item"] != "anchor_pi" and m["item"] not in E.ANCHORS and typ.get((m["item"], m["pos"])) == t]
            for t in ("fp32", "fp16", "int8")}
    for t in pool:
        pool[t].sort(key=lambda m: m["pos"])
    mp = {}
    used_t = {t: 0 for t in pool}
    nt = 0
    for j, (n, s) in enumerate(E.order_by_rule("aifoundry3", p_new)):
        if n == "anchor_pi":
            m = ties[nt]
            nt += 1
        elif n in E.ANCHORS:
            m = anc[(n, s)]
        else:
            t = n.split(".")[0]
            m = pool[t][used_t[t]]
            used_t[t] += 1
        mp[(m["item"], m["pos"])] = (n, j, s)
    out_marks, dropped = [], 0
    for m in marks:
        m = dict(m)
        if m["kind"] == "run":
            k = (m["item"], m["pos"])
            if k not in mp:
                dropped += 1
                continue
            m["item"], m["pos"], m["segment"] = mp[k]
        if m.get("block") == p_old:
            m["block"] = p_new
        out_marks.append(m)
    out_runs = []
    for r in runs:
        k = (r["item"], r["pos"])
        if k not in mp:
            continue
        r = dict(r)
        n, j, s = mp[k]
        r.update(item=n, pos=j, segment=s, block=p_new, kind_name=n.split(".", 1)[1] if "." in n else r.get("kind_name"))
        out_runs.append(r)
    os.makedirs(os.path.join(dst, "tiles"), exist_ok=True)
    for f in ("block.json", "config_start.json", "config_end.json", "telemetry.jsonl.gz", "c-log.jsonl.gz"):
        shutil.copyfile(os.path.join(src, f), os.path.join(dst, f))
    cfg = json.load(open(os.path.join(src, "configs.json")))
    cfg["args"]["first_block"] = p_new
    cfg["desk_test"] = f"E171 pass {p_old} relabelled into E178's pass {p_new} by selftest_collect_e178.py (plumbing only)"
    json.dump(cfg, open(os.path.join(dst, "configs.json"), "w"), indent=1)
    wjl(os.path.join(dst, "marks.jsonl"), out_marks)
    wjl(os.path.join(dst, "runs.jsonl"), out_runs)
    shutil.copyfile(os.path.join(src, "tiles", f"anchor_pi.b{p_old}.bin"), os.path.join(dst, "tiles", f"anchor_pi.b{p_new}.bin"))
    for n in sorted({v[0] for v in mp.values()} - {"anchor_pi"}):
        shutil.copyfile(os.path.join(TOP, items[n]["tile"]), os.path.join(dst, "tiles", f"{n}.b{p_new}.bin"))
    json.dump([{"pos": j, "item": n, "segment": s} for (n, j, s) in sorted(mp.values(), key=lambda v: v[1])],
              open(os.path.join(dst, "plan.json"), "w"), indent=0)
    return {"runs_mapped": len(mp), "run_marks_dropped": dropped, "e171_run_marks": len(rmarks), "launch_records": len(out_runs)}


def check(name, ok, detail):
    RES[name] = {"pass": bool(ok), "detail": detail}
    LINES.append(f"{name}: {'PASS' if ok else 'FAIL'} - {detail}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--txt")
    ap.add_argument("--json")
    ap.add_argument("--keep", help="a directory outside the repository to copy results.md, scored.json and the collector's log into")
    a = ap.parse_args()
    raw = os.path.join(TOP, RAW_REL)
    out = os.path.join(TOP, OUT_REL)
    work = os.path.join(TOP, "build", "e178-desktest-work")
    for d in (raw, os.path.join(TOP, "build", "e178-out"), work):
        shutil.rmtree(d, ignore_errors=True)
    items = {it["name"]: it for it in E.load_items()}
    try:
        info = {}
        for po, pn in PASSMAP.items():
            info[pn] = relabel_pass(os.path.join(SRC, "aifoundry3", "e171", f"p{po}"), os.path.join(raw, "e178", f"p{pn}"), po, pn, items)
        shutil.copytree(os.path.join(SRC, "aifoundry3", "e171-smoke", "p17101"), os.path.join(raw, "e178-smoke", "p17801"))
        shutil.copytree(os.path.join(SRC, "aifoundry3", "e171-stoptest", "p17102"), os.path.join(raw, "e178-stoptest", "p17802"))
        os.makedirs(os.path.join(raw, "logs"))
        open(os.path.join(raw, "logs", "README.txt"), "w").write("desk test: no session logs\n")
        ren = {f"c-log-p{po}.jsonl": f"c-log-p{pn}.jsonl" for po, pn in PASSMAP.items()}
        ren["c-log-p17101.jsonl"] = "c-log-p17801.jsonl"
        v = json.load(open(os.path.join(SRC, "ccheck", "ccheck-all.json")))
        for x in v["launches"]:
            x["log"] = ren.get(x["log"], x["log"])
        os.makedirs(work)
        vf = os.path.join(work, "verdicts-relabelled.json")
        json.dump(v, open(vf, "w"))
        check("R1 the relabel", all(i["runs_mapped"] == 76 and i["run_marks_dropped"] == i["e171_run_marks"] - 76 for i in info.values()),
              "; ".join(f"p{p}: {i['runs_mapped']} slots filled from {i['e171_run_marks']} E171 runs ({i['run_marks_dropped']} dropped), "
                        f"{i['launch_records']} launch records" for p, i in info.items()))
        env = dict(os.environ, E178_DESKTEST="1", E178_CCHECK_STANDIN=os.path.join(HERE, "desktest_ccheck_standin_e178.py"),
                   E178_DESKTEST_VERDICTS=vf, E178_DATE="desktest", PY="/usr/bin/python3")
        r = subprocess.run(["nice", "-n", "10", "bash", os.path.join(HERE, "collect_e178.sh"), RAW_REL], cwd=TOP, env=env,
                           capture_output=True, text=True, timeout=1500)
        log = (r.stdout + r.stderr).replace(TOP + os.sep, "").replace(TOP, "<repo>")
        open(os.path.join(work, "collect.log"), "w").write(log)
        rcs = {k: ("rc=0" in ln) for ln in log.splitlines() for k in ("primary", "session-own", "auto, dips removed", "k frozen, dips kept",
                                                                       "leak-arm 0.1994", "leak-arm 0.3803", "leak-arm 0", "gates-off arm")
               if ln.startswith(k + " rc=")}
        check("R2 the collector", r.returncode == 0 and "passes reduced: 4" in log and "results.md written" in log and len(rcs) == 8
              and all(rcs.values()) and "sessions that must carry a C log: 5; C logs found: 5" in log,
              f"collect_e178.sh exit {r.returncode}; " + "; ".join(ln for ln in log.splitlines()
                                                                if ln.startswith(("passes reduced", "sessions that must", "ccheck rc", "primary rc",
                                                                                  "results.md")))
              + f"; the primary and its 7 arms exit 0: {all(rcs.values())} ({len(rcs)} read)")
        sj = json.load(open(os.path.join(out, "scored.json")))
        red = json.load(open(os.path.join(out, "e178.json")))
        pr = sj["primary"]
        cc = pr["rules"]["E178-C"]
        cpl = {rule: {p: v["couples"] for p, v in pr["rules"][rule]["per_pass"].items()} for rule in ("E178-H-int8", "E178-H-fp32", "E178-H-fp16",
                                                                                                         "E178-U")}
        allk = all(all(k in red["per_pass"][str(p)] for k in E.E178_NAMES) for p in red["passes"])
        check("R3 the scored session", sj["c_sessions"]["ok"] and sj["c_sessions"]["listed"] == 5 and cc["verdict"] == "PASS"
              and red["passes"] == [17810, 17811, 17812, 17813] and allk and all(all(n == 3 for n in v.values()) for v in cpl.values())
              and sorted(pr["scale"]["anchors_used"]) == ["fp16.randn", "fp32.randn"] and set(sj["verdicts"]) == set(sj["primary"]["verdicts"])
              and len(sj["arms"]) == 7 and not any("error" in x for x in sj["arms"].values()),
              f"C sessions {sj['c_sessions']['listed']} listed, all checked {sj['c_sessions']['ok']}; E178-C {cc['verdict']} ({cc['PASS']} of "
              f"{cc['launches']} launches of the 40 kinds); kept passes {red['passes']}; all 40 kinds in every pass {allk}; complete couples "
              f"{ {k: sorted(set(v.values())) for k, v in cpl.items()} }; s {pr['scale']['s_float']:.5f} from {sorted(pr['scale']['anchors_used'])}; "
              f"7 arms scored, none in error; verdicts written for {len(sj['verdicts'])} rules (meaningless here: E171's tiles under E178's labels)")
        RES["verdicts_of_the_relabelled_session_not_quotable"] = sj["verdicts"]
        files = sorted(os.listdir(out))
        check("R4 the data directory's files", all(f in files for f in ("e178.json", "runs.csv", "scored.json", "results.md", "code.sha256",
                                                                      "ccheck", "aifoundry3", "logs")),
              f"{len(files)} entries: " + ", ".join(files[:40]))
        st = subprocess.run(["bash", os.path.join(HERE, "collect_e178.sh"), RAW_REL], cwd=TOP, capture_output=True, text=True, timeout=120,
                            env=dict(os.environ, E178_CCHECK_STANDIN="x", PY="/usr/bin/python3"))
        check("R5 the stand-in refused outside the desk test", st.returncode == 10 and "read only with E178_DESKTEST=1" in st.stdout,
              f"E178_CCHECK_STANDIN set without E178_DESKTEST=1: exit {st.returncode}")
        if a.keep:
            os.makedirs(a.keep, exist_ok=True)
            for f in ("results.md", "scored.json"):
                shutil.copyfile(os.path.join(out, f), os.path.join(a.keep, f))
            shutil.copyfile(os.path.join(work, "collect.log"), os.path.join(a.keep, "collect.log"))
    finally:
        for d in (raw, os.path.join(TOP, "build", "e178-out"), work):
            shutil.rmtree(d, ignore_errors=True)
    ok = all(v["pass"] for v in RES.values() if isinstance(v, dict) and "pass" in v)
    LINES.append(f"SELFTEST-COLLECT-E178 {'PASS' if ok else 'FAIL'}: {sum(1 for v in RES.values() if isinstance(v, dict) and v.get('pass'))} "
                 f"of {sum(1 for v in RES.values() if isinstance(v, dict) and 'pass' in v)} checks (build/e178-raw-desktest and build/e178-out "
                 f"removed)")
    txt = "\n".join(LINES) + "\n"
    print(txt, end="")
    if a.txt:
        open(a.txt, "w").write(txt)
    if a.json:
        open(a.json, "w").write(json.dumps(RES, indent=1, sort_keys=True) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
