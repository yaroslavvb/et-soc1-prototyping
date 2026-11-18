#!/usr/bin/env python3
"""v31-trace (Q217): ONE traced sys_emu run of a GEMM arm on aifoundry3, summarized as it streams (nothing of the log is kept), or the
summarizer alone on a log file (desk tests). Standard library only; /usr/bin/python3 3.12.

    python3 -I -B trace_run.py run --name N --host H --elf K --arm gemmL2x4x16 --values-gen tiles --tile T --type fp32 --mask 0xf \
        --log-sel '0,5555...' [--log-sel ...] --out RUNDIR [--timeout 1500]
    python3 -I -B trace_run.py summarize --log FILE --out SUMMARY.json.gz          (desk: a log file, e.g. a synthetic one)

THE RUN (THE SIMULATOR's rule; mm-timing's and kit-e211's form): the host runs with --sysemu (its runtime's simulator device layer starts the
installed sys_emu) inside bubblewrap with a private /dev holding no /dev/et* node and an empty /run/lock, under prlimit --as 4 GB, at nice
19, under a plain `timeout` (TERM only: never -k); the simulator's own options (--sim-args): -vpurf_warn -l (DEBUG) and -ls <shire>,<harts>
for each logged shire. The runtime writes the emulator's log to sysemu.log in the host's working directory: this script makes it a FIFO
and reads it in a thread, like tools/counter/run_counted.sh (a host that never opens the log gets an empty writer so the reader ends).
Refuses to start if a card process holds a device node (et-who), the 1-minute load is above 6, a simulator run of ours is going, or the
sandbox shows a card node. Its own memory is capped by the caller (prlimit).

WHAT IS KEPT per logged hart (the summary, gzip JSON): its tensor operations in program order, from the simulator's Start lines, U-mode
only (the firmware's M- and S-mode tensor operations are counted apart): TensorLoad (addr, start, coop, its tensor_coop value, rows, stride,
id, tenb, msk, cmd, boffset, the coop leader neighbourhood), TensorStore (addr, stride, rows, cols, regstart, srcinc, coop), TensorFMA32 /
16A32 / IMA8A32 (msk, bcols, arows, acols, aoffset, tenb, bstart, astart, mul, dst), anything else tensor by name; each with the
simulator's step (its emulated cycle, not time). For every Execute TensorLoad / TensorStore it checks the lines the simulator actually
read or wrote (MEM512 reads, MEM128 writes) against addr + i stride and keeps the counts, the physical-minus-virtual offsets and any
mismatch. Instruction counts per hart by privilege mode, restarts, the log's line and byte counts.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import collections
import gzip
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time

PFX = re.compile(rb"^(\d+): (\w+) EMU: \[H(\d+) S(\d+):N\d+:C\d+:T\d+\] ?(.*)$")
KV = re.compile(rb"(\w+): ?(0x[0-9a-fA-F]+\b|-?[0-9a-fA-F]+\b)")
UUID = re.compile(rb"\((T[A-Z])-H(\d+)-(\d+)\) (Start|Execute) (\w+)")
MEM = re.compile(rb"MEM(\d+)\[0x([0-9a-f]+)\] ([:=])")
COOP = re.compile(rb"tensor_coop ([:=]) 0x([0-9a-f]+)")
LEADER = re.compile(rb"Leader-neigh: (-?\d+), minion-mask=0x([0-9a-f]+), pending-mask=0x([0-9a-f]+)")
HEX_ALWAYS = {b"addr", b"stride"}   # TensorStore prints them %016x without 0x (sw-sysemu insns/tensors.cpp); TensorLoad with 0x


def kv(rest):
    out = {}
    for k, v in KV.findall(rest):
        try:
            if v.lower().startswith(b"0x") or k in HEX_ALWAYS:
                out[k.decode()] = int(v, 16)
            elif re.fullmatch(rb"-?\d+", v):
                out[k.decode()] = int(v)
        except ValueError:
            pass
    return out


class Summary:
    def __init__(self):
        self.harts = {}
        self.lines = 0
        self.bytes = 0
        self.other_lines = 0
        self.first_step = None
        self.last_step = None
        self.warn = collections.Counter()
        self.unparsed_tensor = collections.Counter()

    def hart(self, h):
        st = self.harts.get(h)
        if st is None:
            st = {"mode": "?", "instr": collections.Counter(), "killed": 0, "events": [], "outside": collections.Counter(),
                  "exec": None, "exec_left": 0, "exec_loads": 0, "exec_stores": 0, "lines_read": 0, "lines_written": 0,
                  "line_mismatch": 0, "pa_minus_va": collections.Counter(), "exec_vs_start_mismatch": 0, "starts": {}, "starts_out": set(), "outside_exec": 0, "outside_lines": 0,
                  "first_step": None, "last_step": None, "shire": None}
            self.harts[h] = st
        return st

    def feed(self, line):
        self.lines += 1
        self.bytes += len(line)
        i = line.find(b"EMU: [H")
        if i < 0:
            self.other_lines += 1
            return
        # instruction lines: track the privilege mode (cheap path)
        j = line.find(b"] I(", i)
        if j >= 0:
            h = int(line[i + 7:line.index(b" ", i + 7)])
            st = self.hart(h)
            mode = chr(line[j + 4])
            st["mode"] = mode
            st["instr"][mode] += 1
            return
        if not (b"Tensor" in line or b"MEM" in line or b"tensor_coop" in line or b"Leader" in line or b"killed" in line):
            return
        if b"MEM" in line and b"Tensor" not in line:
            # a memory line: only the lines of a tensor operation being executed on this hart are read (scalar MEM lines are skipped)
            h = int(line[i + 7:line.index(b" ", i + 7)])
            st = self.harts.get(h)
            if st is None or st["exec"] is None:
                return
        m = PFX.match(line.rstrip(b"\n"))
        if not m:
            self.warn["prefix_unparsed"] += 1
            return
        step, h, shire, rest = int(m.group(1)), int(m.group(3)), int(m.group(4)), m.group(5)
        st = self.hart(h)
        st["shire"] = shire
        if b"killed" in rest:
            st["killed"] += 1
            return
        if self.first_step is None:
            self.first_step = step
        self.last_step = step
        if b"MEM" in rest and b"Tensor" not in rest:
            if st["exec"] is None:
                return
            mm = MEM.search(rest)
            if mm and st["exec"][6]:
                # the lines of a tensor operation started outside U mode (the firmware's): consumed, counted apart
                if (st["exec"][0] == "L" and mm.group(3) == b":" and mm.group(1) == b"512") or \
                        (st["exec"][0] == "S" and mm.group(3) == b"=" and mm.group(1) == b"128"):
                    st["outside_lines"] += 1
                    st["exec_left"] -= 1
                    if st["exec_left"] <= 0:
                        st["exec"] = None
                return
            if mm:
                kind, addr, op = st["exec"][0], int(mm.group(2), 16), mm.group(3)
                if kind == "L" and op == b":" and mm.group(1) == b"512":
                    va, stride, idx = st["exec"][1], st["exec"][2], st["exec"][3]
                    exp = va + idx * stride
                    st["pa_minus_va"][addr - exp] += 1
                    if st["exec"][4] is None:
                        st["exec"][4] = addr - exp
                    elif addr - exp != st["exec"][4]:
                        st["line_mismatch"] += 1
                    st["lines_read"] += 1
                    st["exec"][3] += 1
                    st["exec_left"] -= 1
                elif kind == "S" and op == b"=" and mm.group(1) == b"128":
                    va, stride, idx, cols = st["exec"][1], st["exec"][2], st["exec"][3], st["exec"][5]
                    exp = va + (idx // cols) * stride + (idx % cols) * 16
                    if st["exec"][4] is None:
                        st["exec"][4] = addr - exp
                    elif addr - exp != st["exec"][4]:
                        st["line_mismatch"] += 1
                    st["lines_written"] += 1
                    st["exec"][3] += 1
                    st["exec_left"] -= 1
                if st["exec_left"] <= 0:
                    st["exec"] = None
            return
        if b"tensor_coop" in rest:
            mc = COOP.search(rest)
            if mc and mc.group(1) == b":" and st["events"] and st["events"][-1][0] in ("LA", "LB") and st["events"][-1][5] is None \
                    and st["mode"] == "U":
                st["events"][-1][5] = int(mc.group(2), 16)
            return
        if b"Leader-neigh" in rest:
            ml = LEADER.search(rest)
            if ml and st["events"] and st["events"][-1][0] in ("LA", "LB") and st["mode"] == "U":
                st["events"][-1][12] = int(ml.group(1))
            return
        mu = UUID.search(rest)
        if b"Start/Execute" in rest:
            name = rest.split(b"Start/Execute ", 1)[1].split(b" ", 1)[0].decode()
            if st["mode"] == "U":
                st["events"].append([name, step, kv(rest.split(name.encode(), 1)[1])])
            else:
                st["outside"][name] += 1
            return
        if not mu:
            self.unparsed_tensor[rest[:40].decode(errors="replace")] += 1
            return
        tag, uid, phase, name = mu.group(1).decode(), int(mu.group(3)), mu.group(4), mu.group(5).decode()
        f = kv(rest.split(mu.group(5), 1)[1])
        if phase == b"Execute":
            if st["exec"] is not None:
                self.warn["execute_before_previous_lines_done"] += 1
            outside = (tag, uid) in st["starts_out"]
            if outside:
                st["starts_out"].discard((tag, uid))
                st["outside_exec"] += 1
            if name == "TensorLoad":
                st["exec_loads"] += 0 if outside else 1
                s0 = st["starts"].pop(("TL", uid), None)
                if s0 is not None and (s0[0] != f.get("addr") or s0[1] != f.get("rows") or s0[2] != f.get("stride")):
                    st["exec_vs_start_mismatch"] += 1
                rows = f.get("rows", 0)
                if f.get("msk", 0):
                    rows = bin(f.get("tmask", 0xFFFF) & ((1 << rows) - 1)).count("1")
                st["exec"] = ["L", f.get("addr", 0), f.get("stride", 0), 0, None, 1, outside]
                st["exec_left"] = rows
            elif name == "TensorStore":
                st["exec_stores"] += 0 if outside else 1
                s0 = st["starts"].pop(("TS", uid), None)
                if s0 is not None and (s0[0] != f.get("addr") or s0[1] != f.get("rows") or s0[2] != f.get("stride")):
                    st["exec_vs_start_mismatch"] += 1
                st["exec"] = ["S", f.get("addr", 0), f.get("stride", 0), 0, None, max(1, f.get("cols", 1)), outside]
                st["exec_left"] = f.get("rows", 0) * f.get("cols", 0)
            return
        # a Start line
        if st["first_step"] is None:
            st["first_step"] = step
        st["last_step"] = step
        if st["mode"] != "U":
            st["outside"][name] += 1
            st["starts_out"].add((tag, uid))
            return
        if name == "TensorLoad":
            kind = "LB" if f.get("tenb", 0) else "LA"
            # [kind, step, addr, start, coop, tcoop, rows, stride, id, msk, cmd, boffset, leader]
            st["events"].append([kind, step, f.get("addr"), f.get("start"), f.get("coop"), None if f.get("coop") else 0, f.get("rows"),
                                 f.get("stride"), f.get("id"), f.get("msk"), f.get("cmd"), f.get("boffset"), None])
            st["starts"][("TL", uid)] = (f.get("addr"), f.get("rows"), f.get("stride"))
        elif name == "TensorStore":
            st["events"].append(["S", step, f.get("addr"), f.get("stride"), f.get("rows"), f.get("cols"), f.get("regstart"),
                                 f.get("srcinc"), f.get("coop")])
            st["starts"][("TS", uid)] = (f.get("addr"), f.get("rows"), f.get("stride"))
        elif name in ("TensorFMA32", "TensorFMA16A32", "TensorIMA8A32"):
            st["events"].append(["F", step, name, f.get("msk"), f.get("bcols"), f.get("arows"), f.get("acols"), f.get("aoffset"),
                                 f.get("tenb"), f.get("bstart"), f.get("astart"), f.get("mul"), f.get("dst", 0)])
        else:
            st["events"].append([name, step, f])

    def result(self, meta):
        harts = {}
        for h, st in sorted(self.harts.items()):
            ev = st["events"]
            harts[str(h)] = {"shire": st["shire"], "instr_by_mode": dict(st["instr"]), "killed": st["killed"],
                             "outside_tensor": dict(st["outside"]), "events": ev, "n_events": len(ev),
                             "counts": dict(collections.Counter(e[0] for e in ev)),
                             "exec_loads": st["exec_loads"], "exec_stores": st["exec_stores"], "lines_read": st["lines_read"],
                             "lines_written": st["lines_written"], "line_mismatch": st["line_mismatch"],
                             "pa_minus_va": {str(k): v for k, v in st["pa_minus_va"].items()},
                             "exec_vs_start_mismatch": st["exec_vs_start_mismatch"], "starts_never_executed": len(st["starts"]),
                             "outside_exec": st["outside_exec"], "outside_lines": st["outside_lines"],
                             "first_tensor_step": st["first_step"], "last_tensor_step": st["last_step"]}
        return {"meta": meta, "log_lines": self.lines, "log_bytes": self.bytes, "other_lines": self.other_lines,
                "first_step": self.first_step, "last_step": self.last_step, "warn": dict(self.warn),
                "unparsed_tensor": dict(self.unparsed_tensor.most_common(20)), "harts": harts}


def read_stream(f, summ, chunk=1 << 20):
    buf = b""
    while True:
        b = f.read(chunk)
        if not b:
            break
        buf += b
        lines = buf.split(b"\n")
        buf = lines.pop()
        for ln in lines:
            summ.feed(ln)
    if buf:
        summ.feed(buf)


def write_summary(path, res):
    with gzip.open(path, "wt") as g:
        json.dump(res, g, separators=(",", ":"))


def cmd_summarize(a):
    s = Summary()
    op = gzip.open if a.log.endswith(".gz") else open
    with op(a.log, "rb") as f:
        read_stream(f, s)
    res = s.result({"mode": "summarize", "log": os.path.basename(a.log), "python": sys.version.split()[0]})
    write_summary(a.out, res)
    print(json.dumps({"harts": len(res["harts"]), "lines": res["log_lines"], "bytes": res["log_bytes"], "out": a.out}))
    return 0


def sh(cmd, timeout=30):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout + p.stderr
    except Exception as e:  # noqa: BLE001
        return 99, repr(e)


def rss_of(names):
    """total RSS (kB) of this user's processes whose comm is in names"""
    tot, n = 0, 0
    uid = os.getuid()
    for p in os.listdir("/proc"):
        if not p.isdigit():
            continue
        try:
            if os.stat("/proc/" + p).st_uid != uid:
                continue
            comm = open("/proc/%s/comm" % p).read().strip()
            if comm not in names:
                continue
            for ln in open("/proc/%s/status" % p):
                if ln.startswith("VmRSS:"):
                    tot += int(ln.split()[1])
                    n += 1
        except OSError:
            continue
    return tot, n


