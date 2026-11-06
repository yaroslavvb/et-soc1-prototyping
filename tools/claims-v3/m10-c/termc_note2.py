#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q148(c), REGISTRATION.md dated note 2 (the verifier's faults, before any E178 datum): which of E178's 27 float one-number
kinds are new by bytes and which re-measure the term's fit kinds (E178's R3 bridge), the REPORTED split of the entry rule's
statistics on the new kinds with its power, and the post hoc readings the note quotes (the tie against fp32.pi's bytes measured
as a kind row, the kinds whose accumulator cannot move, the jackknife's degrees of freedom).

termc.py is imported unchanged: the registered rule is termc.score_session as committed, and every estimator, interval and the
power are termc's own functions. Nothing here changes a frozen figure.

    python3 -B termc_note2.py selftest [--txt <file>]   # the checks; writes nothing else
    python3 -B termc_note2.py posthoc --out <dir>       # termc-note2.json and termc-note2.txt (the note's figures)
    python3 -B termc_note2.py score --scored <E178 scored.json> [--fit termc-fit.json] [--note2 termc-note2.json] [--out <json>]
                                                        # after E178's data: the registered rule (termc) and the split beside it

Standard library and numpy 1.26. One core. Read-only git calls (ls-tree, cat-file, grep) on a fixed commit. Nothing here
writes outside --out / --txt.
SPDX-License-Identifier: Apache-2.0
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import struct  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from collections import defaultdict  # noqa: E402

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import termc as TC  # noqa: E402  (unchanged: the registered rule, the estimator, the jackknife, the power, the readers)

TOP, DD, E178D, FLOATS = TC.TOP, TC.DD, TC.E178D, TC.FLOATS
FIT = os.path.join(HERE, "termc-fit.json")
NOTE2 = os.path.join(HERE, "termc-note2.json")
SUMS = os.path.join(HERE, "SHA256SUMS")
SCAN_REF = "6b5ad913"  # the term's outputs commit (05:39:33 PST): the tree the term and its verifier read
FOOT = {"E78": os.path.join(DD, "2026-11-03-q139u-footing", "reduced", "e78-footing.json"),
        "E82": os.path.join(DD, "2026-11-03-q139u-footing", "reduced", "e82-footing.json")}
SEP20 = os.path.join(DD, "2026-09-20-power-aifoundry2")
MAIN_CPP = os.path.join(TOP, "workloads", "sparsity", "host", "main.cpp")
# the host's built-in constant kinds (main.cpp, fillValues): every element of A and B the same word; the source line each one rests on
BUILTIN = {("fp32", "zeros"): (0x00000000, 'if (mode == "zeros") return 0.f;'),
           ("fp32", "ones"): (0x3F800000, 'if (mode == "ones") return 1.f;'),
           ("fp32", "twos"): (0x40000000, 'if (mode == "twos") return 2.f;'),
           ("fp32", "pi"): (0x40490FDB, 'if (mode == "pi") return 3.14159274f;'),
           ("fp32", "onebit"): (0x00800000, 'if (mode == "onebit") { const uint32_t b = 0x00800000u;'),
           ("fp16", "zeros"): (0x00000000, 'if (mode == "zeros") { f = 0.f; q = 0; }'),
           ("fp16", "ones"): (0x3C003C00, 'else if (mode == "ones") { f = 1.f; q = 1; }')}
EXPECT_BRIDGE = {"fp32.ones": (9, 9), "fp32.neg_ones": (2, 2), "fp16.ones": (10, 10), "fp16.neg_ones": (2, 2)}
EXPECT_NEW = {"fp32": 12, "fp16": 11}
EXPECT_STILL_FIT = {"fp32": {"fp32.nz_both", "fp32.dn1_both"}, "fp16": {"fp16.nz_both", "fp16.c_cancel"}}
EXPECT_STILL_E178 = {"fp32.e178_uf"}
# every committed data directory that names 'twos' (git grep -w at SCAN_REF), and what it is: only E7 and E8 measured it on this chip
EXPECT_TWOS_DIRS = {
    "docs/reports/data/2026-09-20-power-aifoundry2": "E7 and E8, this chip: aifoundry2, the fp32 TensorFMA, 20 Sep 2026 (superseded by E9)",
    "docs/reports/data/2026-10-31-q130-literature": "text: Horace He's list of kinds",
    "docs/reports/data/2026-11-01-q132-governor-desk": "text: Horace He's A100 gist numbers",
    "docs/reports/data/2026-11-02-e135-a100-kinds": "E135, an A100 GPU",
    "docs/reports/data/2026-11-02-e149-gpu-model-check": "E149, an A100 GPU",
    "docs/reports/data/2026-11-02-e150-second-gpu": "E150, a second GPU",
    "docs/reports/data/2026-11-03-e162-gpu-row-k": "E162, GPUs"}
SHIFT_W = 0.005  # fault 6's count: a run whose leaving-out moves L on aifoundry3 by more than this


def stop(msg):
    raise SystemExit("TERM C NOTE 2 STOPPED: " + msg)


def git(*args, inp=None):
    return subprocess.run(["git", "-C", TOP] + list(args), input=inp, capture_output=True, check=True).stdout


def committed_sha(path):
    """the sha256 SHA256SUMS records for a path (repo-relative)"""
    for ln in open(SUMS):
        h, p = ln.split(None, 1)
        if p.strip() == path:
            return h
    return None


# ------------------------------------------------------------------ which E178 float kinds are new (fault 1)
def fit_kind_bytes(fitj):
    """every fit kind's bytes, re-read from its committed tiles (each path must hash as termc-fit.json says)"""
    paths = defaultdict(set)
    for r in fitj["rows"]["fit_rows"]:
        if r["src"] == "m10-row" and r.get("tile"):
            paths[(r["fmt"], r["kind"])].add(r["tile"])
    out = {}
    for (fmt, kind), ps in sorted(paths.items()):
        for p in sorted(ps):
            raw = open(os.path.join(TOP, p), "rb").read()
            if TC.sha_b(raw) != kind:
                stop(f"{p} does not hash as termc-fit.json's kind {kind[:12]}")
        out[(fmt, kind)] = {"raw": raw, "paths": sorted(ps)}
    return out


def split_kinds(fitj):
    """E178's float kinds (termc.e178_float_kinds: hashed against kinds-e178.json, classed by bytes), split by sha256 against the
    fit's kinds: a bridge kind has a fit kind's bytes in its own format, a new kind matches no fit kind in either format"""
    fc, kinds = TC.e178_float_kinds()
    fk = {(k["fmt"], k["kind_sha256"]): k for k in fitj["kinds"]}
    any_fmt = {k["kind_sha256"] for k in fitj["kinds"]}
    bridge, new = {}, {}
    for key, v in sorted(kinds.items()):
        f = fk.get((v["fmt"], v["sha256"]))
        if f is not None:
            if f["cls"] != "one":
                stop(f"{key} has an eight-word fit kind's bytes")
            bridge[key] = {"fmt": v["fmt"], "role": v["role"], "sha256": v["sha256"], "fit_kind_labels": f["labels"],
                           "fit_rows": f["n_rows"], "fit_runs": len(f["runs"]), "fit_run_list": f["runs"]}
        elif v["sha256"] in any_fmt:
            stop(f"{key} has the bytes of a fit kind of the other format")
        else:
            new[key] = {"fmt": v["fmt"], "role": v["role"], "sha256": v["sha256"], "a_word": v["a_word"], "b_word": v["b_word"]}
    return fc, kinds, bridge, new


def committed_bins(ref):
    """every .bin blob in the tree of ref, as (path, bytes), read with one git cat-file --batch"""
    ents = []
    for e in git("ls-tree", "-r", "-z", ref).decode("utf-8", "surrogateescape").split("\0"):
        if not e:
            continue
        meta, path = e.split("\t", 1)
        _mode, typ, oid = meta.split()
        if typ == "blob" and path.endswith(".bin"):
            ents.append((oid, path))
    data = git("cat-file", "--batch", inp="".join(o + "\n" for o, _ in ents).encode())
    out, i = [], 0
    for oid, path in ents:
        j = data.index(b"\n", i)
        hdr = data[i:j].split()
        if hdr[0].decode() != oid or hdr[1] != b"blob":
            stop(f"git cat-file answered {hdr!r} for {path}")
        n = int(hdr[2])
        out.append((path, data[j + 1:j + 1 + n]))
        i = j + 1 + n + 1
    return out


def bin_scan(kinds, ref=SCAN_REF):
    want = {v["sha256"]: k for k, v in kinds.items()}
    bins = committed_bins(ref)
    hits = defaultdict(list)
    for path, raw in bins:
        h = TC.sha_b(raw)
        if h in want:
            hits[want[h]].append(path)
    return {"ref": ref, "n_bin_files": len(bins), "n_2048_byte": sum(1 for _, r in bins if len(r) == 2048),
            "paths_by_kind": {k: sorted(hits.get(k, [])) for k in sorted(kinds)},
            "outside_e178_by_kind": {k: sorted(p for p in hits.get(k, []) if not p.startswith("tools/claims-v3/e178/"))
                                     for k in sorted(kinds)}}


def builtins_and_twos(kinds, ref=SCAN_REF):
    """the host's built-in constant kinds (no .bin is written for them) whose words an E178 float kind holds, and where the
    committed data names 'twos', the one such kind outside the bridge"""
    src = open(MAIN_CPP).read()
    lines_ok = {f"{f}.{m}": s in src for (f, m), (_, s) in BUILTIN.items()}
    match = {}
    for k, v in sorted(kinds.items()):
        raw = open(os.path.join(TOP, v["tile"]), "rb").read()
        _, _, s = TC.classify(raw, v["fmt"])
        a, b = s["a_word"], s["bases"][0]
        for (f, m), (w, _) in BUILTIN.items():
            if f == v["fmt"] and a == w and b == w:
                match[k] = m
    hits = git("grep", "-l", "-w", "-F", "twos", ref, "--", "docs/reports/data").decode().split("\n")
    dirs = sorted({"/".join(h.split(":", 1)[1].split("/")[:4]) for h in hits if h})
    runs = []
    for f, exp in (("horace-runs.jsonl", "E7"), ("horace2-runs.jsonl", "E8")):
        rs = [json.loads(x) for x in open(os.path.join(SEP20, f)) if x.strip()]
        tw = [r for r in rs if r.get("values") == "twos"]
        runs.append({"experiment": exp, "file": TC.REL(os.path.join(SEP20, f)), "launches": len(tw),
                     "type": sorted({r.get("type") for r in tw}), "test": sorted({r.get("test") for r in tw}),
                     "ghz_range": [min(r["ghz"] for r in tw), max(r["ghz"] for r in tw)], "minions": sorted({r.get("minions") for r in tw}),
                     "rounds": sorted({r.get("round") for r in tw})})
    return {"main_cpp_lines_present": lines_ok, "e178_kinds_with_builtin_bytes": match,
            "twos_named_in_data_dirs": {d: EXPECT_TWOS_DIRS.get(d, "UNEXPECTED") for d in dirs}, "twos_launches": runs}


def m10_rows_check(I, kinds):
    """no float row M10 is fitted on (rows-m10.json) holds a new kind's bytes; the bridge kinds' rows listed; rows with no tile file"""
    mrows = TC.m10_classed(I)
    by = defaultdict(list)
    for r in mrows:
        if r["kind"]:
            by[(r["fmt"], r["kind"])].append(f"{r['exp']}|{r['card']}:{r['key']}")
    out = {k: sorted(by.get((v["fmt"], v["sha256"]), [])) for k, v in sorted(kinds.items())}
    nofile = sorted(f"{r['exp']}|{r['card']}:{r['key']}" for r in mrows if not r["kind"])
    return {"n_float_rows": len(mrows), "rows_by_e178_kind": out, "float_rows_without_a_tile_file": nofile}


# ------------------------------------------------------------------ the accumulator's step, by bytes (fault 3)
def _f32(w):
    return 0.0 if (w >> 23) & 0xFF == 0 else struct.unpack("<f", struct.pack("<I", w))[0]  # DAZ: a denormal input reads 0


def _r32(x):
    y = struct.unpack("<f", struct.pack("<f", x))[0]  # round to nearest even
    return 0.0 if (struct.unpack("<I", struct.pack("<f", y))[0] >> 23) & 0xFF == 0 else y  # FTZ: a denormal result reads 0


def _f16(h):
    return 0.0 if (h >> 10) & 0x1F == 0 else struct.unpack("<e", struct.pack("<H", h))[0]


def step(fmt, a, b):
    """one step's contribution to C from a lane's A and B words, by E178's arithmetic model (E178.md lines 51-53: fp32 rounded per
    step, round to nearest even, DAZ/FTZ; fp16 a 2-term update, both pairings of the halves tried)"""
    if fmt == "fp32":
        p = _r32(_f32(a) * _f32(b))
        return {"step": p, "moves": p != 0.0, "pairing_matters": False}
    al, ah, bl, bh = a & 0xFFFF, a >> 16, b & 0xFFFF, b >> 16
    s1 = _f16(al) * _f16(bl) + _f16(ah) * _f16(bh)
    s2 = _f16(al) * _f16(bh) + _f16(ah) * _f16(bl)
    return {"step": s1, "step_other_pairing": s2, "moves": s1 != 0.0, "pairing_matters": (s1 != 0.0) != (s2 != 0.0)}


def accumulator_table(fitj, kinds):
    fb = fit_kind_bytes(fitj)
    fit = {}
    for k in fitj["kinds"]:
        if k["cls"] != "one":
            continue
        raw = fb[(k["fmt"], k["kind_sha256"])]["raw"]
        _, _, s = TC.classify(raw, k["fmt"])
        a, b = s["a_word"], s["bases"][0]
        lab = [x for x in k["labels"] if x != "anchor_pi"][0]
        fit[lab] = dict(step(k["fmt"], a, b), fmt=k["fmt"], a_word=f"{a:08x}", b_word=f"{b:08x}", rows=k["n_rows"])
    e178 = {}
    for key, v in sorted(kinds.items()):
        raw = open(os.path.join(TOP, v["tile"]), "rb").read()
        _, _, s = TC.classify(raw, v["fmt"])
        a, b = s["a_word"], s["bases"][0]
        e178[key] = dict(step(v["fmt"], a, b), fmt=v["fmt"], a_word=f"{a:08x}", b_word=f"{b:08x}")
    return fit, e178


# ------------------------------------------------------------------ readings on the committed fit rows (faults 2, 3, 6)
def one_rows(fitj, fmt):
    out = []
    for r in fitj["rows"]["fit_rows"]:
        if r["fmt"] == fmt and r["cls"] == "one":
            q = {k: r[k] for k in ("src", "run", "exp", "card", "key", "fmt", "cls", "kind", "e", "rate", "s", "c")}
            q["rho_J"] = q["e"] / (q["s"] * q["c"] * q["rate"])
            if abs(q["rho_J"] - r["rho_J"]) > 1e-22:
                stop(f"{r['run']}:{r['key']} rho does not recompute")
            out.append(q)
    return out


def lev_w(fitj, fmt, rows):
    lam = TC.level(rows, "kind")
    return lam, fitj["levels"]["primary_K"][fmt]["rate_per_s"] * lam


def with_interval(fitj, fmt, rows):
    rows = [dict(r) for r in rows]
    full = TC.levels(rows, "kind")
    folds = TC.loro(rows, "kind")
    j = TC.jackknife(rows, folds, full, fmt)
    rate = fitj["levels"]["primary_K"][fmt]["rate_per_s"]
    return {"L_w_a3": rate * full[fmt]["one"], "L_95_w_a3": [rate * j["lo95_J"], rate * j["hi95_J"]] if "lo95_J" in j else None,
            "n_runs": j["n_runs"], "n_kinds": len({r["kind"] for r in rows}), "n_rows": len(rows)}


def tie_vs_kind(fitj):
    """post hoc: the tie (anchor_pi, first and last in every pass) against fp32.pi (the same bytes as a kind row) in the only two
    sessions that hold both, from Q139(u)'s footing reductions; then what that difference does to fp32's level"""
    out, wi, wp = {}, [], []
    for exp, p in FOOT.items():
        d = TC.load(p)
        t, k = d["items"]["anchor_pi"], d["items"]["fp32.pi"]
        diff = k["D"]["mean"] - t["D"]["mean"]
        se = math.hypot(k["D"]["se"], t["D"]["se"])
        pp = d["per_pass"]
        both = [ps for ps in sorted(pp) if "anchor_pi" in pp[ps] and "fp32.pi" in pp[ps]]
        dt, dk = [pp[ps]["anchor_pi"]["D"] for ps in both], [pp[ps]["fp32.pi"]["D"] for ps in both]
        reads = abs(TC.mean(dt) - t["D"]["mean"]) < 1e-9 and abs(TC.mean(dk) - k["D"]["mean"]) < 1e-9 and \
            len(both) == t["D"]["n"] == k["D"]["n"]
        dd = [b - a for a, b in zip(dt, dk)]
        n = len(dd)
        md = sum(dd) / n
        sep = math.sqrt(sum((x - md) ** 2 for x in dd) / (n - 1)) / math.sqrt(n)
        out[exp] = {"card": d.get("card"), "reduction": TC.REL(p), "tie_D_w": t["D"]["mean"], "tie_se_w": t["D"]["se"],
                    "kind_D_w": k["D"]["mean"], "kind_se_w": k["D"]["se"], "passes": n, "kind_minus_tie_w": diff,
                    "se_independent_w": se, "z_independent": diff / se, "paired_mean_w": md, "paired_se_w": sep,
                    "paired_t": md / sep, "per_pass_means_reproduce_items": reads,
                    "per_pass_kind_minus_tie_w": dict(zip([str(x) for x in both], dd))}
        wi.append((diff, se))
        wp.append((md, sep))

    def pool(v):
        w = [1 / s ** 2 for _, s in v]
        return sum(x * q for (x, _), q in zip(v, w)) / sum(w), 1 / math.sqrt(sum(w))

    pi_, pp_ = pool(wi), pool(wp)
    rows = one_rows(fitj, "fp32")
    lam0, L0 = lev_w(fitj, "fp32", rows)
    bounds = {}
    for name, delta in (("pooled_independent", pi_[0]), ("pooled_paired", pp_[0])):
        sh = []
        for r in rows:
            q = dict(r)
            if q["src"] == "tie":
                q["e"] += delta
                q["rho_J"] = q["e"] / (q["s"] * q["c"] * q["rate"])
            sh.append(q)
        bounds[name] = {"shift_w": delta, "L_w_a3": lev_w(fitj, "fp32", sh)[1], "dL_w_a3": lev_w(fitj, "fp32", sh)[1] - L0}
    nt = [r for r in rows if r["src"] != "tie"]
    bounds["pi_from_its_kind_rows_only"] = {"L_w_a3": lev_w(fitj, "fp32", nt)[1], "dL_w_a3": lev_w(fitj, "fp32", nt)[1] - L0,
                                             "pi_rows": sum(1 for r in nt if r["kind"] == _pi_kind(fitj))}
    return {"label": "POST HOC (Q139(u)'s footing; these rows are fit rows already read)", "sessions": out,
            "pooled_independent_w": {"mean": pi_[0], "se": pi_[1]}, "pooled_paired_w": {"mean": pp_[0], "se": pp_[1]},
            "fp32_L_w_a3_registered": L0, "bounds_on_fp32_L": bounds,
            "tie_share_of_pi_rows": [sum(1 for r in rows if r["src"] == "tie"), sum(1 for r in rows if r["kind"] == _pi_kind(fitj))]}


def _pi_kind(fitj):
    return [k["kind_sha256"] for k in fitj["kinds"] if "fp32.pi" in k["labels"]][0]


def still_kinds_levels(fitj, fit_tab):
    """post hoc: the level without the fit kinds whose accumulator cannot move, with the registered jackknife on what is left"""
    out = {}
    lab_of = {(k["fmt"], k["kind_sha256"]): [y for y in k["labels"] if y != "anchor_pi"][0] for k in fitj["kinds"]}
    for fmt in FLOATS:
        rows = one_rows(fitj, fmt)
        still = {lab for lab, v in fit_tab.items() if v["fmt"] == fmt and not v["moves"]}
        keep = [r for r in rows if lab_of[(fmt, r["kind"])] not in still]
        only = [r for r in rows if lab_of[(fmt, r["kind"])] in still]
        res = {"still_kinds": sorted(still), "registered": with_interval(fitj, fmt, rows),
               "without_still_kinds": with_interval(fitj, fmt, keep), "still_kinds_alone_L_w_a3": lev_w(fitj, fmt, only)[1]}
        for lab in sorted(still):
            res[f"without_{lab}_only_L_w_a3"] = lev_w(fitj, fmt, [r for r in rows if lab_of[(fmt, r["kind"])] != lab])[1]
        out[fmt] = res
    return out


def jackknife_df(fitj):
    out = {}
    for fmt in FLOATS:
        v = fitj["levels"]["primary_K"][fmt]
        j, rate, lam = v["jackknife"], v["rate_per_s"], v["lambda_J_per_op"]
        J = j["loro_values_J"]
        mj = sum(J.values()) / len(J)
        shifts = {R: rate * (x - lam) for R, x in J.items()}
        big = sorted((R for R, s in shifts.items() if abs(s) > SHIFT_W), key=lambda x: int(x.split("|")[0][1:]))
        d = [x - mj for x in J.values()]
        kish = sum(x * x for x in d) ** 2 / sum(x ** 4 for x in d)
        se_w, L = rate * j["se_J"], v["L_w"]["a3"]
        reg = [L - j["t"] * se_w, L + j["t"] * se_w]
        if max(abs(reg[0] - v["L_95_w"]["a3"][0]), abs(reg[1] - v["L_95_w"]["a3"][1])) > 1e-12:
            stop(f"{fmt}: the registered interval does not recompute")
        dfs = {}
        for df in sorted({len(big) - 1, 4}):
            t = TC.t_ppf(0.975, df)
            dfs[str(df)] = {"t": t, "L_95_w_a3": [L - t * se_w, L + t * se_w], "holds_0": L - t * se_w <= 0 <= L + t * se_w}
        out[fmt] = {"n_runs": j["n_runs"], "df_registered": j["n_runs"] - 1, "t_registered": j["t"], "se_J_w_a3": se_w,
                    "L_w_a3": L, "L_95_w_a3_registered": reg, "registered_holds_0": reg[0] <= 0 <= reg[1],
                    "runs_moving_L_over_w": SHIFT_W, "runs_moving_L": big, "shifts_w_a3_of_those": {R: shifts[R] for R in big},
                    "max_abs_shift_other_runs_w": max([abs(s) for R, s in shifts.items() if R not in big] or [0.0]),
                    "kish_effective_runs": kish, "at_reduced_df": dfs}
    return out


# ------------------------------------------------------------------ the split (fault 1), registered as a REPORTED arm
def score_split(scored, fitj, bridge):
    """the registered rule exactly as termc.score_session reads it, and beside it the same statistics on the new kinds alone"""
    reg = TC.score_session(scored, fitj)
    out = {"run": "E178", "label": "REPORTED split (REGISTRATION.md dated note 2): never a verdict, never the entry rule; the "
                                   "registered rule's verdict decides entry",
           "registered_rule": reg, "bridge_kinds": sorted(bridge)}
    if reg.get("verdict") == "NOT SCORED":
        out["split"] = {"verdict": "NOT SCORED", "why": reg.get("why")}
        return out
    rows = reg["kinds"]
    new = [r for r in rows if r["kind"] not in bridge]
    bri = [r for r in rows if r["kind"] in bridge]
    if new:
        C1 = TC.c1_rule([r["x_w"] for r in new], [r["x_prime_w"] for r in new])
        C2 = {}
        for fmt in FLOATS:
            a = [r for r in new if r["fmt"] == fmt]
            C2[fmt] = (TC.rms([r["x_prime_w"] for r in a]) - TC.rms([r["x_w"] for r in a])) if a else None
        c2ok = all(C2[f] is not None and C2[f] < 0 for f in FLOATS)
        sp = {"n_kinds": len(new), "kinds": sorted(r["kind"] for r in new), "C1": C1, "C2_d_w": C2, "C2_holds": c2ok,
              "C1_BETTER_and_C2": C1["verdict"] == "BETTER" and c2ok,
              "m_level_w": {fmt: TC.t_interval([r["x_w"] for r in new if r["fmt"] == fmt]) for fmt in FLOATS}}
        sp["agrees_with_the_rule"] = sp["C1_BETTER_and_C2"] == reg["enters_M10_for_the_next_blind_pool"]
    else:
        sp = {"verdict": "NOT SCORED", "why": "no new float kind kept"}
    out["split"] = sp
    out["bridge"] = {"n_kinds": len(bri), "m_level_w": {fmt: TC.t_interval([r["x_w"] for r in bri if r["fmt"] == fmt]) for fmt in FLOATS},
                     "kinds": bri}
    return out


# ------------------------------------------------------------------ the checks
def facts(fitj, I=None):
    """everything the note quotes except the power"""
    fc, kinds, bridge, new = split_kinds(fitj)
    fit_tab, e178_tab = accumulator_table(fitj, kinds)
    I = I or TC.Inputs()
    return {"fc": fc, "kinds": kinds, "bridge": bridge, "new": new, "scan": bin_scan(kinds), "builtin": builtins_and_twos(kinds),
            "m10": m10_rows_check(I, kinds), "fit_acc": fit_tab, "e178_acc": e178_tab, "tie": tie_vs_kind(fitj),
            "still": still_kinds_levels(fitj, fit_tab), "jk": jackknife_df(fitj)}


def checks(fitj, F):
    log = []
    P = log.append
    # [1] termc-fit.json is the committed one, and its fit kinds' tiles hash as it says
    want = committed_sha("tools/claims-v3/m10-c/termc-fit.json")
    ok1 = want == TC.fsha(FIT)
    fb = fit_kind_bytes(fitj)
    ok1 &= len(fb) == len(fitj["kinds"]) == 14
    P(f"[1] termc-fit.json sha256 {TC.fsha(FIT)[:12]} = SHA256SUMS' {str(want)[:12]}; {len(fb)} fit kinds re-hashed from their "
      f"{sum(len(v['paths']) for v in fb.values())} tile paths  {'OK' if ok1 else 'FAIL'}")
    # [2] the split by bytes
    br = {k: (v["fit_rows"], v["fit_runs"]) for k, v in F["bridge"].items()}
    nn = {fmt: sum(1 for v in F["new"].values() if v["fmt"] == fmt) for fmt in FLOATS}
    ok2 = br == EXPECT_BRIDGE and nn == EXPECT_NEW and len(F["kinds"]) == 27
    P(f"[2] E178's float kinds by sha256 against the fit's kinds: bridge {br}; new {nn}  {'OK' if ok2 else 'FAIL'}")
    # [3] no M10 row and no committed .bin outside E178's own tiles holds a new kind's bytes
    m10hit = {k: v for k, v in F["m10"]["rows_by_e178_kind"].items() if v}
    out = {k: v for k, v in F["scan"]["outside_e178_by_kind"].items() if v}
    ok3 = set(m10hit) == set(EXPECT_BRIDGE) and set(out) <= set(EXPECT_BRIDGE) and \
        all(F["scan"]["paths_by_kind"][k] for k in F["kinds"])
    P(f"[3] at {F['scan']['ref']}: {F['scan']['n_bin_files']} committed .bin files ({F['scan']['n_2048_byte']} of 2,048 bytes); "
      f"kinds found outside tools/claims-v3/e178/: {sorted(out)}; M10's {F['m10']['n_float_rows']} float rows holding an E178 kind's "
      f"bytes: {sorted(m10hit)}; M10 float rows with no tile file: {len(F['m10']['float_rows_without_a_tile_file'])}  "
      f"{'OK' if ok3 else 'FAIL'}")
    # [4] the host's built-in constant kinds, and where 'twos' is named
    b = F["builtin"]
    ok4 = all(b["main_cpp_lines_present"].values()) and b["e178_kinds_with_builtin_bytes"] == \
        {"fp16.ones": "ones", "fp32.e178_v2": "twos", "fp32.ones": "ones"} and set(b["twos_named_in_data_dirs"]) == set(EXPECT_TWOS_DIRS)
    P(f"[4] built-in constant kinds (main.cpp lines present {all(b['main_cpp_lines_present'].values())}): E178 kinds with a "
      f"built-in's bytes {b['e178_kinds_with_builtin_bytes']}; 'twos' named in {len(b['twos_named_in_data_dirs'])} data dirs, "
      f"measured on this chip only in {[d.split('/')[-1] for d, w in b['twos_named_in_data_dirs'].items() if 'this chip' in w]}; launches "
      + "; ".join(f"{x['experiment']} {x['launches']} ({','.join(x['type'])}, {x['ghz_range'][0]:.3f}-{x['ghz_range'][1]:.3f} GHz)"
                  for x in b["twos_launches"]) + f"  {'OK' if ok4 else 'FAIL'}")
    # [5] whose accumulator can move, by bytes
    still_fit = {fmt: {k for k, v in F["fit_acc"].items() if v["fmt"] == fmt and not v["moves"]} for fmt in FLOATS}
    still_e = {k for k, v in F["e178_acc"].items() if not v["moves"]}
    pm = [k for k, v in list(F["fit_acc"].items()) + list(F["e178_acc"].items()) if v["pairing_matters"]]
    ok5 = still_fit == EXPECT_STILL_FIT and still_e == EXPECT_STILL_E178 and not pm
    P(f"[5] a step that adds 0 (E178's arithmetic: fp32 DAZ/FTZ, fp16 2-term): fit kinds {dict((f, sorted(v)) for f, v in still_fit.items())}; "
      f"E178 kinds {sorted(still_e)} of {len(F['e178_acc'])}; pairing changes none {not pm}  {'OK' if ok5 else 'FAIL'}")
    # [6] the footing reductions' per-pass means reproduce their items
    ok6 = all(v["per_pass_means_reproduce_items"] for v in F["tie"]["sessions"].values())
    P(f"[6] E78 and E82: per-pass D of anchor_pi and fp32.pi reproduce items.D.mean and n  {'OK' if ok6 else 'FAIL'}")
    # [7] the split's scorer on synthetic sessions, and the registered rule passed through unchanged
    ok7 = True
    for truth, want_v in (("P + L", "BETTER"), ("P", "WORSE")):
        sc, fj = TC._synthetic(F["fc"], F["kinds"], truth)
        res = score_split(sc, fj, set(F["bridge"]))
        reg = TC.score_session(sc, fj)
        same = json.dumps(res["registered_rule"], sort_keys=True) == json.dumps(reg, sort_keys=True)
        sp = res["split"]
        good = same and sp["C1"]["verdict"] == want_v and sp["C2_holds"] == (want_v == "BETTER") and sp["n_kinds"] == 23 and \
            sorted(sp["kinds"]) == sorted(F["new"]) and res["bridge"]["n_kinds"] == 4 and sp["agrees_with_the_rule"]
        ok7 &= good
        P(f"[7] split on a synthetic session, truth {truth:5s}: rule C1 {reg['C1']['verdict']} (passed through unchanged {same}); "
          f"split C1 {sp['C1']['verdict']} d {sp['C1']['d_w']:+.4f} W on {sp['n_kinds']} kinds, C2 {sp['C2_holds']}, bridge "
          f"{res['bridge']['n_kinds']} (want {want_v})  {'OK' if good else 'FAIL'}")
    sc, fj = TC._synthetic(F["fc"], F["kinds"], "P", passes=["17810"])
    ns = score_split(sc, fj, set(F["bridge"]))
    ok7 &= ns["split"].get("verdict") == "NOT SCORED" and ns["registered_rule"].get("verdict") == "NOT SCORED"
    P(f"[7] one kept pass: rule {ns['registered_rule'].get('verdict')}, split {ns['split'].get('verdict')}  "
      f"{'OK' if ns['split'].get('verdict') == 'NOT SCORED' else 'FAIL'}")
    # [8] the t quantiles fault 6 reads
    ok8 = abs(TC.t_ppf(0.975, 4) - 2.776445) < 1e-5 and abs(TC.t_ppf(0.975, 5) - 2.570582) < 1e-5
    P(f"[8] t(0.975, 4) {TC.t_ppf(0.975, 4):.6f} (2.776445), t(0.975, 5) {TC.t_ppf(0.975, 5):.6f} (2.570582)  {'OK' if ok8 else 'FAIL'}")
    allok = ok1 and ok2 and ok3 and ok4 and ok5 and ok6 and ok7 and ok8
    P(f"SELFTEST {'PASS' if allok else 'FAIL'}")
    return allok, log


# ------------------------------------------------------------------ the outputs
def posthoc(out):
    fitj = TC.load(FIT)
    F = facts(fitj)
    ok, log = checks(fitj, F)
    if not ok:
        print("\n".join(log))
        stop("a check failed: no output")
    L = {fmt: fitj["levels"]["primary_K"][fmt]["L_w"]["a3"] for fmt in FLOATS}
    sig = {fmt: fitj["levels"]["primary_K"][fmt]["sigma_C_w"] for fmt in FLOATS}
    reg = TC.power(L, sig)
    if json.dumps(reg, sort_keys=True) != json.dumps(fitj["power"], sort_keys=True):
        stop("termc.power at 14 + 13 does not reproduce termc-fit.json's power")
    spl = TC.power(L, sig, n=(EXPECT_NEW["fp32"], EXPECT_NEW["fp16"]))
    res = {
        "_what": "Q148(c), REGISTRATION.md dated note 2: the verifier's faults, before any E178 datum - which of E178's float kinds "
                 "are new by bytes, the REPORTED split on the new kinds and its power, and the post hoc readings",
        "labels": {"split": "REPORTED arm, registered before any E178 datum; never a verdict, never the entry rule",
                   "power_split": "design arithmetic (registration section 7's model and seed, 12 fp32 + 11 fp16 kinds)",
                   "tie_vs_kind": "POST HOC", "accumulator": "by bytes, E178's arithmetic model", "still_kinds_levels": "POST HOC",
                   "jackknife_df": "a reported caveat; the registered interval stands"},
        "checks": log,
        "split": {"bridge_kinds": F["bridge"], "new_kinds": F["new"],
                  "new_by_format": {fmt: sorted(k for k, v in F["new"].items() if v["fmt"] == fmt) for fmt in FLOATS},
                  "bin_scan": F["scan"], "builtin": F["builtin"], "m10_rows": F["m10"]},
        "power_registered_reproduced": reg, "power_split": spl,
        "power_nit": {"no_level_sigma_common_0.04_P_enter": [p for p in reg if p["L_true_fraction"] == 0.0 and
                                                             p["sigma_common_w"] == 0.04][0]["P_enter"]},
        "accumulator": {"fit_kinds": F["fit_acc"], "e178_kinds": F["e178_acc"]},
        "tie_vs_kind": F["tie"], "still_kinds_levels": F["still"], "jackknife_df": F["jk"],
        "inputs_sha256": {TC.REL(p): TC.fsha(p) for p in (FIT, os.path.join(HERE, "termc.py"), os.path.abspath(__file__),
                                                           os.path.join(E178D, "forecast-e178.json"), os.path.join(E178D, "kinds-e178.json"),
                                                           MAIN_CPP, FOOT["E78"], FOOT["E82"], os.path.join(SEP20, "horace-runs.jsonl"),
                                                           os.path.join(SEP20, "horace2-runs.jsonl"))},
    }
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "termc-note2.json"), "w").write(json.dumps(res, indent=1, sort_keys=True) + "\n")
    txt = report(res)
    open(os.path.join(out, "termc-note2.txt"), "w").write(txt)
    print(txt, end="")
    return 0


