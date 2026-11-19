#!/usr/bin/env python3
"""E216 (Q227, lane kit-e216, Thu 19 Nov 2026, before any E216 datum): E216's BOX ROOT - what runs on aifoundry2, from where, at which bytes -
and E216's SCHEDULE in E208's form. E209's make_box_e209.py form (tools/claims-v3/e209/), with E216's files. Python's own modules only.

    /usr/bin/python3 -I -B tools/claims-v3/e216/make_box_e216.py make     writes box/a2c0-E216.json, box/SRC-SHA256SUMS-e216 and
                                                                           harness-e216.json beside this file (the desk, once)
    /usr/bin/python3 -I -B tools/claims-v3/e216/make_box_e216.py check    re-makes all three in memory, compares them byte for byte with
                                                                           the committed files and checks every source: CHECK PASS
    /usr/bin/python3 -I -B tools/claims-v3/e216/make_box_e216.py sync <root>   copies the harness's files from this checkout into the
                                                                           box root (step 5), then reads every one back at its sha256

THE BOX ROOT is E208's kit layout (tools/claims-v3/e208/proposal/src/README.md, "the kit's root") in a folder of the card lane's own (the
card-lane brief names it; never a model session's ee-* folder, never inside the lab clone):
  src/                 E208's registered kit, every file UNCHANGED at its committed sha256 (run_mms.py, mms_common.py, mms_ident.py,
                       fake_card_mms.py, guard_ettelem.sh, build_mms.sh, preflight_mms.sh, check_mms.py, status_mms.sh, stop_mms.sh,
                       reduce_mms.py, the rgm136 and ettelem sources, the device-command table, the tiles, ...), PLUS E216's box files:
                       src/run_e216.py (the runner: E208's imported, E216's lines and family G), src/fake_card_e216.py (rgm211's host's
                       double), src/ident_e216.py (the identity gate per process), src/build_e216.sh (rgm211's host), src/session_e216.sh,
                       src/start_e216.sh, src/dry_e216.sh, src/sched/a2c0-E216.json (the schedule, below); the identity gate's inputs
                       src/kernel-e216.json (the registration's, unchanged) and E206's checker src/e206/check_e206.py and
                       src/e206/e206_common.py (the lab's tools/claims-v3/e206/ files, unchanged); E211's rgm211 sources in src/rgm211/
                       (the ten files kernel-e216.json pins, unchanged); and src/SRC-SHA256SUMS (what E208's check_mms.py --box reads: every
                       src/ file but itself);
  fwgate/fwgate.py, fwgate/records/*.json     the lab's reboot gate, unchanged (its records beside it, as it reads them);
  build/, run/, sessions/, dry/, first/       written on the box (both builds, the box lock and STOP files, the session, the dry passes,
                                              step 7's folders).
THE SCHEDULE (src/sched/a2c0-E216.json), made here from three registered files and nothing else, each at its pin:
  plan-e216.json (the registration's: the order, each run's role, block, form, est_s and planning peak; the anchor), points-e216.json (the
  registration's: each point's arm token, format, mask and loop) and E209's registered sched-e209.json (E208's forms, timing, process and
  smoke, which E216.md 6 names: "E208's three smoke arms", the burst and null forms, the 60 s opening rest, the die gate's 180 s, the rule 45
  and the cap 55). Every point's data is random, E208's form (fp32 and fp16 src/tiles/<fmt>/randn.bin, int8 src/tiles/int8/full.bin, gen
  randn, seed 1). The run "i" is the run's place in plan-e216.json's order (1-69; "plan_n" keeps the plan's own count, which counts the
  smoke as 1). The kit word "1116-mmsweep" and E208's line 80.0 W are the words E208's schedule reader (mms_common.load_sched, unchanged)
  requires; E216's own line is "e216_line_w": 64.0 (run_e216.py refuses a run over it). Each process run carries its "family".
SPDX-License-Identifier: Apache-2.0
"""
import fcntl
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
E = "tools/claims-v3/e216"
E208 = "tools/claims-v3/e208/proposal/src"
FWG = "tools/claims-v3/fwgate"
BOXF = {"src/run_e216.py": f"{E}/box/run_e216.py", "src/fake_card_e216.py": f"{E}/box/fake_card_e216.py",
        "src/ident_e216.py": f"{E}/box/ident_e216.py", "src/build_e216.sh": f"{E}/box/build_e216.sh",
        "src/session_e216.sh": f"{E}/box/session_e216.sh", "src/start_e216.sh": f"{E}/box/start_e216.sh",
        "src/dry_e216.sh": f"{E}/box/dry_e216.sh", "src/sched/a2c0-E216.json": f"{E}/box/a2c0-E216.json",
        "src/kernel-e216.json": f"{E}/kernel-e216.json",
        "src/e206/check_e206.py": "tools/claims-v3/e206/check_e206.py", "src/e206/e206_common.py": "tools/claims-v3/e206/e206_common.py"}
