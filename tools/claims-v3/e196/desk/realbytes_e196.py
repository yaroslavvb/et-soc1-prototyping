#!/usr/bin/env python3
"""E196's REAL-BYTES desk test (Q185, lane kit-e196, Sun 15 Nov 2026, PST, before any E196 datum; CONTEXT section 116's lesson: "its
real-path desk test feeds the parser the REAL stdout bytes committed from a card, not only stand-in JSON"). The kit's host-line reader
(e196_lines.py: drop_runtime, read_host, launches_in_order), the one place the runner reads a host's stdout, fed the bytes the lab
committed, from the top of the tree at the commit under test:

  RB1  THE SPLIT BYTES (1a4bc1e3, E191's first session on aifoundry1 card 1): session/smoke/copy-64m-random/stdout.txt, the ledger host's
       line with "Opening device 1" inside it: drop_runtime gives back one line that parses, status PASS, records_ok 2048, one runtime line
       dropped; the reader E191's kit used then (the last line that begins with "{") takes the broken head: the negative control;
  RB2  every committed stdout.txt that holds "Opening device" (E191's two sessions on aifoundry1 card 1): each reassembles to a host line
       that parses, the runtime lines counted;
  RB3  THE LAB'S OWN HOST ON aifoundry3: every fp32 TensorFMA stdout file the lab committed from aifoundry3 in the claims check
       (docs/reports/data/2026-09-25-claims-v3/raw/aifoundry3/lat/p*/sp/fma-fp32-*.jsonl: the sparsity host's raw stdout, the source
       E196 runs, with --values): read_host(..., 'lab') reads every SPARSITY line, the same dict as json.loads, with the command line each
       file's own records give (values, pattern, row mask, shires, minions); the launches in order where a file is one process;
  RB4  the runtime line at EVERY byte offset of each such file's first line (and two at once): the same records, the line dropped;
  RB5  aifoundry3'S RUNTIME TEXT ON stdout: E192's committed run/stderr.txt and E193's device-stderr.txt (the runtime's real output on
       aifoundry3, which it prints on stderr) put between real SPARSITY lines: the host lines read, the runtime's lines counted as other
       text; the same text put INSIDE a host line: the process is UNREADABLE (fails safe: no record written), never a wrong datum;
  RB6  E193's committed device-stdout.txt (aifoundry3, X04 lines, the request family's host form) and E189's committed smoke stdout.txt
       (aifoundry3, ledger lines): the reader's method (drop_runtime, then the prefixed or "{" lines) reads each line as json.loads does,
       and with the runtime line spliced at every offset of the first line, the same dict;
  RB7  THE REQUEST'S HOST FORM (x14_host): no card has ever printed an X14 line, so its lines here are STAND-INS in the host's own printf
       form (proposal/src/host/main.cpp lines 454-462 and 473-476), for each registered train command (desk/commands-e196.txt) and each
       premise run: read in order, every split offset read the same; a line of the wrong kind's label, the wrong row mask, a missing key,
       a launch out of order, a lost calibration line: UNREADABLE;
  RB8  THE E78 HEATER'S OWN REAL stdout (docs/reports/data/2026-09-29-memp2/raw/aifoundry2/p911/heat.out: the lab's host, --values
       randn, all 1,024 minions, a timed process; aifoundry2's card): read with the kit's registered heater command line, launches in
       order (RB3c); with its calibration line lost, or a middle line lost: out of order, UNREADABLE (a missing first launch would move
       the reduction's window: the runner writes none of the run); against another command's --values: UNREADABLE.
    /usr/bin/python3 -I -B tools/claims-v3/e196/desk/realbytes_e196.py        (prints REALBYTES-E196 <n> of <m> PASS last)
A desk check of code on committed records: nothing here is measured. SPDX-License-Identifier: Apache-2.0
"""
import glob
import json
import os
import subprocess
import sys

TOP = os.getcwd()
sys.path.insert(0, os.path.join(TOP, "tools/claims-v3/e196"))
import e196_lines as L  # noqa: E402

