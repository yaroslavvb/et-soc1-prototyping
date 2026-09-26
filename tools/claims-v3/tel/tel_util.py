#!/usr/bin/env python3
"""Standard-library helpers for the V3-TEL block (tools/claims-v3/tel/block.sh); they run on every lab host.

    tel_util.py order <seed>                      the pass's arm order (random.Random(seed).shuffle), one line
    tel_util.py spst-info <file>                  one SP stats extract: records, first/last SP time, recent pass (JSON)
    tel_util.py wrapwait <extracts.jsonl> <now_ms> <arm_s>
                                                  seconds of quiet to wait so the SP stats ring does not wrap inside
                                                  the next arm (0 if it will not); see "Why wrapwait" below
    tel_util.py merge-spst <trace dir>            merge every extract of the pass into merged.spst (unique records,
                                                  in SP-time order, behind the newest extract's header) and delete
                                                  the extracts once the merge is checked
    tel_util.py check <pass dir> [--smoke]        what the pass holds (counts, parses) as JSON; with --smoke, exit 1
                                                  when a component produced nothing

The SP stats trace ("SPST", dev_mngt_service -t SPST:extract) is a 1 MB ring of 152-byte records after a 64-byte
header, one record per service-processor loop pass (workloads/memprobe/analyze_power.py read_trace()).

Why wrapwait. When the ring is full the firmware resets its write offset to the header (et-trace encoder.h,
trace_check_buffer_full), and an extract returns the header plus the records written since that reset only
(dev_mngt_service.cc dumpRawTraceBuffer writes data_size bytes). Records written between the previous extract and
a wrap are therefore lost. The block extracts after every arm and, before each arm, waits in quiet until the wrap
has happened if the ring could wrap inside the arm, so a wrap only ever costs quiet records.
"""
import glob
import json
import os
import random
import re
import statistics as st
import struct
import sys

HDR, REC = 64, 152
N_MAX = (1024 * 1024 - HDR) // REC      # 6898 records in the 1 MB SP_STATS_BUFFER_SIZE (et-common-libs layout.h)
RAILS = ("minion", "sram", "noc", "system")
ARMS = ["Q", "PWR", "L10", "E10", "E20", "E40", "VOLT"]


def spst_records(buf):
    """[(sp_us, ((avg, min, max) minion mW, sram mW, noc mW, system 10 mW))] as analyze_power.read_trace() reads them."""
    out = []
    for off in range(HDR, len(buf) - REC + 1, REC):
        cyc, = struct.unpack_from("<Q", buf, off)
        if cyc == 0:
            continue
        out.append((cyc, tuple(struct.unpack_from("<HHH", buf, off + 24 + i * 32 + 8) for i in range(4))))
    return out


def read_bytes(path):
    if path.endswith(".gz"):
        import gzip
        return gzip.open(path, "rb").read()
    return open(path, "rb").read()


def spst_info(path):
    try:
        recs = spst_records(read_bytes(path))
    except OSError:
        return {"n": 0}
    if not recs:
        return {"n": 0}
    c = [r[0] for r in recs]
    tail = sorted(c)[-51:]
    d = [(b - a) / 1000.0 for a, b in zip(tail, tail[1:]) if 0 < b - a < 2e6]
    return {"n": len(recs), "first_us": c[0], "last_us": c[-1], "max_us": max(c), "med_last50_ms": st.median(d) if d else None}


def wrapwait(manifest, now_ms, arm_s):
    rows = []
    try:
        rows = [json.loads(l) for l in open(manifest) if l.strip()]
    except OSError:
        pass
    rows = [dict(r.get("info", {}), t_end_ms=r["t_end_ms"]) for r in rows if "t_end_ms" in r]
    rows = [r for r in rows if r.get("n", 0) > 0]
    if not rows:
        return 0, "no extract with records yet"
    r = rows[-1]
    p = r.get("med_last50_ms") or 130.0
    left = N_MAX - r["n"]
    if left < 0:
        return 0, "extract holds %d records, more than the %d expected: ring size differs, no guard" % (r["n"], N_MAX)
    since = now_ms - r["t_end_ms"]
    early = left * p * 0.98 - since          # the earliest the ring can wrap (arms only lengthen the pass)
    if early > (arm_s + 20) * 1000:
        return 0, "ring wraps in >= %.0f s" % (early / 1000)
    wait = max(0.0, left * p * 1.03 - since) / 1000 + 5
    if wait > 240:
        return 0, "wait %.0f s is implausible: no guard" % wait
    return int(wait + 0.999), "ring may wrap within %.0f s: wait %.0f s in quiet" % (max(early, 0) / 1000, wait)


