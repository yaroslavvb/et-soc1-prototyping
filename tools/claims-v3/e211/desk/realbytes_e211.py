#!/usr/bin/env python3
"""E211's REAL-BYTES desk test (Q204, lane kit-e211, Tue 17 Nov 2026, before any E211 datum; CONTEXT section 116's lesson: "every kit reads a
host's result from a source no runtime print can split ... and its real-path desk test feeds the parser the REAL stdout bytes committed from a
card"). Every parser, reducer path and identity reader of E211's kit, fed bytes committed from the cards, read-only (nothing here writes in the
repo). E206's desk/realbytes_e206.py form, as E207's kit ported it (Q199), with E206 arm A's own committed session on THIS card (rgm136's host,
binary and card, which E211's gemmL twins run) as the first case, and rgm211's host's own real bytes (the kit's simulator check) as the last:

  RB-E206   E206 arm A's committed rgm136 outputs on aifoundry3 card 0 (docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3/, data
            d7e4f35e: the smoke's 3 and the 241 runs' stdouts, the subset masks 0x1 ... 0x11111111 among them) through e211_common.host_records
            with each process's own committed command line: every record a plain reader reads is read, the same record, none unparsed, none
            naming another command, every runtime line counted (aifoundry3's runtime printed none);
  RB-E206R  E206 arm A's committed session's runs through reduce_e211.reduce_run (E206's per-run readings, line for line): every one of the
            241 runs' t_gemm_s, cycles_per_op, cycles_gemm, n_gemm, n_launch_counted, p_work_w, p_rest_w, die_start_c, die_c, mhz, mhz_min,
            mhz_max, checks, record, block and n EQUAL to E206's committed data-e206.json (made by E206's reducer); E211's reducer then writes
            them in the E211 scorer's form;
  RB-E190   E190's own rgm136 outputs on both cards (docs/reports/data/2026-11-13-e190-large-gemm/: every proc.out of the smoke and the runs,
            aifoundry2 and aifoundry1 card 1, 87 of them carrying aifoundry1's "Opening device 1" line) through host_records with each
            process's own command line: every record E190's own reader read is read, none unparsed, none naming another command, every
            runtime line counted;
  RB-E190R  E190's card-1 BURSTS (the same one-process form as E211's runs) through reduce_e211.reduce_run on E190's committed telemetry:
            t_gemm_s, p_work_w, p_rest_w, die_start_c, die_c, n_gemm, mhz and mhz_min equal E190's committed data-e190.json values;
  RB-SPLICE a runtime line ("Opening device 0" and "Opening device 1") spliced INTO E206's real aifoundry3 records at EVERY byte offset of a
            launch record and of the check record (a subset run's, mask 0x11111111, and a full-chip run's): each reads the same records, the
            line counted and its card named (a record cut short, or one naming another mask, is not read);
  RB-NEST   two runtime lines, one printed inside the other, spliced into the same real records at every byte offset: each reads the same
            records (drop_runtime runs until no runtime line is left);
  RB-SPLIT  the real split stdouts: 1a4bc1e3's smoke (the ledger host's line cut by "Opening device 1", the bytes that stopped E191's first
            session) and every 7156ac15 pass stdout that carries the runtime line: drop_runtime then last_json give exactly the host line that
            E191's kit note 2 committed as host-raw.json, and a whole JSON object with status PASS for 1a4bc1e3's;
  RB-CFG    config_json on E206 arm A's committed aifoundry3 config line (config-start.out) with a runtime line before, after and at every
            offset inside it: the committed config-start.json each time; a cut line is no reading;
  RB-ID     THE IDENTITY GATE on committed forms: it PASSES aifoundry3 card 0's committed reads (E206 arm A's config-start and config-end, E189's
            config with its sampler block) and its committed host blocks (E206 arm A's three smoke hosts, E196's host); it REFUSES card 1's
            (E190 arm B's and E191's two sessions' config reads, card 1's committed host block) and any read with its block removed; aifoundry2's
            card 0 (E190 arm A) passes the device block's gate as any card 0 does, and is told apart by the hostname (the box check and the
            guard refuse every box but aifoundry3: desk/desktest_build_e211.sh and desk/realpath_e211.sh show it);
  RB-SIM    rgm211's host's REAL bytes: the kit's own simulator check on aifoundry3 (logs/simcheck/<case>.out, the stdouts of rgm211's and
            rgm136's hosts built there, run under sys_emu; their home path written "~"), each through host_records with its own committed command
            line (every record read, none unparsed or naming another command) and walk_check by its arm family: walk nm, walk_ok true and
            walk_launches_bad 0 read OK for the gemmLn cases (fp32, int8, MB 1, NB 1), walk mn for gemmLnc; the wrong-ELF case (gemmLn on
            rgm136's ELF) read NOT OK (walk_ok false, walk_launches_bad 1); rgm136's host's records carry no walk; then a runtime line (cards 0
            and 1) and a nested pair spliced into rgm211's real launch record and check record at every byte offset: the same records, the walk
            fields whole, the walk read the same.
    /usr/bin/python3 -I -B tools/claims-v3/e211/desk/realbytes_e211.py > logs/realbytes-e211.txt      (last line: REALBYTES-E211 <n> of <m> PASS)
A desk read of committed records and a desk check of code: nothing here is measured. SPDX-License-Identifier: Apache-2.0
"""
import glob
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
sys.path.insert(0, E)
import e211_common as C  # noqa: E402
import e211_ident as N1  # noqa: E402
import reduce_e211 as RD  # noqa: E402

