#!/usr/bin/env python3
"""EXPERIMENT nocr (hub rungs 31 and 32): plans, card rules, the pre-registration lock, and the dry-run stub.

  nocr.py check-card --pass P --card C       may pass P run on card C? (exit 0 yes, 2 no, with the reason)
  nocr.py plan --pass P --out DIR            every file a pass needs: call lists, host plans, procs.txt
  nocr.py lockcheck [--kernel ELF]           validation passes: LOCK.sha256, PREREG.sha256, kernel .text hash
  nocr.py check-sets                         sets.json equals what workloads/nocroute/meshmap.py generates
  nocr.py export-sets                        rewrite sets.json from meshmap.py (development only)
  nocr.py tel                                stdin: ettelem sample lines -> "die_mean_c minion_mhz" (empty if none)
  nocr.py texthash ELF                       sha256 of the ELF's .text section (the same on every host's toolchain)
  nocr.py fakehost --plan F --out-dir D [--theory T] [--seed S]
                                             V3_DRY only: what nocroute_host would print, from a model (README.md)
  nocr.py selftest [--dir D] [--theory T]    the discrimination test: plan, fakehost and reduce.py for every planted
                                             model; checks that each registered verdict is the planted answer

Nothing here opens a device.
"""
import argparse
import hashlib
import json
import os
import random
import re
import struct
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "workloads", "nocroute"))
import meshmap as mm  # noqa: E402

PARAMS = json.load(open(os.path.join(HERE, "params.json")))

# call-list encoding (workloads/nocroute/nocroute_args.h)
SC, MS, NOP, SELF = 1, 2, 3, 0xFF
BAD = 0xFFFFFFFF
DEV_CARD = "aifoundry1-c1"
VAL_CARDS = ("aifoundry3", "aifoundry2")
# DV2's frozen validation holds aifoundry2 until about 17:00 PDT on 29 September 2026: 00:30 UTC on 30 September
A2_FREE_AFTER = 1790728200


def enc(kind, ident, a=0, b=0):
    return kind | (ident << 8) | (a << 16) | (b << 24)


def dec(e):
    return e & 0xFF, (e >> 8) & 0xFF, (e >> 16) & 0xFF, (e >> 24) & 0xFF


def pass_kind(p):
    if p == 9:
        return "smoke"
    if 1 <= p <= 8:
        return "dev"
    if 11 <= p <= 19:
        return "val"
    return None


# ---------------------------------------------------------------- card rules
def check_card(p, card, dry=False, now=None):
    kind = pass_kind(p)
    if kind is None:
        return False, f"pass {p} is not 9 (smoke), 1-8 (development) or 11-19 (validation)"
    if card == "aifoundry1-c0":
        return False, "aifoundry1 card 0 is never used"
    if card not in (DEV_CARD,) + VAL_CARDS:
        return False, f"unknown card {card}"
    if card == "aifoundry2" and not dry:
        now = time.time() if now is None else now
        if now < A2_FREE_AFTER:
            return False, "aifoundry2 runs DV2's frozen validation until about 17:00 PDT 29 September"
    if kind == "dev" and card != DEV_CARD:
        return False, f"development passes run only on the development card ({DEV_CARD})"
    if kind == "val" and card == DEV_CARD:
        return False, "validation runs on a different card from development"
    return True, f"{kind} pass {p} on {card}"


# ---------------------------------------------------------------- the pre-registration lock
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def elf_text(path):
    """The bytes of the .text section of a little-endian ELF64 file."""
    b = open(path, "rb").read()
    if b[:4] != b"\x7fELF" or b[4] != 2:
        raise ValueError(f"{path}: not an ELF64 file")
    shoff, = struct.unpack_from("<Q", b, 0x28)
    shentsize, shnum, shstrndx = struct.unpack_from("<HHH", b, 0x3A)
    secs = [struct.unpack_from("<IIQQQQIIQQ", b, shoff + i * shentsize) for i in range(shnum)]
    stro = secs[shstrndx][4]
    for s in secs:
        name = b[stro + s[0]:b.index(b"\0", stro + s[0])].decode()
        if name == ".text":
            return b[s[4]:s[4] + s[5]]
    raise ValueError(f"{path}: no .text")


