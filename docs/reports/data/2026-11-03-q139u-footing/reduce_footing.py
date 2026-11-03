#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Q139(u): one reduction footing for the kinds loop at 600 MHz (FOOTING-RULE.md, committed d4c36bfe before any row was
re-read). Later lanes import this module:

    import reduce_footing as RF
    RF.K_FROZEN["a3"], RF.K_FROZEN["c1"]           # the frozen per-card leakage slopes (W/C), read from footing.json
    RF.drop_dips(records)                          # E82 A2: (kept records, dropped indices)
    RF.filtered_copy(src_pass_dir, dst_pass_dir)   # a pass directory with A2's dips removed from its telemetry
    RF.reduce(exp, k, out_dir, scratch)            # the experiment's own registered reducer, unchanged, at slope k, dips per F2
    RF.rests_from_csv(csv_path)                    # the valid idle rests of one reduction's runs.csv (F1)
    RF.fit_slope(rests)                            # OLS with one intercept per pass, one slope; bootstrap over passes

    python3 reduce_footing.py rests  <scratch>      # stage A: every experiment reduced at k = 0 (dips per F2) -> rests -> footing.json
    python3 reduce_footing.py reduce <scratch>      # stage B: every experiment reduced at its card's frozen k -> reduced/<exp>.json

F1: k_c = the within-pass slope of the idle bracket's board W on its die reading (the reducer's own [t0-1.2 s, t0-0.2 s)
bracket, valid by its idle test, the run passing every per-run gate), pooled over every pass of every session on card c.
F2: E82 A2's dip rule on every pass (board_w[i] < min(board_w[i-2], board_w[i+2]) - 4.0 W), before anything reads it.
F3: every experiment's registered reducer unchanged otherwise (gates, zeros interpolation, D = p80 - Zhat(t0), statistics).
Wrappers whose registered primary already applies A2 (built in) run on the committed pass directories unchanged; wrappers
with an A2 flag run with --drop-dips; reducers with no dip handling run on A2-filtered copies. A2 is applied exactly once.
"""
import csv
import gzip
import json
import os
import random
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DD = os.path.join(ROOT, "docs", "reports", "data")
CV = os.path.join(ROOT, "tools", "claims-v3")
DIP_W = 4.0
FOOTING = os.path.join(HERE, "footing.json")

# exp: (data dir, card, wrapper under tools/claims-v3, dips: builtin | flag | copy)
EXPS = {
    "E78": ("2026-10-31-e78-kinds-energy-matrix", "a3", "kinds/reduce_e78.py", "copy"),
    "E82": ("2026-10-31-e82-kinds-aifoundry1", "c1", "kinds/reduce_e82.py", "copy"),
    "E86": ("2026-10-31-e86-real-tensors-energy", "a3", "kinds/reduce_e86.py", "copy"),
    "E88": ("2026-10-31-e88-result-path", "c1", "rpath/reduce_e88.py", "builtin"),
    "E90": ("2026-10-31-e90-signs-spread", "a3", "kinds/reduce_e90.py", "copy"),
    "E91": ("2026-10-31-e91-real-tensors-aifoundry1", "c1", "kinds/reduce_e91.py", "builtin"),
    "E92": ("2026-11-01-e92-sign-split", "a3", "kinds/reduce_e92.py", "copy"),
    "E93": ("2026-11-01-e93-zero-gate-silicon", "c1", "kinds/reduce_e93.py", "builtin"),
    "E94": ("2026-11-01-e94-tile-spread", "c1", "kinds/reduce_e94.py", "builtin"),
    "E95": ("2026-11-01-e95-real-tensors-energy", "a3", "kinds/reduce_e95.py", "copy"),
    "E102": ("2026-11-01-e102-balanced-bit-prices", "c1", "kinds/reduce_e102.py", "builtin"),
    "E103": ("2026-11-01-e103-model-blind-test", "c1", "kinds/reduce_e103.py", "builtin"),
    "E104": ("2026-11-01-e104-c-readback", "c1", "kinds/reduce_e104.py", "builtin"),
    "E106": ("2026-11-01-e106-held-signs", "c1", "kinds/reduce_e106.py", "builtin"),
    "E108": ("2026-11-01-e108-sign-located", "c1", "signloc/reduce_e108.py", "builtin"),
    "E115": ("2026-11-01-e115-blind-pool", "a3", "e115/reduce_e115.py", "flag"),
    "E121": ("2026-11-01-e121-zero-gate-replicate", "a3", "kinds/reduce_e93.py", "builtin"),
    "E122": ("2026-11-01-e122-signs-replicate", "a3", "signloc/reduce_e108.py", "builtin"),
    "E123": ("2026-11-01-e123-tile-spread-rest", "a3", "e123/reduce_e123.py", "builtin"),
    "E127": ("2026-11-02-e127-b-gate", "a3", "e127/reduce_e127.py", "flag"),
    "E128": ("2026-11-02-e128-fp16-signs", "c1", "e128/reduce_e128.py", "builtin"),
    "E131": ("2026-11-02-e131-real-tiles-card1", "c1", "e131/reduce_e131.py", "builtin"),
    "E137": ("2026-11-02-e137-fp16-sign-rest", "c1", "e137/reduce_e137.py", "builtin"),
    "E140": ("2026-11-02-e140-blind4", "a3", "e140/reduce_e140.py", "flag"),
    "E141": ("2026-11-02-e141-blind5-aifoundry3", "a3", "e141/reduce_e141.py", "flag"),
    "E142": ("2026-11-02-e142-blind5-card1", "c1", "e142/reduce_e142.py", "builtin"),
}


def _load_frozen():
    try:
        return {c: v["k_w_per_c"] for c, v in json.load(open(FOOTING))["slopes"].items()}
    except (OSError, ValueError, KeyError):
        return {}


K_FROZEN = _load_frozen()


def drop_dips(records):
    """E82 A2: drop sample i when board_w[i] < min(board_w[i-2], board_w[i+2]) - 4 W. Returns (kept, dropped indices)."""
    B = [r.get("board_w") for r in records]
    bad = set()
    for i in range(2, len(records) - 2):
        if None not in (B[i], B[i - 2], B[i + 2]) and B[i] < min(B[i - 2], B[i + 2]) - DIP_W:
            bad.add(i)
    return [r for i, r in enumerate(records) if i not in bad], sorted(bad)


def _tel_path(d):
    for nm in ("telemetry.jsonl", "telemetry.jsonl.gz"):
        if os.path.exists(os.path.join(d, nm)):
            return os.path.join(d, nm)
    return None


def filtered_copy(src, dst):
    """Copy a pass directory, its telemetry rewritten (gzip) without A2's dip samples. Returns the number dropped."""
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)
    for f in os.listdir(src):
        if f.startswith("telemetry.jsonl"):
            continue
        s = os.path.join(src, f)
        (shutil.copytree if os.path.isdir(s) else shutil.copy2)(s, os.path.join(dst, f))
    p = _tel_path(src)
    op = gzip.open if p.endswith(".gz") else open
    lines = [ln for ln in op(p, "rt") if ln.startswith("{")]
    recs = []
    for ln in lines:
        try:
            recs.append(json.loads(ln))
        except ValueError:
            recs.append({})
    _, bad = drop_dips(recs)
    bad = set(bad)
    with gzip.open(os.path.join(dst, "telemetry.jsonl.gz"), "wt") as g:
        for i, ln in enumerate(lines):
            if i not in bad:
                g.write(ln if ln.endswith("\n") else ln + "\n")
    return len(bad)


