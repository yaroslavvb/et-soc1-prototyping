#!/usr/bin/env python3
"""Q140(x), its fix pass after verification (Wed 4 Nov 2026, desk only): the numbers behind the dated notes A1-1 to A1-4 of
tools/claims-v3/kinds/blind7/README-predictions.md, re-derived from git objects. No working-tree file is opened and nothing
is written but stdout; standard library only.

    python3 -B notes_check.py <the lab tree> [<gate commit> [<later commit>]] > notes-check.json

A1-1  predictions-blind7-aifoundry2.md's "M9 MHz" and "M9 board W" columns against M9's registered aifoundry2 primary
      (each tile's M9.a2_q140l block), by the primary's group; the .md's peak and 82 W columns; and the README's own table.
A1-2  every 2,048-byte blob outside tools/claims-v3/kinds/blind7/ hashed against pool 7's tiles, at the gate and at a later
      commit; the twin's bytes; M9's committed calibration record and 27-point recount lines; M9's frozen D for the tile.
A1-3  Q140(l)'s committed corrections C4: the held-out errors with the selection nested, and the bands' rule on them.
A1-4  the commit times of c9aaf179, e39d06da and the gate; the clone's reflog for them, if the clone has one (a local
      record, not part of any commit).
"""
import hashlib
import json
import re
import struct
import subprocess
import sys

REPO = sys.argv[1]
GATE = sys.argv[2] if len(sys.argv) > 2 else "75802201"
LATER = sys.argv[3] if len(sys.argv) > 3 else None
POOL = "tools/claims-v3/kinds/blind7/"
M9D = "docs/reports/data/2026-11-04-q140m-m9/"
L_D = "docs/reports/data/2026-11-04-q140l-a2-session-terms/"
TWIN_POOL, TWIN_M9 = "fp32.b_onebit_b20_pi", "fp32.cal_pi_b20"


def git(*a, inp=None):
    return subprocess.run(["git", "-C", REPO, *a], check=True, capture_output=True, input=inp).stdout


def show(commit, path):
    return git("show", f"{commit}:{path}")


def rng(xs):
    return [round(min(xs), 3), round(max(xs), 3)]


out = {"gate": git("rev-parse", GATE).decode().strip(), "script": "notes_check.py"}

# ---------------------------------------------------------------- A1-1
js = json.loads(show(GATE, POOL + "predictions-blind7-aifoundry2.json"))
md = show(GATE, POOL + "predictions-blind7-aifoundry2.md").decode()
md_rows = {}
for line in md.splitlines():
    m = re.match(r"\| `([^`]+)` \| (\d) \| ([-\d.]+) \| ([-\d.]+) \| ([-\d.]+) \| ([-\d.]+) / ([-\d.]+) \| (\w+) \|", line)
    if m:
        md_rows[m.group(1)] = {"mhz": m.group(4), "board": m.group(5), "peak": m.group(6), "hi95": m.group(7), "flag": m.group(8)}
header = next((l for l in md.splitlines() if l.startswith("Bursts under")), "")
rd = show(GATE, POOL + "README-predictions.md").decode()
rd_rows = {}
for line in rd.splitlines():
    c = [x.strip() for x in line.split("|")]
    if len(c) == 16 and c[1].startswith("`") and c[1].endswith("`") and re.match(r"[-\d.]+ \[", c[10] or ""):
        rd_rows[c[1].strip("`")] = {"mhz_band": c[10], "board": c[11], "peak": c[12]}
per, groups = {}, {}
md_is_top = rd_is_primary = rd_is_top = flags_same = 0
for n, r in js["tiles"].items():
    m9 = r["M9"]
    q = m9["a2_q140l"]
    g = q["group"]
    mr = md_rows[n]
    md_is_top += (mr["mhz"] == f"{m9['burst_mhz']:.1f}" and mr["board"] == f"{m9['burst_board_w']:.2f}"
                  and mr["peak"] == f"{m9['peak_board_w']:.2f}" and mr["hi95"] == f"{m9['peak_board_hi95_w']:.2f}"
                  and (mr["flag"] == "YES") == bool(m9["peak_over_82w"]))
    rr = rd_rows.get(n)
    if rr:
        prim = f"{q['burst_mhz']:.1f} [{q['burst_mhz_95'][0]:.0f}, {q['burst_mhz_95'][1]:.0f}]"
        top = f"{m9['burst_mhz']:.1f} [{m9['burst_mhz_95'][0]:.0f}, {m9['burst_mhz_95'][1]:.0f}]"
        rd_is_primary += (rr["mhz_band"] == prim and rr["board"] == f"{q['burst_board_w']:.2f}")
        rd_is_top += (rr["mhz_band"] == top and rr["board"] == f"{m9['burst_board_w']:.2f}")
    flags_same += (bool(q["peak_over_82w"]) == bool(m9["peak_over_82w"]))
    d = {"group": g, "priority": r["priority"],
         "md_mhz": float(mr["mhz"]), "md_board_w": float(mr["board"]),
         "primary_mhz": q["burst_mhz"], "primary_board_w": q["burst_board_w"],
         "md_minus_primary_mhz": round(m9["burst_mhz"] - q["burst_mhz"], 3),
         "md_minus_primary_board_w": round(m9["burst_board_w"] - q["burst_board_w"], 3),
         "md_minus_primary_peak_w": round(m9["peak_board_w"] - q["peak_board_w"], 3),
         "md_minus_primary_hi95_w": round(m9["peak_board_hi95_w"] - q["peak_board_hi95_w"], 3),
         "top_minus_primary_P800_w": round(m9["P800_w"] - q["P800_w"], 3)}
    per[n] = d
    groups.setdefault(g, []).append(d)
