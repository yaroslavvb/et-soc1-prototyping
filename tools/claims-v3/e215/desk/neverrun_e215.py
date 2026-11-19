#!/usr/bin/env python3
"""E215 (Q224) desk: which of E215's points never ran - arm A on aifoundry3 card 0 (MM1-v3.1's frozen points), arm B on aifoundry1 card 1 (the
points this registration chooses) - by E213's never-run scan, re-run at the registration, with the two post hoc readings MM1-v3.1's land named
for families L and S. Standard library only (MM1-v3.1's data loader for its measured points: numpy through it); reads files, writes only its report.

    python3 -I -B tools/claims-v3/e215/desk/neverrun_e215.py scan --lab <the lab at GitHub main> --lanes <W/out> --out <dir>
        reads every file under the lab's committed data folders (docs/reports/data), E212's and E208's committed schedules and arms, and the
        round's card and data lane folders under W/out (names starting card-, data-, a1, a2, a3), gzip read through - E213's scan
        (tools/claims-v3/e213/desk/neverrun_e213.py: its token rule, roots, folder classes and reader, imported unchanged at its pin) with E215's own
        folders SUBTRACTED (a data folder whose name holds '-e215-'; the lanes card-e215a and card-e215b); beside each token, the shire masks the
        files holding it name, by card class (family L's reading); the S kinds' tile names each card class's files name, and those the files
        holding gemmL3x1x3 name (family S's reading); MM1-v3.1's measured points (its data loader); writes <dir>/scan-e215.json
    python3 -I -B tools/claims-v3/e215/desk/neverrun_e215.py report --scan <scan-e215.json> --points <candidates JSON> --out <dir>
        writes <dir>/neverrun-e215.json and <dir>/neverrun-e215.txt (each point's verdict under its family's reading)

THE READINGS (E215.md section 4):
  literal (families P, C, R; DECLARED-v31.md item 10 step 1): THE TOKEN (E213's: gemmL<MB>x<NB>x<KB>, gemmLn.., gemmLnc.., matched whole: a
      SHAPE-LEVEL reading). Arm A: no hit on any card and no MM1-v3.1 measured point of the token on any card ('drop any point that ran
      anywhere since'). Arm B: no hit COUNTED for aifoundry1 card 1 (E213's classes: a folder naming card 1, naming no card, or naming
      aifoundry1 without a card) and no MM1-v3.1 measured point of the token on card 1.
  post hoc L (MM1-v3.1's land, README section 8; adopted by E215.md's dated departure D1): a CONFIGURATION (shape token, shire mask) that no
      MM1-v3.1 measured point holds and that no scanned file holding the shape token names (the masks as numbers). Arm A: any card; arm B:
      card 1's points and the files counted for card 1.
  post hoc S (the same departure): a counted kind never run in a GEMM on the arm's card - no MM1-v3.1 time or energy point of that format and
      kind on the card (MM1-v3.1's data holds every committed matmul point it read, E212's pattern sessions and E207's and E210's kinds
      among them), and no GEMM RUN RECORD naming one of the kind's tile files (or, for e37, its generator) in a folder counted for the card
      whose experiment lies outside MM1-v3.1's data (E214's seven sessions are the committed matmul runs since; a record is the host's values
      string <arm token>:<generator>:<tile files>, so a tile named only in an inventory, a listing or a SHA256SUMS file does not count);
      and for arm A, 'drop any point that ran anywhere since': no such record on any card and no MM1-v3.1 point of the kind at gemmL3x1x3.
      Tile names are matched as whole file names; every tile file under the lab's tools/claims-v3 tree byte-equal to a kind's tile adds its own
      name (REPORTED as an alias).
Not read: the model session's uncommitted folders (the orchestrator's rule of 23:18:35 PST Mon 16 Nov 2026); aifoundry1's and aifoundry3's own
disks (the round's card lanes copy their run folders back to W/out, read here); desk folders (registrations, models, kits, verifiers).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
E213_SCAN = ("tools/claims-v3/e213/desk/neverrun_e213.py", "d603ff8b4fac97a8adbafe0bf4ea0e99e555576c7601c93484362c0cd3500546")
V31 = os.path.join(REPO, "tools", "matmul", "mm1", "v3.1")
A3 = "aifoundry3 card 0"
C1 = "aifoundry1 card 1"
S_SHAPE = "gemmL3x1x3"
MRX = re.compile(r"0x[0-9a-fA-F]{1,8}\b")
# the S kinds' tiles, by kind key (format.kind as MM1-v3.1's energy code names them) -> the lab's tile files (and a generator, for e37)
S_TILES = {
    "fp32.pattern:bf16trunc": ["tools/claims-v3/e212/proposal/src/tiles/fp32/bf16trunc.bin"],
    "fp32.pattern:den16": ["tools/claims-v3/e212/proposal/src/tiles/fp32/den16.bin"],
    "fp32.pattern:den21": ["tools/claims-v3/e212/proposal/src/tiles/fp32/den21.bin"],
    "fp32.pattern:den4": ["tools/claims-v3/e212/proposal/src/tiles/fp32/den4.bin"],
    "fp32.pattern:den8": ["tools/claims-v3/e212/proposal/src/tiles/fp32/den8.bin"],
    "fp32.pattern:fld_mant": ["tools/claims-v3/e212/proposal/src/tiles/fp32/fld_mant.bin"],
    "fp32.pattern:fld_sign": ["tools/claims-v3/e212/proposal/src/tiles/fp32/fld_sign.bin"],
    "fp32.pattern:fp16grid": ["tools/claims-v3/e212/proposal/src/tiles/fp32/fp16grid.bin"],
    "fp32.pattern:lanes2": ["tools/claims-v3/e212/proposal/src/tiles/fp32/lanes2.bin"],
    "fp32.pattern:pow2": ["tools/claims-v3/e212/proposal/src/tiles/fp32/pow2.bin"],
    "fp32.real:blind4": ["tools/claims-v3/kinds/blind4/tiles/fp32/fp32.real_pythia_embed_qkv.bin",
                         "tools/claims-v3/kinds/blind4/tiles/fp32/fp32.real_qwen_q_down.bin"],
    "fp32.designed:blind3 a_colconst_b_randn": ["tools/claims-v3/kinds/blind3/tiles/fp32/a_colconst_b_randn.bin"],
    "fp32.e37": [],
    "int8.pattern:i8_den1": ["tools/claims-v3/e212/proposal/src/tiles/int8/i8_den1.bin"],
    "int8.pattern:i8_den3": ["tools/claims-v3/e212/proposal/src/tiles/int8/i8_den3.bin"],
    "int8.pattern:i8_den6": ["tools/claims-v3/e212/proposal/src/tiles/int8/i8_den6.bin"],
    "int8.pattern:i8_pm1": ["tools/claims-v3/e212/proposal/src/tiles/int8/i8_pm1.bin"],
    "int8.real:blind4": ["tools/claims-v3/kinds/blind4/tiles/int8/int8.real_pythia_embed_mlpout.bin",
                         "tools/claims-v3/kinds/blind4/tiles/int8/int8.real_qwen_q_down.bin"],
    "int8.real": ["tools/claims-v3/kinds/real2/tiles/int8/gpt2_l6_down_p999.bin", "tools/claims-v3/kinds/real2/tiles/int8/gpt2_l6_down_p9999.bin",
                  "tools/claims-v3/kinds/real2/tiles/int8/gpt2_l6_down_per_token.bin", "tools/claims-v3/kinds/real2/tiles/int8/gpt2_l11_down_p999.bin"],
}
# a GEMM run record's values string, as the lab's hosts print it: <arm token>:<generator>:<tile file>[,<tile file>...]
VRX = re.compile(r"(gemmL(?:n|nc)?\d+x\d+x\d+):([A-Za-z0-9_]+):([^\s\"',;\]\)]+(?:,[^\s\"',;\]\)]+)*)")


def folder_exps(rel):
    """the experiments a data or lane folder's name carries (three digits after 'e'), for family S's 'outside MM1-v3.1's data' test"""
    parts = rel.split("/")
    name = parts[3] if rel.startswith("docs/reports/data/") and len(parts) > 3 else (parts[2] if rel.startswith("W/out/") and len(parts) > 2 else
                                                                                   (parts[2] if len(parts) > 2 else rel))
    if rel.startswith("tools/claims-v3/e212/"):
        return ["212"]
    if rel.startswith("tools/claims-v3/e208/"):
        return ["208"]
    return sorted(set(re.findall(r"e(\d{2,3})(?![0-9])", name)))


