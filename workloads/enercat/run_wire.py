#!/usr/bin/env python3
"""Heat per millimetre: the energy of moving bits across the mesh, with the data on the wires controlled.

    python3 workloads/enercat/run_wire.py <out-dir> [--set v1|v2] [--host-bin PATH] [--passes 3] [--burst 3] [--gap 5] [--after 4]
                                          [--only PREFIXES] [--warm-c 69]

Every configuration is 1 KB tensor loads by hart 0 of every participating minion from a scratchpad exactly d mesh
hops away (d = 0 is the shire's own scratchpad), at most two readers per target. Before each configuration every
scratchpad is filled with a known 512 B image by `--pattern tstore_raw`, which stores the host's bytes exactly
(checked on the card with --dump-slice), so the bits on the links are chosen:

  wbern/p{P}/hop{d}   every bit independently 1 with probability P: two consecutive flits differ in a bit with
                      probability 2P(1-P) whichever flows interleave on a link. P and 1-P toggle alike but carry
                      opposite densities of ones, which separates "energy per transition" from "energy per one".
  walt/n{N}/hop{d}    blocks of N bytes alternately all-zero and all-one: a link toggles only where a flit boundary
                      meets a block boundary, so the cost against N shows the flit width.
  waxis/{x|y}/hop{d}/p{P}   only pairs in the same row (x) or column (y): a straight run of d links in one direction.
  wlegacy/random/hop{d}     the manual's original 'random' data (E27), to tie the two experiments together.

Configurations run in a different random order each pass, bracketed by idle on both sides (the prefill and the
heater are logged in marks.jsonl so the analysis can keep them out of the brackets), with ettelem telemetry at 10 Hz.
On a card whose governor lifts the clock when the die is cool (aifoundry2), a 2 s heater runs before a
configuration whenever the die reads below --warm-c; the analysis drops any burst whose samples left 600 MHz.
Every host process holds the card for under 12 s.
"""
import argparse
import json
import os
import random
import socket
import subprocess
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
H = os.path.join(ROOT, "build", "enercat", "host", "enercat_host")
HEATER = os.path.join(ROOT, "build", "sparsity_t2", "host", "sparsity_host")
ENV = dict(os.environ, LD_LIBRARY_PATH="/opt/et/lib")
LOAD = ["--pattern", "tload_pat", "--slice-bytes", "32K", "--stride", "1K", "--access-bytes", "1K", "--region", "32K"]

PS = ("0", "0.1", "0.25", "0.5", "0.75", "0.9", "1")


def where(d, axis=None):
    if d == 0:
        return ["--scp"]
    return ["--hop-distance", str(d)] + (["--hop-axis", axis] if axis else [])


def configs():
    c = []
    for p in PS:
        for d in (0, 1, 2, 3, 4, 6):
            c.append({"cfg": f"wbern/p{p}/hop{d}", "fill": f"bern:{p}", "args": LOAD + ["--operands", f"bern:{p}"] + where(d)})
    for n in (16, 32, 64, 128, 256):
        for d in (0, 1, 3, 6):
            c.append({"cfg": f"walt/n{n}/hop{d}", "fill": f"alt:{n}", "args": LOAD + ["--operands", f"alt:{n}"] + where(d)})
    for axis in ("x", "y"):
        for d in (1, 2, 3, 4):
            for p in ("0", "0.5"):
                c.append({"cfg": f"waxis/{axis}/hop{d}/p{p}", "fill": f"bern:{p}",
                          "args": LOAD + ["--operands", f"bern:{p}"] + where(d, axis)})
    for d in (0, 1, 3, 6):
        c.append({"cfg": f"wlegacy/random/hop{d}", "fill": "legacy:random", "args": LOAD + ["--operands", "random"] + where(d)})
    return c


# ---- the second set (v2): every line on the chip unique, and flows that share no link -------------------------
# The first set fills each scratchpad region with one 512 B image repeated 64 times, and two readers of a target read
# the same bytes, so consecutive flits on a link can be exact copies (a minion's two in-flight loads, or two flows
# that interleave). That lowers the real toggle rate below 2P(1-P) by an unknown factor. v2 fills every 512 B block
# from its own random bytes (--pattern tstore_uniq, P in {0, 1/4, 1/2, 3/4, 1}, 3/4 the exact complement of 1/4),
# gives the two readers of a target different regions (--uniq-regions), and adds:
#   wsep/p{P}/hop{d}  straight row/column pairs chosen so no two flows share a directed link and every target has one
#                     reader, so link contention does not grow with d;
#   wfrz/hop{d}       one random 64 B line repeated everywhere: half the bits ones, no two flits differ.
MESH = {0: (0, 0), 24: (1, 0), 9: (2, 0), 25: (3, 0), 2: (4, 0), 11: (5, 0), 8: (0, 1), 16: (1, 1), 1: (2, 1), 17: (3, 1),
        10: (4, 1), 19: (5, 1), 3: (0, 2), 4: (1, 2), 13: (2, 2), 14: (3, 2), 18: (4, 2), 27: (5, 2), 12: (1, 3), 21: (2, 3),
        22: (3, 3), 26: (4, 3), 20: (1, 4), 29: (2, 4), 30: (3, 4), 15: (4, 4), 23: (5, 4), 28: (1, 5), 5: (2, 5), 6: (3, 5),
        7: (4, 5), 31: (5, 5)}


