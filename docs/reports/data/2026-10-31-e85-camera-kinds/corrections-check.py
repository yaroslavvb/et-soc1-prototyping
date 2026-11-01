#!/usr/bin/env python3
"""E85: the desk check behind the corrections after verification (Sat 31 Oct 2026). No verdict moves.

    cd docs/reports/data/2026-10-31-e85-camera-kinds && python3 corrections-check.py > corrections-check.txt

Prints every number the README's "Corrections after verification" quotes, from committed files only: this folder's
session/, analysis/, pre/, dry/ and posthoc/, plus four files elsewhere in the repo (tools/ettelem/ettelem.cpp,
tools/claims-v3/tel/README.md, tools/claims-v3/hlk/README.md, and E80's and E83's data READMEs). Standard library
only. It changes nothing: the registered outputs (analysis/score.json, lockin.json, dips.json) are read, and their
sha256 are printed first so they can be compared with the data commit cf9eba15.
"""
import bisect
import gzip
import hashlib
import json
import math
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))


def p(*a):
    print(*a)


def rel(*parts):
    return os.path.join(HERE, *parts)


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def grep(path, needle, width=200):
    out = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if needle in line:
                out.append(f"{os.path.relpath(path, REPO)}:{i}: {line.strip()[:width]}")
    return out


def binom_tail(k, n, q):
    return sum(math.comb(n, i) * q ** i * (1 - q) ** (n - i) for i in range(k, n + 1))


def fisher_greater(a, b, c, d):
    n1, n2, k = a + b, c + d, a + c
    return sum(math.comb(n1, i) * math.comb(n2, k - i) for i in range(a, min(n1, k) + 1)) / math.comb(n1 + n2, k)


def load_tel():
    rows = []
    with gzip.open(rel("session", "tel.jsonl.gz"), "rt") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if "since_reset_ms" not in d or not isinstance(d.get("mhz"), dict):
                continue
            rows.append(dict(t=d["t_ms"] / 1000.0, took=d.get("took_ms"), since=d["since_reset_ms"],
                             mhz=d["mhz"].get("minion")))
    return rows


def config_line(path):
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line.startswith("{") and "tdp_w" in line:
            return json.loads(line)
    return None