def cmd_run(a):
    t_start = time.time()
    rd = os.path.abspath(a.out)
    if os.path.exists(rd):
        print("run dir exists: " + rd)
        return 8
    # refusals before anything starts
    if shutil.which("et-who"):
        rc, out = sh(["timeout", "20", "et-who"])
        if "No process holds an ET-SoC-1 device node or card lock" not in out:
            print("CARD HELD OR UNKNOWN: not running\n" + out[:400])
            return 5
    l1 = float(open("/proc/loadavg").read().split()[0])
    if l1 > 6.0:
        print("LOAD %.2f ABOVE 6: not running" % l1)
        return 6
    rc, out = sh(["pgrep", "-u", str(os.getuid()), "-x", "sys_emu"])
    if rc == 0:
        print("A sys_emu OF OURS IS RUNNING: not running")
        return 7
    rc, out = sh(["pgrep", "-u", str(os.getuid()), "-f", "sparsity_host --sysemu"])
    if rc == 0:
        print("A SIM RUN OF OURS IS GOING: not running")
        return 7
    os.makedirs(rd)
    bw = ["/usr/bin/bwrap", "--dev-bind", "/", "/", "--dev", "/dev", "--tmpfs", "/run/lock", "--die-with-parent", "--"]
    rc, out = sh(bw + ["/bin/ls", "-1", "/dev"])
    n_et = sum(1 for x in out.split() if x.startswith("et"))
    rc2, out2 = sh(bw + ["/bin/ls", "-1", "/run/lock"])
    n_lock = len([x for x in out2.split() if x])
    open(os.path.join(rd, "sandbox-check.txt"), "w").write("dev entries named et*: %d\nrun/lock entries: %d\n" % (n_et, n_lock))
    if n_et != 0:
        print("SANDBOX SHOWS A CARD NODE: not running")
        return 10
    sim = "-vpurf_warn -l " + " ".join("-ls " + s for s in a.log_sel)
    values = "%s:%s:%s" % (a.arm, a.values_gen, a.tile)
    host_cmd = [a.host, "--sysemu", "--sim-args", sim, "--test", "fma", "--type", a.type, "--pattern", "none", "--values", values,
                "--shires", a.mask, "--per-shire", "32", "--seed", "1", "--kernel", a.elf]
    full = ["timeout", str(a.timeout), "nice", "-n", "19", "prlimit", "--as=4294967296"] + bw + host_cmd
    home = os.path.expanduser("~")
    open(os.path.join(rd, "RUN.txt"), "w").write("command: " + " ".join(full).replace(home, "~") + "\n")
    fifo = os.path.join(rd, "sysemu.log")
    os.mkfifo(fifo)
    summ = Summary()
    state = {"opened": False, "error": None}

    def reader():
        try:
            with open(fifo, "rb") as f:
                state["opened"] = True
                read_stream(f, summ)
        except Exception as e:  # noqa: BLE001
            state["error"] = repr(e)

    th = threading.Thread(target=reader, daemon=True)
    th.start()
    t0 = time.time()
    errstat = collections.Counter()

    def err_filter(pipe, fe):
        # the host's stderr: the runtime's simulator layer logs every host poll of device memory ('Device memory read at', 'Processing
        # request') at INFO; those lines are counted, not kept (they would fill the disk); every other line is kept in err.log
        for ln in iter(pipe.readline, b""):
            if b"Device memory read at" in ln or b"Processing request" in ln:
                errstat["poll_lines_dropped"] += 1
                continue
            errstat["kept"] += 1
            fe.write(ln)
        pipe.close()

    with open(os.path.join(rd, "out.json"), "wb") as fo, open(os.path.join(rd, "err.log"), "wb") as fe:
        p = subprocess.Popen(full, cwd=rd, stdout=fo, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)
        te = threading.Thread(target=err_filter, args=(p.stderr, fe), daemon=True)
        te.start()
        peak_kb, samples = 0, 0
        while p.poll() is None:
            time.sleep(2.0)
            kb, n = rss_of({"sys_emu", "sparsity_host", "timeout", "prlimit", "bwrap"})
            peak_kb = max(peak_kb, kb)
            samples += 1
        hrc = p.returncode
        te.join(timeout=60)
    t1 = time.time()
    if th.is_alive() and not state["opened"]:
        # a host that never opened the log: an empty writer lets the reader end
        try:
            fd = os.open(fifo, os.O_WRONLY | os.O_NONBLOCK)
            os.close(fd)
        except OSError:
            pass
    th.join(timeout=600)
    try:
        os.unlink(fifo)
    except OSError:
        pass
    sparsity = [ln for ln in open(os.path.join(rd, "out.json"), errors="replace") if ln.startswith("SPARSITY ")]
    meta = {"mode": "run", "name": a.name, "arm": a.arm, "type": a.type, "mask": a.mask, "values_gen": a.values_gen,
            "log_sel": a.log_sel, "sim_args": sim, "host_rc": hrc, "host_wall_s": round(t1 - t0, 1), "reader_error": state["error"],
            "reader_alive_after_join": th.is_alive(), "peak_rss_kb_sum_of_sim_tree": peak_kb, "rss_samples": samples,
            "stderr_lines": dict(errstat),
            "sparsity": [json.loads(x[9:]) for x in sparsity], "python": sys.version.split()[0],
            "start_epoch": int(t_start), "end_epoch": int(time.time()),
            "host_sha256": sh(["sha256sum", a.host])[1].split()[0], "elf_sha256": sh(["sha256sum", a.elf])[1].split()[0]}
    res = summ.result(meta)
    write_summary(os.path.join(rd, "summary.json.gz"), res)
    cnt = collections.Counter()
    for v in res["harts"].values():
        cnt.update(v["counts"])
    print("run %s rc=%d wall=%.0f s; log %d lines %.2f GB; harts %d; events %s; peak RSS %.0f MB; reader_error %s" % (
        a.name, hrc, t1 - t0, res["log_lines"], res["log_bytes"] / 1e9, len(res["harts"]), dict(cnt), peak_kb / 1024.0, state["error"]))
    for x in sparsity:
        print(x.strip()[:700].replace(home, "~"))
    return 0 if hrc == 0 and state["error"] is None else (hrc or 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--name", required=True)
    r.add_argument("--host", required=True)
    r.add_argument("--elf", required=True)
    r.add_argument("--arm", required=True)
    r.add_argument("--values-gen", default="tiles")
    r.add_argument("--tile", required=True)
    r.add_argument("--type", default="fp32")
    r.add_argument("--mask", required=True)
    r.add_argument("--log-sel", action="append", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--timeout", type=int, default=1500)
    s = sub.add_parser("summarize")
    s.add_argument("--log", required=True)
    s.add_argument("--out", required=True)
    a = ap.parse_args()
    return cmd_run(a) if a.cmd == "run" else cmd_summarize(a)


if __name__ == "__main__":
    sys.exit(main())
