#!/usr/bin/env python3
"""E189's test doubles (Q167, the kit, Thu 12 Nov 2026, before any E189 datum; fixed Fri 13 Nov 2026, fix-e189b): no device, no management
node, no lock, no box.

    fake_card_e189.py config          stands in for `ettelem config` (E189_FAKE_CONFIG=ok|tdp5|thr70|mhz800|fail)
    fake_card_e189.py etwho           stands in for `et-who` (E189_FAKE_ETWHO=free|held)
    fake_card_e189.py sample --seconds T --every-ms M
                                      stands in for `ettelem sample`: a card whose board power is its idle plus the dynamic power of
                                      the launches the host doubles announce in $E189_FAKE_SCHED, in real time. E189_FAKE_BASE=alt|base
                                      puts energy_stub.py's simulated card (its 'alt' or 'base' laws: the SP average's lag, the thermal
                                      chain, the late board reading) under the same injections instead, so a desk case can trip a stop
                                      line AND reduce the pass (selftest_run_e189.py's R2E and R3E). E189_FAKE_INJECT names a JSON file of
                                      injections the stop-path desk cases use to trip each line: each {"board_w" | "die" | "mhz": value}
                                      with its conditions, all optional: "from_s"/"to_s" (seconds from the sampler's start), "during":
                                      "pass" (while a pass's host double runs) | "smoke" (while a smoke launch runs), "after_pass_launches":
                                      N (once N pass launches have started), "for_s" (how long after its condition first held), "count" (at
                                      most that many samples). An injection moves the SAMPLED POINT the stop lines read (board_w, the
                                      minion shires' temperatures, the minion clock); the SP's board average, which the reducer
                                      integrates, stays the card model's, so a pass that tripped a line can still be checked for its
                                      joules. E189_FAKE_SAMPLER=dead prints nothing and exits 1; =stubborn ignores its first SIGTERM and
                                      stops on the second (the closing bound's desk case, R18).
    fake_card_e189.py host-ledger <the ledger host's arguments>
    fake_card_e189.py host-spp <sparse parity host's arguments>
                                      stand in for the two hosts: --selftest prints the FIPS lines; a card run sleeps through set-up and
                                      K launches under the host's own budget rule, ANNOUNCING each launch in $E189_FAKE_SCHED with its
                                      dynamic power AT ITS START (as energy_stub.py's own host double does: its sampler simulates the
                                      card 0.1 s behind real time, so a launch announced only at its end was injected for its last 0.1-0.2
                                      s alone, verify-e189's fault 1), then prints the host's JSON line. E189_FAKE_HOST=ok|fail|short|
                                      nojson|crash picks the outcome (short and fail-pass touch the queue's passes only, never the smoke's
                                      small runs); E189_FAKE_SCALE scales every duration (a fast desk case).
The launch times and watts are the frozen forecast's points (forecast-e189.json): nothing here is a measurement. The process names stay
python3, so no double is ever counted as a device process. SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
FC = os.path.join(HERE, "forecast-e189.json")
STUB = os.path.join(REPO, "workloads", "sparseparity", "tools", "energy_stub.py")
IDLE_W = 24.9


def arg(argv, name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default


def scale():
    return float(os.environ.get("E189_FAKE_SCALE", "1"))


def forecast():
    with open(FC) as f:
        return json.load(f)["configs"]


def sched_add(t0, t1, dp, tag):
    p = os.environ.get("E189_FAKE_SCHED")
    if p:
        with open(p, "a") as f:
            f.write(json.dumps({"t0": t0, "t1": t1, "dp": dp, "tag": tag}) + "\n")


class InPass:
    """While a pass's host double runs, the file <E189_FAKE_SCHED>.inpass exists (the sampler's "during": "pass" reads it)."""

    def __init__(self, on):
        self.p = (os.environ.get("E189_FAKE_SCHED", "") + ".inpass") if on and os.environ.get("E189_FAKE_SCHED") else ""

    def __enter__(self):
        if self.p:
            open(self.p, "w").close()

    def __exit__(self, *a):
        if self.p and os.path.exists(self.p):
            os.remove(self.p)


def read_sched():
    p = os.environ.get("E189_FAKE_SCHED")
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
    mode = os.environ.get("E189_FAKE_CONFIG", "ok")
    if mode == "fail":
        print("ettelem: cannot open the management node", file=sys.stderr)
        return 1
    j = {"tdp_w": 0, "temp_threshold_c": 65, "power_state": "FULL", "minion_mhz": 600, "noc_mhz": 1000, "fake": True}
    if mode == "tdp5":
        j["tdp_w"] = 5
    elif mode == "thr70":
        j["temp_threshold_c"] = 70
    elif mode == "mhz800":
        j["minion_mhz"] = 800
    print(json.dumps(j, separators=(",", ":")))
    return 0


def etwho():
    if os.environ.get("E189_FAKE_ETWHO", "free") == "held":
        print("/dev/et0_ops someoneelse 4242 other_host")
        return 1
    print("No process holds an ET-SoC-1 device node or card lock.")
    return 0


class Inject:
    """The desk cases' injections (E189_FAKE_INJECT, the module docstring): each moves the sampled point the stop lines read."""

    def __init__(self):
        self.inj = []
        p = os.environ.get("E189_FAKE_INJECT")
        if p and os.path.exists(p):
            with open(p) as f:
                self.inj = json.load(f)
        self.first, self.used = {}, {}

    def apply(self, line, tick, el, sch):
        if not self.inj:
            return line
        live = [s for s in sch if s["t0"] <= tick < s["t1"]]
        npass = sum(1 for s in sch if s.get("tag") == "pass")
        inpass = os.path.exists(os.environ.get("E189_FAKE_SCHED", "") + ".inpass")
        for i, x in enumerate(self.inj):
            cond = x.get("from_s", 0) <= el < x.get("to_s", 1e9) and npass >= x.get("after_pass_launches", 0)
            if cond and x.get("during") == "pass":
                cond = inpass
            elif cond and x.get("during"):
                cond = any(s.get("tag") == x["during"] for s in live)
            if cond and i not in self.first:
                self.first[i] = tick
            if cond and "for_s" in x and tick - self.first[i] > x["for_s"]:
                cond = False
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