# the registration's pins (SHA256SUMS-e216-registration) of the files this tool reads, and E209's registered schedule
REG_PINS = {f"{E}/plan-e216.json": "35090542617c45b19b073553454cc045f50421b173107775d4ca5fdcc14afb68",
            f"{E}/points-e216.json": "63899cae4e7122cf665f9ab37d146bb209d2294669f20c89ac87dbd689753e3c",
            f"{E}/kernel-e216.json": "41feea0fd6bba322a3a9e012d576914ac87316fe9f765919b983d3ad4aa07bfa",
            "tools/claims-v3/e209/sched-e209.json": "ec8713a7a69ddf5ee503f4efe6fd77bda3f63845aada69ac167fb9a2df0ec620",
            "tools/claims-v3/e206/check_e206.py": "fdbd35a63aa6b681322d228d8a50ecaadc70ae76bff51a9f0a57a6869d2b5a7d",
            "tools/claims-v3/e206/e206_common.py": "9278e1f1eca268a6f815b7d7514dd0c01a24ea13835796946142db2c8fb6d79d"}
E208_SUMS_PIN = "543e9298d5a1013d"          # E208's registered src/ list (its data checks' C0)
E208_PINS = {f"{E208}/reduce_mms.py": "b9e32618020d28a590a615f97e5655c1ea458a6a757bf5658f2517a87fc3e0a5",
             f"{E208}/mms_common.py": "c3fc7883544ad73c3e455f7e950b62b9b155fd2ed972cee5e3524d74a378569c",
             f"{E208}/run_mms.py": "5dae80e0"}
FWG_PIN = "4d529a5764a97373f451544821f0432ce31d6afaecad0f1e254d18d76e736b95"
KIT_WORD = "1116-mmsweep"
E208_LINE_W = 80.0
E216_LINE_W = 64.0
TILE = {"fp32": "src/tiles/fp32/randn.bin", "fp16": "src/tiles/fp16/randn.bin", "int8": "src/tiles/int8/full.bin"}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def shab(b):
    return hashlib.sha256(b).hexdigest()


def rp(r):
    return os.path.join(REPO, r)


def e208_files():
    out, bad = {}, []
    sums = rp(f"{E208}/SRC-SHA256SUMS")
    if not sha(sums).startswith(E208_SUMS_PIN):
        bad.append(f"{E208}/SRC-SHA256SUMS is not the registered list (sha256 {sha(sums)[:16]}, want {E208_SUMS_PIN})")
    for ln in open(sums):
        h, r = ln.rstrip("\n").split("  ", 1)
        src = f"{E208}/{r[len('src/'):]}"
        got = sha(rp(src)) if os.path.isfile(rp(src)) else "missing"
        if got != h:
            bad.append(f"{src}: {got[:16]}, want {h[:16]}")
        out[r] = (src, h)
    listed = set(out)
    for dp, dn, fn in os.walk(rp(E208)):
        dn[:] = [d for d in dn if d != "__pycache__"]
        for n in fn:
            r = "src/" + os.path.relpath(os.path.join(dp, n), rp(E208))
            if r != "src/SRC-SHA256SUMS" and not n.endswith(".pyc") and r not in listed:
                bad.append(f"{E208}/{r[4:]}: in E208's src/ but not in its list")
    for p, want in E208_PINS.items():
        if not sha(rp(p)).startswith(want):
            bad.append(f"{p}: not the registered {want[:16]}")
    return out, bad


