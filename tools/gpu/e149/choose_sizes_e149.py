"""Amendment A1's rule, applied to the size smoke S2: for fp16 and int8, the largest of 1792^3, 1536^3 and 1024^3 at
which the random kind's window is valid (1410 MHz in every sample, no clock-event reason bit) and draws at most 360 W.

    python choose_sizes_e149.py <logs/e149-20261102-smoke2>      # prints every window and the choice as JSON
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_e149 as AZ  # noqa: E402

LIMIT_W = 360.0
RANDOM = {"fp16": "randn", "int8": "rand"}


def main(run):
    u = AZ.load_unit(os.path.join(run, "S2"))
    rows = {}
    for s in u["steps"]:
        if s.get("op") != "pass":
            continue
        for w in s["windows"]:
            if w["role"] != "cell":
                continue
            st = AZ.wstats(u, w["t_a"], w["t_b"], AZ.SETTLE["cell"], 1410)
            tf = 2.0 * w["n"] ** 3 * w["calls"] / (w["gpu_ms"] / 1000.0) / 1e12
            rows[w["kind"]] = {"n": w["n"], "p_w": round(st["p_w"], 2), "t_c": round(st["t_c"], 1),
                               "sm_min": st["sm_min"], "cap_frac": st["cap_frac"], "rsn_or": st["rsn_or"],
                               "valid": st["valid"], "tflops": round(tf, 1)}
    choice = {"bf16": 2048}
    for fmt, rk in RANDOM.items():
        pick = None
        for n in (1792, 1536, 1024):
            r = rows.get(f"{fmt}.{rk}@{n}")
            if r and r["valid"] and r["p_w"] <= LIMIT_W:
                pick = n
                break
        choice[fmt] = pick
    print(json.dumps({"windows": rows, "limit_w": LIMIT_W, "choice": choice}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