def sample_on_stub(card, seconds, every_ms, inj):
    """E189_FAKE_BASE=alt|base: energy_stub.py's simulated card (unchanged, as the end-to-end case runs it), under the injections."""
    child = subprocess.Popen([sys.executable, "-B", STUB, "sample", "--seconds", str(int(seconds)), "--every-ms", str(every_ms),
                              "--sched", os.environ.get("E189_FAKE_SCHED", ""), "--card", card], stdout=subprocess.PIPE,
                             stdin=subprocess.DEVNULL, text=True)

    def term(*_):
        try:
            child.send_signal(signal.SIGTERM)       # energy_stub finishes its line and exits; the loop below then ends
        except OSError:
            pass

    signal.signal(signal.SIGTERM, term)
    t0 = time.time()
    for raw in child.stdout:
        if not raw.startswith("{"):
            continue
        try:
            line = json.loads(raw)
        except ValueError:
            continue
        line = inj.apply(line, line.get("t_ms", 0) / 1000.0, time.time() - t0, read_sched())
        print(json.dumps(line, separators=(",", ":")), flush=True)
    return child.wait()


def sample(argv):
    mode = os.environ.get("E189_FAKE_SAMPLER", "")
    if mode == "dead":                                      # a sampler that never prints a line (the runner must not launch)
        print("fake sampler: cannot open the management node", file=sys.stderr)
        return 1
    seconds = float(arg(argv, "--seconds", 10))
    every_ms = int(arg(argv, "--every-ms", 100))
    every = every_ms / 1000.0
    inj = Inject()
    base = os.environ.get("E189_FAKE_BASE", "")
    if base in ("alt", "base"):
        return sample_on_stub(base, seconds, every_ms, inj)
    terms = {"n": 0}
    signal.signal(signal.SIGTERM, lambda *_: terms.update(n=terms["n"] + 1))
    need = 2 if mode == "stubborn" else 1                  # stubborn: the first SIGTERM is ignored, the second stops it
    t0 = time.time()
    while terms["n"] < need and time.time() - t0 < seconds:
        tick = time.time()
        sch = read_sched()
        live = [s for s in sch if s["t0"] <= tick < s["t1"]]
        dp = sum(s["dp"] for s in live)
        bw, die = IDLE_W + dp, 55 + min(3, int(dp / 5))
        line = {"t_ms": int(tick * 1000), "took_ms": 22, "since_reset_ms": -1, "board_w": round(bw, 2),
                "sp": {"board_avg_w": round(bw, 2), "minion_w": [5.5 + 0.6 * dp] * 3, "sram_w": [3.1 + 0.1 * dp] * 3,
                       "noc_w": [2.4] * 3},
                "temp_c": {"minshire": [die, die - 1, die + 1]}, "mhz": {"minion": 600, "noc": 1000}, "fake": True}
        line = inj.apply(line, tick, tick - t0, sch)
        print(json.dumps(line, separators=(",", ":")), flush=True)
        time.sleep(max(0.0, tick + every - time.time()))
    return 0


SELFTEST = """SELFTEST abc x1 ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad OK
SELFTEST  x1 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 OK
SELFTEST abcdbcde... x1 248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1 OK
SELFTEST a x1000000 cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0 OK
SELFTEST PASS"""


def ledger_key(argv):
    prog = arg(argv, "--prog")
    if prog == "copy":
        return "copy-" + ("zeros" if arg(argv, "--data") == "zeros" else "random")
    if prog == "sort":
        return "sort-" + arg(argv, "--order", "shuffled")
    return "sha256"


