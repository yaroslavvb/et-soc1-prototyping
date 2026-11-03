"""Q139(s) diagnostic (post hoc): split each arm's E143 board-W error into the switching part D (board W less the same
type's zeros anchor, measured in the same pass; E143 results.json D_w) and the zeros level, per registered group."""
import json, math, sys, statistics as st
cv = json.load(open(sys.argv[1]))
R = json.load(open(sys.argv[2]))["score"]["reported"]["tiles"]
out = {}
for arm, tiles in cv["E143_tiles"].items():
    z = {t["type"]: t["w_pred"] for n, t in tiles.items() if n.endswith("anchor_zeros")}
    zm = {tiles[n]["type"]: R[n]["burst_w"] for n in tiles if n.endswith("anchor_zeros")}
    res = {}
    for g in ("governed", "pinned"):
        eD = [R[n]["D_w"] - (t["w_pred"] - z[t["type"]]) for n, t in tiles.items() if t["group"] == g and R[n].get("D_w") is not None and not n.endswith("anchor_zeros")]
        res[g] = {"n_D": len(eD), "D_rms_w": math.sqrt(sum(e * e for e in eD) / len(eD)), "D_mean_meas_minus_pred_w": st.mean(eD)}
    res["zeros_level_meas_minus_pred_w"] = {t: zm[t] - z[t] for t in z}
    out[arm] = res
    print(f"{arm:30s} D governed rms {res['governed']['D_rms_w']:.3f} (mean {res['governed']['D_mean_meas_minus_pred_w']:+.3f}, n {res['governed']['n_D']}) | "
          f"D pinned rms {res['pinned']['D_rms_w']:.3f} (mean {res['pinned']['D_mean_meas_minus_pred_w']:+.3f}, n {res['pinned']['n_D']}) | zeros level meas-pred "
          + ", ".join(f"{t} {v:+.2f}" for t, v in sorted(res["zeros_level_meas_minus_pred_w"].items())))
json.dump(out, open(sys.argv[3], "w"), indent=1, sort_keys=True)
