#!/usr/bin/env python3
"""fwgate: the lab's generic firmware-identity gate (Q188, Sun 15 Nov 2026). Stdlib only; README.md beside it.

A card's firmware identity is carried by continuity: a box that has not booted since a committed firmware read of that
card still runs that firmware. After a later boot the identity is read again, with the read query the owner allows, and
compared field by field with the newest committed record (by read time). His words, Sun 15 Nov 2026: "Firmware
revisions query was a false positive. It should have never been forbidden. Reading operations and firmware are always
allowed." (15:07:01 PST) and "Yeah, fix the corresponding guards. I don't want to modify firmware, but commands which
read firmware should be fine." (15:09:49 PST). tools/claims-v3/dmcmd_table_v2.json classes the query READ (id 14).

    fwgate.py look  --box B --card N [--extra DIR ...]        no device: CONTINUITY (0), NEEDS-READ (17), NO-RECORD
                                                              (16), or STOPPED (16): a read of this boot did not end
                                                              EQUAL
    fwgate.py read  --box B --card N --out DIR [--extra DIR ...] [--both-nodes-ok]
                    only on NEEDS-READ: et-who --check must read free, then the card's lock (flock, non-blocking, on
                    the lab's own lock file, never made here), then ONE call, exactly
                      timeout 10 /opt/et/bin/dev_mngt_service -m <the query> -n N -u 5000 < /dev/null
                    in a scratch working directory under DIR, its answer parsed and compared with the record:
                    EQUAL writes a dated record in DIR (0); DIFFERENT or UNREADABLE stop (16); a held card, or a busy
                    or missing lock, sends nothing (17). Never another command, never a retry: each attempt is written
                    to the LEDGER (below) before the call and again after it, and once a read of this card has not
                    ended EQUAL on this boot, every later read of it on this boot refuses (16), into any DIR, until a
                    person has read it.
    fwgate.py guard --box B --card N [--extra DIR ...]        at launch: "identity: ... ok" (0) or "IDENTITY-STOP: ..."
                                                              (16), k6's words, from the committed records and any
                                                              EQUAL record a read wrote today, on this boot, in an
                                                              --extra DIR; always 16 while the LEDGER or an --extra DIR
                                                              holds a read of this boot that did not end EQUAL
    fwgate.py parse FILE [--section N]                         desk: the seven fields of a saved answer
    fwgate.py check-records                                    desk: every record against its committed source

LEDGER: <home>/.local/state/fwgate/<box>-c<card>.jsonl, the home directory taken from the user database (never
$HOME). One JSON line per event, SENT before the call and END with the verdict after it, each with this boot's id
(/proc/sys/kernel/random/boot_id) and boot time: only the lines of this boot count, and a line that cannot be read stops
every read (fail closed). It is per user and per box. A person who has read a stopped attempt moves its files out of DIR
and the ledger file aside; fwgate never clears a stop.

Exit codes: 0 ok; 10 refused before anything (usage, a box that is not this host, aifoundry1 without --both-nodes-ok,
desk-test settings outside a desk test or a desk test without every stand-in, a ledger that cannot be written);
16 IDENTITY-STOP; 17 NEEDS-READ, or call again (nothing sent).
aifoundry1: the vendor CLI opens both cards' management nodes even with -n, so a read there opens the other card's node
too: refused unless --both-nodes-ok (the owner's word for that), and then both cards' locks are held. aifoundry3: its
non-public build reports the same versions as aifoundry2's, so an EQUAL there shows the reported versions only.
Desk tests (tests/): FWGATE_DESK_TEST=1 needs every stand-in, FWGATE_CLI, FWGATE_ETWHO, FWGATE_LOCKDIR and
FWGATE_LEDGER_DIR, none of them a real path or a device tool's name, and lets FWGATE_HOSTNAME, FWGATE_BOOT_EPOCH,
FWGATE_BOOT_ID and FWGATE_NOW_EPOCH stand in; it is refused wherever a card node (/dev/et*_mgmt or /dev/et*_ops) exists.
"""
import argparse
import datetime
import errno
import fcntl
import glob
import hashlib
import json
import os
import pwd
import re
import socket
import subprocess
import sys
import time
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
RECORDS = HERE / "records"
REPO = HERE.parent.parent.parent
PACIFIC = ZoneInfo("America/Los_Angeles")
QUERY = "DM_CMD_GET_MODULE_FIRMWARE_REVISIONS"
QUERY_CODE = "14"
REAL = {"cli": "/opt/et/bin/dev_mngt_service", "timeout": "/usr/bin/timeout", "etwho": "/usr/local/bin/et-who",
        "lockdir": "/run/lock"}
