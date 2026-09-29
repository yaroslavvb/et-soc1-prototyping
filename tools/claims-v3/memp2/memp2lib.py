#!/usr/bin/env python3
"""memp2 helpers (tools/claims-v3/memp2/README.md). Off-card only: nothing here opens a device.

    memp2lib.py plan --pass N --card C          prints KEY=value lines (kind, role, seed, needlock) or exits 2 with the reason
    memp2lib.py tloop-configs --pass N [--smoke] [--stage S] [--args]   R43's configurations (the smoke's ladder), one
                                                JSON per line in the pass's order (--args: name TAB memprobe_host args)
    memp2lib.py binhash name=path ...           JSON: sha256 of each file and of its .text section
    memp2lib.py teldie FILE                     the last telemetry line's minshire mean (empty if none)
    memp2lib.py watch --tel F --stop-c C --pid P --flag F [--log L --hang-flag H]   SIGTERM P and write F when the
                                                mean reaches C (or H when the runner's log L shows a hung launch)
    memp2lib.py dry-probe OUT [--world W]       V3_DRY: synthetic results for OUT/mp/*.json and OUT/tl/plan.jsonl
    memp2lib.py dry-energy DIR [--world W]      V3_DRY: synthetic runs.jsonl / telemetry.jsonl / marks.jsonl
    memp2lib.py preregcheck --lock-sha S        exit 0 if LOCK.sha256 has sha256 S and every entry in it verifies
    memp2lib.py freeze (--kernel ELF | --kernel-text-sha H | --binaries binaries.json)
                                                writes prereg/PREREG.sha256 and LOCK.sha256 (once: refuses if a lock
                                                exists) and prints sha256(LOCK.sha256), the value validation needs
    memp2lib.py smokegate --data D --kernel K [--dry]   exit 0 if an ok smoke (p9xx) under D ran this kernel file

Worlds for the dry simulators (so the decision code is exercised every way): "predicted" (the PREREG predictions:
the L50 map, per-controller unsynchronised refresh, the L2 keeps TensorLoad lines, T43-B, T102); "alt" (PA[11] the
channel, PA[9], PA[10] and PA[12] the bank, and a second access on another channel of A's memory shire still costs
3 cycles; the L2 does not keep TensorLoad lines; T43-D; a flat stride-256 energy); "lockstep" (as predicted, but
every controller refreshes at the same phase); "alt2" (as predicted, but the two channels of a memory shire share
one refresh timer, and T43-Cc: a 128 B/cycle crossbar with 64 B/cycle banks, where minions that start in one
sub-bank convoy at 32 B/cycle).
"""
import argparse
import hashlib
import json
import math
import os
import random
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

# ---------------------------------------------------------------- passes and cards
DEV_CARD = "aifoundry1-c1"
VAL_CARDS = ("aifoundry3", "aifoundry2")


def plan(pas, card, env):
    """(info dict, None) or (None, reason)."""
    if card == "aifoundry1-c0":
        return None, "aifoundry1 card 0 is never used"
    if card not in (DEV_CARD,) + VAL_CARDS:
        return None, f"{card} is not a memp2 card"
    if card == "aifoundry2" and env.get("MEMP2_AFTER_DV2") != "1":
        return None, "aifoundry2 runs memp2 only after the DV2 validation ends (set MEMP2_AFTER_DV2=1 then)"
    hundreds, k = divmod(pas, 100)
    if hundreds == 9 and 1 <= k <= 99:
        kind, role = "SMOKE", "smoke"
    elif hundreds in (1, 2) and 1 <= k <= 9:
        kind, role = ("PROBE" if hundreds == 1 else "ENERGY"), "development"
    elif hundreds in (1, 2) and 11 <= k <= 19:
        kind, role = ("PROBE" if hundreds == 1 else "ENERGY"), "validation"
    else:
        return None, f"no pass {pas} (901-999 smoke; 101-109 / 201-209 development; 111-119 / 211-219 validation)"
    if role == "development" and card != DEV_CARD:
        return None, f"development passes run on {DEV_CARD} only (validation passes are 111-119 / 211-219)"
    if role == "validation" and card == DEV_CARD:
        return None, f"{DEV_CARD} is the development card: validation passes run on {', '.join(VAL_CARDS)}"
    # any pass on a validation card, its smoke included, needs the frozen lock: a smoke there before the freeze would
    # already be validation-card data (the discriminating configurations and treload among it)
    return {"kind": kind, "role": role, "seed": pas, "passes": 3 if kind == "ENERGY" else 0,
            "needlock": 1 if card in VAL_CARDS else 0}, None


