#!/usr/bin/env python3
"""E202's REAL-BYTES TEST (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum): every reader of a tool's output in E202's kit fed
the BYTES THE LAB COMMITTED (the lesson of E191's first session, round log 116: a runtime line printed inside a host's JSON line on a
real box; the desk's clean stand-ins never met it), with E191's kit note 2 (2d0fe517) as the form.

    /usr/bin/python3 -I -B tools/claims-v3/e202/desk/realbytes_e202.py <scratch dir outside the repo>

The readers (e202_common.py): read_result (THE HOST'S RESULT, from its own --out file only), sample_line (the sampler), config_line (the
guard's config), etwho_holders (et-who), r_for (the R rule on a smoke record) and adapt (the reducer's host.json). The bytes:
  B1  the mnistmlp host's own --out files from its nine simulator runs (docs/reports/data/2026-11-16-q193-mnistmlp/sim/*/host-result.json:
      the real host's real bytes, device "sysemu"): each read exactly as json.loads reads the file; S3x's core PASS / logits FAIL read as the
      gate's pass; r_for and adapt on each;
  B2  E191's first session's split stdout (1a4bc1e3: the ledger host's JSON line with aifoundry1's "Opening device 1" printed inside it)
      as a host's stdout.txt beside NO --out file: no result ("no host result file"), never the broken head; the same bytes AS the --out
      file: no result (the line does not parse whole); E191's first reader (last_json, the line's head) as the negative control;
  B3  THE SPLICE: aifoundry1's runtime line at EVERY byte offset of each B1 file's line (and on its own line before and after it): every
      read is the exact record or no result, never another record;
  B4  the sampler's real lines: E189's whole committed session telemetry (9,436 lines) and E195's, each read exactly; aifoundry1's runtime
      line spliced at every offset of E189's first line: the exact sample or none, never another;
  B5  the guard's real config output (E195's committed config-session-start.json, compact) and E189's (the runner's own form), each read;
      the runtime line inside it: no reading (a gate, never a wrong config);
  B6  et-who's real output (E195's committed etwho-end.txt): no holder; et-who's holder-line form (another login's two lines, ours one):
      two counted, ours never;
  B7  other hosts' real lines as an --out file (E189's ledger host-raw.json, E190's rgm136 SPARSITY stdout): refused as not the mnistmlp
      host's record.
Prints each check PASS/FAIL and REALBYTES-E202 <n> of <m> PASS or FAIL last. SPDX-License-Identifier: Apache-2.0
"""
import glob
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import e202_common as C  # noqa: E402

REPO = C.REPO
D = os.path.join(REPO, "docs", "reports", "data")
RT = "Opening device 1"
RES = []


def check(name, ok, detail=""):
    RES.append(bool(ok))
    print(f"{'PASS' if ok else 'FAIL'} {name}: {detail}", flush=True)


def put(p, body):
    with open(p, "wb") as f:
        f.write(body)


def last_json_e191_first(text):
    """E191's first reader (e191_common.last_json, its kit as first landed): the last line that starts with '{', parsed, else {}."""
    for ln in reversed(text.splitlines()):
        if ln.startswith("{"):
            try:
                return json.loads(ln)
            except ValueError:
                return {}
    return {}


