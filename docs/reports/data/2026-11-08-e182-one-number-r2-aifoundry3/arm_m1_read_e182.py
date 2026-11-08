#!/usr/bin/env python3
"""card-e182 (Q156): october-forecast-model's REPORTED arm for E182, read by E182.md.dated-note-M1.md section M1-4's words (that section is
the arm's reader; no code reader is committed). Written by this lane during E182's session on Sun 8 Nov 2026, before any E182 datum was
read at the desk; it imports e182_stats.py unchanged for Spearman's rho (E182-R-int8's statistic).
Usage (from the lab repository's top): python3 -B arm_m1_read.py <scored.json> <m1-october-forecast-model-e182.json> <out.json> <out.txt>
Words: inside / above / below the interval; the estimate's sign or the other; rho with its n. Never a verdict word, never an E182 rule.
The model's figures are at the card rail (aifoundry3 0.522 V, the export's units); the trains and the kinds passes read the board: nothing
is scaled, and each reading names the column it is set against."""
import json
import os
import statistics
import sys

LAB = os.path.abspath(os.path.join("tools", "claims-v3", "e182"))  # run from the lab repository's top
if not os.path.isfile(os.path.join(LAB, "e182_stats.py")):
    sys.exit("run from the lab repository's top (tools/claims-v3/e182/e182_stats.py not found)")
sys.path.insert(0, LAB)
import e182_stats as S  # noqa: E402  (unchanged: spearman with average ranks for ties)

sc_p, m1_p, out_j, out_t = sys.argv[1:5]
sc = json.load(open(sc_p))
m1 = json.load(open(m1_p))
lines, res = [], {"_what": "october-forecast-model's reported arm for E182, read by E182.md.dated-note-M1.md section M1-4 (reported, never a "
                  "rule)", "scored_json": os.path.basename(sc_p), "m1_json": os.path.basename(m1_p),
                  "column": "model: W at the card rail (the export's units); E182: W at the board", "trains": {}, "split": {},
                  "kinds_passes": {}, "quartet_swaps": {}}


def where(m, iv):
    if iv.get("lo") is None:
        return None
    return "inside" if iv["lo"] <= m <= iv["hi"] else ("above" if m > iv["hi"] else "below")


def sign_word(m, est):
    if est is None or m == 0 or est == 0:
        return "no sign to compare"
    return "the estimate's sign" if (m > 0) == (est > 0) else "the other sign"


lines.append("october-forecast-model's reported arm (E182.md.dated-note-M1.md, M1-4); the model at the card rail, E182 at the board")
lines.append("TRAINS (each covered train's model figure against the train's estimate and 95% interval, e182_stats.py's):")
for pid in ("T1", "T2", "T3", "T4", "T5", "T6"):
    mt = m1["trains"]["trains"][pid]
    iv = sc.get("trains", {}).get(pid, {})
    if not mt.get("scored", True) or "model_w_a3" not in mt:
        res["trains"][pid] = {"read": "not read: the model does not cover this train"}
        lines.append(f"  {pid}: not read (not covered by the model)")
        continue
    if iv.get("lo") is None:
        res["trains"][pid] = {"read": "not read: the scorer reads this train NOT SCORED", "why": iv.get("why")}
        lines.append(f"  {pid}: not read (the train is NOT SCORED: {iv.get('why')})")
        continue
    m = mt["model_w_a3"]
    w, s = where(m, iv), sign_word(m, iv["mean"])
    res["trains"][pid] = {"model_w_card_rail": m, "estimate_w_board": iv["mean"], "lo": iv["lo"], "hi": iv["hi"], "n_units": iv.get("n"),
                          "model_reads": w, "sign": s, "model_minus_estimate_w": m - iv["mean"]}
    lines.append(f"  {pid}: model {m:+.5f} W against {iv['mean']:+.5f} [{iv['lo']:+.5f}, {iv['hi']:+.5f}] W ({iv.get('n')} units): {w}, {s}")