def pass_dirs(exp):
    """The committed copies of the pass directories the experiment's primary reduction read (its JSON's `dirs`)."""
    ddir = os.path.join(DD, EXPS[exp][0])
    prim = json.load(open(os.path.join(ddir, exp.lower() + ".json")))
    want = [os.path.basename(x.rstrip("/")) for x in prim["dirs"]]
    found = {}
    for dp, dn, fn in os.walk(ddir):
        if any(f.startswith("telemetry.jsonl") for f in fn) and os.path.basename(dp) in want:
            found.setdefault(os.path.basename(dp), dp)
    missing = [w for w in want if w not in found]
    return [found[w] for w in want if w in found], missing


def reduce(exp, k, out_dir, scratch, tag):
    """Run the experiment's registered reducer, unchanged, at leakage slope k with A2 applied once. Returns paths."""
    ddir, card, wrapper, dips = EXPS[exp]
    dirs, missing = pass_dirs(exp)
    if missing:
        raise SystemExit(f"{exp}: pass dirs not committed: {missing}")
    ndrop = {}
    if dips == "copy":
        cdirs = []
        for d in dirs:
            c = os.path.join(scratch, "passes", exp, os.path.basename(d))
            if not os.path.exists(os.path.join(c, "telemetry.jsonl.gz")):
                ndrop[os.path.basename(d)] = filtered_copy(d, c)
            cdirs.append(c)
        dirs = cdirs
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{exp.lower()}-{tag}.json")
    csvp = os.path.join(scratch, "csv", f"runs-{exp.lower()}-{tag}.csv")
    txt = os.path.join(scratch, "txt", f"reduce-{exp.lower()}-{tag}.txt")
    os.makedirs(os.path.dirname(csvp), exist_ok=True)
    os.makedirs(os.path.dirname(txt), exist_ok=True)
    cmd = [sys.executable, os.path.join(CV, wrapper), *dirs, "--out", out, "--csv", csvp, "--txt", txt,
           "--leak", repr(float(k)), "--no-refit"] + (["--drop-dips"] if dips == "flag" else [])
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    log = os.path.join(scratch, "txt", f"reduce-{exp.lower()}-{tag}.log")
    open(log, "w").write(" ".join(os.path.relpath(c, ROOT) if c.startswith(ROOT) else c for c in cmd) + "\n"
                         + r.stdout[-4000:] + "\n" + r.stderr[-4000:])
    return {"exp": exp, "card": card, "k": k, "rc": r.returncode, "out": out, "csv": csvp, "log": log,
            "dips": dips, "copy_dropped": ndrop, "n_dirs": len(dirs)}