DATA = os.path.join(REPO, "docs/reports/data")
E206D = os.path.join(DATA, "2026-11-16-e206-matmul-sweep-aifoundry3")
E190D = os.path.join(DATA, "2026-11-13-e190-large-gemm")
E191A = os.path.join(DATA, "2026-11-15-e191-blind-day-aifoundry1-c1")
E191B = os.path.join(DATA, "2026-11-15-e191-blind-day-aifoundry1-c1-s2")
E189 = os.path.join(DATA, "2026-11-14-e189-blind-day-aifoundry3")
E196 = os.path.join(DATA, "2026-11-16-e196-zeroshare-aifoundry3")


class T:
    def __init__(self):
        self.n = self.ok = 0

    def case(self, name, good, detail):
        self.n += 1
        self.ok += 1 if good else 0
        print(f"{name}: {'PASS' if good else 'FAIL'} - {detail}", flush=True)


def plain_parse(text):
    """A plain reader (E190's e190_common.parse_sparsity, line for line): the lines that start with 'SPARSITY ', each json.loads'ed."""
    out = []
    for ln in text.splitlines():
        if ln.startswith("SPARSITY "):
            try:
                out.append(json.loads(ln[9:]))
            except ValueError:
                pass
    return out


def proc_argv(pdir, name):
    """A committed process's command line, from its run.json (runs) or smoke.json (the smoke)."""
    for f in ("run.json", "smoke.json"):
        p = os.path.join(pdir, f)
        if os.path.exists(p):
            j = json.load(open(p))
            for pr in j.get("procs", []) or [j]:
                if pr.get("name") == name:
                    return pr.get("argv")
    return None


def by_time(recs):
    return sorted(recs, key=lambda r: (r.get("t_start_ms") or 0, r.get("launch") or 0, r.get("test") or ""))


def parse_all(files, label_root):
    n_rec = n_rt = 0
    bad = []
    for p in files:
        text = open(p, errors="replace").read()
        argv = proc_argv(os.path.dirname(p), os.path.basename(p)[:-4])
        fma, chk, info = C.host_records(text, argv)
        want = [r for r in plain_parse(text) if r.get("test") in ("fma", "check")]
        got = by_time(fma + chk)
        n_rec += len(got)
        n_rt += len(info["runtime_lines"])
        if argv is None or got != by_time(want) or info["unparsed"] or info["mismatched"] or text.count("Opening device") != len(info["runtime_lines"]):
            bad.append(f"{os.path.relpath(p, label_root)}: {len(got)} of {len(want)} records, unparsed {info['unparsed']}, mismatched "
                       f"{len(info['mismatched'])}, argv {argv is not None}")
    return n_rec, n_rt, bad


