#!/usr/bin/env python3
"""E194's kit (Q183, Sun 15 Nov 2026, written after E194's registration 0d8e3de0 and before any E194 datum): what the box runner, the
doubles, the collector and the desk tests share. It is E191's common module (tools/claims-v3/e191/e191_common.py, eb1ac923, unchanged
beside it, itself E189's ported to aifoundry1 card 1 with both of its verifiers' fixes) ported BACK to a card on the orchestrating box,
aifoundry2's own card 0, with E194's registered changes (E194.md sections 2, 3.1, 8.2, 11) and the parser lesson of E191's stop record:
  - the plan is E194's registered plan-e194.json (K, the order, the stops, the die gate, the clock rule, the cap), read and never changed;
    its six configurations' host arguments and K equal E189's (E194.md 4; step 2 checks it), so E189's host check reads E194's hosts;
  - THE CARD: aifoundry2 card 0, the box's only card, opened with ET_DEVICES (and V3_DEVICE) UNSET in every process (E190 arm A's form
    on this card: aifoundry2's device layer carries no ET_DEVICES; its guard refused any setting); its lock /run/lock/etsoc-shire0.lock;
    the box tree ~/claude/et-soc1-prototyping (k6's rb_tree for aifoundry2, E190 arm A's tree); the telemetry reader
    build/ettelem-hpl/ettelem there at its pin (E136's, E146's, E169's and E190 arm A's sampler), through E194's guard, which refuses any
    box but aifoundry2 and any ET_DEVICES setting;
  - the start config's line: TDP 65 W, threshold 65 C, minion 600 MHz at rest (E194.md 2, as E190 arm A read this card), and the
    identity gate's bounds (e194_ident.py): the read's stderr naming /dev/et0_mgmt and device ID 0, minion_mv a number between 450 and
    600 (this card read 519 at rest; a failed read 0 and a voltage at the 800 MHz point refused);
  - THE STOP LINES (E194.md 11): E189's (board at or above 65 W, minshire[0] at or above 70 C, on any live sample) and aifoundry2's own,
    kept beside them (board above 85 W on 3 samples in a row; minshire[0] or the latch minshire[2] at or above 80 C); E189's per-sample
    clock line is gone: at 800 MHz under load and 600 MHz at rest it would trip in every pass. THE CLOCK RULE, live, replaces it, per pass
    (clock_pass below): the live samples from the burst's first launch's start + 1.5 s to its last launch's end must read 800 MHz; the
    runner sets aside the first pass off it and stops the session at the second (E194.md 11);
  - the die gate at 57 C (E194.md 11; a die below 46 C does not block, it is labelled), everything else E189's word for word;
  - THE HOST'S LINE (E191's stop record 1a4bc1e3, CONTEXT section 116's lesson; kit mechanics): host_json() reads a host's own JSON object
    from its whole stdout, which a runtime print can split (aifoundry1's runtime printed "Opening device 1" between the two parts of the
    ledger host's line, and E191's last_json took the broken head): a reassembling parser that drops what the JSON grammar cannot take,
    to the end of its line, and records every dropped span; tested on the committed aifoundry1 bytes and on this box's (desk/parser_e194.py);
  - E191's kit constants (the sampler's freshness 2 s, the stop file, the BOUND poll), and sample_live() (a sample carrying every reading
    the stop lines read: board_w, minshire[0] and the minion clock, each a number), unchanged.
fix-e194 (Q183, Sun 15 Nov 2026, after E194's verifier and before any E194 datum; kit mechanics only, KIT.md section 11):
  - THE HOST'S LINE, VERIFIED (verify-e194's finding 2): host_result() is what the runner reads. It takes host_json's reading of the LAST
    object in the stdout that begins with the host's own key, and reads 'none' ({}: a FAILED RUN or a failed gate, never a guess) when a
    later object with that key cannot be read (never an earlier one), when a raw newline lies inside the object but at the end of a dropped
    span (a foreign line merged into a number leaves one: width 32 read as 3242), when a dropped span is not a whole known runtime line, or
    when the object fails its command line's checks (E191's kit note 2's ledger_checks and spp_checks, ported: the head fields equal the
    command's, the tail typed, len(wall_s) == launches, len(launch_epoch_ms) == 2 x launches, sparse parity's reps_requested the command's);
  - die_of, latch_of, sample_live and THE STOP LINES read a sampler line of any shape without raising (verify-e194's nit 7): a field that is
    not the object, list or number it should be reads as no reading;
  - `e194_common.py --config-line FILE` prints the config read's object as host_result reads it (step 7 on the box; verify-e194's nit 6).
Python's own modules only (it runs on aifoundry2 under /usr/bin/python3 3.12.3 with -I -B where called so).
    python3 -I -B tools/claims-v3/e194/e194_common.py        the self-check (E194-COMMON SELF-CHECK PASS)
    python3 -I -B tools/claims-v3/e194/e194_common.py --config-line <the config read's stdout file>
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
PLAN = os.path.join(HERE, "plan-e194.json")
ORDER = ["copy-zeros", "copy-random", "sha256", "sort-sorted", "sort-shuffled", "sparse-parity"]
LEDGER = ORDER[:5]
PROGRAM = {k: ("ledger" if k in LEDGER else "spp") for k in ORDER}
# ---- the card (E194.md 2)
BOX = "aifoundry2"
TREE = "claude/et-soc1-prototyping"                        # k6's rb_tree for aifoundry2 (E190 arm A's tree, a git checkout)
CARD = "0"
LOCK = "/run/lock/etsoc-shire0.lock"                       # card 0's lock, held for the session (the box's only card)
READER = "build/ettelem-hpl/ettelem"                       # E136's, E146's, E169's and E190 arm A's sampler on this card
READER_SHA256 = "77a46171c915d3a92898af9ffe04d92b86b65f4d36bc29d58f5c086f8accfeb5"   # its pin (e190_common.ARMS["A"])
GUARD = "tools/claims-v3/e194/ettelem_guard_e194.sh"      # E128's allow-list in E190's form: aifoundry2 and ET_DEVICES unset only
CONFIG_LINE = {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 600}   # E194.md 2 (E190 arm A); a different start: the gate
MV_ABOVE, MV_BELOW = 450, 600                              # the identity gate's sanity bounds (e194_ident.py); this card read 519 at rest
# ---- the box's build directories (build_e194.sh writes them in the box tree)
LEDGER_DIR = "build/e194ledger"
SPP_DIR = "build/e194spp"
LEDGER_HOST = LEDGER_DIR + "/host/ledger_host"
LEDGER_ELF = LEDGER_DIR + "/kernel/ledger.elf"
SPP_HOST = SPP_DIR + "/host/sparseparity_host"
SPP_ELF = SPP_DIR + "/kernel/sparseparity.elf"
BUILD_REC = {"ledger": LEDGER_DIR + "/BUILD-e194.json", "spp": SPP_DIR + "/BUILD-e194.json"}
EXPECT_SMOKE = "docs/reports/data/2026-11-12-q166-progs/digests/expect-b2048-r1-2048.txt"
# ---- E189's numbers, and E194's own (E194.md 9-11)
IDLE_BEFORE_S, IDLE_AFTER_S, EVERY_MS = 8.0, 10.0, 100      # energy.sh's form (E194.md 9)
HOST_TIMEOUT_S = 10                                         # every device-opening process under `timeout 10`
HOST_BOUND_S = HOST_TIMEOUT_S + 20                          # the runner's own bound around it; past it the QUEUE STOPS (run_e194.py)
ANCHOR_S = 120                                              # three 2-minute idle anchors (E194.md 10)
CAP_PASS_START_S = 108 * 60                                 # no pass starts after 108 card-minutes (E194.md 10)
CAP_S = 110 * 60
DIE_GATE_C, DIE_GATE_WAIT_S, DIE_LOW_C = 57, 600, 46        # E194.md 11; below 46 C does not block, it is labelled
STOP_BOARD_W, STOP_DIE_C = 65.0, 70.0                       # E189's lines (bind first)
A2_BOARD_W, A2_BOARD_N, A2_DIE_C = 85.0, 3, 80.0            # aifoundry2's own lines (E190 arm A's on this card), kept beside them
CLOCK_MHZ, IDLE_MHZ, CLIMB_S = 800, 600, 1.5                # THE CLOCK RULE (E194.md 3.1, 8.2, 11): 800 MHz from lo + 1.5 s to hi
LAST_MHZ = (780.0, 810.0)                                   # the scorer's last-launch window (E194.md 8.2; the runner does not read it)
CLOSE_CONFIG_S = 15                                         # the end bound: the closing config read's share of the last seconds
# ---- E191's kit mechanics, unchanged (its fix-e191k and fix-e191k2)
SAMPLE_FRESH_S = 2.0          # a host process and the die gate need a LIVE sample under 2 s old
STOP_FILE = "STOP"            # the session's early stop, a file of this name in its own directory (or SIGTERM to the runner)
BOUND_POLL_S = 1.0            # after a BOUND the runner keeps the card's lock and polls the host's end (nothing is killed)
# ---- E194's kit mechanics (KIT.md section 4)
HOLDER_REREAD_N, HOLDER_REREAD_S = 3, 2.0     # the holder rule at the start, with the lock held, re-read for our live collector's transient
RUNTIME_LINES = (re.compile(r"Opening device \d+"),)       # runtime prints seen on a host's stdout (aifoundry1's, 1a4bc1e3); reported


def plan():
    with open(PLAN) as f:
        return json.load(f)


def device_env(base=None):
    """The environment of every process the runner starts: the box's one card selected by leaving ET_DEVICES and V3_DEVICE UNSET (E190
    arm A's form on this card), the runtime's libraries."""
    env = dict(os.environ if base is None else base)
    env["LD_LIBRARY_PATH"] = "/opt/et/lib"
    env.pop("ET_DEVICES", None)
    env.pop("V3_DEVICE", None)
    return env


def sequence(p=None):
    """The session's sequence as plan-e194.json writes it: ('anchor', n) and ('pass', config, k, order_index) items, in order."""
    p = p or plan()
    seq, seen, idx = [("anchor", 1)], {}, 0
    rounds = p["order"]["rounds"]
    for r, rnd in enumerate(rounds):
        for cfg in rnd:
            seen[cfg] = seen.get(cfg, 0) + 1
            idx += 1
            seq.append(("pass", cfg, seen[cfg], idx))
        if r == 1:
            seq.append(("anchor", 2))
    seq.append(("anchor", 3))
    return seq