def texthash(path):
    return hashlib.sha256(elf_text(path)).hexdigest()


def lockcheck(kernel=None):
    """(ok, message). Validation needs: PREREG.md marked frozen, PREREG.sha256 equal to its hash, every file in
    LOCK.sha256 unchanged, and (with --kernel) the kernel's .text equal to kernel-text.sha256."""
    lock = os.path.join(HERE, "LOCK.sha256")
    pre = os.path.join(HERE, "PREREG.md")
    pre_sha = os.path.join(HERE, "PREREG.sha256")
    for f in (lock, pre, pre_sha):
        if not os.path.exists(f):
            return False, f"missing {os.path.relpath(f, ROOT)}: freeze with make_lock.sh after development"
    if "Status: FROZEN" not in open(pre).read():
        return False, "PREREG.md is not marked 'Status: FROZEN'"
    want = open(pre_sha).read().split()[0]
    pre_got = sha256_file(pre)
    if want != pre_got:
        return False, f"PREREG.md sha256 {pre_got[:12]} != PREREG.sha256 {want[:12]}"
    bad = []
    n = 0
    for line in open(lock):
        line = line.strip()
        if not line:
            continue
        h, f = line.split(None, 1)
        f = f.lstrip("*")
        n += 1
        p = os.path.join(ROOT, f)
        if not os.path.exists(p) or sha256_file(p) != h:
            bad.append(f)
    if bad:
        return False, "LOCK.sha256: changed or missing: " + ", ".join(bad)
    if kernel:
        kt = os.path.join(HERE, "kernel-text.sha256")
        if not os.path.exists(kt):
            return False, "missing kernel-text.sha256"
        want = open(kt).read().split()[0]
        got = texthash(kernel)
        if want != got:
            return False, f"kernel .text {got[:12]} != kernel-text.sha256 {want[:12]}"
    return True, f"lock ok: {n} files, PREREG.md {pre_got[:12]}" + (f", kernel .text {got[:12]}" if kernel else "")


# ---------------------------------------------------------------- plans
def load_sets():
    return json.load(open(os.path.join(HERE, "sets.json")))


def check_sets():
    have = load_sets()
    want = json.loads(json.dumps(mm.export()))
    if have != want:
        return False, "sets.json differs from workloads/nocroute/meshmap.py export (run export-sets in development)"
    if have["checks_failed"]:
        return False, "sets.json design checks failed: " + "; ".join(have["checks_failed"])
    return True, f"sets ok: {len(have['sets'])} sets, {len(have['flows'])} flows"


def write_calls(path, entries, meta):
    with open(path, "wb") as f:
        f.write(struct.pack(f"<{len(entries)}Q", *entries))
    json.dump(meta, open(path[:-4] + ".json", "w"))


def pad8(ents, rep_of):
    """Pad a call list with NOP entries (rep -1: never counted) to a multiple of 8, so that each caller's results fill
    whole 64 B lines of the output (L1 is not coherent: two shires writing one line lose each other's entries)."""
    while len(ents) % 8:
        ents.append(enc(NOP, 0))
        rep_of.append(-1)
    return ents, rep_of


def mesh_list(rng, reps, warm, sc_targets, ms_targets, with_pmc3=True):
    ents, rep_of = [], []
    for r in range(warm + reps):
        bank = r % 4
        e = [enc(SC, t, bank, 0) for t in sc_targets]
        if with_pmc3:
            e += [enc(SC, t, bank, 3) for t in sc_targets]
        e += [enc(MS, m, 0) for m in ms_targets]
        e += [enc(SC, SELF, 0, 7), enc(MS, 0, 7), enc(NOP, 0)]
        rng.shuffle(e)
        ents += e
        rep_of += [r] * len(e)
    return pad8(ents, rep_of)


def master_list(rng, reps, warm):
    ents, rep_of = [], []
    for r in range(warm + reps):
        bank = r % 4
        e = [enc(SC, 32, bank, 0), enc(SC, SELF, bank, 0), enc(SC, SELF, 0, 7)]
        rng.shuffle(e)
        ents += e
        rep_of += [r] * len(e)
    return pad8(ents, rep_of)