def main(argv):
    if len(argv) != 1:
        print(__doc__)
        return 2
    S = os.path.abspath(argv[0])
    os.makedirs(S, exist_ok=True)
    print(f"realbytes_e202: /usr/bin/python3 {sys.version.split()[0]}, the lab's committed bytes", flush=True)
    # B1
    sims = sorted(glob.glob(os.path.join(D, "2026-11-16-q193-mnistmlp", "sim", "*", "host-result.json")))
    exact, gates, rr, ad = 0, {}, 0, 0
    pm = C.plan_module()
    for p in sims:
        want = json.loads(open(p).read())
        got, why = C.read_result(p, device="sysemu")
        exact += got == want
        gates[os.path.basename(os.path.dirname(p))] = (C.core_pass(got), (got or {}).get("logits_status"))
        R, pred, w, _ = C.r_for(got, pm)            # fix-e202: r_for also returns its detail (the host's timeout cap)
        rr += R in C.R_ALLOWED
        h = C.adapt(got)
        ad += h["reps_done"] == (1 if want.get("launch_ok") else 0) and h["launch_epoch_ms"] == want["launch_epoch_ms"]
    check("B1 the mnistmlp host's nine real --out files (simulator) read exactly", len(sims) == 9 and exact == 9, f"{exact} of {len(sims)}")
    new_form = {k: v for k, v in gates.items() if json.loads(open(os.path.join(D, "2026-11-16-q193-mnistmlp", "sim", k, "host-result.json")).read()).get("core_status")}
    old_form = sorted(set(gates) - set(new_form))
    check("B1 the gate on real records: S3x (only the debug logits wrong) core PASS, logits FAIL: passes; S3 and S1b core PASS; the six runs "
          "of the host before it wrote core_status fail safe (no core_status: never a gate pass)",
          gates.get("S3x") == (True, "FAIL") and gates.get("S3") == (True, "PASS") and gates.get("S1b") == (True, "PASS")
          and len(old_form) == 6 and not any(gates[k][0] for k in old_form), json.dumps(gates))
    check("B1 the R rule and the adapter read every real record (its work_cycles.max, copy_cycles_max, launch marks)", rr == 9 and ad == 9,
          f"R read {rr} of 9, adapter {ad} of 9")
    gotc, why = C.read_result(sims[0], device="card")
    check("B1 a simulator record is not a card's (device check)", gotc is None and "device" in why, why)
    # B2
    split = glob.glob(os.path.join(D, "2026-11-15-e191-blind-day-aifoundry1-c1", "session", "smoke", "copy-64m-random", "stdout.txt"))
    body = open(split[0], "rb").read() if split else b""
    d2 = os.path.join(S, "b2")
    os.makedirs(d2, exist_ok=True)
    if os.path.exists(os.path.join(d2, "host-raw.json")):
        os.remove(os.path.join(d2, "host-raw.json"))
    put(os.path.join(d2, "stdout.txt"), body)
    g, why = C.read_result(os.path.join(d2, "host-raw.json"))
    check("B2 E191's split stdout beside no --out file: no result, never the head", bool(body) and RT.encode() in body and g is None
          and why == "no host result file", why)
    put(os.path.join(d2, "host-raw.json"), body)
    g, why = C.read_result(os.path.join(d2, "host-raw.json"))
    head = last_json_e191_first(body.decode())
    check("B2 the same bytes AS the --out file: no result (the line does not parse whole); E191's first reader read {} (status None)",
          g is None and "cut" in why and head.get("status") is None, why)
    # B3
    n, bad, none = 0, 0, 0
    for p in sims:
        raw = open(p, "rb").read()
        line = raw.rstrip(b"\n")
        want = json.loads(line)
        for k in range(len(line) + 1):
            put(os.path.join(S, "b3.json"), line[:k] + (b"\n" if k in (0, len(line)) else b"") + RT.encode() + b"\n" + line[k:] + b"\n")
            got, _ = C.read_result(os.path.join(S, "b3.json"), device=None)
            n += 1
            if got is None:
                none += 1
            elif got != want:
                bad += 1
        put(os.path.join(S, "b3.json"), RT.encode() + b"\n" + line + b"\n" + RT.encode() + b"\n")
        got, _ = C.read_result(os.path.join(S, "b3.json"), device=None)
        bad += got != want
    check("B3 THE SPLICE: the runtime line (a whole printed line) at every byte offset of nine real records: the exact record or none, "
          "never another; on its own line before and after: read exactly", n > 14000 and bad == 0,
          f"{n} splices, {n - none} read exactly, {none} none, {bad} wrong")
    GATE = ("status", "core_status", "groups_done", "pad_groups", "ops", "copy_cycles_max", "launch_epoch_ms", "wall_s", "launch_ok",
            "tensor_error_or", "passes", "device", "mnistmlp")

    def readv(r):   # every value the gate, the R rule, the adapter and the scorer read from a host record
        return tuple(r.get(f) for f in GATE) + ((r.get("hart0_cycles") or {}).get("max"), (r.get("work_cycles") or {}).get("max"))
    n = acc = same = unsafe = 0
    for p in sims:
        line = open(p, "rb").read().rstrip(b"\n")
        want = json.loads(line)
        for k in range(len(line) + 1):
            put(os.path.join(S, "b3.json"), line[:k] + RT.encode() + line[k:] + b"\n")
            got, _ = C.read_result(os.path.join(S, "b3.json"), device="sysemu")
            n += 1
            if got is None:
                continue
            acc += 1
            if readv(got) == readv(want):
                same += 1
            elif C.core_pass(got) and got.get("status") == "PASS":
                unsafe += 1
    check("B3b the runtime text with no newline inside a real record at every offset (a key or a string renamed; impossible in the "
          "host's own --out file, tested anyway): every record read either keeps every field the gate, the adapter and the scorer read, or "
          "fails the gate (complete() and core_pass); none passes with a field changed", unsafe == 0 and n > 14000,
          f"{n} splices, {acc} parse (inside a string), {same} with every read field the original's, {unsafe} unsafe")
    # B4
    tels = [os.path.join(D, "2026-11-14-e189-blind-day-aifoundry3", "session", "telemetry.jsonl.gz")]
    tels += sorted(glob.glob(os.path.join(D, "2026-11-16-e195-x09-dramtoggle-aifoundry3", "passes", "*", "telemetry.jsonl.gz")))[:3]
    lines = ok = 0
    first = None
    for p in tels:
        for ln in gzip.open(p, "rt"):
            if not ln.startswith("{"):
                continue
            lines += 1
            s = C.sample_line(ln)
            ok += s == json.loads(ln)
            first = first or ln.rstrip("\n")
    check("B4 the sampler's real lines (E189's whole session, three of E195's passes) read exactly", lines > 9436 and ok == lines,
          f"{ok} of {lines}")
    n = bad = none = 0
    want = json.loads(first)

    def readf(s):
        return (s["t_ms"], s["board_w"], s["sp"]["board_avg_w"], [s["sp"][k][0] for k in ("minion_w", "sram_w", "noc_w")],
                s["temp_c"]["minshire"][:3], s["mhz"]["minion"])
    for k in range(len(first) + 1):
        for piece in (first[:k] + RT + first[k:], first[:k] + RT + "\n" + first[k:], first[:k] + "\n" + RT + "\n" + first[k:]):
            for part in piece.split("\n"):
                s = C.sample_line(part)
                n += 1
                if s is None:
                    none += 1
                elif readf(s) != readf(want):
                    bad += 1
    check("B4 the runtime text inside and across E189's first sampler line at every offset: a sample read keeps every field the stops and "
          "the reducer read, or the line is lost", bad == 0 and n > 3000, f"{n} pieces, {n - none} samples read, {bad} with a read field changed")
    # B5
    c195 = open(os.path.join(D, "2026-11-16-e195-x09-dramtoggle-aifoundry3", "session", "config-session-start.json")).read()
    c189 = open(os.path.join(D, "2026-11-14-e189-blind-day-aifoundry3", "session", "config-start.json")).read()
    j1, j2 = C.config_line(c195), C.config_line(c189)
    cut = c195.strip()
    j3 = C.config_line(cut[:30] + RT + "\n" + cut[30:])
    check("B5 the guard's real config output (E195's raw line) and E189's form read, as found (TDP 0 W / 65 C / 600 MHz); a runtime line "
          "inside: no reading", C.config_ok(j1) and C.config_ok(j2) and j3 == {} and not C.config_ok(j3), f"{j1.get('minion_mhz')} MHz, "
          f"{j2.get('tdp_w')} W")
    # B6
    w = open(os.path.join(D, "2026-11-16-e195-x09-dramtoggle-aifoundry3", "session", "etwho-end.txt")).read()
    held = "/dev/et0_mgmt otherlogin 4242 ettelem\nlock:etsoc-shire0.lock otherlogin 4242 ettelem\nlock:etsoc-shire0.lock me 77 python3\n"
    check("B6 et-who's real output reads no holder; its holder-line form: another login's two lines counted, ours never; fix-e202: both "
          "readable at rc 0, the real text unreadable at rc 1",
          w.startswith("No process holds") and C.etwho_holders(w, "me") == 0 and C.etwho_holders(held, "me") == 2
          and C.etwho_unreadable(0, w) == "" and C.etwho_unreadable(0, held) == "" and C.etwho_unreadable(1, w) != "", w.strip())
    # B7
    lh = os.path.join(D, "2026-11-14-e189-blind-day-aifoundry3", "passes", "copy-zeros", "p1", "host-raw.json")
    g1, why1 = C.read_result(lh)
    sp = sorted(glob.glob(os.path.join(D, "2026-11-13-e190-large-gemm", "aifoundry2", "runs", "*", "proc-00.out")))[:1]
    g2, why2 = C.read_result(sp[0]) if sp else (1, "none")
    check("B7 other hosts' real lines as an --out file (E189's ledger record, E190's rgm136 stdout): refused, not the mnistmlp host's",
          g1 is None and "not an mnistmlp" in why1 and g2 is None, f"{why1}; {why2}")
    for f in ("b3.json",):
        if os.path.exists(os.path.join(S, f)):
            os.remove(os.path.join(S, f))
    n = sum(RES)
    print(f"REALBYTES-E202 {n} of {len(RES)} {'PASS' if n == len(RES) else 'FAIL'}")
    return 0 if n == len(RES) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
