#!/usr/bin/env python3
"""E213 Amendment A3 (Q219, lane a3-e213, Wed 18 Nov 2026, before any datum of E213's arm B): THE DESK TEST OF A3'S ORDER, ITS WRAPPER, THE
RUNNER THROUGH IT AND THE SCORER'S READING BY POINT, at the desk, on the doubles (tools/claims-v3/e213/fake_card_e213.py): no device, no box.
desk/selftest_a3_e213.sh runs it first (its runbook cases follow). Run it ONLY inside a sandbox with no /dev/et* and an empty /run/lock (the
round's nodev.sh on aifoundry2), never while THE QUIET DESK FLAG stands (its sessions start the doubles' hosts). Every number here comes from the
doubles (MM1-v3's frozen arm B forecast driven through a toy card): a desk check of code, not a measurement and not a reading of E213. Cases:
  O1  `run_e213_a3.py check`: "A3-ORDER OK: arm B 85 runs, ...", exit 0
  O2  `run_e213_a3.py order`: exit 0; 85 run lines; the last eight the moved ones; the multiset line "yes"
  O3  A3'S ORDER RE-DERIVED HERE, independently of the wrapper, from points-e213.json's registered order: the sequence file's 85 runs equal it;
      the ties t02 at runs 1, 39 and 77; the last eight runs pass 1's k40 k37 k38 k39 then pass 2's k39 k38 k37 k40; the other 77 in their
      registered relative order; n = 1..85; registered_n a bijection onto 1..85 naming each run's registered place; the same multiset of (block,
      point); every registered run's (block, point) once
  O4  THE CHECK REFUSES (each in its own scratch copy of the files it reads): (a) the sequence file one byte changed: A3-STOP (its pin), exit 3;
      (b) a sequence file with runs 78 and 79 swapped and a wrapper pinned to IT: A3-STOP (not A3's order derived from the registered one), exit
      3 - the check is not the pin alone; (c) points-e213.json one byte changed: A3-STOP (the registered file), exit 3; (d) `session --arm A`:
      exit 2, A3-STOP (arm B's alone), nothing written in --out; (e) the device-command checker missing: A3-STOP (the audit of A3's two session
      files did not read GO), exit 3
  O5  THE REPLACEMENT in a process: the wrapper's a3_sequence('B') gives 85 runs {n, block, id, name}, each name the registered name of its id;
      a3_sequence('A') is the kit's registered arm A order; a3_sequence('C') raises KeyError as the kit's does; the kit's own self-check
      (e213_common.py, a separate process: the registration unpatched) PASS
  R1  THE RUNNER THROUGH THE WRAPPER, the whole order (`session --dry --arm B --sequence plan`) at a tiny scale: rc 0; runner.out's first line
      A3-ORDER OK; queue.json 85 runs, every one ran, in A3's order (keys NNN-block-id, n = 1..85); every process's argv the point's registered
      one (host and ELF by its loop, its host_args, --seconds 6 --budget 7.5, --kernel, --stop-file, under the runner's timeout 10, never -k),
      every process gated; the session log's run lines in A3's order
  R2  END TO END, BOTH ORDERS: one session through the wrapper (A3's order) and one through the kit's runner (the registered order), side by
      side on the doubles with their watts and seconds at MM1-v3's frozen arm B forecast (leakage off, a 6 s rest read: the reducer's registered
      5 s window); each through the reducer and the FROZEN scorer: rc 0 each; the A3 session's runs in A3's order, the registered session's in
      the registered order; the same 41 points with 2 runs each; every point's cycles (wall and counter) and seconds EQUAL; its W over idle and
      rest within 0.1 W (the doubles add a seeded 0.05 W Gaussian to every board sample, drawn in sampling order, so the two sessions' power
      medians differ by that noise: fake_card_e213.py); every verdict, count, cell's pass and head-to-head verdict EQUAL
  S1  THE SCORER READS RUNS BY POINT, NOT BY PLACE: R2's A3 data with every run's n replaced by its registered place, and again with every n
      reversed (86 - n) and each point's runs listed backwards: the frozen scorer's output EQUAL to the A3 data's in everything but the run
      numbers inside message strings
    /usr/bin/python3 -B tools/claims-v3/e213-a3/desk/selftest_order_a3_e213.py <scratch dir> [--only O1 R1 ...]   (prints SELFTEST-ORDER-A3 n of m PASS)
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
A3 = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(A3, "..", "..", ".."))
E213 = os.path.join(REPO, "tools", "claims-v3", "e213")
WRAP = os.path.join(A3, "run_e213_a3.py")
RUNNER = os.path.join(E213, "run_e213.py")
sys.path.insert(0, E213)
import e213_common as C  # noqa: E402

PY = "/usr/bin/python3"
MOVED = ("k37", "k38", "k39", "k40")
TAIL = [("pass1", "k40"), ("pass1", "k37"), ("pass1", "k38"), ("pass1", "k39"), ("pass2", "k39"), ("pass2", "k38"), ("pass2", "k37"), ("pass2", "k40")]
RUNNUM = re.compile(r"\brun (-?[0-9]+)\b")


class T:
    def __init__(self, S, only):
        self.S, self.only, self.n, self.ok = S, set(only or []), 0, 0

    def want(self, name):
        return not self.only or name in self.only

    def case(self, name, good, detail):
        self.n += 1
        self.ok += 1 if good else 0
        print(f"{name}: {'PASS' if good else 'FAIL'} - {detail}", flush=True)


def run(cmd, cwd=REPO, env=None, timeout=600):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env, timeout=timeout)
    return r.returncode, r.stdout + r.stderr


def seq_file(top=A3):
    return json.load(open(os.path.join(top, "sequence-B-a3.json")))


def a3_expected():
    """A3's order re-derived here, from the registered order, without the wrapper's code"""
    reg = C.sequence("B")
    pts = C.points()["arms"]["B"]["points"]
    lnc = sorted(p["id"] for p in pts if p["loop"] == "rgm136 gemmLnc")
    keep = [r for r in reg if r["id"] not in lnc]
    move = [r for r in reg if r["id"] in lnc]
    return reg, lnc, [(i, r["block"], r["id"], r["n"]) for i, r in enumerate(keep + move, 1)]


def scratch_copy(S, tag, files_e213=("e213_common.py", "points-e213.json", "plan-e213.json", "kernel-e213.json")):
    """a scratch tree holding the files the wrapper's check reads: tools/claims-v3/e213/<those> and the whole of tools/claims-v3/e213-a3/"""
    top = os.path.join(S, tag)
    if os.path.exists(top):
        shutil.rmtree(top)
    os.makedirs(os.path.join(top, "tools", "claims-v3", "e213"))
    for f in files_e213:
        shutil.copy2(os.path.join(E213, f), os.path.join(top, "tools", "claims-v3", "e213", f))
    for f in ("dmcmd_audit_v2.py", "dmcmd_table_v2.json"):         # the device-command checker the wrapper's check runs on A3's two files
        shutil.copy2(os.path.join(REPO, "tools", "claims-v3", f), os.path.join(top, "tools", "claims-v3", f))
    shutil.copytree(A3, os.path.join(top, "tools", "claims-v3", "e213-a3"), ignore=shutil.ignore_patterns("__pycache__", "logs", "desk"))
    return top


