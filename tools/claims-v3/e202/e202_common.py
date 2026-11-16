#!/usr/bin/env python3
"""E202's kit (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum): what the box runner, the doubles, the collector and the
desk tests share. Python's own modules only (aifoundry3's system python3 3.12.3; the desk's /usr/bin/python3 3.12.3, -I -B).

It reads the registration's plan-e202.json and forecast-e202.json and never changes them, and calls plan_e202.r_rule (the registered R
rule, E202.md 8.3) unchanged. It adds, each stated in KIT.md section 4 where the registration leaves the reading to the kit:
  - THE HOST'S COMMAND LINES (E202.md 8.2 and 8.4; plan-e202.json > smoke): the five R = 1 smoke processes in the registered order,
    and the bursts, with the box's paths (build_e202.sh's build/e202mnist, files_e202.sh's checked inputs in build/e202files);
  - THE HOST'S RESULT, read from the host's own --out file ONLY (E202.md 7.1; the lesson of E191's first session, round log 116): a
    runtime line printed into the host's stdout can never reach it; a file that does not parse whole is no result, never a head;
  - THE ADAPTER: the host's --out record into the reducer's host.json fields, so that workloads/sparseparity/tools/energy_reduce.py,
    unchanged, reduces a burst (one launch of R passes) as one solve;
  - THE ORDER (E202.md 8.4-8.5): the scored pair's T Z Z T T Z Z T (K = 4 each), then the dram pair T Z Z T (K = 2 each, REPORTED)
    only when the scp pair is scored;
  - THE STOP LINES (E202.md 9) on every live sample: board at or above 65 W; minshire[0] at or above 70 C; THE CLOCK (every sample at
    600 MHz: the first sample off it sets its burst aside, a second anywhere in the session stops it); a telemetry line older than 1 s;
  - the cap (no burst starts after 33 card-minutes from the first card command; the session ends by 35), the die gate (60 C, at most
    10 minutes; below 52 C labelled, never a block), and the kit's stop K1 (a launch that did not finish ends the session);
  - et-who's holder lines of another login, and the start config's check (TDP 0 W, threshold 65 C, minion 600 MHz, as found).
Fixed before the land (fix-e202, Mon 16 Nov 2026, answering verify-e202's findings; no forecast, band, scored rule or threshold changed):
  - ET-WHO UNREADABLE (finding 1, E191's rule from fix-e191k): et-who is read only when it exits 0 and answers with a holder line or its
    no-holder sentence; anything else (its privileged helper refused, a text with neither, a missing command) is UNREADABLE, read as a
    holder: a refusal before the first card command, a stop before a start, the closing config read not sent (etwho_unreadable);
  - K1 WIDER (finding 5): also a host that died (rc 125 or more: a signal, or timeout's own failures), and a host that wrote no --out
    record after its device was opened ("device ready" on its stderr), may leave a hung hart: the session ends;
  - THE HOST'S TIMEOUT CAP ON THE R RULE (finding 7): the registered rule's R is kept only if its predicted launch is at most the host's own
    launch timeout less 0.5 s (main.cpp: int(min(8 s, 2 x its guard model + 1.5 s, the --budget time left at the launch)), the time left
    read from the arm's own smoke); else the largest allowed R under both ceilings; none: no burst for the arm. Never a larger R than the
    registered rule's; at the forecast (3.0 s at the point, 4.6 s at the slow end, R = 96, the cap 7.5 s) it changes nothing.
SPDX-License-Identifier: Apache-2.0
"""
import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
PLAN = os.path.join(HERE, "plan-e202.json")
FORECAST = os.path.join(HERE, "forecast-e202.json")
BOX = "aifoundry3"
NODES = ("/dev/et0_mgmt", "/dev/et0_ops")                   # exactly card 0's two nodes (aifoundry3 has one card)
LOCK = "/run/lock/etsoc-shire0.lock"
GUARD = "tools/claims-v3/e128/ettelem_guard.sh"             # E128's allow-list in front of build/ettelem/ettelem (READs only)
BUILD = "build/e202mnist"                                    # build_e202.sh's build directory on the box (new, E202's own)
HOST = BUILD + "/host/mnistmlp_host"
ELF = BUILD + "/kernel/mnistmlp.elf"
FILES = "build/e202files"                                    # files_e202.sh's checked inputs on the box
MNIST = FILES + "/mnist"
WDIR = FILES + "/files"
PINS = WDIR + "/PINS-SHA256SUMS"                             # a copy of workloads/mnistmlp/model/PINS-SHA256SUMS (the host's --pins)
TEXT_PIN = "ace7bcb04536329f1d75135446049c442b9f4b65f726083f7623b959b279d82d"   # E202.md 2: the kernel's .text, both boxes
ELF_A3 = "0f74ff0d35d1114dddb92ade81b5d549b837fa2512093908adf60d40358a0a19"     # E202.md 2: the ELF as built on aifoundry3 (reported)
IDLE_BEFORE_S, IDLE_AFTER_S, EVERY_MS = 8.0, 10.0, 100      # E202.md 8.4: 8 s at rest, ONE host process, 10 s at rest; 10 Hz
HOST_TIMEOUT_S = 10                                          # every device-opening process under `timeout 10`, never -k
ANCHOR_S = 120                                               # two idle anchors of 2 minutes (E202.md 8.1 and 8.6)
CAP_BURST_START_S = 33 * 60                                  # E202.md 8: no burst starts after 33 card-minutes
CAP_S = 35 * 60                                              # the session ends by 35
CLOSE_S = 45                                                 # the closing's share of the last seconds before 35:00: et-who
                                                             # (timeout 20) and the closing config read (timeout 10) and the bounds