lines.append("THE HELD-BIT SPLIT (the model's beta_A = (T3 - T2) / 14 and beta_B = (T3 + T2) / 14, W a held 1-bit a byte):")
T = m1["trains"]["trains"]
mA = (T["T3"]["model_w_a3"] - T["T2"]["model_w_a3"]) / 14
mB = (T["T3"]["model_w_a3"] + T["T2"]["model_w_a3"]) / 14
for nm, mv, rule, key in (("beta_A", mA, "E182-A", "beta_A"), ("beta_B", mB, "E182-B", "beta_B")):
    r = sc.get("rules", {}).get(rule, {})
    iv = r.get(key, {}) or {}
    if iv.get("lo") is None:
        res["split"][nm] = {"model": mv, "read": f"not read: {rule} NOT SCORED"}
        lines.append(f"  {nm}: model {mv:+.6f}; {rule} NOT SCORED: not read")
        continue
    w, s = where(mv, iv), sign_word(mv, iv["mean"])
    res["split"][nm] = {"model": mv, "estimate": iv["mean"], "lo": iv["lo"], "hi": iv["hi"], "model_reads": w, "sign": s}
    lines.append(f"  {nm}: model {mv:+.6f} against {iv['mean']:+.6f} [{iv['lo']:+.6f}, {iv['hi']:+.6f}]: {w}, {s}")
res["split"]["model_statement"] = m1["held_bit_split"]["export_statement"]
res["split"]["E182-SPLIT_word_beside"] = sc.get("rules", {}).get("E182-SPLIT", {}).get("verdict")
lines.append(f"  the model's own statement: {res['split']['model_statement']}; beside it, E182-SPLIT reads {res['split']['E182-SPLIT_word_beside']}")

lines.append("THE KINDS PASSES (covered int8 kinds the scorer keeps: Spearman rho, average ranks, of the scored figure against the measured D):")
kinds = sc.get("reported", {}).get("kinds", {}) or {}
kept8 = (sc.get("rules", {}).get("E182-R-int8", {}) or {}).get("kinds")
if kept8 is None:
    kept8 = [k for k, v in kinds.items() if k.startswith("int8.") and v.get("c_kept")]
mk = m1["scored"]["kinds"]
cov8 = [k for k in kept8 if k in mk and mk[k].get("w_a3") is not None and k in kinds]
per = {}
for k in sorted(mk):
    if mk[k].get("w_a3") is None or k not in kinds:
        continue
    per[k] = {"model_w_card_rail": mk[k]["w_a3"], "measured_D_w_board": kinds[k]["D_w"], "n_passes": kinds[k].get("n"),
              "model_minus_D_w": mk[k]["w_a3"] - kinds[k]["D_w"], "in_rho": k in cov8}
res["kinds_passes"]["per_kind"] = per
if len(cov8) >= 3:
    rho = S.spearman([mk[k]["w_a3"] for k in cov8], [kinds[k]["D_w"] for k in cov8])
    res["kinds_passes"]["rho"] = rho
    res["kinds_passes"]["n"] = len(cov8)
    lines.append(f"  rho {rho:+.3f}, n {len(cov8)} (of the 12 covered int8 kinds)")
else:
    res["kinds_passes"]["rho"] = None
    res["kinds_passes"]["n"] = len(cov8)
    lines.append(f"  not read: {len(cov8)} covered int8 kinds kept")
for k, v in per.items():
    lines.append(f"  {k}: model {v['model_w_card_rail']:+.4f} - measured {v['measured_D_w_board']:+.4f} = {v['model_minus_D_w']:+.4f} W"
                 f" ({v['n_passes']} passes{'' if v['in_rho'] else '; kind by kind only'})")

lines.append("THE QUARTET SWAPS (the export's two, beside the same kinds' measured D difference; reported only):")
qs = m1["held_bit_split"]["export_central_aifoundry3"]["quartet_swaps"]
for a, b, key in (("int8.e182_a1_b85", "int8.e182_a85_b1", "(1,85)-(85,1)_W"), ("int8.e182_a1_b127", "int8.e182_a127_b1", "(1,127)-(127,1)_W")):
    if a in kinds and b in kinds:
        dm = kinds[a]["D_w"] - kinds[b]["D_w"]
        res["quartet_swaps"][key] = {"model": qs[key], "measured_D_difference_w": dm, "n_passes": [kinds[a].get("n"), kinds[b].get("n")]}
        lines.append(f"  {key}: model {qs[key]:+.5f}; measured D difference {dm:+.5f} W")
    else:
        res["quartet_swaps"][key] = {"model": qs[key], "measured": None}
        lines.append(f"  {key}: model {qs[key]:+.5f}; not measured in the kept passes")
lines.append("Labels: REPORTED, never a rule; the model's figures are modelled (frozen Fri 6 Nov 2026); E182's are blind measurements.")
json.dump(res, open(out_j, "w"), indent=1, sort_keys=True)
open(out_t, "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