def merge_spst(d):
    files = sorted(glob.glob(os.path.join(d, "*.bin.done")))
    if not files:
        print(json.dumps({"merged": 0, "note": "no extracts"}))
        return
    recs, hdr = {}, None
    for f in files:
        b = read_bytes(f)
        if len(b) >= HDR:
            hdr = b[:HDR]
        for off in range(HDR, len(b) - REC + 1, REC):
            cyc, = struct.unpack_from("<Q", b, off)
            if cyc:
                recs[cyc] = b[off:off + REC]
    out = os.path.join(d, "merged.spst")
    prev = {}
    if os.path.exists(out):                        # a previous merge of this pass (re-run of the merge)
        b = open(out, "rb").read()
        for off in range(HDR, len(b) - REC + 1, REC):
            cyc, = struct.unpack_from("<Q", b, off)
            prev[cyc] = b[off:off + REC]
    prev.update(recs)
    tmp = out + ".tmp"
    with open(tmp, "wb") as f:
        f.write(hdr or b"\0" * HDR)
        for cyc in sorted(prev):
            f.write(prev[cyc])
    check = spst_records(open(tmp, "rb").read())
    if len(check) != len(prev):
        print(json.dumps({"merged": 0, "note": "merge check failed; extracts kept"}))
        os.remove(tmp)
        return
    os.replace(tmp, out)
    for f in files:
        os.remove(f)
    print(json.dumps({"merged": len(prev), "extracts": len(files)}))


def jl(path):
    out = []
    for p in (path, path + ".gz"):
        if os.path.exists(p):
            txt = read_bytes(p).decode("utf-8", "replace")
            for l in txt.splitlines():
                l = l.strip()
                if l.startswith("{"):
                    try:
                        out.append(json.loads(l))
                    except ValueError:
                        pass
            break
    return out


def lines(path):
    for p in (path, path + ".gz"):
        if os.path.exists(p):
            return read_bytes(p).decode("utf-8", "replace").splitlines()
    return []


VLINE = re.compile(rb"MS\s*(\d+) Voltage \[mV\]: VDD_MNN: (\d+) \[")


