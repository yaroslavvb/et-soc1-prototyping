#!/usr/bin/env python3
"""E213 Amendment A2's box helper (Q219, lane a2-e213, Wed 18 Nov 2026, before any datum of E213's arm B): arm B's firmware identity on the
boot aifoundry1 runs now, by the lab's own gate, tools/claims-v3/fwgate/fwgate.py (landed d5beec9b, unchanged), run on the box from its tree
(nekko), where A2's step 4 synced fwgate.py, its six records and this file at their pinned sha256. Python's own modules only.

    python3 -I -B tools/claims-v3/e213-a2/fwgate_e213a2.py look --box aifoundry1 --card 1 --dir build/e213/fwgate-B-<day>
        fwgate.py look --box <box> --card <card> --extra DIR (no device): CONTINUITY (exit 0) passes; NEEDS-READ (17) goes on to the read; any
        other answer (STOPPED, NO-RECORD, a refusal, anything unreadable) is 16; and 16 too while this kit's attempt log (below) holds a read
        attempt of this boot that did not end EQUAL.
    python3 -I -B tools/claims-v3/e213-a2/fwgate_e213a2.py read --box aifoundry1 --card 1 --dir build/e213/fwgate-B-<day>
        ONLY ON NEEDS-READ (fwgate's look is made again first, no device: anything but NEEDS-READ sends nothing and is 16), and only when this
        kit's attempt log holds no attempt of this boot that did not end EQUAL: the attempt is written to the log first, then ONE call, exactly
        `fwgate.py read --box <box> --card <card> --both-nodes-ok --out DIR`, with ET_DEVICES removed from its environment (the stock vendor CLI
        does not honour it and opens both cards' management nodes whatever -n says; fwgate holds both cards' locks for the call); then the
        outcome is written to the log. EQUAL (fwgate's exit 0, its "EQUAL:" line, and the newest record in DIR this boot's EQUAL of today)
        passes, exit 0; ANYTHING ELSE is 16: DIFFERENT, UNREADABLE, a read of this boot that already ended otherwise, a busy or missing lock,
        et-who --check not free, a refusal (10), an exit or a record that cannot be read. Never a second call on the boot.
    python3 -I -B tools/claims-v3/e213-a2/fwgate_e213a2.py evidence --box aifoundry1 --card 1 --dir build/e213/fwgate-B-<day>
        READ ONLY (fix-a2e213, before A2 landed: verify-a2e213's finding 2): no device, no fwgate call, nothing written. It prints THIS BOOT'S
        lines of fwgate's own ledger (its path from fwgate's settings) and of this kit's attempt log, each verbatim after "A2-LEDGER " or
        "A2-ATTEMPT ", then one line "A2-EVIDENCE: ..." with their counts and its reading ("one call on this boot, ended EQUAL", "no call on
        this boot", or "NOT one EQUAL call on this boot: read the lines"), exit 0; "A2-EVIDENCE: NOT READ: ..." and 16 when a file or
        fwgate's settings cannot be read. A2's step 4 brings these lines to the desk for the data verifier; it is evidence, never a gate.
        (--dir is taken for the form's sake and not read.)

THE ATTEMPT LOG (this kit's, beside fwgate's own ledger): build/e213/a2-fwgate-attempts-<box>-c<card>.jsonl in the box's tree, one JSON line
ATTEMPT before the call and one END after it, each with the boot id fwgate itself reads (its settings(): /proc/sys/kernel/random/boot_id, or a
desk test's stand-in). fwgate's ledger records only the reads it sends; this log also records the calls that end before anything is sent (17: a
busy lock, a missing lock file, et-who --check not free; 10: a refusal), so that neither this kit nor any lane that uses it calls the read a
second time on a boot once a call did not end EQUAL (Amendment A2, item 1). An ATTEMPT with no END (a call cut off) stops every later read on
the boot; a line that cannot be read stops every read (fail closed). Only a person who has read the stopped attempt moves the log aside
(renamed with the date); this file never clears it, and an agent does not.

Exit codes: 0 pass (CONTINUITY, or this boot's EQUAL read; evidence: read); 17 NEEDS-READ (look only); 16 stop (no read and no launch on this
boot; evidence: not read); 2 usage.
Its words, one a line, are read by the runbook steps (tools/claims-v3/e213-a2/rb/): "A2-LOOK: CONTINUITY|NEEDS-READ|STOP: ...",
"A2-CALL: ...", "A2-READ: EQUAL <record> ...", "A2-STOP: ...", and the evidence's "A2-LEDGER ...", "A2-ATTEMPT ..." and "A2-EVIDENCE: ...".
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
TREE = HERE.parent.parent.parent                      # the box's tree (tools/claims-v3/e213-a2/ is three levels below it)
FWGATE = TREE / "tools" / "claims-v3" / "fwgate" / "fwgate.py"
SCHEMA = "e213a2-fwgate-attempt/1"
EXIT_OK, EXIT_USAGE, EXIT_STOP, EXIT_AGAIN = 0, 2, 16, 17


def say(line):
    print(line, flush=True)


def load_fwgate():
    """fwgate.py as a module (its settings(): the boot id and boot time it reads, a desk test's stand-ins honoured); nothing runs at import."""
    sys.path.insert(0, str(FWGATE.parent))
    try:
        import fwgate  # noqa: E402
    finally:
        sys.path.pop(0)
    return fwgate


def run_fwgate(args, env=None):
    """fwgate.py <args> as its own process: (rc, its output lines). Its output is printed, each line indented."""
    r = subprocess.run([sys.executable, "-I", "-B", str(FWGATE)] + args, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                       errors="replace", env=env)
    lines = (r.stdout + r.stderr).splitlines()
    for ln in lines:
        say("  | " + ln)
    return r.returncode, lines


def first(lines, *heads):
    for ln in lines:
        if ln.startswith(heads):
            return ln
    return ""


def log_path(box, card):
    return TREE / "build" / "e213" / f"a2-fwgate-attempts-{box}-c{card}.jsonl"


def attempts(box, card, boot_id):
    """This boot's attempts in this kit's log, [(when, its END verdict or None)], and the lines that cannot be read."""
    p = log_path(box, card)
    try:
        text = p.read_text()
    except FileNotFoundError:
        return [], []
    except (OSError, UnicodeDecodeError) as e:
        return [], [f"{p.name}: {e}"]
    opened, ended, bad = {}, {}, []
    for i, ln in enumerate(text.split("\n"), 1):
        if not ln.strip():
            continue
        try:
            e = json.loads(ln)
        except ValueError:
            e = None
        if (not isinstance(e, dict) or e.get("schema") != SCHEMA or e.get("box") != box or e.get("card") != card
                or e.get("event") not in ("ATTEMPT", "END") or not isinstance(e.get("attempt"), str)
                or not isinstance(e.get("boot_id"), str)):
            bad.append(f"{p.name}:{i}")
            continue
        if e["boot_id"] != boot_id:
            continue
        if e["event"] == "ATTEMPT":
            opened[e["attempt"]] = str(e.get("at_text", "?"))
        else:
            ended[e["attempt"]] = str(e.get("verdict"))
    rows = [(at, ended.get(k)) for k, at in opened.items()] + [("?", v) for k, v in ended.items() if k not in opened]
    return rows, bad


def blocked(box, card, boot_id):
    """'' when no attempt of this boot stands in the way, else why (an attempt not ended EQUAL, or a line that cannot be read)."""
    rows, bad = attempts(box, card, boot_id)
    if bad:
        return f"this kit's attempt log has line(s) that cannot be read ({', '.join(bad[:3])}): every read stops (fail closed)"
    stops = [f"{at} ended {v if v else 'with no END (cut off)'}" for at, v in rows if v != "EQUAL"]
    if stops:
        return (f"a read attempt of this boot did not end EQUAL ({'; '.join(stops[:3])}): never a second call on this boot, by this kit or any "
                "lane; a person reads it first")
    return ""


def log_append(box, card, event, attempt, s, **more):
    p = log_path(box, card)
    p.parent.mkdir(parents=True, exist_ok=True)
    line = dict({"schema": SCHEMA, "box": box, "card": card, "event": event, "attempt": attempt, "boot_id": s["boot_id"],
                 "boot_epoch": s["boot"], "at": time.time(), "at_text": time.strftime("%Y-%m-%d %H:%M:%S %Z"), "desk_test": s["desk"]}, **more)
    data = (json.dumps(line, sort_keys=True) + "\n").encode()
    fd = os.open(p, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOCTTY, 0o644)
    try:
        n = os.write(fd, data)
        os.fsync(fd)
    finally:
        os.close(fd)
    if n != len(data):
        raise OSError("a short write")


def settings_or_stop(F, box):
    try:
        s = F.settings()
    except F.Refused as e:
        say("  | " + e.msg)
        return None, f"fwgate's settings were refused (exit {e.code})"
    if s["hostname"] != box:
        return None, f"--box {box} is not this host ({s['hostname']})"
    return s, ""


def cmd_look(box, card, d):
    F = load_fwgate()
    s, why = settings_or_stop(F, box)
    if s is None:
        say(f"A2-LOOK: STOP: {why}: no read and no launch")
        return EXIT_STOP
    rc, lines = run_fwgate(["look", "--box", box, "--card", str(card), "--extra", d])
    b = blocked(box, card, s["boot_id"])
    if b:
        say(f"A2-LOOK: STOP: {b} (fwgate's look exited {rc}): no read and no launch on this boot")
        return EXIT_STOP
    if rc == 0 and first(lines, "CONTINUITY: "):
        say("A2-LOOK: CONTINUITY: " + first(lines, "CONTINUITY: ")[12:])
        return EXIT_OK
    if rc == 17 and first(lines, "NEEDS-READ: "):
        say("A2-LOOK: NEEDS-READ: " + first(lines, "NEEDS-READ: ")[12:])
        return EXIT_AGAIN
    w = first(lines, "STOPPED", "NO-RECORD", "IDENTITY-STOP") or (lines[-1] if lines else "no output")
    say(f"A2-LOOK: STOP: fwgate's look exited {rc}: {w[:300]}: no read and no launch on this boot")
    return EXIT_STOP


def equal_record(F, d, box, card, s):
    """(name, '') when the newest fwgate read record in DIR for this box and card is this boot's EQUAL of today (Pacific, fwgate's own
    clock), not a desk test's unless this is one; else (None, why)."""
    recs = []
    for p in sorted(Path(d).glob(f"fwgate-{box}-c{card}-*.json")):
        try:
            r = json.loads(p.read_text())
        except (OSError, ValueError):
            return None, f"{p.name} cannot be read"
        if not isinstance(r, dict):
            return None, f"{p.name} is not a record"
        t = r.get("read_epoch")
        recs.append((t if isinstance(t, (int, float)) else -1.0, p.name, r))
    if not recs:
        return None, "no record in DIR"
    t, name, r = max(recs)
    ok = (r.get("schema") == "fwgate-read/1" and r.get("verdict") == "EQUAL" and r.get("box") == box and r.get("card") == card
          and r.get("boot_id") == s["boot_id"] and r.get("boot_epoch") == s["boot"] and isinstance(r.get("desk_test"), bool)
          and r.get("desk_test") == s["desk"] and t > s["boot"] and F.pacific(t).date() == F.pacific(s["now"]).date())
    if ok:
        return name, ""
    return None, (f"{name}: verdict {r.get('verdict')}, {'this' if r.get('boot_id') == s['boot_id'] else 'another'} boot, "
                  f"{'a desk test' if r.get('desk_test') else 'not a desk test'}")


def cmd_read(box, card, d):
    F = load_fwgate()
    s, why = settings_or_stop(F, box)
    if s is None:
        say(f"A2-STOP: {why}: nothing sent, no launch")
        return EXIT_STOP
    b = blocked(box, card, s["boot_id"])
    if b:
        say(f"A2-STOP: {b}: nothing sent")
        return EXIT_STOP
    rc, lines = run_fwgate(["look", "--box", box, "--card", str(card), "--extra", d])        # the look again, at the read: no device
    if not (rc == 17 and first(lines, "NEEDS-READ: ")):
        w = first(lines, "CONTINUITY", "STOPPED", "NO-RECORD", "IDENTITY-STOP") or (lines[-1] if lines else "no output")
        say(f"A2-STOP: fwgate's look at the read is not NEEDS-READ (exit {rc}: {w[:300]}): nothing sent; stop and report")
        return EXIT_STOP
    attempt = f"{s['boot_id']}-{time.time():.6f}"
    argv = ["read", "--box", box, "--card", str(card), "--both-nodes-ok", "--out", d]
    try:
        log_append(box, card, "ATTEMPT", attempt, s, dir=d, argv=argv)
    except OSError as e:
        say(f"A2-STOP: this kit's attempt log cannot be written ({e}): nothing sent")
        return EXIT_STOP
    env = {k: v for k, v in os.environ.items() if k != "ET_DEVICES"}
    say(f"A2-CALL: fwgate.py {' '.join(argv)} (the one call; ET_DEVICES removed from its environment, it was "
        f"{'set' if 'ET_DEVICES' in os.environ else 'unset'})")
    rc, lines = run_fwgate(argv, env=env)
    name, why = equal_record(F, d, box, card, s)
    eq = rc == 0 and bool(first(lines, "EQUAL: ")) and name is not None
    if eq:
        verdict = "EQUAL"
    elif first(lines, "IDENTITY-STOP: DIFFERENT"):
        verdict = "DIFFERENT"
    elif first(lines, "IDENTITY-STOP: UNREADABLE"):
        verdict = "UNREADABLE"
    else:
        verdict = {0: "NOT-EQUAL-0", 10: "REFUSED-10", 16: "STOP-16", 17: "NOT-SENT-17"}.get(rc, f"EXIT-{rc}")
    try:
        log_append(box, card, "END", attempt, s, verdict=verdict, rc=rc, record=name or why)
    except OSError as e:
        say(f"A2-STOP: the read's outcome could not be written to this kit's attempt log ({e}): its ATTEMPT line stops every later read on "
            "this boot")
        return EXIT_STOP
    if eq:
        say(f"A2-READ: EQUAL {name} (fwgate exit 0: {first(lines, 'EQUAL: ')[7:][:240]})")
        return EXIT_OK
    w = first(lines, "IDENTITY-STOP", "HELD", "STOPPED", "NO-RECORD", "CONTINUITY", "EQUAL", "the card lock") or (lines[-1] if lines else
                                                                                                                  "no output")
    say(f"A2-STOP: the one read ended {verdict} (fwgate exit {rc}: {w[:240]}; {why or 'its record read'}): no launch on this boot and never a "
        "second read on it; report it")
    return EXIT_STOP


def boot_lines(p, boot_id, form_ok):
    """(this boot's lines, verbatim, each with its entry; the lines of another form, as name:line; '' or why the file cannot be read). A
    missing file has no line. A line is of this boot when it reads as an entry of the file's form and carries this boot's id."""
    try:
        text = p.read_text()
    except (FileNotFoundError, NotADirectoryError):
        return [], [], ""
    except (OSError, UnicodeDecodeError) as e:
        return [], [], f"{p.name}: {e}"
    keep, other = [], []
    for i, ln in enumerate(text.split("\n"), 1):
        if not ln.strip():
            continue
        try:
            e = json.loads(ln)
        except ValueError:
            e = None
        if not isinstance(e, dict) or not form_ok(e) or not isinstance(e.get("boot_id"), str):
            other.append(f"{p.name}:{i}")
            continue
        if e["boot_id"] == boot_id:
            keep.append((ln, e))
    return keep, other, ""


def cmd_evidence(box, card, d):
    """READ ONLY (fix-a2e213, verify-a2e213's finding 2): this boot's lines of fwgate's ledger and of this kit's attempt log, for the data
    verifier; no device, no fwgate call, nothing written. --dir is not read."""
    F = load_fwgate()
    s, why = settings_or_stop(F, box)
    if s is None:
        say(f"A2-EVIDENCE: NOT READ: {why}")
        return EXIT_STOP
    ledger_form = lambda e: (e.get("schema") == F.LEDGER_SCHEMA and e.get("box") == box and e.get("card") == card  # noqa: E731
                             and isinstance(e.get("record"), str))
    attempt_form = lambda e: (e.get("schema") == SCHEMA and e.get("box") == box and e.get("card") == card  # noqa: E731
                              and e.get("event") in ("ATTEMPT", "END") and isinstance(e.get("attempt"), str))
    ledger_file, attempt_file = Path(F.ledger_path(s, box, card)), log_path(box, card)
    led, led_other, why1 = boot_lines(ledger_file, s["boot_id"], ledger_form)
    att, att_other, why2 = boot_lines(attempt_file, s["boot_id"], attempt_form)
    if why1 or why2:
        say(f"A2-EVIDENCE: NOT READ: {why1 or why2}")
        return EXIT_STOP
    for ln, _ in led:
        say("A2-LEDGER " + ln)
    for ln, _ in att:
        say("A2-ATTEMPT " + ln)
    sent = [e for _, e in led if e.get("event") == "SENT"]
    lend = [e for _, e in led if e.get("event") == "END"]
    opened = [e for _, e in att if e.get("event") == "ATTEMPT"]
    aend = [e for _, e in att if e.get("event") == "END"]
    one = (len(led) == 2 and len(sent) == 1 and len(lend) == 1 and lend[0].get("verdict") == "EQUAL"
           and lend[0].get("record") == sent[0].get("record")
           and len(att) == 2 and len(opened) == 1 and len(aend) == 1 and aend[0].get("verdict") == "EQUAL"
           and aend[0].get("attempt") == opened[0].get("attempt") and not led_other and not att_other)
    none = not led and not att and not led_other and not att_other
    reading = ("one call on this boot, ended EQUAL" if one else
               "no call on this boot" if none else "NOT one EQUAL call on this boot: read the lines")
    verdicts = lambda es: ",".join(str(e.get("verdict")) for e in es) or "-"  # noqa: E731
    other = lambda o: f"; {len(o)} line(s) of another form ({', '.join(o[:3])})" if o else ""  # noqa: E731
    say(f"A2-EVIDENCE: fwgate's ledger {ledger_file.name}: {len(led)} line(s) of this boot (SENT {len(sent)}, END {len(lend)}: {verdicts(lend)})"
        f"{other(led_other)}; the kit's attempt log {attempt_file.name}: {len(att)} line(s) of this boot (ATTEMPT {len(opened)}, END {len(aend)}: "
        f"{verdicts(aend)}){other(att_other)}: {reading}")
    return EXIT_OK


def main(argv):
    if len(argv) != 7 or argv[0] not in ("look", "read", "evidence") or argv[1] != "--box" or argv[3] != "--card" or argv[5] != "--dir":
        print(__doc__)
        return EXIT_USAGE
    box, d = argv[2], argv[6]
    try:
        card = int(argv[4])
    except ValueError:
        print(__doc__)
        return EXIT_USAGE
    if card < 0 or not d or d.startswith("-"):
        print(__doc__)
        return EXIT_USAGE
    return {"look": cmd_look, "read": cmd_read, "evidence": cmd_evidence}[argv[0]](box, card, d)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