def _links(t, r):
    (x, y), (x1, y1) = MESH[t], MESH[r]
    out = []
    while x != x1:
        nx = x + (1 if x1 > x else -1); out.append(((x, y), (nx, y))); x = nx
    while y != y1:
        ny = y + (1 if y1 > y else -1); out.append(((x, y), (x, ny))); y = ny
    return out


def disjoint_pairs(d, tries=400):
    """Largest set found of straight reader<-target pairs d apart with one reader per target and no shared link."""
    cands = [(r, t) for r in MESH for t in MESH if r != t and (MESH[r][0] == MESH[t][0] or MESH[r][1] == MESH[t][1])
             and abs(MESH[r][0] - MESH[t][0]) + abs(MESH[r][1] - MESH[t][1]) == d]
    best = []
    for k in range(tries):
        random.Random(k).shuffle(cands)
        ur, ut, ul, sel = set(), set(), set(), []
        for r, t in cands:
            L = _links(t, r)
            if r in ur or t in ut or any(l in ul for l in L):
                continue
            sel.append((r, t)); ur.add(r); ut.add(t); ul.update(L)
        if len(sel) > len(best):
            best = list(sel)
    return sorted(best)


def configs_v2():
    c = []
    for p in ("0", "0.25", "0.5", "0.75", "1"):
        for d in (0, 1, 2, 3, 4, 6):
            c.append({"cfg": f"wu/p{p}/hop{d}", "fill": f"uniq:uq:{p}",
                      "args": LOAD + ["--operands", f"uq:{p}"] + where(d) + (["--uniq-regions"] if d else [])})
    for p in ("0", "0.5"):
        for d in (1, 2, 3, 4, 5):
            pairs = ",".join(f"{r}:{t}" for r, t in disjoint_pairs(d))
            c.append({"cfg": f"wsep/p{p}/hop{d}", "fill": f"uniq:uq:{p}",
                      "args": LOAD + ["--operands", f"uq:{p}", "--pairs", pairs]})
    for d in (0, 1, 3, 6):
        c.append({"cfg": f"wfrz/hop{d}", "fill": "frz", "args": LOAD + ["--operands", "frz"] + where(d)})
    return c