# ---------------------------------------------------------------- R43: the TensorLoad stride sweep
# spread: where minion m's region starts. same: bank 0, sub-bank 0 for every minion; bank: (m mod 4) x 64 B (bank
# m mod 4); sub: also ((m / 4) mod 4) x 256 B; onebank: (m mod 4) x 256 B (bank 0 for every minion, sub-bank m mod 4:
# one bank without the lockstep of "same", the configurations that separate T43-B from a sub-bank convoy).
R43_ROWS = [(f"{tag}-n{n}", "scp", st, n, "same") for st, tag in ((64, "s64"), (256, "s256"), (1024, "s1k"))
            for n in (1, 2, 3, 4)] + \
           [("s256b-n1", "scp", 256, 1, "bank"), ("s256b-n4", "scp", 256, 4, "bank"),
            ("s1kb-n4", "scp", 1024, 4, "bank"), ("s1ks-n4", "scp", 1024, 4, "sub"),
            ("s256q-n4", "scp", 256, 4, "onebank"), ("s1kq-n4", "scp", 1024, 4, "onebank"),
            ("l2-s64-n4", "arena", 64, 4, "same"), ("l2-s256-n4", "arena", 256, 4, "same")]
# The smoke's ladder, run in this order and stopped at the first stage with any failure: (1) one minion of shire 0,
# every stride, spread and source, 200 loads; (2) the four op programs (one hart; treload's timed TensorLoads);
# (3) one whole shire; (4) the chip. (stage, name, where, stride, spread, shires, minions, iters, reps)
SMOKE_ROWS = [(1, "t1-s64", "scp", 64, "same", 0x1, 0x1, 200, 1), (1, "t1-s256", "scp", 256, "same", 0x1, 0x1, 200, 1),
              (1, "t1-s1ks", "scp", 1024, "sub", 0x1, 0x1, 200, 1),
              (1, "t1-s1kq", "scp", 1024, "onebank", 0x1, 0x1, 200, 1),
              (1, "t1-l2-s64", "arena", 64, "same", 0x1, 0x1, 200, 1),
              (1, "t1-l2-s256", "arena", 256, "same", 0x1, 0x1, 200, 1),
              (3, "sh-s64-n4", "scp", 64, "same", 0x1, 0xFFFFFFFF, 2000, 1),
              (3, "sh-s256-n4", "scp", 256, "same", 0x1, 0xFFFFFFFF, 2000, 1),
              (3, "sh-s1ks-n4", "scp", 1024, "sub", 0x1, 0xFFFFFFFF, 2000, 1),
              (3, "sh-s256q-n4", "scp", 256, "onebank", 0x1, 0xFFFFFFFF, 2000, 1),
              (3, "sh-l2-s64-n4", "arena", 64, "same", 0x1, 0xFFFFFFFF, 2000, 2),
              (4, "chip-s64-n4", "scp", 64, "same", 0xFFFFFFFF, 0xFFFFFFFF, 2000, 1),
              (4, "chip-s256-n4", "scp", 256, "same", 0xFFFFFFFF, 0xFFFFFFFF, 2000, 1),
              (4, "chip-s1kq-n4", "scp", 1024, "onebank", 0xFFFFFFFF, 0xFFFFFFFF, 2000, 1)]


def tloop_configs(pas, smoke=False, stage=None):
    """One dict per launch process. A development or validation pass: R43_ROWS on all 32 shires, 20,000 loads,
    3 launches (arena 4: the first a warm-up), in an order shuffled by the pass. The smoke: SMOKE_ROWS in order."""
    out = []
    if smoke:
        for stg, name, where, st, spread, shires, minions, iters, reps in SMOKE_ROWS:
            out.append({"name": name, "stage": stg, "where": where, "stride": st, "nbhd": bin(minions).count("1") / 8,
                        "minions": hex(minions), "shires": hex(shires), "spread": spread,
                        "span": 32768 if where == "scp" else 8192, "iters": iters, "reps": reps})
    else:
        for name, where, st, n, spread in R43_ROWS:
            out.append({"name": name, "stage": 0, "where": where, "stride": st, "nbhd": n,
                        "minions": hex((1 << (8 * n)) - 1), "shires": "0xffffffff", "spread": spread,
                        "span": 32768 if where == "scp" else 8192, "iters": 20000, "reps": 4 if where == "arena" else 3})
        random.Random(1000 + pas).shuffle(out)
    if stage is not None:
        out = [c for c in out if c["stage"] == stage]
    return out


