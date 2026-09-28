#!/usr/bin/env python3
"""Heat placement (HP, DESIGN2): parameters, block plans, Williams orders, statistics, run observables, the live
watcher, the post-run checks, the pre-registration lock and the dry-run simulator. Standard library only (reduce.py
adds numpy for the kappa fit).

Subcommands (block.sh, probe.sh and a2/block.sh call them; every one prints plain text a shell can read):
  plan --pass P --card C                       the block's runs, one "RUN ..." line each, and "SET k=v" lines; refuses a
                                               block kind the card may not run (ALLOWED) and aifoundry1 card 0 always
  params --pass P --card C | --a2              the resolved parameters as SET lines (ranges of DESIGN2 §5.5 checked);
                                               --a2: the fixed DEFAULTS only (a2/block.sh: no params file is read)
  envcheck --mode dev|val|a2 [--card C]       exit 1 if an override variable is set without V3_DRY (HP_PARAMS_DIR,
                                               HP_PREREG_DIR, the a2 bypasses; V3_FORCE for val, a2 and every
                                               aifoundry1-c1 block); prints the overrides and recorded variables set
  vallock --card C [--bins F] [--data D]      validation's PREREG lock (DESIGN2 §6.3): PREREG.md against PREREG.sha256
                                               and against HP_PREREG_SHA256 (the value recorded outside the tree;
                                               required outside V3_DRY), every file and binary hashed in PREREG.md,
                                               params-val field by field against prereg.json, no validation block
                                               under another PREREG
  a2lock --prereg a2/prereg-a2.json [--bin ..] the PREREG-A2 lock (files and binaries in PREREG-A2.md)
  binhash role=path ...                        {role: {path, sha256}} of the binaries a block would run
  level-begin/level-mark/level-show --state F  the SP log level's per-card state (the level first found, a pending set)
  v0final --data DIR --card C [--write F]      V0's settled S_L and S_L8 (S_L8 only while L8 or G8 is kept; prereg.py --val requires the file)
  watch --tel RAW --state F --ctl F ...        the live watcher of one run (safety stops, edge, first 66, guard)
  runcheck --out DIR --idx I --card C         void reasons of one run from its files (JSON)
  blockcheck --out DIR --card C                runs to re-run at the block's end (void, or WORK outside +-5%), with
                                               the round and params of the block's own plan.json; exit 1 if it cannot
  guardcheck --guard RAW                       card 0's guard: exit 0 if fresh and <= the gate, else 1
  preregcheck --prereg prereg.json             exit 0 if every hashed file is unchanged
  v0edge --data DIR --card C --target L|L8     the next V0 calibration edge from the finished V0 blocks
  sessionfirst --data DIR                      "1" if no hp block ended on this card within the session gap
  dry-sampler|dry-heater|dry-die|dry-sptrace|dry-config|dry-loglevel   the V3_DRY=1 simulator (below)
  selftest                                     Williams, statistics and outcome-rule checks

Pass numbers (queue.sh needs a number): pass = R*1000 + T*100 + k, k = 1..99 the block's index.
  R: 0 R0, 1 R1, 2 R2, 3 R3 (development, aifoundry3), 5 V0 (card-1 calibration), 9 val (validation)
  T: 1 S, 2 L16, 3 L8, 4 G8, 5 CAL (V0 chains), 6 SCOUT (R1b), 7 B1 (the one-shot), 8 PROBE, 9 SMOKE
  e.g. 801 = the R0 probe, 901 = the R0 smoke, 1701 = R1a's one-shot, 1601-1603 = R1b scouting, 1101 = R1's first
  S block, 1201 = R1's first L16 block, 9201 = the first validation L16 block.
"""
import bisect
import glob
import gzip
import hashlib
import json
import math
import os
import random
import re
import signal
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def _find_root(d):
    """The tree root (the directory holding tools/claims-v3/lib.sh): hp/ is 3 levels down, the frozen a2/ copy 4."""
    x = d
    for _ in range(6):
        if os.path.exists(os.path.join(x, "tools", "claims-v3", "lib.sh")):
            return x
        x = os.path.dirname(x)
    return os.path.abspath(os.path.join(d, "..", "..", ".."))


ROOT = _find_root(HERE)

ROUNDS = {0: "r0", 1: "r1", 2: "r2", 3: "r3", 5: "v0", 9: "val"}
TYPES = {1: "S", 2: "L16", 3: "L8", 4: "G8", 5: "CAL", 6: "SCOUT", 7: "B1", 8: "PROBE", 9: "SMOKE"}
CARD_INDEX = {"aifoundry2": 2, "aifoundry3": 3, "aifoundry1-c1": 11}
# aifoundry1 card 0 overheats and is never used (owner, 27 Sep 2026; DESIGN2 §0): every entry point refuses it
FORBIDDEN_CARDS = {"aifoundry1-c0": "aifoundry1 card 0 is never used (owner decision, DESIGN2 §0): only the read-only "
                                    "card-0 guard of a card-1 block reads it"}
# Which block kinds may run on which card (DESIGN2 §0, §5.2, §6): development (R1-R3, the one-shot, scouting) only on
# aifoundry3; card 1 of aifoundry1 only R0 (probe, smoke), V0 and validation; aifoundry2 only a2/block.sh (its own
# frozen session), never hp/block.sh or hp/probe.sh.
ALLOWED = {
    "aifoundry3": {"r0": {"PROBE", "SMOKE"}, "r1": {"B1", "SCOUT", "S", "L16", "L8", "G8", "SMOKE"},
                   "r2": {"S", "L16", "L8", "G8", "SMOKE"}, "r3": {"S", "L16", "L8", "G8", "SMOKE"}},
    "aifoundry1-c1": {"r0": {"PROBE", "SMOKE"}, "v0": {"CAL"}, "val": {"S", "L16", "L8", "G8"}},
}


class Refused(ValueError):
    """A card or block kind that must not run (the shell exits 2 on it)."""


def check_card(card):
    if card in FORBIDDEN_CARDS:
        raise Refused("%s: %s" % (card, FORBIDDEN_CARDS[card]))
    if card not in CARD_INDEX:
        raise Refused("unknown card %r" % card)


def check_allowed(rnd, typ, card):
    """Refuse a block kind the card may not run (ALLOWED); aifoundry2 runs only a2/block.sh."""
    check_card(card)
    if card == "aifoundry2":
        raise Refused("aifoundry2 runs only tools/claims-v3/hp/a2/block.sh (its frozen same-day session), never "
                      "hp/block.sh or hp/probe.sh: heating it would spoil the a2 rest reading")
    kinds = ALLOWED.get(card, {})
    if typ not in kinds.get(rnd, set()):
        raise Refused("%s may not run a %s block of round %s (allowed: %s)" % (
            card, typ, rnd, "; ".join("%s %s" % (r, "/".join(sorted(t))) for r, t in sorted(kinds.items()))))

# ------------------------------------------------------------------------------------------ fixed parameters
# Everything here is fixed by DESIGN2 before any data. The development rounds may change only the keys in RANGES,
# within those ranges (DESIGN2 §5.5); params files carry the round's values.
DEFAULTS = {
    "S_L": 60, "S_L8": 63, "S_S": 64,               # start edges (the mean's S+1 -> S falling edge)
    "target_S": 68, "target_L_over": 2, "target_L8_over": 2,   # preheat targets: 68 for S, S_L + 2, S_L8 + 2
    "preheat_max_bursts": 30, "preheat_stop_c": 80, "preheat_s": 2, "preheat_run": "ALL24",
    "edge_wait_cap_s": 600,
    "chain_cap_s": 150, "chain_launch_s": 2, "chain_after_66": 2,
    "S_launch_s": 7, "S_idle_after_s": 10,
    "C_S": 7.0, "C_L": 150.0,
    "kappa_gate": 0.90,
    "void_tauc_lo": 0.5, "void_tauc_hi": 2.0, "void_widle_range_w": 1.0, "void_work": 0.05,
    "abs_stop_c": 90, "cap_mean_c": 80, "cap_high_c": 85, "cap_board_w": 73, "cap_consecutive": 2,
    "guard_gate_c": 85, "guard_stop_c": 90, "guard_stale_s": 10, "guard_widle_rise_w": 2.0,
    "guard_max_s": 2700, "guard_refresh_s": 1500,   # the guard sampler's lifetime; restarted between runs after 1500 s
    "sampler_stale_s": 3, "sampler_every_ms": 100, "reset_ms": 1000,
    "session_gap_s": 1800,
    "band_t": math.log(1.10), "band_kappa": 0.05, "band_conc_c": 0.5, "band_map_c": 0.5,
    "band_power_w": 0.5, "band_work": 0.01, "reg_factor": 0.7,
    "n_min": 5, "n_max": 12,
    "types": ["S", "L16", "L8", "G8"],
    "trigb": "auto",                 # auto: WARNING and a dump after each run only on a card whose probe was ALIVE
}
RANGES = {
    "S_L": (59, 62), "S_L8": (61, 64), "target_L_over": (0, 4), "target_L8_over": (0, 4),
    "target_S": (66, 70), "chain_cap_s": (100, 150), "C_L": (100.0, 150.0), "kappa_gate": (0.85, 0.97),
    "void_tauc_lo": (0.33, 0.5), "void_tauc_hi": (2.0, 3.0), "void_widle_range_w": (0.5, 2.0),
}
# Validation's own edge ranges (DESIGN2 §6.1 V0): card 1's calibration may settle S_L at 58-62 and S_L8 at 60-64
VAL_RANGES = dict(RANGES, S_L=(58, 62), S_L8=(60, 64))
# Keys a round's params file may carry besides DEFAULTS' keys (metadata and frozen registration facts), per round
EXTRA_KEYS = {"v0": {"T_cal_s", "L8_offset"}, "val": {"trigb_registered", "beta", "primary", "card", "round", "frozen_from"}}
TRIGB_VALUES = ("auto", "off")      # "auto": WARNING only on an ALIVE probe (O2); "off": never. There is no "on".
EXPECTED_MHZ = {"aifoundry3": 600, "aifoundry1-c1": 600, "aifoundry2": None}

# Block contents (DESIGN2 §4.3). Every block starts with its burn-in CAL run(s) (§4.4).
BLOCK_SETS = {
    "S": ["INT16@32", "PER16@32", "UNI32@16", "B4NE", "B4NE", "B4SW", "B4SW"],
    "L16": ["INT16@32", "PER16@32", "UNI32@16"],
    "L8": ["MEM8", "EDGE8", "CEN8", "INT16@16", "PER16@16", "UNI32@16"],
    "G8": ["W8b", "E8b", "N8b", "S8b"],
}