DESK_NEEDS = ("FWGATE_CLI", "FWGATE_ETWHO", "FWGATE_LOCKDIR", "FWGATE_LEDGER_DIR")
DESK_KEYS = DESK_NEEDS + ("FWGATE_HOSTNAME", "FWGATE_BOOT_EPOCH", "FWGATE_BOOT_ID", "FWGATE_NOW_EPOCH")
# the process names THE QUIET DESK FLAG keeps off a box while its card runs a session (a stand-in never carries one)
DEVICE_TOOL = re.compile(r"_host$|^ettelem$|^dev_mngt|^et-powertop$|^mmbench_launch|^sys_emu$")
FIELDS = (("Firmware release revision", "release"), ("BL1 Firmware versions", "bl1"), ("BL2 Firmware versions", "bl2"),
          ("PMIC Firmware versions", "pmic"), ("Master Minion Firmware versions", "mm"),
          ("Worker Minion versions", "wm"), ("Machine Minion versions", "machm"))
KEYS = tuple(k for _, k in FIELDS)
# the words a transcribed record's statement uses for each field (check-records ties each value to one of them)
LABEL_WORDS = {"release": ("release",), "bl1": ("bl1",), "bl2": ("bl2",), "pmic": ("pmic",),
               "mm": ("master", "minion"), "wm": ("worker", "minion"), "machm": ("machine", "minion")}
BOTH_NODES = {"aifoundry1": (0, 1)}
CAVEAT = {"aifoundry3": ("caveat: aifoundry3 runs a non-public build that reports the same versions as aifoundry2's, and "
                         "its behaviour has changed under unchanged versions: an EQUAL there shows the reported versions "
                         "only")}
EXIT_OK, EXIT_USAGE, EXIT_STOP, EXIT_AGAIN = 0, 10, 16, 17
ANSI = re.compile(r"\x1b\[[0-9;]*m")
SUCCEEDED = re.compile(r"(?:^|\]: )Service request succeeded\s*$")
COMMAND = re.compile(r"\]: command: (\w+) code (\d+)\s*$")
DIGITS_ONLY = re.compile(r"^\s*\d+\s*$")
OPENING = re.compile(r"^\s*Opening device\b(.*)$")
VERSION = re.compile(r"(?<![\d.])\d{1,3}\.\d{1,3}\.\d{1,3}(?![\d.]*\d)")
RECORD_SCHEMA, READ_SCHEMA, LEDGER_SCHEMA = "fwgate-record/1", "fwgate-read/1", "fwgate-ledger/1"