DIE_GATE_C, DIE_GATE_WAIT_S, DIE_LOW_C = 60, 600, 52         # E202.md 8 and 9
STOP_BOARD_W, STOP_DIE_C, CLOCK_MHZ, STALE_S = 65.0, 70.0, 600, 1.0   # E202.md 9
GROUPS_PER_PASS, GROUPS_PER_TEST_PASS, OPS_PER_GROUP = 3750, 625, 10892
R_ALLOWED = (16, 32, 48, 64, 80, 96)
CONFIGS = ("trained", "random")
STAGES = ("scp", "dram")
SMOKE = (  # E202.md 8.2 / plan-e202.json > smoke > processes, in its order: (arm, weights, stage, split, debug logits, test accuracy)
    ("T-scp", "trained", "scp", "train", True, False),
    ("Z-scp", "random", "scp", "train", True, False),
    ("T-dram", "trained", "dram", "train", True, False),
    ("Z-dram", "random", "dram", "train", True, False),
    ("ACC", "trained", "scp", "test", False, True),
)
SCORED_ORDER = ("trained", "random", "random", "trained", "trained", "random", "random", "trained")   # T Z Z T T Z Z T, K = 4
REPORTED_ORDER = ("trained", "random", "random", "trained")                                          # T Z Z T, K = 2
DEV_COMM = r"_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$|^Runner\.Worker$"   # lib.sh's, as E189's runner
DESK_VARS = ("E202_FAKE", "E202_SI", "V3_DRY", "E202_DESK")  # a variable whose name starts so is a desk test's: refused on a real run
NO_HOLDER = "No process holds an ET-SoC-1 device node or card lock."   # et-who's (et-holders') own sentence when nothing is held
# the mnistmlp host's own launch guard (workloads/mnistmlp/host/main.cpp, modelSeconds() and the launch's timeoutS), fix-e202 finding 7
HOST_GUARD_CYCLES_PER_ROUND = 10892 * 700.0 + 449 * 1500.0   # 700 cycles a TensorIMA8A32, 1,500 a chunk, on the busiest shire
HOST_GUARD_PLUS_S = 0.002
HOST_TIMEOUT_MAX_S, HOST_BUDGET_S, HOST_MAX_KERNEL_S = 8.0, 9.5, 6.0
HOST_CAP_MARGIN_S = 0.5


def plan():
    with open(PLAN) as f:
        return json.load(f)


def forecast():
    with open(FORECAST) as f:
        return json.load(f)