def load_json(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def placements():
    return load_json(os.path.join(HERE, "placements.json"))


def decode_pass(p):
    p = int(p)
    R, T, k = p // 1000, (p // 100) % 10, p % 100
    if R not in ROUNDS or T not in TYPES or not 1 <= k <= 99:
        raise ValueError("pass %d: expected R*1000 + T*100 + k (R in %s, T in %s, k 1-99)" % (p, sorted(ROUNDS), sorted(TYPES)))
    return ROUNDS[R], TYPES[T], k


def dry():
    return bool(os.environ.get("V3_DRY"))


# Override variables: honoured only under V3_DRY=1 (dry tests with made-up frozen values); on a card they are refused.
# V3_FORCE (lib.sh's block_begin re-runs a finished block into its own directory: runs.jsonl truncated, telemetry
# overwritten) is refused for validation and a2 blocks and for every block on aifoundry1 card 1 (R0, V0, validation:
# nothing there is re-run over its own data; DESIGN2 §6.4 no iteration). a2/block.sh runs its frozen copy of this file,
# so for a2 the refusal is in tools/claims-v3/hp/run_a2.sh (README).
OVERRIDES = {"dev": ["HP_PARAMS_DIR", "HP_PREREG_DIR"], "val": ["HP_PARAMS_DIR", "HP_PREREG_DIR", "V3_FORCE"],
             "a2": ["HP_PARAMS_DIR", "HP_PREREG_DIR", "HP_A2_ANY_DAY", "HP_A2_NO_GAP", "HP_A2_IN_QUEUE", "V3_FORCE"]}
CARD_OVERRIDES = {"aifoundry1-c1": ["V3_FORCE"]}
# recorded whenever set (marks.jsonl block_begin "overrides", prereg-lock.json), honoured or not
RECORDED = ["V3_FORCE", "HP_BIN_ROOT", "HP_HEATER", "HP_ETTELEM", "HP_ETTELEM_HP"]


def envcheck(mode, card=None):
    """(ok, every override or recorded variable set, the refused ones set): a refused variable without V3_DRY fails."""
    refused = list(OVERRIDES.get(mode, OVERRIDES["a2"])) + CARD_OVERRIDES.get(card or "", [])
    bad = sorted({k for k in refused if os.environ.get(k)})
    found = sorted(set(bad) | {k for k in RECORDED if os.environ.get(k)})
    return (dry() or not bad), found, bad


def override_dir(var, default):
    v = os.environ.get(var)
    if v and not dry():
        raise Refused("%s is honoured only under V3_DRY=1 (a dry test); on a card the frozen files are used" % var)
    return v or default


def params_file(rnd, card):
    # HP_PARAMS_DIR overrides the directory, under V3_DRY only (dry tests of V0 and validation with made-up values)
    d = override_dir("HP_PARAMS_DIR", os.path.join(HERE, "params"))
    return os.path.join(d, "params-%s-%s.json" % (rnd, card))


def ranges_of(rnd):
    return VAL_RANGES if rnd == "val" else RANGES


def resolve_params(rnd, card):
    """DEFAULTS, then params/params-<round>-<card>.json (if any). Keys outside RANGES may not change; trigb may be
    'auto' or 'off' only; aifoundry1 card 0 and a round the card may not run are refused."""
    check_card(card)
    if card == "aifoundry2" or rnd not in ALLOWED.get(card, {}):
        raise Refused("%s has no params for round %s (a2/block.sh reads only the fixed DEFAULTS: params --a2)" % (card, rnd))
    P = dict(DEFAULTS)
    src = params_file(rnd, card)
    over = load_json(src, None) if os.path.exists(src) else None
    notes = []
    R = ranges_of(rnd)
    if over:
        for k, v in over.items():
            if k.startswith("_") or k in EXTRA_KEYS.get(rnd, set()):
                P[k] = v
                continue
            if k not in DEFAULTS:
                raise ValueError("%s: unknown key %s" % (src, k))
            if k == "trigb":
                if v not in TRIGB_VALUES:
                    raise ValueError("%s: trigb=%r: only %s (WARNING is set only on an ALIVE probe, DESIGN2 §3.2, O2)"
                                     % (src, v, "/".join(TRIGB_VALUES)))
            elif v != DEFAULTS[k] and k not in R and k not in ("types", "n_max"):
                raise ValueError("%s: %s may not change (DESIGN2 §5.5)" % (src, k))
            if k in R and not (R[k][0] <= v <= R[k][1]):
                raise ValueError("%s: %s=%s outside %s (DESIGN2 §5.5%s)" % (src, k, v, R[k], ", §6.1" if rnd == "val" else ""))
            if k == "types" and not set(v) <= set(DEFAULTS["types"]):
                raise ValueError("%s: types may only drop block types" % src)
            P[k] = v
        notes.append(os.path.relpath(src, ROOT))
        # C (Tier L's censoring time) IS the chain cap (DESIGN2 §2.1): a file that sets only chain_cap_s carries C_L
        # with it (review low: C_L 150 with a 100 s chain would enter a run heated for 100 s as ln 150)
        if "chain_cap_s" in over and "C_L" not in over:
            P["C_L"] = float(P["chain_cap_s"])
    if float(P["C_L"]) != float(P["chain_cap_s"]):
        raise ValueError("%s: C_L=%s differs from chain_cap_s=%s: C is the chain cap (DESIGN2 §2.1), so both change "
                         "together" % (os.path.relpath(src, ROOT), P["C_L"], P["chain_cap_s"]))
    P["_params_source"] = notes[0] if notes else "defaults"
    return P


def a2_params():
    """a2/block.sh's limits: the fixed DEFAULTS, no params file (PREREG-A2 freezes a2/params-a2.json separately)."""
    P = dict(DEFAULTS)
    P["_params_source"] = "defaults (a2)"
    return P


# ----------------------------------------------------------------------------------------------- Williams orders
def williams(m):
    """Williams (carryover-balanced) Latin square sequences for m treatments: m sequences for even m, 2m for odd m.
    Over the full set every treatment follows every other treatment equally often."""
    base = [0]
    lo, hi = 1, m - 1
    for j in range(1, m):
        if j % 2:
            base.append(lo); lo += 1
        else:
            base.append(hi); hi -= 1
    rows = [[(b + r) % m for b in base] for r in range(m)]
    if m % 2:
        rows += [list(reversed(r)) for r in rows]
    return rows


def check_williams(m):
    rows = williams(m)
    cnt = {}
    for r in rows:
        assert sorted(r) == list(range(m))
        for a, b in zip(r, r[1:]):
            cnt[(a, b)] = cnt.get((a, b), 0) + 1
    vals = set(cnt.values())
    assert len(cnt) == m * (m - 1) and len(vals) == 1, (m, cnt)
    return len(rows), vals.pop()


def block_seed(card, pass_no):
    # DESIGN2 §6.3 says "1000 x card index + pass"; the passes here have four digits, so 100000 keeps seeds unique
    return 100000 * CARD_INDEX.get(card, 0) + int(pass_no)


def plan(pass_no, card, first_of_session=False):
    rnd, typ, k = decode_pass(pass_no)
    check_allowed(rnd, typ, card)
    P = resolve_params(rnd, card)
    PL = placements()["runs"]
    seed = block_seed(card, pass_no)
    runs = []

    def add(role, name, tier, edge, target):
        r = PL[name]
        runs.append({"role": role, "name": name, "mask": r["mask"], "per_shire": r["per_shire"],
                     "minions": r["minions"], "tier": tier, "edge": edge, "target": target})
    info = {"pass": int(pass_no), "round": rnd, "type": typ, "k": k, "card": card, "seed": seed,
            "first_of_session": bool(first_of_session), "params_source": P["_params_source"]}
    tL, tL8 = P["S_L"] + P["target_L_over"], P["S_L8"] + P["target_L8_over"]
    if typ in ("S", "L16", "L8", "G8"):
        if typ not in P["types"]:
            info["skip"] = "block type %s dropped for %s/%s (params types=%s)" % (typ, rnd, card, P["types"])
            return info, runs, P
        tier = "S" if typ == "S" else "L"
        edge = {"S": P["S_S"], "L16": P["S_L"], "L8": P["S_L8"], "G8": P["S_L8"]}[typ]
        target = {"S": P["target_S"], "L16": tL, "L8": tL8, "G8": tL8}[typ]
        for _ in range(2 if first_of_session else 1):
            add("cal", "ALL24", tier, edge, target)
        names = BLOCK_SETS[typ]
        if typ == "S":
            order = list(names)
            random.Random(seed).shuffle(order)
            info["order"] = "seeded shuffle (seed %d)" % seed
        else:
            W = williams(len(names))
            idx = (k - 1 + CARD_INDEX.get(card, 0)) % len(W)
            order = [names[i] for i in W[idx]]
            info["order"] = "Williams sequence %d of %d (m=%d)" % (idx, len(W), len(names))
            info["williams_index"] = idx
        for n in order:
            add("meas", n, tier, edge, target)
    elif typ == "SCOUT":                      # R1b (DESIGN2 §5.2), split in three blocks
        if k == 1:
            add("cal", "ALL24", "L", P["S_L"], tL); add("cal", "ALL24", "L", P["S_L"], tL)
            add("meas", "UNI32@16", "L", P["S_L"], tL); add("meas", "UNI32@16", "L", P["S_L"], tL)
        elif k == 2:
            add("cal", "ALL24", "L", P["S_L8"], tL8)
            for n in ("CEN8", "W8b", "CEN8"):
                add("meas", n, "L", P["S_L8"], tL8)
        else:
            add("cal", "ALL24", "S", P["S_S"], P["target_S"])
            add("meas", "UNI32@16", "S", P["S_S"], P["target_S"]); add("meas", "UNI32@16", "S", P["S_S"], P["target_S"])
    elif typ == "CAL":                        # V0 on card 1: 3 ALL24 chains at the edge v0edge chooses
        tgt = "L8" if k >= 11 else "L"
        if not 1 <= (k - 10 if tgt == "L8" else k) <= 3:
            raise Refused("V0 pass %d: k must be 1-3 (S_L edges) or 11-13 (S_L8 edges)" % int(pass_no))
        if tgt == "L8" and not l8_kept(P["types"]):
            info["skip"] = "V0 L8: L8 and G8 dropped (params types=%s): no S_L8 series (README departure 36)" % P["types"]
            return info, runs, P
        e = v0_edge(os.environ.get("HP_DATA_DIR", ""), card, tgt, P)
        info["v0"] = e
        if e.get("edge") is None:
            info["skip"] = "V0 %s: %s" % (tgt, e.get("why"))
            return info, runs, P
        for _ in range(3):
            add("meas", "ALL24", "L", e["edge"], e["edge"] + 2)
    elif typ == "B1":                         # ONE chain of <= chain_cap_s (O1); no second chain (README)
        add("meas", "INT16@32", "B1", None, None)
    elif typ == "SMOKE":
        add("meas", "INT16@32", "SMOKE", None, None)
    return info, runs, P


V0_BASE = {"L": 5500, "L8": 5510}
V0_LIMITS = {"L": (58, 62), "L8": (60, 64)}


def v0_series(data_dir, card, target, P):
    """The finished V0 blocks of one target (5501-5503 for S_L, 5511-5513 for S_L8), in order: [{pass, edge, t66,
    censored}] (each block's 3 ALL24 chains; void chains left out)."""
    done = []
    for j in range(1, 4):
        pno = V0_BASE[target] + j
        d = os.path.join(data_dir, "hp", "p%d" % pno)
        bj = load_json(os.path.join(d, "block.json"))
        if not bj or bj.get("status") != "ok":
            break
        pl = load_json(os.path.join(d, "plan.json"), {}) or {}
        if (pl.get("info") or {}).get("skip"):
            break
        rs = [r for r in load_jsonl(os.path.join(d, "runs.jsonl")) if r.get("role") == "meas"]
        t, cens, lnt = [], False, []
        for r in rs:
            o = run_observables(r, load_jsonl(os.path.join(d, "tel-%s.jsonl" % r["idx"])),
                                heater_lines(os.path.join(d, "heater-%s.out" % r["idx"])), card, P)
            if o.get("void"):
                continue
            t.append(o.get("t66_s") if not o.get("censored") else None)
            if o.get("t66_c"):
                lnt.append(math.log(o["t66_c"]))
            cens = cens or bool(o.get("censored"))
        done.append({"pass": pno, "edge": rs[0]["edge"] if rs else None, "t66": t, "censored": cens, "ln_t66_c": lnt})
    return done


def v0_edge(data_dir, card, target, P):
    """DESIGN2 §6.1 V0. S_L: start at aifoundry3's frozen S_L; S_L8: start at CARD 1's settled S_L + the frozen L8
    offset (the offset is kept), so the S_L8 series waits until the S_L series has settled. After each edge's 3
    chains: median < 0.5 T_cal -> lower by 1; > 2 T_cal or any censored -> raise by 1; within 58-62 (S_L) or 60-64
    (S_L8); at most 3 edges. T_cal: aifoundry3's median CAL t66 at its frozen edge (params-v0-<card>.json).
    Returns {'edge': the next edge to run, or None with 'why' and, once settled, 'final' and 'final_pass'}."""
    T_cal = (P.get("T_cal_s") or {}).get(target)
    if T_cal is None:
        return {"edge": None, "why": "T_cal_s[%s] not in params-v0-%s.json (written after R3)" % (target, card)}
    if target == "L":
        start = P["S_L"]
    else:
        L = v0_edge(data_dir, card, "L", P)
        if L.get("final") is None:
            return {"edge": None, "why": "the S_L8 series starts from card 1's settled S_L + the L8 offset; S_L is not "
                                         "settled yet (%s)" % (L.get("why") or "S_L chains still to run")}
        start = L["final"] + int(P.get("L8_offset", P["S_L8"] - P["S_L"]))
    lo, hi = V0_LIMITS[target]
    if not lo <= start <= hi:
        return {"edge": None, "why": "start edge %s outside %s-%s" % (start, lo, hi)}
    done = v0_series(data_dir, card, target, P)
    e = start
    prev = None
    base = {"done": done, "T_cal_s": T_cal, "start": start, "target": target}
    for d in done:
        tt = sorted(x for x in d["t66"] if x is not None)
        med = tt[len(tt) // 2] if tt else None
        if not d["t66"]:                  # every chain void (e.g. an edge below the card's rest is never reached)
            if prev is None:
                return dict(base, edge=None, why="no valid chain at the start edge %s: V0 cannot settle" % d["edge"])
            return dict(base, edge=None, why="edge %s gave no valid chain: settled at the previous edge %s" % (
                d["edge"], prev["edge"]), final=prev["edge"], final_pass=prev["pass"])
        if d["censored"] or (med is not None and med > 2 * T_cal):
            nxt = d["edge"] + 1
        elif med is not None and med < 0.5 * T_cal:
            nxt = d["edge"] - 1
        else:
            return dict(base, edge=None, why="settled at %s (median %s s, T_cal %s s)" % (d["edge"], med, T_cal),
                        final=d["edge"], final_pass=d["pass"])
        if not lo <= nxt <= hi:
            return dict(base, edge=None, why="edge limit reached at %s" % d["edge"], final=d["edge"], final_pass=d["pass"])
        prev = d
        e = nxt
    if len(done) >= 3:
        return dict(base, edge=None, why="3 edges used", final=done[-1]["edge"], final_pass=done[-1]["pass"])
    return dict(base, edge=e)


def l8_kept(types):
    """True if L8 or G8 (the block types that run at S_L8) is among the kept block types (params 'types')."""
    return bool({"L8", "G8"} & set(types or ()))


def v0_final(data_dir, card, P):
    """V0's result for PREREG: {'S_L', 'S_L8', 'complete', 'L', 'L8', 'types'} (prereg.py --val refuses an incomplete
    one). S_L8 is required only while L8 or G8 is kept (params-v0's 'types'); with both dropped (D-L8) the S_L8 series
    never runs, S_L8 stays None and V0 is complete once S_L has settled (README departure 36)."""
    L = v0_edge(data_dir, card, "L", P)
    need8 = l8_kept(P.get("types"))
    L8 = v0_edge(data_dir, card, "L8", P) if need8 else {
        "edge": None, "why": "L8 and G8 dropped (params types=%s): S_L8 not needed" % P.get("types")}
    out = {"card": card, "S_L": L.get("final"), "S_L8": L8.get("final"),
           "L": {k: v for k, v in L.items() if k != "done"}, "L8": {k: v for k, v in L8.items() if k != "done"},
           "L8_offset": P.get("L8_offset"), "T_cal_s": P.get("T_cal_s"), "types": list(P.get("types") or [])}
    out["complete"] = out["S_L"] is not None and (out["S_L8"] is not None or not need8)
    return out


# ----------------------------------------------------------------------------------------------- statistics
T995 = {1: 63.657, 2: 9.925, 3: 5.841, 4: 4.604, 5: 4.032, 6: 3.707, 7: 3.499, 8: 3.355, 9: 3.250, 10: 3.169,
        11: 3.106, 12: 3.055, 13: 3.012, 14: 2.977, 15: 2.947, 16: 2.921, 17: 2.898, 18: 2.878, 19: 2.861, 20: 2.845}


def _betacf(a, b, x, itmax=300, eps=3e-14):
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > 1e-300 else 1e-300); h = d
    for m in range(1, itmax + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d; d = 1 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1 + aa / c if abs(c) > 1e-300 else 1e300
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d; d = 1 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1 + aa / c if abs(c) > 1e-300 else 1e300
        de = d * c; h *= de
        if abs(de - 1) < eps:
            break
    return h


def _betainc(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x))
    if x < (a + 1) / (a + b + 2):
        return bt * _betacf(a, b, x) / a
    return 1 - bt * _betacf(b, a, 1 - x) / b


def t_ppf(q, df):
    """Student t quantile (tools/claims-v3/wire/registered/tdist.py's method); the 0.995 table where it exists."""
    if abs(q - 0.995) < 1e-12 and df in T995:
        return T995[df]
    lo, hi = -1e3, 1e3
    for _ in range(200):
        mid = (lo + hi) / 2
        x = df / (df + mid * mid)
        p = 0.5 * _betainc(df / 2, 0.5, x)
        cdf = 1 - p if mid >= 0 else p
        if cdf < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def mean(v):
    return sum(v) / len(v) if v else None


def sd(v):
    if len(v) < 2:
        return None
    m = mean(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))


