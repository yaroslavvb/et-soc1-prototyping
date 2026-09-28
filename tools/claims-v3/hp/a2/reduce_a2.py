#!/usr/bin/env python3
"""Heat placement, aifoundry2's same-day session (DESIGN2 §3.4-3.5): TRIG-A, TRIG-B, H12. Frozen by PREREG-A2.

    reduce_a2.py --check-pass <attempt dir>                the smoke check of a2/block.sh (the sampler ran, the
                                                           launch ran, the dump parsed)
    reduce_a2.py --data build/claims-v3/aifoundry2/hp/a2 [--out verdicts-a2.json]

TRIG-A, per measured run (not a warm-up; the edge reached; not void), from the 10 Hz --reset-ms 1000 samples after t0
(the heater's own t_start_ms) up to the launch end + 10 s:
  t_up    the first sample at 800 MHz;
  t_hi    the first sample at 800 MHz whose windowed high (minshire[2]) reads >= 66   (the H1' trip);
  t_m     the first sample whose mean (minshire[0]) reads >= 66                        (the H1 trip);
  t_down  the first ONE-POINT down-step, 800 -> 700 MHz (a thermal reduce steps one VMIN-LUT point); a single
          800 -> 600 change is an idle or boot reset and is excluded.
  separating: (a) t_m - t_hi >= 1.5 s, or (b) a rise under a hot max: the high already reads >= 67 at t_up and the
  clock holds 800 MHz for >= 0.5 s.
  fits H1: (a) t_down in [t_m - 0.3, t_m + 1.2] s, or (b); fits H1': (a) t_down in [t_hi - 0.3, t_hi + 1.2] s.
  holds: >= 5 separating runs over >= 2 blocks, >= 80% fit H1 and <= 1 fits H1'; fails: >= 50% fit H1'; else None.
TRIG-B (registered only on an ALIVE probe): sptrace_events.trigb_evaluate (DESIGN2 §3.3) on the session's dumps.
H12 (exploratory, reported): per block ln(min(t_down_PER16@8, 7) / min(t_down_INT16@8, 7)), each placement the mean of
its runs' ln min(t_down, 7).
A WARM attempt (rest >= 66) makes TRIG-A, TRIG-B and H12 NOT OBSERVABLE -> INSUFFICIENT, with the reason.
Outcome words: V3's (card_verdicts) over the one registered card, aifoundry2.
"""
import argparse
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hplib as H  # noqa: E402  (the frozen copy in this directory)
import sptrace_events as SE  # noqa: E402

A2 = json.load(open(os.path.join(HERE, "params-a2.json")))


def check_pass(out):
    tel = H.load_jsonl(os.path.join(out, "tel-smoke.jsonl"))
    hl = H.heater_lines(os.path.join(out, "heater-smoke.out"))
    ok = len(tel) >= 20 and bool(hl)
    lv = None
    sp = os.path.join(out, "sp-smoke.bin")
    if os.path.exists(sp):
        lv = SE.level(SE.events(open(sp, "rb").read()))
    mhz = sorted({(s.get("mhz") or {}).get("minion") for s in tel if s.get("mhz")})
    print("smoke: %d samples, %d heater lines, clocks %s MHz, SP dump level %s" % (len(tel), len(hl), mhz, lv))
    return 0 if ok and lv is not None else 1


