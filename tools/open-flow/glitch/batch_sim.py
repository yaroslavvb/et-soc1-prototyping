#!/usr/bin/env python3
"""Q138(g): run_tile.py over every stimulus file for the given arms and points, JOBS at a time, nice 10.
    batch_sim.py --arms booth_tree,... --points 471698 --tag primary [--model-suffix _w0] [--extra '--skew-ps 150'] --jobs 6
"""
import argparse, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
W = os.environ.get("Q138G_WORK", ".")      # the work directory: stim/, models/, sims/
HERE = os.path.dirname(os.path.abspath(__file__))

def one(args):
    arm, tile, n0, tag, suffix, extra = args
    stim = f"{W}/stim/{arm}__{tile}__{n0}.pkl.gz"
    out = f"{W}/sims/{tag}/{arm}__{tile}__{n0}.json"
    if os.path.exists(out):
        return out, "cached"
    r = subprocess.run(["nice", "-n", "10", sys.executable, os.path.join(HERE, "run_tile.py"), "--model", f"{W}/models/{arm}{suffix}.pkl",
                        "--stim", stim, "--out", out] + extra.split(), capture_output=True, text=True)
    return out, (r.stdout.strip() if r.returncode == 0 else "FAILED " + r.stderr[-400:])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="booth_tree,booth,booth_swap,plain")
    ap.add_argument("--points", default="471698")
    ap.add_argument("--tiles", default="")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--model-suffix", default="")
    ap.add_argument("--extra", default="")
    ap.add_argument("--jobs", type=int, default=6)
    argv = sys.argv[1:]
    for i in range(len(argv) - 1):                       # "--extra '--a --b'": a value that starts with a dash
        if argv[i] == "--extra":
            argv[i:i + 2] = ["--extra=" + argv[i + 1]]
            break
    a = ap.parse_args(argv)
    os.makedirs(f"{W}/sims/{a.tag}", exist_ok=True)
    tiles = a.tiles.split(",") if a.tiles else sorted({f.split("__")[1] for f in os.listdir(f"{W}/stim") if f.endswith(".pkl.gz")})
    jobs = [(arm, t, p, a.tag, a.model_suffix, a.extra) for p in a.points.split(",") for arm in a.arms.split(",") for t in tiles
            if os.path.exists(f"{W}/stim/{arm}__{t}__{p}.pkl.gz")]
    t0 = time.time()
    with ThreadPoolExecutor(a.jobs) as ex:
        for out, st in ex.map(one, jobs):
            print(f"{time.time()-t0:7.1f}s {st}", flush=True)
    print("done", len(jobs), f"{time.time()-t0:.1f}s")

if __name__ == "__main__":
    main()
