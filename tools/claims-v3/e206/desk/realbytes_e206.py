#!/usr/bin/env python3
"""E206's REAL-BYTES desk test (Q198, lane kit-e206, Mon 16 Nov 2026, before any E206 datum; CONTEXT section 116's lesson: "every kit reads a
host's result from a source no runtime print can split ... and its real-path desk test feeds the parser the REAL stdout bytes committed from a
card"). Every parser and identity reader of E206's kit, fed bytes committed from the cards, read-only (nothing here writes in the repo):

  RB-E190   E190's own rgm136 outputs on both cards (docs/reports/data/2026-11-13-e190-large-gemm/: every proc.out of the smoke and the runs,
            aifoundry2 and aifoundry1 card 1, 87 of them carrying aifoundry1's "Opening device 1" line) through e206_common.host_records with
            each process's own committed command line: every record E190's own reader (e190_common.parse_sparsity) read is read, the same
            record, none unparsed, none naming another command, every runtime line counted;
  RB-E190R  E190's card-1 BURSTS (the same one-process form as E206's runs) through reduce_e206.reduce_run on E190's committed telemetry:
            t_gemm_s, p_work_w, p_rest_w, die_start_c, die_c, n_gemm, mhz and mhz_min equal E190's committed data-e190.json values;
  RB-SPLICE aifoundry1's runtime line spliced INTO E190's real card-1 records at EVERY byte offset of a launch record and of the check record:
            each reads the same record, the runtime line counted (and a record cut short, or one naming another mask, is not read);
  RB-NEST   (fix-e206, before any E206 datum; the verifier's finding 9) two runtime lines, one printed inside the other, spliced into the same
            real records at every byte offset: each reads the same records (drop_runtime runs until no runtime line is left);
  RB-SPLIT  the real split stdouts: 1a4bc1e3's smoke (the ledger host's line cut by "Opening device 1", the bytes that stopped E191's first
            session) and every 7156ac15 pass stdout that carries the runtime line: drop_runtime then last_json give exactly the host line that
            E191's kit note 2 committed as host-raw.json (7156ac15), and a whole JSON object with status PASS for 1a4bc1e3's;
  RB-CFG    config_json on committed config lines with the runtime line before and inside the read's stdout;
  RB-ID     THE IDENTITY GATE BOTH WAYS on committed forms: arm B passes card 1's committed config reads (E190 arm B's, E191's two sessions')
            and their hosts' and sampler's blocks; it REFUSES card 0's forms (aifoundry2's committed config read, 519 mV; aifoundry3's
            sampler block with E189's 523 mV config) and a read with its block removed; arm A passes aifoundry3's committed forms (E189's
            sampler block and config, E196's host block) and refuses card 1's.
    /usr/bin/python3 -I -B tools/claims-v3/e206/desk/realbytes_e206.py > logs/realbytes-e206.txt      (last line: REALBYTES-E206 <n> of <m> PASS)
A desk read of committed records and a desk check of code: nothing here is measured. SPDX-License-Identifier: Apache-2.0
"""
import glob
import gzip
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
sys.path.insert(0, E)
import e206_common as C  # noqa: E402
import e206_ident as N1  # noqa: E402
import reduce_e206 as RD  # noqa: E402

DATA = os.path.join(REPO, "docs/reports/data")
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


def e190_parse(text):
    """E190's own reader (e190_common.parse_sparsity, line for line): the lines that start with 'SPARSITY ', each json.loads'ed."""
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


