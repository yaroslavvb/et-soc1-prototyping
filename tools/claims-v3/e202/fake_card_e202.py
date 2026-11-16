#!/usr/bin/env python3
"""E202's test doubles (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum): no device, no management node, no lock, no box.
run_e202.py --dry runs them (step 8's dry pass on the box, and the runner's desk test); desk/standin_e202.py puts the same behaviour
behind the real tools' paths for THE REAL-PATH DESK TEST, its knobs read from a case file instead of the environment.

    fake_card_e202.py config        `ettelem config` (knob CONFIG: ok | tdp5 | thr70 | mhz800 | fail | cut)
    fake_card_e202.py etwho         `et-who` (knob ETWHO: free | held | fail | text1 | garbled, each also as <mode>-from:N, from its
                                    N-th call on: fix-e202's forms of a read that failed, beside a holder of another login)
    fake_card_e202.py sample --seconds T --every-ms M
                                    `ettelem sample`: a card whose board power is its idle plus the dynamic power of the launches the
                                    host double announces in the schedule (E202_FAKE_SCHED), in real time; knob BASE alt|base puts
                                    energy_stub.py's simulated card (unchanged) under the same injections, so a case can trip a stop line
                                    AND reduce the burst; knob INJECT: a list of {"board_w"|"die"|"mhz": v, "from_s", "to_s", "during":
                                    "burst"|"smoke", "after_launches": N, "count": n}; knob SAMPLER: dead (no line, exit 1) | stubborn
                                    (ignores its first SIGTERM) | deaf:S (ignores every SIGTERM, exits S seconds after the first:
                                    fix-e202) | quiet-from:S (prints nothing from S seconds on, alive: the stale line) |
                                    old-from:S (from S seconds on, each line's t_ms is 1.5 s in the past) | split (a runtime line inside
                                    every 25th line: that line is lost, never misread)
    fake_card_e202.py host <the mnistmlp host's arguments>
                                    the mnistmlp host: parses its arguments as main.cpp does (an unknown option or a bad value: usage,
                                    exit 2), sleeps through set-up and ONE launch of R passes, announcing the launch in the schedule AT ITS
                                    START with its dynamic power, writes its JSON record to --out (main.cpp's fields and form) and repeats
                                    it on stdout; knob SPLIT: a runtime line printed INSIDE the stdout copy (the --out file stays whole);
                                    knob SMOKE {arm: core|logits|nojson|crash|hang|slow:F} and BURSTS {"config/bk": core|nojson|crash|hang}
                                    pick the outcomes; knob SCALE scales every duration (a fast desk case); FAILHANG: a launch that does
                                    not finish prints main.cpp's "kernel did not finish within 8 s, aborting the stream" (K1).
The launch times and watts are the frozen forecast's points (forecast-e202.json, R = 96 scaled by the busiest shire's rounds): nothing
here is a measurement. The process names stay python3, so no double is ever counted as a device process. SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
FC = os.path.join(HERE, "forecast-e202.json")
STUB = os.path.join(REPO, "workloads", "sparseparity", "tools", "energy_stub.py")
IDLE_W = 24.9
F_HZ = 600e6


def knobs_from_env():
    k = {}
    for name in ("CONFIG", "ETWHO", "SAMPLER", "BASE", "SPLIT", "SCALE", "SCHED"):
        v = os.environ.get("E202_FAKE_" + name)
        if v is not None:
            k[name] = v
    for name in ("INJECT", "SMOKE", "BURSTS"):
        v = os.environ.get("E202_FAKE_" + name)
        if v:
            k[name] = json.load(open(v)) if os.path.exists(v) else json.loads(v)
    return k


K = {}


def kn(name, default=None):
    return K.get(name, default)


def arg(argv, name, default=None):
    return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else default


def scale():
    return float(kn("SCALE", "1"))


def forecast():
    with open(FC) as f:
        return json.load(f)["configs"]


def sched_path():
    return kn("SCHED") or os.environ.get("E202_FAKE_SCHED", "")


def sched_add(t0, t1, dp, tag, name):
    p = sched_path()
    if p:
        with open(p, "a") as f:
            f.write(json.dumps({"t0": t0, "t1": t1, "dp": dp, "tag": tag, "name": name}) + "\n")


def read_sched():
    p = sched_path()
    out = []
    if p and os.path.exists(p):
        with open(p) as f:
            for ln in f:
                if ln.startswith("{"):
                    try:
                        out.append(json.loads(ln))
                    except ValueError:
                        pass
    return out


def config():
    mode = kn("CONFIG", "ok")
    if mode == "fail":
        print("ettelem: cannot open the management node", file=sys.stderr)
        return 1
    j = {"tdp_w": 0, "temp_threshold_c": 65, "power_state": 0, "power_state_name": "max_power", "minion_mhz": 600,
         "minion_mv": 523, "fake": True}
    if mode == "tdp5":
        j["tdp_w"] = 5
    elif mode == "thr70":
        j["temp_threshold_c"] = 70
    elif mode == "mhz800":
        j["minion_mhz"] = 800
    line = json.dumps(j, separators=(",", ":"))
    if mode == "cut":
        line = line[:20] + "Opening device 0\n" + line[20:]
    print(line)
    return 0


def etwho(counter_file=None):
    """`et-who` (knob ETWHO: <mode> or <mode>-from:N, the mode from its N-th call on, free before). Modes (fix-e202, verify-e202's
    finding 1, E191's forms): free; held (a holder of another login: rc 0, as the real et-who, whose privileged helper exits 0 whether or
    not the card is held); fail (its helper refused: rc 1, nothing on stdout); text1 (rc 1 with a line of text); garbled (rc 0, but
    neither a holder line nor the no-holder sentence)."""
    mode = kn("ETWHO", "free")
    n = 0
    if counter_file:
        try:
            n = int(open(counter_file).read().strip() or 0)
        except (OSError, ValueError):
            n = 0
        open(counter_file, "w").write(str(n + 1))
    base, _, frm = mode.partition("-from:")
    if frm and n + 1 < int(frm):
        base = "free"
    if base == "held":
        print("/dev/et0_mgmt someoneelse 4242 other_host")
        print("lock:etsoc-shire0.lock someoneelse 4242 other_host")
        return 0
    if base == "fail":
        print("et-who: its helper refused (double)", file=sys.stderr)
        return 1
    if base == "text1":
        print("et-who: its helper is missing (double)")
        return 1
    if base == "garbled":
        print("Segmentation fault (double)")
        return 0
    print("No process holds an ET-SoC-1 device node or card lock.")
    return 0


class Inject:
    """The cases' injections: each moves the SAMPLED POINT the stop lines read (board_w, the minion shires' temperatures, the minion
    clock); the SP's board average, which the reducer integrates, stays the card model's."""

    def __init__(self):
        self.inj = kn("INJECT") or []
        self.used = {}

    def apply(self, line, tick, el, sch):
        if not self.inj:
            return line
        live = [s for s in sch if s["t0"] <= tick < s["t1"]]
        nl = sum(1 for s in sch if s.get("tag") == "burst")
        for i, x in enumerate(self.inj):
            cond = x.get("from_s", 0) <= el < x.get("to_s", 1e9) and nl >= x.get("after_launches", 0)
            if cond and x.get("during"):
                cond = any(s.get("tag") == x["during"] for s in live)
            if cond and self.used.get(i, 0) >= x.get("count", 1 << 30):
                cond = False
            if cond:
                self.used[i] = self.used.get(i, 0) + 1
                if "board_w" in x:
                    line["board_w"] = x["board_w"]
                if "die" in x:
                    line.setdefault("temp_c", {})["minshire"] = [x["die"], x["die"] - 1, x["die"] + 1]
                if "mhz" in x:
                    line.setdefault("mhz", {})["minion"] = x["mhz"]
        return line


def emit(line, n, t0):
    """One sampler line out, as the knob SAMPLER says (quiet: nothing; old: t_ms 1.5 s back; split: a runtime line inside)."""
    mode = kn("SAMPLER", "")
    el = time.time() - t0
    if mode.startswith("quiet-from:") and el >= float(mode.split(":")[1]):
        return
    if mode.startswith("old-from:") and el >= float(mode.split(":")[1]):
        line["t_ms"] = int(line["t_ms"] - 1500)
    txt = json.dumps(line, separators=(",", ":"))
    if mode == "split" and n % 25 == 24:
        txt = txt[:40] + "\nOpening device 0\n" + txt[40:]
    print(txt, flush=True)


def sample_on_stub(card, seconds, every_ms, inj):
    child = subprocess.Popen([sys.executable, "-B", STUB, "sample", "--seconds", str(int(seconds)), "--every-ms", str(every_ms),
                              "--sched", sched_path(), "--card", card], stdout=subprocess.PIPE, stdin=subprocess.DEVNULL, text=True)
    terms = {"n": 0}

    def term(*_):
        terms["n"] += 1
        if kn("SAMPLER", "") == "stubborn" and terms["n"] < 2:
            return
        try:
            child.send_signal(signal.SIGTERM)
        except OSError:
            pass

    signal.signal(signal.SIGTERM, term)
    t0 = time.time()
    n = 0
    for raw in child.stdout:
        if not raw.startswith("{"):
            continue
        try:
            line = json.loads(raw)
        except ValueError:
            continue
        line = inj.apply(line, line.get("t_ms", 0) / 1000.0, time.time() - t0, read_sched())
        emit(line, n, t0)
        n += 1
    return child.wait()


def sample(argv):
    mode = kn("SAMPLER", "")
    if mode == "dead":
        print("fake sampler: cannot open the management node", file=sys.stderr)
        return 1
    seconds = float(arg(argv, "--seconds", 10))
    every_ms = int(arg(argv, "--every-ms", 100))
    inj = Inject()
    base = kn("BASE", "")
    if base in ("alt", "base"):
        return sample_on_stub(base, seconds, every_ms, inj)
    terms = {"n": 0, "first": None}

    def on_term(*_):
        terms["n"] += 1
        terms["first"] = terms["first"] or time.time()
    signal.signal(signal.SIGTERM, on_term)
    need = 2 if mode == "stubborn" else 1
    deaf = float(mode.split(":")[1]) if mode.startswith("deaf:") else None   # fix-e202 (finding 8): ignores every SIGTERM, prints
    #                                                                           nothing after the first, exits S seconds after it
    t0 = time.time()
    n = 0
    while time.time() - t0 < seconds:
        if deaf is not None and terms["first"] is not None:
            if time.time() - terms["first"] >= deaf:
                break
            time.sleep(0.1)
            continue
        if deaf is None and terms["n"] >= need:
            break
        tick = time.time()
        sch = read_sched()
        dp = sum(s["dp"] for s in sch if s["t0"] <= tick < s["t1"])
        bw, die = IDLE_W + dp, 50 + min(3, int(dp / 5))
        line = {"t_ms": int(tick * 1000), "took_ms": 22, "since_reset_ms": -1, "board_w": round(bw, 2),
                "sp": {"board_avg_w": round(bw, 2), "minion_w": [5.5 + 0.6 * dp] * 3, "sram_w": [3.1 + 0.1 * dp] * 3,
                       "noc_w": [2.4] * 3},
                "temp_c": {"minshire": [die, die - 1, die + 1]}, "mhz": {"minion": 600, "noc": 400}, "fake": True}
        emit(inj.apply(line, tick, tick - t0, sch), n, t0)
        n += 1
        time.sleep(max(0.0, tick + every_ms / 1000.0 - time.time()))
    return 0


# ---------------------------------------------------------------- the mnistmlp host double
OPTS_FLAG = {"--sysemu", "--card", "--dry", "--ref", "--selftest", "--debug-logits", "--no-pins"}
OPTS_VAL = {"--sim-args", "--sim-extra", "--images", "--weights", "--expect", "--expect-logits", "--true-labels", "--split",
            "--passes", "--groups", "--shires", "--per-shire", "--stage", "--epoch", "--out", "--labels-out", "--pins",
            "--max-kernel-s", "--budget", "--kernel", "--poll-limit", "--ref-groups", "--ref-out"}


def parse_host(argv):
    """main.cpp's parse(): an unknown option or a missing value is usage (exit 2); the same refusals."""
    o, i = {}, 0
    while i < len(argv):
        a = argv[i]
        if a in OPTS_FLAG:
            o[a] = True
            i += 1
        elif a in OPTS_VAL:
            if i + 1 >= len(argv):
                return None, a + " needs a value"
            o[a] = argv[i + 1]
            i += 2
        else:
            return None, "unknown option " + a
    if o.get("--selftest"):
        return o, ""
    if sum(1 for m in ("--sysemu", "--card", "--dry", "--ref") if o.get(m)) != 1:
        return None, "give exactly one of --sysemu, --card, --dry, --ref"
    if not (o.get("--images") and o.get("--weights") and o.get("--expect")):
        return None, "--images, --weights and --expect are required"
    if o.get("--split", "train") not in ("train", "test") or o.get("--stage", "scp") not in ("scp", "dram"):
        return None, "--split train|test / --stage scp|dram"
    if not 1 <= int(o.get("--passes", 1)) <= 1000:
        return None, "--passes 1-1000"
    if float(o.get("--budget", 9.5)) > 9.5:
        return None, "--budget at most 9.5 s"
    if o.get("--debug-logits") and not o.get("--expect-logits") and not o.get("--dry"):
        return None, "--debug-logits needs --expect-logits"
    return o, ""