def trig_a_run(tel, t0, t_end):
    P = A2["trigA"]
    S = sorted((s for s in tel if s.get("t_ms") and t0 <= s["t_ms"] <= t_end + 10000), key=lambda s: s["t_ms"])
    f = [(s["t_ms"], s["temp_c"]["minshire"][0], s["temp_c"]["minshire"][2], (s.get("mhz") or {}).get("minion"))
         for s in S if (s.get("temp_c") or {}).get("minshire")]
    t_up = next((x for x in f if x[3] == 800), None)
    t_hi = next((x[0] for x in f if x[3] == 800 and x[2] >= 66), None)
    t_m = next((x[0] for x in f if x[1] >= 66), None)
    t_down = None
    excluded = []
    for a, b in zip(f, f[1:]):
        if a[3] == 800 and b[3] == 700:
            t_down = b[0]; break
        if a[3] == 800 and b[3] == 600:
            excluded.append(b[0])
    r = {"t0": t0, "t_up": t_up and t_up[0], "t_hi": t_hi, "t_m": t_m, "t_down": t_down, "excluded_800_600": excluded,
         "mhz_seen": sorted({x[3] for x in f if x[3]})}
    sep_a = t_m is not None and t_hi is not None and (t_m - t_hi) >= P["sep_tm_minus_thi_s"] * 1000
    sep_b = False
    if t_up is not None and t_up[2] >= P["rise_under_hot_high_c"]:
        held = [x for x in f if x[0] >= t_up[0]]
        end800 = next((x[0] for x in held if x[3] != 800), held[-1][0] if held else t_up[0])
        sep_b = (end800 - t_up[0]) >= P["rise_hold_s"] * 1000
    r.update(separating_a=sep_a, separating_b=sep_b, separating=sep_a or sep_b)
    lo, hi = P["fit_lo_s"] * 1000, P["fit_hi_s"] * 1000
    f1 = sep_b or (sep_a and t_down is not None and t_m + lo <= t_down <= t_m + hi)
    f1p = sep_a and t_down is not None and t_hi + lo <= t_down <= t_hi + hi
    r.update(fits_H1=bool(f1), fits_H1p=bool(f1p))
    r["t_down_s"] = (t_down - t0) / 1000.0 if t_down is not None else None
    return r


