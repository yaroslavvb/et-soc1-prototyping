#!/usr/bin/env python3
"""E199 (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum): THE KIT'S GATE, run by session_e199.sh beside E192's reference
session (run_session.sh, unchanged) on aifoundry1 card 1. E192's gate (tools/claims-v3/e192/gate_e192.py, a6fe5c20, unchanged beside it:
THE SMOKE GATE and THE CAP, word for word in effect) with card 1's three additions (E199.md sections 3, 7 and 15). It opens no device and
sends no command: it reads the session's own files (marks.jsonl, runs.jsonl and stderr.txt, written by run_block.py; telemetry.jsonl, the
sampler's), et-who's answer and /proc of the session's own processes, and acts only through the registered stop file OUT/STOP, which
run_block.py checks before every device process and the host before every 0.4 s launch ("the kit may add stops that end a session early";
E199.md section 15). Five stops, nothing else:
  THE SMOKE GATE (E192's): when the smoke block (pass -1) has recorded its three runs, each must have its device process's exit 0, at
  least 3 INTBITS lines, on every line "ok" true, "check_bad" 0 and 1,024 participants; the smoke's heater launch exit 0; the smoke's arms
  in order; and, E199's addition (E191's dated note 1, item 3(c): "in the smoke each device-opening process must also have shown card 1"),
  the smoke's device processes (the heater check and the three runs) each printed the device layer's identity block naming card 1 on its
  stderr (run_block.py appends every device process's stderr to OUT/stderr.txt; each prints one block when it opens its node: 706 blocks
  for 706 device processes in E192's committed stderr.txt) and none named another card. Else STOP before any pass.
  THE CAP (E192's): 65 card-minutes from the first card command; the next pass starts only if now + gap + D fits (D the longest measured
  pass + 60 s, else D0 400 s); 30 s before the cap, STOP.
  CARD 1'S LIVE STOP LINES (E199.md section 7; E191's kit, e191_common.Stops): board_w at or above 65 W, or temp_c.minshire[0] (the shire
  mean) at or above 70 C, on any live sample of the session's sampler: STOP (the running device process finishes, nothing further starts).
  THE IDENTITY GATE (b) (E191's dated note 1, item 3(b), by ident_e199.etwho_b on E191's e191_ident, unchanged): with the sampler running
  (its first telemetry line written) and before the smoke's first launch, et-who's holder lines of our login are all on card 1, at least
  one on /dev/et1_mgmt, none on card 0, none of another login, and the sampler's own open files hold /dev/et1_mgmt and nothing of card 0.
  Failing, or not decided within --b-deadline s of the first sample (8 s: the smoke's first launch comes at least 20 s after the sampler
  starts, run_session.sh's 10 s and the smoke's 10 s 'before' idle), or decided only after a device process of the session had started:
  STOP before any launch (a gate, no data).
  THE WATCH (E191's item 3(c), on every device process, from outside): every 0.1 s, the new text of OUT/stderr.txt (any identity block
  naming a card other than 1) and the open files and mappings of every process under the wrapper (--root-pid; e191_ident.proc_nodes: a
  card 0 node, or card 0's lock file open): STOP, the process in flight finishing by its own budget (never a kill).
    python3 -I -B gate_e199.py OUT --first EPOCH --cap 3900 --root-pid PID [--d0 400] [--gap 30] [--passes 9] [--b-deadline 8]
Writes OUT/gate.jsonl (one event a line) and prints each event. Exits when OUT/SESSION_DONE appears, or after a STOP (its own or anyone's).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "e191"))
import e191_ident as I  # noqa: E402   E191's, unchanged
import ident_e199 as IE  # noqa: E402

SMOKE_ARMS = ("nop", "add.a.f2", "add.cr.l31")
PARTICIPANTS = 1024
MIN_LAUNCHES = 3
MARGIN_S = 60.0
HARD_S = 30.0
BOARD_STOP_W = 65.0
DIE_STOP_C = 70.0
CARD0_LOCK = "/run/lock/etsoc-shire0.lock"
DEVICE_KINDS = ("heater_check", "heater", "run")
RE_TARGET_LINE = re.compile(r"^PCIe target:\s+/dev/et(\d+)_(ops|mgmt)\b", re.M)


class Tail:
    """New complete JSON lines of a file that grows."""

    def __init__(self, path):
        self.path, self.pos, self.buf = path, 0, ""

    def read(self):
        try:
            with open(self.path, "rb") as f:
                f.seek(self.pos)
                chunk = f.read()
                self.pos = f.tell()
        except OSError:
            return []
        self.buf += chunk.decode(errors="ignore")
        *lines, self.buf = self.buf.split("\n")
        out = []
        for ln in lines:
            ln = ln.strip()
            if ln.startswith("{") and ln.endswith("}"):
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    pass
        return out


class TextTail:
    """The new text of a file that grows (whole lines only)."""

    def __init__(self, path):
        self.path, self.pos, self.buf = path, 0, ""

    def read(self):
        try:
            with open(self.path, "rb") as f:
                f.seek(self.pos)
                chunk = f.read()
                self.pos = f.tell()
        except OSError:
            return ""
        self.buf += chunk.decode(errors="replace")
        i = self.buf.rfind("\n")
        if i < 0:
            return ""
        out, self.buf = self.buf[:i + 1], self.buf[i + 1:]
        return out


def smoke_verdict(marks, runs, blocks):
    """(ok, rows, why) for the smoke block: E192's conditions, then each smoke device process's card-1 identity block (blocks: the cards
    named by the identity blocks printed so far, in order)."""
    rm = [m for m in marks if m.get("kind") == "run" and m.get("pass") == -1]
    bad, rows = [], []
    for m in rm:
        seq, arm = m.get("seq"), m.get("arm")
        lines = [r for r in runs if r.get("pass") == -1 and r.get("seq") == seq]
        n = len(lines)
        nok = sum(1 for r in lines if r.get("ok") is True)
        nbad = sum(1 for r in lines if r.get("check_bad", 1) != 0)
        parts = sorted({r.get("participants") for r in lines}, key=str)
        rows.append({"seq": seq, "arm": arm, "rc": m.get("rc"), "launches": n, "ok": nok, "check_bad_lines": nbad,
                     "participants": parts})
        why = []
        if m.get("rc") != 0:
            why.append("exit %s" % m.get("rc"))
        if n < MIN_LAUNCHES:
            why.append("%d INTBITS lines (< %d)" % (n, MIN_LAUNCHES))
        if nok != n:
            why.append("%d of %d lines not ok" % (n - nok, n))
        if nbad:
            why.append("check_bad on %d lines" % nbad)
        if parts != [PARTICIPANTS]:
            why.append("participants %s" % parts)
        if why:
            bad.append("%s: %s" % (arm, ", ".join(why)))
    hcm = [m for m in marks if m.get("kind") == "heater_check" and m.get("pass") == -1]
    for m in hcm:
        rows.append({"heater_check_rc": m.get("rc")})
        if m.get("rc") != 0:
            bad.append("the heater check's launch exited %s" % m.get("rc"))
    arms = [m.get("arm") for m in rm]
    if tuple(arms) != SMOKE_ARMS:
        bad.append("the smoke's arms were %s, not %s" % (arms, list(SMOKE_ARMS)))
    ndev = len([m for m in marks if m.get("pass") == -1 and m.get("kind") in DEVICE_KINDS])
    rows.append({"identity_blocks": len(blocks), "card1_blocks": blocks.count("1"), "smoke_device_processes": ndev})
    if blocks.count("1") != ndev or len(blocks) != ndev:
        bad.append("%d identity block(s) naming card 1 (of %d printed) for the smoke's %d device process(es): each must show card 1"
                   % (blocks.count("1"), len(blocks), ndev))
    return (not bad), rows, "; ".join(bad)


def stderr_wrong(text):
    """THE WATCH's reading of device processes' stderr text: ([the card each identity block's 'PCIe target' line names, in order],
    [everything that names a card other than card 1]); e191_ident.parse_ident reads the block's lines."""
    blocks = [m.group(1) for m in RE_TARGET_LINE.finditer(text)]
    targets, ids = I.parse_ident(text)
    wrong = sorted({"/dev/et%s_%s" % t for t in targets if t[0] != I.CARD} | {"Physical device ID %d" % i for i in ids if str(i) != I.CARD})
    return blocks, wrong


def comm(pid):
    try:
        with open("/proc/%d/comm" % pid) as f:
            return f.read().strip()
    except OSError:
        return ""


def cmdline(pid):
    try:
        with open("/proc/%d/cmdline" % pid, "rb") as f:
            return [w.decode(errors="ignore") for w in f.read().split(b"\0") if w]
    except OSError:
        return []


def find_sampler(pids):
    """The session's sampler among its processes: run_session.sh's own `"$ETTELEM" sample ...` (comm ettelem, or argv[0] the reader's
    path) or, with SAMPLER=pvt, `python3 -B "$PVT_SAMPLE" --seconds ...` (never the probe); SAMPLER and PVT_SAMPLE as the wrapper exports."""
    smp = os.environ.get("SAMPLER", "ettelem")
    pv = os.path.basename(os.environ.get("PVT_SAMPLE", "") or "pvt_sample.py")
    for p in pids:
        c, cl = comm(p), cmdline(p)
        if smp == "pvt":
            if any(w.endswith(pv) for w in cl) and "--probe" not in cl and "--seconds" in cl:
                return p
        elif (c == "ettelem" or (cl and cl[0].endswith("/ettelem"))) and "sample" in cl:
            return p
    return None


def holds_card0_lock(pid):
    try:
        for fd in os.listdir("/proc/%d/fd" % pid):
            try:
                if os.readlink("/proc/%d/fd/%s" % (pid, fd)) == CARD0_LOCK:
                    return True
            except OSError:
                continue
    except OSError:
        pass
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--first", type=float, required=True, help="the session's first card command, epoch seconds")
    ap.add_argument("--cap", type=float, required=True)
    ap.add_argument("--root-pid", type=int, required=True, help="the wrapper's pid: every process of the session is under it")
    ap.add_argument("--d0", type=float, default=400.0)
    ap.add_argument("--gap", type=float, default=30.0)
    ap.add_argument("--passes", type=int, default=9)
    ap.add_argument("--b-deadline", type=float, default=8.0)
    a = ap.parse_args()
    me = os.getpid()
    stop_file = os.path.join(a.out, "STOP")
    done_file = os.path.join(a.out, "SESSION_DONE")
    tm, tr = Tail(os.path.join(a.out, "marks.jsonl")), Tail(os.path.join(a.out, "runs.jsonl"))
    tt = Tail(os.path.join(a.out, "telemetry.jsonl"))
    te = TextTail(os.path.join(a.out, "stderr.txt"))
    marks, runs, blocks = [], [], []
    smoke_done, smoke_due = False, None
    began, durs, seen_after = {}, {}, set()
    first_tel, b_done = None, False
    dev_seen = {}       # pid -> comm, every device process of the session the watch saw
    nsamples = 0

    def event(kind, **kw):
        rec = dict(t_ms=int(time.time() * 1000), kind=kind, **kw)
        with open(os.path.join(a.out, "gate.jsonl"), "a") as f:
            f.write(json.dumps(rec) + "\n")
        print("gate_e199: " + json.dumps(rec), flush=True)

    def stop(why, **kw):
        if not os.path.exists(stop_file):
            with open(stop_file, "w") as f:
                f.write(json.dumps({"by": "gate_e199", "why": why, "t_ms": int(time.time() * 1000)}) + "\n")
        event("stop", why=why, **kw)
        sys.exit(0)

    def smoke_check():
        nonlocal smoke_done, runs
        runs += tr.read()
        ok, rows, why = smoke_verdict(marks, runs, blocks)
        smoke_done = True
        if not ok:
            stop("smoke gate: " + why, runs=rows)
        event("smoke_gate", verdict="GO", runs=rows)

    event("start", first=a.first, cap_s=a.cap, d0_s=a.d0, gap_s=a.gap, passes=a.passes, root_pid=a.root_pid,
          b_deadline_s=a.b_deadline, board_stop_w=BOARD_STOP_W, die_stop_c=DIE_STOP_C,
          cap_at=time.strftime("%H:%M:%S %Z", time.localtime(a.first + a.cap)))
    while True:
        if os.path.exists(done_file):
            event("session_done", samples=nsamples, device_processes_watched=len(dev_seen))
            return 0
        if os.path.exists(stop_file):
            try:
                why = open(stop_file).read().strip()[:300]
            except OSError:
                why = "?"
            event("stop_seen", stop=why)
            return 0
        now = time.time()
        # ---- THE WATCH: every process under the wrapper (its open card nodes and card 0's lock), and the device layer's blocks ----
        pids = [p for p in I.descendants(a.root_pid) if p not in (me, a.root_pid)]
        for p in pids:
            nodes = I.proc_nodes(p)
            off = sorted("/dev/et%s_%s" % n for n in nodes if n[0] != I.CARD)
            c = comm(p)
            if re.search(r"_host$|^ettelem$", c) or any(w.endswith("pvt_sample.py") for w in cmdline(p)):
                dev_seen.setdefault(p, c)
            if off:
                stop("the watch: process %d (%s) of the session holds %s, not card 1's node" % (p, c, ",".join(off)), pid=p)
            if holds_card0_lock(p):
                stop("the watch: process %d (%s) of the session holds card 0's lock file open" % (p, c), pid=p)
        new_err = te.read()
        if new_err:
            nb, wrong = stderr_wrong(new_err)
            blocks += nb
            if wrong:
                stop("the watch: a device process of the session named another card on its stderr (%s)" % ", ".join(wrong))
        # ---- CARD 1'S LIVE STOP LINES, on every sample ----
        for s in tt.read():
            nsamples += 1
            if first_tel is None:
                first_tel = time.time()
                event("first_sample", sample_t_ms=s.get("t_ms"))
            bw = s.get("board_w")
            die = ((s.get("temp_c") or {}).get("minshire") or [None])[0]
            if isinstance(bw, (int, float)) and bw >= BOARD_STOP_W:
                stop("card 1's live stop: board %s W at or above %g W (sample t_ms %s)" % (bw, BOARD_STOP_W, s.get("t_ms")))
            if isinstance(die, (int, float)) and die >= DIE_STOP_C:
                stop("card 1's live stop: minshire[0] %s C at or above %g C (sample t_ms %s)" % (die, DIE_STOP_C, s.get("t_ms")))
        # ---- THE IDENTITY GATE (b): with the sampler running, before the smoke's first launch ----
        new_m = tm.read()
        marks += new_m
        if not b_done and first_tel is not None:
            launched = [p for p, c in dev_seen.items() if c.endswith("_host")]
            mk = [m for m in marks if m.get("kind") in DEVICE_KINDS]
            if launched or mk:
                stop("identity gate (b): a device process of the session started before the gate was decided (%s)" % (launched or "a mark"))
            sp = find_sampler(pids)
            try:
                r = subprocess.run(["timeout", "20", "et-who"], capture_output=True, text=True)
                lines, rc = r.stdout.splitlines(), r.returncode
            except OSError as ex:
                lines, rc = [], 127
                print("gate_e199: et-who could not run: %s" % ex, flush=True)
            why, counts, nodes = IE.etwho_b(lines, rc, sp)
            if why:
                stop("identity gate (b): " + why, counts=counts, sampler_nodes=nodes)
            nm2 = tm.read()
            marks += nm2
            new_m += nm2
            launched = [p for p in I.descendants(a.root_pid) if comm(p).endswith("_host")]
            if launched or [m for m in nm2 if m.get("kind") in DEVICE_KINDS]:
                stop("identity gate (b): decided only after a device process of the session had started")
            b_done = True
            event("identity_b", verdict="OK", counts=counts, sampler_pid=sp, sampler_nodes=nodes,
                  decided_s_after_first_sample=round(time.time() - first_tel, 2))
        if not b_done and first_tel is not None and time.time() - first_tel > a.b_deadline:
            stop("identity gate (b): not decided within %g s of the first sample (before the smoke's first launch)" % a.b_deadline)
        # ---- E192's two gates ----
        runs += tr.read()
        if new_m and not b_done and [m for m in new_m if m.get("kind") in DEVICE_KINDS]:
            stop("identity gate (b): a device process ran before the gate was decided")
        if not smoke_done:
            nrun = sum(1 for m in marks if m.get("kind") == "run" and m.get("pass") == -1)
            p0 = any(m.get("pass", -1) >= 0 for m in marks)
            if nrun >= len(SMOKE_ARMS) and smoke_due is None:
                smoke_due = now + 0.8
            if (smoke_due is not None and now >= smoke_due) or p0:
                nb, wrong = stderr_wrong(te.read())
                blocks += nb
                if wrong:
                    stop("the watch: a device process of the session named another card on its stderr (%s)" % ", ".join(wrong))
                smoke_check()
        for m in new_m:
            p = m.get("pass", -1)
            if m.get("kind") == "idle" and m.get("label") == "before" and p >= 0:
                began[p] = m.get("t0_ms", 0) / 1000.0
            if m.get("kind") == "idle" and m.get("label") == "after" and p not in seen_after:
                seen_after.add(p)
                if p >= 0 and p in began:
                    durs[p] = m.get("t1_ms", 0) / 1000.0 - began[p]
                if p == -1 and not smoke_done:
                    smoke_check()
                nxt = p + 1
                if nxt >= a.passes:
                    event("last_block_done", block=p)
                    continue
                d = (max(durs.values()) + MARGIN_S) if durs else a.d0
                need = (a.gap if nxt > 0 else 0.0) + d
                left = a.first + a.cap - time.time()
                if need > left:
                    stop("cap: pass %d could end after the cap (%.0f s needed: %s; %.0f s left of %.0f)" % (
                        nxt, need, "the longest pass so far %.0f s + %.0f s" % (max(durs.values()), MARGIN_S) if durs
                        else "D0 %.0f s" % a.d0, left, a.cap), next_pass=nxt, measured=durs)
                event("cap_ok", next_pass=nxt, need_s=round(need, 1), left_s=round(left, 1),
                      measured={str(k): round(v, 1) for k, v in durs.items()})
        if time.time() >= a.first + a.cap - HARD_S:
            stop("cap: %.0f s before the cap (%.0f s from the first card command): the run in flight finishes, no more" % (
                HARD_S, a.cap))
        time.sleep(0.1)


if __name__ == "__main__":
    sys.exit(main())