class Refused(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code, self.msg = code, msg


def device_nodes():
    return sorted(glob.glob("/dev/et*_mgmt") + glob.glob("/dev/et*_ops"))


def real_ledger_dir():
    return os.path.join(pwd.getpwuid(os.getuid()).pw_dir, ".local", "state", "fwgate")


def same_path(a, b):
    """True when a and b name one file or directory: the same real path, or the same inode (a hard link)."""
    try:
        return os.path.realpath(a) == os.path.realpath(b) or os.path.samefile(a, b)
    except OSError:
        return False


def desk_check(env):
    """A desk test runs only with every stand-in, none of them a real path or named as a device tool."""
    missing = [k for k in DESK_NEEDS if not env.get(k)]
    if missing:
        raise Refused(EXIT_USAGE, f"a desk test without every stand-in ({', '.join(missing)} not set): refused; a desk "
                      "test never falls back to the real tools")
    real = {"FWGATE_CLI": REAL["cli"], "FWGATE_ETWHO": REAL["etwho"], "FWGATE_LOCKDIR": REAL["lockdir"],
            "FWGATE_LEDGER_DIR": real_ledger_dir()}
    for k, path in real.items():
        if same_path(env[k], path):
            raise Refused(EXIT_USAGE, f"a desk test with {k} at the real {path}: refused")
    for k in ("FWGATE_CLI", "FWGATE_ETWHO"):
        names = {os.path.basename(env[k]), os.path.basename(os.path.realpath(env[k]))}
        if any(DEVICE_TOOL.search(n) or DEVICE_TOOL.search(n[:15]) or n in ("et-who", "et-holders") for n in names):
            raise Refused(EXIT_USAGE, f"a desk test with {k} named as a lab tool ({', '.join(sorted(names))}): "
                          "refused; a stand-in carries no device tool's name")


def settings():
    """The real paths and clocks, or a desk test's stand-ins (only under FWGATE_DESK_TEST=1, never beside a card node)."""
    desk = os.environ.get("FWGATE_DESK_TEST") == "1"
    given = [k for k in DESK_KEYS if k in os.environ]
    if given and not desk:
        raise Refused(EXIT_USAGE, f"desk-test settings outside a desk test ({', '.join(given)}): refused")
    if desk and device_nodes():
        raise Refused(EXIT_USAGE, "a desk test where a card node exists (" + ", ".join(device_nodes()) + "): refused; "
                      "run it in a sandbox with no card node (bubblewrap --dev /dev)")
    if desk:
        desk_check(os.environ)
    env = os.environ if desk else {}
    s = {"desk": desk,
         "cli": env.get("FWGATE_CLI", REAL["cli"]),
         "timeout": REAL["timeout"],
         "etwho": env.get("FWGATE_ETWHO", REAL["etwho"]),
         "lockdir": env.get("FWGATE_LOCKDIR", REAL["lockdir"]),
         "ledger": env.get("FWGATE_LEDGER_DIR") or real_ledger_dir(),
         "hostname": env.get("FWGATE_HOSTNAME") or socket.gethostname().split(".")[0]}
    s["boot"] = int(env["FWGATE_BOOT_EPOCH"]) if "FWGATE_BOOT_EPOCH" in env else boot_epoch()
    s["boot_id"] = env.get("FWGATE_BOOT_ID") or (f"desk-boot-{s['boot']}" if desk else boot_id())
    s["now"] = float(env["FWGATE_NOW_EPOCH"]) if "FWGATE_NOW_EPOCH" in env else time.time()
    return s


def boot_epoch():
    try:
        with open("/proc/stat") as f:
            for ln in f:
                if ln.startswith("btime "):
                    return int(ln.split()[1])
    except OSError:
        pass
    raise Refused(EXIT_STOP, "IDENTITY-STOP: this host's boot time cannot be read (/proc/stat btime): nothing launched")


def boot_id():
    try:
        with open("/proc/sys/kernel/random/boot_id") as f:
            v = f.read().strip()
    except OSError:
        v = ""
    if not re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", v):
        raise Refused(EXIT_STOP, "IDENTITY-STOP: this host's boot id cannot be read (/proc/sys/kernel/random/boot_id): "
                      "nothing launched")
    return v


def pacific(epoch):
    return datetime.datetime.fromtimestamp(epoch, PACIFIC)


def text_time(epoch):
    return pacific(epoch).strftime("%Y-%m-%d %H:%M:%S %Z")


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(p):
    with open(p, "rb") as f:
        return sha256_bytes(f.read())


# ---- the parse: robust to runtime lines between the answer's lines, fails closed on anything else -------------------
def parse(text):
    """The seven fields of one answer. Colour codes are stripped; each label must stand on exactly one line, at its
    start (a filtered copy) or after the logger's ']: ', its three numbers ending the line; 'Service request succeeded'
    exactly once; a 'command:' line, when the tool prints one, must name the query and code 14 alone. A runtime line
    between lines changes nothing; one spliced into a field's line, a label twice, a missing success line or another
    command make the answer UNREADABLE, and so do a line of digits alone and a line 'Opening device <one digit>'
    followed by digits alone (a print that starts with a newline, spliced into a number, leaves the number's tail
    there). Returns (fields or None, problems, info)."""
    lines = ANSI.sub("", text).splitlines()
    fields, problems = {}, []
    for label, key in FIELDS:
        rx = re.compile(r"^(?:.*\]: )?" + re.escape(label) + r": Major: (\d{1,3}) Minor: (\d{1,3}) Revision: (\d{1,3})\s*$")
        hits = [m for m in (rx.match(ln) for ln in lines) if m]
        if len(hits) != 1:
            problems.append(f"{len(hits)} lines for '{label}' (want 1)")
            continue
        nums = [int(x) for x in hits[0].groups()]
        if max(nums) > 255:
            problems.append(f"'{label}': a number above 255")
            continue
        fields[key] = ".".join(str(x) for x in nums)
    ok = sum(1 for ln in lines if SUCCEEDED.search(ln))
    if ok != 1:
        problems.append(f"{ok} 'Service request succeeded' lines (want 1)")
    cmds = [m.groups() for m in (COMMAND.search(ln) for ln in lines) if m]
    if len(cmds) > 1 or any(c != (QUERY, QUERY_CODE) for c in cmds):
        problems.append(f"command lines {cmds}: want at most one, the query (code {QUERY_CODE})")
    digits = [ln.strip() for ln in lines if DIGITS_ONLY.match(ln)]
    if digits:
        problems.append(f"{len(digits)} line(s) of digits alone ({', '.join(digits[:3])}): a number split by a print")
    odd = [ln.strip() for ln in lines if (m := OPENING.match(ln)) and not opening_ok(m.group(1))]
    if odd:
        problems.append(f"{len(odd)} runtime line(s) not 'Opening device <one digit>' ({odd[0][:40]!r}): a number "
                        "split by a print")
    info = {"command_lines": len(cmds), "succeeded_lines": ok, "lines": len(lines)}
    return (None if problems else fields), problems, info


def opening_ok(rest):
    """The text after 'Opening device' is one digit, then anything but digits alone (a split number's tail)."""
    m = re.match(r" (\d)(.*)$", rest)
    return bool(m) and not DIGITS_ONLY.match(m.group(2))


def compare(fields, ref):
    rows = [{"field": k, "record": ref[k], "this": (fields or {}).get(k), "equal": bool(fields) and fields[k] == ref[k]}
            for k in KEYS]
    return ("EQUAL" if fields and all(r["equal"] for r in rows) else "DIFFERENT"), rows


# ---- the records ---------------------------------------------------------------------------------------------------
def record_epoch(r):
    return datetime.datetime.fromisoformat(r["read_at"]).timestamp()


def committed_records(box=None, card=None):
    out = []
    for p in sorted(RECORDS.glob("*.json")):
        r = json.loads(p.read_text())
        if r.get("schema") != RECORD_SCHEMA or set(r.get("fields", {})) != set(KEYS):
            raise Refused(EXIT_STOP, f"IDENTITY-STOP: {p.name} is not a {RECORD_SCHEMA} record with the seven fields")
        if (box is None or r["box"] == box) and (card is None or r["card"] == card):
            out.append({"file": p.name, "sha256": sha256_file(p), "epoch": record_epoch(r), "label": r["by"],
                        "read_at": r["read_at_text"], "fields": r["fields"], "kind": "committed",
                        "desc": f"{r['by']}'s firmware read of {r['read_at_text']}"})
    return out


def extra_records(dirs, box, card, s):
    """EQUAL records a read wrote in DIRS for this box and card, on this boot and today (Pacific), each checked again:
    its raw answer beside it at its sha256, re-parsed EQUAL to the committed record it names, at that record's sha256."""
    good, notes = [], []
    committed = {c["file"]: c for c in committed_records(box, card)}
    for d in dirs or []:
        for p in sorted(Path(d).glob("fwgate-*.json")):
            try:
                r = json.loads(p.read_text())
            except (OSError, ValueError):
                notes.append(f"{p.name}: unreadable, not used")
                continue
            if (not isinstance(r, dict) or r.get("schema") != READ_SCHEMA or r.get("box") != box
                    or r.get("card") != card):
                continue
            why = None
            refd = r.get("reference") if isinstance(r.get("reference"), dict) else {}
            ref = committed.get(refd.get("file"))
            t = r.get("read_epoch")
            if r.get("verdict") != "EQUAL":
                why = f"verdict {r.get('verdict')}"
            elif r.get("desk_test") is not False and not s["desk"]:
                why = "a desk test's record (or one that does not say)"
            elif (not isinstance(t, (int, float)) or r.get("boot_epoch") != s["boot"]
                  or r.get("boot_id") != s["boot_id"] or not t > s["boot"]):
                why = "not on this boot"
            elif pacific(t).date() != pacific(s["now"]).date():
                why = "not written today (Pacific)"
            elif ref is None or ref["sha256"] != refd.get("sha256"):
                why = "its committed record is missing or changed"
            else:
                try:
                    raw = b"".join((p.parent / r["raw"][k]["file"]).read_bytes() for k in ("stdout", "stderr"))
                    shas_ok = all(sha256_file(p.parent / r["raw"][k]["file"]) == r["raw"][k]["sha256"]
                                  for k in ("stdout", "stderr"))
                except (OSError, KeyError, TypeError):
                    raw, shas_ok = b"", False
                fields, _, _ = parse(raw.decode("utf-8", "replace"))
                if not shas_ok:
                    why = "its raw answer is missing or changed"
                elif fields != r.get("fields") or compare(fields, ref["fields"])[0] != "EQUAL":
                    why = "its raw answer does not re-parse EQUAL"
            if why:
                notes.append(f"{p.name}: {why}, not used")
                continue
            good.append({"file": p.name, "sha256": sha256_file(p), "epoch": t, "label": "fwgate",
                         "read_at": r.get("read_at"), "fields": r["fields"], "kind": "extra",
                         "desc": f"the firmware read of {r.get('read_at')} ({p.name})"})
    return good, notes


def newest(box, card, extra, s):
    """The reference (the newest record by read time, committed or a verified EQUAL read of today) and the newest
    committed record by read time, never by file name."""
    recs = committed_records(box, card)
    more, notes = extra_records(extra, box, card, s)
    by_time = lambda r: r["epoch"]  # noqa: E731
    allr = recs + more
    return (max(allr, key=by_time) if allr else None), (max(recs, key=by_time) if recs else None), notes


# ---- the ledger and the stops: one card, one boot, never a retry ----------------------------------------------------
def ledger_path(s, box, card):
    return Path(s["ledger"]) / f"{box}-c{card}.jsonl"


def ledger_attempts(s, box, card):
    """This boot's attempts in the ledger as {record: its last verdict}, and the lines that cannot be read (each a stop:
    which boot they belong to cannot be told)."""
    p = ledger_path(s, box, card)
    try:
        text = p.read_text()
    except (FileNotFoundError, NotADirectoryError):  # no ledger, so no attempt yet (a write of one is checked apart)
        return {}, []
    except (OSError, UnicodeDecodeError) as e:
        return {}, [(str(p), f"LEDGER-UNREADABLE ({e})")]
    final, bad = {}, []
    for i, ln in enumerate(text.split("\n"), 1):
        if not ln.strip():
            continue
        try:
            e = json.loads(ln)
        except ValueError:
            e = None
        if (not isinstance(e, dict) or e.get("schema") != LEDGER_SCHEMA or e.get("box") != box or e.get("card") != card
                or not isinstance(e.get("record"), str) or not isinstance(e.get("boot_id"), str)):
            bad.append((f"{p}:{i}", "LEDGER-LINE-UNREADABLE"))
            continue
        if e["boot_id"] == s["boot_id"]:
            final[e["record"]] = e.get("verdict")
    return final, bad


def read_stops(dirs, box, card, s, sent_counts):
    """The reads of this card on this boot that did not end EQUAL, from the ledger and from the records in DIRS, as
    (where, verdict). A SENT counts when sent_counts is set (under the held card lock, where no read of ours is in
    flight, or at look and guard); a ledger line or a record that cannot be read always counts."""
    final, stops = ledger_attempts(s, box, card)
    stops += [(rec, str(v)) for rec, v in final.items() if v != "EQUAL" and (sent_counts or v != "SENT")]
    for d in dirs or []:
        for p in sorted(Path(d).glob(f"fwgate-{box}-c{card}-*.json")):
            try:
                r = json.loads(p.read_text())
            except (OSError, ValueError):
                r = None
            if (not isinstance(r, dict) or r.get("schema") != READ_SCHEMA or r.get("box") != box
                    or r.get("card") != card):
                stops.append((str(p), "UNREADABLE-RECORD"))
                continue
            if isinstance(r.get("boot_id"), str):
                this_boot = r["boot_id"] == s["boot_id"]
            elif isinstance(r.get("boot_epoch"), int):
                this_boot = r["boot_epoch"] == s["boot"]
            else:
                stops.append((str(p), "UNREADABLE-RECORD"))
                continue
            v = r.get("verdict")
            if this_boot and v != "EQUAL" and (sent_counts or v != "SENT"):
                stops.append((str(p), str(v)))
    return stops


def stop_text(stops):
    where, v = stops[-1]
    return f"{v} ({where})" + (f" and {len(stops) - 1} more" if len(stops) > 1 else "")


def ledger_line(s, box, card, event, verdict, record):
    return json.dumps({"schema": LEDGER_SCHEMA, "box": box, "card": card, "event": event, "verdict": verdict,
                       "record": str(record), "boot_id": s["boot_id"], "boot_epoch": s["boot"],
                       "boot": text_time(s["boot"]), "at": time.time(), "at_text": text_time(time.time()),
                       "desk_test": s["desk"]}, sort_keys=True) + "\n"


def ledger_open(s, box, card):
    p = ledger_path(s, box, card)
    try:
        p.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        return os.open(p, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOCTTY, 0o600)
    except OSError as e:
        raise Refused(EXIT_USAGE, f"the attempt ledger {p} cannot be written ({e.strerror}): nothing sent")


def ledger_append(s, box, card, event, verdict, record):
    """One whole line appended (one write, O_APPEND) and synced, or Refused: an attempt not in the ledger is never
    sent."""
    fd = ledger_open(s, box, card)
    data = ledger_line(s, box, card, event, verdict, record).encode()
    try:
        n = os.write(fd, data)
        os.fsync(fd)
    except OSError as e:
        raise Refused(EXIT_USAGE, f"the attempt ledger {ledger_path(s, box, card)}: {e.strerror}")
    finally:
        os.close(fd)
    if n != len(data):
        raise Refused(EXIT_USAGE, f"the attempt ledger {ledger_path(s, box, card)}: a short write")


# ---- the subcommands -----------------------------------------------------------------------------------------------
def head(s, box, card):
    if s["hostname"] != box:
        raise Refused(EXIT_USAGE, f"--box {box} is not this host ({s['hostname']}): refused")
    if card < 0:
        raise Refused(EXIT_USAGE, f"--card {card}: refused")
    if box in CAVEAT:
        print(CAVEAT[box])


def where(box, card, ref, s):
    return f"{box} card {card} booted {text_time(s['boot'])}; its newest firmware read of record is {ref['desc']}"


def cmd_look(a, s):
    head(s, a.box, a.card)
    stops = read_stops(a.extra, a.box, a.card, s, sent_counts=True)
    if stops:
        print(f"STOPPED: a firmware read of {a.box} card {a.card} on this boot (booted {text_time(s['boot'])}) did not "
              f"end EQUAL: {stop_text(stops)}: no read and no launch on this boot until a person has read it")
        return EXIT_STOP
    ref, _, notes = newest(a.box, a.card, a.extra, s)
    for n in notes:
        print("note: " + n)
    if ref is None:
        print(f"NO-RECORD: no committed firmware read of {a.box} card {a.card}: identity cannot be shown")
        return EXIT_STOP
    if s["boot"] < ref["epoch"]:
        print(f"CONTINUITY: {where(a.box, a.card, ref, s)}, after the boot: identity carried; no read needed")
        return EXIT_OK
    print(f"NEEDS-READ: {where(a.box, a.card, ref, s)}, before the boot: read it again (fwgate.py read)")
    return EXIT_AGAIN


def cmd_guard(a, s):
    head(s, a.box, a.card)
    stops = read_stops(a.extra, a.box, a.card, s, sent_counts=True)
    if stops:
        print(f"IDENTITY-STOP: {a.box} card {a.card} booted '{text_time(s['boot'])}': a firmware read on this boot did "
              f"not end EQUAL, {stop_text(stops)}: nothing launched")
        return EXIT_STOP
    ref, _, notes = newest(a.box, a.card, a.extra, s)
    for n in notes:
        print("note: " + n)
    if ref is not None and s["boot"] < ref["epoch"]:
        print(f"identity: {a.box} card {a.card} booted {text_time(s['boot'])}, before {ref['desc']}: ok")
        return EXIT_OK
    what = ref["desc"] if ref else "any committed firmware read"
    print(f"IDENTITY-STOP: {a.box} card {a.card} booted '{text_time(s['boot'])}', not before {what}: its firmware "
          "build is not carried by continuity (fwgate.py read re-reads it): nothing launched")
    return EXIT_STOP


def take_locks(lockdir, cards):
    fds = []

    def close_all():
        for f in fds:
            os.close(f)

    for c in cards:
        path = os.path.join(lockdir, f"etsoc-shire{c}.lock")
        try:
            fd = os.open(path, os.O_RDONLY | os.O_NOCTTY)  # never made here: the lab's lock files exist from boot
        except FileNotFoundError:
            close_all()
            raise Refused(EXIT_AGAIN, f"the card lock {path} is missing (fwgate never makes one, and the lab's kits do "
                          "not start without it): nothing sent")
        except OSError as e:
            close_all()
            raise Refused(EXIT_AGAIN, f"the card lock {path} cannot be opened ({e.strerror}): nothing sent (call "
                          "again)")
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as e:
            os.close(fd)
            close_all()
            if e.errno in (errno.EWOULDBLOCK, errno.EAGAIN):
                raise Refused(EXIT_AGAIN, f"the card lock {path} is held: nothing sent (call again)")
            raise Refused(EXIT_AGAIN, f"the card lock {path}: {e}: nothing sent (call again)")
        fds.append(fd)
    return fds


def write_json(path, obj):
    tmp = str(path) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)