def rests_from_csv(path, exp):
    """F1's rests: the idle bracket of every run valid by the reducer's idle test whose run passed every per-run gate."""
    out = []
    for row in csv.DictReader(open(path)):
        if row.get("idle_ok") != "True" or (row.get("fail_reasons") or "") != "":
            continue
        try:
            p, t = float(row["p_idle"]), float(row["t_idle"])
        except (TypeError, ValueError):
            continue
        out.append({"exp": exp, "pass": f"{exp}:{row['pass']}", "p": p, "t": t})
    return out


def _slope(groups):
    sxy = sxx = 0.0
    for g in groups:
        if len(g) < 2:
            continue
        mt = sum(r["t"] for r in g) / len(g)
        mp = sum(r["p"] for r in g) / len(g)
        for r in g:
            sxy += (r["t"] - mt) * (r["p"] - mp)
            sxx += (r["t"] - mt) ** 2
    return (sxy / sxx if sxx > 0 else None), sxx


def fit_slope(rests, draws=2000, seed=139):
    by = {}
    for r in rests:
        by.setdefault(r["pass"], []).append(r)
    groups = list(by.values())
    k, sxx = _slope(groups)
    rng = random.Random(seed)
    bs = []
    for _ in range(draws):
        s, _ = _slope([groups[rng.randrange(len(groups))] for _ in groups])
        if s is not None:
            bs.append(s)
    bs.sort()
    resid = []
    for g in groups:
        mt = sum(r["t"] for r in g) / len(g)
        mp = sum(r["p"] for r in g) / len(g)
        resid += [(r["p"] - mp) - k * (r["t"] - mt) for r in g]
    sd_t = (sxx / max(len(rests) - len(groups), 1)) ** 0.5
    return {"k_w_per_c": k, "ci95_bootstrap_passes": [bs[int(0.025 * len(bs))], bs[int(0.975 * len(bs)) - 1]],
            "se_bootstrap": (sum((x - sum(bs) / len(bs)) ** 2 for x in bs) / (len(bs) - 1)) ** 0.5,
            "n_rests": len(rests), "n_passes": len(groups), "within_pass_sd_t_c": sd_t,
            "t_range_c": [min(r["t"] for r in rests), max(r["t"] for r in rests)],
            "resid_rms_w": (sum(e * e for e in resid) / max(len(resid) - len(groups) - 1, 1)) ** 0.5,
            "by_experiment": {e: _slope([g for g in groups if g[0]["exp"] == e])[0]
                              for e in sorted({r["exp"] for r in rests})}}


def _run_all(k_of, scratch, tag, jobs=6):
    out_dir = os.path.join(scratch, "stage-" + tag) if tag == "k0" else os.path.join(HERE, "reduced")
    with ThreadPoolExecutor(max_workers=jobs) as ex:
        res = list(ex.map(lambda e: reduce(e, k_of(e), out_dir, scratch, tag), EXPS))
    return res


def main():
    stage, scratch = sys.argv[1], os.path.abspath(sys.argv[2])
    if stage == "rests":
        res = _run_all(lambda e: 0.0, scratch, "k0")
        bad = [r for r in res if r["rc"] != 0]
        rests = {"a3": [], "c1": []}
        for r in res:
            if r["rc"] == 0:
                rests[r["card"]] += rests_from_csv(r["csv"], r["exp"])
        slopes = {c: fit_slope(v) for c, v in rests.items()}
        doc = {"what": "Q139(u)'s frozen footing (FOOTING-RULE.md, d4c36bfe): F1's per-card leakage slope, F2's dip rule",
               "dip_rule": "E82 A2: drop board_w[i] < min(board_w[i-2], board_w[i+2]) - 4.0 W, every pass, once",
               "slopes": slopes, "reductions_k0": [{k: v for k, v in r.items() if k not in ("out", "csv", "log")} for r in res],
               "failed": [r["exp"] for r in bad]}
        json.dump(doc, open(FOOTING, "w"), indent=1)
        json.dump(rests, open(os.path.join(scratch, "rests.json"), "w"))
        for c, s in slopes.items():
            print(c, json.dumps({k: v for k, v in s.items() if k != "by_experiment"}))
            print("   by experiment", {e: (None if v is None else round(v, 4)) for e, v in s["by_experiment"].items()})
        print("failed:", [(r["exp"], r["log"]) for r in bad])
    elif stage == "reduce":
        K = _load_frozen()
        res = _run_all(lambda e: K[EXPS[e][1]], scratch, "footing")
        json.dump(res, open(os.path.join(scratch, "stage-footing.json"), "w"), indent=1)
        for r in res:
            print(r["exp"], r["card"], r["k"], "rc", r["rc"], r["log"] if r["rc"] else "")
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
