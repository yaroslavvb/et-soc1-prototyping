#!/usr/bin/env python3
"""Q141(k) v2, the card day's runbook: the one bounded runner every remote call and every collector goes through.

    python3 -B rb_run.py --cls probe|read|copy|wait|launch|desk --host <box or local> --step <step> --what <text> \
        [--stdin <file>] [--cwd <dir>] [--cap <capture file>] [--stdout <file>] [--host-from <regex>] -- <command> [<arg> ...]

The successor of ../rb_run.py (lab e962227a), which is unchanged. v2 adds one option and changes nothing else: --host-from, a
regex with one group, names the box a login link came from when one call reaches several boxes (E167's collector reads the
history on aifoundry1, aifoundry2 and aifoundry3, and reports a link as "TAILSCALE CHECK NEEDED (ssh <box> ...)"). On a link,
the lock line and the links line name the group's last match in the call's recent output, or --host when nothing matches;
the log line then carries link_host=<that box> beside host=. Without --host-from it behaves exactly as v1.

It runs the command in a new session with stdin from --stdin (or /dev/null), never a terminal, so nothing can prompt; it reads
stdout and stderr as they come, and:
  * a login link (a Tailscale check URL, login.tailscale.com) on either stream kills the call at once (every process under it,
    TERM then KILL 2 s later), appends "<HH:MM:SS> <host> needs a check" to the lock file $RB_LOCK, keeps the link in $RB_LINKS
    (outside the repo, for the person who approves it) and exits 11;
  * a call past its bound is killed the same way (TERM, then KILL 10 s later; the probe 2 s later) and exits 13; a probe that
    does not answer in its 15 s, or exits non-zero, exits 12;
  * a command that exits non-zero exits 14 (its own status is in the log line); 0 is 0.
Every call appends one line to $RB_LOG with its class, host, bound, seconds, exit status and the command. What the call printed
goes to stdout and to --cap with every et-who holder line's login and command masked (the counts and the node stay), and any
other user's login mark (users:<login>, holders:<login>) masked, so no lab user's name lands in a file. --stdout also
writes the command's own stdout, unchanged, to a file (a kit's `> results.txt`).

The bounds (seconds; RB_<CLS>_S overrides one, for the desk test only): probe 15, read 60, copy 600, wait 600, launch 60,
desk 5400. Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import os
import re
import selectors
import shlex
import signal
import subprocess
import sys
import time

BOUNDS = {"probe": 15, "read": 60, "copy": 600, "wait": 600, "launch": 60, "desk": 5400}
GRACE = {"probe": 2}
LINK = re.compile(r"login\.tailscale\.com")
URL = re.compile(r"https?://login\.tailscale\.com/[^\s'\"<>]*")
# et-holders (tools/lab/et-holders): '%-14s %s' of the node or lock:<file>, then ps's user, pid, etime and args
HOLDER = re.compile(r"^(\s*)(/dev/et\d+_\S+|lock:\S+)(\s+)(\S+)(\s+)(\d+)(\s+)([\d:.-]+)(.*)$")
MARKS = [(re.compile(r"(users:)(?!<)[^;\"'\s\]\)]+"), r"\1<another lab user>"),           # E111's mark form
         (re.compile(r"(holders:)(?!<)[^;\"'\s\]\)]+"), r"\1<holder>"),                   # lib.sh's others-present form
         (re.compile(r"(holders=\[)[^\]]*(\])"), r"\1<masked>\2")]                         # block scripts' others-present form
E_LINK, E_PROBE, E_TIMEOUT, E_FAIL = 11, 12, 13, 14


def mask(line):
    m = HOLDER.match(line)
    if m:
        line = f"{m.group(1)}{m.group(2)}{m.group(3)}<holder>{m.group(5)}{m.group(6)}{m.group(7)}{m.group(8)} <command withheld>"
    for pat, rep in MARKS:
        line = pat.sub(rep, line)
    return line


def tree(root):
    """{pid: pgid} of every process under root, read from ps (macOS and Linux)."""
    try:
        out = subprocess.run(["ps", "-A", "-o", "pid=,ppid=,pgid="], capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        return {}
    kids, grp = {}, {}
    for ln in out.splitlines():
        p = ln.split()
        if len(p) == 3 and all(x.isdigit() for x in p):
            kids.setdefault(int(p[1]), []).append(int(p[0]))
            grp[int(p[0])] = int(p[2])
    seen, todo = {}, [root]
    while todo:
        x = todo.pop()
        for k in kids.get(x, []):
            if k not in seen:
                seen[k] = grp.get(k)
                todo.append(k)
    return seen


def descendants(root):
    return list(tree(root))


def same(pid, pgid):
    """alive and still in the process group it was seen in (a reused pid is never signalled)"""
    try:
        return os.getpgid(pid) == pgid
    except OSError:
        return False


def kill_tree(proc, grace, known=None):
    known = known or {}
    pids = [proc.pid] + descendants(proc.pid) + [p for p, g in known.items() if same(p, g)]
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(proc.pid, sig)
        except OSError:
            pass
        for p in pids:
            try:
                os.kill(p, sig)
            except OSError:
                pass
        t = time.time() + grace
        while time.time() < t and proc.poll() is None:
            time.sleep(0.05)
        if sig == signal.SIGTERM:
            time.sleep(0.2)
            pids = [p for p in pids if alive(p)]
            if proc.poll() is not None and not pids:
                return


def alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def append(path, text):
    if not path:
        return
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        os.write(fd, text.encode())
    finally:
        os.close(fd)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cls", required=True, choices=sorted(BOUNDS))
    ap.add_argument("--host", required=True)
    ap.add_argument("--step", required=True)
    ap.add_argument("--what", default="")
    ap.add_argument("--stdin")
    ap.add_argument("--cwd")
    ap.add_argument("--cap")
    ap.add_argument("--stdout", dest="stdout_file")
    ap.add_argument("--host-from", dest="host_from")
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd[:1] == ["--"] else a.cmd
    if not cmd:
        sys.exit("rb_run: no command")
    lock, log, links = os.environ.get("RB_LOCK"), os.environ.get("RB_LOG"), os.environ.get("RB_LINKS")
    if not lock or not log:
        sys.exit("rb_run: RB_LOCK and RB_LOG must be set (the lock file for login checks, and the runbook's log)")
    bound = float(os.environ.get(f"RB_{a.cls.upper()}_S", BOUNDS[a.cls]))
    grace = GRACE.get(a.cls, 10)
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", SSH_ASKPASS="", SSH_ASKPASS_REQUIRE="never", DISPLAY="")
    stdin = open(a.stdin, "rb") if a.stdin else subprocess.DEVNULL
    t0 = time.time()
    cap = open(a.cap, "a", encoding="utf-8") if a.cap else None
    sof = open(a.stdout_file, "w", encoding="utf-8") if a.stdout_file else None
    try:
        proc = subprocess.Popen(cmd, stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=a.cwd, env=env,
                                start_new_session=True)
    except OSError as e:
        rc, status = (E_PROBE if a.cls == "probe" else E_FAIL), f"not started: {e}"
        append(log, f"{time.strftime('%F %T %Z')} step={a.step} class={a.cls} host={a.host} bound={bound:g}s secs=0 rc={rc} "
                    f"status=fail ({status}) cmd={shlex.join(cmd)}{' < ' + a.stdin if a.stdin else ''}\n")
        print(f"rb_run: {status}", flush=True)
        return rc
    sel = selectors.DefaultSelector()
    tails = {}
    for f in (proc.stdout, proc.stderr):
        os.set_blocking(f.fileno(), False)
        sel.register(f, selectors.EVENT_READ)
        tails[f] = ""
    buf = {proc.stdout: "", proc.stderr: ""}
    status, link, exited_at = None, None, None
    known, snap_at = {}, 0.0           # every process seen under the call {pid: pgid}, so one left by an exited parent is found
    recent = ""                        # the last 8 KB of both streams, for --host-from

    def emit(f, text, final=False):
        buf[f] += text
        lines = buf[f].split("\n")
        buf[f] = "" if final else lines.pop()
        for ln in lines:
            if final and ln == "":
                continue
            out = mask(ln)
            print(out, flush=True)
            if cap:
                cap.write(out + "\n")
                cap.flush()

    while sel.get_map():
        now = time.time()
        if now - snap_at >= 2.0 and proc.poll() is None:
            known.update(tree(proc.pid))
            snap_at = now
        if now - t0 >= bound:
            status = "timeout"
            break
        if exited_at is not None and now - exited_at > 5:
            break
        for key, _ in sel.select(timeout=0.2):
            f = key.fileobj
            try:
                data = os.read(f.fileno(), 65536)
            except BlockingIOError:
                continue
            if not data:
                sel.unregister(f)
                continue
            text = data.decode("utf-8", errors="replace")
            if sof and f is proc.stdout:
                sof.write(text)
                sof.flush()
            scan = tails[f] + text
            recent = (recent + text)[-8192:]
            if LINK.search(scan):
                m = URL.search(scan)
                link = m.group(0) if m else "login.tailscale.com"
                status = "link"
                emit(f, text)
                break
            tails[f] = scan[-512:]
            emit(f, text)
        if status == "link":
            break
        if exited_at is None and proc.poll() is not None:
            exited_at = time.time()
    if status in ("link", "timeout"):
        kill_tree(proc, 2 if status == "link" else grace, known)
    elif proc.poll() is None:
        try:
            proc.wait(timeout=max(0.5, bound - (time.time() - t0)))
        except subprocess.TimeoutExpired:
            status = "timeout"
            kill_tree(proc, grace, known)
    held_open = bool(sel.get_map()) and exited_at is not None
    left = {p: g for p, g in known.items() if same(p, g)} if (held_open or status in ("link", "timeout")) else {}
    if left:                              # a process the call left holding its output (its parent gone): never left running
        kill_tree(proc, grace, left)
    for f in (proc.stdout, proc.stderr):
        if buf[f]:
            emit(f, "", final=True)
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        kill_tree(proc, 2, known)
    secs = time.time() - t0
    crc = proc.poll()
    lhost = a.host
    if status == "link" and a.host_from:
        found = [m.group(1) for m in re.finditer(a.host_from, recent) if m.groups() and m.group(1)]
        if found:
            lhost = found[-1]
    if status == "link":
        rc = E_LINK
        append(lock, f"{time.strftime('%H:%M:%S')} {lhost} needs a check\n")
        append(links, f"{time.strftime('%F %T %Z')} {lhost} {link}\n")
        print(f"rb_run: {lhost} printed a login link: the call was killed; '{time.strftime('%H:%M:%S')} {lhost} needs a check' "
              f"appended to the lock file; the link is kept in RB_LINKS for the approval", flush=True)
    elif status == "timeout":
        rc = E_PROBE if a.cls == "probe" else E_TIMEOUT
        print(f"rb_run: no end within {bound:g} s: killed", flush=True)
    elif crc == 0:
        rc, status = 0, "ok"
    else:
        rc, status = (E_PROBE if a.cls == "probe" else E_FAIL), f"exit {crc}"
        print(f"rb_run: the command exited {crc}", flush=True)
    if cap:
        cap.close()
    if sof:
        sof.close()
    if a.cls == "probe" and status == "timeout":
        status = "no answer"
    lh = f" link_host={lhost}" if lhost != a.host else ""
    append(log, f"{time.strftime('%F %T %Z')} step={a.step} class={a.cls} host={a.host}{lh} bound={bound:g}s secs={secs:.1f} rc={rc} "
                f"child_rc={crc} status={status} what={a.what!r} cmd={shlex.join(cmd)}{' < ' + a.stdin if a.stdin else ''}\n")
    return rc


if __name__ == "__main__":
    sys.exit(main())