def check_sequence(p=None):
    """The written-out sequence (plan > order > sequence) equals the one built from the rounds: never re-drawn."""
    p = p or plan()
    words = [s for s in p["order"]["sequence"] if s.startswith("pass ")]
    built = [f"pass {it[3]}: {it[1]} p{it[2]}" for it in sequence(p) if it[0] == "pass"]
    return words == built and len(built) == 24


def host_argv(cfg, p=None, pass_dir=None):
    """One pass's host command line (without `timeout 10`), from the box tree's root."""
    p = p or plan()
    c = p["configs"][cfg]
    if PROGRAM[cfg] == "ledger":
        return [LEDGER_HOST, "--card"] + c["args"].split() + ["--kernel", LEDGER_ELF]
    rec = os.path.join(pass_dir, "host.rec") if pass_dir else "host.rec"
    return [SPP_HOST] + c["args"].split() + c["reps_flag"].split() + ["--kernel", SPP_ELF, "--records-out", rec]


def smoke_runs(programs):
    """The ramped smoke (E194.md 10, E189's), for the programs built today: (name, argv, what it must show)."""
    out = []
    if "ledger" in programs:
        out.append(("ledger-selftest", [LEDGER_HOST, "--selftest"], "selftest"))
        base = [LEDGER_HOST, "--card", "--kernel", LEDGER_ELF, "--launches", "1"]
        out += [("copy-64m-random", base + ["--prog", "copy", "--bytes", "64M", "--passes", "1", "--data", "random", "--width", "32"], "ledger"),
                ("copy-64m-zeros", base + ["--prog", "copy", "--bytes", "64M", "--passes", "1", "--data", "zeros", "--width", "32"], "ledger"),
                ("copy-1g-random", base + ["--prog", "copy", "--bytes", "1G", "--passes", "1", "--data", "random", "--width", "32"], "ledger"),
                ("sha256-b2048-r1", base + ["--prog", "sha256", "--block", "2048", "--repeat", "1", "--expect", EXPECT_SMOKE], "ledger"),
                ("sort-shuffled-r1", base + ["--prog", "sort", "--keys", "512", "--reps", "1", "--order", "shuffled"], "ledger"),
                ("sort-sorted-r1", base + ["--prog", "sort", "--keys", "512", "--reps", "1", "--order", "sorted"], "ledger")]
    if "spp" in programs:
        c = plan()["configs"]["sparse-parity"]
        out.append(("sparse-parity-r1", [SPP_HOST] + c["args"].split() + ["--reps", "1", "--kernel", SPP_ELF], "spp"))
    return out