def main():
    score = json.load(open(rel("analysis", "score.json")))
    lockin = json.load(open(rel("analysis", "lockin.json")))
    dips = next(iter(json.load(open(rel("analysis", "dips.json"))).values()))
    sess = json.load(open(rel("session", "session.json")))
    la = [json.loads(l) for l in open(rel("session", "launches.jsonl")) if l.strip()]
    tel = load_tel()

    p("E85 corrections after verification: the desk check (Sat 31 Oct 2026). No number in the registered outputs")
    p("changes and no verdict moves; their sha256 (compare with the data commit cf9eba15):")
    for f in ("analysis/score.json", "analysis/lockin.json", "analysis/dips.json"):
        p(f"   {sha(rel(*f.split('/')))}  {f}")
    p()

    # ---------------------------------------------------------------- C1
    p("C1 (major). THE ONE WRITE: THE SAMPLER'S STATISTICS RESET")
    p(f"   session/session.json sampler.args: {sess['sampler']['args']!r}")
    for g in grep(os.path.join(REPO, "tools", "ettelem", "ettelem.cpp"), "0x47"):
        p("   " + g)
    for g in grep(os.path.join(REPO, "tools", "ettelem", "ettelem.cpp"), "DM_CMD_SET_STATS_RUN_CONTROL"):
        p("   " + g)
    drops = [i for i in range(1, len(tel)) if tel[i]["since"] < tel[i - 1]["since"]]
    dset = set(drops)
    span = tel[-1]["t"] - tel[0]["t"]
    waits = [(tel[i]["t"] - tel[i - 1]["t"]) * 1000.0 - tel[i - 1]["took"] for i in drops
             if isinstance(tel[i - 1]["took"], (int, float))]
    sleeps = [(tel[i]["t"] - tel[i - 1]["t"]) * 1000.0 - tel[i - 1]["took"] for i in range(1, len(tel))
              if i not in dset and isinstance(tel[i - 1]["took"], (int, float))]
    p(f"   session/tel.jsonl.gz: {len(tel)} samples over {span:.1f} s; resets seen as a drop in since_reset_ms: "
      f"{len(drops)}, plus the one ettelem sends when it starts; one per {span / len(drops):.3f} s")
    q = sorted(waits)
    p(f"   end of a reset sample's reads to the next sample: median {st.median(q):.0f} ms (10-90% {q[len(q) // 10]:.0f}-"
      f"{q[9 * len(q) // 10]:.0f}), which holds the reset call; after a sample with no reset: median "
      f"{st.median(sleeps):.0f} ms (the sleep to the next 100 ms tick). The next sample's since_reset_ms reads <= 10 ms "
      f"after {sum(1 for i in drops if tel[i]['since'] <= 10)} of {len(drops)} resets: the call outlasts the tick.")
    c0, c1 = config_line(rel("pre", "e85-config-start.txt")), config_line(rel("pre", "e85-config-end.txt"))
    p(f"   pre/e85-config-start.txt: {json.dumps(c0)}")
    p(f"   pre/e85-config-end.txt:   {json.dumps(c1)}")
    p("   So no governor, TDP, threshold or clock was set (both reads equal); the statistics reset is the one write.")
    for g in grep(os.path.join(REPO, "tools", "claims-v3", "tel", "README.md"), "switches the SP stats trace off"):
        p("   " + g)
    for g in grep(os.path.join(REPO, "tools", "claims-v3", "kspeed", "README.md"), "restarts the PMIC's running average"):
        p("   " + g)
    p()

    # ---------------------------------------------------------------- C2
    p("C2 (major). THE CAMERA'S DRIFT: WHAT E85 ALONE SAYS")
    rl = score["reference_line"]
    m, sm, sl, ssl = rl["mag_at_mid"], rl["se_mag_at_mid"], rl["slope_mk_per_w_per_s"], rl["se_slope"]
    for pt in rl["points"]:
        p(f"   {pt['block']}: |H| {pt['mag']:.2f} +- {pt['se_mag']:.2f} mK/W at t {pt['t_s']:.0f} s")
    p(f"   registered line: {m:.2f} +- {sm:.2f} mK/W at mid-time, slope {100 * sl * 3600 / m:+.1f} +- "
      f"{100 * ssl * 3600 / m:.1f} %/h (z {sl / ssl:+.2f}), chi2 {rl['chi2']:.2f}/{rl['dof']}  [score.json reference_line]")
    w = [1.0 / pt["se_mag"] ** 2 for pt in rl["points"]]
    c = sum(wi * pt["mag"] for wi, pt in zip(w, rl["points"])) / sum(w)
    sc = 1.0 / math.sqrt(sum(w))
    chi2c = sum(((pt["mag"] - c) / pt["se_mag"]) ** 2 for pt in rl["points"])
    p(f"   a constant (no drift) through the same three: {c:.2f} +- {sc:.2f} mK/W, chi2 {chi2c:.2f}/2")
    kinds = score["kinds"]
    main = [k for k in ("E85-F32", "E85-I8", "E85-F16") if k in kinds]
    rows = {}
    for k in main:
        x = kinds[k]
        R, so, sr = x["H_mk_per_w"] / c, x["se_H"] / c, x["H_mk_per_w"] * sc / c ** 2
        rows[k] = (R, so, sr)
        p(f"   {k} against the constant: R {R:.3f} +- {math.hypot(so, sr):.3f}; registered (the line) "
          f"{x['ratio_R']:.3f} +- {x['se_R']:.3f}")
    wo = {k: 1.0 / rows[k][1] ** 2 for k in main}
    Rp = sum(wo[k] * rows[k][0] for k in main) / sum(wo.values())
    se_p = math.hypot(1.0 / math.sqrt(sum(wo.values())), sum(wo[k] * rows[k][2] for k in main) / sum(wo.values()))
    p(f"   pooled against the constant (lockin_hlk.py's pooling): {Rp:.3f} +- {se_p:.3f}; registered "
      f"{score['rules']['E85-R3_pooled']['R_pooled']:.3f} +- {score['rules']['E85-R3_pooled']['se']:.3f}")
    p()

    # ---------------------------------------------------------------- C3
    p("C3. INT8: NOT DETECTED, SO ITS OTHER PASSES CARRY NO INFORMATION")
    for r in ("E85-R1_seen", "E85-R2_heat_follows_watts", "E85-R4_same_lag", "E85-R9_absolute"):
        p(f"   {r}[E85-I8]: {json.dumps(score['rules'][r]['E85-I8'])}")
    t2 = score["rules"]["E85-R2_heat_follows_watts"]["E85-I8"]["tolerance"]
    p(f"   R2's tolerance {t2:.3f} >= 1.0: an R of 2.0 (|R - 1| = 1.0) would also have passed")
    for g in grep(os.path.join(REPO, "tools", "claims-v3", "hlk", "README.md"), "near 0.13"):
        p("   " + g)
    p(f"   measured SE_R {kinds['E85-I8']['se_R']:.3f} = {kinds['E85-I8']['se_R'] / 0.145:.1f}x the registered 0.13-0.15")
    p()

    # ---------------------------------------------------------------- C4
    p("C4. 'FULL-CARD EQUIVALENTS' ARE A LINEAR x1024/192 SCALING, NOT A FULL-CARD MEASUREMENT")
    for k in ("E85-F32", "E85-F16", "E85-I8", "E85-SP90"):
        x = kinds[k]
        e, pr = x["board_step_full_card_equiv_w"], x["predicted_full_card_step_w"]
        p(f"   {k}: {x['board_step_w']:.3f} W x 1024/192 = {e:.2f} W; E80/E83 p800 difference {pr:.2f} W "
          f"({100 * (e / pr - 1):+.1f}%)")
    p()

    # ---------------------------------------------------------------- C5
    p("C5. THE CAMERA-READ WATTS ARE R RESTATED IN WATTS (calibrated on the reference rung's metered watts)")
    B = lockin["blocks"]
    refs = [b for b in ("E85-REF1", "E85-REF2", "E85-REF3")]
    fps = st.mean(B[r]["power"]["amp"] / B[r]["board_step_w"]["mean"] for r in refs)
    for k in ("E85-F32", "E85-F16", "E85-I8"):
        x = kinds[k]
        restated = x["ratio_R"] * x["board_fundamental_w"] / fps
        p(f"   {k}: camera_read_step_w {x['camera_read_step_w']:.4f}; R x (kind's fundamental) / (references' "
          f"fundamental per W of step, {fps:.4f}) = {restated:.4f}")
    p()

    # ---------------------------------------------------------------- C6
    p("C6. THE FIRMWARE")
    for g in grep(rel("pre", "e85-manifest.txt"), "et_soc1"):
        p("   " + g)
    p("   (the manifest and both config reads carry no firmware version)")
    for d in ("2026-10-31-e80-kinds-speed", "2026-10-31-e83-kinds-speed-rest"):
        for g in grep(os.path.join(HERE, "..", d, "README.md"), "BL2 0.22.0"):
            p("   " + g)
    p()

    # ---------------------------------------------------------------- C7
    p("C7. NO SMOKE RUN: DRY RUN, THEN THE OPERAND CHECK, THEN THE REGISTERED SESSION")
    dry = [l.strip() for l in open(rel("dry", "run.log")) if l.strip()]
    plan = [l for l in dry if " plan: " in l]
    p(f"   dry/run.log: {plan[0][:90] if plan else dry[0][:8]} ... {dry[-1][:90]}")
    tc = json.load(open(rel("pre", "tiles", "tile_check.json")))
    p(f"   pre/tiles/tile_check.json: {len(tc['rows'])} sets, one --seconds 0 launch each, wall "
      f"{sum(r['wall_s'] for r in tc['rows']):.2f} s in all, failures {tc['failures']}")
    sl0 = [l.strip() for l in open(rel("session", "run.log")) if l.strip() and " plan: " in l]
    p(f"   session/run.log: {sl0[0][:100]}")
    p()

    # ---------------------------------------------------------------- C8
    p("C8. SMALL NUMBERS")
    for k in ("E85-F32", "E85-F16", "E85-I8"):
        r = B[k]["roi"]
        pl = B[k]["per_lap"]["roi"]
        ph = math.atan2(r["Z_im"], r["Z_re"])
        along = [re * math.cos(ph) + im * math.sin(ph) for re, im in pl]
        p(f"   {k}: per-lap scatter along the phase, SE x sqrt(laps) {r['se_along'] * math.sqrt(r['n_laps']):.0f} mK "
          f"(weighted, what sets the SE); unweighted sd {st.stdev(along):.0f} mK; {r['n_laps']} laps")
    p(f"   E85-I8 camera_read_step_w {kinds['E85-I8']['camera_read_step_w']:.5f} -> 1.79")
    p(f"   session.json caps.max_card_min {sess['caps']['max_card_min']}; card_s {sess['card_s']} = "
      f"{sess['card_s'] / 60:.1f} min")
    p()

    # ---------------------------------------------------------------- C9
    p("C9 (found while fixing C1; post hoc, no verdict). THE CLOCK EXCURSIONS AND THE RESETS")
    rows_t = [r["t"] for r in tel]
    late = {d["n"] for d in dips["dips"] if d["onset_s"] < 2.0}
    mid = [d for d in dips["dips"] if d["onset_s"] >= 2.0]
    base = sum(1 for r in tel if r["since"] <= 110) / len(tel)
    p(f"   dips.json: {dips['launches_with_dip']} of {dips['launches']} launches; {len(late)} late ramps (onset < 2 s), "
      f"{len(mid)} mid-launch idle-reset dips; share of all samples with since_reset_ms 0 or 100: {base:.3f}")
    tab = {True: [0, 0], False: [0, 0]}
    for L in la:
        t0, t1 = L["t_start_ms"] / 1000.0, L["t_end_ms"] / 1000.0
        j = bisect.bisect_left(rows_t, t0 + 1.5)
        if j < len(tel) and tel[j]["t"] <= t1:
            tab[tel[j]["since"] <= 110][0 if L["n"] in late else 1] += 1
    a, b = tab[True]
    cc, dd = tab[False]
    p(f"   late ramps: {a} of {a + b} launches whose 1.5 s check sample came right after a reset (since_reset_ms 0 or "
      f"100), against {cc} of {cc + dd} otherwise; one-sided Fisher exact p {fisher_greater(a, b, cc, dd):.1e}")
    hits = 0
    for d in mid:
        L = next(x for x in la if x["n"] == d["n"])
        j = bisect.bisect_left(rows_t, L["t_start_ms"] / 1000.0 + d["onset_s"] - 0.05)
        hits += tel[j]["since"] <= 110
        p(f"   mid-launch dip, launch {d['n']} ({d['block']}, {d['set']}), onset {d['onset_s']:.2f} s: since_reset_ms "
          f"{tel[j]['since']}, the sampler's command took {tel[j]['took']} ms (median {dips['sampler_took_ms_median']})")
    p(f"   {hits} of {len(mid)} mid-launch dips began right after a reset: P(>= {hits} of {len(mid)} | {base:.3f}) = "
      f"{binom_tail(hits, len(mid), base):.3f} (the 0-or-100 window was chosen after seeing the data)")
    p("   Reading: suggestive only. A run of the same design without --reset-ms would decide it. The excursions sit")
    p("   in both arms and inside the board power that feeds every H, and R8 (hold) passed in every block.")


if __name__ == "__main__":
    main()