def r32_launches(sets, labels=None):
    """Every launch of one repeat: 'solo:<pair>' for every flow, 'set:<name>' for every set."""
    out = [(f"solo:{f['pair']}", f["pair"]) for f in sets["flows"]]
    out += [(f"set:{s['name']}", s["pairs"]) for s in sets["sets"]]
    if labels is not None:
        out = [x for x in out if x[0] in labels]
    return out


def make_plan(p, out):
    """Write every file pass p needs under out/ and return the process list [(name, plan, jsonl, outdir)]."""
    kind = pass_kind(p)
    P = PARAMS
    r31, r32, sm = P["r31"], P["r32"], P["smoke"]
    os.makedirs(os.path.join(out, "r31"), exist_ok=True)
    os.makedirs(os.path.join(out, "r32"), exist_ok=True)
    sets = load_sets()
    procs = []
    smoke = kind == "smoke"
    # R31: the mesh launches (compute shires, memory shires, null calls) in one process
    lines = []
    n_mesh = 1 if smoke else r31["mesh_launches"]
    for L in range(n_mesh):
        rng = random.Random(100000 * p + 100 * L + 31)
        if smoke:
            ents, rep = mesh_list(rng, sm["reps"], 1, sm["targets_sc"], sm["targets_ms"])
            callers = sm["callers"]
        else:
            ents, rep = mesh_list(rng, r31["mesh_reps"], r31["mesh_warm_reps"], list(range(32)), list(range(8)))
            callers = r31["callers"]
        warm = 1 if smoke else r31["mesh_warm_reps"]
        name = f"mesh-{L + 1}"
        path = os.path.join(out, "r31", name + ".bin")
        write_calls(path, ents, {"name": name, "rep": rep, "warm_reps": warm, "callers": callers})
        lines.append(f"mesh {name} {path} {callers} {r31['mesh_slot_cycles']} {r31['mesh_lead_cycles']} "
                     f"{r31['gap_cycles']}")
    open(os.path.join(out, "r31", "mesh.plan"), "w").write("\n".join(lines) + "\n")
    procs.append(("r31-mesh", os.path.join(out, "r31", "mesh.plan"), os.path.join(out, "r31", "mesh.jsonl"),
                  os.path.join(out, "r31")))
    # R32: reads and writes, each repeat its own process and its own shuffled order
    win = sm["window_cycles"] if smoke else r32["window_cycles"]
    sb = r32["slice_bytes"]
    reps = 1 if smoke else max(r32["read_repeats"], r32["write_repeats"])
    for r in range(reps):
        for mode in ("read", "write"):
            if not smoke and r >= r32[f"{mode}_repeats"]:
                continue
            labels = sm[f"{mode}_labels"] if smoke else None
            ls = r32_launches(sets, labels)
            random.Random(100000 * p + 1000 * r + (7 if mode == "read" else 11)).shuffle(ls)
            body = [f"fill {sb}"] if mode == "read" else []
            body += [f"{mode} {lab} {win} {sb} {pairs}" for lab, pairs in ls]
            name = f"r32-{mode}-{r + 1}"
            path = os.path.join(out, "r32", name + ".plan")
            open(path, "w").write("\n".join(body) + "\n")
            procs.append((name, path, os.path.join(out, "r32", name + ".jsonl"), os.path.join(out, "r32")))
    # R31: shire 32 last, in a process of its own
    rng = random.Random(100000 * p + 32)
    if smoke:
        ents, rep = master_list(rng, sm["master_reps"], 1)
        callers, warm = sm["master_callers"], 1
    else:
        ents, rep = master_list(rng, r31["master_reps"], r31["master_warm_reps"])
        callers, warm = r31["callers"], r31["master_warm_reps"]
    path = os.path.join(out, "r31", "master-1.bin")
    write_calls(path, ents, {"name": "master-1", "rep": rep, "warm_reps": warm, "callers": callers})
    open(os.path.join(out, "r31", "master.plan"), "w").write(
        f"mesh master-1 {path} {callers} {r31['master_slot_cycles']} {r31['master_lead_cycles']} {r31['gap_cycles']}\n")
    procs.append(("r31-master", os.path.join(out, "r31", "master.plan"), os.path.join(out, "r31", "master.jsonl"),
                  os.path.join(out, "r31")))
    with open(os.path.join(out, "procs.txt"), "w") as f:
        for pr in procs:
            f.write(" ".join(pr) + "\n")
    json.dump({"pass": p, "kind": kind, "procs": [pr[0] for pr in procs], "params": P,
               "sets_sha256": sha256_file(os.path.join(HERE, "sets.json"))},
              open(os.path.join(out, "plan.json"), "w"), indent=1)
    return procs