def median(v):
    v = sorted(x for x in v if x is not None)
    if not v:
        return None
    n = len(v)
    return v[n // 2] if n % 2 else 0.5 * (v[n // 2 - 1] + v[n // 2])


def ci99(vals):
    """(mean, lo, hi, n) with a two-sided 99% Student t interval, df = n - 1; None if n < 2."""
    v = [x for x in vals if x is not None]
    if len(v) < 2:
        return None
    m, s = mean(v), sd(v)
    h = t_ppf(0.995, len(v) - 1) * s / math.sqrt(len(v))
    return {"mean": m, "lo": m - h, "hi": m + h, "n": len(v), "sd": s, "half": h}


def outcome(ptype, vals, band):
    """Three outcomes (DESIGN2 §2.3): True holds, False fails, None otherwise; fewer than 3 blocks gives None.
    Precedence (fixed here before any data; README departure 18, PREREG): a CI lying wholly inside +-band FAILS a
    SIGN or NONZERO item even when it also excludes 0 (the effect is shown negligible: e.g. [0.017, 0.033] against
    band 0.095 fails SIGN+), so a significant but negligible effect never PASSes a directional item."""
    c = ci99(vals)
    if c is None or c["n"] < 3:
        return None, c
    lo, hi = c["lo"], c["hi"]
    inside = -band < lo and hi < band
    if ptype == "SIGN+":
        if hi < 0 or inside:
            return False, c
        if lo > 0:
            return True, c
        return None, c
    if ptype == "SIGN-":
        if lo > 0 or inside:
            return False, c
        if hi < 0:
            return True, c
        return None, c
    if ptype == "NONZERO":
        if inside:
            return False, c
        if lo > 0 or hi < 0:
            return True, c
        return None, c
    if ptype == "EQUIV":
        if inside:
            return True, c
        if lo > band or hi < -band:
            return False, c
        return None, c
    raise ValueError(ptype)


def card_verdicts(holds, cards):
    """V3's outcome words (tools/claims-v3/idle/reduce.py:454-463) over the registered cards."""
    vals = [holds.get(c) for c in cards]
    if not cards or any(v is None for v in vals):
        return "INSUFFICIENT"
    if all(vals):
        return "PASS"
    if not any(vals):
        return "FAIL"
    return "CARD-DIFFERENT"


def binom_two_sided(k, n):
    """Exact two-sided sign-test p (p = 0.5)."""
    if n == 0:
        return None
    pk = [math.comb(n, i) / 2.0 ** n for i in range(n + 1)]
    return min(1.0, sum(p for p in pk if p <= pk[k] + 1e-12))


def projected_half(s, n):
    """h(n) = t(0.995, n-1) s / sqrt(n) (DESIGN2 §2.4)."""
    return t_ppf(0.995, n - 1) * s / math.sqrt(n) if n >= 2 and s is not None else None


# ----------------------------------------------------------------------------------------------- telemetry
def open_any(path):
    if path.endswith(".gz"):
        return gzip.open(path, "rt", errors="replace")
    return open(path, errors="replace")


def load_jsonl(path):
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path += ".gz"
    out = []
    if not os.path.exists(path):
        return out
    with open_any(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("{"):
                try:
                    out.append(json.loads(line))
                except Exception:
                    pass
    return out


def sample_fields(s):
    """(t_ms, mean, low, high, board_w, mhz, io_high, since_reset) of one sampler line (None where absent)."""
    tc = s.get("temp_c") or {}
    ms = tc.get("minshire") or [None, None, None]
    io = tc.get("ioshire") or [None, None, None]
    return (s.get("t_ms"), ms[0], ms[1], ms[2], s.get("board_w"), (s.get("mhz") or {}).get("minion"), io[2],
            s.get("since_reset_ms"))


def heater_lines(path):
    """The heater's SPARSITY JSON lines (launch -1 is the calibration launch of each process)."""
    out = []
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path += ".gz"
    if not os.path.exists(path):
        return out
    with open_any(path) as f:
        for line in f:
            if line.startswith("SPARSITY {"):
                try:
                    out.append(json.loads(line[9:]))
                except Exception:
                    pass
    return out


def session_anchors(d):
    """Every heater process of a block or session directory, as tick-fit anchors (DESIGN2 §3.3): its first kernel
    start (the launch -1 line's t_start_ms) and its last kernel end (the t_end_ms of its last SPARSITY line: the master
    minion goes idle there, and the governor's idle event follows within one SP pass), from every heater-*.out[.gz]
    (preheat, lifts, probe and smoke included). With the card lock held no one else launched, so every SP power line
    in the span must sit within one SP pass of one of these."""
    out = []
    for f in sorted(glob.glob(os.path.join(d, "heater-*.out")) + glob.glob(os.path.join(d, "heater-*.out.gz")) +
                    glob.glob(os.path.join(d, "probe", "heater-*.out*"))):
        cur = None
        for h in heater_lines(f):
            if h.get("launch") == -1:
                if cur:
                    out += [(cur[0], "start"), (cur[1], "end")]
                cur = [h["t_start_ms"], h["t_end_ms"]]
            elif cur:
                cur[1] = max(cur[1], h["t_end_ms"])
        if cur:
            out += [(cur[0], "start"), (cur[1], "end")]
    return sorted(set(out))


def windows(samples, reset_ms=1000):
    """Reset windows of a --reset-ms sampler: a sample with since_reset_ms >= reset_ms closes its window (ettelem
    resets after reading it). A window lasting > 1.5 reset_ms or with < 3 samples is a failed reset, dropped."""
    out, cur = [], []
    for s in samples:
        cur.append(s)
        sr = s.get("since_reset_ms")
        if sr is not None and sr >= reset_ms:
            out.append(cur); cur = []
    res = []
    for w in out:
        f = [sample_fields(s) for s in w]
        dur = f[-1][7]
        ok = len(w) >= 3 and dur is not None and dur <= 1.5 * reset_ms
        means = [x[1] for x in f if x[1] is not None]
        highs = [x[3] for x in f if x[3] is not None]
        ios = [x[6] for x in f if x[6] is not None]
        res.append({"t_end": f[-1][0], "t_start": f[0][0], "ok": ok, "max_mean": max(means) if means else None,
                    "max_high": max(highs) if highs else None, "max_io": max(ios) if ios else None})
    return res


def run_observables(run, tel, hl, card, P):
    """DESIGN2 §2.1 for one run. run: its runs.jsonl record; tel: its sampler lines; hl: its SPARSITY lines."""
    o = {"idx": run.get("idx"), "name": run.get("name"), "role": run.get("role"), "tier": run.get("tier"),
         "edge": run.get("edge"), "void": [], "flags": []}
    if run.get("stop"):
        o["void"].append("safety stop %s" % run["stop"])
    if any(rc != 0 for rc in run.get("rcs", [])):
        o["void"].append("heater rc %s" % [rc for rc in run.get("rcs", []) if rc != 0])
    if run.get("tier") in ("S", "L") and run.get("role") != "warmup" and not run.get("edge_ok", True):
        o["void"].append("edge not reached")
    meas = [h for h in hl if h.get("launch", -1) >= 0]
    if not hl:
        o["void"].append("no heater output")
        return o
    t0 = min(h["t_start_ms"] for h in hl)
    t_end = max(h["t_end_ms"] for h in hl)
    o["t0_ms"], o["t_end_ms"] = t0, t_end
    o["launch_s"] = (t_end - t0) / 1000.0
    F = [sample_fields(s) for s in tel if s.get("t_ms") is not None]
    F.sort(key=lambda x: x[0])
    if not F:
        o["void"].append("no telemetry")
        return o
    pre = [x for x in F if t0 - 2000 <= x[0] < t0 and x[4] is not None]
    W_idle = median([x[4] for x in pre])
    o["W_idle"] = W_idle
    need = 3.0 if run.get("minions", 0) >= 512 else 1.5
    chk = [x for x in F if t0 <= x[0] <= t0 + 600 and x[4] is not None]
    o["t0_check"] = bool(W_idle is not None and any(x[4] >= W_idle + need for x in chk))
    if not o["t0_check"]:
        o["flags"].append("t0 check: board_w did not rise %.1f W within 0.6 s" % need)
    C = P["C_S"] if run.get("tier") == "S" else (P["C_L"] if run.get("tier") in ("L", "B1") else P["C_S"])
    after = [x for x in F if x[0] >= t0]
    hit = next((x for x in after if x[1] is not None and x[1] >= 66), None)
    t66 = (hit[0] - t0) / 1000.0 if hit else None
    cens = t66 is None or t66 > C
    o["t66_s"] = t66
    o["censored"] = cens
    o["t66_c"] = min(t66, C) if t66 is not None else C
    o["ln_t66_c"] = math.log(o["t66_c"]) if o["t66_c"] > 0 else None
    o["C"] = C
    t_meas_end = min(t0 + (t66 if t66 is not None else 1e9) * 1000.0, t_end)
    win = [x for x in F if t0 + 1000 <= x[0] <= t_meas_end and x[4] is not None]
    o["sw_W"] = median([x[4] - W_idle for x in win]) if W_idle is not None and win else None
    it = sum(h.get("iters", 0) for h in meas)
    ws = sum(h.get("wall_s", 0.0) for h in meas)
    o["ops_rate"] = it / ws if ws > 0 else None
    o["ghz"] = median([h.get("ghz") for h in meas])
    # clock: every sample of the measured window at the card's expected clock
    exp = EXPECTED_MHZ.get(card)
    inwin = [x for x in F if t0 <= x[0] <= t_end]
    off = [x[5] for x in inwin if x[5] is not None and exp is not None and x[5] != exp]
    if off:
        o["void"].append("clock off %d MHz in %d samples" % (exp, len(off)))
    o["mhz_set"] = sorted({x[5] for x in inwin if x[5] is not None})
    # sampler gap in the measured window
    ts = [x[0] for x in F if t0 - 2000 <= x[0] <= t_end]
    gap = max((b - a for a, b in zip(ts, ts[1:])), default=None)
    o["max_gap_ms"] = gap
    if gap is None or gap > 1000 or not ts or ts[0] > t0 or ts[-1] < t_end - 1000:
        o["void"].append("sampler gap > 1 s in the measured window (max %s ms)" % gap)
    # tau_c from the telemetry: the falling S+1 -> S edge before t0
    S = run.get("edge")
    if S is not None:
        # the watcher's edge rule (DESIGN2 §4.4), offline: after the last reading >= S+2 before t0, s1 = the first S+1
        # and the edge = the first reading <= S after s1; no reading >= S+2 before t0 -> no tau_c (a flickering integer
        # mean at the edge does not move it: the first crossing is the one the block launched on)
        pre = [x for x in F if x[0] < t0 and x[1] is not None]
        k = max((i for i, x in enumerate(pre) if x[1] >= S + 2), default=None)
        s1 = e = None
        if k is not None:
            for x in pre[k + 1:]:
                if s1 is None and x[1] == S + 1:
                    s1 = x[0]
                elif s1 is not None and x[1] <= S:
                    e = x[0]
                    break
        o["tau_c_s"] = (e - s1) / 1000.0 if s1 is not None and e is not None else None
        o["edge_to_t0_s"] = (t0 - e) / 1000.0 if e is not None else None
        o["tau_c_live_s"] = run.get("tau_c_s")
    # peak-hold windows: Delta-hot and iota_io
    Wn = [w for w in windows(tel, P.get("reset_ms", 1000)) if w["ok"]]
    def last3(t_lim):
        ws_ = [w for w in Wn if w["t_end"] <= t_lim][-3:]
        return ws_ if len(ws_) == 3 else None
    b_pre, b_hot, b_io = last3(t0), last3(t_meas_end), last3(t_end)
    if b_pre and b_hot:
        f = lambda ws_: mean([w["max_high"] - w["max_mean"] for ws2 in [ws_] for w in ws2])
        o["dhot"] = f(b_hot) - f(b_pre)
    if b_pre and b_io:
        g = lambda ws_: mean([w["max_io"] for w in ws_])
        o["iota_io"] = g(b_io) - g(b_pre)
    last = [x for x in F if t_end - 3000 <= x[0] <= t_end]
    raw_io = [s for s in tel if t_end - 3000 <= (s.get("t_ms") or 0) <= t_end]
    pre2 = [s for s in tel if t0 - 2000 <= (s.get("t_ms") or 0) < t0]
    def io_minus_mean(ss):
        v = [((s.get("temp_c") or {}).get("ioshire") or [None])[0] - ((s.get("temp_c") or {}).get("minshire") or [None])[0]
             for s in ss if (s.get("temp_c") or {}).get("ioshire") and (s.get("temp_c") or {}).get("minshire")]
        return mean(v)
    a, b = io_minus_mean(raw_io), io_minus_mean(pre2)
    o["iota_D86"] = a - b if a is not None and b is not None else None
    o["n_samples"] = len(last)
    return o


# ----------------------------------------------------------------------------------------------- virtual time
def vnow_ms():
    """Wall-clock ms; under V3_DRY=1 with HP_DRY_SPEED the simulator's accelerated clock (shared with the shell)."""
    r = time.time() * 1000.0
    if dry():
        vt0 = float(os.environ.get("HP_VT0", "0") or 0)
        sp = float(os.environ.get("HP_DRY_SPEED", "1") or 1)
        if vt0:
            return vt0 + (r - vt0) * sp
    return r


def vsleep(s):
    sp = float(os.environ.get("HP_DRY_SPEED", "1") or 1) if dry() else 1.0
    time.sleep(max(0.0, s / sp))


# ----------------------------------------------------------------------------------------------- the watcher
def watch(a):
    """One run's live watcher. Reads the sampler's raw output as it grows and writes one state line (atomically):
       t_ms mean high board_w mhz n stop first66_ms edge_ms tau_c_s s1_ms age_ms g_mean g_age_s wall_ms
    (wall_ms: the real clock when the line was written; the shell aborts if it is older than sampler_stale_s or
    the watcher is gone)
    Stops (sticky): ABS90 (mean or high >= abs), CAP_MEAN/CAP_HIGH/CAP_W (cap_consecutive samples in a row),
    GUARD90 (card 0's mean > guard_stop), GUARD_STALE (guard output older than guard_stale s). On any stop it creates
    the heater's --stop-file; on ABS90 and the guard stops also the session stop file (queue.sh stops)."""
    caps = dict(DEFAULTS)
    for kv in (a.get("caps") or "").split(","):
        if "=" in kv:
            k, v = kv.split("=", 1)
            caps[k] = float(v)
    tel, state, ctl = a["tel"], a["state"], a["ctl"]
    guard = a.get("guard") or ""
    stop_file, session_stop = a.get("stop_file") or "", a.get("session_stop") or ""
    pos, buf = 0, ""
    gpos, gbuf = 0, ""
    last = None
    n = 0
    consec = 0
    stop = None
    first66 = None
    edge = {"S": None, "since": None, "armed": False, "s1": None, "t": None, "tau": None}
    arm66 = None
    ctl_sig = None
    g_last = None
    t_start = vnow_ms()
    parent = os.getppid()

    hist = []

    def edge_step(t, m):
        """The falling S+1 -> S edge (DESIGN2 §4.4): armed by a reading >= S+2; s1 = the first S+1 after it; the edge is
        the first reading <= S after s1 at or after the wait began. A reading <= S before the wait disarms."""
        if edge["S"] is None or edge["t"] is not None:
            return
        S = edge["S"]
        if m >= S + 2:
            edge.update(armed=True, s1=None)
        elif m == S + 1:
            if edge["s1"] is None:
                edge["s1"] = t
        elif t >= edge["since"] and edge["s1"] is not None:
            edge["t"] = t
            edge["tau"] = (t - edge["s1"]) / 1000.0 if edge["armed"] else None
        else:
            edge.update(armed=False, s1=None)

    def set_stop(why, session=False):
        nonlocal stop
        if stop is None:
            stop = why
            for f in [stop_file] + ([session_stop] if session else []):
                if f:
                    try:
                        open(f, "a").close()
                    except Exception:
                        pass

    def write_state():
        now = vnow_ms()
        f = lambda v: "-" if v is None else (("%.3f" % v) if isinstance(v, float) else str(v))
        age = (now - last[0]) if last else None
        g_age = ((now - g_last[0]) / 1000.0) if g_last else None
        line = " ".join(f(v) for v in [last[0] if last else None, last[1] if last else None, last[3] if last else None,
                                       last[4] if last else None, last[5] if last else None, n, stop, first66,
                                       edge["t"], edge["tau"], edge["s1"], int(age) if age is not None else None,
                                       g_last[1] if g_last else None, g_age, int(time.time() * 1000)])
        tmp = state + ".tmp"
        with open(tmp, "w") as fh:
            fh.write(line + "\n")
        os.replace(tmp, state)

    while True:
        try:
            st = os.stat(ctl)
            sig = (st.st_mtime_ns, st.st_size)
            if sig != ctl_sig:
                ctl_sig = sig
                for line in open(ctl):
                    p = line.split()
                    if not p:
                        continue
                    if p[0] == "quit":
                        write_state()
                        return 0
                    if p[0] == "edge" and len(p) >= 3 and (edge["S"] != int(p[1]) or edge["since"] != float(p[2])):
                        edge.update(S=int(p[1]), since=float(p[2]), armed=False, s1=None, t=None, tau=None)
                        for ht, hm in hist:          # replay the run so far: a fall that began before the wait counts
                            edge_step(ht, hm)
                    if p[0] == "arm66" and len(p) >= 2:
                        arm66 = float(p[1])
        except FileNotFoundError:
            pass
        try:
            with open(tel, errors="replace") as fh:
                fh.seek(pos)
                chunk = fh.read()
                pos = fh.tell()
        except FileNotFoundError:
            chunk = ""
        buf += chunk
        lines = buf.split("\n")
        buf = lines.pop()
        for line in lines:
            if not line.startswith("{"):
                continue
            try:
                s = json.loads(line)
            except Exception:
                continue
            x = sample_fields(s)
            if x[0] is None or x[1] is None:
                continue
            last = x
            n += 1
            t, m, hi, w = x[0], x[1], x[3], x[4]
            if (hi is not None and hi >= caps["abs_stop_c"]) or m >= caps["abs_stop_c"]:
                set_stop("ABS90", session=True)
            bad = None
            if m >= caps["cap_mean_c"]:
                bad = "CAP_MEAN"
            elif hi is not None and hi >= caps["cap_high_c"]:
                bad = "CAP_HIGH"
            elif w is not None and w >= caps["cap_board_w"]:
                bad = "CAP_W"
            consec = consec + 1 if bad else 0
            if bad and consec >= caps["cap_consecutive"]:
                set_stop(bad)
            if arm66 is not None and first66 is None and t >= arm66 and m >= 66:
                first66 = t
            hist.append((t, m))
            edge_step(t, m)
        if guard:
            try:
                if os.path.getsize(guard) < gpos:       # the guard was restarted (a drain): its file starts again
                    gpos, gbuf = 0, ""
            except OSError:
                pass
            try:
                with open(guard, errors="replace") as fh:
                    fh.seek(gpos)
                    gchunk = fh.read()
                    gpos = fh.tell()
            except FileNotFoundError:
                gchunk = ""
            gbuf += gchunk
            gl = gbuf.split("\n")
            gbuf = gl.pop()
            for line in gl:
                if line.startswith("{"):
                    try:
                        gx = sample_fields(json.loads(line))
                    except Exception:
                        continue
                    if gx[0] is not None and gx[1] is not None:
                        g_last = gx
                        if gx[1] > caps["guard_stop_c"]:
                            set_stop("GUARD90", session=True)
            now = vnow_ms()
            # a guard with no line yet gets 30 s of grace (ref 20 s after the start + guard_stale_s): hp_guard_start
            # already waits for a first line, so this only matters if the file is replaced by an empty one
            ref = g_last[0] if g_last else t_start + 20000.0
            if now - ref > caps["guard_stale_s"] * 1000.0:
                set_stop("GUARD_STALE", session=True)
        write_state()
        try:
            os.kill(parent, 0)
        except OSError:
            return 0
        time.sleep(0.05)


# ----------------------------------------------------------------------------------------------- run checks
def runs_of(out):
    return load_jsonl(os.path.join(out, "runs.jsonl"))


def block_plan(out, card):
    """(round, params) of a block from its own plan.json: the round is under plan['info'] and the params are the ones
    recorded when the block ran (as reduce.load_blocks reads them). Never a default round (review high: reading the
    top-level 'round' made every block r1, so card 1's blockcheck raised Refused and R2/R3 blocks used R1's params)."""
    pl = load_json(os.path.join(out, "plan.json"))
    info = (pl or {}).get("info") or {}
    rnd = info.get("round")
    if not rnd:
        raise ValueError("%s: plan.json missing or without info.round" % os.path.join(out, "plan.json"))
    if info.get("card") and info["card"] != card:
        raise ValueError("%s: plan.json is for card %s, not %s" % (out, info["card"], card))
    P = pl.get("params") or resolve_params(rnd, card)
    return rnd, P


def runcheck(out, idx, card):
    rnd, P = block_plan(out, card)
    run = next((r for r in runs_of(out) if str(r.get("idx")) == str(idx)), None)
    if run is None:
        return {"idx": idx, "void": ["no run record"]}
    tel = load_jsonl(os.path.join(out, "tel-%s.jsonl" % idx))
    hl = heater_lines(os.path.join(out, "heater-%s.out" % idx))
    o = run_observables(run, tel, hl, card, P)
    return {k: o.get(k) for k in ("idx", "name", "void", "flags", "t66_s", "censored", "sw_W", "ops_rate", "tau_c_s", "W_idle")}


def blockcheck(out, card):
    """Runs to re-run once at the block's end: void runs, and runs whose WORK is outside +-void_work of the block
    median. A placement whose re-run is void again is dropped from the block (DESIGN2 §4.4)."""
    rnd, P = block_plan(out, card)
    runs = [r for r in runs_of(out) if r.get("role") == "meas"]
    obs = []
    for r in runs:
        tel = load_jsonl(os.path.join(out, "tel-%s.jsonl" % r["idx"]))
        hl = heater_lines(os.path.join(out, "heater-%s.out" % r["idx"]))
        obs.append((r, run_observables(r, tel, hl, card, P)))
    rates = [o["ops_rate"] for _, o in obs if o.get("ops_rate") and not o["void"]]
    med = median(rates)
    for r, o in obs:
        if med and o.get("ops_rate") and abs(math.log(o["ops_rate"] / med)) > P["void_work"]:
            o["void"].append("WORK outside +-%.0f%% of the block median" % (100 * P["void_work"]))
    latest = {}
    for r, o in obs:
        latest.setdefault(r["slot"], []).append((r, o))
    rerun = []
    for slot, lst in sorted(latest.items()):
        r, o = lst[-1]
        if o["void"] and len(lst) == 1:
            rerun.append({"slot": slot, "name": r["name"], "why": o["void"]})
    return {"rerun": rerun, "work_median": med, "round": rnd, "params_source": P.get("_params_source"),
            "void": {str(r["idx"]): o["void"] for r, o in obs if o["void"]}}


def guardcheck(path, gate, max_age):
    lines = [l for l in open(path, errors="replace").read().splitlines() if l.startswith("{")] if os.path.exists(path) else []
    if not lines:
        return False, "no guard line"
    try:
        x = sample_fields(json.loads(lines[-1]))
    except Exception:
        return False, "unreadable guard line"
    age = (vnow_ms() - x[0]) / 1000.0
    if age > max_age:
        return False, "guard stale %.1f s" % age
    if x[1] is None or x[1] > gate:
        return False, "card 0 mean %s C > %s" % (x[1], gate)
    return True, "card 0 mean %s C, age %.1f s" % (x[1], age)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


# ---- the pre-registration locks (DESIGN2 §6.3; README "The lock"). PREREG.md (PREREG-A2.md) is the root: its
# sha256 is in PREREG.sha256 (PREREG-A2.sha256), and it carries, between the markers below, a JSON block with the
# sha256 of every file the session or validation uses (prereg.json and params-val included) and of every binary it runs.
LOCK_BEGIN, LOCK_END = "<!-- lock-begin -->", "<!-- lock-end -->"


def rel(p):
    return os.path.relpath(os.path.abspath(p), ROOT)


def lock_block(lock):
    return "%s\n```json\n%s\n```\n%s\n" % (LOCK_BEGIN, json.dumps(lock, indent=1, sort_keys=True), LOCK_END)


def parse_lock(md_path):
    txt = open(md_path, errors="replace").read()
    if LOCK_BEGIN not in txt or LOCK_END not in txt:
        raise ValueError("%s has no lock block" % md_path)
    body = txt.split(LOCK_BEGIN, 1)[1].split(LOCK_END, 1)[0].strip()
    body = body.strip("`").strip()
    if body.startswith("json"):
        body = body[4:]
    return json.loads(body)


def binhash(pairs):
    """{role: {path, sha256}} for role=path pairs (sha256 None if the file is missing)."""
    out = {}
    for kv in pairs:
        role, path = kv.split("=", 1)
        out[role] = {"path": path, "sha256": sha256(path if os.path.isabs(path) else os.path.join(ROOT, path))
                     if os.path.isfile(path if os.path.isabs(path) else os.path.join(ROOT, path)) else None}
    return out


def md_and_sha(md_path, sha_path):
    """(ok, why, sha): PREREG.md exists and equals the hash recorded in PREREG.sha256."""
    if not os.path.exists(md_path):
        return False, "no %s" % rel(md_path), None
    h = sha256(md_path)
    want = (open(sha_path).read().split() or [""])[0] if os.path.exists(sha_path) else ""
    if h != want:
        return False, "%s (sha256 %s) differs from %s (%s)" % (rel(md_path), h[:12], rel(sha_path), want[:12] or "missing"), h
    return True, "", h


def check_lock_files(lock, bins, need_bins=True):
    """Every file hashed in the lock unchanged; every binary role the block runs has the locked sha256."""
    bad = []
    for rp, h in sorted((lock.get("files") or {}).items()):
        p = os.path.join(ROOT, rp)
        if not os.path.isfile(p):
            bad.append("%s missing" % rp)
        elif sha256(p) != h:
            bad.append("%s changed" % rp)
    lb = lock.get("binaries") or {}
    if need_bins:
        if not lb:
            bad.append("no binaries in the lock")
        for role, ent in sorted(lb.items()):
            want = ent.get("sha256")
            if want is None and not dry():
                bad.append("binary %s has no sha256 in the lock" % role)
                continue
            have = (bins or {}).get(role)
            if have is None:
                bad.append("binary %s: not given to the check" % role)
            elif have.get("sha256") != want:
                bad.append("binary %s (%s) sha256 %s != locked %s" % (role, have.get("path"), str(have.get("sha256"))[:12],
                                                                      str(want)[:12]))
    return bad


VAL_PARAMS_META = {"_what", "trigb_registered", "beta", "card", "round", "frozen_from"}


def prereg_dir():
    return override_dir("HP_PREREG_DIR", os.path.join(HERE, "prereg"))


def val_blocks_recorded(data_dir):
    """{block dir: PREREG.md sha256 it ran under} for every validation block directory (attempts included)."""
    out = {}
    for d in glob.glob(os.path.join(data_dir, "hp", "p9[0-9][0-9][0-9]*")) + glob.glob(os.path.join(data_dir, "hp-smoke", "p9[0-9][0-9][0-9]*")):
        r = load_json(os.path.join(d, "prereg-lock.json"))
        out[d] = (r or {}).get("prereg_md_sha256")
    return out


def vallock(card, bins, data_dir=None, need_bins=True):
    """Validation's lock (DESIGN2 §6.3, §6.4). Returns (ok, why, record)."""
    try:
        check_allowed("val", "L16", card)
        pdir = prereg_dir()
        pv_path = params_file("val", card)
    except Refused as e:
        return False, str(e), None
    md = os.path.join(pdir, "PREREG.md")
    ok, why, mdh = md_and_sha(md, os.path.join(pdir, "PREREG.sha256"))
    if not ok:
        return False, why, None
    # PREREG.md and PREREG.sha256 certify only each other (editing both would pass until the first validation block
    # records its hash): the sha256 prereg.py --val printed, recorded OUTSIDE the tree, must be given (review low)
    want = (os.environ.get("HP_PREREG_SHA256") or "").strip().lower()
    if not want and not dry():
        return False, ("HP_PREREG_SHA256 is not set: a validation block needs PREREG.md's sha256 as recorded outside "
                       "the tree when prereg.py --val printed it (README 'The lock'; start the queue with "
                       "HP_PREREG_SHA256=<sha> tools/claims-v3/hp/run_queue.sh ...)"), None
    if want and want != mdh:
        return False, ("PREREG.md sha256 %s is not the recorded %s (HP_PREREG_SHA256): PREREG.md was re-frozen or "
                       "edited after its sha256 was recorded" % (mdh[:12], want[:12])), None
    try:
        lock = parse_lock(md)
    except Exception as e:
        return False, "PREREG.md lock block unreadable: %s" % e, None
    bad = []
    pj_path = os.path.join(pdir, "prereg.json")
    if lock.get("prereg_json") != rel(pj_path):
        bad.append("prereg.json in use (%s) is not the one PREREG.md locks (%s)" % (rel(pj_path), lock.get("prereg_json")))
    if lock.get("params_val") != rel(pv_path):
        bad.append("params-val in use (%s) is not the one PREREG.md locks (%s)" % (rel(pv_path), lock.get("params_val")))
    if lock.get("card") != card:
        bad.append("PREREG.md is for card %s, not %s" % (lock.get("card"), card))
    bad += check_lock_files(lock, bins, need_bins)
    pj, pv = load_json(pj_path), load_json(pv_path)
    if not pj or not pv:
        bad.append("prereg.json or params-val unreadable")
    else:
        fr = dict(pj.get("frozen") or {})
        fr.pop("n_val", None)
        for k, v in sorted(fr.items()):
            if pv.get(k) != v:
                bad.append("params-val %s=%r differs from prereg.json frozen %r" % (k, pv.get(k), v))
        extra = sorted(set(pv) - set(fr) - VAL_PARAMS_META)
        if extra:
            bad.append("params-val keys not in prereg.json frozen: %s" % extra)
        for k in ("trigb_registered", "beta"):
            if pv.get(k) != pj.get(k):
                bad.append("params-val %s=%r differs from prereg.json %r" % (k, pv.get(k), pj.get(k)))
    if data_dir:
        for d, h in sorted(val_blocks_recorded(data_dir).items()):
            if h != mdh:
                bad.append("validation block %s ran under PREREG %s, not this PREREG %s (DESIGN2 §6.4: no re-freeze "
                           "after validation starts)" % (os.path.basename(d), (h or "unrecorded")[:12], mdh[:12]))
    if bad:
        return False, "; ".join(bad), None
    rec = {"prereg_md_sha256": mdh, "prereg_md": rel(md), "files_checked": len(lock.get("files") or {}),
           "binaries": bins, "t_ms": int(vnow_ms()), "prereg_md_sha256_recorded": want or None,
           "overrides": envcheck("val", card)[1], "dry": dry()}
    return True, "PREREG %s%s: %d files and %d binaries match, params-val equals prereg.json's frozen values" % (
        mdh[:12], " (= the recorded HP_PREREG_SHA256)" if want else " (no recorded sha256: dry)",
        len(lock.get("files") or {}), len(lock.get("binaries") or {})), rec


def a2lock(prereg_a2_json, bins, need_bins=True):
    """PREREG-A2's lock: PREREG-A2.md against PREREG-A2.sha256 and prereg-a2.json, then every file and binary."""
    pj = load_json(prereg_a2_json)
    if not pj:
        return False, "no %s" % prereg_a2_json
    md = os.path.join(ROOT, (pj.get("md") or {}).get("path", ""))
    ok, why, mdh = md_and_sha(md, os.path.join(os.path.dirname(md), "PREREG-A2.sha256"))
    if not ok:
        return False, why
    if mdh != (pj.get("md") or {}).get("sha256"):
        return False, "prereg-a2.json's PREREG-A2.md hash differs"
    try:
        lock = parse_lock(md)
    except Exception as e:
        return False, "PREREG-A2.md lock block unreadable: %s" % e
    bad = check_lock_files(lock, bins, need_bins)
    for rp, h in sorted((pj.get("sha256") or {}).items()):
        if (lock.get("files") or {}).get(rp) != h:
            bad.append("prereg-a2.json and PREREG-A2.md disagree on %s" % rp)
    return (not bad), ("; ".join(bad) if bad else "PREREG-A2 %s: %d files and %d binaries match" % (
        mdh[:12], len(lock.get("files") or {}), len(lock.get("binaries") or {})))


def preregcheck(prereg_json, root):
    pj = load_json(prereg_json)
    if not pj:
        return False, "no %s" % prereg_json
    bad = []
    for rel, h in sorted(pj.get("sha256", {}).items()):
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            bad.append("%s missing" % rel)
        elif sha256(p) != h:
            bad.append("%s changed" % rel)
    md = pj.get("md")
    if md:
        p = os.path.join(root, md["path"])
        if not os.path.exists(p) or sha256(p) != md["sha256"]:
            bad.append("%s changed" % md["path"])
    return (not bad), ("; ".join(bad) if bad else "all %d hashes match" % len(pj.get("sha256", {})))


SESSION_TYPES = {"S", "L16", "L8", "G8", "SCOUT", "CAL"}     # the heating blocks that count for a session (§4.4)


def session_first(data_dir, gap_s):
    """True if no heating block (S, L16, L8, G8, SCOUT, CAL; not the probe, the smoke or the one-shot) ended ok on
    this card within gap_s: the block is then the session's first and gets 2 CAL runs (DESIGN2 §4.4)."""
    newest = 0
    for bj in glob.glob(os.path.join(data_dir, "hp", "p*", "block.json")):
        b = load_json(bj) or {}
        try:
            typ = decode_pass(b.get("pass"))[1]
        except Exception:
            continue
        if b.get("status") == "ok" and b.get("t1_ms") and typ in SESSION_TYPES:
            newest = max(newest, b["t1_ms"])
    return (vnow_ms() - newest) / 1000.0 > gap_s


# ----------------------------------------------------------------------------------------------- SP log level
# The level first found on a card is kept in DATA_ROOT/hp/sp-level.json and is the only restore target (O2, DESIGN2
# §3.3). WARNING is set only when that original level is known (INFO or DEBUG); "pending" is written BEFORE the set
# command and cleared only when an end-of-block dump reads the original level again, so a set that timed out, a block
# killed or aborted (exit 3 leaves the card at once) is restored by the next block on the card.
LEVELS_RESTORABLE = ("INFO", "DEBUG")


def level_state(path):
    return load_json(path, None) or {"original": None, "pending": False, "log": []}


def level_save(path, st, **ev):
    st.setdefault("log", []).append(dict(ev, t_ms=int(vnow_ms())))
    st["log"] = st["log"][-50:]
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    json.dump(st, open(tmp, "w"), indent=1)
    os.replace(tmp, path)


def level_begin(path, found, block):
    """The decision at a TRIG-B block's start, from the level just found: (action, original, why), action one of
    'set' (set WARNING, restore to original at the end), 'none' (TRIG-B at the current level; nothing set or restored),
    'skip' (no TRIG-B in this block: the level is unknown)."""
    st = level_state(path)
    if st.get("pending"):
        if st.get("original") in LEVELS_RESTORABLE:
            act, orig, why = "set", st["original"], "an earlier set was not restored (pending): restore target %s" % st["original"]
        else:
            act, orig, why = "skip", None, "pending set with no known original level: nothing is set"
    elif found in LEVELS_RESTORABLE:
        act, orig, why = "set", found, "found %s: WARNING for the block, %s restored at its end" % (found, found)
        st["original"] = found
    elif found == "WARNING_OR_LOWER":
        act, orig, why = "none", found, ("found at WARNING or lower (a reboot or another tool since V3): TRIG-B at the "
                                         "current level, nothing set, nothing to restore")
    else:
        act, orig, why = "skip", None, "level %s (the idle dump failed or was empty): WARNING is never set on an unknown level; no TRIG-B in this block" % found
    level_save(path, st, ev="begin", block=block, found=found, action=act, original=orig)
    return act, orig, why


def level_mark(path, block, pending=None, checked=None):
    st = level_state(path)
    ev = {"ev": "mark", "block": block}
    if pending is not None:
        st["pending"] = bool(int(pending))
        ev["pending"] = st["pending"]
    if checked is not None:
        ev["checked"] = checked
        ev["ok"] = checked == st.get("original")
        if ev["ok"]:
            st["pending"] = False
    level_save(path, st, **ev)
    return st


# ----------------------------------------------------------------------------------------------- dry simulator
# V3_DRY=1 runs the blocks against a small thermal model on an accelerated clock (HP_DRY_SPEED, default 40), so the
# block logic (preheat, edge, chain rule, caps, guard, void checks) and the reducer run end to end with no device.
# It models only what the logic needs; its numbers mean nothing about the cards.
DRY_CARDS = {
    "aifoundry3": {"P_idle": 25.7, "R": [0.55, 1.0], "tau": [6.0, 150.0], "rest": 56.0, "dvfs": False, "tdp": 0},
    "aifoundry1-c1": {"P_idle": 34.0, "R": [0.55, 0.9], "tau": [4.0, 100.0], "rest": 57.0, "dvfs": False, "tdp": 65},
    "aifoundry2": {"P_idle": 32.0, "R": [0.6, 1.1], "tau": [5.0, 150.0], "rest": 61.0, "dvfs": True, "tdp": 65},
}
# aifoundry1 card 0 is not a simulated card (nothing may run on it): the card-0 guard's readings come from dry-guard,
# a constant rest (HP_DRY_REST_C0, default 72 C) plus an optional ramp (HP_DRY_C0_RAMP C per virtual minute)
DRY_KAPPA = {"INT16": 1.03, "PER16": 0.95, "UNI32": 1.0, "MEM8": 0.96, "EDGE8": 0.92, "CEN8": 1.05, "W8b": 1.02,
             "E8b": 0.98, "N8b": 1.0, "S8b": 1.0, "B4NE": 1.0, "B4SW": 1.0, "B4C": 1.1}
DRY_CONC = {"INT16": 1.0, "PER16": 0.8, "UNI32": 0.4, "B4NE": 1.5, "B4SW": 1.5, "B4C": 1.6}
DRY_IO = {"B4NE": 2.0}


def _dry_dir():
    d = os.environ.get("HP_DRY_DIR") or os.path.join(os.getcwd(), "build", "claims-v3-dry", "hp-sim")
    os.makedirs(d, exist_ok=True)
    return d


def _dry_card():
    c = os.environ.get("HP_DRY_CARD") or os.environ.get("CARD") or "aifoundry3"
    return c


def _dry_state_path(card):
    return os.path.join(_dry_dir(), "sim-%s.json" % card)


def _dry_load(card):
    check_card(card)                      # aifoundry1-c0 (or an unknown card) is refused by the simulator too
    st = load_json(_dry_state_path(card))
    cfg = dict(DRY_CARDS[card])
    rest = os.environ.get("HP_DRY_REST")
    if rest and card == os.environ.get("HP_DRY_CARD", card):
        cfg["rest"] = float(rest)
    if not st:
        T_amb = cfg["rest"] - sum(cfg["R"]) * cfg["P_idle"]
        st = {"t": vnow_ms(), "x": [cfg["P_idle"]] * 2, "T_amb": T_amb, "mhz": 600, "gov": "idle", "level": "INFO",
              "cfg": cfg, "last_pass": 0}
    return st


def _dry_save(card, st):
    p = _dry_state_path(card)
    tmp = p + ".tmp"
    json.dump(st, open(tmp, "w"))
    os.replace(tmp, p)


def _dry_launches(card):
    """Latest record per launch id (the fake heater rewrites a launch's end when it stops)."""
    d = {}
    for l in load_jsonl(os.path.join(_dry_dir(), "launches-%s.jsonl" % card)):
        d[l["id"]] = l
    return list(d.values())


def _dry_event(card, kind, t_ms, lvl=None, **kw):
    """One SP log event, with the log level in force when the SP wrote it (lvl): the fake ring keeps every line the
    level let through at that time, so INFO-era lines stay in the ring after a switch to WARNING until ~50 newer
    entries overwrite them, as on the cards (review medium: the level is inferred from new entries only)."""
    cls = os.environ.get("HP_DRY_PROBE", "")
    if lvl is None:
        lvl = (load_json(_dry_state_path(card)) or {}).get("level", "INFO")
    with open(os.path.join(_dry_dir(), "events-%s.jsonl" % card), "a") as f:
        f.write(json.dumps(dict(kind=kind, t=t_ms, cls=cls, lvl=lvl, **kw)) + "\n")


def _dry_host_request(card, st, what):
    """A host DM request (a dump, a log-level command, a config read): at INFO or DEBUG the SP logs it (Host_Iface and
    pc_vq lines; at DEBUG also a voltage line), at WARNING or lower it does not."""
    lvl = st.get("level", "INFO")
    if lvl in ("INFO", "DEBUG"):
        _dry_event(card, "host", vnow_ms(), lvl=lvl, what=what)


def _dry_power(card, st, t, launches):
    cfg = st["cfg"]
    busy = [l for l in launches if l["t0"] <= t < l.get("t1", 0)]
    P, Pk, conc, io = cfg["P_idle"], 0.0, 0.0, 0.0
    if os.environ.get("HP_DRY_PIDLE_BUMP") and card == os.environ.get("HP_DRY_CARD", card):   # the W_idle proxy test
        P += float(os.environ["HP_DRY_PIDLE_BUMP"])
    f = (st.get("mhz", 600) / 600.0) ** 1.6 if cfg["dvfs"] else 1.0
    if cfg["dvfs"] and st.get("mhz", 600) > 600:      # the whole chip's clock and voltage: ~9 W more at 800 MHz
        P += 9.0 * (st["mhz"] - 600) / 200.0
        Pk += 9.0 * (st["mhz"] - 600) / 200.0
    for l in busy:
        g = l.get("group", "UNI32")
        w = 0.0256 * l["minions"] * f
        P += w
        Pk += w * DRY_KAPPA.get(g, 1.0)
        conc += w * DRY_CONC.get(g, 0.6)
        io += w * DRY_IO.get(g, 0.2)
    return P, Pk, conc, io, bool(busy)


def _dry_advance(card, st, t_to, launches, emit=None, reset_ms=0):
    """Integrate the model from st['t'] to t_to in 0.1 s steps; emit(sample) at each 100 ms if given."""
    cfg = st["cfg"]
    t = st["t"]
    rng = random.Random(int(t) % 100000)
    while t + 100 <= t_to:
        t += 100
        P, Pk, conc, io, busy = _dry_power(card, st, t, launches)
        # the mean sensor sees kappa-weighted switching power on the fast stage, all power on the slow stage
        x = st["x"]
        a0 = 1 - math.exp(-0.1 / cfg["tau"][0]); a1 = 1 - math.exp(-0.1 / cfg["tau"][1])
        x[0] += a0 * ((cfg["P_idle"] + Pk) - x[0])
        x[1] += a1 * (P - x[1])
        T = st["T_amb"] + cfg["R"][0] * x[0] + cfg["R"][1] * x[1]
        st["hot"] = st.get("hot", 0.0) + (1 - math.exp(-0.1 / 3.0)) * (conc * 0.35 - st.get("hot", 0.0))
        st["io"] = st.get("io", 0.0) + (1 - math.exp(-0.1 / 3.0)) * (io * 0.3 - st.get("io", 0.0))
        st["T"] = T
        # a pinned card (aifoundry3) whose power task is STUCK: its thermal trigger fires once, at the first crossing
        # since boot, then latches (DESIGN2 §3.2); the fake ring shows that one line for the STUCK class
        if not cfg["dvfs"] and not st.get("latched") and int(math.floor(T)) > 65:
            st["latched"] = True
            _dry_event(card, "thermal_down", t, lvl=st.get("level", "INFO"), T=int(math.floor(T)))
        # the governor (aifoundry2 only): one SP pass every 133 ms; H1: the integer mean > 65
        if cfg["dvfs"]:
            mean_i = int(math.floor(T))
            if t - st.get("last_pass", 0) >= 133:
                st["last_pass"] = t
                if mean_i > 65 and st["gov"] != "thermal":
                    st["gov"] = "thermal"
                    _dry_event(card, "thermal_down", t, lvl=st.get("level", "INFO"), T=mean_i)
                if st["gov"] == "thermal":
                    if mean_i > 65:
                        st["mhz"] = max(600, st["mhz"] - 100)
                    else:
                        st["gov"] = "idle"; st["mhz"] = 600
                        _dry_event(card, "thermal_idle", t, lvl=st.get("level", "INFO"), T=mean_i)
                elif busy and st["mhz"] < 800:
                    st["mhz"] = 800
                elif not busy:
                    st["mhz"] = 600
        if emit:
            n = rng.gauss(0, 0.15)
            m = int(math.floor(T + n))
            hi = int(math.floor(T + 1.6 + st["hot"] + n))
            lo = int(math.floor(T - 3.0 + n))
            iov = int(math.floor(T - 0.3 + st["io"] + n))
            emit(t, m, lo, hi, iov, P + rng.gauss(0, 0.15), st.get("mhz", 600))
    st["t"] = t
    return st


def dry_sampler(a):
    card = a.get("card") or _dry_card()
    secs = float(a.get("seconds", 10))
    every = int(a.get("every_ms", 100))
    reset = int(a.get("reset_ms", 0) or 0)
    out = a["out"]
    stop = {"now": False}
    signal.signal(signal.SIGTERM, lambda *_: stop.update(now=True))
    signal.signal(signal.SIGINT, lambda *_: stop.update(now=True))
    st = _dry_load(card)
    t_begin = vnow_ms()
    if st["t"] < t_begin - 3.6e6:
        st["t"] = t_begin
    st = _dry_advance(card, st, t_begin, _dry_launches(card))      # catch up silently: no back-dated samples
    win = {"t0": t_begin, "lo": None, "hi": None, "iohi": None, "last_emit": 0}
    fh = open(out, "a")

    def emit(t, m, lo, hi, iov, w, mhz):
        if t - win["last_emit"] < every:
            return
        win["last_emit"] = t
        sr = int(t - win["t0"]) if reset else -1
        if reset:
            win["lo"] = lo if win["lo"] is None else min(win["lo"], lo)
            win["hi"] = hi if win["hi"] is None else max(win["hi"], hi)
            win["iohi"] = iov if win["iohi"] is None else max(win["iohi"], iov)
            L, H, IO = win["lo"], win["hi"], win["iohi"]
        else:
            L, H, IO = lo, hi, iov
        fh.write(json.dumps({"t_ms": int(t), "took_ms": 20, "since_reset_ms": sr, "board_w": round(w, 2),
                             "temp_c": {"pmic": m, "ioshire": [iov, iov - 2, IO], "minshire": [m, L, H]},
                             "mhz": {"minion": mhz, "noc": 400, "ddr": 933}}, separators=(",", ":")) + "\n")
        fh.flush()
        if reset and sr >= reset:
            win.update(t0=t, lo=None, hi=None, iohi=None)
    while not stop["now"] and vnow_ms() - t_begin < secs * 1000.0:
        L = _dry_launches(card)
        st = _dry_advance(card, st, vnow_ms(), L, emit)
        _dry_save(card, st)
        time.sleep(0.02)
    fh.close()
    return 0


def dry_guard(a):
    """The card-0 guard's readings under V3_DRY (card 0 is not simulated: nothing runs on it)."""
    secs = float(a.get("seconds", 10))
    every = int(a.get("every_ms", 1000))
    stop = {"now": False}
    signal.signal(signal.SIGTERM, lambda *_: stop.update(now=True))
    signal.signal(signal.SIGINT, lambda *_: stop.update(now=True))
    rest = float(os.environ.get("HP_DRY_REST_C0", "72"))
    ramp = float(os.environ.get("HP_DRY_C0_RAMP", "0"))
    t_begin = vnow_ms()
    last = 0
    with open(a["out"], "a") as fh:
        while not stop["now"] and vnow_ms() - t_begin < secs * 1000.0:
            t = vnow_ms()
            if t - last >= every:
                last = t
                T = rest + ramp * (t - t_begin) / 60000.0
                m = int(math.floor(T))
                fh.write(json.dumps({"t_ms": int(t), "took_ms": 20, "since_reset_ms": -1, "board_w": 19.0,
                                     "temp_c": {"pmic": m, "ioshire": [m, m - 2, m + 1], "minshire": [m, m - 3, m + 2]},
                                     "mhz": {"minion": 600, "noc": 400, "ddr": 933}}, separators=(",", ":")) + "\n")
                fh.flush()
            time.sleep(0.02)
    return 0


def dry_die(a):
    card = a.get("card") or _dry_card()
    st = _dry_load(card)
    if st["t"] < vnow_ms() - 3.6e6:
        st["t"] = vnow_ms()
    st = _dry_advance(card, st, vnow_ms(), _dry_launches(card))
    _dry_save(card, st)
    print(int(math.floor(st.get("T", st["cfg"]["rest"]))))
    return 0


def dry_heater(a):
    """A fake sparsity_host: registers the launch with the model, sleeps its accelerated duration (honouring
    --stop-file between its 0.5 s inner launches) and prints SPARSITY lines on the virtual clock."""
    card = a.get("card") or _dry_card()
    args = a["argv"]
    def opt(name, default):
        return args[args.index(name) + 1] if name in args else default
    mask = int(opt("--shires", "0xffffffff"), 0)
    per = int(opt("--per-shire", "32"))
    secs = float(opt("--seconds", "0"))
    stopf = opt("--stop-file", "")
    minions = bin(mask).count("1") * per
    PL = placements()["groups"]
    group = next((g for g, v in PL.items() if int(v["mask"], 0) == mask and g not in ("W12", "E12", "N12", "S12")), "UNI32")
    lf = os.path.join(_dry_dir(), "launches-%s.jsonl" % card)
    t0 = vnow_ms() + 200
    lid = "%d-%d" % (int(t0), os.getpid())
    with open(lf, "a") as f:
        f.write(json.dumps({"id": lid, "t0": t0, "t1": t0 + 30 + secs * 1000 + 20, "minions": minions, "group": group}) + "\n")
    cls = os.environ.get("HP_DRY_PROBE", "")
    st = _dry_load(card)
    _dry_event(card, "power_start", t0, lvl=st.get("level", "INFO"), tdp=st["cfg"]["tdp"])
    lines = []
    ghz = 0.6
    def line(n, ts, te, it):
        return ("SPARSITY " + json.dumps({"test": "fma", "type": "fp32", "values": "randn", "minions": minions,
                                          "shire_mask": hex(mask), "iters": it, "launch": n, "cycles_per_op": 546.0,
                                          "wall_s": (te - ts) / 1000.0, "t_start_ms": int(ts), "t_end_ms": int(te),
                                          "ghz": ghz, "tensor_errors": 0, "result": "unchecked", "ok": True},
                                         separators=(",", ":")))
    t = t0
    vsleep(0.2)
    lines.append(line(-1, t, t + 30, 20000)); t += 30
    stopped = False
    k = 0
    while t < t0 + 30 + secs * 1000 - 1:
        if stopf and os.path.exists(stopf):
            stopped = True
            break
        vsleep(0.5)
        lines.append(line(k, t, t + 500, 549000)); t += 500; k += 1
    t_end = t
    with open(lf, "a") as f:
        f.write(json.dumps({"id": lid, "t0": t0, "t1": t_end, "minions": minions, "group": group}) + "\n")
    _dry_event(card, "power_idle", t_end, lvl=st.get("level", "INFO"), tdp=st["cfg"]["tdp"])
    print("device ready in 0.20 s (dry), kernel %s" % opt("--kernel", "(compiled-in KERNEL_ELF)"), file=sys.stderr)
    for l in lines:
        print(l)
    if stopped:
        print("stopping: %s exists" % stopf, file=sys.stderr)
    vsleep(0.3)
    return 0


def dry_sptrace(a):
    """A fake SP ring from the simulator's governor events, filtered by the simulated log level and the probe class
    (HP_DRY_PROBE, else the card's DESIGN2 prediction: aifoundry3 SILENT, card 1 SILENT, aifoundry2 ALIVE when its
    rest reading is <= 65)."""
    from sptrace_events import build_ring
    card = a.get("card") or _dry_card()
    st = _dry_load(card)
    fail = os.environ.get("HP_DRY_SPTRACE_FAIL")              # test hook: this dump fails (no file written)
    if fail and re.search(fail, os.path.basename(a["out"])):
        print("sptrace: failed (dry test hook HP_DRY_SPTRACE_FAIL)", file=sys.stderr)
        return 1
    cls = os.environ.get("HP_DRY_PROBE") or {"aifoundry3": "SILENT", "aifoundry1-c1": "SILENT"}.get(card) or \
        ("ALIVE" if st["cfg"]["rest"] <= 65 else "SILENT")
    lvl = st.get("level", "INFO")
    # this dump's own request: logged at INFO/DEBUG (before the ring is copied, so it is in this dump and every later
    # one until overwritten)
    _dry_host_request(card, st, "sptrace")
    ev = load_jsonl(os.path.join(_dry_dir(), "events-%s.jsonl" % card))
    ents = []
    for e in ev:
        ts = int((e["t"] - 1.7e12) * 40000) if e["t"] > 1.7e12 else int(e["t"] * 40000)
        elvl = e.get("lvl", lvl)                # the level when the SP wrote the line (older sims: the current one)
        crit, info = [], []
        if e["kind"] == "host":
            if elvl in ("INFO", "DEBUG"):
                ents.append((ts, "Host_Iface: Received DM request from host.\n"))
                ents.append((ts + 1, "pc_vq_process_pending_command TagID: 0 MsgID:1\r\n"))
            if elvl == "DEBUG":
                ents.append((ts + 2, "MS 12 Voltage [mV]: 525 0 0 0\n"))
            continue
        if cls in ("ALIVE", "STUCK"):
            if e["kind"] == "power_start":
                if st["cfg"]["tdp"] == 0:
                    crit.append("Power throttle down event, current pwr 35000  tdp level: 0\n")
                else:
                    crit.append("Power throttle up event, current pwr 42000  tdp level: 65000\n")
                if cls == "ALIVE":
                    info.append("Power Throttle event received. throttle_state: 2\n")
            elif e["kind"] == "power_idle":
                crit.append("Power idle state event, current pwr 30000  tdp level %d\n" % (e.get("tdp", 65) * 1000))
                if cls == "ALIVE":
                    info.append("Power Throttle event received. throttle_state: 0\n")
            elif e["kind"] == "thermal_down":
                crit.append("Thermal throttle down event, current temperature: %d, threshold: 65\n" % e["T"])
                if cls == "ALIVE":
                    info.append("Power Throttle event received. throttle_state: 5\n")
            elif e["kind"] == "thermal_idle":
                crit.append("Thermal idle state event, current temperature %d, threshold 65\n" % e["T"])
        for i, s in enumerate(crit):
            ents.append((ts + i, s))
        if elvl in ("INFO", "DEBUG"):
            for i, s in enumerate(info):
                ents.append((ts + 10 + i, s))
    ents.sort()
    open(a["out"], "wb").write(build_ring(ents))
    print("sptrace: rc 0, 8192 bytes (dry, class %s, level %s)" % (cls, lvl))
    return 0


def dry_config(a):
    card = a.get("card") or _dry_card()
    st = _dry_load(card)
    _dry_host_request(card, st, "config")
    tdp = st["cfg"]["tdp"]
    print(json.dumps({"tdp_w": tdp, "temp_threshold_c": 65, "power_state": 1 if tdp else 0,
                      "power_state_name": "managed_power" if tdp else "max_power", "minion_mhz": st.get("mhz", 600),
                      "minion_mv": 525, "dry": True}))
    return 0


def dry_loglevel(a):
    card = a.get("card") or _dry_card()
    st = _dry_load(card)
    _dry_host_request(card, st, "loglevel")      # the request is logged at the level in force when it arrives
    lv = a["level"].upper()
    # test hook HP_DRY_LOGLEVEL_NOAPPLY=<level>[,...]: the SP ignores that command and the call fails (a restore that
    # did not take: the end-of-block check must see it)
    if a["level"].lower() in [x.strip().lower() for x in (os.environ.get("HP_DRY_LOGLEVEL_NOAPPLY") or "").split(",")]:
        print("loglevel %s: rc 1, not applied (dry test hook HP_DRY_LOGLEVEL_NOAPPLY)" % a["level"])
        return 1
    st["level"] = {"CRITICAL": "WARNING", "ERROR": "WARNING", "WARNING": "WARNING", "INFO": "INFO", "DEBUG": "DEBUG"}.get(lv, "?")
    _dry_save(card, st)
    rc = 0                                # test hook HP_DRY_LOGLEVEL_RC=[level:]rc,...: the SP applies the level, the call fails
    for part in (os.environ.get("HP_DRY_LOGLEVEL_RC") or "").split(","):
        if ":" in part:
            lv_, r_ = part.split(":", 1)
            if lv_.lower() == a["level"].lower():
                rc = int(r_)
        elif part.strip():
            rc = int(part)
    print("loglevel %s: rc %d status 0 (dry)" % (a["level"], rc))
    return rc


# ----------------------------------------------------------------------------------------------- self-test
def selftest():
    for m in (3, 4, 6):
        nseq, each = check_williams(m)
        print("Williams m=%d: %d sequences, every ordered pair %d times" % (m, nseq, each))
    assert abs(t_ppf(0.995, 25) - 2.787) < 0.002 and T995[2] == 9.925
    b = DEFAULTS["band_t"]
    assert outcome("SIGN+", [0.2, 0.25, 0.22, 0.21], b)[0] is True
    assert outcome("SIGN+", [-0.2, -0.25, -0.22, -0.21], b)[0] is False       # opposite sign
    assert outcome("SIGN+", [0.01, -0.01, 0.0, 0.005, -0.005], b)[0] is False  # CI wholly inside the band
    assert outcome("SIGN+", [0.3, -0.3, 0.1, -0.1], b)[0] is None
    assert outcome("NONZERO", [-0.2, -0.25, -0.22], b)[0] is True
    assert outcome("NONZERO", [0.01, -0.01, 0.0, 0.005], b)[0] is False
    assert outcome("EQUIV", [0.01, -0.01, 0.0, 0.005], b)[0] is True
    assert outcome("EQUIV", [0.5, 0.52, 0.51], b)[0] is False
    assert outcome("EQUIV", [0.05, 0.12, 0.08], b)[0] is None
    assert outcome("SIGN+", [0.2, 0.3], b)[0] is None                           # fewer than 3 blocks
    assert card_verdicts({"a": True, "b": True}, ["a", "b"]) == "PASS"
    assert card_verdicts({"a": True, "b": False}, ["a", "b"]) == "CARD-DIFFERENT"
    assert card_verdicts({"a": None, "b": False}, ["a", "b"]) == "INSUFFICIENT"
    assert abs(binom_two_sided(0, 6) - 0.03125) < 1e-9
    for p in (801, 901, 1701, 1601, 1101, 1201, 2301, 2401, 3101, 5501, 5511, 9201):
        decode_pass(p)
    # precedence (README departure 18): a CI excluding 0 but wholly inside +-band fails SIGN and NONZERO (review F13)
    v = [0.025 + d for d in (-0.004, 0.004, -0.002, 0.002, 0.0)]      # CI about [0.017, 0.033], band 0.095
    c = ci99(v)
    assert 0.015 < c["lo"] < 0.02 and 0.03 < c["hi"] < 0.035, c
    assert outcome("SIGN+", v, b)[0] is False and outcome("NONZERO", v, b)[0] is False
    assert outcome("SIGN-", [-x for x in v], b)[0] is False and outcome("EQUIV", v, b)[0] is True
    # aifoundry1 card 0 and the allow-list (review F0)
    def refused(f, *a):
        try:
            f(*a)
        except Refused:
            return True
        return False
    assert refused(check_card, "aifoundry1-c0") and "aifoundry1-c0" not in CARD_INDEX and "aifoundry1-c0" not in DRY_CARDS
    for p, card in ((801, "aifoundry1-c0"), (901, "aifoundry1-c0"), (1201, "aifoundry1-c0"), (9201, "aifoundry1-c0"),
                    (1201, "aifoundry1-c1"), (1701, "aifoundry1-c1"), (1601, "aifoundry1-c1"), (2301, "aifoundry1-c1"),
                    (3201, "aifoundry1-c1"), (5201, "aifoundry1-c1"), (9501, "aifoundry1-c1"), (1901, "aifoundry1-c1"),
                    (5501, "aifoundry3"), (9201, "aifoundry3"), (9901, "aifoundry3"), (2701, "aifoundry3"),
                    (5901, "aifoundry1-c1"), (9901, "aifoundry1-c1"),
                    (801, "aifoundry2"), (901, "aifoundry2"), (1201, "aifoundry2"), (9201, "aifoundry2")):
        assert refused(plan, p, card), (p, card)
    for p, card in ((801, "aifoundry3"), (901, "aifoundry3"), (1701, "aifoundry3"), (1601, "aifoundry3"),
                    (1101, "aifoundry3"), (2401, "aifoundry3"), (3301, "aifoundry3"), (1901, "aifoundry3"),
                    (801, "aifoundry1-c1"), (901, "aifoundry1-c1")):
        decode_pass(p); check_allowed(decode_pass(p)[0], decode_pass(p)[1], card)
    assert refused(resolve_params, "r1", "aifoundry2") and refused(resolve_params, "r1", "aifoundry1-c0")
    assert a2_params()["abs_stop_c"] == 90
    assert TRIGB_VALUES == ("auto", "off") and VAL_RANGES["S_L"] == (58, 62) and VAL_RANGES["S_L8"] == (60, 64)
    # the level rule (review F3)
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        f = os.path.join(td, "sp-level.json")
        assert level_begin(f, "UNKNOWN", 1)[0] == "skip" and level_begin(f, "EMPTY", 1)[0] == "skip"
        assert level_begin(f, "WARNING_OR_LOWER", 1)[0] == "none"
        assert level_begin(f, "INFO", 2)[:2] == ("set", "INFO")
        level_mark(f, 2, pending=1)                                   # set, then the block died before restoring
        assert level_begin(f, "WARNING_OR_LOWER", 3)[:2] == ("set", "INFO")   # the next block restores INFO
        level_mark(f, 3, checked="INFO")
        assert not level_state(f)["pending"]
    # blockcheck and runcheck read the round from plan['info'] and use the block's recorded params (review high)
    with tempfile.TemporaryDirectory() as td:
        def blk(card, rnd, P, runs):
            d = os.path.join(td, "%s-%s" % (card, rnd))
            os.makedirs(d)
            json.dump({"info": {"round": rnd, "card": card, "type": "L16"}, "runs": [], "params": P},
                      open(os.path.join(d, "plan.json"), "w"))
            with open(os.path.join(d, "runs.jsonl"), "w") as fh:
                for r in runs:
                    fh.write(json.dumps(r) + "\n")
            return d
        run = lambda idx, slot, rc: {"idx": idx, "slot": slot, "attempt": 1, "role": "meas", "name": "INT16@32",
                                     "tier": "L", "edge": 58, "edge_ok": True, "rcs": [rc], "minions": 512}
        Pv = dict(DEFAULTS, S_L=58, _params_source="params/params-val-aifoundry1-c1.json")
        d = blk("aifoundry1-c1", "val", Pv, [run(3, 1, 0), run(4, 2, 1)])
        r = blockcheck(d, "aifoundry1-c1")            # raised Refused (r1 on card 1) before the fix
        assert r["round"] == "val" and r["params_source"] == Pv["_params_source"] and \
            [x["slot"] for x in r["rerun"]] == [1, 2] and any("heater rc" in w for w in r["void"]["4"]), r
        assert runcheck(d, 4, "aifoundry1-c1")["void"][0].startswith("heater rc")
        P2 = dict(DEFAULTS, _params_source="params/params-r2-aifoundry3.json", void_work=0.02)
        assert blockcheck(blk("aifoundry3", "r2", P2, [run(3, 1, 0)]), "aifoundry3")["round"] == "r2"
        os.makedirs(os.path.join(td, "noplan"))
        for f_, a_ in ((blockcheck, (os.path.join(td, "noplan"), "aifoundry3")), (blockcheck, (d, "aifoundry3"))):
            try:
                f_(*a_)
                raise AssertionError("blockcheck without a plan (or another card's) must raise")
            except ValueError:
                pass
    # V3_FORCE: refused without V3_DRY for validation, a2 and every card-1 block; recorded otherwise (review medium)
    keep = {k: os.environ.get(k) for k in ("V3_DRY", "V3_FORCE", "HP_PARAMS_DIR", "HP_PREREG_DIR")}
    try:
        for k in keep:
            os.environ.pop(k, None)
        os.environ["V3_FORCE"] = "1"
        assert envcheck("val", "aifoundry1-c1")[0] is False and envcheck("a2", "aifoundry2")[0] is False
        assert envcheck("dev", "aifoundry1-c1")[0] is False                     # R0 and V0 on card 1 too
        ok_, found_, _ = envcheck("dev", "aifoundry3")
        assert ok_ and "V3_FORCE" in found_                                     # development: allowed, recorded
        os.environ["V3_DRY"] = "1"
        assert envcheck("val", "aifoundry1-c1")[0] is True and "V3_FORCE" in envcheck("val", "aifoundry1-c1")[1]
        # C_L is the chain cap (review low): a file with chain_cap_s 100 and C_L 150 is refused; chain_cap_s alone
        # carries C_L with it
        with tempfile.TemporaryDirectory() as td:
            os.environ["HP_PARAMS_DIR"] = td
            json.dump({"chain_cap_s": 100, "C_L": 150.0}, open(os.path.join(td, "params-r2-aifoundry3.json"), "w"))
            try:
                resolve_params("r2", "aifoundry3")
                raise AssertionError("C_L != chain_cap_s must be refused")
            except ValueError as e:
                assert "C_L" in str(e)
            json.dump({"chain_cap_s": 120}, open(os.path.join(td, "params-r2-aifoundry3.json"), "w"))
            assert resolve_params("r2", "aifoundry3")["C_L"] == 120.0
    finally:
        for k, v in keep.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    # the watcher's guard grace (review low): an empty guard file is stale only after 30 s, not at once
    import subprocess
    with tempfile.TemporaryDirectory() as td:
        env = dict(os.environ, V3_DRY="1", HP_DRY_SPEED="40", HP_VT0=str(int(time.time() * 1000)))
        tel, guard = os.path.join(td, "tel.raw"), os.path.join(td, "guard.raw")
        open(guard, "w").close()
        st_, ctl = os.path.join(td, "state"), os.path.join(td, "ctl")
        open(ctl, "w").close()
        open(tel, "w").write(json.dumps({"t_ms": int(vnow_ms()), "temp_c": {"minshire": [60, 58, 62]}, "board_w": 30}) + "\n")
        p = subprocess.Popen([sys.executable, os.path.abspath(__file__), "watch", "--tel", tel, "--state", st_, "--ctl", ctl,
                              "--guard", guard, "--caps", "guard_stale_s=10"], env=env)
        stops = []
        for wait_s in (0.4, 1.0):                  # 16 s and 56 s of virtual time
            time.sleep(wait_s)
            stops.append((open(st_).read().split() or ["-"] * 7)[6])
        open(ctl, "a").write("quit\n")
        p.wait(timeout=10)
        assert stops == ["-", "GUARD_STALE"], stops
    # README departure 36: V0 requires S_L8 only while L8 or G8 is kept (a stand-in for v0_edge: S_L settled at 60)
    assert l8_kept(["S", "L16", "L8", "G8"]) and l8_kept(["G8"]) and not l8_kept(["S", "L16"]) and not l8_kept(None)
    keep_ve = globals()["v0_edge"]
    try:
        globals()["v0_edge"] = lambda d, c, t, P: {"edge": None, "final": 60 if t == "L" else None, "why": "stub"}
        full = v0_final("", "aifoundry1-c1", dict(DEFAULTS, types=["S", "L16", "L8", "G8"]))
        drop = v0_final("", "aifoundry1-c1", dict(DEFAULTS, types=["S", "L16"]))
    finally:
        globals()["v0_edge"] = keep_ve
    assert full["complete"] is False and full["S_L8"] is None, full
    assert drop["complete"] is True and drop["S_L"] == 60 and drop["S_L8"] is None and drop["types"] == ["S", "L16"] \
        and "dropped" in drop["L8"]["why"], drop
    print("selftest ok: Williams orders, t quantiles, SIGN/NONZERO/EQUIV three outcomes (inside-band precedence), card "
          "verdicts, sign test, passes, card 0 refused, the card/block allow-list, trigb auto/off, V0 ranges, the SP "
          "level rule, blockcheck/runcheck from plan info (val on card 1, r2 on aifoundry3), V3_FORCE refused/recorded, "
          "C_L = chain cap, the guard's 30 s grace, V0's S_L8 required only while L8/G8 are kept")


# ----------------------------------------------------------------------------------------------- CLI
def _kv(argv):
    a, rest = {}, []
    i = 0
    while i < len(argv):
        if argv[i].startswith("--") and i + 1 < len(argv) and argv[i] != "--":
            a[argv[i][2:].replace("-", "_")] = argv[i + 1]; i += 2
        elif argv[i] == "--":
            rest = argv[i + 1:]; break
        else:
            rest.append(argv[i]); i += 1
    a["argv"] = rest
    return a


def _sh(v):
    if isinstance(v, bool):
        return "1" if v else ""
    if isinstance(v, (list, dict)):
        v = json.dumps(v)
    s = str(v)
    return "'" + s.replace("'", "'\\''") + "'"


def main(argv):
    if not argv:
        print(__doc__); return 2
    cmd, a = argv[0], _kv(argv[1:])
    if cmd == "selftest":
        selftest(); return 0
    if cmd == "params":
        if "--a2" in argv:
            P = a2_params()
        else:
            rnd = decode_pass(a["pass"])[0]
            P = resolve_params(rnd, a["card"])
        for k, v in P.items():
            print("SET P_%s=%s" % (k, _sh(v)))
        return 0
    if cmd == "plan":
        try:
            info, runs, P = plan(a["pass"], a["card"], first_of_session=a.get("first") == "1")
        except Refused as e:
            print("REFUSED: %s" % e, file=sys.stderr)
            return 2
        except ValueError as e:
            print("BAD PARAMS: %s" % e, file=sys.stderr)
            return 2
        if a.get("json"):
            json.dump({"info": info, "runs": runs, "params": P}, open(a["json"], "w"), indent=1)
        for k, v in info.items():
            print("SET INFO_%s=%s" % (k, _sh(v)))
        for k in ("chain_cap_s", "chain_launch_s", "chain_after_66", "S_launch_s", "S_idle_after_s", "edge_wait_cap_s",
                  "preheat_max_bursts", "preheat_stop_c", "preheat_s", "abs_stop_c", "cap_mean_c", "cap_high_c",
                  "cap_board_w", "cap_consecutive", "guard_gate_c", "guard_stop_c", "guard_stale_s", "sampler_stale_s",
                  "reset_ms", "trigb", "C_S", "C_L", "guard_widle_rise_w", "guard_max_s", "guard_refresh_s"):
            print("SET P_%s=%s" % (k, _sh(P[k])))
        print("SET P_trigb_registered=%s" % _sh(bool(P.get("trigb_registered", False))))
        for i, r in enumerate(runs):
            print("RUN %d %s %s %s %d %d %s %s %s" % (i + 1, r["role"], r["name"], r["mask"], r["per_shire"], r["minions"],
                                                     r["tier"], "-" if r["edge"] is None else r["edge"],
                                                     "-" if r["target"] is None else r["target"]))
        return 0
    if cmd == "watch":
        return watch(a)
    if cmd == "runcheck":
        print(json.dumps(runcheck(a["out"], a["idx"], a["card"]))); return 0
    if cmd == "blockcheck":
        try:
            r = blockcheck(a["out"], a["card"])
        except Exception as e:           # block.sh fails the block on a non-zero exit (never a silent "ok")
            print("blockcheck failed: %s: %s" % (type(e).__name__, e), file=sys.stderr)
            print("BLOCKCHECK FAILED %s" % e)
            return 1
        json.dump(r, open(os.path.join(a["out"], "blockcheck.json"), "w"), indent=1)
        print("BLOCKCHECK round %s, params %s, %d void run(s), %d to re-run" % (
            r["round"], r["params_source"], len(r["void"]), len(r["rerun"])))
        for x in r["rerun"]:
            print("RERUN %s %s" % (x["slot"], x["name"]))
        return 0
    if cmd == "guardcheck":
        ok, why = guardcheck(a["guard"], float(a.get("gate", DEFAULTS["guard_gate_c"])), float(a.get("max_age", 10)))
        print(why); return 0 if ok else 1
    if cmd == "check-card":
        try:
            if a.get("pass"):
                rnd, typ, _ = decode_pass(a["pass"])
                check_allowed(rnd, typ, a["card"])
            else:
                check_card(a["card"])
        except (Refused, ValueError) as e:
            print("REFUSED: %s" % e); return 2
        print("ok"); return 0
    if cmd == "envcheck":
        # stdout: the variables set (for marks.jsonl), or on a refusal the refused ones and why (the shell logs it)
        ok, found, bad = envcheck(a.get("mode", "dev"), a.get("card"))
        if not ok:
            print("%s set without V3_DRY=1 (honoured only in dry tests%s)" % (
                " ".join(bad), "; V3_FORCE would re-run a finished block into its own directory" if "V3_FORCE" in bad else ""))
            return 1
        print(" ".join(found) if found else "-")
        return 0
    if cmd == "binhash":
        print(json.dumps(binhash(a["argv"]), sort_keys=True)); return 0
    if cmd == "vallock":
        bins = json.load(open(a["bins"])) if a.get("bins") else None
        ok, why, rec = vallock(a["card"], bins, a.get("data"))
        if ok and a.get("record"):
            json.dump(rec, open(a["record"], "w"), indent=1)
        print(why); return 0 if ok else 1
    if cmd == "a2lock":
        bins = json.load(open(a["bins"])) if a.get("bins") else None
        ok, why = a2lock(a["prereg"], bins)
        print(why); return 0 if ok else 1
    if cmd == "level-begin":
        act, orig, why = level_begin(a["state"], a["found"], a.get("block", "?"))
        print("LV_ACTION=%s LV_ORIG=%s LV_WHY=%s" % (act, orig or "-", _sh(why))); return 0
    if cmd == "level-mark":
        st = level_mark(a["state"], a.get("block", "?"), a.get("pending"), a.get("checked"))
        print("LV_PENDING=%s LV_ORIG=%s" % ("1" if st.get("pending") else "", st.get("original") or "-")); return 0
    if cmd == "level-show":
        st = level_state(a["state"])
        print("LV_PENDING=%s LV_ORIG=%s" % ("1" if st.get("pending") else "", st.get("original") or "-")); return 0
    if cmd == "v0final":
        P = resolve_params("v0", a["card"])
        r = v0_final(a["data"], a["card"], P)
        if a.get("write"):
            if not r["complete"]:
                print(json.dumps(r)); print("V0 not settled: nothing written", file=sys.stderr); return 1
            json.dump(r, open(a["write"], "w"), indent=1)
        print(json.dumps(r)); return 0
    if cmd == "preregcheck":
        ok, why = preregcheck(a["prereg"], a.get("root", ROOT))
        print(why); return 0 if ok else 1
    if cmd == "sessionfirst":
        print("1" if session_first(a["data"], float(a.get("gap", DEFAULTS["session_gap_s"]))) else "0"); return 0
    if cmd == "v0edge":
        rnd = "v0"
        P = resolve_params(rnd, a["card"])
        print(json.dumps(v0_edge(a["data"], a["card"], a.get("target", "L"), P))); return 0
    if cmd == "widle":
        # card 1's secondary proxy (DESIGN2 §7): W_idle at the edge (median board_w over the last 2 s of the live
        # sampler) against the session's first block; exit 1 if it rose by more than --rise W
        rows = [sample_fields(json.loads(l)) for l in open(a["tel"], errors="replace") if l.startswith("{") and l.rstrip().endswith("}")]
        rows = [r for r in rows if r[0] is not None and r[4] is not None]
        if not rows:
            print("no samples"); return 0
        tl = rows[-1][0]
        w = median([r[4] for r in rows if r[0] >= tl - 2000])
        # the baseline is this session's: block.sh resets the file at a session's first block (W_idle null), and the
        # first measured run of the session sets it (review F12: never compare with an earlier session)
        sess = a.get("session")
        base = load_json(sess) if sess and os.path.exists(sess) else None
        if sess and (base is None or base.get("W_idle") is None):
            base = dict(base or {}, W_idle=w, t_ms=tl, set_by=a.get("pass"))
            json.dump(base, open(sess, "w"))
        rise = (w - base["W_idle"]) if base else 0.0
        print("W_idle %.2f W, session baseline %s (session of pass %s), rise %.2f W" % (
            w, base and "%.2f" % base["W_idle"], base and base.get("session_pass"), rise))
        return 1 if rise > float(a.get("rise", DEFAULTS["guard_widle_rise_w"])) else 0
    if cmd == "vnow":
        print(int(vnow_ms())); return 0
    if cmd == "dry-sampler":
        return dry_sampler(a)
    if cmd == "dry-heater":
        return dry_heater(a)
    if cmd == "dry-guard":
        return dry_guard(a)
    if cmd == "dry-die":
        return dry_die(a)
    if cmd == "dry-sptrace":
        return dry_sptrace(a)
    if cmd == "dry-config":
        return dry_config(a)
    if cmd == "dry-loglevel":
        return dry_loglevel(a)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