# ---------------------------------------------------------------------------------------------------- THE HOST'S LINE (the parser)
_NUM = set("0123456789+-.eE")
_LIT = {"t": "true", "f": "false", "n": "null"}


def _scan_object(text, start, info=None):
    """Scan ONE JSON object from text[start] (a '{'), across line breaks, dropping foreign spans. A foreign span runs from a character the
    JSON grammar cannot take at that point (outside a string) to the end of its line, its newline included: a runtime prints whole lines,
    and the host prints its object on one line in parts (the ledger host: its head before it opens the card, the rest after its launches,
    workloads/ledger/host/main.cpp lines 478-492 and 621). Returns (kept text, [dropped spans], '' ) or (None, [spans], why)."""
    stack, kept, dropped = [], [], []
    st = "value"            # value | key_or_end | key | colon | after | value_or_end | str | num | lit
    lit = ""
    in_key = esc = False
    i, n = start, len(text)
    while i < n:
        ch = text[i]
        if st == "str":
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                st = "colon" if in_key else "after"
            elif ch == "\n" or ord(ch) < 0x20:
                return None, dropped, "a raw control character inside a string (the line was split inside a value)"
            kept.append(ch)
            i += 1
            continue
        if st == "num":
            if ch in _NUM:
                kept.append(ch)
                i += 1
                continue
            st = "after"                                    # the number ends here; the character is read again below
        if st == "lit":
            if lit and ch == lit[0]:
                kept.append(ch)
                lit = lit[1:]
                i += 1
                if not lit:
                    st = "after"
                continue
            return None, dropped, "a literal (true, false, null) cut short"
        if ch in " \t\r\n":                                 # whitespace between tokens (JSON's own; the host prints none)
            kept.append(ch)
            i += 1
            continue
        good = False
        if st in ("value", "value_or_end"):
            if ch == "{":
                stack.append("{"); st = "key_or_end"; good = True
            elif ch == "[":
                stack.append("["); st = "value_or_end"; good = True
            elif ch == '"':
                st, in_key, good = "str", False, True
            elif ch in "-0123456789":
                st, good = "num", True
            elif ch in _LIT:
                st, lit, good = "lit", _LIT[ch][1:], True
            elif ch == "]" and st == "value_or_end":
                stack.pop(); st = "after"; good = True
        elif st in ("key_or_end", "key"):
            if ch == '"':
                st, in_key, good = "str", True, True
            elif ch == "}" and st == "key_or_end":
                stack.pop(); st = "after"; good = True
        elif st == "colon":
            if ch == ":":
                st, good = "value", True
        elif st == "after":
            if ch == "," and stack:
                st, good = ("key" if stack[-1] == "{" else "value"), True
            elif ch in "}]" and stack and ch == ("}" if stack[-1] == "{" else "]"):
                stack.pop(); st, good = "after", True
        if good:
            kept.append(ch)
            i += 1
            if not stack and st == "after":
                if info is not None:
                    info["end"] = i                         # fix-e194: where the object ends in the text (host_result's record)
                return "".join(kept), dropped, ""
            continue
        j = text.find("\n", i)                              # a foreign span: from here to the end of its line, its newline too
        j = n if j < 0 else j + 1
        dropped.append(text[i:j].rstrip("\n"))
        i = j
    return None, dropped, "the object never closed"


def host_json(text, want=None):
    """A host's (or the reader's) own JSON object from its WHOLE stdout: (object, record). The record says how it was read: 'whole line'
    (the object was one unbroken line, as on aifoundry3 and in every committed aifoundry2 host stdout), 'reassembled' (one or more foreign
    spans dropped from inside it: each kept in record['dropped'], and record['runtime'] says whether each is a runtime line already seen
    on a lab box), or 'none' (no object could be read: {} is returned, and the reading is a FAILED RUN or a failed gate, never a guess).
    want: a key the object must hold ('ledger' for the ledger host, 'workload' for sparse parity's host, 'tdp_w' for the config read).
    Candidates: every '{' that begins a line, and every '{"<want>"' anywhere, from the LAST to the first."""
    text = text or ""
    cands = set(m.start() + 1 for m in re.finditer(r"\n\{", text))
    if text.startswith("{"):
        cands.add(0)
    if want:
        cands |= set(m.start() for m in re.finditer(r'\{"' + re.escape(want) + r'"', text))
    tried, why_last = 0, "no candidate object"
    for s in sorted(cands, reverse=True):
        tried += 1
        kept, dropped, why = _scan_object(text, s)
        if kept is None:
            why_last = why
            continue
        try:
            obj = json.loads(kept)
        except ValueError as e:
            why_last = f"the reassembled object does not parse ({e})"
            continue
        if not isinstance(obj, dict) or (want and want not in obj):
            why_last = f"the object read holds no '{want}' key" if want else "not an object"
            continue
        known = [any(r.fullmatch(d.strip()) for r in RUNTIME_LINES) for d in dropped]
        return obj, {"method": "reassembled" if dropped else "whole line", "dropped": dropped, "runtime": known,
                     "candidates_tried": tried}
    return {}, {"method": "none", "dropped": [], "runtime": [], "candidates_tried": tried, "why": why_last}


HOST_KEY = {"ledger": "ledger", "spp": "workload", "config": "tdp_w"}     # the key each host's own object begins with
LEDGER_TAIL = (("launches", int), ("wall_s", list), ("launch_epoch_ms", list), ("records_ok", int), ("records_bad", int), ("units", int),
               ("units_expected", int), ("hart0_cycles", dict), ("checked", int), ("mismatches", int), ("expect_checked", int),
               ("expect_mismatches", int), ("first_mismatch", str), ("status", str))      # e191_common_v2.LEDGER_TAIL (2d0fe517), unchanged
SPP_TAIL = (("reps_requested", int), ("reps_done", int), ("launch_s", list), ("launch_epoch_ms", list), ("kernel", dict), ("status", str))


def _arg(argv, name):
    argv = list(argv or [])
    if name in argv:
        i = argv.index(name)
        if i + 1 < len(argv):
            return argv[i + 1]
    return None


def parse_size(s):
    """main.cpp's parseSize (e191_common_v2.parse_size, unchanged): strtod, then K, M or G (powers of 1024), truncated; None if unread."""
    m = re.match(r"^\s*([0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)([A-Za-z]?)", str(s))
    if not m:
        return None
    v = float(m.group(1)) * {"K": 1024, "M": 1024 ** 2, "G": 1024.0 ** 3}.get(m.group(2).upper(), 1)
    return int(v)


def _isint(x):
    return isinstance(x, int) and not isinstance(x, bool)