def main():
    t = T()
    print(f"realbytes_e206 ({sys.executable} {sys.version.split()[0]}), {time.strftime('%Y-%m-%d %H:%M:%S %Z')}; reading the committed data of "
          f"<lab clone>/docs/reports/data (read only)", flush=True)
    # ---- RB-E190: every committed rgm136 stdout of E190, both cards
    files = sorted(glob.glob(os.path.join(E190D, "*", "smoke", "*", "proc.out")) + glob.glob(os.path.join(E190D, "*", "runs", "*", "proc-*.out")))
    n_rec = n_rt = n_files = 0
    bad = []
    for p in files:
        text = open(p, errors="replace").read()
        argv = proc_argv(os.path.dirname(p), os.path.basename(p)[:-4])
        fma, chk, info = C.host_records(text, argv)
        want = [r for r in e190_parse(text) if r.get("test") in ("fma", "check")]
        got = sorted(fma + chk, key=lambda r: (r.get("t_start_ms") or 0, r.get("launch") or 0))
        want = sorted(want, key=lambda r: (r.get("t_start_ms") or 0, r.get("launch") or 0))
        n_files += 1
        n_rec += len(got)
        n_rt += len(info["runtime_lines"])
        if argv is None or got != want or info["unparsed"] or info["mismatched"] or text.count("Opening device") != len(info["runtime_lines"]):
            bad.append(f"{os.path.relpath(p, E190D)}: {len(got)} of {len(want)} records, unparsed {info['unparsed']}, mismatched {len(info['mismatched'])}, argv {argv is not None}")
    t.case("RB-E190", n_files == 174 and not bad and n_rt == 87 and n_rec > 0,
           f"{n_files} committed stdouts (both cards), {n_rec} records read as E190's reader read them, {n_rt} runtime lines dropped"
           f"{'; ' + '; '.join(bad[:3]) if bad else ''}")
    # ---- RB-E190R: E190's card-1 bursts through reduce_e206.reduce_run, against E190's committed reduction
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
            mine = RD.reduce_run(os.path.join(sd, "runs", r["run"]), rec, tel)
            n += 1
            for k in ("t_gemm_s", "p_work_w", "p_rest_w", "die_start_c", "die_c", "n_gemm", "mhz", "mhz_min"):
                a, b = mine.get(k), r.get(k)
                if a is None or b is None:
                    bad.append(f"{r['run']} {k}: {a} vs {b}")
                    continue
                rel = abs(a - b) / max(abs(b), 1e-12)
                worst = max(worst, rel)
                if rel > 1e-12:
                    bad.append(f"{r['run']} {k}: {a} vs {b}")
    t.case("RB-E190R", n == 12 and not bad, f"{n} card-1 bursts; t_gemm, p_work, p_rest, die_start, die, n_gemm, mhz, mhz_min against data-e190.json: "
           f"worst relative difference {worst:.1e}{'; ' + '; '.join(bad[:3]) if bad else ''}")
    # ---- RB-SPLICE: the runtime line at every byte offset of a real card-1 launch record and of its check record
    p = os.path.join(E190D, "aifoundry1-c1", "smoke", "fp32", "proc.out")
    text = open(p).read()
    argv = proc_argv(os.path.dirname(p), "proc")
    lines = [ln for ln in text.split("\n") if ln.startswith("SPARSITY ")]
    base_f, base_c, _ = C.host_records(text, argv)
    n_off, bad = 0, []
    for which in (lines[1], lines[-1]):
        for k in range(len(which) + 1):
            spliced = text.replace(which, which[:k] + "Opening device 1\n" + which[k:], 1)
            f_, c_, inf = C.host_records(spliced, argv)
            n_off += 1
            if f_ != base_f or c_ != base_c or len(inf["runtime_lines"]) != 2 or inf["unparsed"]:
                bad.append(k)
    cut = text.replace(lines[1], lines[1][:120], 1)
    f_cut, _, inf_cut = C.host_records(cut, argv)
    other = text.replace('"shire_mask":"0xffffffff"', '"shire_mask":"0xfffffffe"', 1)
    f_oth, _, inf_oth = C.host_records(other, argv)
    t.case("RB-SPLICE", not bad and n_off > 600 and len(f_cut) == len(base_f) - 1 and inf_cut["unparsed"] == 1 and len(f_oth) == len(base_f) - 1
           and len(inf_oth["mismatched"]) == 1, f"{n_off} offsets in a real launch record and its check record: every one read the same; a record cut "
           f"short not read ({inf_cut['unparsed']} unparsed); a record naming another mask not read ({len(inf_oth['mismatched'])}){'; bad offsets ' + str(bad[:5]) if bad else ''}")
    # ---- RB-NEST (fix-e206, the verifier's finding 9): TWO runtime lines, one printed inside the other (the inner at four places in the outer),
    # spliced into the same real record and check record at every byte offset: each must read the same records, both lines counted
    n_nest, bad = 0, []
    outer = "Opening device 1\n"
    for which in (lines[1], lines[-1]):
        for j in (3, 9, 15, 16):
            pair = outer[:j] + "Opening device 0\n" + outer[j:]
            for k in range(len(which) + 1):
                spliced = text.replace(which, which[:k] + pair + which[k:], 1)
                f_, c_, inf = C.host_records(spliced, argv)
                n_nest += 1
                if f_ != base_f or c_ != base_c or len(inf["runtime_lines"]) != 3 or inf["unparsed"] or \
                        sorted(C.runtime_cards(inf["runtime_lines"])) != ["0", "1", "1"]:
                    bad.append((j, k))
    t.case("RB-NEST", not bad and n_nest > 2400, f"{n_nest} splices of a nested pair of runtime lines (the inner at 4 places in the outer) into a "
           f"real launch record and its check record: every one read the same records, both lines counted and their cards named"
           f"{'; bad ' + str(bad[:5]) if bad else ''}")
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
    # ---- RB-CFG: the config read's line with the runtime line around and inside the read's stdout
    cj = json.load(open(os.path.join(E190D, "aifoundry1-c1", "config-start.json")))
    line = json.dumps(cj, separators=(",", ":"))
    ok = C.config_json("Opening device 1\n" + line + "\n") == cj and C.config_json(line + "\nOpening device 1\n") == cj
    okk = all(C.config_json(line[:k] + "Opening device 1\n" + line[k:] + "\n") == cj for k in range(len(line) + 1))
    t.case("RB-CFG", ok and okk and C.config_json(line[:40] + "\n") == {}, f"E190 arm B's committed config line: read whole with the runtime line before, "
           f"after and at every one of its {len(line) + 1} offsets; a cut line is no reading")
    # ---- RB-ID: the identity gate both ways on committed forms
    def cfg(d, name="config-start"):
        return json.load(open(os.path.join(d, name + ".json"))), open(os.path.join(d, name + ".err"), errors="replace").read()
    rows = []
    for label, d in (("E190 arm B (card 1)", os.path.join(E190D, "aifoundry1-c1")), ("E191 session 1 (card 1)", os.path.join(E191A, "session")),
                     ("E191 session 2 (card 1)", os.path.join(E191B, "session"))):
        for nm in ("config-start", "config-end"):
            j, err = cfg(d, nm)
            rows.append((f"{label} {nm}", "B", j, err, True))
            rows.append((f"{label} {nm} read as arm A", "A", j, err, False))
            rows.append((f"{label} {nm} with its block removed", "B", j, "\n".join(x for x in err.splitlines() if not x.startswith(("PCIe target", "Physical device ID"))), False))
    j2, e2 = cfg(os.path.join(E190D, "aifoundry2"))
    rows.append(("aifoundry2's card (E190 arm A, 519 mV) read as arm B", "B", j2, e2, False))
    a3err = open(os.path.join(E189, "session", "sampler.err"), errors="replace").read()
    a3cfg = json.load(open(os.path.join(E189, "session", "config-start.json")))
    rows.append(("aifoundry3's forms (E189's sampler block, its 523 mV config) as arm A", "A", a3cfg, a3err, True))
    rows.append(("aifoundry3's forms read as arm B", "B", a3cfg, a3err, False))
    bad = [r[0] for r in rows if (N1.config_identity(r[1], r[2], r[3]) == "") != r[4]]
    hb = open(os.path.join(E190D, "aifoundry1-c1", "smoke", "fp32", "proc.err"), errors="replace").read()
    tg, ids = N1.parse_ident(hb)
    wB, rB = N1.host_identity("B", tg, ids, set())
    wA, rA = N1.host_identity("A", tg, ids, set())
    h3 = open(os.path.join(E196, "run", "stderr.txt"), errors="replace").read()
    tg3, ids3 = N1.parse_ident(h3)
    w3A, r3A = N1.host_identity("A", tg3, ids3, set())
    w3B, r3B = N1.host_identity("B", tg3, ids3, set())
    sb = open(os.path.join(E190D, "aifoundry1-c1", "sampler.err"), errors="replace").read()
    tgs, idss = N1.parse_ident(sb)
    hosts_ok = not wB and rB and wA and not w3A and r3A and w3B and set(tgs) == {("1", "mgmt")} and set(idss) == {1}
    t.case("RB-ID", not bad and hosts_ok and len(rows) == 21,
           f"{len(rows)} committed config forms, each passed or refused as stated ({'none' if not bad else 'WRONG: ' + '; '.join(bad[:4])}); card 1's committed "
           f"host block passes arm B ({rB}, wrong {wB}) and is refused by arm A ({wA[:1]}); aifoundry3's committed host block (E196) passes arm A ({r3A}) and is "
           f"refused by arm B ({w3B[:1]}); card 1's committed sampler block names {sorted(set(tgs))} {sorted(set(idss))}")
    print(f"REALBYTES-E206 {t.ok} of {t.n} {'PASS' if t.ok == t.n else 'FAIL'}")
    return 0 if t.ok == t.n else 1


if __name__ == "__main__":
    sys.exit(main())