def burst(K, launch_s, dp, setup_s, budget, guard_s, mode, tag):
    """The host's own budget rule (main.cpp): a launch starts only while budget - elapsed >= guard + 0.5. Each launch is announced to
    the sampler AT ITS START, [a, a + launch_s], before it runs (verify-e189's fault 1: announced at its end, the alt card saw only its
    last 0.1-0.2 s)."""
    start = time.time()
    time.sleep(setup_s)
    walls, spans = [], []
    n_max = K - 2 if mode == "short" else K
    for _ in range(n_max):
        if budget - (time.time() - start) < guard_s * scale() + 0.5 * scale():
            break
        a = time.time()
        sched_add(a, a + launch_s, dp, tag)
        time.sleep(max(0.0, a + launch_s - time.time()))
        b = time.time()
        walls.append(round(b - a, 4))
        spans += [int(a * 1000), int(b * 1000)]
        time.sleep(0.004 * scale())
    return walls, spans


def host_ledger(argv):
    mode = os.environ.get("E189_FAKE_HOST", "ok")
    if "--selftest" in argv:
        print(SELFTEST)
        return 0
    if mode == "crash":
        print("fake ledger host: crashed before its line", file=sys.stderr)
        return 134
    key = ledger_key(argv)
    f = forecast()[key]
    K = int(arg(argv, "--launches", 1))
    small = K == 1                      # the smoke's runs are one launch each; every pass has K of 7 or more
    launch_s = (0.05 if small else f["seconds"]["point"]) * scale()
    guard = {"copy-zeros": 1.5032, "copy-random": 1.5032, "sha256": 0.76803, "sort-sorted": 1.142784, "sort-shuffled": 1.142784}[key]
    with InPass(not small):
        walls, spans = burst(K, launch_s, f["w_over_idle"], 0.3 * scale(), 9.5 * scale(), 0.0 if small else guard,
                             mode if not small else "ok", "smoke" if small else "pass")
    n = len(walls)
    P = 2048
    cyc = int(round(launch_s / scale() * 600e6))
    bad = 1 if mode == "fail" or (mode == "fail-pass" and not small) else 0
    j = {"ledger": 1, "prog": arg(argv, "--prog"), "device": "card", "participants": P, "launches": n, "wall_s": walls,
         "launch_epoch_ms": spans, "records_ok": P, "records_bad": 0, "units": 7, "units_expected": 7,
         "hart0_cycles": {"max": cyc, "min": cyc - 1000, "mean": cyc - 500.0, "n": 1024}, "checked": P, "mismatches": bad,
         "expect_checked": P if "--expect" in argv else 0, "expect_mismatches": 0,
         "first_mismatch": "participant 7" if bad else "", "status": "PASS" if (n == K and not bad) else "FAIL", "fake": True}
    if mode == "nojson":
        print('{"ledger":1,"prog":"cut')
        return 124
    print(json.dumps(j, separators=(",", ":")))
    return 0 if j["status"] == "PASS" else 1


def host_spp(argv):
    mode = os.environ.get("E189_FAKE_HOST", "ok")
    f = forecast()["sparse-parity"]
    R = int(arg(argv, "--reps", 1))
    launch_s = f["seconds"]["point"] * scale()
    t0 = time.time()
    with InPass(R > 1):
        walls, spans = burst(R, launch_s, f["w_over_idle"], 0.6 * scale(), 9.0 * scale(), 0.784738,
                             mode if R > 1 else "ok", "pass" if R > 1 else "smoke")
    n = len(walls)
    rec = arg(argv, "--records-out")
    if rec:
        with open(rec, "w") as fo:
            fo.write("fake records\n")
    cyc = int(round(launch_s / scale() * 600e6))
    j = {"workload": "sparseparity", "device": "silicon", "n": 544, "k": 4, "eta": 0.39, "m": 1792, "seed": 3,
         "instance": {"n": 544, "k": 4, "eta": 0.39, "m": 1792, "seed": 3, "hash": "fake"}, "plan": {"slice": "0/1", "model_s": 0.514741},
         "reps_requested": R, "reps_done": n, "reps_consistent": "ok", "launch_s": walls,
         "launch_epoch_ms": [spans[0], spans[-1]] if spans else [0, 0], "kernel": {"cycles_max": cyc},
         "result": {"solved": mode != "fail", "unique": True, "answer": [1, 2, 3, 4]},
         "host_cpu_s": {"burst": [round(0.9 * (time.time() - t0), 3), 0.05]},
         "status": "PASS" if (n == R and mode != "fail") else "FAIL", "fake": True}
    if n < R:
        j["problems"] = [f"reps: {n} of {R} done"]
        j["stop_reason"] = "budget"
    print(json.dumps(j, separators=(",", ":")))
    return 0 if j["status"] == "PASS" else 1


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    w, rest = argv[0], argv[1:]
    if w == "config":
        return config()
    if w == "etwho":
        return etwho()
    if w == "sample":
        return sample(rest)
    if w == "host-ledger":
        return host_ledger(rest)
    if w == "host-spp":
        return host_spp(rest)
    print(f"fake_card_e189: unknown double {w}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
