#!/usr/bin/env python3
"""verify-v31trace (Q217): ONE traced sys_emu run on aifoundry3 (THE SIMULATOR rule), this lane's own runner.

The host runs with --sysemu inside bubblewrap (a private /dev with no /dev/et* node, an empty /run/lock), under prlimit --as 4 GB, nice 19
and a plain `timeout` (TERM only, never -k); sys_emu's options go through --sim-args (-vpurf_warn -l and one -ls <shire>,<harts> per logged
shire). The emulator's log (sysemu.log in the host's cwd) is a FIFO read by one thread that feeds, line by line:
  (1) v31-trace's own summarizer class (trace_run.py's Summary, imported from a byte-checked copy, sha256 87161c2a...), so the run's
      summary.json.gz has exactly the form of t1-t8's and can be read by check_v31.py;
  (2) this lane's own counters for EVERY logged hart (lines, instruction lines by privilege mode, tensor Start lines by name and mode),
      parsed from sys_emu's printf formats (emu_gio.cpp lprintf, insn_util.h I(%c), tensors.cpp Start lines), independent of (1);
  (3) raw excerpts: every line of the harts named by --excerpt-hart and of the shires named by --excerpt-shire, gzip, for a desk parse.
Nothing else of the log is kept. Refuses to start when a card process holds a device node (et-who), the 1-minute load is above 6, a
simulator run of this user is going, or the sandbox shows a card node. /usr/bin/python3 3.12.3, standard library.
"""
import argparse
import collections
import gzip
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time

TRACE_RUN_SHA = "87161c2a6af5158b125948e8a8ccbec3447354bcd95e470b08729e0149f4cae4"
HART = re.compile(rb"EMU: \[H(\d+) ")
START = re.compile(rb"\((T[A-Z])-H(\d+)-(\d+)\) Start (\w+)")


