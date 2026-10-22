"""E62, post hoc: remove the residual shutter (FFC) steps from a reduced session's frames, for the movies.

reduce_hm.py already bridges every shutter event per pixel; on this camera the events change pixels by up to 10 K, so
a few per cent left over is still 100+ mK of pattern. Per shutter cluster (jumps.py: events under 2.5 s apart merged,
fit windows that skip shutter-flagged and frozen-thinned bins), per pixel, the residual step is the difference of two
straight lines fitted before and after the cluster, evaluated at its middle; the step map is smoothed (Gaussian,
sigma 2 binned px: the per-pixel part was reduce's job, what is left is broad) and subtracted from every later bin.
Writes a copy of the RED with frames.npz replaced and a dejump.json log.
Usage: dejump_frames.py <RED> <RED out>"""
import json
import os
import shutil
import sys

import numpy as np
from scipy.ndimage import gaussian_filter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jumps import MIN_N, clusters, level, windows  # noqa: E402

src, dst = sys.argv[1], sys.argv[2]
SIG = 2.0
os.makedirs(dst, exist_ok=True)
for f in os.listdir(src):
    if f != "frames.npz":
        shutil.copy2(os.path.join(src, f), os.path.join(dst, f))
z = np.load(os.path.join(src, "frames.npz"))
arrs = {k: z[k] for k in z.files}
ts = arrs["t_s"]
mk = arrs["mk"].astype(np.float32)
ok = (~arrs["ffc"].astype(bool)) & (arrs["n"] >= MIN_N)
ev = [e["t_s"] for e in json.load(open(os.path.join(src, "ffc.json")))]
cl = clusters(ev, ts[0], ts[-1])
log = []
for i, (a, b) in enumerate(cl):
    pre, post = windows(ts, ok, cl, i)
    t_mid = 0.5 * (a + b)
    la, lb = level(ts, mk, pre, t_mid), level(ts, mk, post, t_mid)
    if la is None or lb is None:
        log.append({"t_s": [round(a, 3), round(b, 3)], "skipped": True,
                    "n_pre": int(pre.sum()), "n_post": int(post.sum())})
        continue
    step = gaussian_filter(lb - la, SIG)
    mk[ts > a] -= step.astype(np.float32)
    log.append({"t_s": [round(a, 3), round(b, 3)], "step_mean_mk": round(float(step.mean()), 1),
                "step_rms_mk": round(float(step.std()), 1), "n_pre": int(pre.sum()), "n_post": int(post.sum())})
arrs["mk"] = mk
np.savez(os.path.join(dst, "frames.npz"), **arrs)
json.dump({"post_hoc": True, "sigma_px": SIG, "clusters": log}, open(os.path.join(dst, "dejump.json"), "w"), indent=1)
rms = [x["step_rms_mk"] for x in log if "step_rms_mk" in x]
skipped = sum(1 for x in log if x.get("skipped"))
print(f"{len(ev)} events in {len(cl)} clusters, {skipped} skipped; residual step rms median {np.median(rms):.1f} mK, "
      f"max {max(rms):.1f} mK -> {dst}")
