#!/usr/bin/env python3
"""verify-v31trace (Q217) v06: this lane's OWN parse of raw sys_emu log lines (the excerpts kept by vt_run.py from run u1), written from
sys_emu's printf formats (emu_gio.cpp lprintf: '<step>: <level> EMU: [H<h> S<s>:N<n>:C<c>:T<t>] <msg>'; insn_util.h 'I(%c): 0x<pc> ...';
tensors.cpp Start/Execute TensorLoad, TensorStore, TensorFMA32 lines; LOG_TENSOR_COOP 'tensor_coop : 0x..'; LOG_MEMREAD512
'MEM512[0x..] : {'; tensor store writes 'MEM128[0x..] ='), compared field by field with v31-trace's summarizer output (summary.json.gz of
the same run) for the same harts. Nothing of trace_run.py is imported. /usr/bin/python3 3.12.3, standard library.
    python3 -I -B v06_rawparse.py <run dir>
"""
import collections
import glob
import gzip
import json
import os
import re
import sys

PFX = re.compile(r"^(\d+): (\w+) EMU: \[H(\d+) S(\d+):N(\d+):C(\d+):T(\d+)\] ?(.*)$")
INS = re.compile(r"^I\((.)\): 0x([0-9a-f]+) ")
TLS = re.compile(r"\(TL-H(\d+)-(\d+)\) Start TensorLoad with msk: (\d+), coop: (\d+), cmd: (\d+), start: (\d+), tenb: (\d+), "
                 r"addr: 0x([0-9a-f]+), boffset: (\d+), rows: (\d+), stride: 0x([0-9a-f]+), id: (\d+)")
TSS = re.compile(r"\(TS-H(\d+)-(\d+)\) Start TensorStore with addr: ([0-9a-f]+), stride: ([0-9a-f]+), regstart: (\d+), rows: (\d+), "
                 r"cols: (\d+), srcinc: (\d+), coop: (\d+)")
TMS = re.compile(r"\(TM-H(\d+)-(\d+)\) Start (TensorFMA32|TensorFMA16A32|TensorIMA8A32) with msk: (\d+), bcols: (\d+), arows: (\d+), "
                 r"acols: (\d+), aoffset: (\d+), (?:dst: (\d+), ub: \d+, ua: \d+, )?tenb: (\d+), bstart: (\d+), astart: (\d+),? mul: (\d+)")
TLX = re.compile(r"\(TL-H(\d+)-(\d+)\) Execute TensorLoad with .*addr: 0x([0-9a-f]+), boffset: \d+, rows: (\d+), stride: 0x([0-9a-f]+)")
TSX = re.compile(r"\(TS-H(\d+)-(\d+)\) Execute TensorStore with addr: ([0-9a-f]+), stride: ([0-9a-f]+), regstart: \d+, rows: (\d+), "
                 r"cols: (\d+)")
COOP = re.compile(r"tensor_coop : 0x([0-9a-f]+) \(neighs")
MEMR = re.compile(r"MEM512\[0x([0-9a-f]+)\] :")
MEMW = re.compile(r"MEM128\[0x([0-9a-f]+)\] =")