# ---------------------------------------------------------------- telemetry line
def tel(stdin):
    last = None
    for line in stdin:
        line = line.strip()
        if line.startswith("{"):
            try:
                last = json.loads(line)
            except ValueError:
                pass
    if not last:
        return ""
    try:
        return f"{int(last['temp_c']['minshire'][0])} {int(last['mhz']['minion'])}"
    except (KeyError, TypeError, ValueError, IndexError):
        return ""


# ---------------------------------------------------------------- the dry-run stub
# A planted model: reply order, request order, link capacity (GB/s), request cost c (a read's line request, or a
# write's acknowledgement, as a fraction of the data it stands for), networks (split: requests and replies on
# separate links; shared: one), write demand as a fraction of the read's, master cell, memory-shire cells, ESR stores
# (acked: a round trip each; posted: 20 cycles, no hop term), the firmware's ESR accesses (compiled: what objdump of
# MachineMinion.elf shows; source: pmu.c read as if its pointers were volatile), a hub every ESR call passes through,
# and the fraction of ESR calls the master's 1 ms stats worker delays (by 100 to statw_max cycles).
BASE = dict(reply="xy", request="xy", cap=102.4, c=0.25, net="split", wscale=0.8, master=mm.FW_MASTER, ms=mm.FW_MS,
            stores="acked", fw="compiled", hub=None, statw=0.15, statw_max=200, cap_req=None)
THEORIES = {
    "xy": dict(BASE),
    "yx": dict(BASE, reply="yx", request="yx"),
    "retrace": dict(BASE, reply="yx", request="xy", stores="posted"),
    "wide": dict(BASE, cap=1e4),
    "c51": dict(BASE, cap=51.2),
    "adapt": dict(BASE, reply="adapt", request="adapt"),
    "master-bottom": dict(BASE, master=(5, 3)),
    "ms-swap12": dict(BASE, ms={**mm.FW_MS, 1: (3, -1), 2: (2, -1)}),
    "hub": dict(BASE, hub=(0, 4)),
    # the review's cases: requests as costly as replies, or nearly; one shared network; the source's access counts;
    # posted stores; writes too weak to fill a link
    "xy-c1": dict(BASE, c=1.0),
    "yx-c1": dict(BASE, reply="yx", request="yx", c=1.0),
    "xy-c075": dict(BASE, c=0.75),
    "xy-shared": dict(BASE, c=0.5, net="shared"),
    "source-fw": dict(BASE, fw="source"),
    "posted": dict(BASE, stores="posted"),
    "weak-writes": dict(BASE, wscale=0.15),
    # a request network narrower than the reply network, and remote stores at half the reads' bandwidth: the writes
    # fill it although their demand is under 1.2 x the read-derived capacity
    "narrow-req": dict(BASE, cap_req=60.0, wscale=0.5),
    "quiet": dict(BASE, statw=0.0, c=0.0),
    "statw-heavy": dict(BASE, statw=0.25, statw_max=600),
}

# What reduce.py must answer for each planted model (verdict prefixes, keyed by the theory's P number).
_R31_FW = {"P1": "survived", "P2": "survived", "P3": "acked", "P4": "survived", "P5": "survived", "P6": "survived",
           "P6b": "survived", "P7": "survived"}