def _typed(j, spec):
    bad = []
    for k, t in spec:
        v = j.get(k, None)
        if k not in j:
            bad.append(f"no {k}")
        elif t is int and not _isint(v):
            bad.append(f"{k} not an integer")
        elif t is not int and not isinstance(v, t):
            bad.append(f"{k} not a {t.__name__}")
    return bad


def ledger_checks(j, argv):
    """The ledger host's line against its own form and its command line (e191_common_v2.ledger_checks, 2d0fe517, unchanged): [] when it is
    the host's complete line for that command, else the reasons."""
    bad = []
    if j.get("ledger") != 1:
        bad.append(f"ledger {j.get('ledger')!r}, not 1")
    prog = _arg(argv, "--prog")
    if prog is not None and j.get("prog") != prog:
        bad.append(f"prog {j.get('prog')!r}, not the command's {prog!r}")
    if "--card" in (argv or []) and j.get("device") != "card":
        bad.append(f"device {j.get('device')!r}, not 'card'")
    want = []
    if prog == "copy":
        want = [("bytes", "--bytes", parse_size), ("passes", "--passes", int), ("data", "--data", str), ("width", "--width", int)]
    elif prog == "sha256":
        want = [("block", "--block", parse_size), ("repeat", "--repeat", int)]
    elif prog == "sort":
        want = [("keys", "--keys", int), ("reps", "--reps", int), ("order", "--order", str)]
    for key, flag, conv in want:
        a = _arg(argv, flag)
        if a is None:
            continue
        try:
            w = conv(a)
        except (TypeError, ValueError):
            w = None
        if j.get(key) != w:
            bad.append(f"{key} {j.get(key)!r}, not the command's {w!r}")
    st = j.get("status")
    if not isinstance(st, str):
        bad.append("no status")
    elif st in ("PASS", "FAIL"):
        bad += _typed(j, LEDGER_TAIL)
        if not bad:
            n = j["launches"]
            if len(j["wall_s"]) != n:
                bad.append(f"{len(j['wall_s'])} wall times for {n} launches")
            if len(j["launch_epoch_ms"]) != 2 * n:
                bad.append(f"{len(j['launch_epoch_ms'])} span ends for {n} launches")
            if not all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in j["wall_s"]):
                bad.append("a wall time not a number")
            if not all(_isint(x) for x in j["launch_epoch_ms"]):
                bad.append("a span end not an integer")
    return bad


def spp_checks(j, argv):
    """Sparse parity's line against its own form and its command line (e191_common_v2.spp_checks, 2d0fe517, unchanged)."""
    bad = []
    if j.get("workload") != "sparseparity":
        bad.append(f"workload {j.get('workload')!r}, not 'sparseparity'")
    st = j.get("status")
    if not isinstance(st, str):
        bad.append("no status")
    elif st in ("PASS", "FAIL"):
        bad += _typed(j, SPP_TAIL)
        r = _arg(argv, "--reps")
        if not bad and r is not None and str(j["reps_requested"]) != str(r):
            bad.append(f"reps_requested {j['reps_requested']}, not the command's {r}")
    return bad


def host_result(text, kind, argv=None):
    """THE HOST'S LINE, VERIFIED (fix-e194, verify-e194's finding 2): (object, record), what the runner reads for a host (kind 'ledger' or
    'spp', with its command line argv) or the config read (kind 'config'). host_json's reassembly, with every case it cannot verify read
    as 'none' ({} returned; the record's 'why' says which):
      1. the object is the LAST one in the stdout that begins with the host's own key ('{"ledger"', '{"workload"', '{"tdp_w"'); a later
         such object that cannot be read is never replaced by an earlier one (a stale object);
      2. no raw newline lies inside the object read: the host prints its line with no newline in it, so a newline inside is a foreign
         line's end, and when that line merged into a number (a runtime line beginning with a digit, '.', 'e' or 'E' after the head's last
         number, as width 32 becoming 3242) nothing else would show it;
      3. every dropped span is a whole known runtime line (RUNTIME_LINES: aifoundry1's "Opening device <n>", seen on a lab box): a span of
         any other text inside the host's line is never read around;
      4. the object passes its command line's checks (ledger_checks, spp_checks: E191's kit note 2's, unchanged); the config read's object
         is checked by config_ok and the identity gate, as before.
    Text outside the object (before it, or lines after it) is counted in the record, never read into it."""
    key = HOST_KEY.get(kind, kind)
    text = text or ""
    starts = [m.start() for m in re.finditer(r'\{"' + re.escape(key) + r'"', text)]
    base = {"reader": "e194_common.host_result (fix-e194): host_json's reassembly, the last object with the host's key, verified",
            "dropped": [], "runtime": [], "candidates": len(starts)}
    if not starts:
        return {}, dict(base, method="none", why=f"no object beginning with '{{\"{key}\"' in the stdout")
    s = starts[-1]
    info = {}
    kept, dropped, why = _scan_object(text, s, info)
    known = [any(r.fullmatch(d.strip()) for r in RUNTIME_LINES) for d in dropped]
    base.update(dropped=dropped, runtime=known)
    if kept is None:
        return {}, dict(base, method="none", why=f"the last object beginning with '{{\"{key}\"' cannot be read ({why})"
                        + ("; an earlier one is never read in its place" if len(starts) > 1 else ""))
    if "\n" in kept:
        return {}, dict(base, method="none", why="a raw newline inside the object read (a foreign line's end inside the host's line, "
                                                 "not at a dropped runtime line: a line merged into a value)")
    if not all(known):
        return {}, dict(base, method="none", why="a dropped span is not a whole known runtime line: " +
                        "; ".join(repr(d[:60]) for d, k in zip(dropped, known) if not k))
    try:
        obj = json.loads(kept)
    except ValueError as e:
        return {}, dict(base, method="none", why=f"the reassembled object does not parse ({str(e)[:80]})")
    if not isinstance(obj, dict) or key not in obj:
        return {}, dict(base, method="none", why=f"the object read holds no '{key}' key")
    bad = ledger_checks(obj, argv) if kind == "ledger" else (spp_checks(obj, argv) if kind == "spp" else [])
    if bad:
        return {}, dict(base, method="none", why="the line is not the host's complete line for this command: " + "; ".join(bad[:4]))
    outside = [ln for ln in (text[:s] + "\n" + text[info.get("end", len(text)):]).split("\n") if ln.strip()]
    return obj, dict(base, method="reassembled" if dropped else "whole line", other_lines=len(outside),
                     other_heads=[ln[:60] for ln in outside[:3]])