def tloop_args(c):
    return ["--tloop", "--where", c["where"], "--stride", str(c["stride"]), "--tl-lines", "16",
            "--span", str(c["span"]), "--minions", c["minions"], "--shires", c["shires"], "--spread", c["spread"],
            "--iters", str(c["iters"]), "--reps", str(c["reps"]), "--name", c["name"]] + \
           (["--arena", "16M"] if c["where"] == "arena" else [])


# ---------------------------------------------------------------- binaries
def text_sha(path):
    for tool in ("/opt/et/bin/riscv64-unknown-elf-objcopy", "objcopy"):
        try:
            r = subprocess.run([tool, "-O", "binary", "--only-section=.text", path, "/dev/stdout"],
                               capture_output=True, timeout=30)
            if r.returncode == 0 and r.stdout:
                return hashlib.sha256(r.stdout).hexdigest()
        except (OSError, subprocess.SubprocessError):
            pass
    return None


def binhash(pairs):
    out = {}
    for p in pairs:
        k, _, path = p.partition("=")
        try:
            h = hashlib.sha256(open(path, "rb").read()).hexdigest()
        except OSError:
            out[k] = {"path": path, "missing": True}
            continue
        out[k] = {"path": path, "sha256": h, "text_sha256": text_sha(path), "mtime": int(os.path.getmtime(path))}
    return out


# ---------------------------------------------------------------- telemetry and the thermal stop
def last_mean(path):
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - 6000))
            lines = f.read().decode(errors="ignore").splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        if line.startswith("{"):
            try:
                return float(json.loads(line)["temp_c"]["minshire"][0])
            except (ValueError, KeyError, IndexError, TypeError):
                continue
    return None


# A launch that did not finish: the host's own 6 s timeout ("kernel did not finish", then an aborted stream), the
# 10 s cap (rc 124, or 137 after a SIGKILL), a stream error, or the Master Minion's queue refusing work (HPSQ). After
# one of these nothing more is launched on the card (28 Sep: the launches after such a hang all failed, and only a
# card reset cleared it).
HANG_RE = r"did not finish|HPSQ|[Ss]tream error|launch failed|\brc=(124|137)\b"


def hang_in(text):
    import re
    m = re.search(HANG_RE, text or "")
    return m.group(0) if m else None


def watch(tel, stop_c, pid, flag, every=0.5, log=None, hang_flag=None):
    """While pid lives: when the live telemetry's minshire mean reaches stop_c, write flag and SIGTERM pid; when the
    runner's log shows a hung launch, write hang_flag and SIGTERM pid."""
    while True:
        try:
            os.kill(pid, 0)
        except OSError:
            return 0
        t = last_mean(tel)
        why = None
        if t is not None and t >= stop_c:
            why, fn, rec = "thermal", flag, {"mean_c": t, "stop_c": stop_c}
        elif log and hang_flag:
            try:
                h = hang_in(open(log, errors="ignore").read())
            except OSError:
                h = None
            if h:
                why, fn, rec = "hang", hang_flag, {"match": h}
        if why:
            with open(fn, "w") as f:
                json.dump(dict(t_ms=int(time.time() * 1000), why=why, **rec), f)
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError:
                pass
            return 1
        time.sleep(every)


# ---------------------------------------------------------------- the dry simulators
P_REF = 2325.4


def _line_base(x, rng_seed=0):
    h = int(hashlib.md5(f"{x}:{rng_seed}".encode()).hexdigest()[:8], 16)
    return 272 + (h % 60)                 # 272-331: DRAM latency with the line's mesh legs (raw cycles)


def _dram_map(x, world):
    if world == "alt":                    # PA[11] the channel; PA[9], PA[10], PA[12] the bank
        return ((x >> 6) & 7, (x >> 11) & 1, ((x >> 9) & 3) | (((x >> 12) & 1) << 2), x >> 18)
    return ((x >> 6) & 7, (x >> 9) & 1, (x >> 10) & 7, x >> 18)   # the L50 map: ms, channel, bank, row


def _rel(a, b, world):
    ma, mb = _dram_map(a, world), _dram_map(b, world)
    if ma[:2] != mb[:2]:
        return "ctrl"                     # another controller
    if ma[2] != mb[2]:
        return "bank"
    return "row" if ma[3] != mb[3] else "same"