def cmd_read(a, s):
    head(s, a.box, a.card)
    cards = BOTH_NODES.get(a.box, (a.card,))
    if a.box in BOTH_NODES and not a.both_nodes_ok:
        raise Refused(EXIT_USAGE, f"{a.box}: the vendor CLI opens both cards' management nodes even with -n, so this "
                      f"read opens card {', '.join(str(c) for c in cards if c != a.card)}'s node too: refused without "
                      "--both-nodes-ok (the owner's word for it)")
    if a.card not in cards:
        raise Refused(EXIT_USAGE, f"{a.box} has no card {a.card} here: refused")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    dirs = [str(out)] + list(a.extra)
    ref, rec, notes = newest(a.box, a.card, dirs, s)
    for n in notes:
        print("note: " + n)
    if rec is None:
        print(f"NO-RECORD: no committed firmware read of {a.box} card {a.card} to compare with: nothing sent")
        return EXIT_STOP
    stops = read_stops(dirs, a.box, a.card, s, sent_counts=False)  # a SENT may be in flight: decided under the lock
    if stops:
        print(f"IDENTITY-STOP: a firmware read of {a.box} card {a.card} on this boot already ended {stop_text(stops)}: "
              "never a retry; a person reads it first: nothing sent")
        return EXIT_STOP
    if s["boot"] < ref["epoch"]:
        print(f"CONTINUITY: {where(a.box, a.card, ref, s)}, after the boot: nothing sent")
        return EXIT_OK
    try:
        cli_sha = sha256_file(s["cli"])
    except OSError as e:
        print(f"IDENTITY-STOP: the vendor CLI {s['cli']} cannot be read ({e.strerror}): nothing sent")
        return EXIT_STOP
    os.close(ledger_open(s, a.box, a.card))  # the ledger can be written, or Refused (10) before anything
    try:
        w = subprocess.run([s["etwho"], "--check"], stdin=subprocess.DEVNULL, capture_output=True, text=True)
        w_rc, w_out = w.returncode, (w.stdout.strip() + " " + w.stderr.strip()).strip()
    except OSError as e:
        w_rc, w_out = None, f"{s['etwho']}: {e.strerror}"
    if w_rc != 0:
        print(f"et-who --check rc {w_rc}" + (": " + w_out.replace("\n", "; ") if w_out else ""))
        print("HELD: the card is held or the check failed: nothing sent (call again)")
        return EXIT_AGAIN
    fds = take_locks(s["lockdir"], cards)
    try:
        ref, rec, _ = newest(a.box, a.card, dirs, s)  # again, holding the lock(s): no read of ours is in flight now
        stops = read_stops(dirs, a.box, a.card, s, sent_counts=True)
        if stops:
            print(f"IDENTITY-STOP: a firmware read of {a.box} card {a.card} on this boot already ended "
                  f"{stop_text(stops)} (read holding the card's lock): never a retry; a person reads it first: nothing "
                  "sent")
            return EXIT_STOP
        if s["boot"] < ref["epoch"]:
            print(f"CONTINUITY: {ref['desc']} appeared while the lock was taken: nothing sent")
            return EXIT_OK
        now = s["now"] if "FWGATE_NOW_EPOCH" in os.environ and s["desk"] else time.time()
        base = f"fwgate-{a.box}-c{a.card}-{pacific(now).strftime('%Y%m%d-%H%M%S')}"
        jpath, cwd = out / (base + ".json"), out / (base + "-cwd")
        if jpath.exists() or cwd.exists():
            print(f"{jpath.name} or its directory exists already: nothing sent (call again)")
            return EXIT_AGAIN
        argv = [s["timeout"], "10", s["cli"], "-m", QUERY, "-n", str(a.card), "-u", "5000"]
        meta = {"schema": READ_SCHEMA, "box": a.box, "card": a.card, "verdict": "SENT", "argv": argv,
                "stdin": "/dev/null", "cwd": cwd.name, "locks": [f"etsoc-shire{c}.lock" for c in cards],
                "et_who_check_rc": w_rc, "boot_epoch": s["boot"], "boot_id": s["boot_id"], "boot": text_time(s["boot"]),
                "read_epoch": now, "read_at": text_time(now), "ET_DEVICES": os.environ.get("ET_DEVICES"),
                "cli_sha256": cli_sha, "fwgate_sha256": sha256_file(__file__),
                "ledger": str(ledger_path(s, a.box, a.card)),
                "reference": {"file": rec["file"], "sha256": rec["sha256"], "by": rec["label"],
                              "read_at": rec["read_at"]},
                "desk_test": s["desk"]}
        ledger_append(s, a.box, a.card, "SENT", "SENT", jpath.resolve())  # first: a crash leaves a stop, never a retry
        cwd.mkdir()
        write_json(jpath, meta)
        so, se = out / (base + ".stdout"), out / (base + ".stderr")
        t0 = time.time()
        with open(so, "wb") as fo, open(se, "wb") as fe:
            p = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=fo, stderr=fe, cwd=str(cwd))
            try:
                rc = p.wait(timeout=30)
            except subprocess.TimeoutExpired:
                p.terminate()  # a plain kill, never -9
                try:
                    rc = p.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    rc = None
        t1 = time.time()
    finally:
        for f in fds:
            os.close(f)
    left = sorted(x.name for x in cwd.iterdir())
    if not left:
        cwd.rmdir()
    raw = so.read_bytes() + se.read_bytes()
    fields, problems, info = parse(raw.decode("utf-8", "replace"))
    if rc != 0:
        problems.append(f"rc {rc}")
        fields = None
    verdict, rows = compare(fields, rec["fields"]) if fields else ("UNREADABLE", compare(None, rec["fields"])[1])
    meta.update({"verdict": verdict, "rc": rc, "seconds": round(t1 - t0, 3), "fields": fields, "rows": rows,
                 "problems": problems, "parse": info, "cwd_left": left,
                 "raw": {"stdout": {"file": so.name, "sha256": sha256_file(so)},
                         "stderr": {"file": se.name, "sha256": sha256_file(se)}}})
    write_json(jpath, meta)
    for r in rows:
        print(f"  {r['field']:<8} record {r['record']:<8} this {str(r['this']):<8} {'EQUAL' if r['equal'] else 'DIFF'}")
    for x in problems:
        print("problem: " + x)
    try:
        ledger_append(s, a.box, a.card, "END", verdict, jpath.resolve())
    except Refused as e:
        print(e.msg)
        print(f"IDENTITY-STOP: {verdict}, but the ledger did not take this read's end ({jpath.name}): its SENT line "
              "stops every later read and launch on this boot; a person reads it first")
        return EXIT_STOP
    if verdict == "EQUAL":
        print(f"EQUAL: {a.box} card {a.card} at {text_time(now)} matches {rec['label']}'s read of {rec['read_at']} in "
              f"all seven fields: record {jpath.name}")
        return EXIT_OK
    print(f"IDENTITY-STOP: {verdict}: {a.box} card {a.card} at {text_time(now)} against {rec['label']}'s read of "
          f"{rec['read_at']} ({jpath.name}): stop and report; never a retry on this boot")
    return EXIT_STOP