def host_json_words(rec):
    """The parse record in words for the session log ('' for an unbroken line)."""
    if not rec or rec.get("method") == "whole line":
        return ""
    if rec.get("method") == "none":
        return f"the host's line could not be read ({rec.get('why')})"
    spans = "; ".join(repr(d[:60]) for d in rec.get("dropped") or [])
    return (f"the host's line reassembled around {len(rec.get('dropped') or [])} foreign span(s) ({spans}; "
            f"{'each a runtime line seen before' if all(rec.get('runtime') or [False]) else 'NOT all a runtime line seen before: reported'})")


def last_json(text):
    """Kept for the callers that read a whole-line object only (the doubles' own self-checks); the runner reads hosts by host_json."""
    for ln in reversed((text or "").splitlines()):
        if ln.startswith("{"):
            try:
                return json.loads(ln)
            except ValueError:
                return {}
    return {}


def ledger_good(raw):
    """Every check of the ledger host's line but the launch count (main.cpp's pass condition without `launched == launches`)."""
    P = raw.get("participants")
    ok = (raw.get("records_bad") == 0 and P and raw.get("records_ok") == P and raw.get("units") == raw.get("units_expected")
          and (raw.get("checked") or 0) > 0 and raw.get("mismatches") == 0 and raw.get("expect_mismatches", 0) == 0)
    return bool(ok)


def adapt_ledger(raw, K):
    """THE ADAPTER (E194.md 8.1, E189's word for word): the ledger host's line -> the reducer's fields. reps_done = launches;
    reps_requested = K; launch_s = wall_s; launch_epoch_ms = [the first launch's t0, the last launch's t1]; status as the host said it;
    problems ["reps: k of K done"] when the budget cut the burst short with every other check good (SHORT: scored on its launches);
    otherwise, when the host said FAIL, the checks that failed (a FAILED RUN, not a datum)."""
    n = int(raw.get("launches") or 0)
    ep = raw.get("launch_epoch_ms") or []
    good = ledger_good(raw)
    short = good and 0 < n < K and raw.get("status") != "PASS"
    out = {"adapter": "e194_common.adapt_ledger (E194.md section 8.1; E189's adapter)", "ledger_prog": raw.get("prog"),
           "status": raw.get("status"), "reps_requested": K, "reps_done": n,
           "launch_s": [float(x) for x in (raw.get("wall_s") or [])],
           "launch_epoch_ms": [ep[0], ep[-1]] if len(ep) >= 2 else [0, 0],
           "kernel": {"cycles_max": (raw.get("hart0_cycles") or {}).get("max")},
           "problems": [], "stop_reason": ""}
    if raw.get("status") == "PASS":
        out["reps_consistent"] = "ok"
    elif short:
        out["reps_consistent"] = "ok"
        out["problems"] = [f"reps: {n} of {K} done"]
        out["stop_reason"] = "budget"
    else:
        why = (f"records_ok {raw.get('records_ok')} of {raw.get('participants')}, records_bad {raw.get('records_bad')}, "
               f"units {raw.get('units')} of {raw.get('units_expected')}, checked {raw.get('checked')}, mismatches "
               f"{raw.get('mismatches')}, expect_mismatches {raw.get('expect_mismatches')}, first_mismatch "
               f"'{raw.get('first_mismatch')}', launches {n} of {K}")
        out["reps_consistent"] = "bad"
        out["problems"] = ["checks: " + why] if raw else ["no JSON line from the ledger host"]
    return out


def burst_window(hj):
    """(lo_ms, hi_ms) of a burst from the reducer's host.json fields (launch_epoch_ms [the first launch's t0, the last's t1]), or None."""
    ep = (hj or {}).get("launch_epoch_ms") or []
    if len(ep) >= 2 and isinstance(ep[0], (int, float)) and isinstance(ep[-1], (int, float)) and 0 < ep[0] < ep[-1]:
        return int(ep[0]), int(ep[-1])
    return None


def clock_pass(samples, lo_ms, hi_ms, climb_s=CLIMB_S):
    """THE CLOCK RULE, live (E194.md 11): the live samples (t_ms, minion MHz) from the burst's first launch's start + climb_s to its last
    launch's end must read CLOCK_MHZ (800). Returns (verdict, words, n read): 'ok'; 'off' (one or more read another clock: the runner sets
    the pass aside, and a second such pass stops the session); 'unread' (no live sample in that window: flagged, reported; the scorer's
    rule reads it from the telemetry the pass keeps)."""
    w0 = lo_ms + int(round(climb_s * 1000))
    got = [m for t, m in samples if w0 <= t <= hi_ms]
    if not got:
        return "unread", f"the clock: no live sample from the burst's start + {climb_s:g} s to its end", 0
    off = [m for m in got if m != CLOCK_MHZ]
    if off:
        return "off", (f"the clock: {len(off)} of {len(got)} live samples from the burst's start + {climb_s:g} s to its end read "
                       f"{sorted(set(off))} MHz, not {CLOCK_MHZ}"), len(got)
    return "ok", f"the clock: {len(got)} live samples from the burst's start + {climb_s:g} s to its end, each {CLOCK_MHZ} MHz", len(got)


def reading(cfg, host_json_):
    """The pass's reading in words for the session log (E191's kit mechanics): PASS, SHORT (k of K launches, the host's own budget:
    scored on its launches) or FAILED RUN (not a datum). Nothing scored reads it."""
    h = host_json_ or {}
    if h.get("reps_consistent") == "bad" or (not h):
        return "FAILED RUN (not a datum)"
    pr = [str(x).split() for x in (h.get("problems") or []) if str(x).startswith("reps: ")]
    if pr and len(pr[0]) >= 4:
        return f"SHORT ({pr[0][1]} of {pr[0][3]} launches, the host's own budget: scored on its launches)"
    if h.get("status") == "PASS":
        return "PASS"
    return "FAILED RUN (not a datum)"


def _minshire(s):
    """temp_c.minshire as a list, or [] (fix-e194, verify-e194's nit 7: a line whose temp_c or minshire is not an object or a list reads as
    no reading, never an exception in the sampler's reader thread)."""
    t = s.get("temp_c") if isinstance(s, dict) else None
    ms = t.get("minshire") if isinstance(t, dict) else None
    return ms if isinstance(ms, list) else []


def die_of(s):
    ms = _minshire(s)
    return ms[0] if ms else None


def latch_of(s):
    ms = _minshire(s)
    return ms[2] if len(ms) > 2 else None


