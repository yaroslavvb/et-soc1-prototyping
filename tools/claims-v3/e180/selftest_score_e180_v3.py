#!/usr/bin/env python3
"""The self-test of E180's v3 reduction, scorer and collection (the kit's dated note 2, KIT.md.dated-note-2.md sections 1-5), on synthetic
sessions and on listings built from a real objdump listing.

    /usr/bin/python3 tools/claims-v3/e180/selftest_score_e180_v3.py [--root .] > logs/selftest-score-e180-v3.txt   # exit 0 if all pass

It needs a python3 with numpy (analyze_catalogue.py's): on the Intel /usr/bin/python3, as step 22 uses. It writes only in a temporary
directory (the collection runs in a scratch tree that holds copies of the files it reads).
  W1  v3's scorer equals v2's on v2's own self-test sessions (v1's ten synthetic truths, the reported-arm session, A1-7's four readings,
      A1-1's two, A1-5's): every rule record, every reported arm and the owner's sentence identical, given the same walk reading; v3 adds
      only its own record and the per-kind marks;
  W2  A1-7 read from check_elf_e180_v2.py's own output on built listings, with the box's v1 line beside: 262 then 261 (the box's order):
      E180-A labelled "walk verified by disassembly" while the box's v1 line reads 261 UNREAD (kept beside); 261's zeroing block inside the
      loop: E180-A NOT SCORED (v1's record kept), every fadd.ps.acc kind marked "the sums do not walk as registered", fadd.pi.acc's marked
      by 262's reading, while v1 reads UNREAD (the fail-open, shown); no listing: "walk not verified";
  W3  reduce_e180_v3.py equals reduce_e180_v2.py field for field on clean raw passes (a flat die, and one that steps up in each burst):
      v3 adds only its "v3" record;
  W4  one pass of three spoiled (a telemetry gzip cut in half; one sample without board_w, as ettelem prints a failed request; a partial
      last line; a sample whose board_w is null; a runs gzip cut in half; a run without t_end_ms): reduce_e180_v2.py exits non-zero (the
      fault, shown) and v3 exits 0, sets that pass aside as "unreadable" naming the file, and keeps the other two exactly as v2 reduces them
      alone; an empty telemetry file reads as v2 reads it; a data directory that is not there gives 0 passes, exit 0;
  W5  collect_e180_v3.sh end to end in a scratch tree: three passes (one spoiled), the box's logs with its v1 walk line, and a build record
      holding BUILD-E180.json (a toolchain listing with a made-up owner, group, symlink target and a non-version line) and the 262-then-261
      listing: exit 0; the desk walk reads 261 and 262 PASS; E180-A scored on the two kept passes, labelled "walk verified by
      disassembly", the box's 261 UNREAD kept beside; the listing copied byte for byte with its sha256 recorded; the kernel's sha256 in
      logs/build-e180.json and nothing of the made-up owner, group or target there; the spoiled pass named; no scratch path in any output;
  W6  the same with no build record at all: exit 0; the desk walk reads UNREAD (no objdump); E180-A labelled "walk not verified".
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import gzip
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_elf_e180 as ce  # noqa: E402
import score_e180_v2 as s2  # noqa: E402
import score_e180_v3 as s3  # noqa: E402
import selftest_elf_e180_v2 as te  # noqa: E402  (the listings' builders)
import selftest_score_e180 as t1  # noqa: E402  (v1's synthetic sessions)

PY = sys.executable


def load(n):
    return json.load(open(os.path.join(HERE, n)))


def strip_v3(s):
    """a v3 scored session with v3's additions removed (its own record and the per-kind marks)"""
    s = copy.deepcopy(s)
    s.pop("reported_v3", None)
    for rep in s.get("reported", {}).get("kinds", {}).values():
        rep.pop("walk", None)
    return s


def elf_file(d, name, v261, v262):
    p = os.path.join(d, name)
    with open(p, "w") as f:
        for m, v, n in (("261", v261, "fadd.ps.acc"), ("262", v262, "fadd.pi.acc")):
            if v:
                f.write(f"{v} {n:28s} mode {m}: synthetic\n")
        f.write("ELFCHECK-E180-V2: synthetic\n")
    return p


