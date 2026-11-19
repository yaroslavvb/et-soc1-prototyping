#!/usr/bin/env python3
"""E216 (Q227, lane kit-e216, Thu 19 Nov 2026, before any E216 datum): THE RUNBOOK'S DESK TEST, E216's desk/selftest_rb_e216.py form (with
fix-e216's cases). Every runbook step's refusals and paths that a card day can meet, run for real against stand-ins: the window rule (step 1),
THE QUIET DESK FLAG on every path (raise, lower, another's flag never overwritten or removed, THE P2 COUNT by each process's own script name)
and E216's ORDER (the flag raised only once every other card lane of ours that holds a booking has passed its launch step: a booking with no
launch marker, a marker older than its booking, an orchestrator's hold reported and not waited for), THE REST RULE (step 7 refuses before
anything reaches the card until the rest has opened), THE REBOOT GATE as step 7 and step 9 call it (the lab's fwgate in its own desk mode:
NEEDS-READ, one read EQUAL into step 7's folder, the guard; a DIFFERENT answer; CONTINUITY; a boot after the read; a missing record; a
different record), step 9's 120 s bound, the launch by step 9 and THE WAIT finding the session by its REAL script name, THE COLLECTION (a desk
test's session refused outside a desk test; COPY-BACK EXACT, E208's data checker unchanged, THE MASK of a fwgate read record that CARRIES THE
BOX'S HOME in its ledger line and then THE SCRUB both ways, the data directory and its README in a stand-in lab, the masked record read by step
13's manifest check), E, THE END OF EVERY PATH, with the round's own onelab.sh, hold.sh and book.sh (copies whose folder is a stand-in round
folder), and STEP 2 AT EVERY PIN in a scratch repository (a shared sparse clone of the lab clone with the kit as one stand-in commit and
stand-in logs, E207's form; at the lab clone's own HEAD and pins once the kit is committed there): the pass, no window, GitHub's main
elsewhere, the kit list's bytes and count, an override outside a desk test, a list changed in the working tree or in a commit, a shadowing
module, a seal unregistered then registered then marked (a later seal a comment line naming its second note), an E216 data path in a ref, a
log without its PASS line, the frozen scorer's print not the kit's, step 2 itself changed in a later commit, outside a desk test without its
one-lab span; and E after a leftover. fix-e216 (Q227, before any E216 datum) adds: Z1-Z4 (verify-e216's F7: S1 on a record that exists but
cannot be read, on a folder, on an upper-case seal unregistered and registered), G15-G18 (F8: THE CPU RULE's gate at steps 7 and 9 on a
stand-in load of 7.25 and 6.0, RB_LOAD outside a desk test, the host's own load), and G8 reading step 7's own words (nit 6). Standard library only.

    bash W/slot.sh bash W/nodev.sh /usr/bin/python3 -I -B tools/claims-v3/e216/desk/selftest_rb_e216.py <scratch> --round-w W --elf <sparsity.elf>
         --elf211 <rgm211's sparsity.elf>

The fwgate cases run where no /dev/et* exists (fwgate refuses its desk mode beside a card node); the launch, wait and collection cases run in a
bubblewrap of their own (two regular files at /dev/et0_ops and /dev/et0_mgmt, a private /run/lock, uid 0 in a private user namespace, a private
PID namespace, the host name aifoundry2), with desk/realpath_e216.py's stand-in box root. Prints one line a check and SELFTEST-RB-E216 <n> of <m>
PASS last.
SPDX-License-Identifier: Apache-2.0
"""
import datetime
import glob
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
RB = os.path.join(E, "rb")
FWG = os.path.join(REPO, "tools", "claims-v3", "fwgate")
E200A = os.path.join(REPO, "docs", "reports", "data", "2026-11-16-e200-regfile-sitting-1-aifoundry2", "session", "first",
                     "fwgate-aifoundry2-c0-20261116-081326.stderr")
CHK = "docs/reports/data/2026-11-16-e208-mmsweep-a2c0-S1"
try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("America/Los_Angeles")
except Exception:  # noqa: BLE001
    TZ = None
ROWS = []


def row(words, ok, detail=""):
    ROWS.append(bool(ok))
    print(f"{'PASS' if ok else 'FAIL'} {words}" + (f" [{detail}]" if detail != "" else ""), flush=True)