npass = ncase = 0
fails = []


def ok(cond, label, detail=""):
    global npass, ncase
    ncase += 1
    if cond:
        npass += 1
        print("-> PASS (%s)" % label, flush=True)
    else:
        fails.append(label)
        print("-> FAIL (%s%s)" % (label, (": " + str(detail)[:300]) if detail else ""), flush=True)


def head_rev():
    r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip()


def last_brace(text):
    """E191 kit v1's reader (e191_common.last_json): the last line that begins with '{', parsed, or {}"""
    for ln in reversed(text.splitlines()):
        if ln.startswith("{"):
            try:
                return json.loads(ln)
            except ValueError:
                return {}
    return {}


def reassembled_brace(text):
    host, rt = L.drop_runtime(text)
    return last_brace(host), rt


def argv_of(rec):
    """the command line a SPARSITY record's own fields give (the lab host's options)"""
    sh = int(rec["shire_mask"], 16)
    per = rec["minions"] // max(1, bin(sh).count("1"))
    a = ["--test", rec["test"], "--type", rec["type"], "--pattern", rec["pattern"], "--values", rec["values"]]
    if rec["row_mask"] != "0xffff":
        a += ["--row-mask", rec["row_mask"]]
    return a + ["--shires", rec["shire_mask"], "--per-shire", str(per)]