def section_text(path, section=None, jsonl_line=None, pointer=None):
    b = Path(path).read_bytes()
    if jsonl_line:
        obj = json.loads(b.decode("utf-8").split("\n")[jsonl_line - 1])
        for k in pointer.split("."):
            obj = obj[k]
        return obj
    t = b.decode("utf-8", "replace")
    if section:
        parts = re.split(r"(?m)^### ", t)
        return parts[section]
    return t


def cmd_parse(a, s=None):
    fields, problems, info = parse(section_text(a.file, a.section))
    print(json.dumps({"fields": fields, "problems": problems, "info": info}, sort_keys=True))
    return EXIT_OK if fields else EXIT_STOP


def tied(expect, key, value):
    """True when one expect string names the field (one of its label words) and the first version number after that
    word is the record's value."""
    for e in expect:
        low = e.lower()
        for w in LABEL_WORDS[key]:
            i = low.find(w)
            while i >= 0:
                m = VERSION.search(e, i + len(w))
                if m and m.group(0) == value:
                    return True
                i = low.find(w, i + 1)
    return False


def check_record(r):
    """A committed record against its sources: each at its sha256, and its fields re-read from them (a transcribed
    source: its expect strings found in its lines, and each of the seven values tied to its field in them)."""
    bad = []
    for src in r["sources"]:
        p = REPO / src["path"]
        if not p.exists():
            bad.append(f"{src['path']}: missing")
            continue
        if sha256_file(p) != src["sha256"]:
            bad.append(f"{src['path']}: sha256 {sha256_file(p)[:12]} is not {src['sha256'][:12]}")
            continue
        if src["form"] == "transcribed":
            a, b = (int(x) for x in src["lines"].split("-"))
            text = " ".join(x.strip() for x in p.read_text().split("\n")[a - 1:b])
            miss = [e for e in src["expect"] if e not in text]
            if miss:
                bad.append(f"{src['path']}:{src['lines']}: lacks {miss}")
            untied = [k for k in KEYS if not tied(src["expect"], k, r["fields"][k])]
            if untied:
                bad.append(f"{src['path']}:{src['lines']}: its expect strings do not tie {untied} to the record's "
                           "values")
        else:
            fields, problems, _ = parse(section_text(p, src.get("section"), src.get("jsonl_line"), src.get("pointer")))
            if fields != r["fields"]:
                bad.append(f"{src['path']}: re-parsed {fields} {problems}")
    return bad


