#!/usr/bin/env python3
"""E181's data README, dated note 1 (Fri 6 Nov 2026, after the card day's data verifier): the figures the note quotes, read again from
this directory's committed files. Post hoc: it decides nothing, scores nothing and changes no committed file. Standard library only; it
imports no lab module.

It reads this directory's scored-m11.json, scored-m11.md and README.md, the measured pass's and the smoke's marks.jsonl and
telemetry.jsonl.gz (E97's conversion of the 34 raw codes, written out below, and the smoke gate's sample filter: status 0, no fault, 34
codes), the two passes' c-log.jsonl and ccheck/'s two .gz copies of them, and, as text only, the committed files of the repository that
the note's sections 3 and 5 cite (M11's REGISTRATION.md, its dated notes 1 and A4, design_power_heat_v2.py, score_m11.py and
score_m11_v4.py; the kit's runbook scripts in tools/claims-v3/e181/rb/).

    python3 -B docs/reports/data/2026-11-06-e181-m11-session2-aifoundry3/posthoc_note1_e181.py [--out <dir>]

It writes posthoc-note1-e181.json and posthoc-note1-e181.txt beside itself (or in --out), with paths relative to this directory or the
repository's top and no run time, so a re-run from the same tree writes them byte for byte. Exit 0 when it ran, 2 on a usage error.
SPDX-License-Identifier: Apache-2.0
"""
import glob
import gzip
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

sys.dont_write_bytecode = True
D = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(D, "..", "..", "..", ".."))
PASS = os.path.join("aifoundry3", "e181", "p18120")
SMOKE = os.path.join("aifoundry3", "e181-smoke", "p18101")
ORDER = ("H_E", "Z", "L1", "S", "L2")
PST = timezone(timedelta(hours=-8))   # Fri 6 Nov 2026 is standard time on the US west coast
HOLD_LINE_C = 72.0                    # a hold ends at 72 C (E181's registered stops, the README's peaks row)
G_TS, H_TS, CAL5 = 57400, 249400, 4096   # E97's conversion of a raw code (tools/claims-v3/e181/smoke_gate_e181.py, code_to_c)


def code_to_c(n):
    return (G_TS + H_TS * n / CAL5 - H_TS / 2) / 1000.0


def pst(t_ms):
    return datetime.fromtimestamp(t_ms / 1000.0, tz=PST).strftime("%H:%M:%S.%f")[:-3]


def jlines(p):
    op = gzip.open if p.endswith(".gz") else open
    out = []
    with op(p, "rt", encoding="utf-8") as f:
        for x in f:
            x = x.strip()
            if x.startswith("{"):
                out.append(json.loads(x))
    return out


def sample(r):
    """(t_ms, board W, the firmware's minshire[0] C, the 34-sensor mean C or None, filtered out of the mean?)"""
    pv = r.get("pvt") or {}
    c = pv.get("c")
    ok = pv.get("st") == 0 and pv.get("f") == 0 and isinstance(c, list) and len(c) == 34
    m34 = sum(code_to_c(x) for x in c) / 34.0 if ok else None
    ms = (r.get("temp_c") or {}).get("minshire")
    return r.get("t_ms"), r.get("board_w"), (ms[0] if ms else None), m34, not ok


def peaks(rows):
    b = [x for x in rows if x[1] is not None]
    fw = [x for x in rows if x[2] is not None]
    m = [x for x in rows if x[3] is not None]
    top_m = max(m, key=lambda x: x[3])
    return {"n_samples": len(rows), "n_out_of_the_34_mean": sum(1 for x in rows if x[4]),
            "board_max_W": max(x[1] for x in b), "board_mean_W": round(sum(x[1] for x in b) / len(b), 4),
            "firmware_max_C": max(x[2] for x in fw), "m34_max_C": round(top_m[3], 6), "m34_max_at_PST": pst(top_m[0]),
            "hot_max_C": round(max(max(x[2] for x in fw), top_m[3]), 6)}