def main():
    print("E196 real-bytes desk test (kit-e196), at %s; Python %s" % (head_rev()[:12], sys.version.split()[0]), flush=True)
    # ---- RB1 ----
    p = "docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1/session/smoke/copy-64m-random/stdout.txt"
    b = open(p, "rb").read().decode()
    j, rt = reassembled_brace(b)
    ok(j.get("status") == "PASS" and j.get("records_ok") == 2048 and rt == ["Opening device 1"],
       "RB1 1a4bc1e3's split smoke stdout: drop_runtime reassembles the ledger host's line: PASS, 2,048 records, one runtime line", (j.get("status"), rt))
    ok(last_brace(b).get("status") is None, "RB1b the negative control: E191 kit v1's reader takes the broken head (status None)", last_brace(b).get("status"))
    # ---- RB2 ----
    files = [f for f in sorted(glob.glob("docs/reports/data/**/stdout.txt", recursive=True)) if "Opening device" in open(f, errors="replace").read()]
    good = 0
    for f in files:
        j, rt = reassembled_brace(open(f, "rb").read().decode(errors="replace"))
        good += bool(j) and isinstance(j.get("status"), str) and len(rt) >= 1
    ok(len(files) >= 1 and good == len(files), "RB2 every committed stdout.txt with a runtime line (%d files) reassembles to a host line that parses" % len(files), (good, len(files)))
    # ---- RB3 / RB4 ----
    sp = sorted(glob.glob("docs/reports/data/2026-09-25-claims-v3/raw/aifoundry3/lat/p*/sp/fma-fp32-*.jsonl"))
    nlines = nfiles = 0
    bad3 = []
    splice_ok = 0
    splice_n = 0
    for f in sp:
        text = open(f, "rb").read().decode()
        lines = [ln for ln in text.split("\n") if ln.startswith("SPARSITY ")]
        if not lines:
            continue
        first = json.loads(lines[0][len("SPARSITY "):])
        if first.get("test") != "fma":
            continue
        nfiles += 1
        nlines += len(lines)
        recs, info = L.read_host(text, "lab", None)
        want = [json.loads(ln[len("SPARSITY "):]) for ln in lines]
        if not (info["readable"] and [r for _, r in recs] == want):
            bad3.append((f, info["unreadable"][:1]))
        # with the command line its own records give: every record of a one-command file agrees
        if len({(r["values"], r["pattern"], r["row_mask"], r["shire_mask"], r["minions"]) for r in want}) == 1:
            r2, i2 = L.read_host(text, "lab", argv_of(first))
            if not i2["readable"]:
                bad3.append((f, "argv", i2["unreadable"][:1]))
        # RB4: the runtime line at every offset of the first line; and two at once at a few offset pairs
        ln0 = lines[0] + "\n"
        base, _ = L.read_host(ln0, "lab", None)
        for k in range(len(ln0)):
            splice_n += 1
            rr, ii = L.read_host(ln0[:k] + "Opening device 0\n" + ln0[k:], "lab", None)
            splice_ok += ii["readable"] and rr == base and ii["runtime_lines"] == ["Opening device 0"]
        for k1, k2 in ((5, 40), (12, len(ln0) - 3), (0, len(ln0) - 1)):
            splice_n += 1
            t2 = ln0[:k1] + "Opening device 3\n" + ln0[k1:k2] + "Opening device 0\n" + ln0[k2:]
            rr, ii = L.read_host(t2, "lab", None)
            splice_ok += ii["readable"] and rr == base and ii["runtime_lines"] == ["Opening device 3", "Opening device 0"]
    ok(nfiles >= 10 and not bad3, "RB3 the lab's sparsity host's real stdout from aifoundry3: %d fp32 fma files, %d SPARSITY lines, every one read as json.loads reads it, and with its own command line" % (nfiles, nlines), bad3[:3])
    ok(splice_n > 1000 and splice_ok == splice_n, "RB4 the runtime line at every byte offset of each file's first line, and two at once: %d of %d read the same records" % (splice_ok, splice_n))
    # one-process files: the launches in order
    rm = "docs/reports/data/2026-09-25-claims-v3/raw/aifoundry3/lat/p3/sp/fma-fp32-rowmask-0x000F.jsonl"
    rt_, inf_ = L.read_host(open(rm).read(), "lab", None)
    ok(inf_["readable"] and L.launches_in_order(rt_, "SPARSITY "), "RB3b a one-process file (row mask 0x000F, p3): launches -1, 0, 1, ... in order", [j["launch"] for _, j in rt_][:6])
    # ---- RB5 ----
    e192 = open("docs/reports/data/2026-11-14-e192-intbits-aifoundry3/run/stderr.txt", errors="replace").read().split("\n")[:400]
    e193 = open("docs/reports/data/2026-11-15-e193-x04-clock-sitting-a-aifoundry3/x04/device-stderr.txt", errors="replace").read().split("\n")
    rmtext = open(rm).read()
    sl = [ln for ln in rmtext.split("\n") if ln.startswith("SPARSITY ")]
    mixed = "\n".join(e193[:40]) + "\n" + "\n".join(sl[:3]) + "\n" + "\n".join(e192[:60]) + "\n" + "\n".join(sl[3:]) + "\n" + "\n".join(e193[40:]) + "\n"
    rr, ii = L.read_host(mixed, "lab", None)
    ok(ii["readable"] and [j for _, j in rr] == [json.loads(x[9:]) for x in sl] and ii["other_lines"] > 50,
       "RB5 aifoundry3's real runtime text (E192's stderr.txt, E193's device-stderr.txt) between the host's lines: every host line read, %d other lines counted" % ii["other_lines"], ii["unreadable"][:1])
    inside = sl[0][:60] + "LOGGER NOT INITIALIZED:\n" + sl[0][60:] + "\n" + "\n".join(sl[1:]) + "\n"
    rr, ii = L.read_host(inside, "lab", None)
    ok(not ii["readable"], "RB5b the same runtime text INSIDE a host line: UNREADABLE (the runner writes none of the run): fails safe", ii["unreadable"][:1])
    inside2 = sl[0][:100] + "\t\tET [DEVICE_LAYER][TH:135172882808448]: \n" + sl[0][100:] + "\n"
    rr, ii = L.read_host(inside2, "lab", None)
    ok(not ii["readable"] and not rr, "RB5c a device-layer line inside a host line: UNREADABLE, no record", ii["unreadable"][:1])
    # ---- RB6 ----
    nrb6 = badrb6 = 0
    for f in sorted(glob.glob("docs/reports/data/2026-11-15-e193-x04-clock-sitting-*-aifoundry3/*/device-stdout.txt")):
        text = open(f, "rb").read().decode()
        host, rt = L.drop_runtime(text)
        xs = [ln for ln in host.split("\n") if ln.startswith("X04 ")]
        for ln in xs:
            nrb6 += 1
            try:
                json.loads(ln[4:])
            except ValueError:
                badrb6 += 1
        if xs:
            l0 = xs[0] + "\n"
            for k in range(len(l0)):
                h2, rt2 = L.drop_runtime(l0[:k] + "Opening device 0\n" + l0[k:])
                if h2 != l0 or rt2 != ["Opening device 0"]:
                    badrb6 += 1
    for f in sorted(glob.glob("docs/reports/data/2026-11-14-e189-blind-day-aifoundry3/session/smoke/*/stdout.txt")):
        text = open(f, "rb").read().decode()
        j0 = last_brace(text)
        j1, rt = reassembled_brace(text)
        nrb6 += 1
        badrb6 += not (j0 == j1 and rt == [])
    ok(nrb6 > 20 and badrb6 == 0, "RB6 E193's X04 lines and E189's ledger lines from aifoundry3 (%d lines): read as json.loads reads them; the runtime line at every offset of a first line, dropped exactly" % nrb6, badrb6)
    # ---- RB7: the request's host form (stand-ins in its printf form) ----
    cmds = {}
    sec = ""
    for ln in open("tools/claims-v3/e196/desk/commands-e196.txt"):
        if ln.startswith("#"):
            sec = ln
            continue
        if "x14_host" in ln:
            w = ln.split()
            i = w.index("x14_host")
            cmds[" ".join(w[:i])] = w[i + 1:]

    def arg(a, k, d=None):
        return a[a.index(k) + 1] if k in a else d

    def x14line(a, n, kind):
        train = arg(a, "--abba") is not None
        lab = arg(a, "--label-b") if (train and kind == "S") else arg(a, "--label")
        val = arg(a, "--values-b") if (train and kind == "S") else arg(a, "--values")
        rm = arg(a, "--row-mask-b") if (train and kind == "S") else arg(a, "--row-mask", "none")
        rm = "none" if rm in (None, "none") else "0x%04x" % (int(rm, 0) & 0xFFFF)
        t0 = 1794800000000 + 600 * (n + 1)
        return ('X14 {"label":"%s","values":"%s","row_mask":"%s","kind":"%s","abba":"%s","minions":1024,"shire_mask":"0xffffffff",'
                '"iters":%d,"launch":%d,"ops":%d,"cycles_max":%d,"cycles_mean":%.1f,"cycles_per_op":%.3f,"wall_s":%.6f,'
                '"t_start_ms":%d,"t_end_ms":%d,"ghz":%.4f,"tensor_errors":0,"ok":true}') % (
            lab, val, rm, kind if train else "-", arg(a, "--abba") or "", 20000, n, 20000 * 1024, 10880700, 10880600.0, 544.03,
            0.5, t0, t0 + 500, 0.6)

    def x14check(a, n, kind):
        train = arg(a, "--abba") is not None
        lab = arg(a, "--label-b") if (train and kind == "S") else arg(a, "--label")
        return ('X14CHECK {"label":"%s","kind":"%s","after_launch":%d,"zero_rows":"0xffff","live_rows":"none","zero_rows_bad":0,'
                '"live_rows_zero":-1,"ok":true}') % (lab, kind if train else "-", n)

    def process(a):
        train = arg(a, "--abba")
        n_l = int(arg(a, "--launches", "8"))
        out = []
        for n in range(-1, n_l):
            k = (train[0] if n < 1 else train[(n - 1) % 4]) if train else "F"
            out.append(x14line(a, n, k))
            if n == -1 or n == n_l - 1:
                out.append(x14check(a, n, k))
        return "\n".join(out) + "\n"
    nrb7 = badrb7 = 0
    for name, a in sorted(cmds.items()):
        text = process(a)
        rr, ii = L.read_host(text, "x14", a)
        nrb7 += 1
        badrb7 += not (ii["readable"] and L.launches_in_order(rr, "X14 "))
        l0 = text.split("\n")[0] + "\n"
        base, _ = L.read_host(l0, "x14", a)
        for k in range(0, len(l0), 7):
            rr2, ii2 = L.read_host(l0[:k] + "Opening device 0\n" + l0[k:], "x14", a)
            nrb7 += 1
            badrb7 += not (ii2["readable"] and rr2 == base)
    ok(len(cmds) == 8 and badrb7 == 0, "RB7 the request's host form (stand-in lines in its printf form): the 4 train commands and 4 premise runs read in order, the runtime line at every 7th offset read the same (%d reads)" % nrb7, badrb7)
    tr = cmds["T1 SFFS"]
    text = process(tr)
    neg = {
        "the other kind's label on an F launch": text.replace('"label":"T.Z.m1111","values"', '"label":"I.Z.m000F","values"', 1),
        "the wrong row mask": text.replace('"row_mask":"0x1111"', '"row_mask":"0x000f"', 1),
        "a missing key": text.replace(',"ghz":0.6000', "", 1),
        "a launch out of order": text.replace('"launch":3,', '"launch":4,', 1),
        "the calibration line lost": "\n".join(ln for ln in text.split("\n") if '"launch":-1,' not in ln) + "\n",
        "an unknown text inside a line": text.replace('"ops":', 'Opening card 0\n"ops":', 1),
    }
    nn = 0
    for why, t in neg.items():
        rr, ii = L.read_host(t, "x14", tr)
        if ii["readable"] and L.launches_in_order(rr, "X14 "):
            print("   negative control read as good: %s" % why)
        else:
            nn += 1
    ok(nn == len(neg), "RB7b %d of %d broken train outputs UNREADABLE (wrong label, wrong mask, a missing key, out of order, a lost calibration line, unknown text)" % (nn, len(neg)))
    # ---- RB8 (and RB3c): the lab's E78 heater's own real stdout, a timed process (memp2, aifoundry2's card, 29 Sep 2026) ----
    hp = "docs/reports/data/2026-09-29-memp2/raw/aifoundry2/p911/heat.out"
    ht = open(hp, "rb").read().decode()
    hargv = ["--test", "fma", "--type", "fp32", "--pattern", "none", "--values", "randn", "--shires", "0xffffffff",
             "--per-shire", "32", "--seconds", "2", "--seed", "1", "--stop-file", "OUT/STOP"]
    rr, ii = L.read_host(ht, "lab", hargv)
    ok(ii["readable"] and len(rr) >= 4 and L.launches_in_order(rr, "SPARSITY "),
       "RB3c the E78 heater's real stdout (a timed process, all 1,024 minions) with the kit's registered heater command line: read, launches %s in order" % [j["launch"] for _, j in rr], ii["unreadable"][:1])
    lost = "\n".join(ln for ln in ht.split("\n") if '"launch":-1,' not in ln) + "\n"
    rr, ii = L.read_host(lost, "lab", hargv)
    ok(ii["readable"] and len(rr) >= 3 and not L.launches_in_order(rr, "SPARSITY "),
       "RB8 the same real stdout with its calibration line lost: out of order, so the runner writes none of it (the reduction's window never moves)")
    mid = "\n".join(ln for ln in ht.split("\n") if '"launch":2,' not in ln) + "\n"
    rr, ii = L.read_host(mid, "lab", hargv)
    ok(ii["readable"] and not L.launches_in_order(rr, "SPARSITY "), "RB8b a middle launch's line lost: out of order, none written")
    rr, ii = L.read_host(ht, "lab", hargv[:7] + ["randn_small"] + hargv[8:])
    ok(not ii["readable"], "RB8c the same real stdout read against another command's --values: UNREADABLE (a line is checked against its own command)")
    print("REALBYTES-E196 %d of %d %s" % (npass, ncase, "PASS" if npass == ncase else "FAIL"), flush=True)
    return 0 if npass == ncase else 1


if __name__ == "__main__":
    sys.exit(main())