def rgm211_files():
    """E211's rgm211 sources at kernel-e216.json's pins -> {'src/rgm211/<rel>': (repo path, sha256)}"""
    k = json.load(open(rp(f"{E}/kernel-e216.json")))["kernels"]["rgm211"]["sources_sha256"]
    out, bad = {}, []
    for repo_rel, want in sorted(k.items()):
        sub = repo_rel.split("tools/claims-v3/e211/rgm211/", 1)[1]
        got = sha(rp(repo_rel)) if os.path.isfile(rp(repo_rel)) else "missing"
        if got != want:
            bad.append(f"{repo_rel}: {got[:16]}, want {want[:16]}")
        out[f"src/rgm211/{sub}"] = (repo_rel, want)
    if len(out) != 10:
        bad.append(f"kernel-e216.json names {len(out)} rgm211 sources, not 10")
    return out, bad


def make_sched():
    """(json text, problems): E216's schedule from plan-e216.json, points-e216.json and E209's registered forms (module docstring)."""
    bad = []
    plan = json.load(open(rp(f"{E}/plan-e216.json")))
    pts = {p["id"]: p for p in json.load(open(rp(f"{E}/points-e216.json")))["points"]}
    s9 = json.load(open(rp("tools/claims-v3/e209/sched-e209.json")))
    anc = plan["anchor"]
    runs = []
    n_null = 0
    for k, o in enumerate(plan["order"], 1):
        base = {"i": k, "plan_n": o["n"], "block": o["block"], "role": o["role"], "form": o["form"], "est_s": o["est_s"],
                "est_peak_w": o["planning_peak_W"]}
        if o["role"] == "anchor":
            r = dict(base, arm=anc["arm"], unit=o["id"], test="fma", type=anc["type"], shires=anc["shires"], values=anc["values"],
                     family="rgm136 gemmL")
        elif o["role"] == "null":
            n_null += 1
            r = dict(base, arm=f"null-{n_null}", unit=o["id"], test="null")
        elif o["role"] == "arm":
            p = pts[o["id"]]
            if p["kind"] != "random":
                bad.append(f"{o['id']}: data kind {p['kind']}, not random")
            r = dict(base, arm=o["id"], unit=f"{p['arm']}|{p['fmt']}|{p['mask']}", test="fma", type=p["fmt"], shires=p["mask"],
                     values=f"{p['arm']}:randn:{TILE[p['fmt']]}", family=p["loop"])
        else:
            bad.append(f"order entry {o}: an unknown role")
            continue
        runs.append(r)
    for r in runs:
        if r["form"] not in s9["forms"]:
            bad.append(f"run {r['i']}: form {r['form']} not E209's")
        if r["est_peak_w"] > E216_LINE_W:
            bad.append(f"run {r['i']} {r['arm']}: planning peak {r['est_peak_w']} over the {E216_LINE_W} W line")
    if len(runs) != plan["n_runs"] or sum(1 for r in runs if r["role"] == "arm") != plan["n_point_runs"] \
            or sum(1 for r in runs if r["role"] == "anchor") != plan["n_anchors"] or n_null != plan["n_nulls"]:
        bad.append("the run counts are not plan-e216.json's")
    d = {"kit": KIT_WORD, "session": "E216", "card": "a2c0", "line_w": E208_LINE_W, "e216_line_w": E216_LINE_W,
         "forms": s9["forms"], "timing": s9["timing"], "process": s9["process"], "smoke": s9["smoke"], "seed": "E216|pass1",
         "planned_min": plan["planned_card_minutes"], "cap_est_w": round(max(r["est_peak_w"] for r in runs), 2),
         "stops_e216": plan["stops"], "runs": runs,
         "note": ("E216's registered order (plan-e216.json) in E208's schedule form, for the kit (make_box_e216.py); est_peak_w is the "
                  "registration's planning peak (the largest over the six scored forecasters, plan-e216.json); the anchor and nulls are "
                  "E208's; the forms, timing, process and smoke are E209's registered ones (sched-e209.json); the kit word and line_w "
                  "80.0 are what E208's schedule reader requires; e216_line_w and stops_e216 are E216's (run_e216.py reads them)")}
    if d["timing"] != {"cap_min": plan["cap_min"], "gate_wait_s": 180.0, "open_rest_s": 60.0, "rule_min": plan["rule_min"]}:
        bad.append(f"E209's timing {d['timing']} is not E216's rule {plan['rule_min']} and cap {plan['cap_min']}")
    return json.dumps(d, indent=1, sort_keys=True) + "\n", bad