def dry_probe(out, world, seed=5):
    rng = random.Random(seed)
    mp = os.path.join(out, "mp")
    for fn in sorted(os.listdir(mp)) if os.path.isdir(mp) else []:
        if not fn.endswith(".json") or fn.endswith(".results.json"):
            continue
        prog = json.load(open(os.path.join(mp, fn)))
        name, meta, labels = prog["name"], prog["meta"], prog["labels"]
        vals = [_sim_label(lab, meta, world, rng) for lab in labels]
        if name.startswith("refphase"):
            _sim_refphase_fix(labels, vals, meta, world, rng)
        with open(os.path.join(mp, name + ".u32"), "wb") as f:
            for v in vals:
                f.write(int(max(0, min(v, 2 ** 32 - 1))).to_bytes(4, "little"))
        print(f"MEMPROBE {json.dumps({'test': 'program', 'name': name, 'results': len(vals), 'dry': True, 'ok': True})}")
    tl = os.path.join(out, "tl")
    planf = os.path.join(tl, "plan.jsonl")
    if os.path.exists(planf):
        for line in open(planf):
            c = json.loads(line)
            nsh = bin(int(c["shires"], 16)).count("1")
            nmin = bin(int(c["minions"], 16)).count("1")
            with open(os.path.join(tl, c["name"] + ".out"), "w") as f:
                for launch in range(c["reps"]):
                    v = _sim_tloop(c, world)
                    arr = [round(v * (1 + rng.gauss(0, 0.01)), 3) for _ in range(nsh)]
                    cpl = [round(1024.0 * nmin / max(a, 1e-9), 2) for a in arr]
                    f.write("MEMPROBE " + json.dumps({"test": "tloop", "name": c["name"], "where": c["where"],
                            "stride": c["stride"], "tl_lines": 16, "span": c["span"], "spread": c["spread"],
                            "minion_mask": c["minions"], "shire_mask": c["shires"], "minions": nsh * nmin,
                            "iters": c["iters"], "launch": launch, "tensor_errors": 0, "tensor_error_stale": 0,
                            "launch_ok": True, "bytes_per_shire_cycle": arr, "cycles_per_load": cpl, "dry": True,
                            "ok": True}) + "\n")


def _rowalt_mask(cond):
    if cond == "col":
        return 1 << 17
    if cond == "row":
        return 1 << 18
    if cond == "row19":
        return 1 << 19
    if cond.startswith("rowc+"):
        k = int(cond[5:])
        return (1 << (k + 7)) | (1 << k)
    k = int(cond.split("+")[1])
    return (1 << 18) | (1 << k)


def _sim_label(lab, meta, world, rng):
    kind = lab[0]
    noise = rng.gauss(0, 1.5)
    stall = rng.uniform(0, 208) if rng.random() < 0.06 else 0
    if kind == "alt":
        _, cond, t, j, which = lab
        a = meta["bases"][t] + (j << 13)
        b = a ^ _rowalt_mask(cond)
        x = a if which == "A" else b
        rel = _rel(a, b, world)
        if j == 0 or rng.random() < 0.14:
            state = 0                       # the first access, or the first after a refresh: closed row
        else:
            state = 9 if rel == "row" else -12
        return _line_base(x) + state + noise + stall
    if kind in ("ab", "b", "a"):
        _, k, t = lab
        base = 300 + 12 * (int(hashlib.md5(f"{k}:{t}".encode()).hexdigest()[:6], 16) % 7 - 3)   # one pair's path
        a = 1 << 26
        rel = _rel(a, a ^ (1 << k), world)
        if kind != "ab":
            return base + 9 + noise
        # another controller of A's memory shire still costs the second access up to ~3 cycles (queueing behind the
        # other 64 B response, the 1-cycle issue offset): the registered alternative's worst case
        extra = {"ctrl": 3, "bank": 7, "row": 38, "same": 3}[rel]
        return base + 9 + extra + noise
    if kind in ("rp_t", "rp_lat"):
        return 0                            # filled by _sim_refphase_fix
    if kind in ("stamp",):
        return rng.randrange(2 ** 31)
    if kind == "tnop":
        return 10
    if kind in ("terr0", "terr", "terr_end"):
        return 0
    keep = world != "alt"
    table = {"tl1": (950, 40), "tl2": (190, 8) if keep else (430, 30), "ref_l2": (190, 8), "ref_l3": (430, 40),
             "probe_tl": (53, 2) if keep else (160, 25), "probe_l3tl": (53, 2) if keep else (160, 25),
             "tl1_1": (330, 10), "probe1": (53, 2) if keep else (160, 25), "sref_dram": (300, 10),
             "sref_l2": (53, 1), "sref_l3": (150, 25)}
    if kind in table:
        m, s = table[kind]
        return m + rng.gauss(0, s)
    return 0