def make_pass(data, p, kind, truthW, plan, variant="flat", seed=None):
    rng = random.Random(seed if seed is not None else int(p))
    d = os.path.join(data, f"p{p}")
    os.makedirs(d)
    tel, runs, tms, idle = [], [], [1_800_000_000_000 + 10_000_000 * (int(p) - 18010)], 26.0

    def sample(w, die):
        tel.append({"t_ms": tms[0], "took_ms": 22, "since_reset_ms": -1, "board_w": round(w + rng.gauss(0, 0.05), 2),
                    "sp": {"minion_w": [8.0 + 0.7741 * (w - idle)] * 3, "sram_w": [2.3] * 3, "noc_w": [2.5] * 3},
                    "temp_c": {"pmic": 40, "ioshire": [50, 49, 51], "minshire": [die, die - 1, die + 1]},
                    "mhz": {"minion": 600, "noc": 1000, "ddr": 1600}})
        tms[0] += 100
    for _ in range(100):
        sample(idle, 58.0)
    for name in plan["order"][p]:
        for _ in range(45):
            sample(idle, 58.0)
        t0 = tms[0]
        die = 58.0 + (0.1 * truthW[kind[name]] if variant == "step" else 0.0)
        for _ in range(30):
            sample(idle + truthW[kind[name]], die)
        for L in range(7):
            runs.append({"host": "aifoundry3", "pass": int(p), "cfg": name, "kind": kind[name], "pattern": "x", "unit": "instruction",
                         "operands": "file", "harts": 2, "scp": False, "participants": 2048, "shires": 32,
                         "t_start_ms": t0 + L * 400, "t_end_ms": t0 + L * 400 + 399, "ops": 10 ** 11, "bytes": 0,
                         "cycles_max": 240000000, "ops_per_cycle_per_hart": 0.373, "wall_s": 0.4})
    for _ in range(60):
        sample(idle, 58.0)
    with gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "wt") as f:
        f.write("".join(json.dumps(x) + "\n" for x in tel))
    with gzip.open(os.path.join(d, "runs.jsonl.gz"), "wt") as f:
        f.write("".join(json.dumps(x) + "\n" for x in runs))
    json.dump({"status": "ok"}, open(os.path.join(d, "block.json"), "w"))
    return d


def lines_gz(path):
    return gzip.open(path, "rt").read().splitlines()


