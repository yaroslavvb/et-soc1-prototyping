#!/usr/bin/env python3
"""E220 ARM B (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum): arm B's BOX ROOT - what runs on aifoundry2, from where, at
which bytes - and arm B's SCHEDULE in E208's form. E216's make_box_e216.py (landed in 59f5288b, whose box root ran E216 FULL on this card: 69
of 69 runs, data a8ce142d), with E220 arm B's files and registration. Python's own modules only.

    /usr/bin/python3 -I -B tools/claims-v3/e220/make_box_e220b.py make     writes box/a2c0-E220.json, box/SRC-SHA256SUMS-e220b and
                                                                           harness-e220b.json beside this file (the desk, once)
    /usr/bin/python3 -I -B tools/claims-v3/e220/make_box_e220b.py check    re-makes all three in memory, compares them byte for byte with
                                                                           the committed files and checks every source: CHECK PASS
    /usr/bin/python3 -I -B tools/claims-v3/e220/make_box_e220b.py sync <root>   copies the harness's files from this checkout into the
                                                                           box root (step 5), then reads every one back at its sha256

THE BOX ROOT is E208's kit layout (tools/claims-v3/e208/proposal/src/README.md, "the kit's root") in a folder of the card lane's own (the
card-lane brief names it; never a model session's ee-* folder, never inside the lab clone):
  src/                 E208's registered kit, every file UNCHANGED at its committed sha256 (run_mms.py, mms_common.py, mms_ident.py,
                       fake_card_mms.py, guard_ettelem.sh, build_mms.sh, preflight_mms.sh, check_mms.py, status_mms.sh, stop_mms.sh,
                       reduce_mms.py, the rgm136 and ettelem sources, the device-command table, the tiles, ...), PLUS E220 arm B's box files:
                       src/run_e220b.py (the runner: E208's imported, E220's lines and family G), src/fake_card_e220b.py (rgm211's host's
                       double), src/ident_e220b.py (the identity gate per process), src/build_e220b.sh (rgm211's host), src/session_e220b.sh,
                       src/start_e220b.sh, src/dry_e220b.sh, src/sched/a2c0-E220.json (the schedule, below); the identity gate's inputs
                       src/kernel-e220.json (the registration's, unchanged) and E206's checker src/e206/check_e206.py and
                       src/e206/e206_common.py (the lab's tools/claims-v3/e206/ files, unchanged); E211's rgm211 sources in src/rgm211/
                       (the ten files kernel-e220.json pins, unchanged); and src/SRC-SHA256SUMS (what E208's check_mms.py --box reads: every
                       src/ file but itself);
  fwgate/fwgate.py, fwgate/records/*.json     the lab's reboot gate, unchanged (its records beside it, as it reads them);
  build/, run/, sessions/, dry/, first/       written on the box (both builds, the box lock and STOP files, the session, the dry passes,
                                              step 7's folders).
THE SCHEDULE (src/sched/a2c0-E220.json), made here from four files and nothing else, each at its pin: plan-e220.json (the registration's: arm
B's order - plan-e220.json > arms > B > runs, 104 entries - each run's block and planning peak PP32, D1's smoke rows, the card time),
points-e220.json (the registration's: each point's arm token, format, mask and loop), E209's registered sched-e209.json (E208's burst form,
process and smoke, which E220.md 6 names: "E216's run form (E208's runner and schedule form)"; s01 = "E216's opening smoke on this card: E208's
three smoke arms", the schedule's smoke) and the kit's timeout table (desk/timeouts-e220.json > arms > B: each process's plain timeout, 10 s
but xf04's 13 s, E218's R0 lesson). The entries: s01 the schedule's smoke (E208's three arms, run by E208's runner before the runs); t01 (three
times) a run of role "anchor" (E208's word for a reference run of no point: run and read, never in a rule; the frozen scorer reads role anchor
or tie as the tie and counts its checks in R0); every registered point a run of role "arm" (its id the run's arm); s03 (D1: gemmLnc6x5x10 fp32
random, E216's g10 on this card) a run of role "arm" and family G in block "G-smoke" right before the G block - one checked process in E216's
burst form, the G block's own gate and stop path (THE KERNEL STOPS: a failed s03 stops the session before any G point; the frozen scorer reads
no point by its id). Every point's data is random, E208's form (fp32 and fp16 src/tiles/<fmt>/randn.bin, int8 src/tiles/int8/full.bin, gen
randn, seed 1). The run "i" is the run's place in the schedule (1-103; "plan_n" keeps the plan's own n, which counts s01 as 1). The timing is
E220.md 6's for arm B (no run starts after 60 card-minutes, the session ends at 70; the die gate 55 C, at most 180 s; E209's 60 s opening
rest). The kit word "1116-mmsweep" and E208's line 80.0 W are the words E208's schedule reader (mms_common.load_sched, unchanged) requires;
E220 arm B's own line is "e220b_line_w": 67.0 (the drop line, E220.md 6: run_e220b.py refuses a run planned at or above it). Each process run
carries its "family" and its "timeout_s".
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
E = "tools/claims-v3/e220"
E208 = "tools/claims-v3/e208/proposal/src"
FWG = "tools/claims-v3/fwgate"
BOXF = {"src/run_e220b.py": f"{E}/box/run_e220b.py", "src/fake_card_e220b.py": f"{E}/box/fake_card_e220b.py",
        "src/ident_e220b.py": f"{E}/box/ident_e220b.py", "src/build_e220b.sh": f"{E}/box/build_e220b.sh",
        "src/session_e220b.sh": f"{E}/box/session_e220b.sh", "src/start_e220b.sh": f"{E}/box/start_e220b.sh",
        "src/dry_e220b.sh": f"{E}/box/dry_e220b.sh", "src/sched/a2c0-E220.json": f"{E}/box/a2c0-E220.json",
        "src/kernel-e220.json": f"{E}/kernel-e220.json",
        "src/e206/check_e206.py": "tools/claims-v3/e206/check_e206.py", "src/e206/e206_common.py": "tools/claims-v3/e206/e206_common.py"}
# the registration's pins (SHA256SUMS-e220-registration) of the files this tool reads, and E209's registered schedule
REG_PINS = {f"{E}/plan-e220.json": "6d63318734f61bc6b9c9fa7550b52434b2d309e9f1182a6964413fb3a6ef79d9",
            f"{E}/points-e220.json": "2451ca9d3763c17b2366a4c1b88e680a15a30a01a7a93e0cbf1c041d9f87bd28",
            f"{E}/kernel-e220.json": "f332b03a9f30aee15ba465c8c497ee31a2cfc758bcb91a6ae10ed8453e54338e",
            f"{E}/desk/timeouts-e220.json": "36b86f86620fe65397b4393cb13ed6a952dc64e2230bb84728aa04509939a96b",
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
E220B_LINE_W = 67.0
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
    """E211's rgm211 sources at kernel-e220.json's pins -> {'src/rgm211/<rel>': (repo path, sha256)}"""
    k = json.load(open(rp(f"{E}/kernel-e220.json")))["kernels"]["rgm211_host"]["sources_sha256"]
    out, bad = {}, []
    for repo_rel, want in sorted(k.items()):
        sub = repo_rel.split("tools/claims-v3/e211/rgm211/", 1)[1]
        got = sha(rp(repo_rel)) if os.path.isfile(rp(repo_rel)) else "missing"
        if got != want:
            bad.append(f"{repo_rel}: {got[:16]}, want {want[:16]}")
        out[f"src/rgm211/{sub}"] = (repo_rel, want)
    if len(out) != 10:
        bad.append(f"kernel-e220.json names {len(out)} rgm211 sources, not 10")
    return out, bad


S03_D1 = {"token": "gemmLnc6x5x10", "fmt": "fp32", "mask": "0xffffffff", "est_peak_w": 62.25}   # D1: E216's g10; its session never above 62.25 W
STOPS_E220B = {"board_W_strictly_above_on_3_samples_in_a_row": 70.0, "die_mean_minshire0_at_or_above_C": 70.0,
               "latch_minshire2_at_or_above_C_once_risen_in_session": 70.0}


def make_sched():
    """(json text, problems): E220 arm B's schedule from plan-e220.json, points-e220.json, E209's registered forms and the kit's timeouts
    (module docstring)."""
    bad = []
    plan = json.load(open(rp(f"{E}/plan-e220.json")))["arms"]["B"]
    pts = {p["id"]: p for p in json.load(open(rp(f"{E}/points-e220.json")))["points"]["B"]}
    s9 = json.load(open(rp("tools/claims-v3/e209/sched-e209.json")))
    to = {k: int(v["timeout_s"]) for k, v in json.load(open(rp(f"{E}/desk/timeouts-e220.json")))["arms"]["B"]["timeouts"].items()}
    order = plan["runs"]
    if not order or order[0]["id"] != "s01" or order[0]["block"] != "smoke" or "E208's three smoke arms" not in order[0].get("D1", ""):
        bad.append("the plan's first entry is not D1's s01 (E208's three smoke arms)")
    d1 = plan["departure_D1_smoke"]["rows"]["s03"]["run"]
    if not d1.startswith("gemmLnc6x5x10 fp32 random, the full chip") or "62.25 W" not in d1:
        bad.append(f"D1's s03 is not {S03_D1['token']} ({d1[:60]})")
    blocks = {"tie": "tie", "pass1": "pass1", "pass2": "pass2", "G block": "G block", "G block reversed (G2 only)": "G block reversed"}
    runs = []
    for o in order[1:]:
        k = len(runs) + 1
        base = {"i": k, "plan_n": o["n"], "form": "burst", "est_s": float(plan["card_time"]["pace_s_per_run"]), "timeout_s": to.get(o["id"], 10)}
        if o["id"] == "t01":
            r = dict(base, block="tie", role="anchor", arm="t01", unit="t01", test="fma", type=o["fmt"], shires=o["mask"],
                     values=f"{o['token']}:randn:{TILE[o['fmt']]}", family="rgm136 gemmL", est_peak_w=round(float(o["PP32_W"]), 3))
        elif o["id"] == "s03":
            r = dict(base, block="G-smoke", role="arm", arm="s03", unit=f"{S03_D1['token']}|{S03_D1['fmt']}|{S03_D1['mask']}", test="fma",
                     type=S03_D1["fmt"], shires=S03_D1["mask"], values=f"{S03_D1['token']}:randn:{TILE[S03_D1['fmt']]}",
                     family="rgm136 gemmLnc", est_peak_w=S03_D1["est_peak_w"])
        else:
            p = pts.get(o["id"])
            if p is None:
                bad.append(f"{o['id']}: not a registered point of arm B")
                continue
            if p["kind"] != "random" or (p["arm"], p["format"], p["shire_mask"]) != (o["token"], o["fmt"], o["mask"]):
                bad.append(f"{o['id']}: the plan's row {o['token']} {o['fmt']} {o['mask']} is not the point's")
            if blocks.get(o["block"]) is None:
                bad.append(f"{o['id']}: an unknown block {o['block']}")
            r = dict(base, block=blocks.get(o["block"], o["block"]), role="arm", arm=o["id"], unit=f"{p['arm']}|{p['format']}|{p['shire_mask']}",
                     test="fma", type=p["format"], shires=p["shire_mask"], values=f"{p['arm']}:randn:{TILE[p['format']]}", family=p["loop"],
                     est_peak_w=round(float(o["PP32_W"]), 3))
        runs.append(r)
    for r in runs:
        if r["form"] not in s9["forms"]:
            bad.append(f"run {r['i']}: form {r['form']} not E209's")
        if r["est_peak_w"] >= E220B_LINE_W:
            bad.append(f"run {r['i']} {r['arm']}: planning peak {r['est_peak_w']} at or over the {E220B_LINE_W} W line")
    n_pt = sum(1 for r in runs if r["role"] == "arm" and r["arm"] != "s03")
    if len(runs) != plan["n_runs"] + 1 or n_pt != plan["n_runs"] - 3 or sum(1 for r in runs if r["role"] == "anchor") != 3:
        bad.append("the run counts are not plan-e220.json's (102 runs: 99 point runs and three ties, and s03)")
    ct = plan["card_time"]
    timing = {"cap_min": float(ct["cap_card_minutes"]), "gate_wait_s": 180.0, "open_rest_s": float(s9["timing"]["open_rest_s"]),
              "rule_min": float(ct["rule_card_minutes"])}
    if (timing["rule_min"], timing["cap_min"]) != (60.0, 70.0) or "waited at most 180 s" not in plan["die_gate"]:
        bad.append(f"the timing {timing} is not E220.md 6's rule 60 and cap 70")
    d = {"kit": KIT_WORD, "session": "E220", "card": "a2c0", "line_w": E208_LINE_W, "e220b_line_w": E220B_LINE_W,
         "forms": s9["forms"], "timing": timing, "process": s9["process"], "smoke": s9["smoke"], "seed": "E220|B|pass1",
         "planned_min": round(float(ct["planned_card_minutes"]), 2), "cap_est_w": round(max(r["est_peak_w"] for r in runs), 2),
         "stops_e220b": STOPS_E220B, "runs": runs,
         "note": ("E220 arm B's registered order (plan-e220.json > arms > B > runs) in E208's schedule form, for the kit (make_box_e220b.py): "
                  "s01 is the smoke (D1: E208's three smoke arms, E209's registered smoke rows); t01 runs as role anchor (a tie, never in a rule); "
                  "s03 (D1: gemmLnc6x5x10, E216's g10) a family-G burst right before the G block; est_peak_w is MM1-v3.2's planning peak PP32 "
                  "(plan-e220.json; s03's the card's measured session peak, D1); timeout_s the kit's sized plain timeout (desk/timeouts-e220.json); "
                  "the forms, process and smoke are E209's registered ones (sched-e209.json), the timing E220.md 6's (rule 60, cap 70); the kit "
                  "word and line_w 80.0 are what E208's schedule reader requires; e220b_line_w (the drop line) and stops_e220b are E220's "
                  "(run_e220b.py reads them)")}
    if [r["arm"] for r in runs if r.get("family") == "rgm136 gemmLnc"] != ["s03"] + [x["id"] for x in order if x["block"].startswith("G block")]:
        bad.append("the G block is not s03 then the plan's G block, last")
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
            bad.append(f"{r}: E220's box file would replace E208's")
        src[r] = shab(sched_txt.encode()) if r == "src/sched/a2c0-E220.json" else sha(rp(f))
    for r, (_, h) in r211.items():
        if r in src:
            bad.append(f"{r}: would replace another file")
        src[r] = h
    sums_txt = "".join(f"{h}  {r}\n" for r, h in sorted(src.items()))
    rows = []
    for r, (from_, h) in sorted(e208.items()):
        rows.append({"dest": r, "from": from_, "sha256": h, "what": "E208's registered kit, unchanged"})
    for r, f in sorted(BOXF.items()):
        what = ("E220's schedule (made here)" if r.endswith(".json") and "sched" in r else
                "the registration's kernel record, unchanged" if r == "src/kernel-e220.json" else
                "E206's identity checker, unchanged" if r.startswith("src/e206/") else "E220's box file")
        rows.append({"dest": r, "from": f, "sha256": src[r], "what": what})
    for r, (from_, h) in sorted(r211.items()):
        rows.append({"dest": r, "from": from_, "sha256": h, "what": "E211's rgm211 source at kernel-e220.json's pin (its host serves family G)"})
    rows.append({"dest": "src/SRC-SHA256SUMS", "from": f"{E}/box/SRC-SHA256SUMS-e220b", "sha256": shab(sums_txt.encode()),
                 "what": "E220's src/ list (E208's check_mms.py --box reads it)"})
    if sha(rp(f"{FWG}/fwgate.py")) != FWG_PIN:
        bad.append(f"{FWG}/fwgate.py: not {FWG_PIN[:16]}")
    rows.append({"dest": "fwgate/fwgate.py", "from": f"{FWG}/fwgate.py", "sha256": FWG_PIN, "what": "the lab's reboot gate, unchanged"})
    for n in sorted(os.listdir(rp(f"{FWG}/records"))):
        if n.endswith(".json"):
            rows.append({"dest": f"fwgate/records/{n}", "from": f"{FWG}/records/{n}", "sha256": sha(rp(f"{FWG}/records/{n}")),
                         "what": "fwgate's committed firmware records (it reads them beside itself)"})
    harness = {"experiment": "E220", "what": "every file of E220's box root, from this checkout, at its sha256 (make_box_e220b.py sync)",
               "box": "aifoundry2", "card": "a2c0", "schedule": "src/sched/a2c0-E220.json",
               "schedule_from": {k: REG_PINS[k] for k in (f"{E}/plan-e220.json", f"{E}/points-e220.json", "tools/claims-v3/e209/sched-e209.json")},
               "e208_src_list": {"file": f"{E208}/SRC-SHA256SUMS", "sha256": sha(rp(f"{E208}/SRC-SHA256SUMS")), "files": len(e208)},
               "n_files": len(rows), "files": rows}
    gen = {"box/a2c0-E220.json": sched_txt.encode(), "box/SRC-SHA256SUMS-e220b": sums_txt.encode(),
           "harness-e220b.json": (json.dumps(harness, indent=1, sort_keys=True) + "\n").encode()}
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
    h = json.loads(gen["harness-e220b.json"])
    for row in h["files"]:
        got = sha(rp(row["from"])) if os.path.isfile(rp(row["from"])) else "missing"
        if got != row["sha256"]:
            bad.append(f"{row['from']}: {got[:16]}, want {row['sha256'][:16]}")
    s = json.loads(gen["box/a2c0-E220.json"])
    g = [r["arm"] for r in s["runs"] if r.get("family") == "rgm136 gemmLnc"]
    print(f"harness: {h['n_files']} files (E208's {h['e208_src_list']['files']}, E220's box files and inputs {len(BOXF)}, rgm211's sources 10, "
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
    h = json.load(open(os.path.join(HERE, "harness-e220b.json")))
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
    rec = {"experiment": "E220", "synced": time.strftime("%Y-%m-%d %H:%M:%S %Z"), "from_head": head,
           "harness_sha256": sha(os.path.join(HERE, "harness-e220b.json")), "files": len(want), "copied": n_new, "already": n_same,
           "pruned": pruned, "verdict": "SYNCED" if not bad else "SYNC FAILED", "problems": bad}
    with open(os.path.join(root, "SYNC-e220b.json"), "w") as f:
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