def _sim_refphase_fix(labels, vals, meta, world, rng):
    """A clock-driven series: per controller one refresh every P_REF cycles for 210 cycles; a request that reaches its
    controller inside a refresh waits until its end. Controllers' phases are random ("predicted") or equal ("alt")."""
    pairs = meta["pairs"]
    t = rng.randrange(10 ** 6)
    stamp_of = {}
    for i, lab in enumerate(labels):
        kind, k, r, n, which = lab
        A, B = pairs[f"{k}/{r}"]
        x = A if which == "A" else B
        ms, ch = _dram_map(x, world)[:2]
        # controllers' schedules: well apart ("predicted", "alt"), all at one phase ("lockstep"), or one timer per
        # memory shire shared by its two channels ("alt2")
        if world == "lockstep":
            ph0 = 0.0
        elif world == "alt2":
            ph0 = ((ms * 14) % 16) * P_REF / 16
        else:
            ph0 = (((ms * 2 + ch) * 7) % 16) * P_REF / 16
        if kind == "rp_t":
            t += 5 + rng.randrange(meta["jitter"]) + 10
            vals[i] = int(t) & 0xFFFFFFFF
            stamp_of[(k, r, n)] = t
            continue
        base = _line_base(x)
        state = 9 if _rel(A, B, world) == "row" else -12
        fwd = (base - 100) / 2
        ph = (stamp_of[(k, r, n)] + fwd - ph0) % P_REF
        wait = (210 - ph) if ph < 210 else 0
        lat = base + state + wait + rng.gauss(0, 1.5)
        vals[i] = lat
        t = stamp_of[(k, r, n)] + lat + 25


def _banks_subs(st, spread):
    """Banks and sub-banks a configuration's minions use together (bank PA[7:6], sub-bank PA[9:8])."""
    if st == 64:
        return 4, 16
    if spread == "same":
        return 1, (4 if st == 256 else 1)
    if spread == "onebank":
        return 1, 4
    if spread == "bank":
        return 4, (16 if st == 256 else 4)
    return 4, 16                              # sub


def _sim_tloop(c, world):
    st, spread = c["stride"], c["spread"]
    nmin = bin(int(c["minions"], 16)).count("1")
    n = nmin / 8
    minion = 6.4 * nmin
    banks, subs = _banks_subs(st, spread)
    if world == "alt":                      # T43-D: 32 B/cycle per neighbourhood; banks 64, sub-banks 32 (spec)
        return min(minion, 32.0 * max(n, 1 / 8), 64.0 * banks, 32.0 * subs)
    if world == "alt2":                     # T43-Cc: C, plus a 32 B/cycle convoy where every minion starts in one sub-bank
        v = min(minion, 128.0, 64.0 * banks, 32.0 * subs)
        return min(v, 32.0) if (spread == "same" and st >= 256) else v
    return min(minion, 32.0 * banks, 32.0 * subs)       # T43-B