_XY = {"P8": "survived", "P9": "refuted", "P10": "refuted", "P11": "refuted", "P12": "survived"}
_YX = {"P8": "refuted", "P9": "survived", "P10": "refuted", "P11": "refuted", "P12": "survived"}
EXPECT = {
    "xy": {**_R31_FW, **_XY, "reads": "xy", "writes": "xy", "P13": "not decided"},
    "yx": {**_R31_FW, **_YX, "reads": "yx", "writes": "yx"},
    "retrace": {**_R31_FW, "P3": "posted", **_YX, "P12": "refuted", "reads": "yx", "writes": "xy"},
    "wide": {**_R31_FW, "P8": "not decided", "P9": "not decided", "P10": "survived", "P11": "not tested",
             "P12": "not decided", "reads": "wide", "writes": "not decided"},
    "c51": {**_R31_FW, **_XY, "reads": "xy", "writes": "xy"},
    "adapt": {**_R31_FW, "P8": "not decided", "P9": "not decided", "P10": "refuted", "P11": "not decided",
              "P12": "not decided", "reads": "not identified"},
    "master-bottom": {**_R31_FW, "P5": "refuted", **_XY},
    "ms-swap12": {**_R31_FW, "P6": "refuted", "P6b": "refuted", **_XY},
    "hub": {"P1": "refuted", "P2": "not decided", "P3": "not decided", "P5": "not decided", "P6": "not decided",
            "P7": "not decided", **_XY},
    "xy-c1": {**_R31_FW, "P8": "not decided", "P9": "not decided", "P10": "refuted", "P11": "not decided",
              "P12": "not decided", "reads": "not identified", "writes": "not identified"},
    "yx-c1": {**_R31_FW, "P8": "not decided", "P9": "not decided", "P11": "not decided", "reads": "not identified"},
    "xy-c075": {**_R31_FW, **_XY, "reads": "xy", "writes": "xy", "P13": "survived"},
    "xy-shared": {**_R31_FW, **_XY, "reads": "xy", "writes": "xy"},
    "source-fw": {**_R31_FW, "P2": "not decided", "P3": "not decided", **_XY},
    "posted": {**_R31_FW, "P3": "posted", **_XY},
    "weak-writes": {**_R31_FW, **_XY, "P12": "not decided", "reads": "xy", "writes": "not decided"},
    "narrow-req": {**_R31_FW, **_XY, "reads": "xy", "writes": "xy"},
    "quiet": {**_R31_FW, **_XY, "reads": "xy", "writes": "xy", "P13": "not decided"},
    "statw-heavy": {**_R31_FW, **_XY, "reads": "xy", "writes": "xy"},
}


def fake_dt(th, rng, caller, kind, ident, a, b):
    """Cycles of one call under theory th: null 420; each ESR load a round trip of 60 + 12/hop (DDRC 90 + 12/hop);
    each ESR store the same round trip if acknowledged, 20 if posted."""
    c = mm.MARTY[caller]
    if kind == NOP:
        return 10
    if (kind == SC and b == 7) or (kind == MS and a == 7):
        return 420 + round(rng.gauss(0, 1.0))
    if kind == SC:
        cell = th["master"] if ident == 32 else mm.MARTY[caller if ident == SELF else ident]
        base = 60
    else:
        cell = th["ms"][ident]
        base = 90
    h = mm.hops(c, cell) if th["hub"] is None else mm.hops(c, th["hub"]) + mm.hops(th["hub"], cell)
    rt = base + 12 * h
    st = rt if th["stores"] == "acked" else 20
    if th["fw"] == "compiled":      # objdump of sample_sc_pmcs / sample_ms_pmcs: pmc 0 = 2 ld + 2 sd, SC pmc 3 = 1 + 1
        loads, stores = (1, 1) if (kind == SC and b == 3) else (2, 2)
    else:                           # pmu.c as if volatile: pmc 0 = 3 ld + 2 sd, SC pmc 3 = 2 + 2
        loads, stores = (2, 2) if (kind == SC and b == 3) else (3, 2)
    dt = 420 + loads * rt + stores * st + round(rng.gauss(0, 1.5))
    if rng.random() < 1 / 70:
        dt += rng.choice((-128, 128))
    if rng.random() < th["statw"]:  # the master's stats worker on the same ESRs, once a millisecond
        dt += rng.randint(100, th["statw_max"])
    return dt


