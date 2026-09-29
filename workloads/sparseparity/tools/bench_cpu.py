#!/usr/bin/env python3
"""bench_cpu.py: the CPU baselines over the M0 ladder, on a lab host's CPU. Host code only; never opens a card.

  bench_cpu.py --bin DIR --out DIR [--maxt 6] [--only substr,...] [--spbits PATH]
  (run it as `nice -n 19 python3 bench_cpu.py ...`, detached: `setsid nohup ... < /dev/null &`)

Every run gets at most --maxt threads, pinned one per physical core (OMP_PLACES={0},{1},..., OMP_PROC_BIND=close;
the 'smt2' runs put 2 threads on the two hyperthreads of core 0), waits while anyone holds an ET card (et-who), and
records et-who before and after it, the mean clock of the cores it used, the host and the time. One JSON object per
run is appended to OUT/bench.jsonl; OUT also gets lscpu, et-lab-manifest (if installed), the binaries' sha256 and
powercap.txt (the package power limits and who may read the energy counter: the reason CPU energy is assumed).

The ladder (DESIGN.md with the critique's showcase at eta = 0.4):
  C0 (32,3,0.1,128)   C1 (128,4,0.2,192)   L1 (512,4,0.3,448)   L2 (512,4,0.4,1850)   F5 (256,5,0.4,1925)
  L5 (512,5,0.4,2151) as a 1/64 slice (every 64th (i1,i2) prefix)   B1 = 1,024 x (64,4,0.1,64)
  two-stage screens at the showcase sizes, each at two m1 (the card's and the CPU's own optimum; review R2,
  findings 2 and 5): L2 m1 = 832 (tau1 80) and 1024 (104); F5 m1 = 1024 (104) and 1280 (144); L5/64 m1 = 1024 (104)
  and 1280 (144). Every tau1 keeps the secret with probability 0.9989-0.9994.
Methods: vexh (AVX-512, 8 candidates per register) at 1, 2, 4, 6 threads and smt2, --reps (default 5) repetitions
per point (reported as median and range); mitm (bucketed meet in the middle, with the random halving) over seeds;
batch B1 with 8 instances per register (and the old one-instance-per-thread for continuity); spbits exh (SP3's scan)
for continuity; spref (the reference) and vexh sums=1 for correctness at scale; r sweeps of mitm on L1 and L2.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import socket
import subprocess
import threading
import time
from pathlib import Path

LADDER = {
    "C0": (32, 3, 0.1, 128), "C1": (128, 4, 0.2, 192), "L1": (512, 4, 0.3, 448), "L2": (512, 4, 0.4, 1850),
    "F5": (256, 5, 0.4, 1925), "L5": (512, 5, 0.4, 2151),
}


def et_who() -> str:
    """holder lines of et-who ('' = no holder); never opens a device"""
    if not shutil.which("et-who"):
        return ""
    p = subprocess.run(["et-who"], capture_output=True, text=True)
    return "\n".join(x for x in p.stdout.splitlines() if x.startswith("/dev/et") or x.startswith("lock:"))


def wait_card_free(log, limit_s=1800) -> str:
    t0 = time.time()
    held = et_who()
    while held and time.time() - t0 < limit_s:
        log(f"card held, waiting: {held!r}")
        time.sleep(15)
        held = et_who()
    return held


def mhz_of(cpus):
    vals = {}
    cpu = -1
    with open("/proc/cpuinfo") as f:
        for line in f:
            if line.startswith("processor"):
                cpu = int(line.split(":")[1])
            elif line.startswith("cpu MHz") and cpu in cpus:
                vals[cpu] = float(line.split(":")[1])
    return [vals[c] for c in cpus if c in vals]


class MhzSampler(threading.Thread):
    def __init__(self, cpus):
        super().__init__(daemon=True)
        self.cpus, self.samples, self.stop = cpus, [], threading.Event()

    def run(self):
        while not self.stop.wait(0.5):
            v = mhz_of(self.cpus)
            if v:
                self.samples.append(sum(v) / len(v))


def siblings0():
    try:
        s = Path("/sys/devices/system/cpu/cpu0/topology/thread_siblings_list").read_text().strip()
        return [int(x) for x in s.replace("-", ",").split(",")][:2]
    except OSError:
        return [0, 1]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bin", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--maxt", type=int, default=6)
    ap.add_argument("--only", default="")
    ap.add_argument("--spbits", default=None)
    ap.add_argument("--reps", type=int, default=5, help="repetitions per timed point (median and range)")
    a = ap.parse_args()
    B = Path(a.bin).resolve()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    logf = open(out / "bench.log", "a")

    def log(msg):
        logf.write(f"{dt.datetime.now().isoformat(timespec='seconds')} {msg}\n")
        logf.flush()

    # the machine, once
    (out / "lscpu.txt").write_text(subprocess.run(["lscpu"], capture_output=True, text=True).stdout)
    if shutil.which("et-lab-manifest"):
        (out / "manifest.txt").write_text(subprocess.run(["et-lab-manifest"], capture_output=True, text=True).stdout)
    # why CPU energy is not measured here: the RAPL counter is root-only and the package limits are lifted
    pc = []
    for f in sorted(Path("/sys/class/powercap").glob("intel-rapl:*/constraint_*")) + \
            sorted(Path("/sys/class/powercap").glob("intel-rapl:*/energy_uj")) + [Path("/proc/sys/kernel/perf_event_paranoid")]:
        try:
            st = f.stat()
            try:
                val = f.read_text().strip()
            except OSError as e:
                val = f"unreadable ({e.strerror})"
            pc.append(f"{f} mode={oct(st.st_mode & 0o777)} uid={st.st_uid}: {val}")
        except OSError:
            pass
    (out / "powercap.txt").write_text("\n".join(pc) + "\n")
    bins = [B / "spref", B / "spbase"] + ([Path(a.spbits)] if a.spbits else [])
    (out / "code.sha256").write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n"
                                             for p in bins))
    sib = siblings0()
    threads = [t for t in (1, 2, 4, 6) if t <= a.maxt]

    runs = []   # (label, argv, threads, placement)

    def add(label, argv, t, place="cores"):
        runs.append((label, [str(x) for x in argv], t, place))

    def inst(name, **over):
        n, k, eta, m = LADDER[name]
        d = dict(n=n, k=k, eta=eta, m=m, seed=1)
        d.update(over)
        return [f"{kk}={v}" for kk, v in d.items()]

    V, R, S = B / "spbase", B / "spref", a.spbits
    nr = max(1, a.reps)
    reps = dict(C0=200, C1=20, L1=nr, L2=nr, F5=nr)
    # vexh: the thread ladder and smt2
    for name in ("C0", "C1", "L1", "L2", "F5"):
        for t in threads:
            add(f"vexh {name}", [V, "vexh", *inst(name), f"threads={t}", f"reps={reps[name]}"], t)
        add(f"vexh {name}", [V, "vexh", *inst(name), "threads=2", f"reps={reps[name]}"], 2, "smt2")
    # the two-stage screens (stage 1 timed over the reps, stage 2 once), each at two m1
    TWO = [("L2", 832, 80, 1850), ("L2", 1024, 104, 1850), ("F5", 1024, 104, 1925), ("F5", 1280, 144, 1925),
           ("L5", 1024, 104, 2151), ("L5", 1280, 144, 2151)]
    for t in threads:
        add("vexh L5/64", [V, "vexh", *inst("L5"), "slice=64", f"threads={t}", f"reps={nr}"], t)
        for name, m1, tau, m2 in TWO:
            lab = f"vexh {name}{'/64' if name == 'L5' else ''} two-stage m1={m1}"
            add(lab, [V, "vexh", *inst(name, m=m1), *(["slice=64"] if name == "L5" else []), f"tau={tau}",
                      f"m2={m2}", f"threads={t}", f"reps={nr}"], t)
        add("batch B1", [V, "batch", "n=64", "k=4", "eta=0.1", "m=64", "seed=1", "count=1024", f"threads={t}",
                         f"reps={nr}", "lanes=1"], t)
    add("vexh L5/64", [V, "vexh", *inst("L5"), "slice=64", "threads=2", f"reps={nr}"], 2, "smt2")
    add("batch B1", [V, "batch", "n=64", "k=4", "eta=0.1", "m=64", "seed=1", "count=1024", "threads=2",
                     f"reps={nr}", "lanes=1"], 2, "smt2")
    for t in sorted({1, a.maxt}):   # the old B1 baseline (one instance per thread through vexh), for continuity
        add("batch B1 vexh-per-instance", [V, "batch", "n=64", "k=4", "eta=0.1", "m=64", "seed=1", "count=1024",
                                           f"threads={t}", f"reps={nr}", "lanes=0"], t)
    # correctness at scale: vexh with both checksums, the reference, the reference through a 1,024-minion plan
    for name in ("L1", "L2", "F5"):
        add(f"vexh sums {name}", [V, "vexh", *inst(name), f"threads={a.maxt}", "sums=1"], a.maxt)
    for name in ("C1", "L1", "L2"):
        add(f"spref {name}", [R, "scan", *inst(name), f"threads={a.maxt}"], a.maxt)
    add("spref L5/64 two-stage stage 1 (plan slice 0 of 64)", [R, "scan", *inst("L5"), "m1=1280", "tau1=144",
        f"threads={a.maxt}", f"plan={out}/l5s.0.bin", f"out={out}/l5s.0.ref"], a.maxt)
    add("spref L2 plan", [R, "scan", *inst("L2"), f"threads={a.maxt}", f"plan={out}/l2.bin", f"out={out}/l2.ref"],
        a.maxt)
    # SP3's scan, for continuity with proto/RESULTS.md (i7-11700K on aifoundry1)
    if S:
        for name in ("L1", "L2"):
            for t in sorted({1, a.maxt}):
                add(f"spbits {name}", [S, "exh", *inst(name), f"threads={t}"], t)
    # mitm (the random halving is the default for k >= 4): seeds; per-repetition samples where a full solve is long
    for name, seeds in (("C0", range(1, 6)), ("C1", range(1, 6)), ("L1", range(1, 11)), ("L2", range(1, 11))):
        for sd in seeds:
            add(f"mitm {name}", [V, "mitm", *inst(name, seed=sd), f"threads={a.maxt}", "maxsec=300"], a.maxt)
        for sd in list(seeds)[:2]:
            add(f"mitm {name}", [V, "mitm", *inst(name, seed=sd), "threads=1", "maxsec=300"], 1)
    for sd in (1, 2, 3):
        add("mitm F5", [V, "mitm", *inst("F5", seed=sd), f"threads={a.maxt}", "maxsec=240"], a.maxt)
    add("mitm F5 reps", [V, "mitm", *inst("F5"), f"threads={a.maxt}", "maxreps=480", "early=0"], a.maxt)
    add("mitm L5 reps", [V, "mitm", *inst("L5"), f"threads={a.maxt}", "maxreps=120", "early=0"], a.maxt)
    for name in ("L1", "L2"):
        for r in range(12, 20):
            add(f"mitm {name} r-sweep", [V, "mitm", *inst(name), f"r={r}", f"threads={a.maxt}", "maxreps=480",
                                         "early=0"], a.maxt)
        add(f"mitm {name} r-sweep no-split", [V, "mitm", *inst(name), "r=15", "split=0", f"threads={a.maxt}",
                                              "maxreps=240", "early=0"], a.maxt)

    # work lists for the spref plan runs
    tools = Path(__file__).resolve().parent
    subprocess.run(["python3", str(tools / "planner.py"), "plan", "--n", "512", "--k", "4", "--m", "1850",
                    "--out", str(out / "l2.bin"), "--compact"], check=True, capture_output=True)
    subprocess.run(["python3", str(tools / "planner.py"), "plan", "--n", "512", "--k", "5", "--m", "1280", "--tau1",
                    "144", "--slices", "64", "--slice", "0", "--out", str(out / "l5s.0.bin"), "--compact"],
                   check=True, capture_output=True)

    only = [s for s in a.only.split(",") if s]
    host = socket.gethostname()
    with open(out / "bench.jsonl", "a") as res:
        for label, argv, t, place in runs:
            if only and not any(s in label for s in only):
                continue
            held = wait_card_free(log)
            if held:
                log(f"skip {label}: card still held after the wait")
                continue
            cpus = sib[:2] if place == "smt2" else list(range(t))
            env = dict(os.environ, OMP_PROC_BIND="close", OMP_PLACES=",".join(f"{{{c}}}" for c in cpus),
                       OMP_NUM_THREADS=str(t), OMP_WAIT_POLICY="passive")
            samp = MhzSampler(cpus)
            samp.start()
            t0 = time.time()
            p = subprocess.run(argv, capture_output=True, text=True, env=env)
            wall = time.time() - t0
            samp.stop.set()
            samp.join()
            after = et_who()
            try:
                d = json.loads(p.stdout.strip().splitlines()[-1])
            except (IndexError, json.JSONDecodeError):
                d = dict(parse_error=p.stdout[-400:], stderr=p.stderr[-400:])
            d.update(label=label, place=place, cpus=cpus, rc=p.returncode, process_s=round(wall, 4), host=host,
                     time=dt.datetime.now().isoformat(timespec="seconds"),
                     mhz_mean=round(sum(samp.samples) / len(samp.samples)) if samp.samples else None,
                     card_holder_after=after or None, argv=" ".join(Path(x).name if i == 0 else x
                                                                   for i, x in enumerate(argv)))
            res.write(json.dumps(d) + "\n")
            res.flush()
            log(f"done {label} t={t} {place} rc={p.returncode} {wall:.2f}s")
    # the reference's plan runs, merged and checked
    for plan, ref, inst_s in ((out / "l2.bin", out / "l2.ref", "512,4,0.4,1850,1"),):
        if ref.exists():
            p = subprocess.run(["python3", str(tools / "planner.py"), "merge", "--plan", str(plan), "--out", str(ref),
                                "--inst", inst_s, "--compact"], capture_output=True, text=True)
            (out / (ref.name + ".merge.json")).write_text(p.stdout)
    if (out / "l5s.0.ref").exists():
        p = subprocess.run(["python3", str(tools / "planner.py"), "merge", "--plan", str(out / "l5s.0.bin"), "--out",
                            str(out / "l5s.0.ref"), "--inst", "512,5,0.4,2151,1", "--partial", "--compact"],
                           capture_output=True, text=True)
        (out / "l5s.0.ref.merge.json").write_text(p.stdout)
    log("all done")


if __name__ == "__main__":
    main()