def reduce_all(data):
    atts = []
    for d in sorted(glob.glob(os.path.join(data, "p*"))):
        a = H.load_json(os.path.join(d, "a2.json"))
        if a:
            atts.append((d, a))
    out = {"card": "aifoundry2", "attempts": [dict(a, dir=os.path.basename(d)) for d, a in atts], "items": {},
           "aborted_attempts": [os.path.basename(d) for d, a in atts if a.get("branch") == "ABORTED"]}   # never used
    session = next(((d, a) for d, a in atts if a.get("branch") in ("COOL", "COOL-", "MARGINAL")), None)
    if session is None:
        warm = [a for _, a in atts if a.get("branch") == "WARM"]
        why = ("NOT OBSERVABLE: every reading today was >= 66 C (%s): the governor sits in its thermal loop at the "
               "600 MHz bottom point (TPM:2316-2360; firmware.md:189-194), so no clock step can be provoked" %
               ", ".join("%s C" % a.get("rest_c") for a in warm)) if warm else "no session data"
        doc = None
        for d, a in atts:
            tel = H.load_jsonl(os.path.join(d, "tel-doc.jsonl"))
            if tel:
                doc = {"mhz_seen": sorted({(s.get("mhz") or {}).get("minion") for s in tel if s.get("mhz")}),
                       "mean_min": min(s["temp_c"]["minshire"][0] for s in tel), "samples": len(tel),
                       "expected": "600 MHz throughout, mean >= 66"}
        for k in ("TRIG-A", "TRIG-B", "H12"):
            out["items"][k] = {"holds": None, "outcome": "INSUFFICIENT", "reason": why}
        out["items"]["H12"]["outcome"] = "reported (not observable)"
        out["documentation_run"] = doc
        return out
    d, a = session
    runs = H.load_jsonl(os.path.join(d, "runs.jsonl"))
    tests, h12 = [], {}
    samples, meas = [], []
    for r in runs:
        idx = r["idx"]
        tel = H.load_jsonl(os.path.join(d, "tel-%s.jsonl" % idx))
        hl = H.heater_lines(os.path.join(d, "heater-%s.out" % idx))
        samples += [(s["t_ms"], s["temp_c"]["minshire"][0], s["temp_c"]["minshire"][2]) for s in tel
                    if s.get("t_ms") and (s.get("temp_c") or {}).get("minshire")]
        if r.get("role") != "meas" or not hl:
            continue
        t0 = min(h["t_start_ms"] for h in hl)
        t_end = max(h["t_end_ms"] for h in hl)
        void = []
        if not r.get("edge_ok"):
            void.append("edge not reached")
        if any(x != 0 for x in r.get("rcs", [])):
            void.append("heater rc")
        if r.get("stop"):
            void.append("safety stop %s" % r["stop"])
        ts = [s["t_ms"] for s in tel if s.get("t_ms") and t0 - 2000 <= s["t_ms"] <= t_end]
        if not ts or max((b - c for c, b in zip(ts, ts[1:])), default=9999) > 1000:
            void.append("sampler gap")
        rec = {"idx": idx, "name": r["name"], "block": r.get("a2_block"), "void": void}
        if not void:
            rec.update(trig_a_run(tel, t0, t_end))
            meas.append({"idx": idx, "t0_ms": t0, "t_end_ms": t_end})
            td = rec.get("t_down_s")
            v = math.log(min(td, A2["C_down_s"])) if td is not None and td > 0 else math.log(A2["C_down_s"])
            h12.setdefault(r.get("a2_block"), {}).setdefault(r["name"], []).append(v)
        tests.append(rec)
    anchors = H.session_anchors(d)
    P = A2["trigA"]
    sep = [t for t in tests if t.get("separating")]
    blocks = {t.get("block") for t in sep}
    n1 = sum(t["fits_H1"] for t in sep)
    n1p = sum(t["fits_H1p"] for t in sep)
    if sep and n1p >= P["fails_frac_h1p"] * len(sep):
        holds = False
    elif len(sep) >= P["holds_min_sep_runs"] and len(blocks) >= P["holds_min_blocks"] and n1 >= P["holds_frac_h1"] * len(sep) \
            and n1p <= P["holds_max_h1p"]:
        holds = True
    else:
        holds = None
    out["items"]["TRIG-A"] = {"holds": holds, "outcome": H.card_verdicts({"aifoundry2": holds}, ["aifoundry2"]),
                              "separating_runs": len(sep), "blocks": sorted(b for b in blocks if b is not None),
                              "fit_H1": n1, "fit_H1p": n1p, "runs": tests,
                              "limit": "one day, one room (O3): the >= 3 cool periods of DESIGN.md were removed"}
    probe = H.load_json(os.path.join(d, "probe", "probe.json")) or {}
    cls = probe.get("class")
    if cls in ("ALIVE", "ALIVE_CANDIDATE") and not os.path.exists(os.path.join(d, "sp-idle.bin")):
        out["items"]["TRIG-B"] = {"holds": None, "outcome": "INSUFFICIENT",
                                  "reason": "registered (probe %s) but not tested: the SP log level found at the session "
                                            "start was unknown, so WARNING was not set and no TRIG-B dump was taken" % cls}
    elif cls in ("ALIVE", "ALIVE_CANDIDATE"):
        dumps = [os.path.join(d, "sp-idle.bin")] + [os.path.join(d, "sp-%s.bin" % r["idx"]) for r in runs
                                                     if os.path.exists(os.path.join(d, "sp-%s.bin" % r["idx"]))
                                                     and str(r["idx"]) not in ("smoke", "doc")]
        tb = SE.trigb_evaluate(dumps, sorted(anchors), sorted(samples), meas, candidate=(cls == "ALIVE_CANDIDATE"))
        out["items"]["TRIG-B"] = {"holds": tb.get("holds"), "outcome": H.card_verdicts({"aifoundry2": tb.get("holds")}, ["aifoundry2"]),
                                  "detail": tb}
    else:
        out["items"]["TRIG-B"] = {"holds": None, "outcome": "not registered",
                                  "reason": "probe class %s: TRIG-B is registered only on an ALIVE card (DESIGN2 §3.2)" % cls}
    per_block = {}
    for b, m in h12.items():
        if "PER16@8" in m and "INT16@8" in m:
            per_block[str(b)] = sum(m["PER16@8"]) / len(m["PER16@8"]) - sum(m["INT16@8"]) / len(m["INT16@8"])
    vals = list(per_block.values())
    out["items"]["H12"] = {"outcome": "reported", "per_block": per_block,
                           "range": [min(vals), max(vals)] if vals else None,
                           "note": "exploratory at 128 minions; with at most 2 blocks it is not a test"}
    out["session"] = {"dir": os.path.basename(d), "rest_c": a.get("rest_c"), "branch": a.get("branch"),
                      "S_A2": a.get("S_A2"), "blocks_run": a.get("blocks_run"), "probe_class": cls}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check-pass")
    ap.add_argument("--data")
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.check_pass:
        sys.exit(check_pass(a.check_pass))
    if not a.data:
        ap.error("--data or --check-pass")
    res = reduce_all(a.data)
    s = json.dumps(res, indent=1, default=lambda x: None)
    if a.out:
        open(a.out, "w").write(s + "\n")
    else:
        print(s)


if __name__ == "__main__":
    main()