def fake_rates(th, flows, mode):
    dem = [mm.bw_model(mm.hops(s, d)) * (th["wscale"] if mode == "write" else 1.0) for s, d in flows]
    if th["reply"] == "adapt":
        r1 = mm.rates(flows, dem, mode, "xy", "xy", th["cap"], th["c"], th["net"], th["cap_req"])
        r2 = mm.rates(flows, dem, mode, "yx", "yx", th["cap"], th["c"], th["net"], th["cap_req"])
        return [(x + y) / 2 for x, y in zip(r1, r2)]
    return mm.rates(flows, dem, mode, th["reply"], th["request"], th["cap"], th["c"], th["net"], th["cap_req"])


def jcompact(d):
    """JSON as nocroute_host prints it (no spaces): block.sh greps these lines ("ok":false, "timed_out":true)."""
    return json.dumps(d, separators=(",", ":"))


def fakehost(plan, outdir, theory, seed):
    th = THEORIES[theory]
    rng = random.Random(seed)
    now = int(time.time() * 1000)
    for raw in open(plan):
        line = raw.split("#")[0].split()
        if not line:
            continue
        op, f = line[0], line[1:]
        if op == "mesh":
            name, path, cm = f[0], f[1], int(f[2], 0)
            data = open(path, "rb").read()
            ents = struct.unpack(f"<{len(data) // 8}Q", data)
            n = len(ents)
            res = [BAD] * (32 * n * 2)
            per = []
            slot = 0
            for s in range(32):
                if not (cm >> s) & 1:
                    continue
                for i, e in enumerate(ents):
                    k, ident, a, b = dec(e)
                    if k == SC and ident == 33:
                        continue
                    dt = fake_dt(th, rng, s, k, ident, a, b)
                    null = (k == SC and b == 7) or (k == MS and a == 7)
                    res[(slot * n + i) * 2] = dt & 0xFFFFFFFF
                    res[(slot * n + i) * 2 + 1] = BAD if null else rng.randrange(1 << 31)
                per.append({"shire": s, "slot": slot, "t_begin": 3000000 + slot * int(f[3]), "cycles": n * 1500,
                            "refused": 0, "err": 0, "ok": True})
                slot += 1
            if n % 8:
                raise SystemExit(f"{path}: {n} calls, not a multiple of 8 (the host refuses it)")
            open(os.path.join(outdir, name + ".u32"), "wb").write(struct.pack(f"<{len(res)}I", *res))
            print("NOCR " + jcompact({"test": "mesh", "name": name, "calls_file": path, "n_calls": n,
                                        "callers": hex(cm), "slot": int(f[3]), "lead": int(f[4]), "gap": int(f[5]),
                                        "out": os.path.join(outdir, name + ".u32"), "t_start_ms": now,
                                        "t_end_ms": now + 300, "wall_s": 0.3, "per_caller": per, "timed_out": False,
                                        "ok": True}))
        elif op == "fill":
            print("NOCR " + jcompact({"test": "fill", "slice_bytes": int(f[0]), "minions": 1024,
                                        "t_start_ms": now, "t_end_ms": now + 1, "wall_s": 0.001, "timed_out": False,
                                        "ok": True}))
        else:
            label, win, sb, pairs = f[0], int(f[1]), int(f[2]), f[3]
            prs = [tuple(int(x) for x in q.split(">")) for q in pairs.split(",")]
            flows = [(mm.MARTY[s], mm.MARTY[d]) for s, d in prs]
            rates = fake_rates(th, flows, op)
            fl = []
            for (s, d), r in zip(prs, rates):
                bpc = r / 0.6 * (1 + rng.gauss(0, 0.003))
                fl.append({"src": s, "dst": d, "minions": 32, "errs": 0, "bytes": int(bpc * win), "cyc_mean": win,
                           "bpc": round(bpc, 5)})
            print("NOCR " + jcompact({"test": op, "label": label, "window": win, "slice_bytes": sb, "pairs": pairs,
                                        "mask": "0x0", "t_start_ms": now, "t_end_ms": now + 50, "wall_s": 0.05,
                                        "flows": fl, "timed_out": False, "ok": True}))
        now += 60
    return 0