def dry_energy(d, world, seed=11):
    """Synthetic runs.jsonl, telemetry.jsonl and marks.jsonl for one runner pass directory (its configs.json)."""
    rng = random.Random(seed)
    cj = json.load(open(os.path.join(d, "configs.json")))
    cfgs = [c["cfg"] for c in cj["cfgs"]]
    order = list(cfgs)
    rng.shuffle(order)
    epj = {"scpline/stride64/random": 6.64, "scpline/stride128/random": 6.48, "scpline/stride256/random": 7.33,
           "scpline/stride64/zeros": 4.16, "scpline/stride128/zeros": 4.34, "scpline/stride256/zeros": 4.91}
    if world == "alt":
        epj.update({"scpline/stride256/random": 6.56, "scpline/stride256/zeros": 4.25})
    bw = {"64": 923e9, "128": 923e9, "256": 614e9}
    t = time.time() - 3600.0
    tel, runs, marks = [], [], []
    idle_w = 32.0

    def samples(t0, t1, w):
        k = t0
        while k < t1:
            tel.append({"t_ms": int(k * 1000), "took_ms": 22, "board_w": round(w + rng.gauss(0, 0.12), 3),
                        "sp": {"minion_w": [11.0, 10.5, 12.0], "sram_w": [2.0, 1.9, 2.2], "noc_w": [3.7, 3.6, 3.9]},
                        "temp_c": {"minshire": [70, 68, 72]}, "mhz": {"minion": 600}, "die_mv": {"minion": 518}})
            k += 0.1
    samples(t, t + 10, idle_w)
    t += 10
    for cfg in order:
        c = next(x for x in cj["cfgs"] if x["cfg"] == cfg)
        if c.get("prefill"):
            samples(t, t + 0.5, idle_w + 8)
            marks.append({"kind": "prefill", "cfg": cfg, "pass": 0, "t_start_ms": int(t * 1000), "t_end_ms": int((t + 0.5) * 1000)})
            t += 0.5
        samples(t, t + 4.5, idle_w)
        t += 4.5
        if cfg.startswith("spin"):
            p_over, by = 2.0, 0
        else:
            st = cfg.split("/")[1].replace("stride", "")
            p_over = epj[cfg] * 1e-12 * bw[st]
        t0 = t
        for launch in range(5):
            wall = 0.6
            ops = int(0.6e9 * wall * 1024)
            by = 0 if cfg.startswith("spin") else int(bw[cfg.split("/")[1].replace("stride", "")] * wall)
            runs.append({"host": cj["host"], "pass": 0, "cfg": cfg, "pattern": "spin" if cfg.startswith("spin") else "tload_pat",
                         "unit": "op" if cfg.startswith("spin") else "byte", "operands": cfg.split("/")[-1] if not cfg.startswith("spin") else "zeros",
                         "harts": 1, "scp": 0 if cfg.startswith("spin") else 1, "participants": 1024, "shires": 32,
                         "ops": ops, "bytes": by, "cycles_max": int(0.6e9 * wall), "wall_s": wall,
                         "ops_per_cycle_per_hart": 1.0, "t_start_ms": int(t * 1000), "t_end_ms": int((t + wall) * 1000)})
            samples(t, t + wall, idle_w + p_over)
            t += wall
        samples(t, t + 1.0, idle_w)
        t += 1.0
    samples(t, t + 8, idle_w)
    for fn, rows in (("telemetry.jsonl", tel), ("runs.jsonl", runs), ("marks.jsonl", marks)):
        with open(os.path.join(d, fn), "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")


# ---------------------------------------------------------------- the freeze
LOCKED = ["tools/claims-v3/memp2/block.sh", "tools/claims-v3/memp2/memp2lib.py", "tools/claims-v3/memp2/reduce.py",
          "tools/claims-v3/memp2/deploy.sh", "tools/claims-v3/memp2/series.sh", "tools/claims-v3/memp2/sysemu.sh",
          "tools/claims-v3/memp2/README.md", "tools/claims-v3/memp2/prereg/PREREG.md",
          "tools/claims-v3/memp2/schedule-aifoundry1-c1.txt", "tools/claims-v3/memp2/schedule-aifoundry3.txt",
          "workloads/memprobe/gen_ops.py", "workloads/memprobe/gen_ops2.py", "workloads/memprobe/memprobe_args.h",
          "workloads/memprobe/kernel/memprobe.c", "workloads/memprobe/kernel/crt.S",
          "workloads/memprobe/kernel/sections.ld", "workloads/memprobe/kernel/CMakeLists.txt",
          "workloads/memprobe/host/main.cpp", "workloads/memprobe/host/CMakeLists.txt",
          "workloads/memprobe/host/Constants.h.in",
          "workloads/memprobe/CMakeLists.txt", "tools/claims-v3/lib.sh", "tools/claims-v3/queue.sh",
          "tools/claims-v3/cat/run_catalogue_t10.py", "tools/claims-v3/cat/catlib.py",
          "workloads/enercat/run_catalogue.py", "workloads/enercat/analyze_catalogue.py"]
KERNEL_REL = "build/memprobe2/kernel/memprobe.elf"
TEXT_TAG = "@text:"          # a LOCK line "<sha>  @text:<elf>": that ELF's .text section must have this sha256
LOCK_PATH = os.path.join(HERE, "LOCK.sha256")


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _hex64(x):
    return isinstance(x, str) and len(x) == 64 and all(c in "0123456789abcdef" for c in x)