def dedup_runs(v):
    files = sorted({r["file"] for r in v})
    exps = sorted({e for r in v for e in r["experiments"]})
    toks = sorted({r["token"] for r in v})
    by_exp = {}
    for r in v:
        key = ",".join(r["experiments"]) or "none"
        by_exp.setdefault(key, set()).add(r["file"])
    return {"n_records": len(v), "n_files": len(files), "files": files[:8], "tokens": toks[:12], "experiments": exps,
            "files_by_experiments": {k: sorted(x)[:4] for k, x in sorted(by_exp.items())}}


def now():
    return datetime.datetime.now(datetime.timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def e213_module():
    p = os.path.join(REPO, E213_SCAN[0])
    got = sha(p)
    if got != E213_SCAN[1]:
        print(f"neverrun_e215: REFUSED, {E213_SCAN[0]} is {got}, pinned {E213_SCAN[1]}")
        sys.exit(4)
    spec = importlib.util.spec_from_file_location("neverrun_e213", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def subtracted(rel):
    return ("-e215-" in rel) or rel.startswith("W/out/card-e215a/") or rel.startswith("W/out/card-e215b/")


def tile_names(lab):
    """every S kind's tile names, plus the names of byte-equal tile files anywhere under tools/claims-v3 (aliases)"""
    want = {}
    for k, fs in S_TILES.items():
        for f in fs:
            want.setdefault(sha(os.path.join(lab, f)), set()).add((k, os.path.basename(f)))
    names = {k: {os.path.basename(f) for f in fs} for k, fs in S_TILES.items()}
    aliases = {}
    top = os.path.join(lab, "tools", "claims-v3")
    for dp, dn, fns in os.walk(top):
        dn.sort()
        for fn in sorted(fns):
            if not fn.endswith(".bin"):
                continue
            p = os.path.join(dp, fn)
            try:
                if os.path.getsize(p) > 50_000_000:
                    continue
                h = sha(p)
            except OSError:
                continue
            for k, base in want.get(h, ()):
                if fn != base:
                    names[k].add(fn)
                aliases.setdefault(k, set()).add(os.path.relpath(p, lab))
    return names, {k: sorted(v) for k, v in aliases.items()}


def scan(lab, lanes, out):
    N = e213_module()
    t0 = now()
    expmap = N.exp_cards(lab)
    names, aliases = tile_names(lab)
    base_kind = {}
    for k, v in names.items():
        for n in v:
            base_kind.setdefault(n, set()).add(k)
    roots = [os.path.join(lab, "docs", "reports", "data"), os.path.join(lab, "tools", "claims-v3", "e212", "proposal", "src", "sched"),
             os.path.join(lab, "tools", "claims-v3", "e208", "proposal", "src")]
    lane_roots = sorted(os.path.join(lanes, d) for d in os.listdir(lanes) if d.startswith(("card-", "data-", "a1", "a2", "a3")))
    hits, masks, s_runs = {}, {}, {}
    nfiles, big, unreadable, git_dirs = 0, [], 0, 0
    for top in roots + lane_roots:
        for dp, dn, fns in os.walk(top):
            if ".git" in dn or ".git" in fns:
                dn[:] = []
                git_dirs += 1
                continue
            dn.sort()
            for fn in sorted(fns):
                p = os.path.join(dp, fn)
                if fn.endswith(N.SKIP_EXT) or os.path.islink(p):
                    continue
                try:
                    if os.path.getsize(p) > N.MAX_BYTES:
                        big.append(p)
                        continue
                    txt = N.read_text(p)
                except (OSError, EOFError):
                    unreadable += 1
                    continue
                nfiles += 1
                if nfiles % 20000 == 0:
                    print(f"scan: {nfiles} files read ({now()})", file=sys.stderr, flush=True)
                rel = os.path.relpath(p, lab) if p.startswith(lab + os.sep) else "W/out/" + os.path.relpath(p, lanes)
                c = "SUBTRACTED" if subtracted(rel) else (N.lane_card(rel) or N.folder_card(rel, expmap) or N.NONE)
                found = set(N.RX.findall(txt))
                if not found:
                    continue
                fm = sorted({"0x%x" % int(m, 16) for m in MRX.findall(txt)})
                for t in found:
                    hits.setdefault(t, {}).setdefault(c, []).append(rel)
                    mm = masks.setdefault(t, {}).setdefault(c, set())
                    mm.update(fm)
                # family S: GEMM run records - the host's values strings <arm>:<generator>:<tile files> naming an S kind's tile or generator
                if ":" in txt:
                    exps = folder_exps(rel)
                    for tok, gen, files in VRX.findall(txt):
                        ks = set()
                        for f in files.split(","):
                            ks |= base_kind.get(os.path.basename(f.strip()), set())
                        if gen == "e37":
                            ks.add("fp32.e37")
                        for k in ks:
                            s_runs.setdefault(k, {}).setdefault(c, []).append({"file": rel, "token": tok, "experiments": exps})
    # MM1-v3.1's measured points (its own data loader; every one a committed run)
    sys.path.insert(0, V31)
    import data_v31 as DV  # noqa: E402
    meas_tok, meas_cfg, meas_kind, meas_s = {}, {}, {}, {}
    v31_exps = {str(q["exp"]).lstrip("E") for q in DV.time_points() + DV.energy_points()}
    for p in DV.time_points():
        meas_tok.setdefault(p["arm"], set()).add((p["kernel"], p["card"]))
        meas_cfg.setdefault(p["arm"], {}).setdefault(p["card"], set()).add("0x%x" % int(p["mask"], 16))
        for k in str(p.get("kind", "")).split("+"):
            meas_kind.setdefault(f"{p['fmt']}.{k}", set()).add(p["card"])
            if p["arm"] == S_SHAPE:
                meas_s.setdefault(f"{p['fmt']}.{k}", set()).add(p["card"])
    for e in DV.energy_points():
        meas_kind.setdefault(f"{e['fmt']}.{e['kind']}", set()).add(e["card"])
        if e["arm"] == S_SHAPE:
            meas_s.setdefault(f"{e['fmt']}.{e['kind']}", set()).add(e["card"])
        meas_cfg.setdefault(e["arm"], {}).setdefault(e["card"], set()).add("0x%x" % int(e["mask"], 16))
    rec = {"what": "E215's never-run scan: E213's scan (its token rule, roots, folder classes and reader) with E215's folders subtracted; masks "
                   "by card class beside each token; the S kinds' tile names by card class; MM1-v3.1's measured points",
           "neverrun_e213_sha256": E213_SCAN[1], "started": t0, "ended": now(), "files_read": nfiles,
           "roots": [os.path.relpath(r, lab) for r in roots], "lane_roots": ["W/out/" + os.path.basename(r) for r in lane_roots],
           "over_400MB_not_read": [os.path.relpath(p, lanes) if p.startswith(lanes) else os.path.relpath(p, lab) for p in big],
           "unreadable": unreadable, "git_dirs_not_read": git_dirs,
           "tokens": {t: {c: {"n": len(v), "files": sorted(set(v))[:8]} for c, v in sorted(cs.items())} for t, cs in sorted(hits.items())},
           "masks_by_card": {t: {c: sorted(v) for c, v in sorted(cs.items())} for t, cs in sorted(masks.items())},
           "s_kind_tile_names": {k: sorted(v) for k, v in sorted(names.items())}, "s_kind_tile_aliases": aliases,
           "s_kind_gemm_runs_by_card": {k: {c: dedup_runs(v) for c, v in sorted(cs.items())} for k, cs in sorted(s_runs.items())},
           "mm1_v31_experiments": sorted(v31_exps),
           "mm1_v31_measured_tokens": {t: sorted(f"{k} on {c}" for k, c in v) for t, v in sorted(meas_tok.items())},
           "mm1_v31_measured_masks": {t: {c: sorted(v) for c, v in sorted(cs.items())} for t, cs in sorted(meas_cfg.items())},
           "mm1_v31_measured_kinds": {k: sorted(v) for k, v in sorted(meas_kind.items())},
           "mm1_v31_measured_kinds_at_gemmL3x1x3": {k: sorted(v) for k, v in sorted(meas_s.items())},
           "mm1_v31_data_sha256": {"data_v31.py": sha(os.path.join(V31, "data_v31.py"))}}
    os.makedirs(out, exist_ok=True)
    pth = os.path.join(out, "scan-e215.json")
    json.dump(rec, open(pth, "w"), indent=1, sort_keys=True)
    print(f"scan: {nfiles} files read, {len(hits)} distinct tokens, {len(big)} over 400 MB, {unreadable} unreadable, {git_dirs} git dirs not read; "
          f"{t0} - {rec['ended']}; scan-e215.json {sha(pth)}")


def counted_for(card, c):
    """E213's classes: a folder naming that card, naming no card (conservative), or naming aifoundry1 without a card (for an aifoundry1 card)"""
    if c == card or c == "no card named":
        return True
    if card in (C1, "aifoundry1 card 0") and c == "aifoundry1 (card not named)":
        return True
    return False


def verdict(S, p):
    """one point's verdict under its family's reading (the module docstring)"""
    arm, card = p["arm_tag"], (A3 if p["arm_tag"] == "A" else C1)
    tok = p["arm"]
    T = S["tokens"].get(tok, {})
    live = {c: v["n"] for c, v in T.items() if c != "SUBTRACTED"}
    on_card = {c: n for c, n in live.items() if counted_for(card, c)}
    other = {c: n for c, n in live.items() if not counted_for(card, c)}
    meas = S["mm1_v31_measured_tokens"].get(tok, [])
    meas_card = [m for m in meas if m.endswith(card)]
    reading = p["reading"]
    out = {"id": p["id"], "token": tok, "family": p["family"], "reading": reading, "kernel": p["kernel"], "role": p.get("role", "point"),
           "token_hits_on_card": on_card, "token_hits_other_cards": other, "token_subtracted": T.get("SUBTRACTED", {}).get("n", 0),
           "mm1_v31_measured_token": meas}
    if out["role"] != "point":
        never = (not live and not meas) if arm == "A" else (not on_card and not meas_card)
        out["rule"] = "a reference (run and read, never scored): the token rule REPORTED"
    elif reading == "literal":
        never = (not live and not meas) if arm == "A" else (not on_card and not meas_card)
        out["rule"] = "token: no hit on any card, no MM1-v3.1 point (arm A)" if arm == "A" else "token: no hit counted for card 1, no card-1 point (arm B)"
    elif p["family"] == "L":
        m = "0x%x" % int(p["mask"], 16)
        Mb = S["masks_by_card"].get(tok, {})
        Mm = S["mm1_v31_measured_masks"].get(tok, {})
        if arm == "A":
            named = sorted(c for c, ms in Mb.items() if c != "SUBTRACTED" and m in ms)
            mpt = sorted(c for c, ms in Mm.items() if m in ms)
        else:
            named = sorted(c for c, ms in Mb.items() if c != "SUBTRACTED" and counted_for(card, c) and m in ms)
            mpt = sorted(c for c, ms in Mm.items() if c == card and m in ms)
        never = not named and not mpt
        out.update({"mask": m, "mask_named_in_files_holding_token": named, "mask_in_mm1_v31_points": mpt,
                    "rule": "configuration (shape, mask): no MM1-v3.1 point and no file holding the token names the mask, "
                            + ("any card (arm A)" if arm == "A" else "card 1 (arm B)")})
    elif p["family"] == "S":
        k = f"{p['format']}.{p['kind']}"
        v31x = set(S["mm1_v31_experiments"])
        kc = S["mm1_v31_measured_kinds"].get(k, [])
        runs = S["s_kind_gemm_runs_by_card"].get(k, {})

        def outside(r):
            # a run record of an experiment outside MM1-v3.1's data (those inside are MM1-v3.1's measured points already), or of none named
            return not r["experiments"] or not set(r["experiments"]) <= v31x
        new_card = {c: r for c, r in runs.items() if c != "SUBTRACTED" and counted_for(card, c) and outside(r)}
        new_any = {c: r for c, r in runs.items() if c != "SUBTRACTED" and outside(r)}
        cfg_any = S["mm1_v31_measured_kinds_at_gemmL3x1x3"].get(k, [])
        ran_card = card in kc or bool(new_card)
        never = (not ran_card) and ((not new_any and not cfg_any) if arm == "A" else True)
        out.update({"kind_key": k, "kind_mm1_v31_points_by_card": kc,
                    "kind_gemm_runs_outside_mm1_v31_data_counted_for_card": {c: {"n_files": r["n_files"], "experiments": r["experiments"],
                                                                                   "files": r["files"][:3]} for c, r in new_card.items()},
                    "kind_gemm_runs_outside_mm1_v31_data_any_card": {c: {"n_files": r["n_files"], "experiments": r["experiments"]}
                                                                    for c, r in new_any.items()},
                    "kind_gemm_runs_inside_mm1_v31_data_REPORTED": {c: {"n_files": r["n_files"], "experiments": r["experiments"]}
                                                                    for c, r in runs.items() if c != "SUBTRACTED" and not outside(r)},
                    "configuration_gemmL3x1x3_mm1_v31_points": cfg_any,
                    "rule": ("kind: never run in a GEMM on the arm's card - no MM1-v3.1 point of the kind there, and no GEMM run record naming its "
                             "tiles in a folder counted for the card outside MM1-v3.1's data" + (
                                 "; and (arm A, ran anywhere since) no such record on any card, no MM1-v3.1 point at gemmL3x1x3 of the kind"
                                 if arm == "A" else ""))})
    else:
        raise SystemExit(f"neverrun_e215: no reading for {p['id']}")
    out["never_run"] = bool(never)
    return out


def report(scan_path, points_path, out):
    S = json.load(open(scan_path))
    P = json.load(open(points_path))
    res = {"what": "E215's never-run verdicts per point (desk/neverrun_e215.py report)", "scan_sha256": sha(scan_path),
           "candidates_sha256": sha(points_path), "scan_window": [S["started"], S["ended"]], "files_read": S["files_read"], "arms": {}}
    lines = []
    for arm in ("A", "B"):
        rows = [verdict(S, dict(p, arm_tag=arm)) for p in P["arms"][arm]]
        pts = [r for r in rows if r["role"] == "point"]
        res["arms"][arm] = {"card": A3 if arm == "A" else C1, "points": rows, "n_points": len(pts),
                            "n_never_run": sum(1 for r in pts if r["never_run"]),
                            "dropped": [r["id"] for r in pts if not r["never_run"]],
                            "references": [r["id"] for r in rows if r["role"] != "point"]}
        for r in rows:
            lines.append(f"{arm} {r['id']:5s} {r['family']} {r['reading']:7s} {r['token']:16s} never_run={r['never_run']} on_card={r['token_hits_on_card']} "
                         f"other={r['token_hits_other_cards']} measured={r['mm1_v31_measured_token'][:3]}"
                         + (f" mask={r.get('mask')} named={r.get('mask_named_in_files_holding_token')} pts={r.get('mask_in_mm1_v31_points')}"
                            if r["family"] == "L" else "")
                         + (f" kind={r.get('kind_key')} kind_pts={r.get('kind_mm1_v31_points_by_card')} "
                            f"new_runs_card={sorted(r.get('kind_gemm_runs_outside_mm1_v31_data_counted_for_card', {}))} "
                            f"new_runs_any={sorted(r.get('kind_gemm_runs_outside_mm1_v31_data_any_card', {}))} "
                            f"cfg={r.get('configuration_gemmL3x1x3_mm1_v31_points')}" if r["family"] == "S" else ""))
    json.dump(res, open(os.path.join(out, "neverrun-e215.json"), "w"), indent=1, sort_keys=True)
    head = [f"E215 never-run report; scan {res['scan_sha256'][:16]} ({S['files_read']} files, {S['started']} - {S['ended']})"]
    for arm in ("A", "B"):
        a = res["arms"][arm]
        head.append(f"arm {arm} ({a['card']}): {a['n_never_run']} of {a['n_points']} scored points never ran; dropped {a['dropped']}; references {a['references']}")
    open(os.path.join(out, "neverrun-e215.txt"), "w").write("\n".join(head + lines) + "\n")
    print("\n".join(head))


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    a1 = sp.add_parser("scan")
    a1.add_argument("--lab", required=True)
    a1.add_argument("--lanes", required=True)
    a1.add_argument("--out", required=True)
    a2 = sp.add_parser("report")
    a2.add_argument("--scan", required=True)
    a2.add_argument("--points", required=True)
    a2.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.cmd == "scan":
        scan(os.path.abspath(a.lab), os.path.abspath(a.lanes), a.out)
    else:
        report(a.scan, a.points, a.out)


if __name__ == "__main__":
    main()