def spoil(d, how):
    tg, rg = os.path.join(d, "telemetry.jsonl.gz"), os.path.join(d, "runs.jsonl.gz")
    if how == "telemetry gzip cut in half":
        b = open(tg, "rb").read(); open(tg, "wb").write(b[: len(b) // 2])
    elif how in ("one sample without board_w", "a sample whose board_w is null"):
        L = lines_gz(tg); x = json.loads(L[500])
        if how.startswith("one"):
            x.pop("board_w")
        else:
            x["board_w"] = None
        L[500] = json.dumps(x)
        with gzip.open(tg, "wt") as f:
            f.write("\n".join(L) + "\n")
    elif how == "a partial last line":
        L = lines_gz(tg); os.remove(tg)
        open(os.path.join(d, "telemetry.jsonl"), "w").write("\n".join(L) + "\n" + L[-1][:40] + "\n")
    elif how == "runs gzip cut in half":
        b = open(rg, "rb").read(); open(rg, "wb").write(b[: len(b) // 2])
    elif how == "a run without t_end_ms":
        L = lines_gz(rg); x = json.loads(L[10]); x.pop("t_end_ms"); L[10] = json.dumps(x)
        with gzip.open(rg, "wt") as f:
            f.write("\n".join(L) + "\n")
    elif how == "an empty telemetry file":
        with gzip.open(tg, "wt") as f:
            f.write("")


def reduce(script, data, out, root):
    r = subprocess.run([PY, "-B", os.path.join(HERE, script), "--data", data, "--out", out, "--root", root], capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip().splitlines()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, "..", "..", "..")))
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    fc, foot, off, noise = load("forecast-e180.json"), load("footing-e180-a1.json"), load("offset-e180-a1.json"), load("noise/noise-e180.json")
    plan, cfgs = load("plan-e180.json"), load("cfgs-e180.json")
    kind = {c["cfg"]: c["kind"] for c in cfgs["cfgs"]}
    K = fc["kinds"]
    truthW = {nm: K[nm]["W"]["aifoundry3"]["P"] + 10.0 for nm in K}
    res = []

    def case(name, cond, detail):
        res.append(bool(cond))
        print(f"{name}: {'PASS' if cond else 'FAIL'} - {detail}")

    with tempfile.TemporaryDirectory() as t:
        # ---- W1: v3 equals v2 on v2's sessions
        arm = lambda a_: (lambda nm, card: K[nm]["W"][card][a_])
        op = lambda nm, card: K[nm]["W"][card]["P"] + (0.05 * K[nm]["operand_popcount"] if K[nm]["mode"] == "fadd.ps" and K[nm]["operand_popcount"] else 0.0)
        rz = lambda nm, card: (0.1649 * K[nm]["result_popcount"] if K[nm]["mode"] == "fadd.pi" and K[nm]["result_popcount"] else K[nm]["W"][card]["P"])
        sessions = [(n, t1.session(fc, f, **kw), kw.get("card", "aifoundry3")) for n, f, kw in
                    [("P", arm("P"), {}), ("C", arm("C"), {}), ("E", arm("E"), {}), ("F", arm("F"), {}), ("A", arm("A"), {}), ("op", op, {}),
                     ("rz", rz, {}), ("null", lambda nm, card: 0.0, {}), ("one pass", arm("P"), {"passes": t1.PASSES[:1]}),
                     ("card 1", arm("P"), {"card": "aifoundry1-c1", "drop": ("18012", "fadd.ps/f_7")}),
                     ("A x 1.3", lambda nm, card: K[nm]["W"][card]["P"] * (1.3 if nm == "fadd.ps.acc/f_4" else 1.0), {})]]
        states = [("PASS", "PASS"), ("UNREAD", "UNREAD"), ("FAIL", "PASS"), ("PASS", "FAIL"), (None, None)]
        same = n = 0
        diffs = []
        for name, red, card in sessions:
            for st_ in states:
                p2 = elf_file(t, "e.txt", *st_) if st_[0] else os.path.join(t, "absent.txt")
                v2 = s2.score(copy.deepcopy(red), fc, card, foot, off, s2.elf_reading(p2), noise)
                v3 = s3.score(copy.deepcopy(red), fc, card, foot, off, p2, None, noise)
                n += 1
                ok = json.dumps(strip_v3(v3), sort_keys=True, default=str) == json.dumps(v2, sort_keys=True, default=str)
                same += ok
                if not ok:
                    diffs.append(f"{name}/{st_}")
        case("W1 v3's scorer equals v2's on v2's sessions", same == n,
             f"{same} of {n} scored sessions identical with v3's additions removed (11 sessions x 5 walk readings)"
             f"{'; differ: ' + ', '.join(diffs[:6]) if diffs else ''}")

        # ---- W2: A1-7 from check_elf_e180_v2.py's own output, the box's v1 line beside
        raw = open(te.DEFAULT, errors="replace").read().splitlines()
        ins = ce.parse(te.DEFAULT)
        size = {}
        for line in raw:
            m = re.match(r"\s*([0-9a-f]+):\s+([0-9a-f]+)\s+", line)
            if m:
                size[int(m.group(1), 16)] = len(m.group(2)) // 2
        case160, kb = te.real_case(ins)
        base = max(x[0] for x in ins) + 0x100
        mk = lambda mn, b, **kw: te.mk_case(case160, kb, size, mn, b, **kw)
        c262, x = mk("fadd.pi", base)
        c261, _ = mk("fadd.ps", x)
        f1 = os.path.join(t, "f1.dis.txt")
        te.write(f1, raw, [c262, c261])
        cin, _ = mk("fadd.ps", base, zero="loop_head")
        f4 = os.path.join(t, "f4.dis.txt")
        te.write(f4, raw, [cin])

        def walks(listing, tag):
            w2, w1 = os.path.join(t, f"{tag}-v2.txt"), os.path.join(t, f"{tag}-v1.txt")
            for script, o in (("check_elf_e180_v2.py", w2), ("check_elf_e180.py", w1)):
                r = subprocess.run([PY, "-B", os.path.join(HERE, script), listing, "--also-160"], capture_output=True, text=True)
                open(o, "w").write(r.stdout)
            return w2, w1
        red = t1.session(fc, arm("P"))
        w2, w1 = walks(f1, "f1")
        o1 = s3.score(copy.deepcopy(red), fc, "aifoundry3", foot, off, w2, w1, noise)
        w2b, w1b = walks(f4, "f4")
        o4 = s3.score(copy.deepcopy(red), fc, "aifoundry3", foot, off, w2b, w1b, noise)
        o0 = s3.score(copy.deepcopy(red), fc, "aifoundry3", foot, off, os.path.join(t, "nothing-v2.txt"), None, noise)
        acc4 = {nm: r["walk"] for nm, r in o4["reported"]["kinds"].items() if "walk" in r}
        ok = (o1["rules"]["E180-A"].get("walk") == "walk verified by disassembly" and o1["reported_v3"]["elfcheck_box_v1"]["261"] == "UNREAD"
              and o1["reported_v3"]["elfcheck_binding"]["262"] == "PASS"
              and o4["rules"]["E180-A"]["verdict"] == "NOT SCORED" and "v1" in o4["rules"]["E180-A"]
              and all(v == "the sums do not walk as registered" for nm, v in acc4.items() if nm.startswith("fadd.ps.acc/"))
              and all(v == "walk not verified" for nm, v in acc4.items() if nm.startswith("fadd.pi.acc/"))
              and any(nm.startswith("fadd.ps.acc/") for nm in acc4) and o4["reported_v3"]["elfcheck_box_v1"]["261"] == "UNREAD"
              and o0["rules"]["E180-A"].get("walk") == "walk not verified" and not o0["reported_v3"]["elfcheck_binding"]["file"])
        md1 = s3.md(o1)
        ok = ok and "check_elf_e180_v2.py at the desk" in md1 and "kept beside and never read for a verdict: 261 UNREAD" in md1
        case("W2 A1-7 from the desk walk, the box's v1 line beside", ok,
             f"262 then 261: A {o1['rules']['E180-A']['verdict']} ({o1['rules']['E180-A'].get('walk')}), box v1 261 "
             f"{o1['reported_v3']['elfcheck_box_v1']['261']}; zeroing inside the loop: A {o4['rules']['E180-A']['verdict']}, "
             f"{len(acc4)} acc kinds marked, box v1 261 {o4['reported_v3']['elfcheck_box_v1']['261']}; no listing: "
             f"A {o0['rules']['E180-A'].get('walk')}")

        # ---- W3: reduce v3 equals v2 on clean raw passes
        for variant in ("flat", "step"):
            data = os.path.join(t, f"w3-{variant}", "e180")
            for p in ("18010", "18011"):
                make_pass(data, p, kind, truthW, plan, variant)
            o2, o3 = os.path.join(t, f"w3-{variant}-v2.json"), os.path.join(t, f"w3-{variant}-v3.json")
            rc2, _ = reduce("reduce_e180_v2.py", data, o2, root)
            rc3, out3 = reduce("reduce_e180_v3.py", data, o3, root)
            j2, j3 = json.load(open(o2)), json.load(open(o3))
            v3rec = j3.pop("v3", None)
            ok = rc2 == 0 and rc3 == 0 and json.dumps(j2, sort_keys=True) == json.dumps(j3, sort_keys=True) and v3rec is not None \
                and not v3rec["unreadable_passes"] and len(j3["passes"]) == 2
            case(f"W3 reduce v3 equals v2 on clean raw passes ({variant} die)", ok,
                 f"rc {rc2} / {rc3}; kept {sorted(j3['passes'])}; identical with v3's record removed "
                 f"{json.dumps(j2, sort_keys=True) == json.dumps(j3, sort_keys=True)}; {out3[-1][:100]}")

        # ---- W4: one pass of three spoiled
        clean = os.path.join(t, "w4-clean", "e180")
        for p in ("18010", "18012"):
            make_pass(clean, p, kind, truthW, plan)
        oc = os.path.join(t, "w4-clean.json")
        reduce("reduce_e180_v2.py", clean, oc, root)
        jc = json.load(open(oc))
        for how in ("telemetry gzip cut in half", "one sample without board_w", "a partial last line", "a sample whose board_w is null",
                    "runs gzip cut in half", "a run without t_end_ms", "an empty telemetry file"):
            tag = re.sub(r"[^a-z0-9]+", "-", how)
            data = os.path.join(t, f"w4-{tag}", "e180")
            for p in ("18010", "18011", "18012"):
                make_pass(data, p, kind, truthW, plan)
            spoil(os.path.join(data, "p18011"), how)
            o2, o3 = os.path.join(t, f"w4-{tag}-v2.json"), os.path.join(t, f"w4-{tag}-v3.json")
            rc2, out2 = reduce("reduce_e180_v2.py", data, o2, root)
            rc3, out3 = reduce("reduce_e180_v3.py", data, o3, root)
            if rc3 != 0:
                case(f"W4 {how}", False, f"v3 rc {rc3}: {out3[-1][:200]}")
                continue
            j3 = json.load(open(o3))
            keep = all(json.dumps(j3["passes"].get(p), sort_keys=True) == json.dumps(jc["passes"][p], sort_keys=True) for p in ("18010", "18012"))
            why = j3["set_aside"].get("18011", {}).get("why", "")
            if how == "an empty telemetry file":
                j2 = json.load(open(o2)) if rc2 == 0 else {}
                j3.pop("v3")
                ok = rc2 == 0 and json.dumps(j2, sort_keys=True) == json.dumps(j3, sort_keys=True) and keep and "no kept burst" in why
                case(f"W4 {how}: as v2 reads it", ok, f"v2 rc {rc2}, v3 rc {rc3}; 18011 set aside: {why[:90]}; the other two as v2 alone {keep}")
                continue
            fname = "runs.jsonl" if how.startswith("run") or "a run " in how else "telemetry.jsonl"
            ok = rc2 != 0 and why.startswith("unreadable: ") and fname in why and keep and sorted(j3["passes"]) == ["18010", "18012"] \
                and "18011" in j3["v3"]["unreadable_passes"]
            case(f"W4 {how}", ok, f"v2 rc {rc2} ({out2[-1][:60]}); v3 rc {rc3}, kept {sorted(j3['passes'])} (as v2 alone {keep}); "
                                  f"18011: {why[:120]}")
        o3 = os.path.join(t, "w4-nodir.json")
        rc3, _ = reduce("reduce_e180_v3.py", os.path.join(t, "no-such-dir", "e180"), o3, root)
        j3 = json.load(open(o3)) if rc3 == 0 else {}
        case("W4 a data directory that is not there", rc3 == 0 and j3.get("passes") == {} and j3.get("set_aside") == {},
             f"rc {rc3}; passes {j3.get('passes')}, set aside {j3.get('set_aside')}")

        # ---- W5, W6: collect_e180_v3.sh end to end in a scratch tree
        tree = os.path.join(t, "tree")
        shutil.copytree(HERE, os.path.join(tree, "tools", "claims-v3", "e180"), ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(os.path.join(root, "tools", "claims-v3", "footing-law"), os.path.join(tree, "tools", "claims-v3", "footing-law"))
        os.makedirs(os.path.join(tree, "workloads", "enercat"))
        shutil.copy(os.path.join(root, "workloads", "enercat", "analyze_catalogue.py"), os.path.join(tree, "workloads", "enercat"))
        for tag, with_record in (("W5", True), ("W6", False)):
            rawd = os.path.join(t, f"{tag}-raw")
            for p in ("18010", "18011", "18012"):
                make_pass(os.path.join(rawd, "e180"), p, kind, truthW, plan)
            spoil(os.path.join(rawd, "e180", "p18011"), "telemetry gzip cut in half")
            os.makedirs(os.path.join(rawd, "e180-smoke", "p18001"))
            os.makedirs(os.path.join(rawd, "e180-stoptest", "p18002"))
            os.makedirs(os.path.join(rawd, "logs"))
            shutil.copy(w1, os.path.join(rawd, "logs", "elfcheck-e180.txt"))
            open(os.path.join(rawd, "logs", "session.log"), "w").write("2026-11-06 15:00:00 PST session end\n")
            if with_record:
                os.makedirs(os.path.join(rawd, "build-record"))
                shutil.copy(f1, os.path.join(rawd, "build-record", "e180-kernel-dis.txt"))
                tl = ("total 8\n-rwxr-xr-x 1 u_toolowner g_toolgroup 1234 Jan  1  2026 dev_mngt_service\n"
                      "lrwxrwxrwx 1 u_toolowner g_toolgroup 22 Jan  1  2026 objdump -> /srv/u_toolowner/et/objdump\n1.4.1\n"
                      "built by u_toolowner on a box\n")
                json.dump({"binaries": {"build/enercat-e180/host/enercat_host": "ab" * 32, "build/enercat-e180/kernel/enercat.elf": "cd" * 32},
                           "acc_modes_inc_sha256": "ef" * 32, "built": "2026-11-06T14:00:00-0800", "toolchain_listing": tl},
                          open(os.path.join(rawd, "build-record", "BUILD-E180.json"), "w"), indent=1)
            env = dict(os.environ, PY=PY, E180_DATE="2026-11-06")
            r = subprocess.run(["bash", os.path.join(tree, "tools", "claims-v3", "e180", "collect_e180_v3.sh"), rawd], capture_output=True,
                               text=True, env=env)
            outd = os.path.join(tree, "build", "e180-out", "2026-11-06-e180-vector-add-aifoundry3")
            lines = (r.stdout + r.stderr).strip().splitlines()
            if r.returncode != 0 or not os.path.exists(os.path.join(outd, "scored-e180.json")):
                case(f"{tag} collect_e180_v3.sh end to end", False, f"rc {r.returncode}: {' | '.join(lines[-4:])[:300]}")
                continue
            sc = json.load(open(os.path.join(outd, "scored-e180.json")))
            md = open(os.path.join(outd, "scored-e180.md")).read()
            walk2 = s2.elf_reading(os.path.join(outd, "logs", "elfcheck-e180-v2.txt"))
            texts = []
            for dp, _dn, fn in os.walk(outd):
                for f_ in fn:
                    if not f_.endswith(".gz"):
                        texts.append(open(os.path.join(dp, f_), errors="replace").read())
            leak = any(t in x for x in texts)
            A = sc["rules"]["E180-A"]
            if with_record:
                br = json.load(open(os.path.join(outd, "logs", "build-e180.json")))
                bt = json.dumps(br)
                lst_ok = open(os.path.join(outd, "logs", "e180-kernel-dis.txt"), "rb").read() == open(f1, "rb").read() and \
                    br["kernel_listing"]["sha256"] == hashlib.sha256(open(f1, "rb").read()).hexdigest()
                ok = (walk2["261"] == "PASS" and walk2["262"] == "PASS" and A.get("walk") == "walk verified by disassembly"
                      and sc["reported_v3"]["elfcheck_box_v1"]["261"] == "UNREAD" and sc["kept_passes"] == ["18010", "18012"]
                      and "unreadable" in sc["set_aside"].get("18011", "") and lst_ok
                      and br["binaries"]["build/enercat-e180/kernel/enercat.elf"] == "cd" * 32
                      and "u_toolowner" not in bt and "g_toolgroup" not in bt and "/srv/" not in bt and "1.4.1" in bt
                      and "walk verified by disassembly" in md and not leak)
                case(f"{tag} collect_e180_v3.sh end to end, with the build record", ok,
                     f"rc 0; desk walk 261 {walk2['261']}, 262 {walk2['262']}; A {A['verdict']} ({A.get('walk')}); box v1 261 "
                     f"{sc['reported_v3']['elfcheck_box_v1']['261']}; kept {sc['kept_passes']}; 18011: {sc['set_aside'].get('18011', '')[:60]}; "
                     f"listing byte for byte {lst_ok}; owner, group or target in build-e180.json: "
                     f"{any(s_ in bt for s_ in ('u_toolowner', 'g_toolgroup', '/srv/'))}; a scratch path in the output: {leak}")
            else:
                br = json.load(open(os.path.join(outd, "logs", "build-e180.json")))
                ok = (walk2["261"] == "UNREAD" and walk2["262"] == "UNREAD" and A.get("walk") == "walk not verified"
                      and "absent" in br["kernel_listing"] and "absent" in br.get("build", {}) and not leak)
                case(f"{tag} collect_e180_v3.sh with no build record", ok,
                     f"rc 0; desk walk 261 {walk2['261']}; A {A['verdict']} ({A.get('walk')}); build-e180.json records "
                     f"{sorted(k for k in br if k != 'what')}; a scratch path in the output: {leak}")
            shutil.rmtree(os.path.join(tree, "build"), ignore_errors=True)
    print(f"SELFTEST-V3 {'PASS' if all(res) else 'FAIL'}: {sum(res)} of {len(res)}")
    sys.exit(0 if all(res) else 1)


if __name__ == "__main__":
    main()