class Stops:
    """THE STOP LINES on live samples (E194.md 11). feed(sample, in_pass) returns 'stop' once, on the first sample that trips a line:
    E189's lines first (board at or above 65 W, or minshire[0] at or above 70 C, on any sample), then aifoundry2's own kept beside them
    (board strictly above 85 W on 3 samples in a row, a sample with no board reading starting the count again; minshire[0] or the latch
    minshire[2] at or above 80 C). There is no per-sample clock line: THE CLOCK RULE is read per pass (clock_pass). A test threshold (the
    stop-path test) is passed in."""

    def __init__(self, board_w=STOP_BOARD_W, die_c=STOP_DIE_C, a2_board_w=A2_BOARD_W, a2_board_n=A2_BOARD_N, a2_die_c=A2_DIE_C):
        self.board_w, self.die_c = board_w, die_c
        self.a2_board_w, self.a2_board_n, self.a2_die_c = a2_board_w, a2_board_n, a2_die_c
        self.run_above = 0
        self.stop = None
        self.events = []

    def feed(self, s, in_pass):
        acts = []
        bw = s.get("board_w") if isinstance(s, dict) else None
        die = die_of(s)
        latch = latch_of(s)
        bw, die, latch = (x if _num(x) else None for x in (bw, die, latch))   # fix-e194 (nit 7): a reading that is not a number is none
        if bw is not None and bw >= self.board_w and not self.stop:
            self.stop = f"board {bw} W at or above {self.board_w:g} W"
            acts.append("stop")
        if die is not None and die >= self.die_c and not self.stop:
            self.stop = f"minshire[0] {die} C at or above {self.die_c:g} C"
            acts.append("stop")
        if isinstance(bw, (int, float)) and bw > self.a2_board_w:
            self.run_above += 1
        else:
            self.run_above = 0
        if self.run_above >= self.a2_board_n and not self.stop:
            self.stop = f"board above {self.a2_board_w:g} W on {self.a2_board_n} samples in a row ({bw} W)"
            acts.append("stop")
        if not self.stop and ((die is not None and die >= self.a2_die_c) or (latch is not None and latch >= self.a2_die_c)):
            self.stop = (f"minshire[0] {die} C or the latch minshire[2] {latch} C at or above {self.a2_die_c:g} C")
            acts.append("stop")
        if acts:
            self.events.append({"t_ms": s.get("t_ms") if isinstance(s, dict) else None, "stop": self.stop, "in_pass": in_pass})
        return acts


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and x == x     # a number, never a bool or NaN


def sample_live(s):
    """A LIVE sample (E191's kit, fix-e191k2): one that carries every reading THE STOP LINES read - board_w, minshire[0] and the minion
    clock, each a number. Only a live sample keeps the sampler live and passes the die gate; any other line is kept in the telemetry and
    fed to the stop lines all the same."""
    if not isinstance(s, dict):
        return False
    m = s.get("mhz")
    return _num(s.get("board_w")) and _num(die_of(s)) and isinstance(m, dict) and _num(m.get("minion"))   # fix-e194 (nit 7): any shape


def config_ok(j):
    """The start config's line (E194.md 2): TDP 65 W, threshold 65 C, minion 600 MHz at rest (the identity's bounds are e194_ident's)."""
    return bool(j) and all(j.get(k) == v for k, v in CONFIG_LINE.items())