def make_all():
    bad = []
    for p, want in REG_PINS.items():
        if sha(rp(p)) != want:
            bad.append(f"{p}: sha256 {sha(rp(p))[:16]}, not its pin {want[:16]}")
    e208, b2 = e208_files()
    bad += b2
    r211, b3 = rgm211_files()
    bad += b3
    sched_txt, b4 = make_sched()
    bad += b4
    src = {r: h for r, (_, h) in e208.items()}
    for r, f in BOXF.items():
        if r in src:
            bad.append(f"{r}: E216's box file would replace E208's")
        src[r] = shab(sched_txt.encode()) if r == "src/sched/a2c0-E216.json" else sha(rp(f))
    for r, (_, h) in r211.items():
        if r in src:
            bad.append(f"{r}: would replace another file")
        src[r] = h
    sums_txt = "".join(f"{h}  {r}\n" for r, h in sorted(src.items()))
    rows = []
    for r, (from_, h) in sorted(e208.items()):
        rows.append({"dest": r, "from": from_, "sha256": h, "what": "E208's registered kit, unchanged"})
    for r, f in sorted(BOXF.items()):
        what = ("E216's schedule (made here)" if r.endswith(".json") and "sched" in r else
                "the registration's kernel record, unchanged" if r == "src/kernel-e216.json" else
                "E206's identity checker, unchanged" if r.startswith("src/e206/") else "E216's box file")
        rows.append({"dest": r, "from": f, "sha256": src[r], "what": what})
    for r, (from_, h) in sorted(r211.items()):
        rows.append({"dest": r, "from": from_, "sha256": h, "what": "E211's rgm211 source at kernel-e216.json's pin (its host serves family G)"})
    rows.append({"dest": "src/SRC-SHA256SUMS", "from": f"{E}/box/SRC-SHA256SUMS-e216", "sha256": shab(sums_txt.encode()),
                 "what": "E216's src/ list (E208's check_mms.py --box reads it)"})
    if sha(rp(f"{FWG}/fwgate.py")) != FWG_PIN:
        bad.append(f"{FWG}/fwgate.py: not {FWG_PIN[:16]}")
    rows.append({"dest": "fwgate/fwgate.py", "from": f"{FWG}/fwgate.py", "sha256": FWG_PIN, "what": "the lab's reboot gate, unchanged"})
    for n in sorted(os.listdir(rp(f"{FWG}/records"))):
        if n.endswith(".json"):
            rows.append({"dest": f"fwgate/records/{n}", "from": f"{FWG}/records/{n}", "sha256": sha(rp(f"{FWG}/records/{n}")),
                         "what": "fwgate's committed firmware records (it reads them beside itself)"})
    harness = {"experiment": "E216", "what": "every file of E216's box root, from this checkout, at its sha256 (make_box_e216.py sync)",
               "box": "aifoundry2", "card": "a2c0", "schedule": "src/sched/a2c0-E216.json",
               "schedule_from": {k: REG_PINS[k] for k in (f"{E}/plan-e216.json", f"{E}/points-e216.json", "tools/claims-v3/e209/sched-e209.json")},
               "e208_src_list": {"file": f"{E208}/SRC-SHA256SUMS", "sha256": sha(rp(f"{E208}/SRC-SHA256SUMS")), "files": len(e208)},
               "n_files": len(rows), "files": rows}
    gen = {"box/a2c0-E216.json": sched_txt.encode(), "box/SRC-SHA256SUMS-e216": sums_txt.encode(),
           "harness-e216.json": (json.dumps(harness, indent=1, sort_keys=True) + "\n").encode()}
    return gen, bad


def cmd_make():
    gen, bad = make_all()
    if bad:
        print("MAKE REFUSED: " + "; ".join(bad))
        return 1
    for n, b in gen.items():
        with open(os.path.join(HERE, n), "wb") as f:
            f.write(b)
        print(f"wrote {E}/{n} ({len(b)} bytes, sha256 {shab(b)})")
    return 0