out["A1_1"] = {
    "md_header": header,
    "md_rows": len(md_rows),
    "md_columns_equal_M9_top_level_burst_fields": md_is_top,
    "readme_table_rows": len(rd_rows),
    "readme_table_equals_M9_a2_q140l": rd_is_primary,
    "readme_table_equals_M9_top_level": rd_is_top,
    "flags_same_primary_vs_top": flags_same,
    "by_group": {g: {"n": len(L),
                     "md_minus_primary_mhz": rng([x["md_minus_primary_mhz"] for x in L]),
                     "md_minus_primary_mhz_mean": round(sum(x["md_minus_primary_mhz"] for x in L) / len(L), 3),
                     "md_minus_primary_board_w": rng([x["md_minus_primary_board_w"] for x in L]),
                     "md_minus_primary_board_w_mean": round(sum(x["md_minus_primary_board_w"] for x in L) / len(L), 3),
                     "md_minus_primary_peak_w": rng([x["md_minus_primary_peak_w"] for x in L]),
                     "md_minus_primary_hi95_w": rng([x["md_minus_primary_hi95_w"] for x in L]),
                     "top_minus_primary_P800_w": rng([x["top_minus_primary_P800_w"] for x in L])}
                 for g, L in sorted(groups.items())},
    "example": {k: per["fp16.anchor7_randn_a"][k] for k in ("group", "md_mhz", "md_board_w", "primary_mhz", "primary_board_w")},
    "per_tile": per,
}

# ---------------------------------------------------------------- A1-2
def scan(commit):
    full = git("rev-parse", commit).decode().strip()
    pool = json.loads(show(full, POOL + "blind7.json"))
    zero = hashlib.sha256(bytes(2048)).hexdigest()
    mine = {t["sha256"]["whole"]: t["name"] for t in pool["tiles"]}
    bl = []
    for line in git("ls-tree", "-r", "-l", full).decode().splitlines():
        meta, path = line.split("\t", 1)
        _, typ, sha, size = meta.split()
        if typ == "blob" and size == "2048" and not path.startswith(POOL):
            bl.append((sha, path))
    data = git("cat-file", "--batch", inp=("\n".join(s for s, _ in bl) + "\n").encode())
    i, hits, zeros = 0, [], 0
    for s, p in bl:
        j = data.index(b"\n", i)
        size = int(data[i:j].split()[2])
        h = hashlib.sha256(data[j + 1:j + 1 + size]).hexdigest()
        i = j + 1 + size + 1
        if h == zero:
            zeros += 1
        elif h in mine:
            hits.append({"pool7_tile": mine[h], "path": p, "sha256": h})
    return {"commit": full, "blobs_2048_outside_blind7": len(bl), "all_zero": zeros,
            "pool7_distinct_tile_hashes": len(mine), "whole_tile_repeats_other_than_zeros": hits}


twin = {}
for key, path in (("pool7", POOL + "tiles/fp32/" + TWIN_POOL + ".bin"), ("m9_cal", M9D + "bench-check/tiles/" + TWIN_M9 + ".bin")):
    b = show(GATE, path)
    a, bb = struct.unpack("<256I", b[:1024]), struct.unpack("<256I", b[1024:])
    twin[key] = {"path": path, "sha256": hashlib.sha256(b).hexdigest(),
                 "a_words": sorted({f"0x{w:08X}" for w in a}), "b_words": sorted({f"0x{w:08X}" for w in bb}),
                 "b_columns_with_bit20_set": sorted({k % 16 for k, w in enumerate(bb) if w & (1 << 20)})}
cal_txt = show(GATE, M9D + "bench-check/cal-tiles.json").decode()
cal_line = next(k + 1 for k, l in enumerate(cal_txt.splitlines()) if f'"name": "{TWIN_M9}"' in l)
cal = next(t for t in json.loads(cal_txt)["tiles"] if t["name"] == TWIN_M9) if isinstance(json.loads(cal_txt), dict) else \
    next(t for t in json.loads(cal_txt) if t["name"] == TWIN_M9)