def mask(obj):
    """the scored structure with run numbers inside message strings masked (the only place a scorer output carries a run's place)"""
    if isinstance(obj, dict):
        return {k: mask(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [mask(v) for v in obj]
    if isinstance(obj, str):
        return RUNNUM.sub("run <n>", obj)
    return obj


def diff_paths(a, b, path="", out=None, tol=1e-9):
    out = [] if out is None else out
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append(f"{path}/{k}: only in one")
            else:
                diff_paths(a[k], b[k], f"{path}/{k}", out, tol)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path}: lengths {len(a)} vs {len(b)}")
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                diff_paths(x, y, f"{path}[{i}]", out, tol)
    elif isinstance(a, float) or isinstance(b, float):
        try:
            if abs(float(a) - float(b)) > tol * max(1.0, abs(float(a)), abs(float(b))):
                out.append(f"{path}: {a} vs {b}")
        except (TypeError, ValueError):
            out.append(f"{path}: {a!r} vs {b!r}")
    elif a != b:
        out.append(f"{path}: {str(a)[:60]!r} vs {str(b)[:60]!r}")
    return out


def score(S, tag, data):
    dj, sj = os.path.join(S, f"{tag}-data.json"), os.path.join(S, f"{tag}-scored.json")
    json.dump(data, open(dj, "w"), indent=1, sort_keys=True)
    rc, out = run([PY, "-I", "-B", os.path.join(E213, "score_e213.py"), dj, "--out", sj])
    return rc, (json.load(open(sj)) if os.path.exists(sj) else {}), out


def session(S, tag, runner, scale, extra, env_extra=None):
    d = os.path.join(S, tag)
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    out = os.path.join(d, "T")
    e = {k: v for k, v in os.environ.items() if not k.startswith("E213_FAKE_")}
    e.update({"E213_FAKE_SCALE": scale, "E213_FAKE_TAU_S": "1"})
    e.update(env_extra or {})
    cmd = [PY, "-B", runner, "session", "--dry", "--arm", "B", "--t0", str(int(time.time())), "--out", out, "--sequence", "plan"] + extra
    fo = open(os.path.join(out + "-runner.out"), "w")
    return subprocess.Popen(cmd, cwd=REPO, stdout=fo, stderr=subprocess.STDOUT, env=e), out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("scratch")
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args(argv)
    S = os.path.abspath(a.scratch)
    if S == REPO or S.startswith(REPO + os.sep):
        print("the scratch directory must be outside the repository")
        return 2
    if any(os.path.exists(p) for p in ("/dev/et0_mgmt", "/dev/et0_ops", "/dev/et1_mgmt", "/dev/et1_ops")):
        print("REFUSED: a card node is visible: run this inside the sandbox (W/nodev.sh)")
        return 3
    os.makedirs(S, exist_ok=True)
    t = T(S, a.only)
    print(f"A3's order desk test at {REPO} (HEAD {run(['git', '-C', REPO, 'rev-parse', '--short=12', 'HEAD'])[1].strip()}), {time.strftime('%F %T %Z')}, "
          f"{PY} {sys.version.split()[0]}", flush=True)
    reg, lnc, exp = a3_expected()

    if t.want("O1"):
        rc, out = run([PY, "-I", "-B", WRAP, "check"])
        t.case("O1", rc == 0 and out.startswith("A3-ORDER OK: arm B 85 runs, ") and "A3-STOP" not in out, f"rc {rc}; {out.strip()[:200]}")
    if t.want("O2"):
        rc, out = run([PY, "-I", "-B", WRAP, "order"])
        rl = [x for x in out.splitlines() if re.match(r"^\s+[0-9]+ (tie|pass1|pass2)\s", x)]
        last8 = [tuple(x.split()[1:3]) for x in rl[-8:]]
        t.case("O2", rc == 0 and len(rl) == 85 and last8 == TAIL and "same multiset of (block, point) as the registered 85 runs: yes" in out,
               f"rc {rc}; {len(rl)} run lines; last eight {' '.join(i for _, i in last8)}; {[x for x in out.splitlines() if x.startswith('A3-ORDER:')][:1]}")
    if t.want("O3"):
        F = seq_file()
        got = [(x["n"], x["block"], x["id"], x["registered_n"]) for x in F["sequence"]]
        ties = [n for n, b, i, rn in exp if b == "tie"]
        rel_ok = [(b, i) for n, b, i, rn in exp if i not in lnc] == [(r["block"], r["id"]) for r in reg if r["id"] not in lnc]
        bij = sorted(rn for n, b, i, rn in exp) == list(range(1, 86)) and all(reg[rn - 1]["id"] == i and reg[rn - 1]["block"] == b for n, b, i, rn in exp)
        ms = sorted((b, i) for n, b, i, rn in exp) == sorted((r["block"], r["id"]) for r in reg)
        t.case("O3", got == exp and tuple(lnc) == MOVED and ties == [1, 39, 77] and [(b, i) for n, b, i, rn in exp[-8:]] == TAIL and rel_ok and bij and ms
               and [n for n, b, i, rn in exp] == list(range(1, 86)) and len(reg) == 85,
               f"file == re-derived: {got == exp}; moved {lnc}; ties at {ties}; last eight {[i for n, b, i, rn in exp[-8:]]}; the 77 others in "
               f"registered order: {rel_ok}; registered_n a bijection naming each run's place: {bij}; same multiset: {ms}")
    if t.want("O4"):
        res = []
        r = scratch_copy(S, "o4a")
        with open(os.path.join(r, "tools/claims-v3/e213-a3/sequence-B-a3.json"), "ab") as f:
            f.write(b" ")
        rc, out = run([PY, "-I", "-B", os.path.join(r, "tools/claims-v3/e213-a3/run_e213_a3.py"), "check"], cwd=r)
        res.append(("a", rc == 3 and "A3-STOP: sequence-B-a3.json is not A3's pinned file" in out and "A3-ORDER OK" not in out, f"rc {rc}"))
        r = scratch_copy(S, "o4b")
        sp = os.path.join(r, "tools/claims-v3/e213-a3/sequence-B-a3.json")
        txt = open(sp).read()
        l78 = '{"n": 78, "block": "pass1", "id": "k40", "registered_n": 39}'
        l79 = '{"n": 79, "block": "pass1", "id": "k37", "registered_n": 40}'
        sw = None
        if txt.count(l78) == 1 and txt.count(l79) == 1:     # runs 78 and 79 swapped: the same multiset, not A3's order
            sw = txt.replace(l78, '{"n": 78, "block": "pass1", "id": "k37", "registered_n": 40}') \
                    .replace(l79, '{"n": 79, "block": "pass1", "id": "k40", "registered_n": 39}')
        if sw:
            open(sp, "w").write(sw)
            h = hashlib.sha256(sw.encode()).hexdigest()
            wp = os.path.join(r, "tools/claims-v3/e213-a3/run_e213_a3.py")
            w = open(wp).read()
            w2 = re.sub(r'^SEQ_PIN = "[0-9a-f]{64}"$', f'SEQ_PIN = "{h}"', w, flags=re.M)
            open(wp, "w").write(w2)
            rc, out = run([PY, "-I", "-B", wp, "check"], cwd=r)
            res.append(("b", rc == 3 and "the file's runs are not A3's order derived from the registered one" in out and "not A3's pinned file" not in out
                        and w2 != w, f"rc {rc}"))
        else:
            res.append(("b", False, "the swap's lines were not found"))
        r = scratch_copy(S, "o4c")
        with open(os.path.join(r, "tools/claims-v3/e213/points-e213.json"), "ab") as f:
            f.write(b"\n")
        rc, out = run([PY, "-I", "-B", os.path.join(r, "tools/claims-v3/e213-a3/run_e213_a3.py"), "check"], cwd=r)
        res.append(("c", rc == 3 and "A3-STOP: points-e213.json is not the registered file" in out, f"rc {rc}"))
        od = os.path.join(S, "o4d-out")
        rc, out = run([PY, "-B", WRAP, "session", "--dry", "--arm", "A", "--t0", "1", "--out", od])
        res.append(("d", rc == 2 and "A3-STOP: Amendment A3 is E213 arm B's alone" in out and not os.path.exists(od), f"rc {rc}"))
        r = scratch_copy(S, "o4e")
        os.remove(os.path.join(r, "tools/claims-v3/dmcmd_audit_v2.py"))
        rc, out = run([PY, "-I", "-B", os.path.join(r, "tools/claims-v3/e213-a3/run_e213_a3.py"), "check"], cwd=r)
        res.append(("e", rc == 3 and "A3-STOP: the device-command audit of A3's two session files did not read GO" in out and "A3-ORDER OK" not in out,
                    f"rc {rc}"))
        t.case("O4", all(x[1] for x in res), "; ".join(f"({k}) {'refused' if g else 'NOT REFUSED'} {d}" for k, g, d in res))
    if t.want("O5"):
        code = ("import importlib.util, json, sys\n"
                f"spec = importlib.util.spec_from_file_location('w', {WRAP!r}); w = importlib.util.module_from_spec(spec); spec.loader.exec_module(w)\n"
                "C = w.C\nreg = {r['id']: r['name'] for r in w.REGISTERED_SEQUENCE('B')}\nb = w.a3_sequence('B')\n"
                "ok_b = len(b) == 85 and all(set(x) == {'n', 'block', 'id', 'name'} and x['name'] == reg[x['id']] for x in b) and [x['n'] for x in b] == list(range(1, 86))\n"
                "ok_a = w.a3_sequence('A') == w.REGISTERED_SEQUENCE('A')\n"
                "try:\n    w.a3_sequence('C'); ok_c = False\nexcept KeyError:\n    ok_c = True\n"
                "print(json.dumps({'b': ok_b, 'a': ok_a, 'c': ok_c, 'tail': [x['id'] for x in b[-8:]]}))\n")
        rc, out = run([PY, "-I", "-B", "-c", code])
        try:
            j = json.loads(out.strip().splitlines()[-1])
        except (ValueError, IndexError):
            j = {}
        rc2, out2 = run([PY, "-I", "-B", os.path.join(E213, "e213_common.py")])
        t.case("O5", rc == 0 and j.get("b") and j.get("a") and j.get("c") and j.get("tail") == [i for _, i in TAIL] and rc2 == 0 and "SELF-CHECK PASS" in out2,
               f"arm B 85 runs with registered names {j.get('b')}; arm A the kit's {j.get('a')}; arm C KeyError {j.get('c')}; the kit's self-check: {out2.strip()[:60]}")

    r1 = r2 = None
    if t.want("R1"):
        p, out = session(S, "R1", WRAP, "0.02", ["--rest-s", "0.15", "--smoke-rest-s", "1.5", "--tail-s", "0.1", "--gate-wait-s", "3"])
        rc = p.wait(timeout=3600)
        q = json.load(open(os.path.join(out, "queue.json"))) if os.path.exists(os.path.join(out, "queue.json")) else {}
        qq = q.get("queue", [])
        want = [f"{n:03d}-{b}-{i}" for n, b, i, rn in exp]
        bad = []
        for x, k in zip(qq, want):
            if x.get("run") != k or not x.get("ran"):
                bad.append(f"{k}: {x.get('run')} ran {x.get('ran')}")
                continue
            rj = json.load(open(os.path.join(out, "runs", k, "run.json")))
            pr = rj["procs"][0]
            if pr["argv"] != C.host_argv(REPO, rj["id"], C.RUN_SECONDS, C.RUN_BUDGET, os.path.join(out, "STOP")) or "-k" in pr["argv"]:
                bad.append(f"{k} argv")
            if not str(pr.get("gate", "")).startswith("GATE OK"):
                bad.append(f"{k} gate")
        log = open(os.path.join(out, "session.log")).read() if os.path.exists(os.path.join(out, "session.log")) else ""
        logkeys = re.findall(r"DRY run ([0-9]{3}-(?:tie|pass1|pass2)-[a-z0-9]+): ", log)
        ro = open(out + "-runner.out").read() if os.path.exists(out + "-runner.out") else ""
        t.case("R1", rc == 0 and len(qq) == 85 and not bad and logkeys == want and ro.startswith("A3-ORDER OK: arm B 85 runs"),
               f"rc {rc}; {len(qq)} runs, in A3's order with every key, argv and gate the registered point's ({len(bad)} differ{': ' + '; '.join(bad[:3]) if bad else ''}); "
               f"the log's run lines in A3's order: {logkeys == want}; runner.out first line A3-ORDER OK: {ro.startswith('A3-ORDER OK')}; "
               f"runs 78-85: {' '.join(x.get('run', '?')[4:] for x in qq[77:])}")
        r1 = out
    if t.want("R2") or t.want("S1"):
        env = {"E213_FAKE_LEAK": "0", "E213_FAKE_W_SCALE": "1"}
        ext = ["--rest-s", "6", "--smoke-rest-s", "1.5", "--tail-s", "0.2", "--gate-wait-s", "3"]
        pa, oa = session(S, "R2-A3", WRAP, "0.2", ext, env)
        pr_, orr = session(S, "R2-REG", RUNNER, "0.2", ext, env)
        rca, rcr = pa.wait(timeout=5400), pr_.wait(timeout=5400)
        res = {}
        for tag, o in (("A3", oa), ("REG", orr)):
            dj = os.path.join(S, f"R2-{tag}-data.json")
            rc1, o1 = run([PY, "-I", "-B", os.path.join(E213, "reduce_e213.py"), "--arm", f"B={o}", "--out", dj])
            data = json.load(open(dj)) if os.path.exists(dj) else {}
            rc2, sc, o2 = score(S, f"R2-{tag}", data)
            res[tag] = (rc1, rc2, data, sc)
        qa = [x.get("run") for x in json.load(open(os.path.join(oa, "queue.json"))).get("queue", [])] if os.path.exists(os.path.join(oa, "queue.json")) else []
        qr = [x.get("run") for x in json.load(open(os.path.join(orr, "queue.json"))).get("queue", [])] if os.path.exists(os.path.join(orr, "queue.json")) else []
        wa = [f"{n:03d}-{b}-{i}" for n, b, i, rn in exp]
        wr = [C.run_key(r) for r in C.sequence("B")]
        sa, sr = res["A3"][3], res["REG"][3]
        Ba, Br = sa.get("arms", {}).get("B") or {}, sr.get("arms", {}).get("B") or {}
        va, vr = Ba.get("verdicts"), Br.get("verdicts")
        Ma, Mr = Ba.get("measured") or {}, Br.get("measured") or {}
        npts = len(Ma)
        runs_a = {pid: len(P["runs"]) for pid, P in ((res["A3"][2].get("arms", {}).get("B") or {}).get("points") or {}).items()}
        runs_r = {pid: len(P["runs"]) for pid, P in ((res["REG"][2].get("arms", {}).get("B") or {}).get("points") or {}).items()}
        time_eq = sorted(Ma) == sorted(Mr) and all(Ma[p][k] == Mr[p][k] for p in Ma for k in ("cw", "cm", "t"))
        dW = max([abs(Ma[p]["W"] - Mr[p]["W"]) for p in Ma if Ma[p].get("W") is not None and Mr.get(p, {}).get("W") is not None] or [9.9])
        dR = max([abs(Ma[p]["prest"] - Mr[p]["prest"]) for p in Ma if Ma[p].get("prest") is not None and Mr.get(p, {}).get("prest") is not None] or [9.9])
        cells = all([c["pass"] for c in (Ba.get("cells") or {}).get(q, [])] == [c["pass"] for c in (Br.get("cells") or {}).get(q, [])]
                    for q in ("T1", "T2", "T3", "E1", "E2", "E3", "E4"))
        h2h = {k: (Ba.get("head_to_head") or {}).get(k, {}).get("verdict") for k in ("H1", "H2", "H3", "H4", "H5")}
        h2r = {k: (Br.get("head_to_head") or {}).get(k, {}).get("verdict") for k in ("H1", "H2", "H3", "H4", "H5")}
        if t.want("R2"):
            t.case("R2", rca == 0 and rcr == 0 and all(res[k][0] == 0 and res[k][1] == 0 for k in res) and qa == wa and qr == wr and npts == 41
                   and runs_a == runs_r and set(runs_a.values()) == {2} and time_eq and dW <= 0.1 and dR <= 0.1 and cells and va and va == vr
                   and Ba.get("counts") == Br.get("counts") and h2h == h2r,
                   f"sessions rc {rca} (A3) / {rcr} (registered); reduce and score rc {[res[k][:2] for k in ('A3', 'REG')]}; A3's runs in A3's order {qa == wa}, "
                   f"the registered session's in the registered order {qr == wr}; {npts} points, 2 runs each in both {runs_a == runs_r and set(runs_a.values()) == {2}}; "
                   f"cycles and seconds equal at every point {time_eq}; W over idle within {dW:.4f} W, rest within {dR:.4f} W (the doubles' sample noise); "
                   f"cells' passes equal {cells}; verdicts equal {va == vr} ({va}); counts equal {Ba.get('counts') == Br.get('counts')}; head-to-head {h2h} equal {h2h == h2r}")
        r2 = (oa, res["A3"][2], sa)
    if t.want("S1") and r2:
        oa, data, sa = r2
        F = seq_file()
        to_reg = {x["n"]: x["registered_n"] for x in F["sequence"]}
        d1 = copy.deepcopy(data)
        d2 = copy.deepcopy(data)
        nch = 0
        for d, how in ((d1, "reg"), (d2, "rev")):
            B = d["arms"]["B"]
            for P in list(B["points"].values()) + [B["ties"]]:
                for run_ in P["runs"]:
                    if isinstance(run_.get("n"), int) and run_["n"] > 0:
                        run_["n"] = to_reg[run_["n"]] if how == "reg" else 86 - run_["n"]
                        nch += 1
                if how == "rev":
                    P["runs"].reverse()
        rc1, s1, _ = score(S, "S1-reg", d1)
        rc2, s2, _ = score(S, "S1-rev", d2)
        e1, e2 = diff_paths(mask(sa), mask(s1)), diff_paths(mask(sa), mask(s2))
        moved_n = sorted({r.get("n") for pid in MOVED for r in d1["arms"]["B"]["points"].get(pid, {}).get("runs", [])})
        t.case("S1", rc1 == 0 and rc2 == 0 and not e1 and not e2 and nch == 2 * 85 and moved_n == [39, 40, 41, 42, 44, 45, 46, 47],
               f"{nch // 2} runs renumbered to their registered places (the moved points then at {moved_n}) and, again, reversed with each point's "
               f"runs listed backwards: the frozen scorer's output equal to the A3 data's ({len(e1)} and {len(e2)} differences once run numbers in "
               f"messages are masked); rc {rc1}, {rc2}")
    print(f"SELFTEST-ORDER-A3 {t.ok} of {t.n} {'PASS' if t.ok == t.n else 'FAIL'}", flush=True)
    return 0 if t.ok == t.n else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
