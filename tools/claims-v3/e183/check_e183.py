#!/usr/bin/env python3
"""E183's checks (Q155, the kit), off-card: they read files, never the card. E180's checks (check_e180.py, check_e180_v2.py) ported.

    python3 -B tools/claims-v3/e183/check_e183.py harness [--binaries]
        every file the box session runs, sources, builds from or reads equals harness-e183.json's sha256, and every image its
        kinds-e183.json sha256; with --binaries also the train host's build: build/enercat-e183/BUILD-E183.json exists, its two binaries
        equal its record, its patched main.cpp is the pinned one, and its source tree equals harness-e183.json's build_tree file by file.
        Prints "HARNESS OK: <n> files" or the faults; exit 1 on any.
    python3 -B tools/claims-v3/e183/check_e183.py block <block dir> --card <id> --root <tree>
        the post-block check: the anchors' bursts by workloads/enercat/analyze_catalogue.py's bursts_of (E180's), and the train's
        processes (13 launches each, every one ok, each launch's kind and image by the registered schedule); writes <dir>/check.json and
        prints "<status> <note>" (ok | partial | fail).
    python3 -B tools/claims-v3/e183/check_e183.py smoke <smoke dir> --root <tree>
        the smoke's gate (E183.md section 7): every smoke burst has its launches and a kept burst at 600 MHz, their rates within 3% of
        each other (E180's gate), and both train processes have 13 launches ok, each launch's kind and image by the schedule, the card at
        600 MHz in every sample of the processes' span. Prints "SMOKE GO" or "SMOKE NO-GO: <why>"; exit 1 on NO-GO.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import hashlib
import importlib
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e183_common as E  # noqa: E402

EXPECTED_BURST_LAUNCHES = (6, 7, 8)     # a 3 s burst of 0.4 s launches (E180's)
EXPECTED_SMOKE_LAUNCHES = (2, 3)        # a 1 s burst


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def jl(path):
    if os.path.exists(path + ".gz"):
        return [json.loads(l) for l in gzip.open(path + ".gz", "rt") if l.startswith("{")]
    if os.path.exists(path):
        return [json.loads(l) for l in open(path) if l.startswith("{")]
    return []


def harness(binaries, root=ROOT):
    h = json.load(open(os.path.join(HERE, "harness-e183.json")))
    bad = []
    for rel, want in sorted(h["files"].items()):
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            bad.append(f"missing {rel}")
        elif sha(p) != want:
            bad.append(f"changed {rel}")
    for name, k in E.kinds()["kinds"].items():
        p = os.path.join(root, k["image"])
        if not os.path.exists(p) or sha(p) != k["image_sha256"]:
            bad.append(f"image of {name} differs from kinds-e183.json")
    n = len(h["files"])
    if binaries:
        bj = os.path.join(root, E.BUILD_RECORD)
        if not os.path.exists(bj):
            bad.append(f"{E.BUILD_RECORD} missing (the train host: build_host_e183.sh)")
        else:
            b = json.load(open(bj))
            for rel, want in b["binaries"].items():
                p = os.path.join(root, rel)
                if not os.path.exists(p) or sha(p) != want:
                    bad.append(f"binary {rel} differs from BUILD-E183.json")
                n += 1
            if b.get("patched_main_sha256") != h["patched_main_sha256"]:
                bad.append("the build's patched main.cpp is not the pinned one")
            if b.get("source_tree_sha256") != h["build_tree"]:
                diff = sorted(set(b.get("source_tree_sha256", {}).items()) ^ set(h["build_tree"].items()))
                bad.append(f"the build's source tree differs from harness-e183.json's build_tree ({len(diff)} entries)")
            n += len(h["build_tree"])
    if bad:
        print("HARNESS FAULTS: " + "; ".join(bad[:12]) + (f" (+{len(bad) - 12})" if len(bad) > 12 else ""))
        return 1
    print(f"HARNESS OK: {n} files")
    return 0


def analyzer(root):
    sys.path.insert(0, os.path.join(root, "workloads", "enercat"))
    try:
        return importlib.import_module("analyze_catalogue")
    finally:
        sys.path.pop(0)


def bursts(d, root):
    tel, runs = jl(os.path.join(d, "telemetry.jsonl")), jl(os.path.join(d, "runs.jsonl"))
    cfgs = (json.load(open(os.path.join(d, "configs.json"))) if os.path.exists(os.path.join(d, "configs.json")) else {}).get("cfgs", [])
    if len(tel) < 30 or not runs:
        return [], runs, tel, cfgs
    res = analyzer(root).bursts_of(tel, runs)
    return (res[0] if isinstance(res, tuple) else res), runs, tel, cfgs


def train_faults(d, train, processes):
    """the train's processes against the plan: 13 launches each, every one ok, each launch's kind and image by the schedule"""
    recs = jl(os.path.join(d, "train.jsonl"))
    byp = {}
    for r in recs:
        byp.setdefault(r["process"], []).append(r)
    imgs = {"F": E.image_rel(train["first"]), "S": E.image_rel(train["second"])}
    faults, good = [], 0
    for k, ori in processes:
        L = sorted(byp.get(k, []), key=lambda r: r.get("launch", -1))
        want = E.schedule(ori)
        why = None
        if len(L) != E.LAUNCHES:
            why = f"{len(L)} launches"
        elif not all(r.get("ok") for r in L):
            why = "a launch not ok"
        elif [r.get("train_kind") for r in L] != want or any(r.get("abba") != ori or r.get("orientation") != ori for r in L):
            why = "a launch's kind or orientation off the schedule"
        elif any(not str(r.get("train_operands", "")).endswith(imgs[r["train_kind"]]) for r in L):
            why = "a launch's image is not its kind's"
        elif [r.get("launch") for r in L] != list(range(E.LAUNCHES)):
            why = "the launch numbers are not 0-12"
        if why:
            faults.append(f"process {k}: {why}")
        else:
            good += 1
    return faults, good, recs


def mhz_off(tel, recs):
    """samples off 600 MHz in the span of the given launch records"""
    if not recs:
        return 0
    lo, hi = min(r["t_start_ms"] for r in recs), max(r["t_end_ms"] for r in recs)
    return sum(1 for s in tel if lo <= s.get("t_ms", 0) <= hi and s.get("mhz", {}).get("minion") != 600)


def block(d, card, root):
    bl, runs, tel, cfgs = bursts(d, root)
    pj = json.load(open(os.path.join(d, "pass.json"))) if os.path.exists(os.path.join(d, "pass.json")) else {}
    expected = [c["cfg"] for c in cfgs]
    have = {r["cfg"] for r in runs}
    missing = [c for c in expected if c not in have]
    cut = {b["cfg"] for b in bl}
    uncut = [c for c in expected if c in have and c not in cut]
    off = [b["cfg"] for b in bl if not b["mhz_busy_all_600"]]
    launches = {c: sum(1 for r in runs if r["cfg"] == c) for c in expected}
    short = [c for c, n in launches.items() if c in have and n not in EXPECTED_BURST_LAUNCHES]
    conf = json.load(open(os.path.join(d, "configs.json"))) if os.path.exists(os.path.join(d, "configs.json")) else {}
    procs = [(p["process"], p["orientation"]) for p in conf.get("processes", [])]
    tr = E.train_of_block(pj.get("pass", conf.get("pass")))
    tf, good, recs = train_faults(d, tr, procs)
    toff = mhz_off(tel, recs)
    res = {"card": card, "block": tr["block"], "train": tr["train"], "anchors_expected": len(expected), "anchors_with_launches": len(have),
           "missing": missing, "uncut": uncut, "off_600": off, "launch_counts": launches, "short_bursts": short,
           "processes_planned": len(procs), "processes_good": good, "train_faults": tf[:20], "train_samples_off_600": toff,
           "n_tel": len(tel), "n_runs": len(runs), "n_train_launches": len(recs),
           "die_c_busy_max": max((b["die_c_busy"] for b in bl), default=None),
           "board_w_max": max((s["board_w"] for s in tel), default=None)}
    if len(tel) < 30 or (not recs and not runs) or good < len(procs) // 2:
        st, note = "fail", f"no data (telemetry lines {len(tel)}, anchor launches {len(runs)}, {good} of {len(procs)} train processes good)"
    elif missing or uncut or off or tf or toff:
        st, note = "partial", (f"{len(missing)} anchors without a launch, {len(uncut)} not cut, {len(off)} off 600 MHz; {len(tf)} train "
                               f"processes not good, {toff} train samples off 600 MHz: {'; '.join((missing + uncut + off + tf)[:4])}")
    else:
        st, note = "ok", (f"{len(bl)}/{len(expected)} anchors, {good}/{len(procs)} train processes; die "
                          f"{res['die_c_busy_max'] if res['die_c_busy_max'] is not None else float('nan'):.1f} C at most, board "
                          f"{res['board_w_max']:.2f} W at most")
    res.update({"status": st, "note": note})
    json.dump(res, open(os.path.join(d, "check.json"), "w"), indent=1)
    print(f"{st} {note}")
    return 0


def smoke(d, root):
    bl, runs, tel, cfgs = bursts(d, root)
    expected = [c["cfg"] for c in cfgs]
    why = []
    have = {r["cfg"] for r in runs}
    cut = {b["cfg"]: b for b in bl}
    for c in expected:
        n = sum(1 for r in runs if r["cfg"] == c)
        if c not in have:
            why.append(f"{c}: no launch")
        elif n not in EXPECTED_SMOKE_LAUNCHES or not all(r.get("ok") for r in runs if r["cfg"] == c):
            why.append(f"{c}: {n} launches or one not ok")
        elif c not in cut:
            why.append(f"{c}: not cut by bursts_of")
        elif not cut[c]["mhz_busy_all_600"]:
            why.append(f"{c}: off 600 MHz")
    rates = [cut[c]["ops_per_s"] for c in expected if c in cut]
    if rates and (max(rates) - min(rates)) / max(rates) > 0.03:
        why.append(f"instruction rates differ by {(max(rates) - min(rates)) / max(rates):.1%} (the loop's timing must not depend on the number)")
    conf = json.load(open(os.path.join(d, "configs.json"))) if os.path.exists(os.path.join(d, "configs.json")) else {}
    procs = [(p["process"], p["orientation"]) for p in conf.get("processes", [])]
    sm = E.plan()["smoke"]
    if [o for _, o in procs] != sm["train_orientations"][:sm["train_processes"]]:
        why.append(f"the train part ran {procs}, not the plan's {sm['train_orientations']}")
    tf, good, recs = train_faults(d, E.trains()[sm["train"]], procs)
    why += [f"train {f}" for f in tf]
    toff = mhz_off(tel, recs)
    if toff:
        why.append(f"{toff} samples off 600 MHz during the train part")
    if why:
        print("SMOKE NO-GO: " + "; ".join(why))
        return 1
    print(f"SMOKE GO: {len(expected)} bursts, rates {min(rates):.4e}-{max(rates):.4e} a second; {good} train processes of "
          f"{E.LAUNCHES} launches by the schedule, at 600 MHz")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["harness", "block", "smoke"])
    ap.add_argument("dir", nargs="?")
    ap.add_argument("--card")
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--binaries", action="store_true")
    a = ap.parse_args()
    if a.cmd == "harness":
        sys.exit(harness(a.binaries, a.root))
    if a.cmd == "block":
        sys.exit(block(a.dir, a.card, a.root))
    sys.exit(smoke(a.dir, a.root))


if __name__ == "__main__":
    main()