def check(pdir, smoke):
    r, bad = {}, []

    def need(name, ok):
        if not ok:
            bad.append(name)
    g = os.path.join(pdir, "gov")
    for f in ("sp0.bin", "sp1.bin"):
        p = os.path.join(g, f)
        r["gov_" + f] = os.path.getsize(p) if os.path.exists(p) else 0
        need("gov_" + f, r["gov_" + f] > 0)
    runs = [l for l in lines(os.path.join(g, "runs.jsonl")) if "SPARSITY {" in l]      # "G<i> SPARSITY {json}"
    r["gov_launches"] = len(runs)
    r["gov_ghz"] = [json.loads(l.split("SPARSITY ", 1)[1]).get("ghz") for l in runs]
    need("gov_launches", len(runs) >= 1)
    for f in ("config.json", "driver.json"):
        rows = jl(os.path.join(g, f))
        r["gov_" + f] = rows[0] if rows else None
        need("gov_" + f, bool(rows))
    fw = "\n".join(lines(os.path.join(g, "fw.txt")))
    m1 = re.search(r"Firmware release revision: Major: (\d+) Minor: (\d+) Revision: (\d+)", fw)
    m2 = re.search(r"PMIC Firmware versions: Major: (\d+) Minor: (\d+) Revision: (\d+)", fw)
    r["fw"] = [".".join(m.groups()) if m else None for m in (m1, m2)]
    need("fw", bool(m1 and m2))
    sp1 = read_bytes(os.path.join(g, "sp1.bin")) if os.path.exists(os.path.join(g, "sp1.bin")) else b""
    r["gov_lines"] = {k: len(re.findall(p, sp1)) for k, p in
                      (("idle_old", rb"Power idle state event, current pwr"), ("down", rb"Power throttle down event"),
                       ("up", rb"Power throttle up event"), ("thermal_down", rb"Thermal throttle down event"))}
    tr = os.path.join(pdir, "trace")
    m = os.path.join(tr, "merged.spst")
    info = spst_info(m if os.path.exists(m) else (m + ".gz"))
    r["spst_records"] = info.get("n", 0)
    need("spst", r["spst_records"] > 0)
    for arm, f in (("E10", "e10.jsonl"), ("E20", "e20.jsonl"), ("E40", "e40.jsonl"), ("RESET", "reset.jsonl")):
        rows = jl(os.path.join(pdir, f))
        r["n_" + arm] = len(rows)
        need(arm, len(rows) > 0)
        if arm == "RESET":
            r["since_reset_max"] = max([x.get("since_reset_ms", -1) for x in rows] or [-1])
            need("since_reset", r["since_reset_max"] >= 0)
    for arm, f in (("PWR", "pwr.csv"), ("L10", "l10.csv")):
        n = sum(1 for l in lines(os.path.join(pdir, f)) if re.match(r"^\d+,[0-9.]+$", l))
        r["n_" + arm] = n
        need(arm, n > 0)
    r["n_VOLT_replies"] = sum(1 for l in lines(os.path.join(pdir, "volt.log")) if "Module Voltage MINION" in l)
    need("VOLT", r["n_VOLT_replies"] > 0)
    r["n_bursts_lines"] = sum(1 for l in lines(os.path.join(pdir, "burst.jsonl")) if " ENERCAT " in l)
    need("bursts", r["n_bursts_lines"] > 0)
    dbg = os.path.join(pdir, "dbg")
    caps = sorted(glob.glob(os.path.join(dbg, "*.bin")))
    r["dbg_captures"] = {}
    for c in caps:
        b = read_bytes(c)
        r["dbg_captures"][os.path.basename(c)] = {"bytes": len(b), "shires": len({int(x.group(1)) for x in VLINE.finditer(b)}),
                                                  "temp_lines": len(re.findall(rb"Temp \[C\]", b)),
                                                  "mem_lines": len(re.findall(rb"MEM \d+ Voltage", b))}
    need("dbg_voltage_lines", any(v["shires"] == 34 for v in r["dbg_captures"].values()))
    wins = sorted(glob.glob(os.path.join(dbg, "x3-w*.jsonl*")))
    r["dbg_windows"] = {os.path.basename(w): len(jl(w.replace(".gz", ""))) for w in wins}
    need("dbg_windows", bool(wins) and all(v > 0 for v in r["dbg_windows"].values()))
    ic = jl(os.path.join(pdir, "idle_clock.jsonl"))          # the idle operating point read with no sampler running
    r["idle_clock"] = [[x.get("label"), (x.get("config") or {}).get("minion_mhz"), (x.get("config") or {}).get("power_state_name")]
                       for x in ic]
    need("idle_clock", any(x.get("config") for x in ic))
    r["missing"] = bad
    print(json.dumps(r))
    return 1 if (smoke and bad) else 0


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return 2
    if a[0] == "order":
        arms = list(ARMS)
        random.Random(int(a[1])).shuffle(arms)
        print(*arms)
    elif a[0] == "spst-info":
        print(json.dumps(spst_info(a[1])))
    elif a[0] == "wrapwait":
        w, why = wrapwait(a[1], int(a[2]), float(a[3]))
        print(w, why)
    elif a[0] == "merge-spst":
        merge_spst(a[1])
    elif a[0] == "check":
        return check(a[1], "--smoke" in a)
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