def freeze(kernel=None, kernel_text_sha=None, binaries=None):
    """Once, after development and before any validation pass. The kernel's .text sha256 (the three hosts' RISC-V
    toolchains give identical .text) is bound into the lock: from a local ELF, given, or from a development pass's
    binaries.json. Refuses if LOCK.sha256 exists (a re-freeze would silently replace what validation checks)."""
    if os.path.exists(LOCK_PATH):
        return None, (f"{os.path.relpath(LOCK_PATH, ROOT)} exists: memp2 is frozen already (its sha256 "
                      f"{sha_file(LOCK_PATH)}); a new freeze needs the old lock removed by hand, before any "
                      "validation data, with the reason in PREREG.md's development notes")
    if binaries:
        try:
            kernel_text_sha = json.load(open(binaries))["memprobe2_kernel"]["text_sha256"]
        except (OSError, ValueError, KeyError, TypeError):
            return None, f"{binaries}: no memprobe2_kernel.text_sha256"
    elif kernel:
        kernel_text_sha = text_sha(kernel)
        if kernel_text_sha is None:
            return None, f"cannot read the .text section of {kernel}"
    if not _hex64(kernel_text_sha):
        return None, "the kernel's .text sha256 is needed (--kernel ELF, --kernel-text-sha H or --binaries FILE)"
    missing = [p for p in LOCKED if not os.path.exists(os.path.join(ROOT, p))]
    if missing:
        return None, "missing: " + ", ".join(missing)
    pr = os.path.join(HERE, "prereg", "PREREG.md")
    s = sha_file(pr)
    open(os.path.join(HERE, "prereg", "PREREG.sha256"), "w").write(f"{s}  tools/claims-v3/memp2/prereg/PREREG.md\n")
    tmp = LOCK_PATH + ".tmp"
    with open(tmp, "w") as f:
        for p in LOCKED:
            f.write(f"{sha_file(os.path.join(ROOT, p))}  {p}\n")
        f.write(f"{kernel_text_sha}  {TEXT_TAG}{KERNEL_REL}\n")
    os.replace(tmp, LOCK_PATH)
    ls = sha_file(LOCK_PATH)
    return ls, (f"LOCK.sha256 over {len(LOCKED)} files and the kernel's .text ({kernel_text_sha[:16]}); PREREG.md "
                f"{s[:16]}. Validation needs MEMP2_LOCK_SHA256={ls}")


def preregcheck(lock_sha):
    """(ok, message): LOCK.sha256 exists, its own sha256 is lock_sha (the value the freeze printed), and every entry
    verifies on this host (files, and the built kernel's .text)."""
    if not os.path.exists(LOCK_PATH):
        return False, "no LOCK.sha256 (not frozen: run memp2lib.py freeze before any pass on a validation card)"
    if not _hex64(lock_sha):
        return False, "MEMP2_LOCK_SHA256 (the sha256 of LOCK.sha256 that the freeze printed) is not set"
    ls = sha_file(LOCK_PATH)
    if ls != lock_sha:
        return False, f"LOCK.sha256 has sha256 {ls[:16]}, not the frozen {lock_sha[:16]} (replaced after the freeze?)"
    bad, n = [], 0
    for line in open(LOCK_PATH):
        h, _, p = line.strip().partition("  ")
        if not p:
            continue
        n += 1
        if p.startswith(TEXT_TAG):
            path = p[len(TEXT_TAG):]
            got = text_sha(os.path.join(ROOT, path)) if os.path.exists(os.path.join(ROOT, path)) else None
            if got != h:
                bad.append(f"{path} .text ({(got or 'unreadable')[:16]}, frozen {h[:16]})")
            continue
        try:
            if sha_file(os.path.join(ROOT, p)) != h:
                bad.append(p)
        except OSError:
            bad.append(p + " (missing)")
    if bad:
        return False, "LOCK.sha256: changed since the freeze: " + ", ".join(bad)
    return True, f"LOCK.sha256 {ls[:16]} verified ({n} entries, the kernel's .text included)"