def sh(args, env, cwd=None, timeout=900):
    r = subprocess.run(args, env=env, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout + r.stderr


def epoch_today(hms):
    d = datetime.datetime.now(TZ).date()
    h, m, s = (int(x) for x in hms.split(":"))
    return int(datetime.datetime(d.year, d.month, d.day, h, m, s, tzinfo=TZ).timestamp())


class Ctx:
    def __init__(self, S, roundw, elf):
        self.S, self.roundw, self.elf = S, roundw, elf
        self.W = os.path.join(S, "W")                      # a stand-in round folder: the round's own helpers, their folder rewritten
        os.makedirs(os.path.join(self.W, "locks"))
        for n in ("onelab.sh", "hold.sh", "book.sh"):
            t = open(os.path.join(roundw, n)).read()
            lines = [(f"W={self.W}" if ln.startswith("W=") else ln) for ln in t.splitlines()]
            if sum(1 for ln in t.splitlines() if ln.startswith("W=")) != 1:
                raise SystemExit(f"{n}: not one W= line")
            open(os.path.join(self.W, n), "w").write("\n".join(lines) + "\n")
        self.bin = os.path.join(S, "bin")
        os.makedirs(self.bin)
        open(os.path.join(self.bin, "et-who"), "w").write("#!/bin/sh\n# the runbook test's stand-in et-who: nobody holds anything\n"
                                                         "[ \"${1:-}\" = --check ] && exit \"${E216_ETWHO_RC:-0}\"\n"
                                                         "[ -n \"${E216_ETWHO_LINE:-}\" ] && echo \"$E216_ETWHO_LINE\"\nexit 0\n")
        os.chmod(os.path.join(self.bin, "et-who"), 0o755)

    def env(self, out, root=None, **kw):
        e = dict(os.environ)
        e.update(PATH=self.bin + ":" + e.get("PATH", "/usr/bin:/bin"), RB_OUT=out, RB_QUIET=os.path.join(self.W, "locks", "quiet-desk-aifoundry2"),
                 RB_LANE="card-e216", RB_W=self.W, RB_DESKTEST="1")
        if root:
            e["E216_ROOT"] = root
        e.update({k: str(v) for k, v in kw.items()})
        return e


def rbs(name):
    return ["bash", os.path.join(RB, name)]


# ------------------------------------------------------------------------------------------------ the window
def t_window(c):
    out = os.path.join(c.S, "w1")
    now = int(time.time())
    rc, o = sh(rbs("s02_window_e216.sh") + [str(now - 60)], c.env(out))
    w = dict(ln.split("=", 1) for ln in open(os.path.join(out, "window.env")).read().split()) if rc == 0 else {}
    ls_ok = rc == 0 and int(w["E216_LAST_START"]) == ((now - 60 + 5400 + 59) // 60) * 60 and int(w["E216_LAST_END"]) == ((now - 60 + 12600 + 59) // 60) * 60
    row("W1 step 1: G a minute ago: window.env written, last start G + 1:30 and last end G + 3:30 rounded up", ls_ok, o.strip().splitlines()[-1])
    rc, o = sh(rbs("s02_window_e216.sh") + [str(now - 120)], c.env(out))
    row("W2 a second G in the same RB_OUT: refused (one RB_OUT a day, one G)", rc == 10 and "another window" in o)
    rc, o = sh(rbs("s02_window_e216.sh") + [str(now + 600)], c.env(os.path.join(c.S, "w3")))
    row("W3 a G in the future: refused", rc == 10 and "in the future" in o)
    rc, o = sh(rbs("s02_window_e216.sh") + [str(epoch_today("20:30:00"))], c.env(os.path.join(c.S, "w4"), RB_NOW=epoch_today("21:00:00")))
    row("W4 G at 20:30:00 (the clock at 21:00 by RB_NOW): refused, no booking that day", rc == 10 and "later than 20:29:00" in o)
    rc, o = sh(rbs("s02_window_e216.sh") + [str(epoch_today("20:29:00"))], c.env(os.path.join(c.S, "w5"), RB_NOW=epoch_today("21:00:00")))
    row("W5 G at 20:29:00: taken, the last end 23:59:00 inside the day", rc == 0 and "23:59:00" in o, o.strip().splitlines()[-2][:120])
    e = c.env(os.path.join(c.S, "w6"))
    e.pop("RB_DESKTEST")
    e["RB_NOW"] = "1"
    rc, o = sh(rbs("s02_window_e216.sh") + [str(now - 60)], e)
    row("W6 RB_NOW outside a desk test: refused", rc == 10 and "RB_NOW outside a desk test" in o)


# ------------------------------------------------------------------------------------------------ THE QUIET DESK FLAG
def t_quiet(c):
    out = os.path.join(c.S, "q")
    e = c.env(out)
    flag = e["RB_QUIET"]
    rc, o = sh(rbs("quiet_e216.sh") + ["raise", "card-e216"], e)
    row("Q1 raise: the flag up, one line '<lane> <time>'", rc == 0 and open(flag).read().startswith("card-e216 2026-"))
    rc, o = sh(rbs("quiet_e216.sh") + ["raise", "card-e216"], e)
    row("Q2 raise again: already ours (0), the line unchanged", rc == 0 and "already ours" in o)
    rc, o = sh(rbs("quiet_e216.sh") + ["check", "card-e216"], e)
    row("Q3 check: up and ours", rc == 0)
    rc, o = sh(rbs("quiet_e216.sh") + ["lower", "card-e216"], e)
    row("Q4 lower: removed", rc == 0 and not os.path.exists(flag))
    rc, o = sh(rbs("quiet_e216.sh") + ["lower", "card-e216"], e)
    row("Q5 lower again: down already (0)", rc == 0 and "down already" in o)
    open(flag, "w").write("model-session-e208-a2c0-S1-repeat 2026-11-16 23:29:21 PST\n")
    rc, o = sh(rbs("quiet_e216.sh") + ["raise", "card-e216"], e)
    rc2, o2 = sh(rbs("quiet_e216.sh") + ["lower", "card-e216"], e)
    row("Q6 another's flag: raise refused (10), lower refused (10), its line left as it was",
        rc == 10 and rc2 == 10 and open(flag).read().startswith("model-session-e208"))
    rc, o = sh(rbs("quiet_e216.sh") + ["check", "card-e216"], e)
    row("Q7 check with another's flag: 10", rc == 10)
    os.remove(flag)
    rc, o = sh(rbs("quiet_e216.sh") + ["count"], e)
    row("Q8 THE P2 COUNT with nothing of ours running: 0", rc == 0, o.strip().splitlines()[-2] if o.strip() else "")
    dev = os.path.join(c.S, "standin_host")
    shutil.copyfile("/usr/bin/sleep", dev)
    os.chmod(dev, 0o755)
    p = subprocess.Popen([dev, "30"])
    time.sleep(0.5)
    rc, o = sh(rbs("quiet_e216.sh") + ["count"], e)
    p.terminate()
    p.wait()
    row("Q9 a device-named process of ours (comm ..._host): the count 1, exit 17", rc == 17 and "1 device-named" in o)
    ses = os.path.join(c.S, "session_e216.sh")
    open(ses, "w").write("#!/usr/bin/env bash\nsleep 30\n")
    p = subprocess.Popen(["bash", ses])
    p2 = subprocess.Popen(["/usr/bin/python3", "-c", "import time; time.sleep(30)", "session_e216.sh"])
    time.sleep(0.5)
    rc, o = sh(rbs("quiet_e216.sh") + ["count"], e)
    p.terminate()
    p2.terminate()
    p.wait()
    p2.wait()
    row("Q10 a session_e216.sh script of ours counts by its own script name; a command string naming it does not", rc == 17 and
        "1 session or queue script" in o, o.strip().splitlines()[-2] if o.strip() else "")
    # THE ORDER (E216.md 6): the flag only once every other card lane of ours that holds a booking has passed its launch step
    books = os.path.join(c.S, "books.txt")
    mk_a, mk_b = os.path.join(c.S, "e215-T0-A.txt"), os.path.join(c.S, "e215-T0-B.txt")
    now = datetime.datetime.now(TZ)
    bk = (now - datetime.timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S %Z")
    eo = dict(e, RB_BOOKS=books, RB_LAUNCHED=f"card-e215a={mk_a}:card-e215b={mk_b}")
    open(books, "w").write(f"aifoundry3: card-e215a {bk}\naifoundry1: card-e215b {bk}\n(end)\n")
    rc, o = sh(rbs("quiet_e216.sh") + ["others"], eo)
    rc2, o2 = sh(rbs("quiet_e216.sh") + ["raise", "card-e216"], eo)
    row("O1 two other card lanes hold bookings and neither has its launch marker: others 17, raise refused (17), no flag",
        rc == 17 and rc2 == 17 and "WAITING FOR" in o and not os.path.exists(flag), o.strip().splitlines()[-2][:160] if o.strip() else "")
    open(mk_a, "w").write("T0=1\n")
    rc, o = sh(rbs("quiet_e216.sh") + ["others"], eo)
    row("O2 one launched (its marker written after its booking), the other not: others 17, naming card-e215b",
        rc == 17 and "card-e215a launched" in o and "card-e215b (booked" in o, o.strip().splitlines()[-2][:160] if o.strip() else "")
    open(mk_b, "w").write("T0=1\n")
    old = time.time() - 3600
    os.utime(mk_b, (old, old))
    rc, o = sh(rbs("quiet_e216.sh") + ["others"], eo)
    row("O3 the other's marker older than its booking (a marker of an earlier day): others 17", rc == 17 and "older than the booking" in o)
    os.utime(mk_b, None)
    rc, o = sh(rbs("quiet_e216.sh") + ["others"], eo)
    rc2, o2 = sh(rbs("quiet_e216.sh") + ["raise", "card-e216"], eo)
    row("O4 both launched: others 0, raise 0 (the flag up and ours)", rc == 0 and rc2 == 0 and open(flag).read().startswith("card-e216"),
        o.strip().splitlines()[-1][:160])
    sh(rbs("quiet_e216.sh") + ["lower", "card-e216"], eo)
    open(books, "w").write(f"aifoundry3: orch-hold-e215-terms {bk}\naifoundry1: card-e217x {bk}\naifoundry2: card-e216 {bk}\n(end)\n")
    rc, o = sh(rbs("quiet_e216.sh") + ["others"], eo)
    row("O5 an orchestrator's hold is REPORTED, never waited for; our own booking skipped; a card lane with no marker named: waited for (17)",
        rc == 17 and "the orchestrator's hold" in o and "aifoundry2: ours" in o and "no launch marker named" in o, o.strip().splitlines()[-2][:160])
    open(books, "w").write(f"aifoundry3: orch-hold-e215-terms {bk}\naifoundry2: card-e216 {bk}\n(end)\n")
    rc, o = sh(rbs("quiet_e216.sh") + ["others"], eo)
    row("O6 only an orchestrator's hold and our own booking: others 0", rc == 0)
    e6 = dict(eo)
    e6.pop("RB_DESKTEST")
    rc, o = sh(rbs("quiet_e216.sh") + ["others"], e6)
    row("O7 RB_BOOKS (a desk stand-in for book.sh show) outside a desk test: refused (10)", rc == 10 and "RB_BOOKS outside a desk test" in o)


# ------------------------------------------------------------------------------------------------ THE REST RULE
def t_rest(c):
    lab = os.path.join(c.S, "restlab")
    root = os.path.join(c.S, "restroot")
    now = time.time()
    day = datetime.datetime.now(TZ).strftime("%Y-%m-%d")
    d = os.path.join(lab, "docs", "reports", "data", f"{day}-x-aifoundry2", "session")
    os.makedirs(d)
    os.makedirs(os.path.join(root, "sessions"))
    rel = os.path.join(c.S, "releases.txt")
    open(rel, "w").write("# the round's record (a stand-in)\n")
    rr = [sys.executable, "-I", "-B", os.path.join(RB, "rest_rule_e216.py"), "--lab", lab, "--root", root, "--releases", rel]
    json.dump({"card": "a2c0", "t_close_ms": int((now - 1800) * 1000)}, open(os.path.join(d, "queue.json"), "w"))
    rc, o = sh(rr, os.environ)
    row("R1 a committed session of this card ended 30 minutes ago: REST NOT OPEN (17)", rc == 17 and "REST NOT OPEN" in o)
    json.dump({"card": "a2c0", "t_close_ms": int((now - 3000) * 1000)}, open(os.path.join(d, "queue.json"), "w"))
    rc, o = sh(rr, os.environ)
    row("R2 ended 50 minutes ago: REST OPEN (0)", rc == 0 and "REST OPEN since" in o)
    t = datetime.datetime.fromtimestamp(now - 600, TZ)
    open(rel, "a").write(f"a2c0-S9 aifoundry2 card 0 #10.99 {datetime.datetime.fromtimestamp(now, TZ).strftime('%Y-%m-%d %H:%M:%S')} PST "
                         f"(released; session ended {t.strftime('%H:%M:%S')}; ...) ~/claude/work/ee-x/ (on aifoundry2)\n")
    rc, o = sh(rr, os.environ)
    row("R3 a model-session release line ended 10 minutes ago (not committed yet): REST NOT OPEN", rc == 17 and "the release record" in o)
    open(rel, "w").write("a2c0-S9 aifoundry2 card 0 #10.99 a line without its times\n")
    rc, o = sh(rr, os.environ)
    row("R4 a release line that cannot be read: REST UNREADABLE (16)", rc == 16 and "REST UNREADABLE" in o)
    open(rel, "w").write("")
    s = os.path.join(root, "sessions", f"{int(now) - 60}-a2c0-E216")
    os.makedirs(s)
    open(os.path.join(s, "session.log"), "w").write("running\n")
    rc, o = sh(rr, os.environ)
    row("R5 an E216 session of the box root still running (no queue.json, no runner.rc): REST NOT OPEN (its end is now)", rc == 17 and "still running" in o)
    open(os.path.join(s, "runner.rc"), "w").write("16\n")
    old = now - 2700
    for f in os.listdir(s):
        os.utime(os.path.join(s, f), (old, old))
    os.utime(s, (old, old))
    rc, o = sh(rr, os.environ)
    row("R6 a cut E216 session (runner.rc, no queue.json), its latest write 45 minutes ago: REST OPEN", rc == 0 and "a cut session" in o)
    dry = os.path.join(lab, "docs", "reports", "data", f"{day}-y-a2c0", "session")
    os.makedirs(dry)
    json.dump({"card": "a2c0", "dry": True, "t_close_ms": int((now - 60) * 1000)}, open(os.path.join(dry, "queue.json"), "w"))
    rc, o = sh(rr, os.environ)
    row("R7 a dry session's queue.json is never a session on the card", rc == 0)
    rc, o = sh([sys.executable, "-I", "-B", os.path.join(RB, "rest_rule_e216.py"), "--lab", REPO, "--root", root], os.environ)
    row("R8 the lab's own committed data at this checkout's HEAD (yesterday's and today's folders of this card: E212's S3 re-run of Wed 18 Nov "
        "2026 among them on Thu 19 Nov): read, its latest end named, the rest OPEN",
        rc == 0 and ("e212-mmsweep2-a2c0-S3" in o or "REST OPEN since always" in o), o.strip().splitlines()[-1][:160])
    # a session of the box root that ended at a gate before its first card command (E208's runner: t_first_ms null) a minute ago
    s9 = os.path.join(root, "sessions", f"{int(now) - 90}-a2c0-E216")
    os.makedirs(s9)
    json.dump({"card": "a2c0", "dry": False, "t_first_ms": None, "t_close_ms": int((now - 60) * 1000)}, open(os.path.join(s9, "queue.json"), "w"))
    open(os.path.join(s9, "session.log"), "w").write(datetime.datetime.fromtimestamp(now - 60, TZ).strftime("%Y-%m-%d %H:%M:%S %Z")
                                                     + " session end (T0 x; 0 runs ran; 0.0 card-minutes)\n")
    open(os.path.join(s9, "runner.rc"), "w").write("16\n")
    rc, o = sh(rr, os.environ)
    row("R9 a box-root session that never reached the card (queue.json t_first_ms null) ended a minute ago: listed, not counted: REST OPEN",
        rc == 0 and "never reached the card" in o and "REST OPEN since" in o, o.strip().splitlines()[-1][:160])
    # the same session read through --tree (a tree holding the box root's folders): still not counted
    rc, o = sh(rr + ["--tree", root], os.environ)
    row("R10 the same session read again through --tree: the box root is skipped there, nothing counted twice: REST OPEN",
        rc == 0 and "REST OPEN since" in o, o.strip().splitlines()[-1][:160])
    # two release records (E208's and E212's): an aifoundry2 card 0 line in the second, ended 10 minutes ago
    rel2 = os.path.join(c.S, "releases-2.txt")
    t = datetime.datetime.fromtimestamp(now - 600, TZ)
    open(rel2, "w").write("# the second record (a stand-in)\n" + f"a2c0-S1 aifoundry2 card 0 #11.99 {datetime.datetime.fromtimestamp(now, TZ).strftime('%Y-%m-%d %H:%M:%S')} PST "
                          f"(released; session ended {t.strftime('%H:%M:%S')}; ...) ~/claude/work/ee-y/ (on aifoundry2)\n")
    rc, o = sh(rr + ["--releases", rel2], os.environ)
    row("R11 two release records (E208's and E212's): an aifoundry2 card 0 session in the second ended 10 minutes ago: REST NOT OPEN (17)",
        rc == 17 and "the release record" in o, o.strip().splitlines()[-1][:160])


# ------------------------------------------------------------------------------------------------ step 2 at every pin (a scratch repository)
S2_PATHS = ["tools/claims-v3/e216/", "tools/claims-v3/e208/", "tools/claims-v3/e206/", "tools/claims-v3/e136/", "tools/claims-v3/e211/rgm211/",
            "tools/claims-v3/e209/sched-e209.json",
            "tools/claims-v3/e213/desk/", "tools/claims-v3/fwgate/", "tools/claims-v3/kinds/", "tools/claims-v3/sealed-e216/",
            "tools/claims-v3/dmcmd_audit_v2.py", "tools/claims-v3/dmcmd_table_v2.json", "tools/matmul/mm1/",
            "docs/reports/data/2026-11-16-e208-mmsweep-a2c0-S1/"]
S2_LOGS = {"realpath-e216.txt": "DESKTEST-REALPATH-E216 0 of 0 PASS", "selftest-rb-e216.txt": "SELFTEST-RB-E216 0 of 0 PASS",
           "realbytes-e216.txt": "REALBYTES-E216 0 of 0 PASS", "desktest-build-e216.txt": "DESKTEST-BUILD-E216 0 of 0 PASS",
           "selftest-run-e216.txt": "SELFTEST-RUN-E216 0 of 0 PASS", "drypass-e216.txt": "DRY PASS a2c0 E216 (stand-in)",
           "dryaudit-e216.txt": "DRY-AUDIT-E216 0 of 0 COVERED", "dry-listing-e216.txt": "dry listing: 0 steps listed, 0 run, 0 box calls",
           "dmcmd-audit-e216.txt": "dmcmd_audit: GO (stand-in)", "selftest-post-e216.txt": "SELFTEST-POST-E216 0 of 0 PASS",
           "neverrun-desk-e216.txt": "NEVER-RUN-E216: (stand-in)"}
S2_E = "tools/claims-v3/e216"


def git_(T, *a, check=True):
    r = subprocess.run(["git", "-C", T, "-c", "user.name=E216 desk test", "-c", "user.email=desk@invalid", "-c", "core.hooksPath=/dev/null"]
                       + list(a), capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(a[:3])}: rc {r.returncode}: {r.stderr.strip()[-300:]}")
    return r.stdout.strip()


def s2_kit_commit(T, skip_log=None, branch="main", bad_print=False):
    """a stand-in kit commit: the stand-in logs, the stand-in list (every file the commit adds under E216's folder but the list and step 2),
    committed; -> the kit list's pin '<list>:<n>:<sha>:top'"""
    os.makedirs(os.path.join(T, S2_E, "logs"), exist_ok=True)
    for n in ("KIT.md", "CARD-LANE-BRIEF.md"):          # stand-ins only while the kit lane has not written them yet
        if not os.path.exists(os.path.join(T, S2_E, n)):
            open(os.path.join(T, S2_E, n), "w").write(f"# E216 {n} (a stand-in of the runbook desk test)\n")
    for n, line in S2_LOGS.items():
        open(os.path.join(T, S2_E, "logs", n), "w").write(("a stand-in log with no PASS line\n" if n == skip_log else line + "\n"))
    fp = os.path.join(T, S2_E, "logs", "forecasts-print-e216.txt")      # the kit's real print (copied with the kit's files), or a changed one
    if bad_print:
        open(fp, "a").write("a stand-in line the frozen scorer does not print\n")
    new = [f for f in git_(T, "ls-files", "--others", "--exclude-standard", "--", S2_E).splitlines()
           if f not in (f"{S2_E}/SHA256SUMS-e216-kit", f"{S2_E}/rb/s03_desk_e216.sh")]
    import hashlib
    lst = "".join(f"{hashlib.sha256(open(os.path.join(T, f), 'rb').read()).hexdigest()}  {f}\n" for f in sorted(new))
    open(os.path.join(T, S2_E, "SHA256SUMS-e216-kit"), "w").write(lst)
    git_(T, "add", "-A", "--", S2_E)
    git_(T, "commit", "-q", "-m", "E216 runbook desk test: the kit's files (stand-in kit commit)")
    return f"{S2_E}/SHA256SUMS-e216-kit:{len(new)}:{hashlib.sha256(lst.encode()).hexdigest()}:top"


def t_step2(c):
    T = os.path.join(c.S, "s2repo")
    head = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    has_kit = subprocess.run(["git", "-C", REPO, "cat-file", "-e", f"HEAD:{S2_E}/KIT.md"], capture_output=True).returncode == 0
    subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout", REPO, T], check=True, capture_output=True)
    git_(T, "sparse-checkout", "set", "--no-cone", *S2_PATHS)
    git_(T, "checkout", "-q", "-B", "main", head)
    if has_kit:
        form = f"the lab clone's HEAD {head[:12]} holds the kit: step 2 at its own pins (no stand-in)"
        kitpin = None
    else:
        files = subprocess.run(["git", "-C", REPO, "ls-files", "--others", "--exclude-standard", "--", S2_E], capture_output=True,
                               text=True).stdout.split()
        for f in files:
            if ("/logs/" in f and not f.endswith("/logs/forecasts-print-e216.txt")) or "__pycache__" in f:
                continue
            os.makedirs(os.path.dirname(os.path.join(T, f)), exist_ok=True)
            shutil.copy2(os.path.join(REPO, f), os.path.join(T, f))
        kitpin = s2_kit_commit(T)
        form = f"the kit's files untracked in the lab clone: a stand-in kit commit on its HEAD {head[:12]} (stand-in logs), the pin {kitpin.split(':')[1]} files"
    kit = git_(T, "rev-parse", "HEAD")
    print(f"step 2's scratch repository: a shared sparse clone of the lab clone ({form}); HEAD {kit[:12]}", flush=True)
    s03 = ["bash", os.path.join(T, S2_E, "rb", "s03_desk_e216.sh")]
    s02 = ["bash", os.path.join(T, S2_E, "rb", "s02_window_e216.sh")]

    def env2(out, **kw):
        e = c.env(out, RB_GITHUB=git_(T, "rev-parse", "HEAD"), RB_GITLOCK=os.path.join(c.S, "s2-gitlock"), **kw)
        if kitpin:
            e["RB_E216_KITPIN"] = kitpin
        return e

    def fresh(name, window=True):
        out = os.path.join(c.S, name)
        if window:
            sh(s02 + [str(int(time.time()) - 60)], env2(out))
        else:
            os.makedirs(out)
        return out
    out = fresh("s2-p1")
    rc, o = sh(s03, env2(out))
    row("P1 step 2 on the scratch repository: HEAD = GitHub's main, the paths clean, the registration and the kit by content, HISTORY OK, the "
        "seven lists at their pinned counts and bytes, the frozen scorer's print and self-test byte for byte (no maker run), make_box CHECK PASS, "
        "dmcmd_audit_v2 GO, the logs, the freeze line, the sealed record, no datum: STEP2 PASS", rc == 0 and "STEP2 PASS" in o and "HISTORY OK" in o, o.strip().splitlines()[-1][:150])
    rc, o = sh(s03, env2(fresh("s2-k", window=False)))
    row("P2 step 2 with no window in its RB_OUT: refused (10)", rc == 10 and "no window" in o)
    rc, o = sh(s03, dict(env2(fresh("s2-gh")), RB_GITHUB="0" * 40))
    row("P3 GitHub's main (a stand-in) differs from HEAD: refused (10), no fast-forward in a desk test", rc == 10 and "differs from HEAD" in o)
    if kitpin:
        n, h = kitpin.split(":")[1], kitpin.split(":")[2]
        rc, o = sh(s03, dict(env2(fresh("s2-kp")), RB_E216_KITPIN=kitpin.replace(h, "0" * 64)))
        row("P4 the kit list's own bytes not its pin: refused (10)", rc == 10 and "not the pin" in o, o.strip().splitlines()[-1][:150])
        rc, o = sh(s03, dict(env2(fresh("s2-kn")), RB_E216_KITPIN=kitpin.replace(f":{n}:", f":{int(n) + 1}:")))
        row("P5 the kit list's line count not its pin: refused (10)", rc == 10 and f"pinned {int(n) + 1}" in o, o.strip().splitlines()[-1][:150])
        e = env2(fresh("s2-kx"))
        for k in ("RB_DESKTEST", "RB_GITHUB"):
            e.pop(k)
        rc, o = sh(s03, e)
        row("P6 a kit pin override outside a desk test: refused (10) before anything else", rc == 10 and "outside a desk test" in o)
    v2 = os.path.join(T, "tools/matmul/mm1/v3.1/SHA256SUMS")
    keep = open(v2, "rb").read()
    open(v2, "ab").write(b"\n")
    rc, o = sh(s03, env2(fresh("s2-unclean")))
    open(v2, "wb").write(keep)
    row("P7 MM1-v3.1's list changed in the working tree: refused (10), the paths not clean", rc == 10 and "not clean" in o)
    base = git_(T, "rev-parse", "HEAD")
    reg = os.path.join(T, S2_E, "SHA256SUMS-e216-registration")
    open(reg, "a").write("0" * 64 + "  tools/claims-v3/e216/extra.txt\n")
    git_(T, "commit", "-q", "-am", "a stand-in change of the registration's list")
    rc, o = sh(s03, env2(fresh("s2-regmod")))
    git_(T, "reset", "-q", "--hard", base)
    row("P8 the registration's list changed in a commit: HISTORY FAIL (not an addition): refused (10)", rc == 10 and "HISTORY FAIL" in o
        and "not an addition" in o, o.strip().splitlines()[-1][:150])
    open(os.path.join(T, S2_E, "json.py"), "w").write("# a shadowing stand-in\n")
    git_(T, "add", "--", f"{S2_E}/json.py")
    git_(T, "commit", "-q", "-m", "a stand-in shadowing module")
    rc, o = sh(s03, env2(fresh("s2-shadow")))
    git_(T, "reset", "-q", "--hard", base)
    row("P9 a module named like a standard-library module added under tools/: HISTORY FAIL (shadowing): refused (10)", rc == 10
        and "shadowing" in o, o.strip().splitlines()[-1][:150])
    sealrec = os.path.join(c.S, "s2-sealed.txt")
    hsh = "ab" * 32
    open(sealrec, "w").write(f"E216 {hsh} #10.99 2026-11-17 07:00:00 PST (a stand-in seal)\n")
    rc, o = sh(s03, env2(fresh("s2-seal1"), RB_SEALED=sealrec))
    row("P10 the round's sealed record lists a sha256 the sealed-e216 note does not register: refused (10): do not book", rc == 10
        and "do not book" in o, o.strip().splitlines()[-1][:150])
    sd = os.path.join(T, "tools", "claims-v3", "sealed-e216")
    os.makedirs(sd)
    open(os.path.join(sd, "e216-freeze-lines.md"), "w").write(f"# E216's sealed forecasts (a stand-in note)\n\n- `{hsh}` (#10.99)\n")
    git_(T, "add", "--", "tools/claims-v3/sealed-e216")
    git_(T, "commit", "-q", "-m", "a stand-in sealed-forecast note")
    rc, o = sh(s03, env2(fresh("s2-seal2"), RB_SEALED=sealrec))
    git_(T, "reset", "-q", "--hard", base)
    row("P11 the same seal registered in tools/claims-v3/sealed-e216/e216-freeze-lines.md: STEP2 PASS, the freeze line naming it", rc == 0
        and "STEP2 PASS" in o and hsh in o, o.strip().splitlines()[-1][:150])
    open(sealrec, "w").write(f"# E216 {hsh} registered as a comment line (the record marked)\n")
    rc, o = sh(s03, env2(fresh("s2-seal3"), RB_SEALED=sealrec))
    row("P12 the record's line marked as a comment: STEP2 PASS (nothing listed to register)", rc == 0 and "STEP2 PASS" in o)
    h2 = "cd" * 32
    os.makedirs(sd, exist_ok=True)
    open(os.path.join(sd, "e216-freeze-lines.md"), "w").write(f"# E216's sealed forecasts (a stand-in note)\n\n- `{hsh}` (#10.99)\n")
    open(os.path.join(sd, "e216-freeze-lines-2.md"), "w").write(f"# E216's second sealed forecast (a stand-in note)\n\n- `{h2}` (#10.100)\n")
    git_(T, "add", "--", "tools/claims-v3/sealed-e216")
    git_(T, "commit", "-q", "-m", "stand-in sealed-forecast notes, the second a later seal")
    open(sealrec, "w").write(f"E216 {hsh} #10.99 2026-11-19 12:00:00 PST (a stand-in seal)\n# E216 {h2} #10.100 a later seal: registered in e216-freeze-lines-2.md\n")
    rc, o = sh(s03, env2(fresh("s2-seal4"), RB_SEALED=sealrec))
    git_(T, "reset", "-q", "--hard", base)
    row("P12b a later seal: its record line a COMMENT naming the second note, the first registered: STEP2 PASS (sealed 1 of 1; the comment listed "
        "with e216-freeze-lines-2.md)", rc == 0 and "STEP2 PASS" in o and "sealed 1 of 1" in o and "e216-freeze-lines-2.md" in o,
        o.strip().splitlines()[-1][:150])
    # fix-e216 (verify-e216's F7): step 0's S1 on a record that exists but cannot be read, and on a seal written in upper-case hex
    s00 = ["bash", os.path.join(T, S2_E, "rb", "s00_sealed_e216.sh")]
    zrec = os.path.join(c.S, "s0-sealed-unreadable.txt")
    open(zrec, "w").write(f"E216 {hsh} #10.99 2026-11-19 12:00:00 PST (a stand-in seal)\n")
    os.chmod(zrec, 0)
    readable = os.access(zrec, os.R_OK)
    rc, o = sh(s00, dict(os.environ, RB_SEALED=zrec))
    rc2, o2 = sh(s03, env2(fresh("s2-seal-unreadable"), RB_SEALED=zrec))
    os.chmod(zrec, 0o644)
    row("Z1 S1 with a record that exists but cannot be read (mode 000): refused (10), never 'sealed 0 of 0'; step 2's check 10 refuses too (10)",
        not readable and rc == 10 and "cannot be read" in o and "sealed 0 of 0" not in o and rc2 == 10 and "do not book" in o2,
        o.strip().splitlines()[-1][:150])
    zdir = os.path.join(c.S, "s0-sealed-a-folder")
    os.makedirs(zdir)
    rc, o = sh(s00, dict(os.environ, RB_SEALED=zdir))
    row("Z2 S1 with a folder where the record should be: refused (10)", rc == 10 and "cannot be read" in o, o.strip().splitlines()[-1][:150])
    open(zrec, "w").write(f"E216 {hsh.upper()} #10.99 2026-11-19 12:00:00 PST (a stand-in seal in upper-case hex)\n")
    rc, o = sh(s00, dict(os.environ, RB_SEALED=zrec))
    row("Z3 S1 with a seal in upper-case hex that no note registers: refused (10), sealed 0 of 1: do not book", rc == 10 and "NOT REGISTERED" in o
        and "sealed 0 of 1" in o, o.strip().splitlines()[-1][:150])
    os.makedirs(sd, exist_ok=True)
    open(os.path.join(sd, "e216-freeze-lines.md"), "w").write(f"# E216's sealed forecasts (a stand-in note)\n\n- `{hsh}` (#10.99)\n")
    rc, o = sh(s00, dict(os.environ, RB_SEALED=zrec))
    rc2, o2 = sh(s00, dict(os.environ, RB_SEALED=os.path.join(c.S, "s0-no-such-record.txt")))
    shutil.rmtree(sd)
    row("Z4 the same upper-case seal registered in lower case: sealed 1 of 1 (0); a record path that does not exist: sealed 0 of 0 (0)",
        rc == 0 and "sealed 1 of 1" in o and rc2 == 0 and "sealed 0 of 0" in o2, o.strip().splitlines()[-1][:150])
    git_(T, "checkout", "-q", "-b", "side-e216-data")
    dd = os.path.join(T, "docs", "reports", "data", "2026-11-18-e216-blind-matmul-aifoundry2")
    os.makedirs(dd)
    open(os.path.join(dd, "README.md"), "w").write("a stand-in data path\n")
    git_(T, "add", "-f", "--sparse", "--", "docs/reports/data/2026-11-18-e216-blind-matmul-aifoundry2/README.md")
    git_(T, "commit", "-q", "-m", "a stand-in E216 datum on a side branch")
    git_(T, "checkout", "-q", "main")
    rc, o = sh(s03, env2(fresh("s2-data")))
    git_(T, "branch", "-q", "-D", "side-e216-data")
    row("P13 an E216 data path in a ref (a side branch): refused (10): E216 has run already", rc == 10 and "E216 has run already" in o,
        o.strip().splitlines()[-1][:150])
    # fix-e209 (verify-e209's finding 4): step 2 itself changed in a later commit (an innocent edit that keeps every check) fails its
    # history check commit by commit, where the net diff alone read it as an addition
    s03p = os.path.join(T, S2_E, "rb", "s03_desk_e216.sh")
    open(s03p, "a").write("# a stand-in later edit of step 2 itself (the runbook desk test)\n")
    git_(T, "commit", "-q", "-am", "a stand-in later change of step 2")
    rc, o = sh(s03, env2(fresh("s2-s03mod")))
    git_(T, "reset", "-q", "--hard", base)
    row("P15 step 2 itself changed in a later commit: HISTORY FAIL commit by commit (not an addition in a commit): refused (10)",
        rc == 10 and "HISTORY FAIL" in o and "commit by commit" in o and "s03_desk_e216.sh" in o, o.strip().splitlines()[-1][:150])
    # fix-e209 (verify-e209's finding 8): outside a desk test, step 2 refuses unless the lane is in its one-lab desk span, before it reads
    # GitHub (the pass side runs at the card lane's own step 2: a desk test never reads GitHub)
    e = env2(fresh("s2-span"))
    for k in ("RB_DESKTEST", "RB_GITHUB", "RB_E216_KITPIN"):
        e.pop(k, None)
    rc, o = sh(s03, e)
    row("P16 outside a desk test with no one-lab desk span: refused (10) before GitHub is read", rc == 10 and "not in its desk span" in o
        and "2. HEAD" not in o, o.strip().splitlines()[-1][:150])
    if kitpin:
        git_(T, "checkout", "-q", "-B", "nolog", head)
        for f in subprocess.run(["git", "-C", REPO, "ls-files", "--others", "--exclude-standard", "--", S2_E], capture_output=True,
                                text=True).stdout.split():
            if ("/logs/" in f and not f.endswith("/logs/forecasts-print-e216.txt")) or "__pycache__" in f:
                continue
            os.makedirs(os.path.dirname(os.path.join(T, f)), exist_ok=True)
            shutil.copy2(os.path.join(REPO, f), os.path.join(T, f))
        pin2 = s2_kit_commit(T, skip_log="dryaudit-e216.txt")
        rc, o = sh(s03, dict(env2(fresh("s2-nolog")), RB_E216_KITPIN=pin2))
        git_(T, "checkout", "-q", "main")
        row("P14 a kit whose DRY audit log has no PASS line: refused (10) at the logs", rc == 10 and "dryaudit-e216.txt" in o, o.strip().splitlines()[-1][:150])
        git_(T, "checkout", "-q", "-B", "badprint", head)
        for f in subprocess.run(["git", "-C", REPO, "ls-files", "--others", "--exclude-standard", "--", S2_E], capture_output=True,
                                text=True).stdout.split():
            if ("/logs/" in f and not f.endswith("/logs/forecasts-print-e216.txt")) or "__pycache__" in f:
                continue
            os.makedirs(os.path.dirname(os.path.join(T, f)), exist_ok=True)
            shutil.copy2(os.path.join(REPO, f), os.path.join(T, f))
        pin3 = s2_kit_commit(T, bad_print=True)
        rc, o = sh(s03, dict(env2(fresh("s2-badprint")), RB_E216_KITPIN=pin3))
        git_(T, "checkout", "-q", "main")
        row("P17 a kit whose committed forecasts print differs from the frozen scorer's print: refused (10) at check 6 (step 2 runs no maker)",
            rc == 10 and "forecasts-print-e216.txt" in o, o.strip().splitlines()[-1][:150])
    shutil.rmtree(T)


# ------------------------------------------------------------------------------------------------ step 7 and the reboot gate
def gate_setup(c, name, boot_shift=0):
    out = os.path.join(c.S, name)
    root = os.path.join(c.S, name + "-root")
    os.makedirs(os.path.join(root, "build"))
    os.makedirs(os.path.join(root, "fwgate", "records"))
    shutil.copyfile(os.path.join(FWG, "fwgate.py"), os.path.join(root, "fwgate", "fwgate.py"))
    for f in glob.glob(os.path.join(FWG, "records", "*.json")):
        shutil.copyfile(f, os.path.join(root, "fwgate", "records", os.path.basename(f)))
    day = datetime.datetime.now(TZ).strftime("%Y-%m-%d")
    json.dump({"day": day, "verdict": "BUILT", "box": "aifoundry2", "kernel_sha256": "aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0"},
              open(os.path.join(root, "build", "BUILD-mms.json"), "w"))
    json.dump({"day": day, "verdict": "BUILT", "box": "aifoundry2", "family_g_gate": "GATE OK: a desk test's record"},
              open(os.path.join(root, "build", "BUILD-e216.json"), "w"))
    now = int(time.time())
    sh(rbs("s02_window_e216.sh") + [str(now - 60)], c.env(out))
    open(os.path.join(out, "dry.out"), "w").write("DRY PASS a2c0 E216 (runner rc 0; 0 runs not clean)\n")
    open(os.path.join(out, "e216-neverrun.txt"), "w").write(f"{now - 30} NEVER-RUN-E216: 46 of 46 points never ran on aifoundry2 card 0 (a stand-in)\n")
    open(os.path.join(c.W, "locks", "quiet-desk-aifoundry2"), "w").write("card-e216 desk test\n")
    fw = os.path.join(c.S, name + "-fw")
    os.makedirs(os.path.join(fw, "lock"))
    open(os.path.join(fw, "lock", "etsoc-shire0.lock"), "w").close()
    os.makedirs(os.path.join(fw, "ledger"))
    rel = os.path.join(c.S, name + "-releases.txt")
    open(rel, "w").write("# none\n")
    bt = int([ln.split()[1] for ln in open("/proc/stat") if ln.startswith("btime ")][0]) + boot_shift
    # fix-e216: RB_LOAD stands in for the host's 1-minute load (0.5) at THE CPU RULE's gate, so no case here hangs on the box's own load
    env = c.env(out, root, RB_RELEASES=rel, RB_LOAD="0.5", FWGATE_DESK_TEST="1", FWGATE_CLI=os.path.join(FWG, "tests", "fwcli-standin"),
                FWGATE_ETWHO=os.path.join(FWG, "tests", "etwho-standin"), FWGATE_LOCKDIR=os.path.join(fw, "lock"),
                FWGATE_LEDGER_DIR=os.path.join(fw, "ledger"), FWGATE_HOSTNAME="aifoundry2", FWGATE_BOOT_EPOCH=bt, FWGATE_BOOT_ID="desk-boot-e216",
                FWGATE_STANDIN_LOG=os.path.join(fw, "cli.log"), FWGATE_STANDIN_OUT=E200A, FWGATE_STANDIN_LOCKS=os.path.join(fw, "lock", "etsoc-shire0.lock"))
    return out, root, fw, env


def cli_calls(fw):
    p = os.path.join(fw, "cli.log")
    return len(open(p).read().splitlines()) if os.path.exists(p) else 0


def t_gate(c):
    out, root, fw, env = gate_setup(c, "g1")
    rc, o = sh(rbs("s09_reads_e216.sh"), env)
    first = dict(x.split("=", 1) for x in open(os.path.join(out, "e216-first.txt")).read().split()) if rc == 0 else {}
    recs = glob.glob(os.path.join(root, first.get("FIRSTDIR", "x"), "fwgate-*.json"))
    verd = json.load(open(recs[0])).get("verdict") if recs else None
    row("G1 step 7: the rest open, fwgate's look NEEDS-READ, ONE read (the stand-in CLI called once) EQUAL into step 7's folder, the guard ok",
        rc == 0 and first.get("FWGATE") == "read" and cli_calls(fw) == 1 and verd == "EQUAL", o.strip().splitlines()[-1][:160])
    rc, o = sh(rbs("s09_reads_e216.sh"), env)
    row("G2 step 7 again within 120 s: the stamp kept, nothing sent (still one CLI call)", rc == 0 and "the stamp kept" in o and cli_calls(fw) == 1)
    rc, o = sh(rbs("s11_session_e216.sh"), dict(env, RB_FWGATE=""))
    # s11 goes as far as start_e216.sh (no box root sync here: it refuses there, after the guard and the rest passed)
    row("G3 step 9 with that stamp: the rest and fwgate's guard pass (start_e216.sh then refuses in this bare root: no src/)",
        "fwgate guard: rc 0" in o and "start_e216.sh refused" in o, o.strip().splitlines()[-1][:160])
    env_boot = dict(env, FWGATE_BOOT_EPOCH=str(int(time.time()) - 5), FWGATE_BOOT_ID="desk-boot-e216-later")
    rc, o = sh(rbs("s11_session_e216.sh"), env_boot)
    row("G4 a boot after the read (the box rebooted between step 7 and step 9): step 9's guard IDENTITY-STOP (16), nothing launched",
        rc == 16 and "IDENTITY-STOP" in o)
    for f in recs:
        os.rename(f, f + ".moved-by-test")
    rc, o = sh(rbs("s11_session_e216.sh"), env)
    row("G5 the record missing from step 7's folder: step 9's guard IDENTITY-STOP (16)", rc == 16 and "IDENTITY-STOP" in o)
    for f in recs:
        r = json.load(open(f + ".moved-by-test"))
        r["verdict"] = "DIFFERENT"
        json.dump(r, open(f, "w"))
    rc, o = sh(rbs("s11_session_e216.sh"), env)
    row("G6 a record of a read that did not end EQUAL in step 7's folder: step 9's guard IDENTITY-STOP (16)", rc == 16 and "IDENTITY-STOP" in o)
    st = dict(x.split("=", 1) for x in open(os.path.join(out, "e216-first.txt")).read().split())
    open(os.path.join(out, "e216-first.txt"), "w").write(f"FIRST={int(st['FIRST']) - 200} FIRSTDIR={st['FIRSTDIR']} FWGATE=read\n")
    rc, o = sh(rbs("s11_session_e216.sh"), env)
    row("G7 step 9 more than 120 s after the stamp: refused (10), step 7 again", rc == 10 and "more than 120 s" in o)
    # a DIFFERENT answer at the read
    out, root, fw, env = gate_setup(c, "g8")
    bad = os.path.join(c.S, "answer-different.txt")
    a = open(E200A).read()
    mm = "Master Minion Firmware versions: Major: 0 Minor: 25 Revision: 1"
    assert mm in a, "E200's committed answer no longer holds the Master Minion line the test changes"
    open(bad, "w").write(a.replace(mm, mm[:-1] + "2", 1))    # the card answers 0.25.2 where the record says 0.25.1
    rc, o = sh(rbs("s09_reads_e216.sh"), dict(env, FWGATE_STANDIN_OUT=bad))
    rc2, o2 = sh(rbs("s09_reads_e216.sh"), dict(env, FWGATE_STANDIN_OUT=E200A))
    # fix-e216 (verify-e216's nit 6): G8 also reads step 7's own words (THE REBOOT GATE's stop, never reaching fwgate's guard), so a stop at
    # the guard instead (verify-e216's mutation M5: a read not EQUAL taken as a read) would show
    row("G8 a DIFFERENT answer: step 7 stops (16) by THE REBOOT GATE's own words, no stamp; a later step 7 on this boot reads STOPPED (16) and "
        "sends nothing more",
        rc == 16 and "THE REBOOT GATE" in o and "fwgate guard:" not in o and not os.path.exists(os.path.join(out, "e216-first.txt"))
        and rc2 == 16 and cli_calls(fw) == 1, o.strip().splitlines()[-1][:140])
    # CONTINUITY: a boot before the newest committed record
    out, root, fw, env = gate_setup(c, "g9")
    env["FWGATE_BOOT_EPOCH"] = str(int(datetime.datetime(2026, 10, 27, 10, 0, 0, tzinfo=TZ).timestamp()))
    rc, o = sh(rbs("s09_reads_e216.sh"), env)
    first = dict(x.split("=", 1) for x in open(os.path.join(out, "e216-first.txt")).read().split()) if rc == 0 else {}
    row("G9 CONTINUITY (a boot before the newest committed record): nothing sent, look.txt in step 7's folder, the guard ok",
        rc == 0 and first.get("FWGATE") == "continuity" and cli_calls(fw) == 0 and os.path.exists(os.path.join(root, first.get("FIRSTDIR", "x"), "look.txt")))
    # the rest not open: step 7 refuses before the reboot gate's read (nothing reaches the card)
    out, root, fw, env = gate_setup(c, "g10")
    t = datetime.datetime.fromtimestamp(time.time() - 300, TZ)
    open(env["RB_RELEASES"], "w").write(f"a2c0-S9 aifoundry2 card 0 #10.99 {datetime.datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')} PST "
                                        f"(session ended {t.strftime('%H:%M:%S')}) ~/x (on aifoundry2)\n")
    rc, o = sh(rbs("s09_reads_e216.sh"), env)
    row("G10 STEP 7 BEFORE THE REST: refused (17) before any card command: no fwgate call, no step 7 folder",
        rc == 17 and "REST NOT OPEN" in o and cli_calls(fw) == 0 and not os.path.exists(os.path.join(root, "first")))
    out, root, fw, env = gate_setup(c, "g11")
    os.remove(os.path.join(out, "e216-neverrun.txt"))
    rc, o = sh(rbs("s09_reads_e216.sh"), env)
    open(os.path.join(out, "e216-neverrun.txt"), "w").write(f"{int(time.time()) - 1900} NEVER-RUN-E216: 46 of 46 (a stand-in)\n")
    rc2, o2 = sh(rbs("s09_reads_e216.sh"), env)
    row("G11 step 7 without step 6n, or with a 6n over 30 minutes old: refused (10), nothing sent", rc == 10 and rc2 == 10 and cli_calls(fw) == 0)
    rc, o = sh(rbs("s09_reads_e216.sh"), dict(env, RB_NOW=str(int(time.time()) + 6 * 3600)))
    row("G12 step 7 past the window's last start: refused (10)", rc == 10 and "past the last start" in o)
    s = os.path.join(root, "sessions", f"{int(time.time()) - 600}-a2c0-E216")
    os.makedirs(s)
    open(os.path.join(s, "session.log"), "w").write("2026-11-17 00:00:00 PST config start: {}\n")
    open(os.path.join(out, "e216-neverrun.txt"), "w").write(f"{int(time.time())} NEVER-RUN-E216: 46 of 46 (a stand-in)\n")
    rc, o = sh(rbs("s09_reads_e216.sh"), env)
    row("G13 an E216 session of today that reached the card already: step 7 refused (one session a day)", rc == 10 and "one session a day" in o)
    os.remove(os.path.join(c.W, "locks", "quiet-desk-aifoundry2"))
    rc, o = sh(rbs("s09_reads_e216.sh"), env)
    row("G14 step 7 without THE QUIET DESK FLAG: refused (10)", rc == 10 and "not up" in o)
    # fix-e216 (verify-e216's F8): THE CPU RULE's launch gate at steps 7 and 9 (17 while the 1-minute load is 6 or more; nothing sent)
    out, root, fw, env = gate_setup(c, "g15")
    rc, o = sh(rbs("s09_reads_e216.sh"), dict(env, RB_LOAD="7.25"))
    row("G15 step 7 with the host's 1-minute load at 7.25 (a stand-in): refused (17) by THE CPU RULE before any card command: no fwgate "
        "call, no step 7 folder, no stamp", rc == 17 and "THE CPU RULE" in o and cli_calls(fw) == 0 and not os.path.exists(os.path.join(root, "first"))
        and not os.path.exists(os.path.join(out, "e216-first.txt")), o.strip().splitlines()[-1][:160])
    rc, o = sh(rbs("s09_reads_e216.sh"), env)
    rc2, o2 = sh(rbs("s11_session_e216.sh"), dict(env, RB_FWGATE="", RB_LOAD="6.0"))
    rc3, o3 = sh(rbs("s11_session_e216.sh"), dict(env, RB_FWGATE=""))
    row("G16 step 9 with the load at 6.0: refused (17) by THE CPU RULE after the rest and the guard, nothing launched; at 0.5 the same call "
        "reaches start_e216.sh (which refuses in this bare root, as G3)",
        rc == 0 and rc2 == 17 and "THE CPU RULE" in o2 and "fwgate guard: rc 0" in o2 and "start_e216.sh" not in o2
        and "fwgate guard: rc 0" in o3 and "start_e216.sh refused" in o3, o2.strip().splitlines()[-1][:160])
    e = dict(env)
    e.pop("RB_DESKTEST")
    rc, o = sh(rbs("s09_reads_e216.sh"), e)
    row("G17 RB_LOAD (the desk stand-in) outside a desk test: refused (10)", rc == 10 and "RB_LOAD outside a desk test" in o)
    out, root, fw, env = gate_setup(c, "g18")
    e = dict(env)
    e.pop("RB_LOAD")
    l0 = float(open("/proc/loadavg").read().split()[0])
    rc, o = sh(rbs("s09_reads_e216.sh"), e)
    l1 = float(open("/proc/loadavg").read().split()[0])
    import re
    m = re.search(r"THE CPU RULE: the host's 1-minute load ([0-9.]+) at step 7", o)
    x = float(m.group(1)) if m else None
    row("G18 the gate on the host's own load (no stand-in): it prints /proc/loadavg's first field and passes under 6 (else 17)",
        x is not None and min(l0, l1) - 0.5 <= x <= max(l0, l1) + 0.5 and ((x < 6 and rc == 0) or (x >= 6 and rc == 17)),
        f"load read {x}, around it {l0} / {l1}; rc {rc}")


# ------------------------------------------------------------------------------------------------ launch, wait, collect, E (in a sandbox)
def t_sandbox(c):
    d = os.path.join(c.S, "sb")
    os.makedirs(d)
    for n in ("et0_ops", "et0_mgmt"):
        open(os.path.join(d, n), "w").close()
    args = ["/usr/bin/bwrap", "--dev-bind", "/", "/", "--dev", "/dev", "--tmpfs", "/run/lock"]
    for n in ("et0_ops", "et0_mgmt"):
        args += ["--bind", os.path.join(d, n), "/dev/" + n]
    args += ["--unshare-user", "--uid", "0", "--gid", "0", "--unshare-pid", "--proc", "/proc", "--unshare-uts", "--hostname", "aifoundry2",
             "--die-with-parent", "--", "/usr/bin/python3", "-I", "-B", os.path.abspath(__file__), "--inner", c.S, c.roundw, c.elf, c.elf211]
    r = subprocess.run(args, capture_output=True, text=True, timeout=1800)
    sys.stdout.write(r.stdout)
    for ln in r.stdout.splitlines():
        if ln.startswith("PASS ") or ln.startswith("FAIL "):
            ROWS.append(ln.startswith("PASS "))
    if r.returncode != 0 and not r.stdout.strip():
        row("the sandbox part ran", False, r.stderr[-800:])


def inner(S, roundw, elf, elf211):
    sys.path.insert(0, HERE)
    import realpath_e216 as RP
    c = Ctx.__new__(Ctx)
    c.S, c.roundw, c.elf, c.elf211 = S, roundw, elf, elf211
    c.W = os.path.join(S, "W")
    c.bin = os.path.join(S, "bin")
    base = RP.prepare(os.path.join(S, "sbx"), elf, elf211)
    root = os.path.join(base, "root")
    out = os.path.join(S, "sbx-out")
    os.makedirs(out)
    open("/run/lock/etsoc-shire0.lock", "a").close()
    # the stand-in box tools for the session (desk/standin_e216.py), as in the real-path test
    env = c.env(out, root, RB_RELEASES=os.path.join(S, "sbx-rel.txt"), USER="root", MMS_FAKE_CARD="a2c0", MMS_FAKE_DIR="/dev", MMS_FAKE_SCALE="1",
                E216_SI=os.path.join(HERE, "standin_e216.py"), E216_SI_SRC=os.path.join(root, "src"), E216_DESKTEST="1",
                RB_FWGATE=os.path.join(S, "sbx-fwgate-standin"))
    env["PATH"] = os.path.join(base, "bin") + ":" + env["PATH"]
    open(env["RB_RELEASES"], "w").write("# none\n")
    open(env["RB_FWGATE"], "w").write("#!/bin/sh\n# the runbook test's stand-in for fwgate.py's guard inside the card sandbox (fwgate refuses its desk "
                                      "mode beside a node file): it says what fwgate says on an EQUAL read of this boot\n"
                                      "echo \"identity: aifoundry2 card 0 booted (desk test), before the firmware read of today: ok\"\nexit 0\n")
    os.chmod(env["RB_FWGATE"], 0o755)
    now = int(time.time())
    sh(rbs("s02_window_e216.sh") + [str(now - 60)], env)
    open(os.path.join(c.W, "locks", "quiet-desk-aifoundry2"), "w").write("card-e216 desk test\n")
    first = now - 5
    fd = os.path.join(root, "first", str(first))
    os.makedirs(fd)
    bt = int([ln.split()[1] for ln in open("/proc/stat") if ln.startswith("btime ")][0])
    bid = open("/proc/sys/kernel/random/boot_id").read().strip()
    json.dump({"schema": "fwgate-read/1", "box": "aifoundry2", "card": 0, "verdict": "EQUAL", "boot_epoch": bt, "boot_id": bid, "read_epoch": first,
               "desk_test": True}, open(os.path.join(fd, "fwgate-aifoundry2-c0-desktest.json"), "w"))
    open(os.path.join(out, "e216-first.txt"), "w").write(f"FIRST={first} FIRSTDIR=first/{first} FWGATE=read\n")
    # a holder of the card's lock for 25 s: the session waits for its lock (one retry after 15 s) so the wait sees it running, then it ends rc 16
    hp = os.path.join(S, "sbx-holder.py")
    open(hp, "w").write(RP.HOLDER)
    h = subprocess.Popen(["/usr/bin/python3", "-I", "-B", hp, "/run/lock/etsoc-shire0.lock", os.path.join(S, "sbx-holder.flag"), "25"])
    while not os.path.exists(os.path.join(S, "sbx-holder.flag")):
        time.sleep(0.05)
    rc, o = sh(rbs("s11_session_e216.sh"), dict(env, RB_LOAD="0.5"))   # fix-e216: THE CPU RULE gate read on a stand-in load
    sid = open(os.path.join(out, "e216-session.txt")).read().strip().split("=", 1)[1] if os.path.exists(os.path.join(out, "e216-session.txt")) else None
    row("S1 step 9: the rest, the guard (its stand-in), THE P2 COUNT 0, then start_e216.sh: STARTED DESKTEST, the session id written",
        rc == 0 and sid is not None and "STARTED DESKTEST" in o, o.strip().splitlines()[-1][:160])
    rc, o = sh(rbs("s20_wait_e216.sh"), env)
    row("S2 step 10: the session found RUNNING by its real script name (session_e216.sh: 1), then ENDED: runner rc 16 (the card's lock held: "
        "no device opened), exit 16", rc == 16 and "by their own name: 1" in o and "runner rc 16" in o, o.strip().splitlines()[-1][:160])
    h.wait()
    e2 = dict(env)
    e2.pop("RB_DESKTEST")
    e2.pop("RB_FWGATE")
    rc, o = sh(rbs("s22_collect_e216.sh"), e2)
    row("S3b step 11 outside a desk test with no one-lab collect span: refused (10), nothing copied (E209's fix-e209, verify-e209's finding 8)",
        rc == 10 and "not in its collect span" in o and not os.path.exists(os.path.join(out, "copy")), o.strip().splitlines()[-1][:160])
    os.makedirs(os.path.join(c.W, "locks", "onelab"), exist_ok=True)
    open(os.path.join(c.W, "locks", "onelab", "collect-card-e216"), "w").write("card-e216 desk test\n")
    rc, o = sh(rbs("s22_collect_e216.sh"), e2)
    row("S3 step 11 outside a desk test, in its collect span: a desk test's session is refused (10), nothing copied", rc == 10 and "DESKTEST" in o
        and not os.path.exists(os.path.join(out, "copy")))
    # a whole short session for the collection: the operator's STOP after the smoke's first run
    lab = os.path.join(S, "sbx-lab")
    os.makedirs(os.path.join(lab, CHK))
    for n in ("check_session_e208.py", "SHA256SUMS"):
        shutil.copyfile(os.path.join(REPO, CHK, n), os.path.join(lab, CHK, n))
    shutil.copyfile(os.path.join(E, "DATA-README-FORM-e216.md"), os.path.join(S, "form-check.md"))
    out2 = os.path.join(S, "sbx-out2")
    os.makedirs(out2)
    env2 = dict(env, RB_OUT=out2, RB_DATA_LAB=lab)
    shutil.copyfile(os.path.join(out, "window.env"), os.path.join(out2, "window.env"))
    first = int(time.time()) - 3
    fd = os.path.join(root, "first", str(first))
    os.makedirs(fd)
    import pwd
    home = pwd.getpwuid(os.getuid()).pw_dir
    rec_name = "fwgate-aifoundry2-c0-" + datetime.datetime.fromtimestamp(first, TZ).strftime("%Y%m%d-%H%M%S") + ".json"
    json.dump({"schema": "fwgate-read/1", "box": "aifoundry2", "card": 0, "verdict": "EQUAL", "boot_epoch": bt, "boot_id": bid, "read_epoch": first,
               "desk_test": True, "ledger": f"{home}/.local/state/fwgate/aifoundry2-c0.jsonl"},
              open(os.path.join(fd, rec_name), "w"), indent=1)
    open(os.path.join(out2, "e216-first.txt"), "w").write(f"FIRST={first} FIRSTDIR=first/{first} FWGATE=read\n")
    # the first session of today did not reach the card (its gate refused before the config read): a second may start
    rc, o = sh(rbs("s11_session_e216.sh"), dict(env2, RB_LOAD="0.5"))   # fix-e216: THE CPU RULE gate read on a stand-in load
    sid2 = open(os.path.join(out2, "e216-session.txt")).read().strip().split("=", 1)[1] if os.path.exists(os.path.join(out2, "e216-session.txt")) else ""
    row("S4 a second step 9 the same day after a session that never reached the card: STARTED", rc == 0 and sid2, o.strip().splitlines()[-1][:120])
    t = time.time()
    while time.time() - t < 400:
        log = os.path.join(root, "sessions", sid2, "session.log")
        if os.path.exists(log) and "run 002-" in open(log).read():
            sh(["bash", os.path.join(root, "src", "stop_mms.sh"), "a2c0", sid2], env2, cwd=root)
            break
        time.sleep(0.5)
    for _ in range(40):
        rc, o = sh(rbs("s20_wait_e216.sh"), env2)
        if rc != 17:
            break
    row("S5 step 10 on a session the operator's STOP ended after A1: ENDED, runner rc 0", rc == 0 and "runner rc 0" in o, o.strip().splitlines()[-1][:160])
    open(os.path.join(root, "sessions", sid2, "runner.out"), "a").write(f"a planted home path: /home/{os.environ.get('SUDO_USER', 'someone')}/x\n")
    rc, o = sh(rbs("s22_collect_e216.sh"), env2)
    row("S6 THE SCRUB: a home path planted in runner.out (outside the manifest): the collection stops (16) before anything is written in the lab",
        rc == 16 and "THE SCRUB found" in o and not glob.glob(os.path.join(lab, "docs", "reports", "data", "*e216*")))
    t2 = open(os.path.join(root, "sessions", sid2, "runner.out")).read().replace(
        f"a planted home path: /home/{os.environ.get('SUDO_USER', 'someone')}/x\n", "")
    open(os.path.join(root, "sessions", sid2, "runner.out"), "w").write(t2)
    shutil.rmtree(os.path.join(out2, "copy"))
    rc, o = sh(rbs("s22_collect_e216.sh"), env2)
    dd = glob.glob(os.path.join(lab, "docs", "reports", "data", "*-e216-blind-matmul-aifoundry2"))
    ok_sums = False
    readme = ""
    if dd:
        ok_sums = subprocess.run(["sha256sum", "-c", "--quiet", "SHA256SUMS"], cwd=dd[0], capture_output=True).returncode == 0
        readme = open(os.path.join(dd[0], "README.md")).read()
    row("S7 step 11 in a desk test: COPY-BACK EXACT, E208's checker C0-C8, THE SCRUB clean, the data directory with session/, checks, both "
        "build records, README (no placeholder left) and SHA256SUMS (every line OK); THE QUIET DESK FLAG lowered after the copy-back",
        rc == 0 and bool(dd) and ok_sums and "{{" not in readme and "COPY-BACK EXACT" in o and "C0_src" in o
        and os.path.exists(os.path.join(dd[0], "build-record-e216-aifoundry2.json"))
        and not os.path.exists(os.path.join(c.W, "locks", "quiet-desk-aifoundry2")), o.strip().splitlines()[-1][:160])
    if dd:
        recs = glob.glob(os.path.join(dd[0], "session", "first", "fwgate-aifoundry2-c0-*.json"))
        rb = open(recs[0], "rb").read() if recs else b""
        raw = glob.glob(os.path.join(root, "sessions", sid2, "first", "fwgate-aifoundry2-c0-*.json"))
        rawb = open(raw[0], "rb").read() if raw else b""
        row("S8 THE MASK on a read record that CARRIES THE BOX'S HOME in its ledger line: the committed copy reads '~' there and nothing else "
            "differs; the raw record keeps the home in the box root; THE SCRUB passed",
            b'"ledger": "~/.local/state/fwgate/aifoundry2-c0.jsonl"' in rb and home.encode() not in rb and home.encode() in rawb
            and rb.replace(b"~/.local", home.encode() + b"/.local") == rawb and "THE MASK" in o, (recs[0].split("/")[-1] if recs else "no record"))
        rc9, o9 = sh([sys.executable, "-I", "-B", os.path.join(E, "collect_e216.py"), "--manifest-check", os.path.join(dd[0], "session")], env2)
        row("S9 step 13's manifest read of the committed session: every line OK, the masked record by THE MASK alone (1)",
            rc9 == 0 and "(1 by THE MASK" in o9, o9.strip().splitlines()[-1][:160])
        open(os.path.join(dd[0], "session", "session.log"), "a").write("a changed line\n")
        rc9, o9 = sh([sys.executable, "-I", "-B", os.path.join(E, "collect_e216.py"), "--manifest-check", os.path.join(dd[0], "session")], env2)
        row("S10 the same read with another file changed: refused (10)", rc9 == 10 and "differs" in o9, o9.strip().splitlines()[-1][:160])
    # E, the end of every path, with the round's own helpers on a stand-in round folder
    W = c.W
    e = dict(env2)
    def helper(n, *a):
        return subprocess.run(["bash", os.path.join(W, n)] + list(a), capture_output=True, text=True).stdout
    helper("book.sh", "take", "aifoundry2", "card-e216")
    helper("hold.sh", "add", "card-e216")
    helper("hold.sh", "add", "card-e215a")
    helper("onelab.sh", "collect", "card-e216")
    open(os.path.join(W, "locks", "quiet-desk-aifoundry2"), "w").write("card-e216 a stop path\n")
    rc, o = sh(rbs("end_e216.sh"), e)
    st = helper("onelab.sh", "show") + helper("hold.sh", "list") + helper("book.sh", "show")
    row("E1 a stop path after the collect span began: the flag lowered, onelab uncollect, the hold line removed (another lane's kept), the booking "
        "released", rc == 0 and "collect-card-e216" not in st and "card-e215a" in st and "card-e216" not in st
        and not os.path.exists(os.path.join(W, "locks", "quiet-desk-aifoundry2")), o.strip().splitlines()[-1][:200])
    helper("book.sh", "take", "aifoundry2", "card-e216")
    helper("onelab.sh", "desk", "card-e216")
    rc, o = sh(rbs("end_e216.sh"), e)
    st = helper("onelab.sh", "show") + helper("book.sh", "show")
    row("E2 a stop path inside the desk span (steps 0-2): onelab undesk and the booking released; no flag of ours to lower",
        rc == 0 and "desk-card-e216" not in st and "card-e216" not in st, o.strip().splitlines()[-1][:200])
    open(os.path.join(W, "locks", "quiet-desk-aifoundry2"), "w").write("model-session-x another's\n")
    rc, o = sh(rbs("end_e216.sh"), e)
    row("E3 another's quiet flag at the end: left as it was", rc == 0 and open(os.path.join(W, "locks", "quiet-desk-aifoundry2")).read().startswith("model-session-x"))
    os.remove(os.path.join(W, "locks", "quiet-desk-aifoundry2"))
    ses = os.path.join(S, "session_e216.sh")
    open(ses, "w").write("#!/usr/bin/env bash\nsleep 20\n")
    p = subprocess.Popen(["bash", ses])
    time.sleep(0.5)
    helper("book.sh", "take", "aifoundry2", "card-e216")
    rc, o = sh(rbs("end_e216.sh"), e)
    p.terminate()
    p.wait()
    row("E4 with a session_e216.sh of ours running: E refuses (17) and releases nothing (the booking kept)", rc == 17 and "card-e216" in helper("book.sh", "show"))
    helper("book.sh", "release", "aifoundry2", "card-e216")
    # fix-e209 (verify-e209's finding 7): a LEFTOVER keeps the flag, the hold line and the booking
    flag = os.path.join(W, "locks", "quiet-desk-aifoundry2")

    def take_all():
        helper("book.sh", "take", "aifoundry2", "card-e216")
        helper("hold.sh", "add", "card-e216")
        open(flag, "w").write("card-e216 a leftover path\n")

    def kept_all():
        return ("card-e216" in helper("book.sh", "show") and "card-e216" in helper("hold.sh", "list") and os.path.exists(flag)
                and open(flag).read().startswith("card-e216"))
    dev = os.path.join(S, "standin2_host")
    shutil.copyfile("/usr/bin/sleep", dev)
    os.chmod(dev, 0o755)
    take_all()
    p = subprocess.Popen([dev, "30"])
    time.sleep(0.5)
    rc, o = sh(rbs("end_e216.sh"), e)
    p.terminate()
    p.wait()
    row("E5 a device-named process of ours alive (comm ..._host: a leftover): E refuses (17), the flag, the hold line and the booking kept",
        rc == 17 and "device-named" in o and kept_all(), o.strip().splitlines()[-1][:200])
    lo_dir = os.path.join(root, "sessions", f"{int(time.time())}-a2c0-E216")
    os.makedirs(lo_dir)
    q = {"t_first_ms": 1, "leftover": {"records": [{"what": "host"}], "still_alive_at_release": 1, "waited_s": 600.0, "resolved": False}}
    json.dump(q, open(os.path.join(lo_dir, "queue.json"), "w"))
    rc, o = sh(rbs("end_e216.sh"), e)
    row("E6 a box-root session whose queue.json records an unresolved leftover (none alive now): E refuses (17), everything kept",
        rc == 17 and "leftover UNRESOLVED" in o and kept_all(), o.strip().splitlines()[-1][:200])
    q["leftover"].update(still_alive_at_release=0, resolved=True)
    json.dump(q, open(os.path.join(lo_dir, "queue.json"), "w"))
    rc, o = sh(rbs("end_e216.sh"), e)
    row("E7 the same leftover recorded resolved: E releases (the flag lowered, the hold line removed, the booking released)",
        rc == 0 and not os.path.exists(flag) and "card-e216" not in helper("book.sh", "show") and "card-e216" not in helper("hold.sh", "list"),
        o.strip().splitlines()[-1][:200])
    shutil.rmtree(lo_dir)


def main(argv):
    if argv[:1] == ["--inner"]:
        inner(argv[1], argv[2], argv[3], argv[4])
        return 0
    if len(argv) != 7 or argv[1] != "--round-w" or argv[3] != "--elf" or argv[5] != "--elf211":
        print(__doc__)
        return 2
    S = os.path.abspath(argv[0])
    if os.path.realpath(S).startswith(os.path.realpath(REPO) + os.sep):
        print("the scratch folder must be outside the repository")
        return 2
    for p in glob.glob("/dev/et*"):
        if not os.path.isfile(p):
            print(f"REFUSED: {p} is a device node here: run this inside W/nodev.sh")
            return 2
    os.makedirs(S, exist_ok=True)
    if os.listdir(S):
        print("give an empty scratch folder")
        return 2
    c = Ctx(S, os.path.abspath(argv[2]), os.path.abspath(argv[4]))
    c.elf211 = os.path.abspath(argv[6])
    print(f"E216 RUNBOOK DESK TEST {datetime.datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S %Z')}")
    for t in (t_window, t_quiet, t_rest, t_gate, t_step2, t_sandbox):
        try:
            t(c)
        except Exception as e:  # noqa: BLE001
            row(f"{t.__name__} ran to its end", False, f"{type(e).__name__}: {e}")
    print(f"SELFTEST-RB-E216 {sum(ROWS)} of {len(ROWS)} {'PASS' if all(ROWS) else 'FAIL'}")
    return 0 if all(ROWS) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