rc_txt = show(GATE, M9D + "recount-rule/recount-rule.txt").decode()
rc = []
for k, l in enumerate(rc_txt.splitlines()):
    f = l.split()
    if f and f[0] == TWIN_M9:
        rc.append({"line": k + 1, "N": int(f[1]), "mean_w": float(f[2]), "3pt_minus_N_w": float(f[3]),
                   "se_sample_w": float(f[4]), "se_interleaved_w": float(f[5]), "e_N_w": float(f[6]), "met": f[7]})
p6 = [l.strip() for l in rc_txt.splitlines() if l.strip().startswith("fp32.b_onebit_b20_third (N = 27)")]
pred = {}
for card in ("aifoundry3", "aifoundry1c1"):
    t = json.loads(show(GATE, POOL + f"predictions-blind7-{card}.json"))["tiles"][TWIN_POOL]
    pred[card] = {"M9_D_w": t["M9"]["D_w"], "M9_D_95": t["M9"]["D_95"], "priority": t["priority"], "case": t["case"]}
fit_reads = {f: [w for w in ("counts-cal", "bench-check", "cal_pi", "recount") if w in show(GATE, M9D + f).decode()]
             for f in ("fit_m9.py", "predict_blind7.py")}
out["A1_2"] = {"scan": {GATE: scan(GATE), **({LATER: scan(LATER)} if LATER else {})},
               "twin_bytes": twin, "cal_tiles_json_line": cal_line, "cal_tiles_record": cal,
               "recount_rule_txt": rc, "pool6_twin_post_hoc_line": p6,
               "M9_frozen_prediction": pred, "M9_fit_and_predictor_mention": fit_reads}

# ---------------------------------------------------------------- A1-3
ct = show(GATE, L_D + "corrections.txt").decode().splitlines()
c4 = {}
for k, l in enumerate(ct):
    s = l.strip()
    if s.startswith("rule at"):
        rule = s.split(":")[0]
        c4.setdefault(rule, {})
    elif s.startswith("nested (selection inside the fold") or s.startswith("quoted (T1+T2+T3+T4"):
        m = re.search(r"pooled G\s+([\d.]+) \(([-+\d.]+)\) Bg ([\d.]+) \(([-+\d.]+)\) Bp ([\d.]+) \(([-+\d.]+)\)", s)
        key = "nested_pooled" if s.startswith("nested") else "registered_pooled"
        c4[rule][key] = {"line": k + 1, "governed_clock_mhz": float(m.group(1)), "governed_board_w": float(m.group(3)),
                         "pinned_board_w": float(m.group(5))}
    elif s.startswith("the bands' rule on the nested errors"):
        m = re.search(r"governed n (\d+) ([\d.]+) MHz / ([\d.]+) W, pinned n (\d+) ([\d.]+) MHz / ([\d.]+) W "
                      r"\(frozen: ([\d.]+) / ([\d.]+) and ([\d.]+) / ([\d.]+)\)", s)
        c4[rule]["bands_on_nested_errors"] = {"line": k + 1,
                                              "governed_mhz": float(m.group(2)), "governed_board_w": float(m.group(3)),
                                              "pinned_mhz": float(m.group(5)), "pinned_board_w": float(m.group(6))}
        c4[rule]["bands_frozen"] = {"governed_mhz": float(m.group(7)), "governed_board_w": float(m.group(8)),
                                    "pinned_mhz": float(m.group(9)), "pinned_board_w": float(m.group(10))}
a2 = json.loads(show(GATE, L_D + "m9_a2.json"))
out["A1_3"] = {"corrections_txt_C4": c4, "m9_a2_sha256": hashlib.sha256(show(GATE, L_D + "m9_a2.json")).hexdigest(),
               "m9_a2_bands_keys": sorted(k for k in a2 if "band" in k.lower())}

# ---------------------------------------------------------------- A1-4
times = {}
for c in ("c9aaf179", "e39d06da", GATE):
    h, ad, cd = git("log", "-1", "--format=%H%x09%ad%x09%cd", "--date=iso-strict", c).decode().strip().split("\t")
    times[c] = {"commit": h, "author_time": ad, "commit_time": cd}
ref = {}
for name in ("HEAD", "refs/remotes/origin/main"):
    try:
        lines = git("reflog", "show", "--date=iso-strict", "--format=%H%x09%gd%x09%gs", "-n", "400", name).decode().splitlines()
    except subprocess.CalledProcessError:
        lines = []
    ent = []
    for l in lines:
        h, gd, gs = (l.split("\t") + ["", ""])[:3]
        if any(h.startswith(c) for c in ("c9aaf179", "e39d06da", out["gate"][:8])):
            when = gd[gd.find("{") + 1:gd.rfind("}")]
            ent.append({"sha": h[:8], "time": when, "action": "commit" if gs.startswith("commit") else
                        ("push" if gs.startswith("update by push") else gs[:20])})
    ref[name] = ent
out["A1_4"] = {"commit_times": times, "reflog_local": ref}

json.dump(out, sys.stdout, indent=1, sort_keys=True)
print()