def sh(cmd, timeout=30):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout + p.stderr
    except Exception as e:  # noqa: BLE001
        return 99, repr(e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--host", required=True)
    ap.add_argument("--elf", required=True)
    ap.add_argument("--tile", required=True)
    ap.add_argument("--arm", required=True)
    ap.add_argument("--mask", required=True)
    ap.add_argument("--log-sel", action="append", required=True)
    ap.add_argument("--excerpt-hart", action="append", type=int, default=[])
    ap.add_argument("--excerpt-shire", action="append", type=int, default=[])
    ap.add_argument("--trace-run", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--timeout", type=int, default=1500)
    a = ap.parse_args()
    t_start = time.time()
    got = hashlib.sha256(open(a.trace_run, "rb").read()).hexdigest()
    if got != TRACE_RUN_SHA:
        print("trace_run.py copy is not v31-trace's v3 (%s): not running" % got)
        return 4
    spec = importlib.util.spec_from_file_location("v31_trace_run", a.trace_run)
    TR = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(TR)
    rd = os.path.abspath(a.out)
    if os.path.exists(rd):
        print("run dir exists: " + rd)
        return 8
    if shutil.which("et-who"):
        rc, out = sh(["timeout", "20", "et-who"])
        if "No process holds an ET-SoC-1 device node or card lock" not in out:
            print("CARD HELD OR UNKNOWN: not running\n" + out[:400])
            return 5
    l1 = float(open("/proc/loadavg").read().split()[0])
    if l1 > 6.0:
        print("LOAD %.2f ABOVE 6: not running" % l1)
        return 6
    for pat in (["-x", "sys_emu"], ["-f", "sparsity_host --sysemu"]):
        rc, out = sh(["pgrep", "-u", str(os.getuid())] + pat)
        if rc == 0:
            print("A SIMULATOR RUN OF THIS USER IS GOING (%s): not running" % pat[-1])
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
    values = "%s:tiles:%s" % (a.arm, a.tile)
    host_cmd = [a.host, "--sysemu", "--sim-args", sim, "--test", "fma", "--type", "fp32", "--pattern", "none", "--values", values,
                "--shires", a.mask, "--per-shire", "32", "--seed", "1", "--kernel", a.elf]
    full = ["timeout", str(a.timeout), "nice", "-n", "19", "prlimit", "--as=4294967296"] + bw + host_cmd
    home = os.path.expanduser("~")
    open(os.path.join(rd, "RUN.txt"), "w").write("command: " + " ".join(full).replace(home, "~") + "\n")
    fifo = os.path.join(rd, "sysemu.log")
    os.mkfifo(fifo)
    summ = TR.Summary()
    mine = {"lines": collections.Counter(), "instr": collections.defaultdict(collections.Counter),
            "start": collections.defaultdict(collections.Counter), "mode": {}, "other_lines": 0}
    ex_harts = set(a.excerpt_hart)
    ex_shires = set(a.excerpt_shire)
    exf = {}
    for h in sorted(ex_harts):
        exf[("h", h)] = gzip.open(os.path.join(rd, "excerpt-hart%d.log.gz" % h), "wb", compresslevel=3)
    for s in sorted(ex_shires):
        exf[("s", s)] = gzip.open(os.path.join(rd, "excerpt-shire%d.log.gz" % s), "wb", compresslevel=3)
    state = {"opened": False, "error": None}

    def mine_feed(ln):
        m = HART.search(ln)
        if not m:
            mine["other_lines"] += 1
            return
        h = int(m.group(1))
        mine["lines"][h] += 1
        j = ln.find(b"] I(", m.end())
        if j >= 0:
            md = chr(ln[j + 4])
            mine["mode"][h] = md
            mine["instr"][h][md] += 1
        else:
            ms = START.search(ln)
            if ms:
                mine["start"][h][ms.group(4).decode() + "@" + mine["mode"].get(h, "?")] += 1
        if h in ex_harts:
            exf[("h", h)].write(ln + b"\n")
        if (h >> 6) in ex_shires:
            exf[("s", h >> 6)].write(ln + b"\n")

    def reader():
        try:
            with open(fifo, "rb") as f:
                state["opened"] = True
                buf = b""
                while True:
                    b = f.read(1 << 20)
                    if not b:
                        break
                    buf += b
                    lines = buf.split(b"\n")
                    buf = lines.pop()
                    for ln in lines:
                        summ.feed(ln)
                        mine_feed(ln)
                if buf:
                    summ.feed(buf)
                    mine_feed(buf)
        except Exception as e:  # noqa: BLE001
            state["error"] = repr(e)

    th = threading.Thread(target=reader, daemon=True)
    th.start()
    errstat = collections.Counter()

    def err_filter(pipe, fe):
        for ln in iter(pipe.readline, b""):
            if b"Device memory read at" in ln or b"Processing request" in ln:
                errstat["poll_lines_dropped"] += 1
                continue
            errstat["kept"] += 1
            if errstat["kept"] <= 20000:
                fe.write(ln)
        pipe.close()

    t0 = time.time()
    with open(os.path.join(rd, "out.json"), "wb") as fo, open(os.path.join(rd, "err.log"), "wb") as fe:
        p = subprocess.Popen(full, cwd=rd, stdout=fo, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)
        te = threading.Thread(target=err_filter, args=(p.stderr, fe), daemon=True)
        te.start()
        peak_kb = 0
        while p.poll() is None:
            time.sleep(2.0)
            tot = 0
            for pid in os.listdir("/proc"):
                if not pid.isdigit():
                    continue
                try:
                    if os.stat("/proc/" + pid).st_uid != os.getuid():
                        continue
                    if open("/proc/%s/comm" % pid).read().strip() not in ("sys_emu", "sparsity_host", "timeout", "prlimit", "bwrap"):
                        continue
                    for x in open("/proc/%s/status" % pid):
                        if x.startswith("VmRSS:"):
                            tot += int(x.split()[1])
                except OSError:
                    continue
            peak_kb = max(peak_kb, tot)
        hrc = p.returncode
        te.join(timeout=60)
    t1 = time.time()
    if th.is_alive() and not state["opened"]:
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
    for f in exf.values():
        f.close()
    sparsity = [ln for ln in open(os.path.join(rd, "out.json"), errors="replace") if ln.startswith("SPARSITY ")]
    meta = {"mode": "run", "name": a.name, "arm": a.arm, "type": "fp32", "mask": a.mask, "values_gen": "tiles", "log_sel": a.log_sel,
            "sim_args": sim, "host_rc": hrc, "host_wall_s": round(t1 - t0, 1), "reader_error": state["error"],
            "reader_alive_after_join": th.is_alive(), "peak_rss_kb_sum_of_sim_tree": peak_kb, "stderr_lines": dict(errstat),
            "sparsity": [json.loads(x[9:]) for x in sparsity], "python": sys.version.split()[0], "start_epoch": int(t_start),
            "end_epoch": int(time.time()), "host_sha256": sh(["sha256sum", a.host])[1].split()[0],
            "elf_sha256": sh(["sha256sum", a.elf])[1].split()[0], "runner": "verify-v31trace vt_run.py",
            "summarizer": "v31-trace trace_run.py Summary " + TRACE_RUN_SHA[:16]}
    res = summ.result(meta)
    TR.write_summary(os.path.join(rd, "summary.json.gz"), res)
    mj = {"meta": meta, "other_lines": mine["other_lines"], "lines": {str(k): v for k, v in sorted(mine["lines"].items())},
          "instr": {str(k): dict(v) for k, v in sorted(mine["instr"].items())},
          "start": {str(k): dict(v) for k, v in sorted(mine["start"].items())}}
    with gzip.open(os.path.join(rd, "mine.json.gz"), "wt") as g:
        json.dump(mj, g, separators=(",", ":"))
    print("run %s rc=%d wall=%.0f s; log %d lines %.2f GB; harts %d (mine %d); peak RSS %.0f MB; reader_error %s" % (
        a.name, hrc, t1 - t0, res["log_lines"], res["log_bytes"] / 1e9, len(res["harts"]), len(mine["lines"]), peak_kb / 1024.0,
        state["error"]))
    for x in sparsity:
        print(x.strip()[:600].replace(home, "~"))
    return 0 if hrc == 0 and state["error"] is None else (hrc or 1)


if __name__ == "__main__":
    sys.exit(main())
