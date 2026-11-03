#!/usr/bin/env python3
"""Q138(g): every E130 tile through each Q133(a) bench binary at the given launch points; each VCD is read for the 16
tima_top instances (vcdread.read_tima), saved as a gzipped pickle, and deleted. nice 10, at most JOBS processes.
    batch_vcd.py --arms booth_tree,booth,booth_swap,plain --points 471698 --jobs 6 --out <dir>
"""
import argparse, gzip, os, pickle, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vcdread
B = os.environ.get("Q138G_BUILD", "")   # Q133(a)'s bench build: obj_<arm>/Vtb and accum
TILES = os.path.join(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")), "tools", "claims-v3", "kinds", "e130", "tiles", "int8")

def one(args):
    arm, tile, n0, out, tdir = args
    pk = os.path.join(out, f"{arm}__{tile}__{n0}.pkl.gz")
    if os.path.exists(pk):
        return pk, "cached"
    vcd = os.path.join(out, f"{arm}__{tile}__{n0}.vcd")
    r = subprocess.run(["nice", "-n", "10", sys.executable, os.path.join(HERE, "mkvcd.py"), f"{B}/obj_{arm}/Vtb", f"{B}/accum",
                        f"{tdir}/{tile.replace('kind_', '')}.bin", str(n0), vcd], capture_output=True, text=True)
    if r.returncode:
        return pk, "FAILED " + r.stderr[-500:]
    times, insts, xz = vcdread.read_tima(vcd)
    with gzip.open(pk + ".tmp", "wb") as f:
        pickle.dump({"arm": arm, "tile": tile, "n0": n0, "times": times, "insts": insts, "xz": xz}, f, protocol=4)
    os.replace(pk + ".tmp", pk)
    os.remove(vcd)
    return pk, "ok"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="booth_tree,booth,booth_swap,plain")
    ap.add_argument("--points", default="471698")
    ap.add_argument("--tiles", default="")
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tiles-dir", default=TILES, help="kinds tiles: tools/claims-v3/kinds/tiles/int8 (named kind_<kind>)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    pre = "" if a.tiles_dir == TILES else "kind_"
    tiles = a.tiles.split(",") if a.tiles else sorted(pre + f[:-4] for f in os.listdir(a.tiles_dir) if f.endswith(".bin"))
    jobs = [(arm, t, int(p), a.out, a.tiles_dir) for p in a.points.split(",") for arm in a.arms.split(",") for t in tiles]
    t0 = time.time()
    with ThreadPoolExecutor(a.jobs) as ex:
        for pk, st in ex.map(one, jobs):
            print(f"{time.time()-t0:7.1f}s {st} {os.path.basename(pk)}", flush=True)
    print("done", len(jobs), f"{time.time()-t0:.1f}s")

if __name__ == "__main__":
    main()