def splice_cases(text, argv, lines_to_splice):
    """Every byte offset of each given record line: one runtime line (cards 0 and 1), then a nested pair; (n single, n nested, bad)."""
    base_f, base_c, _ = C.host_records(text, argv)
    n1 = n2 = 0
    bad = []
    for which in lines_to_splice:
        for card in ("0", "1"):
            for k in range(len(which) + 1):
                sp = text.replace(which, which[:k] + f"Opening device {card}\n" + which[k:], 1)
                f_, c_, inf = C.host_records(sp, argv)
                n1 += 1
                if f_ != base_f or c_ != base_c or C.runtime_cards(inf["runtime_lines"]) != [card] or inf["unparsed"] or inf["mismatched"]:
                    bad.append(("single", card, k))
        outer = "Opening device 1\n"
        for j in (3, 9, 15, 16):
            pair = outer[:j] + "Opening device 0\n" + outer[j:]
            for k in range(len(which) + 1):
                sp = text.replace(which, which[:k] + pair + which[k:], 1)
                f_, c_, inf = C.host_records(sp, argv)
                n2 += 1
                if f_ != base_f or c_ != base_c or sorted(C.runtime_cards(inf["runtime_lines"])) != ["0", "1"] or inf["unparsed"]:
                    bad.append(("nested", j, k))
    return n1, n2, bad, base_f