def cmd_check():
    gen, bad = make_all()
    for n, b in gen.items():
        p = os.path.join(HERE, n)
        if not os.path.exists(p) or open(p, "rb").read() != b:
            bad.append(f"{E}/{n}: differs from its re-make")
        else:
            print(f"{E}/{n}: equal to its re-make (sha256 {shab(b)[:16]})")
    h = json.loads(gen["harness-e216.json"])
    for row in h["files"]:
        got = sha(rp(row["from"])) if os.path.isfile(rp(row["from"])) else "missing"
        if got != row["sha256"]:
            bad.append(f"{row['from']}: {got[:16]}, want {row['sha256'][:16]}")
    s = json.loads(gen["box/a2c0-E216.json"])
    g = [r["arm"] for r in s["runs"] if r.get("family") == "rgm136 gemmLnc"]
    print(f"harness: {h['n_files']} files (E208's {h['e208_src_list']['files']}, E216's box files and inputs {len(BOXF)}, rgm211's sources 10, "
          f"its list, fwgate); the schedule: {len(s['runs'])} runs, the G block last ({', '.join(g)})")
    print("CHECK PASS" if not bad else "CHECK FAIL: " + "; ".join(bad))
    return 0 if not bad else 1


def cmd_sync(root):
    root = os.path.abspath(root)
    repo_real = os.path.realpath(REPO)
    if os.path.realpath(root) == repo_real or os.path.realpath(root).startswith(repo_real + os.sep):
        print("SYNC REFUSED: the box root is inside the lab checkout")
        return 3
    if os.path.basename(root).startswith("ee-") or "/ee-" in os.path.realpath(root):
        print("SYNC REFUSED: a folder named ee-* is the model session's")
        return 3
    h = json.load(open(os.path.join(HERE, "harness-e216.json")))
    os.makedirs(os.path.join(root, "run"), exist_ok=True)
    lk = open(os.path.join(root, "run", "box.lock"), "a+")
    try:
        fcntl.flock(lk.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("SYNC REFUSED: run/box.lock is held (a session, a build or a dry pass of the kit runs in this root)")
        return 3
    bad = []
    for row in h["files"]:
        src = rp(row["from"])
        if not os.path.isfile(src) or sha(src) != row["sha256"]:
            bad.append(f"{row['from']}: not at its sha256 in this checkout")
    if bad:
        print("SYNC REFUSED: " + "; ".join(bad))
        return 3
    want = {row["dest"] for row in h["files"]}
    n_new = n_same = 0
    for row in h["files"]:
        dst = os.path.join(root, row["dest"])
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.isfile(dst) and not os.path.islink(dst) and sha(dst) == row["sha256"]:
            n_same += 1
            continue
        tmp = dst + ".sync-tmp"
        shutil.copyfile(rp(row["from"]), tmp)
        os.chmod(tmp, 0o644)
        os.replace(tmp, dst)
        n_new += 1
    pruned = []
    for top in ("src", "fwgate"):
        for dp, dn, fn in os.walk(os.path.join(root, top)):
            dn[:] = [d for d in dn if d != "__pycache__"]
            for n in fn:
                p = os.path.join(dp, n)
                r = os.path.relpath(p, root)
                if r not in want and not os.path.islink(p) and os.path.isfile(p):
                    os.remove(p)
                    pruned.append(r)
    for row in h["files"]:
        dst = os.path.join(root, row["dest"])
        got = sha(dst) if os.path.isfile(dst) and not os.path.islink(dst) else "missing"
        if got != row["sha256"]:
            bad.append(f"{row['dest']}: {got[:16]} after the copy, want {row['sha256'][:16]}")
    try:
        head = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=30).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        head = None
    rec = {"experiment": "E216", "synced": time.strftime("%Y-%m-%d %H:%M:%S %Z"), "from_head": head,
           "harness_sha256": sha(os.path.join(HERE, "harness-e216.json")), "files": len(want), "copied": n_new, "already": n_same,
           "pruned": pruned, "verdict": "SYNCED" if not bad else "SYNC FAILED", "problems": bad}
    with open(os.path.join(root, "SYNC-e216.json"), "w") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
    print(f"{rec['verdict']}: {len(want)} files at the harness's sha256 ({n_new} copied, {n_same} already there, {len(pruned)} pruned "
          f"{pruned[:6]}) from HEAD {head}" + (f"; {'; '.join(bad)}" if bad else ""))
    return 0 if not bad else 14


def main(argv):
    if argv[:1] == ["make"]:
        return cmd_make()
    if argv[:1] == ["check"]:
        return cmd_check()
    if argv[:1] == ["sync"] and len(argv) == 2:
        return cmd_sync(argv[1])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