def die_c(tel_path):
    try:
        with open(tel_path, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - 4000))
            lines = [l for l in f.read().decode(errors="ignore").splitlines() if l.startswith("{")]
        return json.loads(lines[-1])["temp_c"]["minshire"][0] if lines else None
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--passes", type=int, default=3)
    ap.add_argument("--burst", type=float, default=3.0)
    ap.add_argument("--gap", type=float, default=5.0, help="quiet seconds between a configuration's prefill and its burst")
    ap.add_argument("--after", type=float, default=4.0, help="quiet seconds after each burst, so it has an idle bracket on both sides")
    ap.add_argument("--only", default="")
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--warm-c", type=float, default=0.0, help="run a heater before a configuration when the die is below this")
    ap.add_argument("--set", default="v1", choices=["v1", "v2"], help="v1: repeated images; v2: unique lines, disjoint flows")
    ap.add_argument("--host-bin", default=H, help="enercat_host to use (v2 needs a build with tstore_uniq)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cfgs = configs() if a.set == "v1" else configs_v2()
    hb = a.host_bin
    if a.only:
        keep = a.only.split(",")
        cfgs = [c for c in cfgs if any(c["cfg"].startswith(k) for k in keep)]
    host = socket.gethostname()
    tel_path = os.path.join(a.out, "telemetry.jsonl")
    tel = open(tel_path, "a")
    per = a.burst + a.gap + a.after + 3.5 + (2.5 if a.warm_c else 0)
    total_s = int(len(cfgs) * a.passes * per + 300)

    def start_sampler():
        """Start ettelem and wait until it writes; it can fail to open the management node right after another
        instance let go of it (23 and 24 Sep: both cards' v2 runs lost their telemetry that way), so retry."""
        for attempt in range(8):
            size0 = os.path.getsize(tel_path)
            sp = subprocess.Popen([os.path.join(ROOT, "build", "ettelem", "ettelem"), "sample", "--seconds", str(total_s),
                                   "--every-ms", "100"], stdout=tel, stderr=subprocess.DEVNULL, env=ENV)
            for _ in range(40):
                time.sleep(0.25)
                if os.path.getsize(tel_path) > size0:
                    return sp
            sp.kill(); sp.wait()
            if attempt == 1:
                # a reply left in the management queue by a sampler killed mid-request crashes every newcomer;
                # the vendor tool consumes it (and dies doing so), after which ettelem starts (tools/ettelem/ettelem.cpp)
                subprocess.run(["timeout", "20", "/opt/et/bin/dev_mngt_service", "-m", "DM_CMD_GET_MODULE_POWER", "-n", "0",
                                "-u", "5000"], env=ENV, capture_output=True)
            time.sleep(3)
        raise SystemExit("ettelem sampler would not start")

    sampler = start_sampler()
    runs = open(os.path.join(a.out, "runs.jsonl"), "a")
    # Every use of the card that is not a measured burst (the prefill stores, the heater) is logged here, so the
    # analysis can keep it out of the idle windows that bracket the bursts.
    marks = open(os.path.join(a.out, "marks.jsonl"), "a")

    def mark(kind, cfg, t0, t1, p):
        marks.write(json.dumps({"kind": kind, "cfg": cfg, "pass": p, "t_start_ms": int(t0 * 1000), "t_end_ms": int(t1 * 1000)}) + "\n")
        marks.flush()
    log = open(os.path.join(a.out, "run.log"), "a")
    print(f"{host}: {len(cfgs)} configurations x {a.passes} passes, about {len(cfgs) * a.passes * per / 60:.0f} min", file=log, flush=True)
    time.sleep(8)
    last_size = [os.path.getsize(tel_path), time.time()]

    def check_sampler():
        """Before each configuration: the sampler must be alive and the file growing, else restart it."""
        nonlocal sampler
        size = os.path.getsize(tel_path)
        stalled = time.time() - last_size[1] > 2.0 and size <= last_size[0]   # it writes a line every 100 ms
        if sampler.poll() is not None or stalled:
            print(f"sampler {'exited' if sampler.poll() is not None else 'stalled'}; restarting", file=log, flush=True)
            if sampler.poll() is None:
                sampler.kill(); sampler.wait()
            time.sleep(2)
            sampler = start_sampler()
            time.sleep(4)
        last_size[0], last_size[1] = os.path.getsize(tel_path), time.time()
    try:
        for p in range(a.passes):
            order = list(range(len(cfgs)))
            random.Random(a.seed + p).shuffle(order)
            for i in order:
                c = cfgs[i]
                check_sampler()
                if a.warm_c:
                    t = die_c(tel_path)
                    if t is not None and t < a.warm_c:
                        h0 = time.time()
                        subprocess.run(["timeout", "10", HEATER, "--test", "fma", "--type", "fp32", "--pattern", "none", "--values",
                                        "randn", "--shires", "0xffffffff", "--per-shire", "32", "--seconds", "2", "--seed", "1"],
                                       env=ENV, capture_output=True)
                        mark("heater", c["cfg"], h0, time.time(), p)
                        print(f"heater at {t} C", file=log, flush=True)
                if c["fill"].startswith("legacy:"):
                    fill = ["--pattern", "tstore", "--operands", c["fill"].split(":", 1)[1]]
                elif c["fill"].startswith("uniq:"):
                    fill = ["--pattern", "tstore_uniq", "--operands", c["fill"].split(":", 1)[1]]
                else:
                    fill = ["--pattern", "tstore_raw", "--operands", c["fill"]]
                f0 = time.time()
                subprocess.run(["timeout", "12", hb] + fill + ["--slice-bytes", "32K", "--scp", "--seconds", "0.3", "--window", "60000000"],
                               env=ENV, capture_output=True)
                mark("fill", c["cfg"], f0, time.time(), p)
                time.sleep(a.gap)
                r = subprocess.run(["timeout", "12", hb] + c["args"] + ["--seconds", str(a.burst), "--window", "240000000"],
                                   env=ENV, capture_output=True, text=True)
                n = 0
                for line in r.stdout.splitlines():
                    if line.startswith("ENERCAT {"):
                        runs.write(json.dumps({"host": host, "pass": p, "cfg": c["cfg"], **json.loads(line[8:])}) + "\n")
                        n += 1
                runs.flush()
                time.sleep(a.after)
                print(f"pass {p} {c['cfg']}: {n} launches" + ("" if n else f" rc={r.returncode} {r.stderr[-200:]!r}"), file=log, flush=True)
        time.sleep(a.gap + 3)
    finally:
        sampler.terminate()   # ettelem finishes the sample in flight on SIGTERM, leaving the queue clean
        try:
            sampler.wait(timeout=10)
        except subprocess.TimeoutExpired:
            sampler.kill()
    print("done", file=log, flush=True)


if __name__ == "__main__":
    main()