# ---------------------------------------------------------------- the discrimination test
def selftest(root, only=None, passes=(1, 2)):
    """For every planted model: plan the passes, run fakehost for each process, reduce, and compare every registered
    verdict with the planted answer (EXPECT). Returns the number of mismatches. No device, no block.sh."""
    import contextlib
    import io
    import shutil
    sys.path.insert(0, HERE)
    import reduce as rd
    sets = load_sets()
    bad = 0
    for name in (only or sorted(THEORIES)):
        d = os.path.join(root, name)
        shutil.rmtree(d, ignore_errors=True)
        for p in passes:
            out = os.path.join(d, f"p{p}")
            os.makedirs(out)
            with open(os.path.join(out, "marks.jsonl"), "w") as mk:
                for i, (pn, plan, jl, od) in enumerate(make_plan(p, out)):
                    with open(jl, "w") as f, contextlib.redirect_stdout(f):
                        fakehost(plan, od, name, 1000 * p + i)
                    mk.write(json.dumps({"ev": "proc", "name": pn, "rc": 0, "mhz": 600}) + "\n")
            json.dump({"status": "ok"}, open(os.path.join(out, "block.json"), "w"))
        V = rd.reduce_dir(d, [(p, os.path.join(d, f"p{p}")) for p in passes], sets)["theories"]
        got = {k.split(" ", 1)[0]: v for k, v in V.items()}
        miss = [f"{k}: want {w!r}, got {got.get(k)!r}" for k, w in EXPECT[name].items()
                if not str(got.get(k, "")).startswith(w)]
        bad += len(miss)
        print(f"{name:14s} {'ok' if not miss else 'MISMATCH'}  reads {got.get('reads')!r:34s} writes "
              f"{got.get('writes')!r}" + "".join("\n      " + m for m in miss))
    return bad


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("check-card")
    a.add_argument("--pass", dest="p", type=int, required=True)
    a.add_argument("--card", required=True)
    a.add_argument("--dry", action="store_true")
    a = sub.add_parser("plan")
    a.add_argument("--pass", dest="p", type=int, required=True)
    a.add_argument("--out", required=True)
    a = sub.add_parser("lockcheck")
    a.add_argument("--kernel")
    sub.add_parser("check-sets")
    sub.add_parser("export-sets")
    sub.add_parser("tel")
    a = sub.add_parser("texthash")
    a.add_argument("elf")
    a = sub.add_parser("fakehost")
    a.add_argument("--plan", required=True)
    a.add_argument("--out-dir", required=True)
    a.add_argument("--theory", default="xy", choices=sorted(THEORIES))
    a.add_argument("--seed", type=int, default=1)
    a = sub.add_parser("selftest")
    a.add_argument("--dir", default=os.path.join(ROOT, "build", "claims-v3-dry", "nocr-selftest"))
    a.add_argument("--theory", action="append", choices=sorted(THEORIES))
    g = ap.parse_args()
    if g.cmd == "check-card":
        ok, why = check_card(g.p, g.card, g.dry)
        print(why)
        return 0 if ok else 2
    if g.cmd == "plan":
        for pr in make_plan(g.p, g.out):
            print(" ".join(pr))
        return 0
    if g.cmd == "lockcheck":
        ok, why = lockcheck(g.kernel)
        print(why)
        return 0 if ok else 1
    if g.cmd == "check-sets":
        ok, why = check_sets()
        print(why)
        return 0 if ok else 1
    if g.cmd == "export-sets":
        json.dump(mm.export(), open(os.path.join(HERE, "sets.json"), "w"), indent=1)
        print("wrote sets.json")
        return 0
    if g.cmd == "tel":
        print(tel(sys.stdin))
        return 0
    if g.cmd == "texthash":
        print(texthash(g.elf))
        return 0
    if g.cmd == "fakehost":
        if not os.environ.get("V3_DRY"):
            print("fakehost runs only under V3_DRY=1", file=sys.stderr)
            return 2
        return fakehost(g.plan, g.out_dir, g.theory, g.seed)
    if g.cmd == "selftest":
        n = selftest(g.dir, g.theory)
        print(f"selftest: {len(g.theory or THEORIES)} planted models, {n} mismatches")
        return 0 if n == 0 else 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