def busiest(R, gpp):
    rounds = -(-gpp * R // 32)
    return rounds, -(-rounds // 32)


def outcome_for(o):
    stage = o.get("--stage", "scp")
    weights = "random" if "random" in os.path.basename(o.get("--weights", "")) else "trained"
    split = o.get("--split", "train")
    R = int(o.get("--passes", 1))
    out = o.get("--out", "")
    if R == 1:
        arm = "ACC" if split == "test" else ("T-" if weights == "trained" else "Z-") + stage
        return (kn("SMOKE") or {}).get(arm, "ok"), arm, weights, stage, split, R
    d = os.path.basename(os.path.dirname(out)) if out else ""
    key = f"{weights}-{stage}/{d}"
    return (kn("BURSTS") or {}).get(key, "ok"), key, weights, stage, split, R


def host(argv):
    o, why = parse_host(argv)
    if o is None:
        print(f"mnistmlp_host: {why}", file=sys.stderr)
        print("usage: mnistmlp_host (--sysemu ... | --card | --dry | --ref | --selftest) ...", file=sys.stderr)
        return 2
    if o.get("--selftest"):
        print("SELFTEST sha256(abc)                                  OK\nSELFTEST PASS")
        return 0
    mode, name, weights, stage, split, R = outcome_for(o)
    if mode == "crash":
        print("terminate called after throwing an instance of 'std::runtime_error' (fake)", file=sys.stderr)
        return 134
    f = forecast()[f"{weights}-{stage}"]
    gpp = 3750 if split == "train" else 625
    rounds, bz = busiest(R, gpp)
    slow = float(mode.split(":")[1]) if mode.startswith("slow:") else 1.0
    launch_s = f["seconds"]["launch_R96"]["point"] * bz / 352.0 * slow
    sc = scale()
    time.sleep(0.3 * sc)
    print("device ready in 0.31 s (fake)", file=sys.stderr)
    a = time.time()
    tag = "smoke" if R == 1 else "burst"
    hang = mode == "hang"
    dur = (8.0 if hang else (max(launch_s, 1.0) if R == 1 else launch_s)) * sc   # a smoke launch held 1 s (scaled) so a 10 Hz
    #                                                                                     sampler sees it; its record keeps launch_s
    sched_add(a, a + dur, f["w_over_idle"], tag, name)
    time.sleep(max(0.0, a + dur - time.time()))
    b = time.time()
    if hang:
        print("kernel did not finish within 8 s, aborting the stream (fake)", file=sys.stderr)
    print("device held for 1.2 s (fake)", file=sys.stderr)
    groups = gpp * R
    pad = rounds * 32 - groups
    cyc = int(round(launch_s * F_HZ))
    core = "FAIL" if mode in ("core", "hang") else "PASS"
    dbg = bool(o.get("--debug-logits"))
    logits = "NOT CHECKED" if not dbg else ("FAIL" if mode == "logits" else "PASS")
    st = "PASS" if core == "PASS" and logits != "FAIL" else "FAIL"
    j = {"mnistmlp": 1, "device": "card", "split": split, "stage": stage, "debug_logits": dbg, "inputs": [], "pins": "OK",
         "weights_name": f"{weights}-fake", "gpp": gpp, "groups": groups, "passes": R, "shire_mask": "0xffffffff", "nshires": 32,
         "per_shire": 32, "rounds": rounds, "input_groups_copied": min(groups, gpp), "resident_lines_max": 5760 if stage == "scp" else 0,
         "epoch": 1, "model_s": round(bz * (10892 * 700 + 449 * 1500) / F_HZ + 0.002, 6), "ops_per_group": 10892,
         "macs_issued_per_image": 11153408, "kernel_sha256": "fake", "device_scp_kb_per_shire": 2560,
         "launch_ok": not hang, "wall_s": round(b - a, 6), "launch_epoch_ms": [int(a * 1000), int(b * 1000)],
         "working_minions": 1024, "records_ok": 0 if hang else 1024, "records_bad": 0, "groups_done": 0 if hang else rounds * 32,
         "pad_groups": 0 if hang else pad, "ops": 0 if hang else (groups + pad) * 10892,
         "ops_expected": 0 if hang else (groups + pad) * 10892, "tensor_error_or": 0,
         "hart0_cycles": {"max": cyc, "min": cyc - 900, "mean": cyc - 450.0},
         "work_cycles": {"max": cyc - (89119 if stage == "scp" else 0), "mean": cyc - 90000.0},
         "wait_cycles": {"max": 21108, "mean": 18142.0}, "copy_cycles_max": 89119 if stage == "scp" else 0,
         "label_lines_bad": 0, "label_mismatches": 7 if core == "FAIL" else 0, "checksum_mismatches": 0,
         "discard_lines_ok": pad, "discard_lines_bad": 0, "logit_tiles_checked": groups if dbg else 0,
         "logit_tile_mismatches": 3 if logits == "FAIL" else 0, "first_mismatch": "label line 7 labels" if core == "FAIL" else
         ("logits of group 3" if logits == "FAIL" else ""), "core_status": core, "logits_status": logits, "status": st,
         "fake": True}
    if o.get("--true-labels"):
        j["accuracy"] = {"correct": 9849, "scored": 10000}
    line = json.dumps(j, separators=(",", ":"))
    if mode != "nojson" and o.get("--out"):
        with open(o["--out"], "w") as fo:
            fo.write(line + "\n")
    if o.get("--labels-out") and not hang:
        with open(o["--labels-out"], "wb") as fo:
            fo.write(b"\x00" * 64 * groups)
    out = line
    if kn("SPLIT"):
        out = line[:57] + "Opening device 0\n" + line[57:]
    print(out, flush=True)
    return 0 if st == "PASS" else 1


def main(argv, knobs=None, counter_file=None):
    global K
    K = knobs if knobs is not None else knobs_from_env()
    if not argv:
        print(__doc__)
        return 2
    w, rest = argv[0], argv[1:]
    if w == "config":
        return config()
    if w == "etwho":
        return etwho(counter_file or ((sched_path() + ".etwho") if sched_path() else None))
    if w == "sample":
        return sample(rest)
    if w == "host":
        return host(rest)
    print(f"fake_card_e202: unknown double {w}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
