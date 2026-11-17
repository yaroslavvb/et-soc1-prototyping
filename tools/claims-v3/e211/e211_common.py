#!/usr/bin/env python3
"""E211's kit (Q204, lane kit-e211, Tue 17 Nov 2026, before any E211 datum): what the box runner, the doubles, the reducer, the collector and
the desk tests share. E206's kit form for its arm A (tools/claims-v3/e206/e206_common.py, landed in 906699ea and run FULL on this card by E206
arm A, data d7e4f35e), through E207's one-arm port of it (Q199's kit-e207, not landed when this was written), for E211's one card, aifoundry3
card 0. Python's own modules only: it runs on aifoundry3 under the system python3 (3.12.3, read there on Tue 17 Nov 2026 00:23 PST) and at the
desk under /usr/bin/python3 -I -B (3.12.3).

It reads the registration's files and never changes them: points-e211.json (every point's host arguments, its arm family, host and kernel, the
smoke's three points and the order), plan-e211.json (the card, its clock and config, the line, the stops, the gate and the card-time rules) and
forecast-e211.json (the frozen forecasts, at their sha256 90e8d1ae...: the smoke's cycles an op is read against MM1's counter-mean forecast
there, E211.md section 7, R0; the doubles drive their toy card with MM1's seconds and watts). It adds:
  - THE ARM'S IDENTITY (one arm, A, E206's word for it, so the scorer's data form {"arms": {"A": ...}} holds): aifoundry3 card 0 (its one
    card: /dev/et0_*, the lock etsoc-shire0.lock, ET_DEVICES unset, the box tree ~/aifoundry, the box's reader build/ettelem/ettelem at the
    sha256 E206's and E207's kits read there), the start config gate (TDP 0 W / 65 C / 600 MHz, read as found) and the clock band (590-610 MHz);
  - THE TWO BUILDS (kernel-e211.json): rgm136 from tools/claims-v3/e136/rgm136 (unchanged) into build/e211rgm/rgm136, and rgm211 from
    tools/claims-v3/e211/rgm211 into build/e211rgm/rgm211 (new folders of ours); THE KERNEL GATE on each (ident_e211.py, the registration's
    gate: the .text always the family's pin, and the whole ELF the desk build's or else its loadable identity the pinned one; aifoundry3's riscv
    gcc prints "(g1b306039a) 15.1.0", which lands in a section the card never loads: read there Tue 17 Nov 2026 00:23 PST, where this lane's
    build gave rgm211 .text 82c79807... and identity 1351a569..., the pins); the hosts read by their behaviour, never by their bytes;
  - THE ARM FAMILIES (points-e211.json > arm_families): gemmL runs rgm136's ELF on rgm136's host; gemmLn rgm211's ELF on rgm211's host; gemmLnc
    rgm136's ELF on rgm211's host. host_argv names each point's own host and kernel; THE IDENTITY GATE PER PROCESS is the runner's (ident_e211);
  - THE WALK CHECK's reading (E211.md section 2; plan-e211.json > stops > kernel_stops): every launch record of rgm211's host carries "walk",
    "walk_tagged" and "walk_ok", its check record "walk" and "walk_launches_bad"; a gemmLn process wants walk nm, a gemmLnc process walk mn, on
    every launch, walk_ok true on every launch and walk_launches_bad 0. rgm136's host prints no walk (none is read for gemmL);
  - THE TILES: the two files the points' --values name, at the sha256 kinds.json records;
  - THE STOP LINES (plan-e211.json > stops: board above 70 W on 3 samples in a row, die at or above 70 C, E206 arm A's lines as amended by
    E206.md A1 items 1 and 2), with THE LATCH READING: the telemetry's minshire[2] is a latch held since the card's last statistics reset
    (docs/findings/14-card-behaviour.md, its dated note of Tue 3 Nov 2026), not the hottest sensor now: on aifoundry3 card 0 it read 87 C in
    every committed sample of E189, E195, E196, E197 and E206 arm A. So the die line trips on the shires' mean (minshire[0]) at or above the
    line, or on the latch only when it has RISEN during the session above the lowest value it read since the session's first sample and reads
    at or above the line. The board line: strictly above 70 W on 3 samples in a row that carry a board reading, a sample with no board reading
    neither counting nor breaking the row;
  - THE GATES: the die gate min(60, rest die + 4) C (at most 300 s, else that run is NO DATA), the rest die the median of the shires' mean over
    the smoke's 30 s rest; THE CARD-TIME RULE (plan-e211.json > card_time: no run starts once the card time passes 30 minutes; the session ends
    at 35 after the run in progress) and the window's last end;
  - THE ORDER: points-e211.json > order (the smoke s01-s03, then family X, family W, family C: 38 runs, n 4-41), each run one host process
    `timeout 10 <the point's host> <the point's host_args> --kernel <the point's ELF> --stop-file <STOP>`, never `timeout -k`;
  - THE HOST'S RECORDS, READ FROM A SOURCE NO RUNTIME PRINT CAN SPLIT (CONTEXT section 116's lesson; E206's form, line for line): both hosts
    print their SPARSITY records on stdout and have no result file of their own; a runtime may print "Opening device N" on the same stdout
    (aifoundry1's does; aifoundry3's printed none in E206 arm A's 244 committed stdouts). drop_runtime removes every such line wherever it fell,
    pass after pass until none is left, and a JSON string cannot hold a raw newline, so the removal never cuts the host's own text;
    runtime_cards names the cards those lines open (a line naming another card than card 0 is an identity trip); then each "SPARSITY {...}"
    line must parse whole as a JSON object and carry its command's own fields (test, arm, type, values, shire mask, minions), else it is NOT read
    (counted, never a datum). The config read is read the same way (drop_runtime, then the last whole JSON line);
  - the counted launch (E211.md 7): an fma launch with launch >= 0, ok, wall_s >= 0.1 s, at least one pass, and its kernel clock
    (cycles_max / wall_s) in 590-610 MHz.
    python3 -I -B tools/claims-v3/e211/e211_common.py        the self-check (E211-COMMON SELF-CHECK PASS)
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
PLAN_F = os.path.join(HERE, "plan-e211.json")
PTS_F = os.path.join(HERE, "points-e211.json")
FC_REL = "tools/claims-v3/e211/forecast-e211.json"
FC_F = os.path.join(REPO, FC_REL)
FC_PIN = "90e8d1ae4c68c162eab687624f72bf15599ae26d2050012c3381f179453108f5"     # E211.md section 0 (the freeze line)
KJ_F = os.path.join(HERE, "kernel-e211.json")

# ---- the builds (build_e211.sh writes them on the box, from the box tree's root)
BUILD_DIR = "build/e211rgm"
BUILD_REC = BUILD_DIR + "/BUILD-e211.json"
GUARD = "tools/claims-v3/e211/ettelem_guard_e211.sh"
BUILDER = "build_e211.sh"
KERNELS = {     # kernel-e211.json, repeated here and checked against it by the self-check
    "rgm136": {"src": "tools/claims-v3/e136/rgm136", "dir": BUILD_DIR + "/rgm136",
               "elf": "aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0",
               "text": "61315bf6a449c2823fbffc33834b4c0a68aa19e8436a29c1124b15c04114b763",
               "load": "649d40793e459e51db9a590ca90dd1363da3a00398f98938c3ef6e190514e2b7", "family": "gemmL"},
    "rgm211": {"src": "tools/claims-v3/e211/rgm211", "dir": BUILD_DIR + "/rgm211",
               "elf": "00402801a1a53a9330898ef023297d8967a2c655472a40e0f1cd65dea04f09ae",
               "text": "82c7980716a0f0cacd24364ef9a23435343eb8f2c35c32b0ec5d60b46c8a4069",
               "load": "1351a569e4a200cb4cd916c4c6af822b45ce6e1cac9b7aa8b71c945a1f5bd847", "family": "gemmLn"},
}
FAMILY_HOST = {"gemmL": "rgm136", "gemmLn": "rgm211", "gemmLnc": "rgm211"}
FAMILY_KERNEL = {"gemmL": "rgm136", "gemmLn": "rgm211", "gemmLnc": "rgm136"}
WALK_WANT = {"gemmLn": "nm", "gemmLnc": "mn"}       # rgm211's host's walk check; rgm136's host prints none (gemmL)


def host_rel(kind):
    return KERNELS[kind]["dir"] + "/host/sparsity_host"


def elf_rel(kind):
    return KERNELS[kind]["dir"] + "/kernel/sparsity.elf"


# ---- the one arm (plan-e211.json): A, as E206 arm A's form names it
ARMS = {
    "A": {"box": "aifoundry3", "card": "aifoundry3 card 0", "lock": "/run/lock/etsoc-shire0.lock", "et_devices": None,
          "tree": "aifoundry", "data_dir": "aifoundry3",
          "ettelem": "build/ettelem/ettelem",
          "ettelem_sha256": "16037641ab75bdbe1209f323641e269c9b897468091243173bfaaaf0b21686e2",   # E206's and E207's kits' read on aifoundry3
          "config": {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600}, "clock_mhz": 600, "count_mhz": (590.0, 610.0),
          "gate_cap_c": 60.0, "gate_add_c": 4.0},
}

# ---- every file a point's --values names, at the sha256 kinds.json records (kinds.json > kinds > <fmt> > <name> > sha256)
TILES = {
    "tools/claims-v3/kinds/tiles/fp32/randn.bin": "34b2add3eb5b7b3c83be7ca7286cf1625c0fca7a1ac9957cafe4fd22e1b804fa",
    "tools/claims-v3/kinds/tiles/int8/full.bin": "f5a5f3bf675fca97e857be3747d5f58b6b3d020f25ed11f5d047a87f161444a9",
}
TILE_MANIFEST = "tools/claims-v3/kinds/kinds.json"

# ---- the session's timing: the registration's numbers (E211.md 7 and 8; plan-e211.json), and the kit's own (marked)
REST_READ_S = 10.0          # plan-e211.json run_form: "10 s at rest (p_rest = the median of its last 5 s)"
REST_WINDOW_S = 5.0         # the same
SMOKE_REST_S = 30.0         # plan-e211.json smoke: "30 s at rest (the session's rest reading; the die gates from it)"
SMOKE_PIDS = ("s01", "s02", "s03")                            # points-e211.json smoke, in this order (gemmL, gemmLn, gemmLnc)
SMOKE_SECONDS, SMOKE_BUDGET = 2.0, 3.5     # "one checked short process": E146's, E190's, E206's and E207's smoke form (the kit's reading, KIT.md 4)
RUN_SECONDS, RUN_BUDGET = 6.0, 7.5         # plan-e211.json run_form: "--seconds 6 --budget 7.5"
TAIL_S = 4.0                # plan-e211.json run_form: "a 4 s tail"
GATE_WAIT_S = 300.0         # plan-e211.json die_gate: "at most 300 s, else that run is NO DATA"
CARD_RULE_S = 30 * 60.0     # plan-e211.json card_time: no run starts after 30 card-minutes
CAP_S = 35 * 60.0           # plan-e211.json card_time: the session ends at 35 after the run in progress
CLOSE_S = 60.0              # the kit's: the closing (the sampler's stop, the closing config read) keeps this much of the cap
WINDOW_MARGIN_S = 90.0      # the kit's (E190's, E206's): no run starts within its length + 90 s of the window's last end
EVERY_MS = 100              # the sampler's rate (10 Hz, E206's)
HOST_TIMEOUT_S = 10         # `timeout 10` on every device-opening process (plain: never -k)
HANG_GRACE_S = 4.0          # the kit's: a host whose `timeout` has not returned 4 s after its 10 s TERM is HUNG (reported and left)
RUN_MAX_S = REST_READ_S + HOST_TIMEOUT_S + HANG_GRACE_S + TAIL_S   # the longest a run can last once its gate has passed (28 s)
CYC_LO, CYC_HI = 0.5, 2.5   # rules-e211.json R0 smoke_band: the smoke's cycles an op within 50-250% of MM1's counter-mean forecast
MHZ_BAND = (590.0, 610.0)   # E211.md 7: the kernel clock a counted launch is in, and S6's band
LINE_W = 65.0               # plan-e211.json line_w: no point whose planning peak passes it runs (none does: the self-check reads it)
RUNTIME_LINE = re.compile(r"Opening device [0-9]+\n")         # a runtime's line on a host's or a reader's stdout (aifoundry1's form)
RUNTIME_CARD = re.compile(r"Opening device ([0-9]+)")         # the card such a line opens (another card's is an identity trip)


def load(path):
    with open(path) as f:
        return json.load(f)


def plan():
    return load(PLAN_F)


_PTS = {}


def points():
    if "p" not in _PTS:
        _PTS["p"] = load(PTS_F)
    return _PTS["p"]


def point(pid):
    """A point of points-e211.json by its id: a scored point (points) or a smoke point (smoke)."""
    P = points()
    for p in P["points"] + P["smoke"]:
        if p["id"] == pid:
            return p
    raise KeyError(pid)


def family(pid):
    return point(pid)["arm_family"]


_FC = {}


def forecast():
    """forecast-e211.json, which must be at its pin (E211.md section 0); else ValueError (the box check's harness read refuses first)."""
    if "f" not in _FC:
        with open(FC_F, "rb") as f:
            raw = f.read()
        if hashlib.sha256(raw).hexdigest() != FC_PIN:
            raise ValueError(f"{FC_REL} is not E211's frozen file {FC_PIN[:12]}")
        _FC["f"] = json.loads(raw)
    return _FC["f"]


def mm1(pid):
    """MM1's frozen forecast at a point {"cyc_wall", "cyc_mean", "t", "W", "J", "ops"} (forecast-e211.json > points > <id> > MM1); the smoke's
    R0 band reads cyc_mean, as the frozen scorer does."""
    P = forecast()["points"][pid]
    m = P["MM1"]
    return {"cyc_wall": float(m["cycles_per_op_wall"]), "cyc_mean": float(m["cycles_per_op_mean"]), "t": float(m["seconds_per_gemm"]),
            "W": float(m["W_over_idle"]), "J": float(m["J_over_idle_per_gemm"]), "ops": int(P["ops_per_minion_per_gemm"])}


def double_of(pid):
    """The doubles' toy forecast at a point (desk numbers of the doubles, never a datum): MM1's, and for a gemmLnc point family C's registered
    rule C1 (forecast-e211.json > points > <id> > C > C1) where the forecast carries it."""
    d = mm1(pid)
    P = forecast()["points"][pid]
    c1 = (P.get("C") or {}).get("C1")
    if point(pid)["arm_family"] == "gemmLnc" and c1:
        d.update(cyc_wall=float(c1["cycles_per_op_wall"]), cyc_mean=float(c1["cycles_per_op_mean"]), t=float(c1["seconds_per_gemm"]),
                 W=float(c1["W_over_idle"]), J=float(c1["J_over_idle_per_gemm"]))
    return d


def stops_of(arm, p=None):
    """The arm's stop lines under the watcher's keys, from plan-e211.json ("stops")."""
    if arm not in ARMS:
        raise KeyError(arm)
    s = (p or plan())["stops"]
    return {"board_cap_w": float(s["board_w_above"]), "cap_consecutive": int(s["samples_in_a_row"]), "abs_stop_c": float(s["die_c_at_or_above"])}


def gate_c(arm, rest_die):
    """The die gate a run starts under (plan-e211.json die_gate): min(60, rest die + 4); None with no rest die (no run starts)."""
    if rest_die is None:
        return None
    a = ARMS[arm]
    return min(a["gate_cap_c"], rest_die + a["gate_add_c"])


def sequence(arm):
    """The registered order's runs: [{"n", "block", "id", "name", "pair"}, ...] (points-e211.json > order, the smoke left out: the runner runs
    the smoke itself, first); one arm, A."""
    if arm not in ARMS:
        raise KeyError(arm)
    return [{"n": x["n"], "block": x["block"], "id": x["point"], "name": x["arm"], "pair": x["pair"]}
            for x in points()["order"] if x["block"] != "smoke"]


def run_key(r):
    return f"{r['n']:03d}-{r['block']}-{r['id']}"


def host_argv(root, pid, seconds, budget, stop_file):
    """One process's command line (without `timeout 10`): the point's own host (its arm family's: rgm136's for gemmL, rgm211's for gemmLn and
    gemmLnc), its registered host_args with --seconds and --budget set to the process form, then the kit's --kernel (its arm family's ELF:
    rgm211's for gemmLn, rgm136's for gemmL and gemmLnc) and --stop-file."""
    p = point(pid)
    a = list(p["host_args"])
    for flag, val in (("--seconds", f"{seconds:g}"), ("--budget", f"{budget:g}")):
        a[a.index(flag) + 1] = val
    return [os.path.join(root, host_rel(p["host"]))] + a + ["--kernel", os.path.join(root, elf_rel(p["kernel"])), "--stop-file", stop_file]


def arg_of(argv, name):
    argv = list(argv or [])
    return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else None


def expect_of(argv):
    """The record fields a process's command line fixes: what every SPARSITY record of that process must carry."""
    vals = arg_of(argv, "--values") or ""
    mask = int(arg_of(argv, "--shires") or "0", 0)
    per = int(arg_of(argv, "--per-shire") or "0", 0)
    return {"arm": vals.split(":")[0], "type": arg_of(argv, "--type"), "values": vals, "shire_mask": "0x%x" % mask,
            "minions": bin(mask).count("1") * per}


def die_of(s):
    return ((s.get("temp_c") or {}).get("minshire") or [None])[0]


def latch_of(s):
    ms = (s.get("temp_c") or {}).get("minshire") or []
    return ms[2] if len(ms) > 2 else None


def kclock(L):
    """A launch's kernel clock in MHz: cycles_max / wall_s (E119's clock_x)."""
    w = L.get("wall_s") or 0
    return (L.get("cycles_max") or 0) / w / 1e6 if w > 0 else None


def counted(L, arm=None):
    """E211.md 7's counted launch: an fma launch, launch >= 0, ok, wall_s >= 0.1 s, at least one pass, its kernel clock in 590-610 MHz."""
    if L.get("test") != "fma" or not isinstance(L.get("launch"), int) or L["launch"] < 0 or not L.get("ok") or \
            (L.get("wall_s") or 0) < 0.1 or not L.get("passes"):
        return False
    f = kclock(L)
    return f is not None and MHZ_BAND[0] <= f <= MHZ_BAND[1]


def walk_check(fam, fma, chk):
    """THE WALK CHECK's reading for one process (E211.md section 2): (ok, words, detail). rgm211's host (gemmLn, gemmLnc): every launch record
    carries walk == the family's (nm, mn) and walk_ok true, and the last check record walk == the family's and walk_launches_bad 0; a process
    with no launch record or no check record fails. rgm136's host (gemmL) prints no walk: (True, "no walk (rgm136's host)", {})."""
    want = WALK_WANT.get(fam)
    if want is None:
        return True, "no walk (rgm136's host prints none)", {}
    names = [x.get("walk") for x in fma]
    oks = [x.get("walk_ok") for x in fma]
    tagged = [x.get("walk_tagged") for x in fma]
    c = chk[-1] if chk else {}
    det = {"want": want, "names": names, "ok": oks, "tagged": tagged, "check_walk": c.get("walk"), "launches_bad": c.get("walk_launches_bad")}
    why = []
    if not fma:
        why.append("no launch record")
    if any(n != want for n in names):
        why.append(f"a launch's walk is not {want} ({sorted({str(n) for n in names})})")
    if any(o is not True for o in oks):
        why.append(f"walk_ok not true on {sum(1 for o in oks if o is not True)} launch(es)")
    if not chk:
        why.append("no check record")
    elif c.get("walk") != want or c.get("walk_launches_bad") != 0:
        why.append(f"the check line reads walk {c.get('walk')!r}, walk_launches_bad {c.get('walk_launches_bad')!r}")
    return (not why), ("walk " + want + " on every launch, walk_ok true, walk_launches_bad 0" if not why else "; ".join(why)), det


def kernel_stop(fam, proc):
    """THE KERNEL STOPS (plan-e211.json > stops > kernel_stops) for a gemmLn or gemmLnc process: a check of C wrong (or missing), a tensor
    error, the walk check failed, a launch timeout (K1, or the process ended by its `timeout`'s TERM) or any launch not ok, or the process's
    exit not 0: '' when none, else why (the session stops: nothing more that day). The identity gate is the runner's, before the process
    starts. A gemmL process (rgm136, run FULL by E206 arm A on this card) keeps E206's rules (a failed process flagged; two in a row stop)."""
    if fam not in WALK_WANT:
        return ""
    why = []
    if proc.get("check") not in ("exact", "approx") or not proc.get("check_ok"):
        why.append(f"the check of C reads {proc.get('check')!r} (ok {proc.get('check_ok')})")
    if proc.get("tensor_errors"):
        why.append(f"{proc.get('tensor_errors')} tensor error(s)")
    if not proc.get("walk_ok"):
        why.append(f"the walk check failed ({proc.get('walk_words')})")
    if proc.get("k1"):
        why.append("a launch did not finish (K1)")
    if proc.get("rc") == 124:
        why.append("the process ended by its timeout's TERM (rc 124: a launch timeout)")
    if not proc.get("launches_ok"):
        why.append("a launch not ok")
    if proc.get("rc") not in (0, None) and proc.get("rc") != 124:
        why.append(f"the process rc {proc.get('rc')}")
    return "; ".join(why)


# ---- the host's records and the config read, from a source no runtime print can split (E206's functions, line for line)
def drop_runtime(text):
    """(the text without runtime lines, [the runtime lines dropped, in the order removed]): every RUNTIME_LINE removed wherever it fell,
    pass after pass until none is left (a runtime line printed INSIDE another runtime line leaves a whole one behind after the first pass;
    the second pass removes it). Each pass removes at least one line, so the loop ends."""
    text = text or ""
    found = []
    while True:
        hits = [m.group(0)[:-1] for m in RUNTIME_LINE.finditer(text)]
        if not hits:
            return text, found
        found += hits
        text = RUNTIME_LINE.sub("", text)


def runtime_cards(lines):
    """The cards the runtime lines open, as strings in order ("Opening device 1" -> "1"); the runner treats a line naming another card than
    card 0 as an identity trip, on a host's, a config read's or the sampler's stdout."""
    out = []
    for ln in lines or []:
        m = RUNTIME_CARD.search(ln or "")
        if m:
            out.append(str(int(m.group(1))))
    return out


def host_records(text, argv=None):
    """(fma records, check records, info): the host's SPARSITY records from its stdout, runtime lines dropped first; each must parse whole
    as a JSON object and, with argv, carry its command's own fields (an fma record: test, arm, type, values, shire_mask, minions; a check
    record: test, arm, type, minions), else it is not read (info counts it: unparsed, mismatched; any other line is 'other')."""
    body, rt = drop_runtime(text)
    want = expect_of(argv) if argv else None
    fma, chk, info = [], [], {"runtime_lines": rt, "unparsed": 0, "mismatched": [], "other": 0}
    for ln in body.split("\n"):
        if not ln.strip():
            continue
        if not ln.startswith("SPARSITY "):
            info["other"] += 1
            continue
        try:
            j = json.loads(ln[9:])
        except ValueError:
            info["unparsed"] += 1
            continue
        if not isinstance(j, dict) or j.get("test") not in ("fma", "check"):
            info["unparsed"] += 1
            continue
        if want:
            keys = ("arm", "type", "values", "shire_mask", "minions") if j["test"] == "fma" else ("arm", "type", "minions")
            bad = {k: (j.get(k), want[k]) for k in keys if j.get(k) != want[k]}
            if bad:
                info["mismatched"].append({"launch": j.get("launch"), "test": j["test"], "differs": {k: list(v) for k, v in bad.items()}})
                continue
        (fma if j["test"] == "fma" else chk).append(j)
    return fma, chk, info


def last_json(text):
    """The last line that parses whole as a JSON object, else {} (a cut line is no reading)."""
    for ln in reversed((text or "").splitlines()):
        s = ln.strip()
        if s.startswith("{") and s.endswith("}"):
            try:
                j = json.loads(s)
            except ValueError:
                continue
            if isinstance(j, dict):
                return j
    return {}


def config_json(text):
    """The config read's JSON line, its runtime lines dropped first."""
    return last_json(drop_runtime(text)[0])


def config_ok(arm, j):
    """The start config the arm's line rests on (plan-e211.json start_config_gate), read as found, nothing set."""
    if not j or arm not in ARMS:
        return False
    return all(j.get(k) == v for k, v in ARMS[arm]["config"].items())


class Stops:
    """THE STOP LINES on live samples (plan-e211.json > stops; E206's watcher, line for line): the shires' mean at or above abs_stop_c trips at
    once; the latch (minshire[2]) trips only when it has risen above the lowest value it read since the first sample and reads at or above
    abs_stop_c; a board reading above board_cap_w on cap_consecutive samples in a row trips (a reading at or under the line starts the count
    again; a sample with no board reading neither counts nor breaks the row). The first trip is kept; trip_file, if given, is touched at the
    trip (the real lines' file is the host's --stop-file, so a running host ends at its next launch boundary, about 0.5 s; nothing is ever
    killed)."""

    def __init__(self, board_cap_w, cap_consecutive, abs_stop_c, trip_file=None):
        self.board_cap_w, self.need, self.abs_stop_c = float(board_cap_w), int(cap_consecutive), float(abs_stop_c)
        self.trip_file = trip_file
        self.over = 0
        self.stop = None
        self.t_trip = None
        self.latch_low = None       # the lowest latch read since the first sample

    def feed(self, s):
        if self.stop:
            return []
        bw = s.get("board_w")
        die, high = die_of(s), latch_of(s)
        if die is not None and die >= self.abs_stop_c:
            return self._trip(f"die {die} C (the shires' mean) at or above {self.abs_stop_c:g} C", s)
        if high is not None:
            if self.latch_low is not None and high > self.latch_low and high >= self.abs_stop_c:
                return self._trip(f"the hottest sensor's latch rose to {high} C (from {self.latch_low} C this session), at or above "
                                  f"{self.abs_stop_c:g} C", s)
            self.latch_low = high if self.latch_low is None else min(self.latch_low, high)
        if bw is None:              # no board reading: neither counted nor breaking the row
            return []
        if bw > self.board_cap_w:
            self.over += 1
            if self.over >= self.need:
                return self._trip(f"board {bw} W above {self.board_cap_w:g} W on {self.need} samples in a row", s)
        else:
            self.over = 0
        return []

    def _trip(self, why, s):
        self.stop = why
        self.t_trip = s.get("t_ms")
        if self.trip_file:
            try:
                with open(self.trip_file, "a"):
                    os.utime(self.trip_file, None)
            except OSError:
                pass
        return ["stop"]


def selfcheck():
    bad = []
    p, pts = plan(), points()
    # the arm against the plan (plan-e211.json)
    st = stops_of("A", p)
    if (st["board_cap_w"], st["cap_consecutive"], st["abs_stop_c"]) != (70.0, 3, 70.0):
        bad.append(f"the stops {st}, not (70, 3, 70)")
    if not p["die_gate"].startswith("min(60, the session's rest die + 4) C, at most 300 s") or \
            (ARMS["A"]["gate_cap_c"], ARMS["A"]["gate_add_c"]) != (60.0, 4.0):
        bad.append(f"the gate {p['die_gate']!r}")
    cfg = ARMS["A"]["config"]
    if not p["start_config_gate"].startswith(f"TDP {cfg['tdp_w']} W, {cfg['temp_threshold_c']} C, {cfg['minion_mhz']} MHz"):
        bad.append(f"the start config {p['start_config_gate']!r}")
    if "aifoundry3 card 0" not in p["card"] or "etsoc-shire0.lock" not in p["card"]:
        bad.append(f"the card {p['card']!r}")
    if (p["card_time"]["no_new_run_after_min"], p["card_time"]["cap_min"]) != (CARD_RULE_S / 60, CAP_S / 60):
        bad.append("the card-time rule and cap")
    if float(p["line_w"]) != LINE_W or p["predicted_peak"]["points_over_the_line"] or \
            any(max(v.values()) > LINE_W for v in p["peaks_per_point"].values()):
        bad.append("a point's planning peak over the 65 W line")
    if "kernel_stops" not in p["stops"] or "walk check failed" not in p["stops"]["kernel_stops"]:
        bad.append("the kernel stops")
    # the order: the smoke, X, W, C (family C after family W), 38 runs n 4-41
    seq = sequence("A")
    order = pts["order"]
    if [x["n"] for x in order] != list(range(1, 42)) or [x["point"] for x in order[:3]] != list(SMOKE_PIDS) or \
            any(x["block"] != "smoke" for x in order[:3]):
        bad.append("the order's smoke or numbering")
    if len(seq) != pts["counts"]["scored_runs"] or len(seq) != 38 or [r["n"] for r in seq] != list(range(4, 42)):
        bad.append(f"the runs ({len(seq)}) are not the registered 38, n 4-41")
    blocks = [r["block"] for r in seq]
    if blocks != sorted(blocks, key=lambda b: "XWC".index(b)) or blocks.index("C") < len(blocks) - 6 or blocks.count("X") != 4:
        bad.append(f"the blocks are not X, then W, then C ({blocks})")
    ids = {r["id"] for r in seq}
    if ids != {q["id"] for q in pts["points"]}:
        bad.append("the runs' points are not the registered 26")
    if tuple(q["id"] for q in pts["smoke"]) != SMOKE_PIDS or [q["arm_family"] for q in pts["smoke"]] != ["gemmL", "gemmLn", "gemmLnc"]:
        bad.append(f"the smoke's points {[q['id'] for q in pts['smoke']]}")
    for q in pts["points"] + pts["smoke"]:
        fam = q["arm_family"]
        if (q["host"], q["kernel"]) != (FAMILY_HOST[fam], FAMILY_KERNEL[fam]) or pts["arm_families"][fam] != {"host": FAMILY_HOST[fam], "kernel": FAMILY_KERNEL[fam]}:
            bad.append(f"{q['id']}: host {q['host']} / kernel {q['kernel']} is not its family {fam}'s")
            break
        if not q["arm"].startswith(fam) or (fam == "gemmL" and q["arm"][5:6] in ("n",)) or (fam == "gemmLn" and q["arm"].startswith("gemmLnc")):
            bad.append(f"{q['id']}: arm {q['arm']} is not of its family {fam}")
            break
    if "--seconds 6 --budget 7.5" not in p["run_form"] or "never -k" not in p["run_form"] or "10 s at rest" not in p["run_form"] or "4 s tail" not in p["run_form"]:
        bad.append("the run form")
    if not p["smoke"].startswith("30 s at rest") or not all(x in p["smoke"] for x in SMOKE_PIDS) or "then the stop-path test" not in p["smoke"] \
            or "MM1's counter-mean forecast" not in p["smoke"] or "walk_ok true" not in p["smoke"]:
        bad.append("the smoke's form")
    # the kernels against kernel-e211.json
    kj = load(KJ_F)["kernels"]
    for k, v in KERNELS.items():
        if (kj[k]["elf_sha256"], kj[k]["text_sha256"], kj[k]["loadable_identity_sha256"], kj[k]["tree"]) != (v["elf"], v["text"], v["load"], v["src"]):
            bad.append(f"{k}'s pins differ from kernel-e211.json")
    # the frozen forecast: at its pin, every point and the smoke there, the smoke's counter-mean forecasts readable
    try:
        fp = forecast()["points"]
        if set(fp) != {q["id"] for q in pts["points"] + pts["smoke"]} or any(not (mm1(x)["cyc_mean"] > 0) for x in SMOKE_PIDS) or \
                any(not (double_of(q["id"])["t"] > 0) for q in pts["points"]):
            bad.append("forecast-e211.json does not hold the registered points")
    except (OSError, ValueError, KeyError) as e:
        bad.append(f"forecast-e211.json ({type(e).__name__}: {str(e)[:80]})")
    # the argv: every family's host and kernel
    a = host_argv("/T", "w06n", RUN_SECONDS, RUN_BUDGET, "/T/STOP")
    if a[:2] != ["/T/build/e211rgm/rgm211/host/sparsity_host", "--test"] or \
            arg_of(a, "--values") != "gemmLn3x5x7:randn:tools/claims-v3/kinds/tiles/fp32/randn.bin" or arg_of(a, "--shires") != "0xffffffff" \
            or arg_of(a, "--per-shire") != "32" or arg_of(a, "--seconds") != "6" or arg_of(a, "--budget") != "7.5" \
            or arg_of(a, "--kernel") != "/T/build/e211rgm/rgm211/kernel/sparsity.elf" or arg_of(a, "--stop-file") != "/T/STOP" or "-k" in a:
        bad.append(f"the gemmLn argv {a}")
    m = host_argv("/T", "w06m", RUN_SECONDS, RUN_BUDGET, "/T/STOP")
    if m[0] != "/T/build/e211rgm/rgm136/host/sparsity_host" or arg_of(m, "--kernel") != "/T/build/e211rgm/rgm136/kernel/sparsity.elf" or \
            arg_of(m, "--values") != "gemmL3x5x7:randn:tools/claims-v3/kinds/tiles/fp32/randn.bin":
        bad.append(f"the gemmL argv {m}")
    c = host_argv("/T", "c02c", RUN_SECONDS, RUN_BUDGET, "/T/STOP")
    if c[0] != "/T/build/e211rgm/rgm211/host/sparsity_host" or arg_of(c, "--kernel") != "/T/build/e211rgm/rgm136/kernel/sparsity.elf" or \
            arg_of(c, "--values") != "gemmLnc3x5x7:randn:tools/claims-v3/kinds/tiles/fp32/randn.bin":
        bad.append(f"the gemmLnc argv {c}")
    s = host_argv("/T", "s03", SMOKE_SECONDS, SMOKE_BUDGET, "/T/STOP")
    if arg_of(s, "--seconds") != "2" or arg_of(s, "--budget") != "3.5" or arg_of(s, "--type") != "fp32" or \
            arg_of(s, "--kernel") != "/T/build/e211rgm/rgm136/kernel/sparsity.elf" or s[0] != "/T/build/e211rgm/rgm211/host/sparsity_host":
        bad.append(f"the smoke's argv {s}")
    i8 = host_argv("/T", "w10n", RUN_SECONDS, RUN_BUDGET, "/T/STOP")
    if arg_of(i8, "--type") != "int8" or arg_of(i8, "--values") != "gemmLn3x5x7:randn:tools/claims-v3/kinds/tiles/int8/full.bin":
        bad.append(f"the int8 argv {i8}")
    if expect_of(a) != {"arm": "gemmLn3x5x7", "type": "fp32", "values": "gemmLn3x5x7:randn:tools/claims-v3/kinds/tiles/fp32/randn.bin",
                        "shire_mask": "0xffffffff", "minions": 1024}:
        bad.append(f"expect_of {expect_of(a)}")
    for q in pts["points"] + pts["smoke"]:
        e = expect_of(host_argv("/T", q["id"], 6, 7.5, "/S"))
        if (int(e["shire_mask"], 16), e["minions"], e["arm"], e["type"]) != (int(q["shire_mask"], 16), q["minions"], q["arm"], q["format"]):
            bad.append(f"{q['id']}: expect_of {e} against the point")
            break
    # the tiles: every file a point names, at its manifest's sha256
    named = set()
    for q in pts["points"] + pts["smoke"]:
        named |= set(arg_of(q["host_args"], "--values").split(":", 2)[2].split(","))
    if named != set(TILES):
        bad.append(f"TILES is not the points' files ({len(named)} named, {len(TILES)} pinned)")
    try:
        kk = load(os.path.join(REPO, TILE_MANIFEST))["kinds"]
        for f, h in TILES.items():
            fmt, base = f.split("/")[-2], os.path.basename(f)
            if kk[fmt][base[:-4]]["sha256"] != h:
                bad.append(f"{f}: pinned {h[:12]}, its manifest {kk[fmt][base[:-4]]['sha256'][:12]}")
    except (OSError, KeyError, ValueError, TypeError) as e:
        bad.append(f"the tile manifest could not be read ({type(e).__name__})")
    # the walk check's reading
    rn = {"test": "fma", "walk": "nm", "walk_tagged": 1024, "walk_ok": True}
    cn = {"test": "check", "walk": "nm", "walk_launches_bad": 0}
    if not walk_check("gemmLn", [rn, rn], [cn])[0] or walk_check("gemmLn", [rn, dict(rn, walk_ok=False)], [cn])[0] or \
            walk_check("gemmLn", [dict(rn, walk="mn", walk_ok=True)], [cn])[0] or walk_check("gemmLn", [rn], [dict(cn, walk_launches_bad=1)])[0] \
            or walk_check("gemmLn", [rn], [])[0] or walk_check("gemmLn", [], [cn])[0] or walk_check("gemmLnc", [rn], [cn])[0] or \
            not walk_check("gemmLnc", [dict(rn, walk="mn", walk_tagged=0)], [dict(cn, walk="mn")])[0] or not walk_check("gemmL", [], [])[0] or \
            walk_check("gemmLn", [dict(rn, walk_ok=None)], [cn])[0]:
        bad.append("the walk check's reading")
    good = {"check": "approx", "check_ok": True, "tensor_errors": 0, "walk_ok": True, "k1": False, "rc": 0, "launches_ok": True}
    if kernel_stop("gemmLn", good) or not kernel_stop("gemmLn", dict(good, check="wrong", check_ok=False)) or \
            not kernel_stop("gemmLnc", dict(good, walk_ok=False, walk_words="x")) or not kernel_stop("gemmLn", dict(good, tensor_errors=1)) or \
            not kernel_stop("gemmLn", dict(good, rc=124)) or not kernel_stop("gemmLn", dict(good, k1=True)) or \
            not kernel_stop("gemmLnc", dict(good, rc=1)) or kernel_stop("gemmL", dict(good, rc=1, check="wrong")):
        bad.append("the kernel stops")
    # the stop lines: the watcher's semantics, the latch reading (E206's cases, arm A)
    def smp(bw=40.0, die=50, high=87):
        return {"t_ms": 1, "board_w": bw, "temp_c": {"minshire": [die, 46, high]}}
    st = Stops(70, 3, 70)
    r = [st.feed(smp(71)), st.feed(smp(71)), st.feed(smp(70.0)), st.feed(smp(71)), st.feed(smp(71)), st.feed(smp(71))]
    if r != [[], [], [], [], [], ["stop"]] or "board" not in (st.stop or ""):
        bad.append(f"the board line {r} {st.stop}")
    st = Stops(70, 3, 70)
    if [st.feed(smp(die=69, high=87)) for _ in range(5)] != [[]] * 5 or st.feed(smp(die=70, high=87)) != ["stop"] or "shires' mean" not in st.stop:
        bad.append("the die line: the 87 C latch must not trip it, the mean at 70 C must")
    st = Stops(70, 3, 70)
    if st.feed(smp(die=60, high=87)) != [] or st.feed(smp(die=60, high=87)) != [] or st.feed(smp(die=60, high=88)) != ["stop"] or "latch rose" not in st.stop:
        bad.append("the latch rising past its session value")
    st = Stops(70, 3, 70)
    if st.feed(smp(die=60, high=87)) != [] or st.feed(smp(die=60, high=50)) != [] or st.feed(smp(die=60, high=71)) != ["stop"]:
        bad.append("the latch after a drop (a statistics reset by another) rising past the line")
    st = Stops(70, 3, 70)       # a sample with no board reading neither counts nor breaks the row
    if st.feed({"t_ms": 1, "board_w": 73}) != [] or st.feed({"t_ms": 2}) != [] or st.feed({"t_ms": 3, "board_w": 73}) != [] or \
            st.feed({"t_ms": 4, "board_w": 73}) != ["stop"]:
        bad.append("a sample with no board reading neither counts nor breaks the row")
    st = Stops(70, 3, 70)       # 95 W on every other sample, no reading between, trips at the third reading
    r = [st.feed({"t_ms": k, "board_w": 95.0} if k % 2 else {"t_ms": k}) for k in range(1, 8)]
    if r != [[], [], [], [], ["stop"], [], []] or "95.0 W above 70 W" not in (st.stop or ""):
        bad.append(f"95 W on every other sample with no reading between {r}")
    st = Stops(70, 3, 70)       # a reading at or under the line still breaks the row
    if [st.feed({"t_ms": k, "board_w": w}) for k, w in enumerate((95.0, None, 69.0, 95.0, None, 95.0))] != [[]] * 6 or st.stop:
        bad.append("a reading under the line between over-line readings did not break the row")
    # the counted launch
    L = {"test": "fma", "launch": 0, "ok": True, "wall_s": 0.5, "passes": 1, "cycles_max": 300e6}
    if not counted(L) or counted(dict(L, cycles_max=400e6)) or counted(dict(L, launch=-1)) or counted(dict(L, launch=-3)) or \
            counted(dict(L, ok=False)) or counted(dict(L, wall_s=0.05, cycles_max=30e6)) or counted(dict(L, passes=0)) or counted(dict(L, test="check")):
        bad.append("the counted launch")
    # the records: runtime lines inside a record (rgm211's host's form, with its walk fields), a cut record, a record of another command
    rec = {"test": "fma", "arm": "gemmLn3x5x7", "gen": "randn", "type": "fp32", "pattern": "none",
           "values": "gemmLn3x5x7:randn:tools/claims-v3/kinds/tiles/fp32/randn.bin", "b_stream": 0, "minions": 1024, "shire_mask": "0xffffffff",
           "iters": 6720, "passes": 1, "launch": 0, "cycles_max": 300000000, "cycles_per_op": 1434.5, "wall_s": 0.5, "walk": "nm",
           "walk_tagged": 1024, "walk_ok": True, "result": "unchecked", "ok": True}
    line = "SPARSITY " + json.dumps(rec, separators=(",", ":"))
    for k in range(0, len(line) + 1, 7):
        f_, c_, inf = host_records(line[:k] + "Opening device 1\n" + line[k:] + "\n", a)
        if f_ != [rec] or inf["runtime_lines"] != ["Opening device 1"]:
            bad.append(f"a runtime line at offset {k} of a record")
            break
    for k in range(0, len(line) + 1, 7):      # a runtime line printed INSIDE another runtime line, the pair inside a record
        for j in (0, 3, 9, len("Opening device 1")):
            outer = "Opening device 1\n"
            pair = outer[:j] + "Opening device 0\n" + outer[j:]
            f_, c_, inf = host_records(line[:k] + pair + line[k:] + "\n", a)
            if f_ != [rec] or sorted(inf["runtime_lines"]) != ["Opening device 0", "Opening device 1"] or inf["unparsed"]:
                bad.append(f"two nested runtime lines (the inner at {j}) at offset {k} of a record")
                break
        else:
            continue
        break
    if runtime_cards(["Opening device 1", "Opening device 0", "x"]) != ["1", "0"] or runtime_cards([]) != []:
        bad.append("runtime_cards")
    f_, c_, inf = host_records(line[:40] + "\n", a)
    if f_ or inf["unparsed"] != 1:
        bad.append("a cut record was read")
    f_, c_, inf = host_records(line.replace('"0xffffffff"', '"0xf"') + "\n", a)
    if f_ or len(inf["mismatched"]) != 1:
        bad.append("a record of another mask was read")
    f_, c_, inf = host_records(line.replace('"gemmLn3x5x7"', '"gemmL3x5x7"', 1) + "\n", a)
    if f_ or len(inf["mismatched"]) != 1:
        bad.append("a record of another arm family was read")
    if config_json("Opening device 0\n" + '{"tdp_w":0,"temp_threshold_c":65,"minion_mhz":600}\n') != {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600} \
            or config_json('{"tdp_w":0,"temp_th') != {}:
        bad.append("config_json")
    if not config_ok("A", {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600, "minion_mv": 523}) or config_ok("A", {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 600}) \
            or config_ok("A", {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 800}) or config_ok("B", {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600}):
        bad.append("the start config")
    if gate_c("A", 50.0) != 54.0 or gate_c("A", 58.0) != 60.0 or gate_c("A", None) is not None:
        bad.append("the die gate")
    try:
        sequence("B")
        bad.append("an arm B sequence")
    except KeyError:
        pass
    if abs(RUN_MAX_S - 28.0) > 1e-9:
        bad.append("RUN_MAX_S")
    return bad


if __name__ == "__main__":
    import sys
    b = selfcheck()
    print("E211-COMMON SELF-CHECK " + ("PASS" if not b else "FAIL: " + "; ".join(b)))
    sys.exit(0 if not b else 1)