def plan_module():
    """The registration's plan_e202.py, imported by path and unchanged (its r_rule and busiest are the registered R rule)."""
    spec = importlib.util.spec_from_file_location("plan_e202", os.path.join(HERE, "plan_e202.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def cfg_key(weights, stage):
    return f"{weights}-{stage}"


def images(split):
    return MNIST + ("/train-images-idx3-ubyte" if split == "train" else "/t10k-images-idx3-ubyte")


def labels(split):
    return MNIST + ("/train-labels-idx1-ubyte" if split == "train" else "/t10k-labels-idx1-ubyte")


def host_argv(weights, stage, split, R, out, debug=False, acc=False, labels_out=None):
    """One host process's command line (without `timeout 10`), from the box tree's root: the mnistmlp host on the card, R passes,
    every input pinned (--pins), its result to its own --out file."""
    tag = "train" if split == "train" else "test"
    a = [HOST, "--card", "--images", images(split), "--weights", f"{WDIR}/mnist-int8-{weights}.mlpw",
         "--expect", f"{WDIR}/expect-{weights}-{tag}.mlpe", "--split", split, "--passes", str(int(R)), "--stage", stage,
         "--pins", PINS, "--kernel", ELF, "--out", out]
    if debug:
        a += ["--debug-logits", "--expect-logits", f"{WDIR}/logits-{weights}-{tag}.mlpl"]
    if acc:
        a += ["--true-labels", labels(split)]
    if labels_out:
        a += ["--labels-out", labels_out]
    return a


def smoke_argv(arm, out, labels_out=None):
    for a, w, st, sp, dbg, acc in SMOKE:
        if a == arm:
            return host_argv(w, st, sp, 1, out, debug=dbg, acc=acc, labels_out=labels_out)
    raise KeyError(arm)


def burst_sequence(scored_stage, report_dram):
    """THE ORDER: [(config key, burst k, order index, label)], the scored pair's T Z Z T T Z Z T and, when the scp pair is scored and
    report_dram, the dram pair's T Z Z T (REPORTED). Never re-drawn."""
    seq, seen, idx = [], {}, 0
    for w in SCORED_ORDER:
        key = cfg_key(w, scored_stage)
        seen[key] = seen.get(key, 0) + 1
        idx += 1
        seq.append((key, seen[key], idx, "scored"))
    if scored_stage == "scp" and report_dram:
        for w in REPORTED_ORDER:
            key = cfg_key(w, "dram")
            seen[key] = seen.get(key, 0) + 1
            idx += 1
            seq.append((key, seen[key], idx, "REPORTED"))
    return seq


def host_model_s(R, pm=None):
    """The mnistmlp host's own guard model of a launch of R passes (main.cpp modelSeconds(): 700 cycles a TensorIMA8A32 and 1,500 a
    chunk on the busiest shire's rounds at 600 MHz, plus 2 ms); its launch timeout and its refusals read it."""
    pm = pm or plan_module()
    return pm.busiest(R) * HOST_GUARD_CYCLES_PER_ROUND / 600e6 + HOST_GUARD_PLUS_S


def host_timeout_s(R, pm=None, left_s=None):
    """(the host's launch timeout in whole seconds, its guard model): main.cpp's timeoutS = int(min(8 s, 2 x model + 1.5 s, the
    --budget time left at the launch)); left_s None reads the first two terms only."""
    m = host_model_s(R, pm)
    t = min(HOST_TIMEOUT_MAX_S, 2.0 * m + 1.5)
    if left_s is not None:
        t = min(t, left_s)
    return int(t), m


def r_for(raw, pm=None, left_s=None):
    """THE R RULE (E202.md 8.3, plan_e202.r_rule, unchanged) on an arm's R = 1 smoke record, then THE HOST'S TIMEOUT CAP (fix-e202,
    verify-e202's finding 7): (R or None, predicted kernel seconds a launch at each allowed R, why, detail). The registered rule's R is
    kept only if its predicted launch is at most the host's own timeout less 0.5 s and the host would not refuse it (its guard over 6 s,
    or less time left than its guard plus 0.5 s); else the largest smaller allowed R that passes; None (no burst for the arm) when the
    smoke record lacks its cycle counts, no allowed R fits the 6 s ceiling, or none passes the cap. left_s: the --budget time left at
    the launch, read from the arm's own smoke (9.5 s less its launch's start after the process's start); None reads the model terms
    only. Never a larger R than the registered rule's."""
    pm = pm or plan_module()
    if not raw:
        return None, {}, "no smoke record", {}
    w = (raw.get("work_cycles") or {}).get("max")
    c = raw.get("copy_cycles_max")
    if not isinstance(w, (int, float)) or w <= 0 or not isinstance(c, (int, float)) or c < 0:
        return None, {}, f"the smoke record has no work_cycles.max / copy_cycles_max ({w}, {c})", {}
    R0, pred = pm.r_rule(w, c)
    detail = {"R_registered_rule": R0, "left_s": None if left_s is None else round(left_s, 3), "cap": {}}
    if not R0:
        return None, pred, "no allowed R fits the 6 s ceiling", detail
    chosen = None
    for R in sorted(R_ALLOWED, reverse=True):
        if R > R0:
            continue
        to, m = host_timeout_s(R, pm, left_s)
        cap = to - HOST_CAP_MARGIN_S
        refuse = m > HOST_MAX_KERNEL_S or (left_s is not None and left_s < m + 0.5)
        detail["cap"][str(R)] = {"predicted_s": round(pred[R], 4), "host_timeout_s": to, "cap_s": cap, "host_guard_s": round(m, 4),
                                 "host_would_refuse": refuse}
        if pred[R] <= cap and not refuse:
            chosen = R
            break
    detail["R_kit"] = chosen
    if chosen is None:
        return None, pred, (f"the host's timeout cap: the registered rule's R {R0} and every smaller allowed R predict a launch past "
                            f"the host's own timeout less {HOST_CAP_MARGIN_S:g} s (or the host would refuse it)"), detail
    if chosen != R0:
        c0 = detail["cap"][str(R0)]
        return chosen, pred, (f"the host's timeout cap: R {R0} predicts {pred[R0]:.2f} s against its timeout {c0['host_timeout_s']} s "
                              f"less {HOST_CAP_MARGIN_S:g} s{' (the host would refuse it)' if c0['host_would_refuse'] else ''}: "
                              f"R {chosen} kept"), detail
    return chosen, pred, "", detail


def left_from_smoke(raw, t0_process_ms):
    """The --budget time left at a launch, read from a smoke process: 9.5 s less (its launch's start, the host's own mark, less the
    runner's mark just before it started the process); the smoke's set-up (it reads the debug logits too) is at least a burst's, so
    this under-reads a burst's time left (the stricter side). None when the record has no launch mark."""
    ep = (raw or {}).get("launch_epoch_ms")
    if not (isinstance(ep, list) and len(ep) == 2 and _num(ep[0])) or not _num(t0_process_ms):
        return None
    return HOST_BUDGET_S - max(0.0, (ep[0] - t0_process_ms) / 1000.0)


def read_result(path, device="card"):
    """THE HOST'S RESULT from its own --out file (never its stdout): (record, why). The host writes one JSON line there and repeats
    it on stdout; this reads the file's LAST line that starts with '{' and parses whole. A file with no such line, a line that does
    not parse (a print cut inside it), a record that is not the mnistmlp host's, or one from another device is no result: (None, why)."""
    try:
        with open(path, "rb") as f:
            body = f.read()
    except OSError:
        return None, "no host result file"
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError:
        return None, "the host result file is not text"
    lines = [ln for ln in text.splitlines() if ln.startswith("{")]
    if not lines:
        return None, "the host result file holds no JSON line"
    try:
        j = json.loads(lines[-1])
    except ValueError:
        return None, "the host result file's line does not parse whole (cut)"
    if not isinstance(j, dict) or j.get("mnistmlp") != 1:
        return None, "not an mnistmlp host record"
    if device and j.get("device") != device:
        return None, f"a record of device {j.get('device')!r}, not {device!r}"
    return j, ""


def complete(raw):
    """The host's launch record carries every field the gate, the R rule, the adapter and the scorer read, each of its type: status and
    core_status PASS or FAIL, logits_status PASS, FAIL or NOT CHECKED, launch_ok a bool, launch_epoch_ms two numbers, wall_s, groups_done,
    pad_groups, ops, tensor_error_or, copy_cycles_max and passes numbers, hart0_cycles.max and work_cycles.max numbers. A record that lacks
    one (a REFUSED record before the device, a host from before core_status, a field renamed) is never a gate's pass nor a burst's datum."""
    if not isinstance(raw, dict) or raw.get("status") not in ("PASS", "FAIL") or raw.get("core_status") not in ("PASS", "FAIL"):
        return False
    if raw.get("logits_status") not in ("PASS", "FAIL", "NOT CHECKED") or not isinstance(raw.get("launch_ok"), bool):
        return False
    ep = raw.get("launch_epoch_ms")
    if not (isinstance(ep, list) and len(ep) == 2 and all(_num(x) for x in ep)):
        return False
    if not all(_num(raw.get(k)) for k in ("wall_s", "groups_done", "pad_groups", "ops", "tensor_error_or", "copy_cycles_max", "passes")):
        return False
    return all(isinstance(raw.get(k), dict) and _num(raw[k].get("max")) for k in ("hart0_cycles", "work_cycles"))


def core_pass(raw):
    """An arm's smoke gate (E202.md 7.2, E202-R0): a complete record reading core_status PASS (every record, label line, checksum,
    discard line and operation count; tensor_error 0); a logits-only failure is recorded, never a gate failure."""
    return complete(raw) and raw.get("core_status") == "PASS" and raw.get("tensor_error_or") == 0 and raw.get("launch_ok") is True


def burst_good(raw, R):
    """The host's half of 'a burst counts' (E202.md 7.2): status and core PASS, groups = 3,750 R, no padding, ops = 3,750 R x 10,892."""
    return (complete(raw) and raw.get("status") == "PASS" and raw.get("core_status") == "PASS"
            and raw.get("groups_done") == GROUPS_PER_PASS * R and raw.get("pad_groups") == 0
            and raw.get("ops") == GROUPS_PER_PASS * R * OPS_PER_GROUP)


def did_not_finish(raw, rc, err_text):
    """THE KIT'S STOP K1: a launch that did not finish (the host's own 'kernel did not finish' line, or `timeout 10`'s rc 124 cutting
    the process) may leave a hung hart: the session ends (nothing further starts; the card is never reset). fix-e202 (verify-e202's
    finding 5): also a host that died (rc 125 or more: a signal such as 134 or 139, or timeout's own 125-127), and a host that left no
    --out record after its device was opened (its "device ready" line on stderr, printed before the launch): the same reason applies."""
    err = err_text or ""
    if not isinstance(rc, int):
        return True
    return rc == 124 or rc >= 125 or "kernel did not finish" in err or (raw is None and "device ready" in err)


def adapt(raw, why=""):
    """THE ADAPTER: the host's --out record -> the reducer's host.json (energy_reduce.py reads reps_done, reps_requested, launch_s,
    launch_epoch_ms, status, problems, reps_consistent): one launch of R passes is one solve; launch_epoch_ms = the host's own launch
    marks [t0, t1]; launch_s = [wall_s]; status as the host said it; a failed or missing record: reps_consistent 'bad' (the reducer
    then fails the burst: no datum, never a failed prediction)."""
    raw = raw or {}
    ok = raw.get("launch_ok") is True
    ep = raw.get("launch_epoch_ms") or []
    out = {"adapter": "e202_common.adapt (KIT.md section 4)", "status": raw.get("status"), "reps_requested": 1,
           "reps_done": 1 if ok else 0,
           "launch_s": [float(raw["wall_s"])] if ok and isinstance(raw.get("wall_s"), (int, float)) else [],
           "launch_epoch_ms": [ep[0], ep[1]] if ok and len(ep) == 2 else [0, 0],
           "kernel": {"cycles_max": (raw.get("hart0_cycles") or {}).get("max")}, "problems": [], "stop_reason": "",
           "passes": raw.get("passes"), "stage": raw.get("stage"), "weights_name": raw.get("weights_name")}
    if raw.get("status") == "PASS" and ok and complete(raw):
        out["reps_consistent"] = "ok"
    elif raw and raw.get("status") == "PASS" and ok:
        out["reps_consistent"] = "bad"
        out["problems"] = ["the host's record is incomplete (a field the gate or the scorer reads is missing or of another type)"]
    else:
        out["reps_consistent"] = "bad"
        out["problems"] = ["checks: status %s, core %s, launch_ok %s, first_mismatch '%s'" % (
            raw.get("status"), raw.get("core_status"), raw.get("launch_ok"), raw.get("first_mismatch"))] if raw else \
            ["no host result: " + (why or "none")]
    return out


def config_ok(j):
    """The start config as found on aifoundry3 card 0 (E202.md 3; k6's step 7 gate): TDP 0 W, threshold 65 C, minion 600 MHz."""
    return bool(j) and j.get("tdp_w") == 0 and j.get("temp_threshold_c") == 65 and j.get("minion_mhz") == 600


def config_line(text):
    """The guard's `config` output: its last line that starts with '{' and parses whole, else {} (a cut line is no reading)."""
    for ln in reversed((text or "").splitlines()):
        if ln.startswith("{"):
            try:
                j = json.loads(ln)
                return j if isinstance(j, dict) else {}
            except ValueError:
                return {}
    return {}


def sample_line(raw):
    """One sampler line: a dict when it starts with '{', parses whole, and carries every field the stop lines and the reducer read
    (t_ms, board_w, sp.board_avg_w and the three rails, temp_c.minshire's three readings, mhz.minion), each a number; else None. A line
    cut or altered by a print (a key renamed inside it) is lost, never read as a sample (the real-bytes test, B4)."""
    if not raw or not raw.startswith("{"):
        return None
    try:
        s = json.loads(raw)
    except ValueError:
        return None
    if not isinstance(s, dict) or not _num(s.get("t_ms")) or not _num(s.get("board_w")):
        return None
    sp, tc, mh = s.get("sp"), s.get("temp_c"), s.get("mhz")
    if not (isinstance(sp, dict) and _num(sp.get("board_avg_w"))
            and all(isinstance(sp.get(k), list) and sp[k] and _num(sp[k][0]) for k in ("minion_w", "sram_w", "noc_w"))):
        return None
    if not (isinstance(tc, dict) and isinstance(tc.get("minshire"), list) and len(tc["minshire"]) >= 3
            and all(_num(x) for x in tc["minshire"][:3])):
        return None
    if not (isinstance(mh, dict) and _num(mh.get("minion"))):
        return None
    return s


def etwho_holders(text, me):
    """et-who's holder lines of ANOTHER login (a /dev/et... or lock: line whose second word is not our login): their count. Ours
    (the session's own card lock) never counts. Lines are counted, never written anywhere."""
    n = 0
    for ln in (text or "").splitlines():
        f = ln.split()
        if len(f) > 1 and (f[0].startswith("/dev/et") or f[0].startswith("lock:")) and f[1] != me:
            n += 1
    return n


def etwho_unreadable(rc, text):
    """'' when et-who's answer can be read: it exited 0 AND answered with a holder line (any login's) or its no-holder sentence; else
    why (fix-e202, verify-e202's finding 1; E191's rule, fix-e191k). A plain et-who asks its privileged helper (et-holders), which exits 0
    whether or not the card is held, so any other exit means the read failed: an unread holder rule is never read as "no holder"."""
    lines = (text or "").splitlines()
    if rc != 0:
        return f"et-who unreadable (rc {rc}{', nothing on its stdout' if not [x for x in lines if x.strip()] else ''})"
    rows = [ln.split() for ln in lines if (ln.startswith("/dev/et") or ln.startswith("lock:")) and len(ln.split()) > 1]
    if not rows and NO_HOLDER not in [x.strip() for x in lines]:
        return "et-who unreadable (rc 0, but neither a holder line nor its no-holder sentence)"
    return ""


def die_of(s):
    return ((s or {}).get("temp_c") or {}).get("minshire", [None])[0]


class Stops:
    """THE STOP LINES on live samples (E202.md 9). feed(sample, in_burst, age_s) returns the actions, in order: 'set-aside' (the first
    sample off 600 MHz, when it falls in a burst: that burst is set aside), 'stop' (board >= 65 W, minshire[0] >= 70 C, a second sample
    off 600 MHz anywhere in the session, or a line older than 1 s at its arrival). THE CLOCK LINE counts EVERY live sample of the
    session, in a burst or not (E202.md 9: "every sample at 600 MHz; the first sample off it sets its burst aside, a second stops the
    session"): a first sample off it outside a burst sets nothing aside (recorded); the second, wherever it falls, stops the session.
    (E189's kit read its own words, "in any pass", as counting in-pass samples only; E202's words name every sample: the stricter
    reading, never looser.) stale() is the watchdog's: no line for more than 1 s. Test thresholds come in for the stop-path test."""

    def __init__(self, board_w=STOP_BOARD_W, die_c=STOP_DIE_C, clock_mhz=CLOCK_MHZ, stale_s=STALE_S):
        self.board_w, self.die_c, self.clock_mhz, self.stale_s = board_w, die_c, clock_mhz, stale_s
        self.off_clock = 0
        self.stop = None
        self.events = []

    def feed(self, s, in_burst, age_s=None):
        acts = []
        bw = s.get("board_w")
        die = die_of(s)
        mhz = (s.get("mhz") or {}).get("minion")
        if isinstance(bw, (int, float)) and bw >= self.board_w and not self.stop:
            self.stop = f"board {bw} W at or above {self.board_w:g} W"
            acts.append("stop")
        if isinstance(die, (int, float)) and die >= self.die_c and not self.stop:
            self.stop = f"minshire[0] {die} C at or above {self.die_c:g} C"
            acts.append("stop")
        if isinstance(mhz, (int, float)) and mhz != self.clock_mhz:
            self.off_clock += 1
            self.events.append({"t_ms": s.get("t_ms"), "minion_mhz": mhz, "n": self.off_clock, "in_burst": in_burst})
            if in_burst:
                acts.append("set-aside")       # its burst is set aside (the first by the words; a later one too, the stricter)
            if self.off_clock >= 2 and not self.stop:
                self.stop = f"a second sample off {self.clock_mhz} MHz in the session ({mhz} MHz)"
                acts.append("stop")
        if age_s is not None and age_s > self.stale_s and not self.stop:
            self.stop = f"a telemetry line {age_s:.3f} s old at its arrival (the line is older than {self.stale_s:g} s)"
            acts.append("stop")
        return acts

    def stale(self, gap_s):
        if gap_s > self.stale_s and not self.stop:
            self.stop = f"no telemetry line for {gap_s:.2f} s (older than {self.stale_s:g} s)"
            return True
        return False


def selfcheck():
    bad = []
    p = plan()
    pm = plan_module()
    if [x["arm"] for x in p["smoke"]["processes"]] != [s[0] for s in SMOKE]:
        bad.append("the smoke's arms differ from plan-e202.json")
    for x, s in zip(p["smoke"]["processes"], SMOKE):
        words = x["args"].split()
        a = smoke_argv(s[0], "o.json")
        if ("--stage" in words and words[words.index("--stage") + 1] != s[2]) or words[words.index("--split") + 1] != s[3] \
                or ("--debug-logits" in words) != s[4] or ("--true-labels" in words) != s[5] \
                or words[words.index("--weights") + 1] != s[1] or a[a.index("--passes") + 1] != "1" or "--card" not in a:
            bad.append(f"smoke {s[0]}: {a} against {x['args']}")
    if list(p["bursts"]["scored"]["order"]) != list(SCORED_ORDER) or list(p["bursts"]["reported"]["order"]) != list(REPORTED_ORDER):
        bad.append("the burst orders differ from plan-e202.json")
    if p["bursts"]["scored"]["K"] != 4 or p["bursts"]["reported"]["K"] != 2:
        bad.append("K differs")
    seq = burst_sequence("scp", True)
    if [s[0] for s in seq] != ["trained-scp", "random-scp", "random-scp", "trained-scp"] * 2 + \
            ["trained-dram", "random-dram", "random-dram", "trained-dram"] or [s[1] for s in seq[:8]] != [1, 1, 2, 2, 3, 3, 4, 4]:
        bad.append(f"sequence {seq}")
    if len(burst_sequence("dram", True)) != 8 or len(burst_sequence("scp", False)) != 8:
        bad.append("the dram-scored or no-report sequence")
    if list(pm.R_ALLOWED) != list(R_ALLOWED) or p["R_rule"]["ceiling_kernel_s"] != 6:
        bad.append("the R rule's allowed set")
    # the R rule at the forecast's point (busiest shire's 4 rounds at R = 1): R = 96
    fc = forecast()
    t96 = fc["configs"]["trained-scp"]["seconds"]["launch_R96"]["point"]
    w1 = t96 / 352.0 * 4 * 600e6
    R, pred, why, det = r_for({"work_cycles": {"max": w1}, "copy_cycles_max": 89119})
    if R != 96 or det.get("R_registered_rule") != 96:
        bad.append(f"the R rule at the forecast point: {R} {why}")
    R2, _, _, _ = r_for({"work_cycles": {"max": w1 * 2.2}, "copy_cycles_max": 89119})
    if R2 != 80:      # t_round 2.2 x 8.524 ms: R 96 gives 6.6 s, R 80 (293 rounds) 5.49 s
        bad.append(f"the R rule at 2.2x the point: {R2}")
    if r_for({"work_cycles": {"max": w1 * 40}, "copy_cycles_max": 0})[0] is not None or r_for({})[0] is not None:
        bad.append("the R rule with nothing that fits, or no record")
    # fix-e202 (finding 7): the host's own timeouts (main.cpp): 8 s at R 64-96, 6 s at R 48, 4 s at R 32, 3 s at R 16
    if [host_timeout_s(r, pm)[0] for r in R_ALLOWED] != [3, 4, 6, 8, 8, 8]:
        bad.append(f"the host's timeouts {[host_timeout_s(r, pm)[0] for r in R_ALLOWED]}")
    wc = 0.0325 * 4 * 600e6                # a 32.5 ms round: the registered rule picks R 48 at 5.72 s, past its 6 s timeout less 0.5 s
    R3, p3, why3, det3 = r_for({"work_cycles": {"max": wc}, "copy_cycles_max": 89119})
    if not (det3.get("R_registered_rule") == 48 and R3 == 16 and "the host's timeout cap" in why3):
        bad.append(f"the cap at a 32.5 ms round: rule {det3.get('R_registered_rule')}, kit {R3}, {why3}")
    R4, _, why4, det4 = r_for({"work_cycles": {"max": 0.045 * 4 * 600e6}, "copy_cycles_max": 0})   # 45 ms: rule R 32, nothing under the cap
    if not (det4.get("R_registered_rule") == 32 and R4 is None and "the host's timeout cap" in why4):
        bad.append(f"the cap at a 45 ms round: rule {det4.get('R_registered_rule')}, kit {R4}")
    R5, _, why5, _ = r_for({"work_cycles": {"max": w1}, "copy_cycles_max": 89119}, left_s=5.0)   # 4.5 s of set-up: R 96 refused by the host
    if R5 != 80 or "would refuse" not in why5:
        bad.append(f"the cap with 5.0 s left at the launch: {R5} {why5}")
    if left_from_smoke({"launch_epoch_ms": [11500, 14500]}, 10000) != 8.0 or left_from_smoke({}, 1) is not None:
        bad.append("left_from_smoke")
    raw = {"mnistmlp": 1, "device": "card", "launch_ok": True, "wall_s": 3.01, "launch_epoch_ms": [1000, 4010],
           "hart0_cycles": {"max": 1800000000}, "work_cycles": {"max": 1790000000}, "copy_cycles_max": 89119, "status": "PASS",
           "core_status": "PASS", "logits_status": "NOT CHECKED", "tensor_error_or": 0, "groups_done": 360000, "pad_groups": 0,
           "ops": 360000 * 10892, "passes": 96}
    h = adapt(raw)
    if not (h["reps_done"] == 1 and h["launch_epoch_ms"] == [1000, 4010] and h["launch_s"] == [3.01] and h["reps_consistent"] == "ok"):
        bad.append(f"adapter pass {h}")
    h2 = adapt(dict(raw, status="FAIL", core_status="FAIL", first_mismatch="label line 7 labels"))
    if not (h2["reps_consistent"] == "bad" and h2["problems"][0].startswith("checks:")):
        bad.append(f"adapter fail {h2}")
    h3 = adapt(None, "no host result file")
    if not (h3["reps_done"] == 0 and h3["reps_consistent"] == "bad" and "no host result" in h3["problems"][0]):
        bad.append(f"adapter none {h3}")
    if not burst_good(raw, 96) or burst_good(dict(raw, pad_groups=26), 96) or burst_good(raw, 64) \
            or burst_good({k: v for k, v in raw.items() if k != "launch_epoch_ms"}, 96):
        bad.append("burst_good")
    if adapt({k: v for k, v in raw.items() if k != "work_cycles"})["reps_consistent"] != "bad":
        bad.append("the adapter took an incomplete record")
    if not core_pass(dict(raw, logits_status="FAIL", status="FAIL")) or core_pass(dict(raw, core_status="FAIL")):
        bad.append("core_pass: a logits-only failure must pass the gate")
    if not did_not_finish({}, 124, "") or not did_not_finish({}, 1, "kernel did not finish within 8 s, aborting the stream") \
            or did_not_finish({}, 1, "stream error: x"):
        bad.append("K1")
    # fix-e202 (finding 5): a host that died, or left no record after its device opened
    if not did_not_finish(None, 134, "terminate called") or not did_not_finish({}, 139, "") or not did_not_finish(None, 127, "") \
            or not did_not_finish(None, 1, "device ready in 0.9 s\n") or did_not_finish(None, 1, "mnistmlp_host: usage") \
            or did_not_finish({"status": "REFUSED"}, 3, "device ready in 0.9 s\n") or did_not_finish(raw, 0, "device ready in 0.9 s\n"):
        bad.append("K1 wider (fix-e202)")
    if config_line('Opening device 0\n{"tdp_w":0,"temp_threshold_c":65,"minion_mhz":600}\n').get("tdp_w") != 0 \
            or config_line('{"tdp_w":0,"temp_thr') != {} or not config_ok({"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600}) \
            or config_ok({"tdp_w": 5, "temp_threshold_c": 65, "minion_mhz": 600}):
        bad.append("config")
    full = ('{"t_ms":1,"board_w":3.0,"sp":{"board_avg_w":3.0,"minion_w":[1.0],"sram_w":[1.0],"noc_w":[1.0]},'
            '"temp_c":{"minshire":[50,49,51]},"mhz":{"minion":600}}')
    if sample_line(full) is None or sample_line('{"t_ms":1,"bo') is not None or sample_line("Opening") is not None \
            or sample_line(full.replace('"board_w"', '"board_Opening device 1w"')) is not None:
        bad.append("sample_line")
    if etwho_holders("No process holds an ET-SoC-1 device node or card lock.\n", "me") != 0 or \
            etwho_holders("/dev/et0_ops other 42 x_host\nlock:etsoc-shire0.lock me 7 python3\n", "me") != 1:
        bad.append("etwho_holders")
    # fix-e202 (finding 1): et-who read only when rc 0 with a holder line or its no-holder sentence (E191's seven forms, and verify-e202's)
    for name, rc, text, want in (("the no-holder sentence", 0, NO_HOLDER + "\n", ""), ("a holder line", 0, "/dev/et0_mgmt other 1 0 x\n", ""),
                                 ("our own lock line", 0, "lock:etsoc-shire0.lock me 7 python3\n", ""),
                                 ("its helper refused (rc 1, nothing on stdout)", 1, "", "x"), ("rc 1 with text", 1, "et-who: its helper refused\n", "x"),
                                 ("rc 1 with a holder line", 1, "/dev/et0_mgmt other 1 0 x\n", "x"), ("rc 2", 2, "", "x"),
                                 ("command not found (127)", 127, "", "x"), ("rc 0 and nothing", 0, "", "x"),
                                 ("rc 0 and other words", 0, "Segmentation fault\n", "x"), ("rc 0, a device name alone", 0, "/dev/et0_mgmt\n", "x")):
        if bool(etwho_unreadable(rc, text)) != bool(want):
            bad.append(f"etwho_unreadable on {name}")

    def smp(mhz=600, bw=30.0, die=55):
        return {"t_ms": 1, "board_w": bw, "temp_c": {"minshire": [die, die - 1, die + 1]}, "mhz": {"minion": mhz}}
    st = Stops()
    acts = [st.feed(smp(800), None), st.feed(smp(600), "trained-scp/b1"), st.feed(smp(800), "trained-scp/b1")]
    if not (acts == [[], [], ["set-aside", "stop"]] and st.off_clock == 2 and "second" in (st.stop or "")):
        bad.append(f"clock line: one sample outside a burst then one in a burst {acts}")
    st2 = Stops()
    if not (st2.feed(smp(800), "x/b1") == ["set-aside"] and st2.feed(smp(800), "x/b2") == ["set-aside", "stop"]):
        bad.append("clock line: two samples in two bursts")
    if not (Stops().feed(smp(bw=65.0), None) == ["stop"] and Stops().feed(smp(die=70), None) == ["stop"]
            and Stops().feed(smp(bw=64.99, die=69), "x/b1") == [] and Stops().feed(smp(), None, age_s=1.2) == ["stop"]
            and Stops().feed(smp(), None, age_s=0.9) == []):
        bad.append("board, die or stale line")
    s5 = Stops()
    if s5.stale(0.95) or not s5.stale(1.05) or "no telemetry" not in s5.stop:
        bad.append("the watchdog's stale line")
    if read_result("/nonexistent/x.json")[0] is not None:
        bad.append("read_result of no file")
    return bad


if __name__ == "__main__":
    import sys
    b = selfcheck()
    print("E202-COMMON SELF-CHECK " + ("PASS" if not b else "FAIL: " + "; ".join(b)))
    sys.exit(0 if not b else 1)