def smokegate(data, kernel, dry=False):
    """(ok, message): an ok smoke pass (p901-p999) under data (<DATA_ROOT>/memp2) whose binaries.json records this
    kernel file's sha256. Development and validation passes run only after the smoke has run the same kernel."""
    try:
        cur = sha_file(kernel)
    except OSError:
        cur = None
    seen = []
    for p in sorted(os.listdir(data)) if os.path.isdir(data) else []:
        if not (p.startswith("p9") and p[1:].isdigit()):
            continue
        d = os.path.join(data, p)
        try:
            st = json.load(open(os.path.join(d, "block.json"))).get("status")
        except (OSError, ValueError):
            st = None
        try:
            ks = json.load(open(os.path.join(d, "binaries.json"))).get("memprobe2_kernel", {}).get("sha256")
        except (OSError, ValueError):
            ks = None
        seen.append(f"{p} {st}")
        if st == "ok" and (ks == cur and (cur is not None or dry)):
            return True, f"smoke {p} ok with this kernel ({(cur or 'dry')[:16]})"
    return False, ("no ok smoke with this kernel (" + (", ".join(seen) or "no smoke") + "): run the smoke pass "
                   "(901 on the development card, 911 or 912 on a validation card) first")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    x = sub.add_parser("plan"); x.add_argument("--pass", dest="pas", type=int, required=True); x.add_argument("--card", required=True)
    x = sub.add_parser("tloop-configs"); x.add_argument("--pass", dest="pas", type=int, required=True); x.add_argument("--smoke", action="store_true")
    x.add_argument("--stage", type=int, default=None, help="the smoke's stage only (1, 3 or 4)")
    x.add_argument("--args", action="store_true", help="print each config's memprobe_host arguments instead")
    x = sub.add_parser("binhash"); x.add_argument("pairs", nargs="*")
    x = sub.add_parser("teldie"); x.add_argument("file")
    x = sub.add_parser("watch"); x.add_argument("--tel", required=True); x.add_argument("--stop-c", type=float, required=True)
    x.add_argument("--pid", type=int, required=True); x.add_argument("--flag", required=True)
    x.add_argument("--log", default=None); x.add_argument("--hang-flag", default=None)
    x = sub.add_parser("hang"); x.add_argument("files", nargs="*", help="print the hang signature found in any file")
    x = sub.add_parser("dry-probe"); x.add_argument("out"); x.add_argument("--world", default=os.environ.get("MEMP2_DRY_WORLD", "predicted"))
    x = sub.add_parser("dry-energy"); x.add_argument("dir"); x.add_argument("--world", default=os.environ.get("MEMP2_DRY_WORLD", "predicted"))
    x.add_argument("--seed", type=int, default=11)
    x = sub.add_parser("preregcheck"); x.add_argument("--lock-sha", default="")
    x = sub.add_parser("freeze"); g = x.add_mutually_exclusive_group(required=True)
    g.add_argument("--kernel"); g.add_argument("--kernel-text-sha"); g.add_argument("--binaries")
    x = sub.add_parser("smokegate"); x.add_argument("--data", required=True); x.add_argument("--kernel", required=True)
    x.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    if a.cmd == "plan":
        info, why = plan(a.pas, a.card, os.environ)
        if info is None:
            print(why)
            sys.exit(2)
        for k, v in info.items():
            print(f"{k.upper()}={v}")
    elif a.cmd == "tloop-configs":
        for c in tloop_configs(a.pas, a.smoke, a.stage):
            print(json.dumps(c) if not a.args else c["name"] + "\t" + " ".join(tloop_args(c)))
    elif a.cmd == "binhash":
        print(json.dumps(binhash(a.pairs), indent=1))
    elif a.cmd == "teldie":
        t = last_mean(a.file)
        print("" if t is None else int(t))
    elif a.cmd == "watch":
        sys.exit(watch(a.tel, a.stop_c, a.pid, a.flag, log=a.log, hang_flag=a.hang_flag))
    elif a.cmd == "hang":
        for fn in a.files:
            try:
                h = hang_in(open(fn, errors="ignore").read())
            except OSError:
                continue
            if h:
                print(f"{os.path.basename(fn)}: {h}")
                sys.exit(0)
        sys.exit(1)
    elif a.cmd == "dry-probe":
        sys.path.insert(0, os.path.join(ROOT, "workloads", "memprobe"))
        dry_probe(a.out, a.world)
    elif a.cmd == "dry-energy":
        dry_energy(a.dir, a.world, a.seed)
    elif a.cmd == "preregcheck":
        ok, why = preregcheck(a.lock_sha)
        print(why)
        sys.exit(0 if ok else 1)
    elif a.cmd == "freeze":
        ls, why = freeze(a.kernel, a.kernel_text_sha, a.binaries)
        print(why)
        sys.exit(0 if ls else 2)
    elif a.cmd == "smokegate":
        ok, why = smokegate(a.data, a.kernel, a.dry)
        print(why)
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