def selfcheck():
    p = plan()
    bad = []
    if not check_sequence(p):
        bad.append("the sequence differs from plan-e194.json's written order")
    ks = {k: p["configs"][k]["launches_K"] for k in ORDER}
    if ks != {"copy-zeros": 8, "copy-random": 8, "sha256": 9, "sort-sorted": 8, "sort-shuffled": 7, "sparse-parity": 9}:
        bad.append(f"K {ks}")
    for k in LEDGER:
        a = host_argv(k, p)
        if f"--launches {ks[k]}" not in " ".join(a) or "--card" not in a:
            bad.append(f"{k} argv {a}")
    if "--expect" not in host_argv("sha256", p):
        bad.append("sha256 without --expect")
    a = host_argv("sparse-parity", p, "X")
    if a[a.index("--reps") + 1] != "9" or "--budget" not in a:
        bad.append(f"sparse parity argv {a}")
    cb = json.dumps(p.get("card", {}))
    if p.get("seed") != 194 or "etsoc-shire0.lock" not in cb or "/dev/et0_mgmt" not in cb:
        bad.append("plan-e194.json's card block or seed")
    if p.get("die_gate", {}).get("gate_c") != DIE_GATE_C or p.get("die_gate", {}).get("band_c") != [DIE_LOW_C, DIE_GATE_C]:
        bad.append("the die gate is not plan-e194.json's (57 C, band 46-57)")
    cr = p.get("clock_rule", {})
    if cr.get("forecast_mhz") != CLOCK_MHZ or cr.get("climb_allowance_s") != CLIMB_S:
        bad.append("the clock rule is not plan-e194.json's (800 MHz from lo + 1.5 s)")
    sp = p.get("stops", {})
    a2 = sp.get("aifoundry2_lines", {})
    if (sp.get("board_w"), sp.get("minshire0_c"), a2.get("board_w_above"), a2.get("consecutive_samples"), a2.get("die_c")) != \
            (STOP_BOARD_W, STOP_DIE_C, A2_BOARD_W, A2_BOARD_N, A2_DIE_C):
        bad.append("the stop lines are not plan-e194.json's")
    raw = {"prog": "copy", "participants": 2048, "records_ok": 2048, "records_bad": 0, "units": 5, "units_expected": 5,
           "checked": 2048, "mismatches": 0, "expect_mismatches": 0, "launches": 6, "wall_s": [0.6] * 6,
           "launch_epoch_ms": [1, 2, 3, 4], "hart0_cycles": {"max": 524800000}, "status": "FAIL"}
    h = adapt_ledger(raw, 8)
    if not (h["problems"] == ["reps: 6 of 8 done"] and h["reps_consistent"] == "ok" and h["launch_epoch_ms"] == [1, 4]):
        bad.append(f"adapter short {h}")
    if not reading("copy-zeros", h).startswith("SHORT (6 of 8 launches"):
        bad.append(f"reading short {reading('copy-zeros', h)}")
    h2 = adapt_ledger(dict(raw, mismatches=1, first_mismatch="participant 7", launches=8), 8)
    if not (h2["reps_consistent"] == "bad" and h2["problems"][0].startswith("checks:")) or not reading("x", h2).startswith("FAILED RUN"):
        bad.append(f"adapter fail {h2}")
    h3 = adapt_ledger(dict(raw, launches=8, status="PASS"), 8)
    if not (h3["problems"] == [] and h3["reps_done"] == 8 and h3["status"] == "PASS") or reading("x", h3) != "PASS":
        bad.append(f"adapter pass {h3}")
    if reading("sparse-parity", {"status": "FAIL", "reps_consistent": "ok", "problems": ["reps: 7 of 9 done"]})[:5] != "SHORT" or \
            reading("sparse-parity", {}) != "FAILED RUN (not a datum)":
        bad.append("reading of sparse parity's own host.json")

    def smp(mhz=800, bw=30.0, die=55, latch=70):
        return {"t_ms": 1, "board_w": bw, "temp_c": {"minshire": [die, die - 1, latch]}, "mhz": {"minion": mhz}}
    st = Stops()
    if not (st.feed(smp(600), None) == [] and st.feed(smp(800), "x/p1") == [] and st.feed(smp(700), "x/p1") == [] and st.stop is None):
        bad.append("a clock reading tripped a stop line (the clock is THE CLOCK RULE's, per pass)")
    if not (Stops().feed(smp(bw=65.0), None) == ["stop"] and Stops().feed(smp(die=70), None) == ["stop"]
            and Stops().feed(smp(bw=64.99, die=69), "x/p1") == []):
        bad.append("E189's board or die line read wrong")
    st4 = Stops(board_w=1e9, die_c=1e9)
    seq = [st4.feed(smp(bw=86.0), "x"), st4.feed(smp(bw=86.0), "x"), st4.feed({"t_ms": 1, "temp_c": {"minshire": [50, 50, 70]}}, "x"),
           st4.feed(smp(bw=86.0), "x"), st4.feed(smp(bw=85.0), "x"), st4.feed(smp(bw=86.0), "x"), st4.feed(smp(bw=86.0), "x"),
           st4.feed(smp(bw=86.0), "x")]
    if seq != [[], [], [], [], [], [], [], ["stop"]] or "85 W on 3 samples in a row" not in (st4.stop or ""):
        bad.append(f"aifoundry2's 85 W x 3 line read wrong ({seq}, {st4.stop})")
    st5 = Stops(board_w=1e9, die_c=1e9)
    if st5.feed(smp(latch=79), None) != [] or st5.feed(smp(latch=80), None) != ["stop"] or "latch" not in (st5.stop or ""):
        bad.append("aifoundry2's 80 C line on the latch minshire[2] read wrong")
    if Stops(board_w=1e9, die_c=1e9).feed(smp(die=80, latch=70), None) != ["stop"]:
        bad.append("aifoundry2's 80 C line on minshire[0] read wrong")
    if Stops().feed(smp(latch=75), None) != []:
        bad.append("the latch minshire[2] was read against E189's 70 C line (it never is: E194.md 11)")
    # THE CLOCK RULE, live
    S = [(1000 + 100 * i, 600 if i < 9 else 800) for i in range(40)]           # lo 1000 ms: 600 MHz to 1.8 s, then 800 MHz to 4.9 s
    if clock_pass(S, 1000, 4900)[0] != "ok":
        bad.append(f"clock_pass on a climb inside 1.5 s: {clock_pass(S, 1000, 4900)}")
    S2 = [(t, 700 if t == 4000 else m) for t, m in S]
    if clock_pass(S2, 1000, 4900)[0] != "off" or "700" not in clock_pass(S2, 1000, 4900)[1]:
        bad.append("clock_pass on a step to 700 MHz after the climb")
    S3 = [(t, 600 if t <= 2600 else 800) for t, m in S]                        # climbs late, at 1.6 s
    if clock_pass(S3, 1000, 4900)[0] != "off" or clock_pass([(t, 600) for t, _ in S], 1000, 4900)[0] != "off":
        bad.append("clock_pass on a late climb or a burst at 600 MHz throughout")
    if clock_pass(S, 1000, 2400)[0] != "unread" or clock_pass(S, 1000, 4900, climb_s=0.05)[0] != "off":
        bad.append("clock_pass on a burst shorter than the climb, or with the desk's climb")
    if burst_window({"launch_epoch_ms": [5, 9]}) != (5, 9) or burst_window({"launch_epoch_ms": [0, 0]}) or burst_window({}):
        bad.append("burst_window")
    if not config_ok({"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 600}) or config_ok({"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600}) \
            or config_ok({}) or config_ok({"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 800}):
        bad.append("config_ok")
    e = device_env({"PATH": "/usr/bin", "ET_DEVICES": "0", "V3_DEVICE": "1"})
    if "ET_DEVICES" in e or "V3_DEVICE" in e or e.get("LD_LIBRARY_PATH") != "/opt/et/lib" or LOCK != "/run/lock/etsoc-shire0.lock":
        bad.append("device_env (ET_DEVICES and V3_DEVICE unset) or the lock")
    live_ok = sample_live(smp()) and sample_live(dict(smp(), board_w=0))
    no_board = dict(smp())
    no_board.pop("board_w")
    dead = [no_board, dict(smp(), board_w=None), dict(smp(), board_w="31.5"), dict(smp(), board_w=True), dict(smp(), board_w=float("nan")),
            dict(smp(), temp_c={"minshire": []}), dict(smp(), temp_c={}), dict(smp(), temp_c={"minshire": [None, 50, 52]}),
            dict(smp(), mhz={"noc": 1000}), dict(smp(), mhz={"minion": None}), {}, None, "x"]
    if not live_ok or any(sample_live(x) for x in dead):
        bad.append("sample_live")
    # the parser (desk/parser_e194.py runs it on the committed bytes; here, the forms)
    line = '{"ledger":1,"prog":"copy","width":32,"launches":1,"status":"PASS"}'
    split = '{"ledger":1,"prog":"copy","width":32Opening device 1\n,"launches":1,"status":"PASS"}\n'
    o1, r1 = host_json(line + "\n", "ledger")
    o2, r2 = host_json(split, "ledger")
    o3, r3 = host_json("Opening device 0\n" + line + "\nOpening device 0\n", "ledger")
    o4, r4 = host_json('{"ledger":1,"prog":"cut', "ledger")
    o5, r5 = host_json('{"a":1}\n', "ledger")
    o6, r6 = host_json('{"ledger":1,"x":[1,2]Opening device 1\nnoise line\n,"status":"PASS"}', "ledger")
    if not (o1 == json.loads(line) and r1["method"] == "whole line" and o2 == json.loads(line) and r2["method"] == "reassembled"
            and r2["dropped"] == ["Opening device 1"] and r2["runtime"] == [True] and o3 == json.loads(line) and r3["method"] == "whole line"
            and o4 == {} and r4["method"] == "none" and o5 == {} and r5["method"] == "none"
            and o6 == {"ledger": 1, "x": [1, 2], "status": "PASS"} and r6["dropped"] == ["Opening device 1", "noise line"]
            and r6["runtime"] == [True, False]):
        bad.append(f"host_json: {r1} {r2} {r3} {r4} {r5} {r6}")
    if host_json('SELFTEST PASS\n', "ledger")[1]["method"] != "none" or host_json('{"tdp_w":65}', "tdp_w")[0] != {"tdp_w": 65}:
        bad.append("host_json on a self-test's text or a config line")
    # fix-e194: the sampler's lines of any shape (verify-e194's nit 7): no exception, no reading
    odd = [dict(smp(), temp_c=[1, 2]), dict(smp(), temp_c={"minshire": 5}), dict(smp(), temp_c={"minshire": {"a": 1}}),
           dict(smp(), temp_c="hot"), dict(smp(), mhz=[800]), dict(smp(), mhz="800"), dict(smp(), board_w="86"), dict(smp(), board_w=[1]),
           dict(smp(), temp_c={"minshire": ["80", "x", "90"]}), [1, 2], 7]
    try:
        so = Stops(board_w=1e9, die_c=1e9)
        res = [(sample_live(x), die_of(x), latch_of(x), so.feed(x, None)) for x in odd]
        if any(r[0] for r in res) or any(r[3] for r in res) or so.stop is not None:
            bad.append(f"a sampler line of another shape read as live or tripped a stop line: {res}")
    except Exception as e:      # noqa: BLE001 - the point is that nothing raises
        bad.append(f"a sampler line of another shape raised {type(e).__name__}: {e}")
    if Stops().feed(dict(smp(), board_w=65.5), None) != ["stop"] or Stops().feed(dict(smp(), board_w="65.5"), None) != []:
        bad.append("E189's board line on a number, or a board_w that is not a number read as one")
    # fix-e194: THE HOST'S LINE, VERIFIED (verify-e194's finding 2): host_result
    argv = [LEDGER_HOST, "--card", "--kernel", LEDGER_ELF, "--launches", "1", "--prog", "copy", "--bytes", "64M", "--passes", "1",
            "--data", "random", "--width", "32"]
    head = ('{"ledger":1,"prog":"copy","device":"card","participants":2048,"seed":1,"bytes":67108864,"passes":1,"data":"random",'
            '"width":32')
    tail = (',"launches":1,"wall_s":[0.0064],"launch_epoch_ms":[1,2],"records_ok":2048,"records_bad":0,"units":67108864,'
            '"units_expected":67108864,"hart0_cycles":{"max":3,"min":2,"mean":2.5,"n":1024},"checked":2048,"mismatches":0,'
            '"expect_checked":0,"expect_mismatches":0,"first_mismatch":"","status":"PASS"}')
    whole = json.loads(head + tail)
    rows = {"whole": (head + tail + "\n", whole), "split": (head + "Opening device 1\n" + tail + "\n", whole),
            "runtime before and after": ("Opening device 0\n" + head + tail + "\nOpening device 0\n", whole),
            "a digit line merged into width": (head + "42\n" + tail + "\n", {}),
            "an e line merged": (head + "E+7\n" + tail + "\n", {}), "a dot line": (head + ".5 x\n" + tail + "\n", {}),
            "a lone brace line": (head + "}\n" + tail + "\n", {}), "an unknown line": (head + "Warning: x\n" + tail + "\n", {}),
            "a runtime line with more text": (head + "Opening device 1 now\n" + tail + "\n", {}),
            "a stale object": (head + tail + "\n" + head + "Opening device 1\n", {}),
            "another command's line": ((head + tail).replace('"width":32', '"width":64') + "\n", {}),
            "a field missing": ((head + tail).replace('"units":67108864,', "") + "\n", {}),
            "a span end missing": ((head + tail).replace("[1,2]", "[1]") + "\n", {}),
            "the head alone": (head + "Opening device 1\n", {}), "nothing": ("", {}),
            "a decoy line after it": (head + tail + '\n{"a decoy"\n', whole)}
    for name, (t, want) in rows.items():
        o, r = host_result(t, "ledger", argv)
        if o != want or (not want and (r.get("method") != "none" or not r.get("why"))):
            bad.append(f"host_result, {name}: read {str(o)[:60]} ({r.get('method')}, {str(r.get('why'))[:80]})")
    sargv = [SPP_HOST, "--n", "544", "--reps", "9", "--kernel", SPP_ELF]
    sj = {"workload": "sparseparity", "device": "silicon", "reps_requested": 9, "reps_done": 9, "launch_s": [0.5] * 9,
          "launch_epoch_ms": [1, 2], "kernel": {"cycles_max": 3}, "result": {"solved": True}, "status": "PASS"}
    if host_result(json.dumps(sj, separators=(",", ":")) + "\n", "spp", sargv)[0] != sj or \
            host_result(json.dumps(dict(sj, reps_requested=1), separators=(",", ":")) + "\n", "spp", sargv)[0]:
        bad.append("host_result on sparse parity's line, or on its line for another --reps")
    cfg = '{"tdp_w":65,"temp_threshold_c":65,"power_state":3,"power_state_name":"low_power","minion_mhz":600,"minion_mv":519}'
    if host_result(cfg + "\n", "config")[0] != json.loads(cfg) or \
            host_result(cfg.replace(',"minion_mhz"', 'Opening device 0\n,"minion_mhz"') + "\n", "config")[0] != json.loads(cfg) or \
            host_result(cfg.replace(':519}', ':51') + "9\n}\n", "config")[0]:
        bad.append("host_result on the config read (whole, split by a runtime line, a line merged into minion_mv)")
    return bad


def config_line(path):
    """fix-e194 (verify-e194's nit 6): the config read's object from its stdout file, as host_result reads it, printed compact on one line
    for step 7 (rb/s09_reads_e194.sh); nothing on stdout (and the reason on stderr, exit 1) when it cannot be read."""
    try:
        text = open(path, errors="replace").read()
    except OSError as e:
        print(f"config-line: {path} unreadable ({type(e).__name__})", file=sys.stderr)
        return 1
    obj, rec = host_result(text, "config")
    if not obj:
        print(f"config-line: no config object read ({rec.get('why')})", file=sys.stderr)
        return 1
    print(json.dumps(obj, separators=(",", ":")))
    if rec.get("method") != "whole line" or rec.get("other_lines"):
        print(f"config-line: {host_json_words(rec) or 'read whole'}; {rec.get('other_lines')} other line(s) on its stdout", file=sys.stderr)
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--config-line":
        sys.exit(config_line(sys.argv[2]))
    b = selfcheck()
    print("E194-COMMON SELF-CHECK " + ("PASS" if not b else "FAIL: " + "; ".join(b)))
    sys.exit(0 if not b else 1)
