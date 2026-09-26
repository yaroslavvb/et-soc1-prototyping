#!/usr/bin/env python3
"""End-of-block check of one run_ablation session directory (abla, ablb, x5): which runs are kept, which are marked
for dropping and why (host failure, a launch not ok, telemetry gap, any mhz.minion sample != 600). Writes check.json
into the directory and prints a one-line note for block.json. No device access.

    ablcheck.py <session-dir> --leak W_PER_C --launch-temp C [--smoke] [--max-failed 2]

Exit 0 when the session is usable (at most --max-failed runs without output or not ok; off-600 runs do not fail the
block, they are only marked), 1 otherwise. --smoke also requires every telemetry field the reducers read and
reports the cycles per op and results of every fma run.

The note gives both clock rules (ablcore.py): off600 = the registered rule (any sample in [t0-2 s, t1] off 600 MHz,
idle bracket included), busy-off600 = the four-card rule (a burst sample off 600 MHz), and the idle-bracket clocks
seen (idle-mhz), so a card that idles in a low-power state (aifoundry1 card 0: 300 MHz) shows as busy-off600 0 with
its runs listed under off600. Neither fails the block.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ablcore as C  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--leak", type=float, required=True)
    ap.add_argument("--launch-temp", type=float, required=True)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--max-failed", type=int, default=2)
    a = ap.parse_args()
    runs = C.session_runs(a.dir, a.leak, a.launch_temp)
    failed = [r for r in runs if not r.get("launches") or r.get("all_ok") is False]
    off = [r for r in runs if "mhz" in r.get("reason", "")]
    gaps = [r for r in runs if "telemetry" in r.get("reason", "") or "clock" in r.get("reason", "")]
    kept = [r for r in runs if r["kept"]]
    kept_busy = [r for r in runs if r.get("kept_busy")]
    off_busy = [r for r in runs if "busy mhz" in r.get("reason_busy", "")]
    idle_states = {}
    for r in runs:
        if r.get("idle_state"):
            idle_states[r["idle_state"]] = idle_states.get(r["idle_state"], 0) + 1
    fields_ok = True
    if a.smoke:
        tel = C.load_jsonl(os.path.join(a.dir, "telemetry.jsonl"))
        need = lambda s: all(k in s for k in ("t_ms", "board_w", "temp_c", "mhz", "die_mv", "sp")) and \
            "minshire" in s["temp_c"] and "minion" in s["mhz"] and all(k + "_w" in s["sp"] for k in ("minion", "sram", "noc"))
        fields_ok = bool(tel) and all(need(s) for s in tel)
    out = {"dir": a.dir, "runs": len(runs), "kept": len(kept), "kept_busy": len(kept_busy), "failed": [r["config"] for r in failed],
           "off600": [r["config"] for r in off], "off600_busy": [r["config"] for r in off_busy], "idle_states_mhz": idle_states,
           "telemetry_gaps": [r["config"] for r in gaps],
           "dropped_samples": sum(r.get("dropped_samples", 0) for r in runs), "telemetry_fields_ok": fields_ok,
           "per_run": [{k: C.rnd(r.get(k)) for k in ("block", "config", "kept", "reason", "rc", "launches", "start_temp",
                                                     "t_early", "p_before", "dyn", "switching", "dropped_samples",
                                                     "mhz_min", "mhz_max", "cycles_per_op", "results", "per_s", "heats",
                                                     "preheat_reached", "kept_busy", "reason_busy", "busy_mhz_min",
                                                     "busy_mhz_max", "idle_state", "idle_mv", "busy_mv",
                                                     "idle_mhz_start")} for r in runs]}
    note = (f"runs {len(runs)} kept {len(kept)} (busy rule {len(kept_busy)}) failed {len(failed)} off600 {len(off)}"
            f" busy-off600 {len(off_busy)} gaps {len(gaps)} dropouts {out['dropped_samples']}"
            f" idle-mhz {','.join(f'{k}:{v}' for k, v in sorted(idle_states.items())) or '-'}")
    if failed:
        note += " failed=" + ",".join(out["failed"])
    if off:
        note += " off600=" + ("all" if len(off) == len(runs) else ",".join(out["off600"]))
    if off_busy:
        note += " busy-off600=" + ",".join(out["off600_busy"])
    chk_bad = []
    if a.smoke:
        note += f" fields {'ok' if fields_ok else 'MISSING'}"
        for r in runs:
            if r.get("test") == "fma":
                note += f" {r['config']}:{r.get('cycles_per_op', 0):.3f}c/{'/'.join(r.get('results', []))}"
            # *_chk_* runs (ablb smoke: --b-stream on the default small-integer operands) exist to have the host
            # check the results: at least one launch must be checked ("both", "math" or "prm-literal"; the long
            # timed fp16 launches pass 2^24 and print "unchecked", the calibration launch does not) and none "wrong"
            if "_chk_" in str(r.get("config")):
                res = set(r.get("results", []))
                if "wrong" in res or not res & {"both", "math", "prm-literal"}:
                    chk_bad.append(r["config"])
        if chk_bad:
            note += " CHECK-FAILED=" + ",".join(chk_bad)
    out["check_failed"] = chk_bad
    json.dump(out, open(os.path.join(a.dir, "check.json"), "w"), indent=1)
    print(note)
    bad = len(failed) > a.max_failed or not runs or (a.smoke and (failed or not fields_ok or chk_bad))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