def sha_file(p, unzip=False):
    h, n = hashlib.sha256(), 0
    op = gzip.open if unzip else open
    with op(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
            n += len(blk)
    return h.hexdigest(), n


def find_lines(rel, needles):
    """{needle: [1-based line numbers]} in a committed text file given relative to the repository's top"""
    with open(os.path.join(TOP, rel), encoding="utf-8") as f:
        txt = f.read().splitlines()
    return {k: [i + 1 for i, ln in enumerate(txt) if k in ln] for k in needles}


def readme_row(prefix):
    with open(os.path.join(D, "README.md"), encoding="utf-8") as f:
        for i, ln in enumerate(f.read().splitlines()):
            if ln.startswith(prefix):
                return i + 1, ln
    return None, ""


def printed(s, v):
    """does the printed string s equal the value v rounded to s's own decimals?"""
    nd = len(s.split(".")[1]) if "." in s else 0
    return f"{v:.{nd}f}" == s, f"{v:.{nd}f}"


def main(a):
    out_dir = D
    if a:
        if len(a) != 2 or a[0] != "--out":
            print(__doc__)
            return 2
        out_dir = os.path.abspath(a[1])
        os.makedirs(out_dir, exist_ok=True)
    sc = json.load(open(os.path.join(D, "scored-m11.json"), encoding="utf-8"))
    a3 = sc["aifoundry3"]
    sig = a3["sigma_c_C"]
    holds = sc["sessions"]["S2:p18120"]["holds"]
    marks = jlines(os.path.join(D, PASS, "marks.jsonl"))
    hm = {m["name"]: m for m in marks if m.get("kind") == "hold"}
    tel = [sample(r) for r in jlines(os.path.join(D, PASS, "telemetry.jsonl.gz"))]
    smk = [sample(r) for r in jlines(os.path.join(D, SMOKE, "telemetry.jsonl.gz"))]
    res = {"what": "E181's data README, dated note 1: post hoc figures from this directory's committed files (decides nothing)",
           "sigma_c_C": sig, "sigma_c_from": "scored-m11.json > aifoundry3 > sigma_c_C (REGISTRATION.md section 4)"}

    # 1. which holds ran warmer than the chain, and each hold's board peak (faults 1 and 4)
    h1 = {}
    for name in ORDER:
        s, m = holds[name], hm[name]
        rows = [x for x in tel if x[0] is not None and m["t_start_ms"] <= x[0] < m["t_end_ms"]]
        z = s["e_C"] / sig
        cls = "warmer than the chain (over 2 sigma_c)" if z > 2 else ("within 1 sigma_c" if abs(z) <= 1 else "between 1 and 2 sigma_c")
        h1[name] = {"item": s["item"], "P_C": s["P_C"], "R_C": s["R_C"], "e_C": s["e_C"], "e_over_sigma_c": round(z, 3),
                    "reads": cls, "window_PST": [pst(m["t_start_ms"]), pst(m["t_end_ms"])], "launches": m["launches"],
                    **peaks(rows)}
    res["holds"] = h1
    e4 = {n: round((holds[n]["e_C"] / sig) ** 2, 4) for n in ("L1", "S", "L2")}
    res["E4p_terms"] = {"terms_from_the_scored_e": e4, "sum": round(sum(e4.values()), 4),
                        "scored_X2": a3["HM_CAL_I8"]["E4p"]["X2"], "chi2_95_point": a3["HM_CAL_I8"]["E4p"]["chi2_95_point"],
                        "rule": "REGISTRATION.md.dated-note-A4.md, E4' (X2 = sum of (e / sigma_c)^2 over L1, S and L2)"}

    # 2. the README's printed peaks against the re-read values, at the README's own printed precision (fault 4)
    ln_p, row_p = readme_row("| peaks, pass 18120 |")
    ln_s, row_s = readme_row("| peaks, the smoke |")
    chk = []

    def cmp(label, s, v):
        ok, want = printed(s, v)
        chk.append({"what": label, "printed": s, "re_read": v, "at_the_printed_precision": want, "ok": ok})

    mt = re.search(r"H_E: board ([\d.]+) W, firmware (\d+) °C, 34-sensor mean ([\d.]+) °C at a ([\d.]+) °C room", row_p)
    cmp("H_E board max W", mt.group(1), h1["H_E"]["board_max_W"])
    cmp("H_E firmware max C", mt.group(2), h1["H_E"]["firmware_max_C"])
    cmp("H_E 34-sensor max C", mt.group(3), h1["H_E"]["m34_max_C"])
    sg = [m for m in marks if m.get("kind") == "start_gate"][0]
    cmp("the room at the start gate C", mt.group(4), sg["room_c"])
    for name in ("L1", "L2", "S", "Z"):
        mt = re.search(re.escape(name) + r" ([\d.]+) W, (\d+) / ([\d.]+) °C", row_p)
        cmp(f"{name} board max W", mt.group(1), h1[name]["board_max_W"])
        cmp(f"{name} firmware max C", mt.group(2), h1[name]["firmware_max_C"])
        cmp(f"{name} 34-sensor max C", mt.group(3), h1[name]["m34_max_C"])
    hot = max(h1[n]["hot_max_C"] for n in ORDER)
    mt = re.search(r"the closest, ([\d.]+) °C under the hold line", row_p)
    cmp("the closest margin under the 72 C hold line, C", mt.group(1), round(HOLD_LINE_C - hot, 6))
    sp = peaks(smk)
    mt = re.search(r"board ([\d.]+) W, firmware (\d+) °C, 34-sensor mean ([\d.]+) °C", row_s)
    cmp("smoke board max W", mt.group(1), sp["board_max_W"])
    cmp("smoke firmware max C", mt.group(2), sp["firmware_max_C"])
    cmp("smoke 34-sensor max C", mt.group(3), sp["m34_max_C"])
    res["readme_peaks_check"] = {"readme_lines": {"peaks, pass 18120": ln_p, "peaks, the smoke": ln_s}, "checks": chk,
                                 "differ": [c["what"] for c in chk if not c["ok"]], "smoke": sp,
                                 "pass_samples": len(tel), "smoke_samples": len(smk),
                                 "pass_out_of_the_34_mean": sum(1 for x in tel if x[4]),
                                 "smoke_out_of_the_34_mean": sum(1 for x in smk if x[4])}

    # 3. the x1.032 arm's "retired", read from one session (fault 2)
    with open(os.path.join(D, "scored-m11.md"), encoding="utf-8") as f:
        md_lines = [i + 1 for i, ln in enumerate(f.read().splitlines()) if "(arm retired)" in ln]
    res["arm_x1p032"] = {
        "A1_4": a3["A1_4"], "scored_md_lines_with_arm_retired": md_lines,
        "HM_LG": {k: a3["HM_LG"][k] for k in ("verdict", "k", "n", "F_null", "F_null_point", "null")},
        "null_rejected": a3["HM_LG"]["F_null"] > a3["HM_LG"]["F_null_point"],
        "M11_carries": a3["M11_carries"],
        "arm_rms_over_L1_S_L2_C": a3["HM_CAL"]["x1p032_arm_rms_later_C"], "arm_rms_on_L2_C": a3["HM_CAL_I8"]["x1p032_arm_rms_L2_C"],
        "text": {
            "tools/claims-v3/m11/REGISTRATION.md": find_lines("tools/claims-v3/m11/REGISTRATION.md", [
                "- **The ×1.032 arm** stays a reported arm unless", "SEPARATED with the null not rejected, the arm is retired from M11's readings.",
                "- With one session (k = 1), neither HM-AG nor S7-W can be read", "constant are reported as a candidate, labelled \"one session\"",
                "**aifoundry3: σ = 0.0884 °C**", "`H_L` (int8 −1s, R 4.25 °C), read"]),
            "tools/claims-v3/m11/REGISTRATION.md.dated-note-1.md": find_lines("tools/claims-v3/m11/REGISTRATION.md.dated-note-1.md", [
                "| NOT SEPARATED, the null not rejected | nothing | **retired** |",
                "With one session (k = 1) the table is the same, except that nothing enters (§ 6), so the arm is never replaced."]),
            "tools/claims-v3/m11/REGISTRATION.md.dated-note-A4.md": find_lines("tools/claims-v3/m11/REGISTRATION.md.dated-note-A4.md", [
                "4. **E4′:** the chain misses the int8 holds."]),
            "tools/claims-v3/m11/design_power_heat_v2.py": find_lines("tools/claims-v3/m11/design_power_heat_v2.py", [
                "def decide(groups, res, k, n, crit, crit_b, sigma_c):", "    if v == \"NOT SEPARATED\":",
                "        return \"nothing: NOT SEPARATED\", (\"retired\" if res[\"null\"] == \"the sessions agree\" else \"reported\")",
                "    if k < 2:", "        return \"nothing: one session (a candidate)\", arm_if_none"]),
            "tools/claims-v3/m11/score_m11.py": find_lines("tools/claims-v3/m11/score_m11.py", [
                "    o, fate = V2.decide(counted, res, k, n, crit, crit_b, sigma_c)"]),
            "tools/claims-v3/m11/score_m11_v4.py": find_lines("tools/claims-v3/m11/score_m11_v4.py", [
                "v4 imports v3 unchanged (v3 imports v2, v2 imports v1)"]),
            "README.md (this directory)": find_lines(os.path.relpath(os.path.join(D, "README.md"), TOP), [
                "| **what M11 carries** |", "every int8 hold after it", "and the zeros hold Z ran warmer than the chain"])}}

    # 4. the C logs held twice (fault 6)
    cl = {}
    for p, g in ((PASS, "ccheck/c-log-p18120.jsonl.gz"), (SMOKE, "ccheck/c-log-p18101.jsonl.gz")):
        h_raw, n_raw = sha_file(os.path.join(D, p, "c-log.jsonl"))
        h_gz, n_gz = sha_file(os.path.join(D, g), unzip=True)
        cl[os.path.join(p, "c-log.jsonl")] = {"bytes": n_raw, "sha256": h_raw, "copy": g, "copy_unpacked_bytes": n_gz,
                                              "copy_unpacked_sha256": h_gz, "copy_bytes": os.path.getsize(os.path.join(D, g)),
                                              "byte_identical": h_raw == h_gz and n_raw == n_gz}
    res["c_logs_twice"] = cl

    # 5. step 3 v2 and the window file (fault 5)
    rb = "tools/claims-v3/e181/rb"
    with open(os.path.join(TOP, rb, "s03_desk_e181_v2.sh"), encoding="utf-8") as f:
        s03 = f.read()
    callers = []
    for p in sorted(glob.glob(os.path.join(TOP, rb, "*.sh"))):
        with open(p, encoding="utf-8") as f:
            t = f.read()
        if "rb_window" in t:
            callers.append(os.path.basename(p))
    res["window"] = {"s03_v2_window_mentions": s03.count("window"), "s03_v2_rb_window_mentions": s03.count("rb_window"),
                     "rb_scripts_naming_rb_window": callers}

    with open(os.path.join(out_dir, "posthoc-note1-e181.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")

    T = ["# E181, dated note 1: post hoc figures from this directory's committed files (posthoc_note1_e181.py; decides nothing)", "",
         f"sigma_c {sig:.6f} C ({res['sigma_c_from']})", "",
         "## 1. The five holds: the chain's miss e = R - P and each hold's board (measured pass 18120, the hold marks' windows)"]
    for name in ORDER:
        h = h1[name]
        T.append(f"{name:3s} {h['item']:14s} P {h['P_C']:7.3f} R {h['R_C']:7.3f} e {h['e_C']:+.3f} C = {h['e_over_sigma_c']:+.2f} sigma_c, "
                 f"{h['reads']}; board max {h['board_max_W']:.2f} W mean {h['board_mean_W']:.2f} W; {h['n_samples']} samples "
                 f"{h['window_PST'][0]}-{h['window_PST'][1]} PST, {h['launches']} launches")
    e = res["E4p_terms"]
    T += [f"E4' terms (e / sigma_c)^2 from the scored e: L1 {e['terms_from_the_scored_e']['L1']:.4f}, S {e['terms_from_the_scored_e']['S']:.4f}, "
          f"L2 {e['terms_from_the_scored_e']['L2']:.4f}; sum {e['sum']:.4f} against the scored X2 {e['scored_X2']} (chi2 95% point "
          f"{e['chi2_95_point']})", "",
          "## 2. The README's printed peaks against the re-read values, at the printed precision (pass 18120's hold windows; the smoke's file)"]
    for c in res["readme_peaks_check"]["checks"]:
        T.append(f"{'OK     ' if c['ok'] else 'DIFFERS'} {c['what']}: printed {c['printed']}, re-read {c['re_read']}, so {c['at_the_printed_precision']}")
    r = res["readme_peaks_check"]
    T += [f"README lines: pass 18120's row {r['readme_lines']['peaks, pass 18120']}, the smoke's row {r['readme_lines']['peaks, the smoke']}; "
          f"samples {r['pass_samples']} (pass) and {r['smoke_samples']} (smoke), out of the 34-sensor mean {r['pass_out_of_the_34_mean']} and "
          f"{r['smoke_out_of_the_34_mean']}",
          "34-sensor peaks per hold: " + "; ".join(f"{n} {h1[n]['m34_max_C']:.4f} C at {h1[n]['m34_max_at_PST']} PST (firmware max "
                                                    f"{h1[n]['firmware_max_C']} C)" for n in ORDER), "",
          "## 3. The x1.032 arm's fate as printed, from one session"]
    am = res["arm_x1p032"]
    T += [f"scored-m11.json > aifoundry3 > A1_4: {json.dumps(am['A1_4'], sort_keys=True)}; scored-m11.md line(s) {am['scored_md_lines_with_arm_retired']}",
          f"HM-LG {am['HM_LG']['verdict']} at k {am['HM_LG']['k']} (n {am['HM_LG']['n']}): the null F {am['HM_LG']['F_null']} against "
          f"{am['HM_LG']['F_null_point']}, rejected {am['null_rejected']}; M11 carries: {am['M11_carries']}",
          f"the arm's rms reported: {am['arm_rms_over_L1_S_L2_C']} C over L1, S and L2; {am['arm_rms_on_L2_C']} C on L2"]
    for f_, d_ in am["text"].items():
        for k, v in d_.items():
            T.append(f"{f_}: line(s) {v}: {k}")
    T += ["", "## 4. The C logs held twice"]
    for p, c in cl.items():
        T.append(f"{p}: {c['bytes']} B, sha256 {c['sha256']}; {c['copy']} ({c['copy_bytes']} B) unpacked {c['copy_unpacked_bytes']} B, "
                 f"sha256 {c['copy_unpacked_sha256']}: byte-identical {c['byte_identical']}")
    w = res["window"]
    T += ["", "## 5. Step 3 v2 and the window file",
          f"s03_desk_e181_v2.sh: 'window' {w['s03_v2_window_mentions']} times, 'rb_window' {w['s03_v2_rb_window_mentions']} times; "
          "the rb scripts that name rb_window: " + ", ".join(w["rb_scripts_naming_rb_window"]), ""]
    with open(os.path.join(out_dir, "posthoc-note1-e181.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(T))
    print("\n".join(T))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