def parse(paths, harts_wanted=None):
    st = {}

    def H(h):
        if h not in st:
            st[h] = {"mode": "?", "instr": collections.Counter(), "events": [], "killed": 0, "starts_u": set(), "starts_other": collections.Counter(),
                     "exec": None, "left": 0, "lines_read": 0, "lines_written": 0, "mismatch": 0, "pending_coop": False,
                     "exec_loads_u": 0, "exec_stores_u": 0, "nlines": 0, "shire": None, "ncoord": None}
        return st[h]
    for p in paths:
        for raw in gzip.open(p, "rt", errors="replace"):
            m = PFX.match(raw.rstrip("\n"))
            if not m:
                continue
            step, h, s, n, c, t, msg = int(m.group(1)), int(m.group(3)), int(m.group(4)), int(m.group(5)), int(m.group(6)), int(m.group(7)), m.group(8)
            if harts_wanted is not None and h not in harts_wanted:
                continue
            x = H(h)
            x["nlines"] += 1
            x["shire"], x["ncoord"] = s, (n, c, t)
            if msg.startswith("Instruction killed"):
                x["killed"] += 1
                continue
            mi = INS.match(msg)
            if mi:
                x["mode"] = mi.group(1)
                x["instr"][x["mode"]] += 1
                x["pending_coop"] = False
                continue
            body = msg.lstrip("\t")
            mm = TLS.search(body)
            if mm:
                uid = int(mm.group(2))
                if x["mode"] != "U":
                    x["starts_other"]["TensorLoad"] += 1
                    continue
                coop, tenb = int(mm.group(4)), int(mm.group(7))
                ev = ["LB" if tenb else "LA", int(mm.group(8), 16), int(mm.group(6)), coop, (None if coop else 0), int(mm.group(10)),
                      int(mm.group(11), 16), int(mm.group(12)), int(mm.group(3)), int(mm.group(5)), int(mm.group(9))]
                x["events"].append(ev)
                x["starts_u"].add(("TL", uid))
                x["pending_coop"] = bool(coop)
                continue
            mc = COOP.search(body)
            if mc:
                if x["pending_coop"] and x["events"] and x["events"][-1][4] is None:
                    x["events"][-1][4] = int(mc.group(1), 16)
                x["pending_coop"] = False
                continue
            mm = TSS.search(body)
            if mm:
                uid = int(mm.group(2))
                if x["mode"] != "U":
                    x["starts_other"]["TensorStore"] += 1
                    continue
                x["events"].append(["S", int(mm.group(3), 16), int(mm.group(4), 16), int(mm.group(6)), int(mm.group(7)), int(mm.group(5)),
                                    int(mm.group(8)), int(mm.group(9))])
                x["starts_u"].add(("TS", uid))
                continue
            mm = TMS.search(body)
            if mm:
                if x["mode"] != "U":
                    x["starts_other"][mm.group(3)] += 1
                    continue
                x["events"].append(["F", mm.group(3), int(mm.group(4)), int(mm.group(5)), int(mm.group(6)), int(mm.group(7)),
                                    int(mm.group(8)), int(mm.group(10)), int(mm.group(11)), int(mm.group(12)), int(mm.group(13))])
                continue
            mm = TLX.search(body)
            if mm:
                u = ("TL", int(mm.group(2))) in x["starts_u"]
                x["starts_u"].discard(("TL", int(mm.group(2))))
                x["exec"] = ["L", int(mm.group(3), 16), int(mm.group(5), 16), 0, u]
                x["left"] = int(mm.group(4))
                x["exec_loads_u"] += u
                continue
            mm = TSX.search(body)
            if mm:
                u = ("TS", int(mm.group(2))) in x["starts_u"]
                x["starts_u"].discard(("TS", int(mm.group(2))))
                x["exec"] = ["S", int(mm.group(3), 16), int(mm.group(4), 16), 0, u, int(mm.group(6))]
                x["left"] = int(mm.group(5)) * int(mm.group(6))
                x["exec_stores_u"] += u
                continue
            if x["exec"] is not None:
                e = x["exec"]
                mr = MEMR.search(body) if e[0] == "L" else MEMW.search(body)
                if mr:
                    a = int(mr.group(1), 16)
                    if e[0] == "L":
                        want = e[1] + e[3] * e[2]
                    else:
                        want = e[1] + (e[3] // e[5]) * e[2] + (e[3] % e[5]) * 16
                    if e[4]:
                        x["mismatch"] += a != want
                        if e[0] == "L":
                            x["lines_read"] += 1
                        else:
                            x["lines_written"] += 1
                    e[3] += 1
                    x["left"] -= 1
                    if x["left"] <= 0:
                        x["exec"] = None
    return st


def to_summ_form(ev):
    """my event -> the summarizer's list layout without the step (for comparison)"""
    k = ev[0]
    if k in ("LA", "LB"):
        _, addr, start, coop, tcoop, rows, stride, idd, msk, cmd, boff = ev
        return [k, addr, start, coop, tcoop, rows, stride, idd, msk, cmd, boff]
    if k == "S":
        _, addr, stride, rows, cols, regstart, srcinc, coop = ev
        return ["S", addr, stride, rows, cols, regstart, srcinc, coop]
    _, name, msk, bcols, arows, acols, aoff, tenb, bstart, astart, mul = ev
    return ["F", name, msk, bcols, arows, acols, aoff, tenb, bstart, astart, mul]


def summ_form(e):
    """the summarizer's event list -> the same layout (dropping its step and its leader field; FMA dst dropped: fp32 prints none)"""
    k = e[0]
    if k in ("LA", "LB"):
        return [k] + e[2:12]
    if k == "S":
        return e[:1] + e[2:]
    return ["F"] + e[2:12]


def main():
    rd = sys.argv[1]
    summ = json.load(gzip.open(os.path.join(rd, "summary.json.gz"), "rt"))
    mine = json.load(gzip.open(os.path.join(rd, "mine.json.gz"), "rt"))
    mask = int(summ["meta"]["mask"], 16)
    act = {s for s in range(32) if (mask >> s) & 1}
    out = {"run": os.path.basename(rd.rstrip("/")), "files": {}}
    for f in sorted(glob.glob(os.path.join(rd, "excerpt-*.log.gz"))):
        st = parse([f])
        res = {}
        for h, x in sorted(st.items()):
            sv = summ["harts"].get(str(h))
            mv = mine["instr"].get(str(h), {})
            mine_events = [to_summ_form(e) for e in x["events"]]
            summ_events = [summ_form(e) for e in sv["events"]] if sv else None
            r = {"shire": x["shire"], "shire_from_hart_id": h >> 6, "n_c_t": x["ncoord"], "lines_in_excerpt": x["nlines"],
                 "lines_in_mine_json": mine["lines"].get(str(h)), "instr_raw": dict(x["instr"]),
                 "instr_summarizer": (sv or {}).get("instr_by_mode"), "instr_mine_json": mv,
                 "instr_equal": dict(x["instr"]) == (sv or {}).get("instr_by_mode") == mv,
                 "u_instr": x["instr"].get("U", 0), "killed_raw": x["killed"], "killed_summarizer": (sv or {}).get("killed"),
                 "tensor_events_raw": len(x["events"]), "tensor_events_summarizer": (sv or {}).get("n_events"),
                 "events_equal": mine_events == summ_events,
                 "counts_raw": dict(collections.Counter(e[0] for e in x["events"])),
                 "other_mode_tensor_starts_raw": dict(x["starts_other"]), "outside_tensor_summarizer": (sv or {}).get("outside_tensor"),
                 "lines_read_raw": x["lines_read"], "lines_read_summarizer": (sv or {}).get("lines_read"),
                 "lines_written_raw": x["lines_written"], "lines_written_summarizer": (sv or {}).get("lines_written"),
                 "addr_mismatch_raw": x["mismatch"], "exec_loads_u_raw": x["exec_loads_u"], "exec_stores_u_raw": x["exec_stores_u"],
                 "in_mask": (h >> 6) in act}
            if not r["events_equal"] and summ_events is not None:
                i = next((i for i, (a, b) in enumerate(zip(mine_events, summ_events)) if a != b), min(len(mine_events), len(summ_events)))
                r["first_difference"] = {"index": i, "raw": mine_events[i] if i < len(mine_events) else None,
                                         "summarizer": summ_events[i] if i < len(summ_events) else None}
            res[str(h)] = r
        out["files"][os.path.basename(f)] = res
    json.dump(out, sys.stdout, indent=1, default=str)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