def report(res):
    L = []
    P = L.append
    s = res["split"]
    P("Q148(c), REGISTRATION.md dated note 2. Labels: the split is a REPORTED arm (never a verdict, never the entry rule); its power is")
    P("design arithmetic; the tie, the accumulator levels and the df readings are POST HOC.")
    P("")
    P("E178'S 27 FLOAT KINDS BY BYTES (sha256 against the term's fit kinds):")
    for k, v in s["bridge_kinds"].items():
        P(f"  bridge {k:16s} = fit kind {','.join(v['fit_kind_labels'])}: {v['fit_rows']} rows in {v['fit_runs']} runs (role {v['role']})")
    for fmt in FLOATS:
        P(f"  new {fmt} ({len(s['new_by_format'][fmt])}): {', '.join(x.split('.', 1)[1] for x in s['new_by_format'][fmt])}")
    sc = s["bin_scan"]
    P(f"  committed .bin files at {sc['ref']}: {sc['n_bin_files']}; any of the 23 outside tools/claims-v3/e178/: "
      f"{sorted(k for k, v in sc['outside_e178_by_kind'].items() if v and k not in s['bridge_kinds']) or 'none'}")
    P(f"  M10's float rows holding a new kind's bytes: "
      f"{sorted(k for k, v in s['m10_rows']['rows_by_e178_kind'].items() if v and k not in s['bridge_kinds']) or 'none'}")
    b = s["builtin"]
    P(f"  E178 kinds with a host built-in's bytes: {b['e178_kinds_with_builtin_bytes']}")
    P("  'twos' named in committed data (git grep -w):")
    for d, w in b["twos_named_in_data_dirs"].items():
        P(f"    {d}: {w}")
    for x in b["twos_launches"]:
        P(f"    {x['experiment']}: {x['launches']} launches of {','.join(x['type'])} {','.join(x['test'])}, {x['ghz_range'][0]:.3f}-"
          f"{x['ghz_range'][1]:.3f} GHz, {x['minions']} minions ({x['file']})")
    P("")
    P("THE SPLIT'S POWER (design arithmetic, 12 fp32 + 11 fp16 kinds) beside the registered rule's (14 + 13, reproduced exactly):")
    for a, q in zip(res["power_registered_reproduced"], res["power_split"]):
        P(f"  L_true {a['L_true_fraction']:.1f} x L, sigma_common {a['sigma_common_w']:.2f} W: rule enters {a['P_enter']:.4f}, WORSE "
          f"{a['P_C1_worse']:.4f} | split C1 BETTER with C2 {q['P_enter']:.4f}, WORSE {q['P_C1_worse']:.4f}")
    P(f"  the README's 'at most 0.10' is {res['power_nit']['no_level_sigma_common_0.04_P_enter']} (no level, sigma_common 0.04 W)")
    P("")
    P("A STEP THAT ADDS 0 (by bytes; E178's arithmetic: fp32 round to nearest even with DAZ/FTZ, fp16 the 2-term update):")
    for name, tab in (("fit", res["accumulator"]["fit_kinds"]), ("E178", res["accumulator"]["e178_kinds"])):
        st = sorted(k for k, v in tab.items() if not v["moves"])
        P(f"  {name} kinds that cannot move the accumulator: {', '.join(st)} (of {len(tab)})")
        for k in st:
            v = tab[k]
            P(f"    {k:16s} A {v['a_word']} B {v['b_word']}: step {v['step']!r}")
    P("")
    t = res["tie_vs_kind"]
    P("POST HOC: THE TIE AGAINST fp32.pi's BYTES AS A KIND ROW (Q139(u)'s footing):")
    for exp, v in t["sessions"].items():
        P(f"  {exp} ({v['card']}): tie {v['tie_D_w']:.4f} (se {v['tie_se_w']:.4f}), fp32.pi {v['kind_D_w']:.4f} (se {v['kind_se_w']:.4f}): "
          f"kind - tie {v['kind_minus_tie_w']:+.4f} W, z {v['z_independent']:.2f}; paired over {v['passes']} passes "
          f"{v['paired_mean_w']:+.4f} +- {v['paired_se_w']:.4f} W (t {v['paired_t']:.2f})")
    P(f"  pooled: independent {t['pooled_independent_w']['mean']:+.4f} +- {t['pooled_independent_w']['se']:.4f} W; paired "
      f"{t['pooled_paired_w']['mean']:+.4f} +- {t['pooled_paired_w']['se']:.4f} W; the tie is {t['tie_share_of_pi_rows'][0]} of pi's "
      f"{t['tie_share_of_pi_rows'][1]} rows")
    for name, v in t["bounds_on_fp32_L"].items():
        P(f"  fp32 L on aifoundry3 with {name}: {v['L_w_a3']:+.4f} W ({v['dL_w_a3']:+.4f} from the registered {t['fp32_L_w_a3_registered']:+.4f})")
    P("")
    P("POST HOC: THE LEVEL WITHOUT THE KINDS WHOSE ACCUMULATOR CANNOT MOVE (registered estimator and jackknife on what is left):")
    for fmt, v in res["still_kinds_levels"].items():
        r, w = v["registered"], v["without_still_kinds"]
        P(f"  {fmt}: registered {r['L_w_a3']:+.4f} [{r['L_95_w_a3'][0]:+.4f}, {r['L_95_w_a3'][1]:+.4f}] ({r['n_kinds']} kinds, {r['n_runs']} runs); "
          f"without {', '.join(v['still_kinds'])} {w['L_w_a3']:+.4f} [{w['L_95_w_a3'][0]:+.4f}, {w['L_95_w_a3'][1]:+.4f}] "
          f"({w['n_kinds']} kinds, {w['n_runs']} runs); those kinds alone {v['still_kinds_alone_L_w_a3']:+.4f}")
        for k2, x in sorted(v.items()):
            if k2.startswith("without_") and k2.endswith("_only_L_w_a3"):
                P(f"        {k2[8:-12]} alone left out: {x:+.4f}")
    P("")
    P("THE JACKKNIFE'S DEGREES OF FREEDOM (a reported caveat; the registered interval stands):")
    for fmt, v in res["jackknife_df"].items():
        P(f"  {fmt}: registered df {v['df_registered']} (t {v['t_registered']:.4f}): [{v['L_95_w_a3_registered'][0]:+.4f}, "
          f"{v['L_95_w_a3_registered'][1]:+.4f}] W; runs moving L by over {v['runs_moving_L_over_w']} W: {len(v['runs_moving_L'])} "
          f"({', '.join(f'{R} {x:+.4f}' for R, x in v['shifts_w_a3_of_those'].items())}); the other runs at most "
          f"{v['max_abs_shift_other_runs_w']:.4f} W; Kish effective runs {v['kish_effective_runs']:.2f}")
        for df, x in v["at_reduced_df"].items():
            P(f"        at df {df} (t {x['t']:.4f}): [{x['L_95_w_a3'][0]:+.4f}, {x['L_95_w_a3'][1]:+.4f}] W, holds 0: {x['holds_0']}")
    P("")
    P("CHECKS:")
    L += ["  " + x for x in res["checks"]]
    return "\n".join(L) + "\n"


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("selftest", "posthoc", "score"))
    ap.add_argument("--out")
    ap.add_argument("--txt")
    ap.add_argument("--scored")
    ap.add_argument("--fit", default=FIT)
    ap.add_argument("--note2", default=NOTE2)
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        fitj = TC.load(FIT)
        ok, log = checks(fitj, facts(fitj))
        txt = "\n".join(log) + "\n"
        print(txt, end="")
        if a.txt:
            open(a.txt, "w").write(txt)
        return 0 if ok else 1
    if a.cmd == "posthoc":
        if not a.out:
            stop("posthoc needs --out")
        return posthoc(a.out)
    if not a.scored:
        stop("score needs --scored")
    fitj = TC.load(a.fit)
    frozen = set(TC.load(a.note2)["split"]["bridge_kinds"])
    _, _, br, _ = split_kinds(TC.load(FIT))
    if set(br) != frozen:
        stop(f"the bridge kinds by bytes {sorted(br)} are not the frozen {sorted(frozen)}")
    res = score_split(TC.load(a.scored), fitj, frozen)
    s = json.dumps(res, indent=1, sort_keys=True) + "\n"
    if a.out:
        open(a.out, "w").write(s)
    sp = res["split"]
    print(json.dumps({"registered_rule": {k: res["registered_rule"].get(k) for k in ("verdict", "C1", "C2_holds",
                                                                                     "enters_M10_for_the_next_blind_pool")
                                          if k in res["registered_rule"]},
                      "split_REPORTED": {k: sp.get(k) for k in ("verdict", "n_kinds", "C1", "C2_holds", "agrees_with_the_rule") if k in sp}}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