def cmd_check_records(a, s=None):
    n_bad = 0
    for p in sorted(RECORDS.glob("*.json")):
        r = json.loads(p.read_text())
        bad = check_record(r)
        n_bad += bool(bad)
        print(f"{p.name}: {'OK' if not bad else 'BAD: ' + '; '.join(bad)} ({r['box']} card {r['card']}, {r['by']}, "
              f"{r['read_at_text']})")
    return EXIT_OK if not n_bad else EXIT_STOP


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("look", "read", "guard"):
        p = sub.add_parser(name)
        p.add_argument("--box", required=True)
        p.add_argument("--card", type=int, required=True)
        p.add_argument("--extra", action="append", default=[], help="a directory a read wrote its records in")
        if name == "read":
            p.add_argument("--out", required=True, help="the directory the read writes its answer and record in")
            p.add_argument("--both-nodes-ok", action="store_true", help="aifoundry1 only, on the owner's word")
    p = sub.add_parser("parse")
    p.add_argument("file")
    p.add_argument("--section", type=int, help="the N-th '### ' section of a file holding several answers")
    sub.add_parser("check-records")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return EXIT_USAGE if e.code else EXIT_OK
    try:
        if a.cmd in ("parse", "check-records"):
            return {"parse": cmd_parse, "check-records": cmd_check_records}[a.cmd](a)
        s = settings()
        return {"look": cmd_look, "read": cmd_read, "guard": cmd_guard}[a.cmd](a, s)
    except Refused as e:
        print(e.msg)
        return e.code


if __name__ == "__main__":
    sys.exit(main())