def main():
    t = T()
    print(f"realbytes_e211 ({sys.executable} {sys.version.split()[0]}), {time.strftime('%Y-%m-%d %H:%M:%S %Z')}; reading the committed data of "
          f"<lab clone>/docs/reports/data (read only)", flush=True)
    sd6 = os.path.join(E206D, "session")
    # ---- RB-E206: every committed rgm136 stdout of E206 arm A on this card
    files6 = sorted(glob.glob(os.path.join(sd6, "smoke", "*", "proc.out")) + glob.glob(os.path.join(sd6, "runs", "*", "proc-*.out")))
    n_rec, n_rt, bad = parse_all(files6, E206D)
    masks = set()
    for p in files6:
        a = proc_argv(os.path.dirname(p), os.path.basename(p)[:-4]) or []
        masks.add(C.arg_of(a, "--shires"))
    t.case("RB-E206", len(files6) == 244 and not bad and n_rec > 0 and n_rt == 0 and len(masks) >= 5,
           f"{len(files6)} committed aifoundry3 card-0 stdouts (the smoke's 3, the runs' 241; masks {sorted(masks)}), {n_rec} records read as a "
           f"plain reader reads them, each checked against its own command line; {n_rt} runtime lines (aifoundry3's runtime printed none)"
           f"{'; ' + '; '.join(bad[:3]) if bad else ''}")
    # ---- RB-E206R: E206 arm A's committed session's runs through E211's reducer's per-run readings, against E206's committed data-e206.json
    ref = json.load(open(os.path.join(E206D, "data-e206.json")))["arms"]["A"]
    tel = RD.load_tel(sd6)
    keys = ("t_gemm_s", "cycles_per_op", "cycles_gemm", "n_gemm", "n_launch_counted", "p_work_w", "p_rest_w", "die_start_c", "die_c", "mhz",
            "mhz_min", "mhz_max", "checks", "record", "block", "n")
    diffs, nr = [], 0
    refruns = [r for P in ref["points"].values() for r in P["runs"]] + list(ref["ties"]["runs"])
    for run in refruns:
        key = (run.get("detail") or {}).get("run")
        rj = os.path.join(sd6, "runs", str(key), "run.json")
        if not key or not os.path.exists(rj):
            diffs.append(f"{key}: no run.json")
            continue
        mine = RD.reduce_run(os.path.join(sd6, "runs", key), json.load(open(rj)), tel)
        nr += 1
        bad = [k for k in keys if mine.get(k) != run.get(k)]
        if bad:
            diffs.append(f"{key}: {bad[:4]}")
    t.case("RB-E206R", nr == 241 and not diffs, f"{nr} runs (119 points and 3 ties): reduce_e211.reduce_run gives E206's committed data-e206.json "
           f"run fields ({', '.join(keys)}) equal ({'equal' if not diffs else 'DIFFER: ' + '; '.join(diffs[:4])}); {len(tel)} committed samples read")
    # ---- RB-E190: every committed rgm136 stdout of E190, both cards
    files = sorted(glob.glob(os.path.join(E190D, "*", "smoke", "*", "proc.out")) + glob.glob(os.path.join(E190D, "*", "runs", "*", "proc-*.out")))
    n_rec, n_rt, bad = parse_all(files, E190D)
    t.case("RB-E190", len(files) == 174 and not bad and n_rt == 87 and n_rec > 0,
           f"{len(files)} committed stdouts (both cards), {n_rec} records read as E190's reader read them, {n_rt} runtime lines dropped"
           f"{'; ' + '; '.join(bad[:3]) if bad else ''}")
    # ---- RB-E190R: E190's card-1 bursts through reduce_e211.reduce_run, against E190's committed reduction
    d190 = json.load(open(os.path.join(E190D, "data-e190.json")))["arms"]["B"]
    sd = os.path.join(E190D, "aifoundry1-c1")
    tel = RD.load_tel(sd)
    worst, n, bad = 0.0, 0, []
    for cell, c in d190["cells"].items():
        if not cell.endswith(".burst"):
            continue
        for r in c["runs"]:
            rj = json.load(open(os.path.join(sd, "runs", r["run"], "run.json")))
            rec = {"run": r["run"], "n": rj["i"], "block": rj["block"], "id": rj["format"], "procs": rj["procs"], "flags": rj.get("flags", [])}
            m = RD.reduce_run(os.path.join(sd, "runs", r["run"]), rec, tel)
            n += 1
            for k in ("t_gemm_s", "p_work_w", "p_rest_w", "die_start_c", "die_c", "n_gemm", "mhz", "mhz_min"):
                a, b = m.get(k), r.get(k)
                if a is None or b is None:
                    bad.append(f"{r['run']} {k}: {a} vs {b}")
                    continue
                rel = abs(a - b) / max(abs(b), 1e-12)
                worst = max(worst, rel)
                if rel > 1e-12:
                    bad.append(f"{r['run']} {k}: {a} vs {b}")
    t.case("RB-E190R", n == 12 and not bad, f"{n} card-1 bursts; t_gemm, p_work, p_rest, die_start, die, n_gemm, mhz, mhz_min against data-e190.json: "
           f"worst relative difference {worst:.1e}{'; ' + '; '.join(bad[:3]) if bad else ''}")
    # ---- RB-SPLICE and RB-NEST: runtime lines spliced into E206's real aifoundry3 records (a subset run's and a full-chip run's)
    rq = json.load(open(os.path.join(E206D, "data-e206.json")))
    sub = None
    for key in sorted(os.listdir(os.path.join(sd6, "runs"))):
        a = proc_argv(os.path.join(sd6, "runs", key), "proc-00") or []
        if C.arg_of(a, "--shires") == "0x11111111" and sub is None:
            sub = key
    n1 = n2 = 0
    bad_all, cut_ok, oth_ok = [], True, True
    for key in (sub, "001-tie-p001"):
        p = os.path.join(sd6, "runs", key, "proc-00.out")
        text = open(p).read()
        argv = proc_argv(os.path.dirname(p), "proc-00")
        lines = [ln for ln in text.split("\n") if ln.startswith("SPARSITY ")]
        a1, a2, bad, base_f = splice_cases(text, argv, (lines[1], lines[-1]))
        n1 += a1
        n2 += a2
        bad_all += [(key,) + b for b in bad]
        cut = text.replace(lines[1], lines[1][:120], 1)
        f_cut, _, inf_cut = C.host_records(cut, argv)
        cut_ok = cut_ok and len(f_cut) == len(base_f) - 1 and inf_cut["unparsed"] == 1
        mk = C.arg_of(argv, "--shires")
        other = text.replace(f'"shire_mask":"{mk}"', '"shire_mask":"0x3"', 1)
        f_oth, _, inf_oth = C.host_records(other, argv)
        oth_ok = oth_ok and len(f_oth) == len(base_f) - 1 and len(inf_oth["mismatched"]) == 1
    singles = [b for b in bad_all if b[1] == "single"]
    nests = [b for b in bad_all if b[1] == "nested"]
    t.case("RB-SPLICE", sub is not None and not singles and n1 > 1500 and cut_ok and oth_ok,
           f"{n1} offsets (runtime lines of card 0 and of card 1) in a real launch record and its check record of E206's {sub} (mask 0x11111111) "
           f"and 001-tie-p001 (the full chip, E206's tie): every one read the same records, the line counted and its card named; a record cut "
           f"short not read; a record naming another mask not read{'; bad ' + str(singles[:4]) if singles else ''}")
    t.case("RB-NEST", not nests and n2 > 2500, f"{n2} splices of a nested pair of runtime lines (the inner at 4 places in the outer) into the same "
           f"real records: every one read the same records, both lines counted and their cards named{'; bad ' + str(nests[:4]) if nests else ''}")
    # ---- RB-SPLIT: the real split stdouts of 1a4bc1e3 and 7156ac15
    s1 = os.path.join(E191A, "session", "smoke", "copy-64m-random", "stdout.txt")
    raw = open(s1).read()
    body, rt = C.drop_runtime(raw)
    j1 = C.last_json(body)
    naive = {}
    for ln in reversed(raw.splitlines()):
        if ln.startswith("{"):
            try:
                naive = json.loads(ln)
            except ValueError:
                naive = {}
            break
    ok1 = rt == ["Opening device 1"] and j1.get("ledger") == 1 and j1.get("status") == "PASS" and j1.get("records_ok") == 2048 and naive == {}
    pairs, bad = 0, []
    for so in sorted(glob.glob(os.path.join(E191B, "passes", "*", "*", "stdout.txt"))):
        raw2 = open(so).read()
        if "Opening device" not in raw2:
            continue
        hr = os.path.join(os.path.dirname(so), "host-raw.json")
        if not os.path.exists(hr):
            continue
        body2, rt2 = C.drop_runtime(raw2)
        pairs += 1
        if C.last_json(body2) != json.load(open(hr)) or not rt2:
            bad.append(os.path.relpath(so, E191B))
    t.case("RB-SPLIT", ok1 and pairs >= 20 and not bad, f"1a4bc1e3's smoke stdout: the runtime line dropped, the host's line whole (ledger 1, status "
           f"{j1.get('status')}, records_ok {j1.get('records_ok')}) where the first-'{{'-line reader read nothing ({naive == {}}); 7156ac15: {pairs} split "
           f"pass stdouts, each read equal to its committed host-raw.json{'; differ: ' + ', '.join(bad[:3]) if bad else ''}")
    # ---- RB-CFG: E206 arm A's committed aifoundry3 config line, with runtime lines around and inside it
    cj = json.load(open(os.path.join(sd6, "config-start.json")))
    line = open(os.path.join(sd6, "config-start.out")).read().strip()
    ok = C.config_json(line + "\n") == cj and C.config_json("Opening device 0\n" + line + "\n") == cj and C.config_json(line + "\nOpening device 1\n") == cj
    okk = all(C.config_json(line[:k] + f"Opening device {c}\n" + line[k:] + "\n") == cj for k in range(len(line) + 1) for c in ("0", "1"))
    t.case("RB-CFG", ok and okk and C.config_json(line[:40] + "\n") == {} and C.config_ok("A", cj),
           f"E206 arm A's committed config line ({line[:60]}...): read as its committed config-start.json, with a runtime line before, after and at "
           f"every one of its {len(line) + 1} offsets (cards 0 and 1); a cut line is no reading; the line passes the start config gate (TDP 0 W / 65 C / 600 MHz)")
    # ---- RB-ID: the identity gate on committed forms
    def cfg(d, name="config-start"):
        return json.load(open(os.path.join(d, name + ".json"))), open(os.path.join(d, name + ".err"), errors="replace").read()
    rows = []
    for nm in ("config-start", "config-end"):
        j, err = cfg(sd6, nm)
        rows.append((f"E206 arm A {nm} (aifoundry3 card 0)", j, err, True))
        rows.append((f"E206 arm A {nm} with its block removed", j, "\n".join(x for x in err.splitlines() if not x.startswith(("PCIe target", "Physical device ID"))), False))
    a3err = open(os.path.join(E189, "session", "sampler.err"), errors="replace").read()
    a3cfg = json.load(open(os.path.join(E189, "session", "config-start.json")))
    rows.append(("aifoundry3's E189 forms (its sampler block, its 523 mV config)", a3cfg, a3err, True))
    for label, d in (("E190 arm B (card 1)", os.path.join(E190D, "aifoundry1-c1")), ("E191 session 1 (card 1)", os.path.join(E191A, "session")),
                     ("E191 session 2 (card 1)", os.path.join(E191B, "session"))):
        for nm in ("config-start", "config-end"):
            j, err = cfg(d, nm)
            rows.append((f"{label} {nm}", j, err, False))
    j2, e2 = cfg(os.path.join(E190D, "aifoundry2"))
    rows.append(("aifoundry2's card 0 (E190 arm A): the device block's gate passes it, as any card 0 (the hostname tells the box)", j2, e2, True))
    bad = [r[0] for r in rows if (N1.config_identity("A", r[1], r[2]) == "") != r[3]]
    hosts = []
    for pid in ("p001", "p046", "p021"):
        tg, ids = N1.parse_ident(open(os.path.join(sd6, "smoke", pid, "proc.err"), errors="replace").read())
        w, r = N1.host_identity("A", tg, ids, set())
        hosts.append(not w and r)
    tg3, ids3 = N1.parse_ident(open(os.path.join(E196, "run", "stderr.txt"), errors="replace").read())
    w3, r3 = N1.host_identity("A", tg3, ids3, set())
    hb = open(os.path.join(E190D, "aifoundry1-c1", "smoke", "fp32", "proc.err"), errors="replace").read()
    tg1, ids1 = N1.parse_ident(hb)
    w1, r1 = N1.host_identity("A", tg1, ids1, set())
    tgs, idss = N1.parse_ident(open(os.path.join(sd6, "sampler.err"), errors="replace").read())
    hosts_ok = all(hosts) and not w3 and r3 and w1 and not r1 and set(tgs) == {("0", "mgmt")} and set(idss) == {0}
    t.case("RB-ID", not bad and hosts_ok and len(rows) == 12,
           f"{len(rows)} committed config forms, each passed or refused as stated ({'none' if not bad else 'WRONG: ' + '; '.join(bad[:4])}); E206 arm A's "
           f"three smoke host blocks pass ({hosts}); E196's aifoundry3 host block passes ({r3}); card 1's committed host block is refused ({w1[:1]}); "
           f"E206 arm A's committed sampler block names {sorted(set(tgs))} {sorted(set(idss))}")
    # ---- RB-SIM: rgm211's host's real bytes (the kit's simulator check on aifoundry3)
    SD = os.path.join(E, "logs", "simcheck")
    want = {"W": ("gemmLn", True), "Wi": ("gemmLn", True), "X": ("gemmLn", True), "Xb": ("gemmLn", True), "C": ("gemmLnc", True),
            "BAD": ("gemmLn", False), "Cn": ("gemmLnc", True)}
    bad, nrec, seen = [], 0, {}
    for case in sorted(os.listdir(SD)) if os.path.isdir(SD) else []:
        if not case.endswith(".out"):
            continue
        c = case[:-4]
        meta = json.load(open(os.path.join(SD, c + ".json")))
        text = open(os.path.join(SD, case)).read()
        argv = meta["argv"]
        fma, chk, info = C.host_records(text, argv)
        plain = [r for r in plain_parse(text) if r.get("test") in ("fma", "check")]
        nrec += len(fma) + len(chk)
        if by_time(fma + chk) != by_time(plain) or info["unparsed"] or info["mismatched"] or not fma or not chk:
            bad.append(f"{c}: {len(fma) + len(chk)} of {len(plain)} records, unparsed {info['unparsed']}, mismatched {len(info['mismatched'])}")
            continue
        if c in want:
            fam, ok_want = want[c]
            ok, words, det = C.walk_check(fam, fma, chk)
            seen[c] = ok
            if ok != ok_want or (c == "BAD" and det.get("launches_bad") != 1):
                bad.append(f"{c}: walk read {ok} ({words[:80]}), want {ok_want}")
        elif meta["host"] == "rgm136" and any("walk" in r for r in fma + chk):
            bad.append(f"{c}: rgm136's host's records carry a walk field")
    w = os.path.join(SD, "W.out")
    n1 = n2 = 0
    if os.path.exists(w):
        text = open(w).read()
        argv = json.load(open(os.path.join(SD, "W.json")))["argv"]
        lines = [ln for ln in text.splitlines() if ln.startswith("SPARSITY ")]
        n1, n2, sbad, basef = splice_cases(text, argv, lines)
        if sbad:
            bad.append(f"splices: {len(sbad)} differ, the first {sbad[:2]}")
        for which in lines:
            for k in range(0, len(which) + 1, 3):
                sp = text.replace(which, which[:k] + "Opening device 1\n" + which[k:], 1)
                f_, c_, inf = C.host_records(sp, argv)
                if not C.walk_check("gemmLn", f_, c_)[0]:
                    bad.append(f"the walk read differs with a runtime line at {k}")
                    break
    t.case("RB-SIM", not bad and len(seen) == len(want) and n1 > 500 and n2 > 1000,
           f"{len(os.listdir(SD)) // 2 if os.path.isdir(SD) else 0} simulator stdouts of the two hosts built on aifoundry3, {nrec} records read as a "
           f"plain reader reads them, each against its own command line; the walk read by family {seen}; {n1} single and {n2} nested runtime-line "
           f"splices into rgm211's real records read the same records and the same walk{'; ' + '; '.join(bad[:3]) if bad else ''}")
    print(f"REALBYTES-E211 {t.ok} of {t.n} {'PASS' if t.ok == t.n else 'FAIL'}")
    return 0 if t.ok == t.n else 1


if __name__ == "__main__":
    sys.exit(main())
