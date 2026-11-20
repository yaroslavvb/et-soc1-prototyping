#!/usr/bin/env python3
"""1119-mmsweep5: the desk tests of the kit (no device; Python's own modules only). Each case prints PASS or FAIL; the last line
is SELFTEST-MMS <n> of <m> PASS.

    python3 -I -B src/selftest_mms.py <scratch dir>          (dry sessions are written under it; nothing in the kit's folder)

  M1  mms_common's self-check (stop lines, latch rule, counted launch, configs, gates, argv, every schedule's lines and roles)
  M2  mms_ident's self-check (config identity of the three cards, holder reads, host identity, the board's rise, freshness)
  M3  the schedules are make_schedule2.py's from the plan (MAKE CHECK PASS; with no plan yet, nothing made); M4 the harness
      file is current (CHECK PASS)
  M5  the device-command audit on the session's files: GO, every send site a READ, no wrapper line
  M6  the tiles (src/tiles_gen.py --check): the lab's nine and the plan's read back, finite, the check of C meaningful
  M7  THE TOY PLAN (TOY below: a new fp32 tile and a new int8 tile, a spread mask, a reverse session S7) made by
      make_schedule2.py into <scratch>/toy/src: its schedules pass mms_common's self-check; an arm over a card's line, a tile
      whose check of C would drift, a session over the sweep's size, a drawn fp tile estimated at a row other than rnd, and a
      drawn fp tile on card 0 (random data, low power) are each REFUSED. The dry cases below run its schedules.
  M8  THE NEW TILE SPECS AND THE PAIR CHECK (TOY3 below: alt for density and toggle rate, field, sparse, in fp32, fp16 and
      int8) made into <scratch>/toy3/src: the alt density rung of 4 bits is the second sweep's den4 byte for byte; every tile
      read back finite with its check of C meaningful; its schedules pass mms_common's self-check; --pairs reads PAIRS PASS;
      a tile at the rung's input toggles (8 bits on 4 lanes) is REFUSED without counted switches and with counts 5 % apart,
      and made with equal counts; a field exponent outside the half's normal range and an alt mask that makes inf are REFUSED
  W1  THE FOURTH SWEEP'S SPECS AND THE WIDER PAIR CHECK (TOY4 below: rates along K by periodic sets, structured zeros, an int8
      density, sign-only toggles, a drawn sparse50 kind; a toy prior list) made into <scratch>/toy4/src with the plan's priors:
      every tile read back finite with its check of C meaningful (exact or approx; drawn for the drawn kind), the rates and
      zeros as specified, its schedules pass mms_common's self-check; --pairs reads PAIRS PASS with the prior of the same bytes
      `same bytes`, the near prior of equal counts `same`, the drawn prior of the same kind `same kind`; REFUSED: the near prior
      without counts, with counts 3 % apart, the drawn kind against a held prior (kind tiles) at its toggles, a list at another
      sha256 than the plan names, a prior file not at its listed sha256, a designed int8 tile at 0 input toggles (against the
      lab's int8 kinds), a periodic set as wide as its period, and counts that follow the toggles (the third sweep's
      `follows`); made: the drawn kind beside a prior run in ways not known (not paired), and the plan without priors, whose
      summary says the wider check was not run
  W2  THE BLOCK ARMS (TOY5 below: gemmc with r and s, gemmh, gemm, mm, tenb, a gemmL control; card 1 and card 0) made into
      <scratch>/toy5/src: its schedules pass mms_common's self-check; each block arm's record by the host's grammar (values,
      ops a minion a pass, footprint, M x N x K = 1,024 x ops a pass x multiply-adds an op, the host's counts); each estimate
      as the block law gives it; the host's own lines the grammar is read from stand in src/rgm136 in the host's prefix order;
      REFUSED: gemmv, gemmnc, mmp, a gemmL token, s before r, a trailing character, a colon, a leading zero, r1, B 33, R 33, N 257, a
      mask, a plan tile, mb on a block arm, a wrong id, fp32 rnd on card 0, int8 rnd and tenb zeros on card 0 (over 52 W),
      mm int8 on card 1 (over the block plan level 66.6 W)
  D1  a short dry session (card 1, the toy's S3): smoke, an anchor, a null, a sus3 run and bursts; every device call printed; manifest; the
      reducer against the doubles' law: T an op, the board's lift, the rails undone (the minion rail's share of the lift), a null
      reading near zero under the line rule, J an op = dP x T / minions
  D2  a board stop line tripped by the doubles (governed card): STOP, nothing further starts, it closes (config end, manifest)
  D3  the first config read fails (a collector's collision): one re-run passes and the session runs
  D4  the host names another card: the smoke gate fails, no run starts, rc 16
  D5  the operator's STOP after the second run: nothing further starts, the session closes, rc 0
  D6  card 0 of aifoundry1: the identity gate and read pass for card 0 (ET_DEVICES 0, minion_mv at or above 510)
  D7  the collector on D1's session: COPY-BACK EXACT, the privacy read, the reduction
  D8  the start config read names the other card: the gate, rc 16, and NO closing config read (one config call in all)
  D9  a stale sampler that ignores SIGTERM: no second sampler is started, the session ends, no closing read, the leftover is
      recorded and resolved when the double ends (the card's lock held till then)
  D10 a host that outlives `timeout 10` and ignores SIGTERM: the session ends at once (nothing further starts), no closing read,
      the leftover recorded in queue.json and status.json and resolved when the double ends
  D11 two failed processes in a row (rc not 0, the check of C not ok): the session stops
  D12 the governed card's capped rule: runs the doubles' governor dithers under its cap are flagged capped, the others not;
      `time` runs carry no energy figure; the window view sits after the clock step
  D13 the start config read outlives its bound, deaf to SIGTERM: no SIGKILL (the double ends by itself), no re-run, no launch,
      no closing read, rc 16; the leftover recorded and resolved, the card's lock held till then
  D14 the closing config read outlives its bound, deaf to SIGTERM: the leftover recorded in queue.json and status.json and
      resolved; the double ends by itself
  D15 a holder of another login appears before the closing read: et-who read once more after the sampler stops, NO closing read
  D16 aifoundry2: a holder of another login appears before a run that is not an anchor: the session stops before that run (et-who
      before every run on every card), no closing read
  D17 the box lock handed over: a child given the held descriptor holds it (one open file), a fresh opener is refused, a
      descriptor of another file is refused, and the lock is free once the holder lets go
  D18 the doubles through M8's toy (card 1, its S1 of the new tile specs): every run started, every process rc 0 with its
      check exact or approx, each new tile's file in the host's calls, the manifest
  D19 the doubles through W1's toy (card 1, its S1 of the fourth sweep's specs): every run started, every process rc 0 with its
      check exact or approx, each new tile's file in the host's calls, the manifest
  D20 the doubles through W2's toy (card 1 and card 0, their S1): every run started, every process rc 0 with its check exact or
      approx, each block arm's values in the host's calls, the manifest; the reducer: every block run's launches at passes x
      its ops a pass, its multiply-adds a minion a pass, cycles an op at the doubles' law (card 1), and no block key on a
      gemmL run
SPDX-License-Identifier: Apache-2.0
"""
import fcntl
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import mms_common as C  # noqa: E402
import mms_ident as N  # noqa: E402
import tiles_gen as TG  # noqa: E402

PY = [sys.executable, "-B"]
TOY_DIR = None        # <scratch>/toy: the toy plan's kit (src/arms.json, src/sched/, src/tiles/), set by main()

# THE TOY PLAN: the desk tests' sessions (each D case below names the session it runs), with two new tiles
_K = lambda mb, nb, kb, t, kind, mask="0xffffffff", form="burst", fam="T": {  # noqa: E731
    "id": f"{mb}x{nb}x{kb}-{t}-{kind}" + ("" if mask == "0xffffffff" else (f"-s{bin(int(mask, 16)).count('1')}"
          if int(mask, 16) == (1 << bin(int(mask, 16)).count('1')) - 1 else f"-m{mask[2:]}")),
    "mb": mb, "nb": nb, "kb": kb, "type": t, "kind": kind, "shires": mask, "form": form, "families": [fam]}
TOY_ARMS = [_K(1, 1, 2, "fp32", "rnd"), _K(1, 1, 2, "fp32", "zeros"), _K(1, 1, 2, "fp32", "chk"), _K(1, 1, 8, "fp32", "rnd"),
            _K(1, 1, 8, "fp32", "zeros"), _K(1, 1, 20, "fp32", "rnd"), _K(2, 1, 4, "fp32", "rnd"), _K(1, 1, 4, "int8", "rnd"),
            _K(1, 1, 4, "int8", "alt8"), _K(1, 1, 1, "fp32", "rnd", "0xf", "sus3", "S"), _K(1, 1, 1, "fp32", "zeros", "0xf", "sus3", "S"),
            _K(1, 1, 4, "fp32", "rnd", "0xf0f0f0f", "burst", "S"), _K(1, 1, 2, "fp16", "rnd")]
_B1 = ["1x1x2-fp32-rnd", "1x1x2-fp32-zeros", "1x1x2-fp32-chk", "1x1x8-fp32-rnd", "1x1x8-fp32-zeros"]
_B2 = ["1x1x20-fp32-rnd", "2x1x4-fp32-rnd", "1x1x4-int8-rnd", "1x1x4-int8-alt8"]
_S = {"name": "S", "arms": ["1x1x1-fp32-rnd-s4", "1x1x1-fp32-zeros-s4", "1x1x4-fp32-rnd-mf0f0f0f"]}
TOY = {"kit": "1119-mmsweep5", "seed": "toy-1117",
       "tiles": [{"name": "chk", "type": "fp32", "pattern": {"both": {"cycle": [1.0, -1.0, 2.0, -0.5], "by": "checker"}}},
                 {"name": "alt8", "type": "int8", "pattern": {"a": {"bits": ["0x55", "0x2a"], "by": "col"},
                                                              "b": {"cycle": [3, -3], "by": "row"}}}],
       "arms": TOY_ARMS,
       "sessions": {"a1c1": [{"S": "S1", "blocks": [_B1, _B2, _S]},
                             {"S": "S3", "blocks": [{"name": "C", "arms": ["1x1x2-fp32-rnd", "1x1x2-fp32-zeros", "1x1x8-fp32-rnd",
                                                                          "1x1x8-fp32-zeros"]},
                                                    {"name": "S", "arms": ["1x1x1-fp32-rnd-s4", "1x1x1-fp32-zeros-s4"]},
                                                    ["1x1x4-int8-rnd", "1x1x4-int8-alt8"]]},
                             {"S": "S7", "blocks": [_B1, _B2, _S], "reverse": True}],
                    "a2c0": [{"S": "S1", "blocks": [["1x1x2-fp32-rnd", "1x1x2-fp32-zeros", "1x1x2-fp32-chk", "1x1x20-fp32-rnd",
                                                     "2x1x4-fp32-rnd"], ["1x1x4-int8-rnd", "1x1x4-int8-alt8", "1x1x2-fp16-rnd"]]}],
                    "a1c0": [{"S": "S1", "blocks": [["1x1x2-fp32-zeros", "1x1x8-fp32-zeros", "1x1x4-int8-rnd"]]}]}}

# THE NEW TILE SPECS' TOY (M8, D18): alt (a density rung, a toggle rate over k lines), field (sign; an fp16 exponent; an int8
# sign), sparse; one card 1 session of their arms
_ONE = {"const": 1.0}
DN4 = "61b74a52ddb9f346339700f8153117d4f6c5bea362121d80d24ecc74b56270da"    # the second sweep's den4 tile (4 bits on B's halves)
TOY3_TILES = [{"name": "dn4", "type": "fp32", "pattern": {"a": _ONE, "b": {"alt": {"base": 1.0, "nbits": 4, "top": 20,
                                                                                     "cols": "8-15"}}}},
              {"name": "kr2", "type": "fp32", "pattern": {"a": _ONE, "b": {"alt": {"base": 1.0, "nbits": 8, "top": 20,
                                                                                     "rows": "0-3", "cols": "8-15"}}}},
              {"name": "fs", "type": "fp32", "pattern": {"both": {"field": {"base": 1.0, "sign": "random"}}}, "est_as": "ones"},
              {"name": "sp", "type": "fp32", "pattern": {"both": {"sparse": {"zero": 0.5, "of": {"draw": "e37"}}}}},
              {"name": "hx", "type": "fp16", "pattern": {"both": {"field": {"base": 1.0, "exp": [-4, 4]}}}},
              {"name": "isg", "type": "int8", "pattern": {"both": {"field": {"base": 1, "sign": "random"}}}}]
TOY3_ARMS = [_K(1, 1, 1, x["type"], x["name"]) for x in TOY3_TILES] + [_K(1, 1, 1, "fp32", "zeros"), _K(1, 1, 2, "fp32", "dn4")]
TOY3 = {"kit": "1119-mmsweep5", "seed": "toy3-1118", "tiles": TOY3_TILES, "arms": TOY3_ARMS,
        "sessions": {"a1c1": [{"S": "S1", "blocks": [["1x1x1-fp32-dn4", "1x1x1-fp32-kr2", "1x1x1-fp32-fs", "1x1x1-fp32-sp",
                                                      "1x1x1-fp32-zeros", "1x1x2-fp32-dn4"],
                                                     ["1x1x1-fp16-hx", "1x1x1-int8-isg"]]}]}}
LN4 = {"name": "ln4", "type": "fp32", "pattern": {"a": _ONE, "b": {"alt": {"base": 1.0, "nbits": 8, "top": 20, "cols": "8-11"}}}}

# THE FOURTH SWEEP'S SPECS' TOY (W1, D19): rates along K (periodic sets over B's k lines: 1/64 in fp32, 1/32 in fp16),
# structured zeros (7 of 8 A rows; lane 0's B columns), an int8 density rung, sign-only toggles on lanes 0-3, a drawn sparse50
# kind; with a toy prior list (the same bytes as sgn; gz8's input toggles at another value, its counts given; another sparse50
# draw of the same kind; the lab's fp16 randn file of no known type)
_RK = {"period": 4, "phase": 2, "width": 2}
TOY4_TILES = [
    {"name": "rk64", "type": "fp32", "pattern": {"a": _ONE, "b": {"alt": {"base": 1.0, "nbits": 4, "top": 20, "rows": _RK}}}},
    {"name": "rk16", "type": "fp16", "pattern": {"a": _ONE, "b": {"alt": {"base": 1.0, "nbits": 3, "top": 9, "rows": _RK}}}},
    {"name": "gz8", "type": "fp32", "switches": 1000.0, "est_as": "ones",
     "pattern": {"a": {"sparse": {"of": {"const": 1.5}, "rows": {"period": 8, "phase": 0, "width": 7}}}, "b": _ONE}},
    {"name": "i8d3", "type": "int8", "pattern": {"a": {"const": 1}, "b": {"alt": {"base": 1, "nbits": 3, "top": 5, "cols": "8-15"}}}},
    {"name": "sgn", "type": "fp32", "est_as": "ones",
     "pattern": {"a": _ONE, "b": {"alt": {"base": 1.25, "xor": "0x80000000", "cols": "8-11"}}}},
    {"name": "gzc", "type": "fp16", "pattern": {"a": _ONE, "b": {"sparse": {"of": {"draw": "e37"}, "cols": [0, 8]}}}},
    {"name": "sp50k", "type": "fp32", "gen": "sparse50"}]
TOY4_ARMS = [_K(1, 1, 1, x["type"], x["name"]) for x in TOY4_TILES] + [_K(1, 1, 4, "fp32", "rk64"), _K(1, 1, 1, "fp32", "ones"),
                                                                       _K(1, 1, 1, "fp32", "gz8", "0xff"), _K(1, 1, 1, "int8", "i8d3", "0xff")]
TOY4 = {"kit": "1119-mmsweep5", "seed": "toy4-1119", "tiles": TOY4_TILES, "arms": TOY4_ARMS,
        "sessions": {"a1c1": [{"S": "S1", "blocks": [["1x1x1-fp32-rk64", "1x1x1-fp16-rk16", "1x1x1-fp32-gz8", "1x1x1-int8-i8d3",
                                                      "1x1x4-fp32-rk64"],
                                                     ["1x1x1-fp32-sgn", "1x1x1-fp16-gzc", "1x1x1-fp32-sp50k", "1x1x1-fp32-ones"]]}],
                     "a1c0": [{"S": "S1", "blocks": [["1x1x1-fp32-gz8-s8", "1x1x1-int8-i8d3-s8"]]}]}}
# the toy priors: (name, type or None, kind or None, switches or None, how its bytes are made)
TOY4_PRIORS = [("p_same", "fp32", None, None, ("tile", "sgn")),
               ("p_near", "fp32", None, 1000.0, ("spec", {"name": "pnear", "type": "fp32", "pattern": {
                   "a": {"sparse": {"of": {"const": 1.25}, "rows": {"period": 8, "phase": 0, "width": 7}}}, "b": _ONE}})),
               ("p_sp50", "fp32", "sparse50", None, ("spec", {"name": "psp", "type": "fp32", "gen": "sparse50",
                                                              "seed": "toy4-prior-sparse50"})),
               ("p_any", None, None, None, ("lab", "fp16/randn"))]


# THE BLOCK ARMS' TOY (W2, D20): the host's own block, stream and TenB arms through the generator and the doubles; card 1 with
# every family the kit takes and a gemmL control, card 0 with zeros only (its low power)
_BK = lambda tok, t, kind, mask="0xffffffff", form="burst", fam="BK": {  # noqa: E731
    "id": f"{tok}-{t}-{kind}", "arm": tok, "type": t, "kind": kind, "shires": mask, "form": form, "families": [fam]}
TOY5_ARMS = [_BK("gemmc2r8", "fp32", "rnd"), _BK("gemmc2r8", "fp32", "zeros"), _BK("gemmc16r4s", "fp16", "rnd"),
             _BK("gemmh1", "int8", "rnd"), _BK("gemm1", "fp32", "ones"), _BK("mm16", "fp32", "rnd"), _BK("tenb", "fp16", "rnd"),
             _BK("tenb", "int8", "zeros"), _BK("gemmh1", "int8", "zeros"), _BK("gemmc16r4s", "fp16", "zeros"),
             _BK("gemmc2r32", "fp32", "zeros", form="sus3"), _K(1, 1, 1, "fp32", "ones", fam="CTL")]
TOY5 = {"kit": "1119-mmsweep5", "seed": "toy5-1119",
        "tiles": [{"name": "chk", "type": "fp32", "pattern": {"both": {"cycle": [1.0, -1.0, 2.0, -0.5], "by": "checker"}}}],
        "arms": TOY5_ARMS + [_K(1, 1, 2, "fp32", "chk")],
        "sessions": {"a1c1": [{"S": "S1", "blocks": [["gemmc2r8-fp32-rnd", "gemmc2r8-fp32-zeros", "gemmc16r4s-fp16-rnd",
                                                      "gemmh1-int8-rnd", "gemm1-fp32-ones"],
                                                     ["mm16-fp32-rnd", "tenb-fp16-rnd", "tenb-int8-zeros", "1x1x1-fp32-ones"]]}],
                     "a1c0": [{"S": "S1", "blocks": [["gemmc2r8-fp32-zeros", "gemmh1-int8-zeros", "gemmc16r4s-fp16-zeros"],
                                                     {"name": "S", "arms": ["gemmc2r32-fp32-zeros"]}]}]}}
# the host's own lines the kit's grammar (src/mms_common.py arm_of) is read from: each must stand in src/rgm136 as written
HOST_LINES = ['if (s.arm == "tenb") { s.tenb = true; s.n = 1; }',
              'else if (s.arm.rfind("mmp", 0) == 0) { s.mm = s.priv = true; s.n = num("mmp"); }',
              'else if (s.arm.rfind("mm", 0) == 0) { s.mm = true; s.n = num("mm"); }',
              'else if (s.arm.rfind("gemmnc", 0) == 0) { s.gemm = true; gemmTail("gemmnc"); }',
              'else if (s.arm.rfind("gemmc", 0) == 0) { s.gemm = s.coop = true; s.layout = SP_LAYOUT_BYCOL; gemmTail("gemmc"); }',
              'else if (s.arm.rfind("gemmv", 0) == 0) { s.gemm = s.coop = true; s.layout = SP_LAYOUT_VENDOR; gemmTail("gemmv"); }',
              'else if (s.arm.rfind("gemmh", 0) == 0) { s.gemm = s.coop = true; s.layout = SP_LAYOUT_HALFK; gemmTail("gemmh"); }',
              'else if (s.arm.rfind("gemmL", 0) == 0) {',
              'else if (s.arm.rfind("gemm", 0) == 0) { s.gemm = s.coop = true; gemmTail("gemm"); }',
              'opsPerPass = s.n * s.reps * 2 * (s.layout == SP_LAYOUT_HALFK ? SP_GEMM_KT / 2 : SP_GEMM_KT);',
              'opsPerPass = s.mb * s.nb * 2 * s.kb * SP_GEMM_KT;',
              '? 1 : std::max<uint64_t>(1, 64000 / opsPerPass);',          # a gemm arm's calibration passes on a card
              '? 2 : s.priv ? 20 : std::max<uint64_t>(1, 64000 / s.n);',  # mm and mmp
              '? 2 : 64000;',                                              # tenb
              'one(s.gemm ? 1 : s.mm ? 2 : 32, -3);',
              'if (s.tenb && s.gen != "tiles") throw std::runtime_error("tenb runs one tile: gen must be tiles");',
              'const size_t cBytes = s.gemm ? (s.large ? s.mb * s.nb : s.cshared ? 1 : s.n) * size_t(SP_GEMM_C_BLOCK)']


def toy_sched(card, sess):
    return os.path.join(TOY_DIR, "src", "sched", f"{card}-{sess}.json")


def make_toy(scratch, name, plan):
    """make_schedule2.py on a plan written into <scratch>/<name>: (rc, stdout, the kit folder)."""
    d = os.path.join(scratch, name)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "plan.json")
    with open(p, "w") as f:
        json.dump(plan, f, indent=1)
    r = subprocess.run(PY + [os.path.join(HERE, "make_schedule2.py"), "--plan", p, "--out", d], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr, d


def toy4_priors(scratch, name, change=None, bad_sha=None):
    """The toy prior list (TOY4_PRIORS, change: {prior name: (type, kind, switches)} replacing those fields) written into
    <scratch>/<name>/priors.json with its files in priors/; bad_sha: a prior listed at another sha256. -> the list's sha256."""
    d = os.path.join(scratch, name)
    os.makedirs(os.path.join(d, "priors"), exist_ok=True)
    recs = []
    for pname, t, kind, sw, (how, what) in TOY4_PRIORS:
        if change and pname in change:
            t, kind, sw = change[pname]
        if how == "tile":
            data = TG.make_tile(next(x for x in TOY4_TILES if x["name"] == what), TOY4["seed"])
        elif how == "spec":
            data = TG.make_tile(what, TOY4["seed"])
        else:
            data = open(os.path.join(HERE, "tiles", what + ".bin"), "rb").read()
        with open(os.path.join(d, "priors", pname + ".bin"), "wb") as f:
            f.write(data)
        h = C.sha256(os.path.join(d, "priors", pname + ".bin"))
        recs.append({"name": pname, "path": f"priors/{pname}.bin", "sha256": ("0" * 64 if pname == bad_sha else h), "type": t,
                     "kind": kind, "switches": sw})
    raw = json.dumps({"priors": recs}, indent=1).encode()
    with open(os.path.join(d, "priors.json"), "wb") as f:
        f.write(raw)
    return C.sha256(os.path.join(d, "priors.json"))


def dry(scratch, name, card, sess, *extra, scale="0.02", timeout=900, sched=None):
    out = os.path.join(scratch, name)
    os.makedirs(out, exist_ok=True)
    r = subprocess.run(PY + [os.path.join(HERE, "run_mms.py"), "session", "--dry", "--scale", scale, "--card", card, "--sched",
                             sched or toy_sched(card, sess), "--t0", str(int(time.time())), "--out", out]
                       + list(extra), cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    log = open(os.path.join(out, "session.log")).read() if os.path.exists(os.path.join(out, "session.log")) else ""
    q = json.load(open(os.path.join(out, "queue.json"))) if os.path.exists(os.path.join(out, "queue.json")) else {}
    calls = open(os.path.join(out, "device-calls.txt")).read().splitlines() if os.path.exists(os.path.join(out, "device-calls.txt")) else []
    return r.returncode, out, log, q, calls


def reduce(scratch, out, name):
    j = os.path.join(scratch, name + "-data.json")
    r = subprocess.run(PY + [os.path.join(HERE, "reduce_mms.py"), out, "--out", j], capture_output=True, text=True)
    return r.returncode, (json.load(open(j)) if os.path.exists(j) else {}), r.stderr[-500:]


def law(values, t):
    g = C.arm_of(values)
    if g and g["family"] != "gemmL":     # the doubles' toy law for a block, stream or TenB arm (src/fake_card_mms.py block_values)
        f = 1.0
        if g["kernel"] == "block":
            f = (1.0 + (0.5 / g["repeats"] if g["nblocks"] > 1 else 0.0)) * (1.2 if g["layout"] == "packed" else 1.0)
        return (500.0 if t != "int8" else 250.0) * f
    mb, nb, kb = (int(v) for v in values.split(":")[0][5:].split("x"))
    reg = "l2" if (mb, nb, kb) == (1, 1, 1) else ("l3" if 2 * mb * kb + nb * kb + 2 * mb * nb <= 32 else "dram")
    return {"l2": 500.0 if t != "int8" else 250.0, "l3": 1000.0, "dram": 1500.0}[reg]


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    scratch = os.path.abspath(argv[0])
    os.makedirs(scratch, exist_ok=True)
    res = []

    def case(name, ok, detail=""):
        res.append(bool(ok))
        print(f"{name} {'PASS' if ok else 'FAIL'} {detail}", flush=True)

    b = C.selfcheck()
    case("M1", not b, "; ".join(b))
    b = N.selfcheck()
    case("M2", not b, "; ".join(b))
    r = subprocess.run(PY + [os.path.join(HERE, "make_schedule2.py"), "--check"], capture_output=True, text=True)
    case("M3", r.returncode == 0 and "MAKE CHECK PASS" in r.stdout, r.stdout.strip())
    r = subprocess.run(PY + [os.path.join(HERE, "check_mms.py"), "--check"], capture_output=True, text=True)
    case("M4", r.returncode == 0 and "CHECK PASS" in r.stdout, r.stdout.strip().splitlines()[-1] if r.stdout else r.stderr)
    r = subprocess.run(["bash", os.path.join(HERE, "preflight_mms.sh"), "a1c1", "--audit-only"], cwd=ROOT, capture_output=True,
                       text=True)
    allout = r.stdout + r.stderr
    first = next((ln for ln in allout.splitlines() if ln.startswith("dmcmd_audit:")), "")
    case("M5", r.returncode == 0 and first.startswith("dmcmd_audit: GO") and "WRAPPER" not in allout
         and "[WRITE" not in allout and "NO-GO" not in allout, first)
    r = subprocess.run(PY + [os.path.join(HERE, "tiles_gen.py"), "--check"], capture_output=True, text=True)
    case("M6", r.returncode == 0 and "TILES CHECK PASS" in r.stdout, r.stdout.strip().replace("\n", "; "))

    global TOY_DIR
    rc, txt, TOY_DIR = make_toy(scratch, "toy", TOY)
    b = C.selfcheck(os.path.join(TOY_DIR, "src")) if rc == 0 else ["not made"]
    over = dict(TOY, sessions={"a1c0": [{"S": "S1", "blocks": [["1x1x2-fp32-chk"]]}]})     # a tile card 0 takes, over 52 W
    rc2, txt2, _ = make_toy(scratch, "toy-over", over)
    drift = dict(TOY, tiles=TOY["tiles"] + [{"name": "tenth", "type": "fp32", "pattern": {"both": {"const": 0.1}}}],
                 arms=TOY_ARMS + [_K(1, 1, 48, "fp32", "tenth")], sessions={})
    rc3, txt3, _ = make_toy(scratch, "toy-drift", drift)
    many = [_K(m, n, k, "int8", "zeros", form="sus3") for m in (1, 2, 3) for n in (1, 2, 3, 5) for k in (1, 2, 3, 5)]
    big = dict(TOY, arms=TOY_ARMS + many, sessions={"a1c1": [{"S": "S2", "blocks": [[a["id"] for a in many], _B1]}]})
    rc4, txt4, _ = make_toy(scratch, "toy-big", big)
    drawn = {"name": "spf", "type": "fp32", "gen": "sparse50"}         # a drawn fp pool: random data whatever its file holds
    dones = dict(TOY, tiles=TOY["tiles"] + [dict(drawn, est_as="ones")], arms=TOY_ARMS + [_K(1, 1, 2, "fp32", "spf")], sessions={})
    rc5, txt5, _ = make_toy(scratch, "toy-drawn-ones", dones)
    dc0 = dict(TOY, tiles=TOY["tiles"] + [drawn], arms=TOY_ARMS + [_K(1, 1, 2, "fp32", "spf")],
               sessions={"a1c0": [{"S": "S1", "blocks": [["1x1x2-fp32-spf"]]}]})
    rc6, txt6, _ = make_toy(scratch, "toy-drawn-c0", dc0)
    ok = rc == 0 and not b and "REFUSED" in txt2 and "over its planning line" in txt2 and "REFUSED" in txt3 and "drifts" in txt3 \
        and "REFUSED" in txt4 and "session size" in txt4 and rc5 == 3 and "est_as rnd only" in txt5 and rc6 == 3 \
        and "drawn pool" in txt6
    case("M7", ok, f"toy made rc {rc} ({len(TOY_ARMS)} arms, sessions a1c1 S1 S3 S7, a2c0 S1, a1c0 S1){'; ' + '; '.join(b) if b else ''}; "
                   f"over the line: {txt2.strip()[-90:]}; drift: {txt3.strip()[-80:]}; over the size: {txt4.strip()[-70:]}; "
                   f"drawn at ones: {txt5.strip()[-60:]}; drawn on card 0: {txt6.strip()[-60:]}")

    rc, txt, d3 = make_toy(scratch, "toy3", TOY3)
    b = C.selfcheck(os.path.join(d3, "src")) if rc == 0 else ["not made: " + txt.strip()[-200:]]
    am = C.load(os.path.join(d3, "src", "arms.json")) if rc == 0 else {"tiles": {}}
    dn4 = os.path.join(d3, "src", "tiles", "fp32", "dn4.bin")
    sha_ok = os.path.exists(dn4) and C.sha256(dn4) == DN4
    checks = [c.get("result") for x in am["tiles"].values() for c in x["checks"].values()]
    chk_ok = len(am["tiles"]) == len(TOY3_TILES) and checks and all(c in ("exact", "approx") for c in checks)
    r = subprocess.run(PY + [os.path.join(HERE, "tiles_gen.py"), "--pairs", "--plan", os.path.join(d3, "plan.json")],
                       capture_output=True, text=True)
    pairs_ok = r.returncode == 0 and r.stdout.strip().endswith("PAIRS PASS")
    t_ln4 = TOY3["tiles"] + [LN4]
    a_ln4 = TOY3_ARMS + [_K(1, 1, 1, "fp32", "ln4")]
    rc1, txt1, d1 = make_toy(scratch, "toy3-eq", dict(TOY3, tiles=t_ln4, arms=a_ln4, sessions={}))
    r = subprocess.run(PY + [os.path.join(HERE, "tiles_gen.py"), "--pairs", "--plan", os.path.join(d1, "plan.json")],
                       capture_output=True, text=True)
    pairs_no = r.returncode == 3 and "PAIRS REFUSED: dn4 and ln4" in r.stdout
    cnt = lambda a, b: [dict(x, switches=a) if x["name"] == "dn4" else dict(x, switches=b) if x["name"] == "ln4" else x
                        for x in t_ln4]  # noqa: E731
    rc2, txt2, _ = make_toy(scratch, "toy3-diff", dict(TOY3, tiles=cnt(71357.0, 67470.0), arms=a_ln4, sessions={}))
    rc3, txt3, _ = make_toy(scratch, "toy3-same", dict(TOY3, tiles=cnt(71357.0, 71357.0), arms=a_ln4, sessions={}))
    hx2 = {"name": "hx2", "type": "fp16", "pattern": {"both": {"field": {"base": 1.0, "exp": [10, 20]}}}}
    rc4, txt4, _ = make_toy(scratch, "toy3-exp", dict(TOY3, tiles=TOY3["tiles"] + [hx2], sessions={}))
    inf = {"name": "inf", "type": "fp32", "pattern": {"a": _ONE, "b": {"alt": {"base": 1.0, "xor": "0x40000000"}}}}
    rc5, txt5, _ = make_toy(scratch, "toy3-inf", dict(TOY3, tiles=TOY3["tiles"] + [inf], sessions={}))
    ok = rc == 0 and not b and sha_ok and chk_ok and pairs_ok and pairs_no \
        and rc1 == 3 and "give both tiles' switches" in txt1 and rc2 == 3 and "different counted switches" in txt2 \
        and rc3 == 0 and rc4 == 3 and "normal range" in txt4 and rc5 == 3 and "inf or NaN" in txt5
    case("M8", ok, f"toy3 made rc {rc} ({len(TOY3_TILES)} tiles, checks {sorted(set(checks))}){'; ' + '; '.join(b) if b else ''}; "
                   f"dn4 = the second sweep's den4: {sha_ok}; pairs: {pairs_ok}, with ln4 refused: {pairs_no}; no counts: "
                   f"{txt1.strip()[-70:]}; counts apart: {txt2.strip()[-60:]}; equal counts rc {rc3}; exp: {txt4.strip()[-50:]}; "
                   f"inf: {txt5.strip()[-50:]}")

    # W1: the fourth sweep's specs and the wider pair check (TOY4 with its toy prior list)
    def toy4(name, plan_extra=None, change=None, bad_sha=None, list_sha=None, priors=True):
        plan = dict(TOY4, **(plan_extra or {}))
        if priors:
            h = toy4_priors(scratch, name, change, bad_sha)
            plan["priors"] = {"path": "priors.json", "sha256": list_sha or h}
        return make_toy(scratch, name, plan)
    rc, txt, d4 = toy4("toy4")
    b = C.selfcheck(os.path.join(d4, "src")) if rc == 0 else ["not made: " + txt.strip()[-300:]]
    am = C.load(os.path.join(d4, "src", "arms.json")) if rc == 0 else {"tiles": {}}
    checks = [(x["gen"], c.get("result")) for x in am["tiles"].values() for c in x["checks"].values()]
    chk_ok = len(am["tiles"]) == len(TOY4_TILES) and checks and all(
        c in (("exact", "approx") if g == "tiles" else ("drawn",)) for g, c in checks)
    shape = []
    if rc == 0:
        def rd(t, n):
            return open(os.path.join(d4, "src", "tiles", t, n + ".bin"), "rb").read()
        it = {n: TG.input_toggles(rd(t, n)) for t, n in (("fp32", "rk64"), ("fp16", "rk16"), ("fp32", "gz8"), ("fp32", "sgn"))}
        wa, _ = TG.unpack("fp32", rd("fp32", "gz8"))
        _, wb = TG.unpack("fp16", rd("fp16", "gzc"))
        shape = [it["rk64"]["b"] == 0.0625 and it["rk64"]["a"] == 0, it["rk16"]["b"] == 0.1875 and it["rk16"]["a"] == 0,
                 sum(1 for r in wa for w in r if w == 0) == 14 * 16 and all(w == 0 for i in range(16) if i % 8 != 7 for w in wa[i]),
                 sum(1 for r in wb for w in r if w == 0) == 2 * 32 and all(r[0] == 0 and r[8] == 0 for r in wb),
                 it["sgn"]["pooled"] == 0.5,
                 sorted(TG._index_set(_RK, 16, "test")) == [2, 3, 6, 7, 10, 11, 14, 15]]
    r = subprocess.run(PY + [os.path.join(HERE, "tiles_gen.py"), "--pairs", "--plan", os.path.join(d4, "plan.json")],
                       capture_output=True, text=True)
    lines = r.stdout.splitlines()
    vline = lambda a, b: next((ln for ln in lines if ln.startswith(f"{a} / {b} ")), "")  # noqa: E731
    pairs_ok = r.returncode == 0 and r.stdout.strip().endswith("PAIRS PASS") and vline("sgn", "prior:p_same").endswith("same bytes") \
        and vline("gz8", "prior:p_near").endswith(" same") and vline("sp50k", "prior:p_sp50").endswith("same kind") \
        and any(ln.startswith("wider: ") for ln in lines)
    rc1, txt1, _ = toy4("toy4-nocount", change={"p_near": ("fp32", None, None)})
    rc2, txt2, _ = toy4("toy4-apart", change={"p_near": ("fp32", None, 1030.0)})
    rc3, txt3, _ = toy4("toy4-held", change={"p_sp50": ("fp32", "tiles", None)})
    rc3b, txt3b, _ = toy4("toy4-unknown", change={"p_sp50": ("fp32", None, None)})
    rc4, txt4, _ = toy4("toy4-listsha", list_sha="1" * 64)
    rc5, txt5, _ = toy4("toy4-filesha", bad_sha="p_any")
    c2 = {"name": "c2", "type": "int8", "pattern": {"both": {"const": 2}}}
    rc6, txt6, _ = toy4("toy4-c2", plan_extra={"tiles": TOY4_TILES + [c2], "arms": TOY4_ARMS + [_K(1, 1, 1, "int8", "c2")]})
    wide = dict(TOY4_TILES[0], name="rkw", pattern={"a": _ONE, "b": {"alt": {"base": 1.0, "nbits": 4, "top": 20, "rows": {
        "period": 4, "phase": 0, "width": 4}}}})
    rc7, txt7, _ = toy4("toy4-period", plan_extra={"tiles": TOY4_TILES + [wide]})
    fol = TG.pair_verdict(1.0, 0.97, 1000.0, 970.0)
    rc8, txt8, _ = toy4("toy4-nopriors", priors=False)
    ok = rc == 0 and not b and chk_ok and shape and all(shape) and pairs_ok \
        and rc1 == 3 and "gz8 and prior:p_near" in txt1 and "give both tiles' switches" in txt1 \
        and rc2 == 3 and "gz8 and prior:p_near" in txt2 and "different counted switches" in txt2 \
        and rc3 == 3 and "sp50k and prior:p_sp50" in txt3 and rc3b == 0 \
        and rc4 == 3 and "sha256" in txt4 and rc5 == 3 and "not at the list's sha256" in txt5 \
        and rc6 == 3 and "c2 and kind:int8/" in txt6 and rc7 == 3 and "periodic set" in txt7 \
        and fol[1] == "REFUSED" and rc8 == 0 and "wider check" in txt8 and "not run" in txt8
    case("W1", ok, f"toy4 made rc {rc} ({len(TOY4_TILES)} tiles, checks {sorted(set(checks))}){'; ' + '; '.join(b) if b else ''}; "
                   f"rates, zeros, sign, the periodic set: {shape}; pairs with priors: {pairs_ok}; no counts: rc {rc1}; counts "
                   f"apart: rc {rc2}; the drawn kind against a held prior: rc {rc3}, against a prior run in ways not known: rc "
                   f"{rc3b}; list sha: rc {rc4}; file sha: rc {rc5}; held int8 at 0 toggles: rc {rc6}; "
                   f"period as wide: rc {rc7}; follows: {fol[1]}; no priors: rc {rc8}")

    # W2: the block arms (TOY5): made, their records by the host's grammar, the host's own lines, and every refusal
    rc, txt, d5 = make_toy(scratch, "toy5", TOY5)
    b = C.selfcheck(os.path.join(d5, "src")) if rc == 0 else ["not made: " + txt.strip()[-200:]]
    am = {a["id"]: a for a in C.load(os.path.join(d5, "src", "arms.json"))["arms"]} if rc == 0 else {}
    rec_bad = []
    for aid, want in {"gemmc2r8-fp32-rnd": ("gemmc2r8:randn:src/tiles/fp32/randn.bin", 1024, 10.0, (1024, 512, 8192)),
                      "gemmc16r4s-fp16-rnd": ("gemmc16r4s:randn:src/tiles/fp16/randn.bin", 4096, 50.0, (1024, 512, 65536)),
                      "gemmh1-int8-rnd": ("gemmh1:randn:src/tiles/int8/full.bin", 32, 5.0, (1024, 512, 1024)),
                      "mm16-fp32-rnd": ("mm16:randn:src/tiles/fp32/randn.bin", 16, 1.03125, (16384, 16, 256)),
                      "tenb-fp16-rnd": ("tenb:tiles:src/tiles/fp16/randn.bin", 1, 1.001953, (16384, 16, 32)),
                      "tenb-int8-zeros": ("tenb:tiles:src/tiles/int8/zeros.bin", 1, 1.001953, (16384, 16, 64))}.items():
        x = am.get(aid) or {}
        if (x.get("values"), x.get("ops_per_minion_pass"), x.get("footprint_mb"), (x.get("M"), x.get("N"), x.get("K"))) != want \
                or x["M"] * x["N"] * x["K"] != 1024 * x["ops_per_minion_pass"] * x["macs_per_op"]:
            rec_bad.append(aid)
    if am and (am["gemmc16r4s-fp16-rnd"].get("c_shared") is not True or am["gemmh1-int8-rnd"].get("kt") != 16
               or am["gemm1-fp32-ones"].get("layout") != "packed" or "arm" in am["1x1x1-fp32-ones"]):
        rec_bad.append("fields")
    est = {}
    if rc == 0:
        for card in ("a1c1", "a1c0"):
            for r_ in C.load(os.path.join(d5, "src", "sched", f"{card}-S1.json"))["runs"]:
                est[(card, r_["arm"])] = r_["est_peak_w"]
    est_want = {("a1c1", "gemmc2r8-fp32-rnd"): 66.6, ("a1c1", "gemmc16r4s-fp16-rnd"): 63.7, ("a1c1", "gemmh1-int8-rnd"): 52.4,
                ("a1c1", "gemm1-fp32-ones"): 46.9, ("a1c1", "mm16-fp32-rnd"): 66.6, ("a1c1", "tenb-fp16-rnd"): 63.7,
                ("a1c1", "tenb-int8-zeros"): 51.2, ("a1c1", "gemmc2r8-fp32-zeros"): 38.4, ("a1c1", "1x1x1-fp32-ones"): 46.9,
                ("a1c0", "gemmc2r8-fp32-zeros"): 37.8, ("a1c0", "gemmh1-int8-zeros"): 40.0, ("a1c0", "gemmc2r32-fp32-zeros"): 37.8}
    est_bad = {k: (est.get(k), v) for k, v in est_want.items() if est.get(k) != v}
    src_txt = open(os.path.join(HERE, "rgm136", "host", "main.cpp")).read()
    pos = [src_txt.find(x) for x in HOST_LINES]
    host_ok = all(p >= 0 for p in pos) and pos[:9] == sorted(pos[:9]) and \
        "#define SP_GEMM_KT 32u" in open(os.path.join(HERE, "rgm136", "sparsity_args.h")).read()

    def refuse(tag, arms=None, sessions=None, why=""):
        plan = dict(TOY5, arms=TOY5["arms"] + (arms or []), sessions=sessions if sessions is not None else {})
        r_, t_, _ = make_toy(scratch, "toy5-" + tag, plan)
        return (r_ == 3 and "MAKE REFUSED" in t_ and why in t_), t_.strip()[-110:]
    tests = {
        "gemmv": refuse("gemmv", [_BK("gemmv1", "fp32", "zeros")], why="vendor-stride"),
        "gemmnc": refuse("gemmnc", [_BK("gemmnc1", "fp32", "zeros")], why="without cooperative loads"),
        "mmp": refuse("mmp", [_BK("mmp64", "fp32", "zeros")], why="private-pool"),
        "gemmL token": refuse("gemmL", [_BK("gemmL1x1x1", "fp32", "zeros")], why="written with mb, nb, kb"),
        "s before r": refuse("sr", [_BK("gemmc16sr4", "fp32", "zeros")], why="not the host's grammar"),
        "mm16x": refuse("mmx", [_BK("mm16x", "fp32", "zeros")], why="not the host's grammar"),
        "a colon": refuse("colon", [_BK("gemmc2:randn", "fp32", "zeros")], why="not the host's grammar"),
        "leading zero": refuse("lz", [_BK("gemmc02", "fp32", "zeros")], why="not the host's grammar"),
        "r1": refuse("r1", [_BK("gemmc2r1", "fp32", "zeros")], why="r1 is the default"),
        "B 33": refuse("b33", [_BK("gemmc33", "fp32", "zeros")], why="at most 32"),
        "R 33": refuse("r33", [_BK("gemmc2r33", "fp32", "zeros")], why="at most 32"),
        "N 257": refuse("n257", [_BK("mm257", "fp32", "zeros")], why="at most 256"),
        "a mask": refuse("mask", [_BK("gemmc4r4", "fp32", "zeros", mask="0xff")], why="whole chip"),
        "a plan tile": refuse("tile", [_BK("gemmc4r4", "fp32", "chk")], why="lab's kinds only"),
        "mb on a block arm": refuse("mb", [dict(_BK("gemmc4r4", "fp32", "zeros"), mb=1)], why="has no mb"),
        "the id": refuse("id", [dict(_BK("gemmc4r4", "fp32", "zeros"), id="gemmc4r4-fp32-rnd")], why="is not its fields' id"),
        "fp32 rnd on card 0": refuse("c0rnd", sessions={"a1c0": [{"S": "S1", "blocks": [["gemmc2r8-fp32-rnd"]]}]},
                                     why="takes no fp32 rnd"),
        "int8 rnd on card 0": refuse("c0i8", sessions={"a1c0": [{"S": "S1", "blocks": [["gemmh1-int8-rnd"]]}]},
                                     why="over its planning line 52"),
        "tenb zeros on card 0": refuse("c0tenb", sessions={"a1c0": [{"S": "S1", "blocks": [["tenb-int8-zeros"]]}]},
                                       why="over its planning line 52"),
        "mm int8 on card 1": refuse("c1mm", [_BK("mm16", "int8", "rnd")],
                                    sessions={"a1c1": [{"S": "S1", "blocks": [["mm16-int8-rnd"]]}]}, why="plan level 66.6")}
    no = [k for k, (v, _) in tests.items() if not v]
    ok = rc == 0 and not b and not rec_bad and not est_bad and host_ok and not no
    case("W2", ok, f"toy5 made rc {rc} ({len(TOY5['arms'])} arms){'; ' + '; '.join(b) if b else ''}; records off: {rec_bad}; "
                   f"estimates off: {est_bad}; the host's lines in order: {host_ok}; refusals {len(tests) - len(no)} of {len(tests)}"
                   + (f"; NOT refused as wanted: {[(k, tests[k][1]) for k in no]}" if no else ""))

    # D1: card 1's S3 to its tenth run: anchor, null, bursts and a null; then card 1's S1 sus3 run is in D1b below
    sched = C.load(toy_sched("a1c1", "S3"))
    rc, out, log, q, calls = dry(scratch, "D1", "a1c1", "S3", "--only", "10")
    n_proc = sum(C.FORM_KEYS[r["form"]] for r in sched["runs"][:10])
    ok = rc == 0 and len([x for x in q.get("queue", []) if x.get("ran")]) == 10 and os.path.exists(os.path.join(out, "MANIFEST.sha256")) \
        and sum(1 for c in calls if "sparsity_host" in c) == 3 + n_proc and sum(1 for c in calls if c.endswith(" config")) == 2 \
        and sum(1 for c in calls if " sample " in c) == 1 and all(not c.split()[0].startswith("/") for c in calls)
    det = f"rc {rc}, calls {len(calls)} (host {sum(1 for c in calls if 'sparsity_host' in c)}, want {3 + n_proc})"
    if ok:
        rrc, d, err = reduce(scratch, out, "D1")
        arm = next(x for x in d["runs"] if x["role"] == "arm" and x["form"] == "burst" and "rnd" in x["arm"])
        v = arm["views"]["band600"]
        want_T = law(arm["values"], arm["type"]) / 600e6 * 1e6
        minion = v["rails"]["minion"]["dW"]
        nul = [x for x in d["runs"] if x["form"] == "null"]
        nl = [x["views"]["band600"]["dP_line"] for x in nul if x.get("views", {}).get("band600")]
        ok = rrc == 0 and abs(v["T_op_us"] / want_T - 1) < 0.01 and 19.0 < v["dP_w"] < 23.0 \
            and abs(v["J_op"] - v["dP_w"] * v["T_op_us"] * 1e-6 / 1024) < 1e-15 and 0.40 < minion / v["dP_w"] < 0.50 \
            and nl and all(abs(x) < 0.5 for x in nl) and v["baseline_rule"] == "line"
        det += (f"; T_op {v['T_op_us']:.4f} us (law {want_T:.4f}); dP {v['dP_w']:.2f} W (the doubles' lift 20 W + leakage); minion rail "
                f"{minion:.2f} W = {minion / v['dP_w']:.3f} of dP (the doubles: 0.45 of the lift); nulls' line reading {[round(x, 3) for x in nl]}")
    case("D1", ok, det)

    s2 = C.load(toy_sched("a2c0", "S1"))
    first_arm = next(r["arm"] for r in s2["runs"] if r["form"] == "burst" and r["role"] != "anchor")
    rc, out, log, q, calls = dry(scratch, "D2", "a2c0", "S1", "--only", "6", "--trip-arm", first_arm, "--trip-w", "60")
    ran = [x["arm"] for x in q.get("queue", []) if x.get("ran")]
    ok = rc == 0 and "board" in str(q.get("stop")) and "STOP:" in log and "config end" in log \
        and os.path.exists(os.path.join(out, "MANIFEST.sha256")) and ran and ran[-1] == first_arm \
        and all(not x.get("ran") for x in q["queue"][len(ran):])
    case("D2", ok, f"rc {rc}; stop {q.get('stop')}; ran {ran}")

    rc, out, log, q, calls = dry(scratch, "D3", "a1c1", "S1", "--only", "1", "--config-fail")
    ok = rc == 0 and "one re-run in 5 s" in log and len([x for x in q.get("queue", []) if x.get("ran")]) == 1
    case("D3", ok, f"rc {rc}")

    rc, out, log, q, calls = dry(scratch, "D4", "a1c1", "S1", "--only", "2", "--wrong-card")
    ok = rc == 16 and "smoke gate failed" in log and not any(x.get("ran") for x in q.get("queue", [])) and "ANOTHER" in log
    case("D4", ok, f"rc {rc}")

    rc, out, log, q, calls = dry(scratch, "D5", "a1c1", "S1", "--only", "6", "--stop-after", "2")
    ok = rc == 0 and "operator" in str(q.get("stop")) and len([x for x in q["queue"] if x.get("ran")]) == 2 \
        and os.path.exists(os.path.join(out, "MANIFEST.sha256"))
    case("D5", ok, f"rc {rc}; stop {q.get('stop')}")

    rc, out, log, q, calls = dry(scratch, "D6", "a1c0", "S1", "--only", "1")
    ok = rc == 0 and "/dev/et0_mgmt, physical device ID 0, minion_mv 519" in log and "card 0 only" in log
    case("D6", ok, f"rc {rc}")

    r = subprocess.run(PY + [os.path.join(HERE, "collect_mms.py"), os.path.join(scratch, "D1"), "--out", os.path.join(scratch, "D7")],
                       capture_output=True, text=True)
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr
    ok = "COPY-BACK EXACT" in r.stdout and "PRIVACY READ: 0 hit" in r.stdout and "COLLECT OK" in last
    case("D7", ok, last)

    rc, out, log, q, calls = dry(scratch, "D8", "a1c1", "S1", "--only", "2", "--wrong-config")
    n_cfg = sum(1 for c in calls if c.endswith(" config"))
    ok = rc == 16 and "the card's identity" in log and n_cfg == 1 and "no closing config read" in log \
        and not any(x.get("ran") for x in q.get("queue", []))
    case("D8", ok, f"rc {rc}; config calls {n_cfg}")

    rc, out, log, q, calls = dry(scratch, "D9", "a1c1", "S1", "--only", "40", "--sampler-stall", "2500", timeout=300)
    n_s = sum(1 for c in calls if " sample " in c)
    n_cfg = sum(1 for c in calls if c.endswith(" config"))
    lo = q.get("leftover") or {}
    ok = n_s == 1 and n_cfg == 1 and "LEFTOVER" in log and "no closing config read" in log and lo.get("resolved") is True \
        and any(x["what"] == "sampler" for x in lo.get("records", []))
    case("D9", ok, f"rc {rc}; sampler calls {n_s}; config calls {n_cfg}; leftover {lo.get('resolved')}; stop {q.get('stop')}")

    hang_arm = next(r["arm"] for r in sched["runs"] if r["form"] == "burst" and r["role"] == "arm")
    rc, out, log, q, calls = dry(scratch, "D10", "a1c1", "S3", "--only", "10", "--host-hang", hang_arm, timeout=600)
    lo = q.get("leftover") or {}
    st = json.load(open(os.path.join(out, "status.json"))) if os.path.exists(os.path.join(out, "status.json")) else {}
    ran = [x["arm"] for x in q.get("queue", []) if x.get("ran")]
    ok = "outlived" in str(q.get("stop")) and ran and ran[-1] == hang_arm and lo.get("resolved") is True \
        and any(x["what"] == "host" for x in lo.get("records", [])) and "no closing config read" in log \
        and (st.get("leftover") or {}).get("resolved") is True and sum(1 for c in calls if c.endswith(" config")) == 1
    case("D10", ok, f"rc {rc}; stop {q.get('stop')}; ran {len(ran)}, the last {ran[-1] if ran else None}; leftover {lo.get('resolved')} "
                    f"after {lo.get('waited_s')} s")

    rc, out, log, q, calls = dry(scratch, "D11", "a1c1", "S3", "--only", "12", "--host-fail-after", "4")
    ok = rc == 0 and "failed processes in a row" in str(q.get("stop")) and "config end" in log
    case("D11", ok, f"rc {rc}; stop {q.get('stop')}")

    rc, out, log, q, calls = dry(scratch, "D12", "a2c0", "S1", "--only", "16")
    ok = rc == 0
    det = f"rc {rc}"
    if ok:
        rrc, d, err = reduce(scratch, out, "D12")
        bad = []
        for x in d["runs"]:
            if not x.get("ran") or x["form"] == "null":
                continue
            reg = "l2" if x["arm"].startswith("1x1x1-") else None
            t, kind = x["arm"].split("-")[1], x["arm"].split("-")[2]
            mb, nb, kb = (int(v) for v in x["arm"].split("-")[0].split("x"))
            reg = "l2" if (mb, nb, kb) == (1, 1, 1) else ("l3" if 2 * mb * kb + nb * kb + 2 * mb * nb <= 32 else "dram")
            lifts = {"rnd": {"fp32": 20, "fp16": 20, "int8": 10}, "ones": {"fp32": 10, "fp16": 10, "int8": 5},
                     "zeros": {"fp32": 5, "fp16": 5, "int8": 5}}
            lift = lifts.get(kind, lifts["rnd"])[t] * (1.9 if reg == "l2" else 1.0) + 8.0     # a tile: rnd's, as the doubles
            want = 20.0 + lift > 45.0
            if bool(x.get("capped")) != want:
                bad.append(f"{x['arm']} capped {x.get('capped')} (doubles {want})")
            if x["role"] == "time" and (x["views"].get("win") or {}).get("dP_w") is not None:
                bad.append(f"{x['arm']}: a time run with an energy figure")
            w = x["views"].get("win")
            if w and w.get("kclock_mhz") and not 790 <= w["kclock_mhz"] <= 810:
                bad.append(f"{x['arm']}: the window's clock {w['kclock_mhz']:.0f} MHz")
        n_capped = sum(1 for x in d["runs"] if x.get("capped"))
        ok = rrc == 0 and not bad and n_capped > 0
        det += f"; capped runs {n_capped}; " + ("; ".join(bad[:4]) if bad else "every flag as the doubles' cap says")
    case("D12", ok, det)

    def leftover_case(name, which, only, want_rc, want_cfg):
        rc, out, log, q, calls = dry(scratch, name, "a1c1", "S3", "--only", str(only), "--config-hang", which, timeout=400)
        lo = q.get("leftover") or {}
        st = json.load(open(os.path.join(out, "status.json"))) if os.path.exists(os.path.join(out, "status.json")) else {}
        n_cfg = sum(1 for c in calls if c.endswith(" config"))
        ended = os.path.exists(os.path.join(out, "fakedev", f"config-hang-{which}.ended"))
        ok = rc == want_rc and n_cfg == want_cfg and lo.get("resolved") is True and ended \
            and any(x["what"] == "config-read" for x in lo.get("records", [])) and (st.get("leftover") or {}).get("resolved") is True \
            and "LEFTOVER resolved" in log and os.path.exists(os.path.join(out, "MANIFEST.sha256"))
        return ok, rc, log, q, n_cfg, lo, ended

    ok, rc, log, q, n_cfg, lo, ended = leftover_case("D13", "start", 2, 16, 1)
    ok = ok and "no re-run" in log and "no closing config read" in log and not any(x.get("ran") for x in q.get("queue", []))
    case("D13", ok, f"rc {rc}; config calls {n_cfg}; leftover resolved {lo.get('resolved')} after {lo.get('waited_s')} s; the double "
                    f"ended by itself {ended}")

    ok, rc, log, q, n_cfg, lo, ended = leftover_case("D14", "end", 1, 0, 2)
    ok = ok and len([x for x in q.get("queue", []) if x.get("ran")]) == 1 and "config end: config read (end) left" in log
    case("D14", ok, f"rc {rc}; config calls {n_cfg}; leftover resolved {lo.get('resolved')} after {lo.get('waited_s')} s; the double "
                    f"ended by itself {ended}")

    rc, out, log, q, calls = dry(scratch, "D15", "a1c1", "S3", "--only", "2", "--closing-holder")
    n_cfg = sum(1 for c in calls if c.endswith(" config"))
    close_txt = open(os.path.join(out, "etwho-close.txt")).read() if os.path.exists(os.path.join(out, "etwho-close.txt")) else ""
    ok = rc == 0 and n_cfg == 1 and "no closing config read: a holder or a device process right before it" in log \
        and "holder line(s) of another login on the card" in close_txt and len([x for x in q.get("queue", []) if x.get("ran")]) == 2
    case("D15", ok, f"rc {rc}; config calls {n_cfg}; {close_txt.strip()}")

    # et-who calls under --dry: 1 before the first card command, 2 the identity read, then one before every run: run k (from 0)
    # is call 3 + k, so --holder-after 2 + k shows the holder first at run k
    k = next(i for i, r in enumerate(s2["runs"]) if i >= 1 and r["role"] != "anchor")
    rc, out, log, q, calls = dry(scratch, "D16", "a2c0", "S1", "--only", str(k + 2), "--holder-after", str(2 + k))
    qq = q.get("queue", [])
    ran = [x for x in qq if x.get("ran")]
    ok = rc == 0 and len(ran) == k and len(qq) > k and qq[k].get("role") != "anchor" and not qq[k].get("ran") \
        and "holder line(s) of another login" in str(q.get("stop")) and "no closing config read" in log
    case("D16", ok, f"rc {rc}; ran {len(ran)} (want {k}); run {k} ({qq[k].get('role') if len(qq) > k else None}): "
                    f"{qq[k].get('why') if len(qq) > k else None}")

    lock = os.path.join(scratch, "D17-box.lock")
    other = os.path.join(scratch, "D17-other.lock")
    probe = os.path.join(scratch, "D17-probe.py")
    with open(probe, "w") as f:
        f.write("import os, sys\nsys.path.insert(0, sys.argv[1])\nimport run_mms as M\n"
                "fd, how = M.take_box_lock(sys.argv[2], os.environ.get('MMS_BOX_LOCK_FD'))\n"
                "print(('HELD ' if fd is not None else 'REFUSED ') + how)\n")
    open(other, "a").close()
    env_n = {k_: v for k_, v in os.environ.items() if k_ != "MMS_BOX_LOCK_FD"}
    fd = os.open(lock, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    fd2 = os.open(other, os.O_RDONLY)

    def probe_run(env, fds=()):
        r = subprocess.run(PY + [probe, HERE, lock], env=env, pass_fds=fds, capture_output=True, text=True, timeout=60)
        return (r.stdout.strip() or r.stderr.strip()[-200:])

    r1 = probe_run(dict(env_n, MMS_BOX_LOCK_FD=str(fd)), (fd,))
    r2 = probe_run(env_n)
    r3 = probe_run(dict(env_n, MMS_BOX_LOCK_FD=str(fd2)), (fd2,))
    os.close(fd)
    os.close(fd2)
    r4 = probe_run(env_n)
    ok = r1.startswith("HELD held since") and r2.startswith("REFUSED the box lock is held") \
        and r3.startswith("REFUSED the descriptor handed over") and r4.startswith("HELD taken")
    case("D17", ok, f"handed: {r1[:40]}; fresh beside it: {r2[:40]}; another file: {r3[:45]}; after: {r4[:20]}")

    s3 = os.path.join(scratch, "toy3", "src", "sched", "a1c1-S1.json")
    det = "no toy3 schedule (M8)"
    ok = False
    if os.path.exists(s3):
        sc = C.load(s3)
        rc, out, log, q, calls = dry(scratch, "D18", "a1c1", "S1", sched=s3)
        qq = q.get("queue", [])
        bad = [x.get("arm") for x in qq if not x.get("ran") or (x.get("form") != "null" and (not x.get("rcs") or any(
            r_ != 0 for r_ in x["rcs"]) or any(c not in ("exact", "approx") for c in x.get("checks") or [None])))]
        named = {x["name"]: sum(1 for c in calls if f"src/tiles/{x['type']}/{x['name']}.bin" in c) for x in TOY3_TILES}
        ok = rc == 0 and len(qq) == len(sc["runs"]) and not bad and all(v > 0 for v in named.values()) \
            and os.path.exists(os.path.join(out, "MANIFEST.sha256"))
        det = f"rc {rc}; runs ran {sum(1 for x in qq if x.get('ran'))} of {len(sc['runs'])}; not clean {bad[:3]}; host calls a tile {named}"
    case("D18", ok, det)

    s4 = os.path.join(scratch, "toy4", "src", "sched", "a1c1-S1.json")
    det = "no toy4 schedule (W1)"
    ok = False
    if os.path.exists(s4):
        sc = C.load(s4)
        rc, out, log, q, calls = dry(scratch, "D19", "a1c1", "S1", sched=s4)
        qq = q.get("queue", [])
        bad = [x.get("arm") for x in qq if not x.get("ran") or (x.get("form") != "null" and (not x.get("rcs") or any(
            r_ != 0 for r_ in x["rcs"]) or any(c not in ("exact", "approx") for c in x.get("checks") or [None])))]
        named = {x["name"]: sum(1 for c in calls if f"src/tiles/{x['type']}/{x['name']}.bin" in c) for x in TOY4_TILES}
        ok = rc == 0 and len(qq) == len(sc["runs"]) and not bad and all(v > 0 for v in named.values()) \
            and os.path.exists(os.path.join(out, "MANIFEST.sha256"))
        det = f"rc {rc}; runs ran {sum(1 for x in qq if x.get('ran'))} of {len(sc['runs'])}; not clean {bad[:3]}; host calls a tile {named}"
    case("D19", ok, det)

    # D20: the doubles through W2's toy (card 1 and card 0, their S1): every run clean, each block arm's values in the host's
    # calls, and the reducer: ops a minion a pass by the host's grammar on every launch, cycles an op at the toy's law
    dets, oks = [], []
    for card in ("a1c1", "a1c0"):
        s5 = os.path.join(scratch, "toy5", "src", "sched", f"{card}-S1.json")
        if not os.path.exists(s5):
            dets.append(f"{card}: no toy5 schedule (W2)")
            oks.append(False)
            continue
        sc = C.load(s5)
        rc, out, log, q, calls = dry(scratch, f"D20-{card}", card, "S1", sched=s5)
        qq = q.get("queue", [])
        bad = [x.get("arm") for x in qq if not x.get("ran") or (x.get("form") != "null" and (not x.get("rcs") or any(
            r_ != 0 for r_ in x["rcs"]) or any(c not in ("exact", "approx") for c in x.get("checks") or [None])))]
        blk = sorted({r_["values"] for r_ in sc["runs"] if r_["form"] != "null" and C.arm_of(r_["values"])["family"] != "gemmL"})
        named = {v: sum(1 for c in calls if f"--values {v} " in c) for v in blk}
        rrc, d, err = reduce(scratch, out, f"D20-{card}")
        red_bad = []
        n_blk = 0
        for x in d.get("runs", []):
            g = C.arm_of(x.get("values") or "")
            if not g or x.get("form") == "null":
                continue
            if g["family"] == "gemmL":
                if any(k in x for k in ("arm_token", "ops_pass", "macs_minion_pass", "ops_pass_ok")):
                    red_bad.append(f"{x['arm']}: block keys on a gemmL run")
                continue
            n_blk += 1
            v = x.get("views", {}).get("band600" if card == "a1c1" else "burst") or {}
            want_c = law(x["values"], x["type"])
            if not x.get("ops_pass_ok") or x.get("ops_pass") != g["ops_pass"] or \
                    x.get("macs_minion_pass") != g["ops_pass"] * {"fp32": 4096, "fp16": 8192, "int8": 16384}[x["type"]]:
                red_bad.append(f"{x['arm']}: ops {x.get('ops_pass')} ok {x.get('ops_pass_ok')}")
            elif card == "a1c1" and not (v.get("cyc_op_max") and abs(v["cyc_op_max"] / want_c - 1) < 0.01):
                red_bad.append(f"{x['arm']}: cycles an op {v.get('cyc_op_max')} (law {want_c})")
        oks.append(rc == 0 and len(qq) == len(sc["runs"]) and not bad and blk and all(n_ > 0 for n_ in named.values())
                   and os.path.exists(os.path.join(out, "MANIFEST.sha256")) and rrc == 0 and n_blk > 0 and not red_bad)
        dets.append(f"{card}: rc {rc}; runs ran {sum(1 for x in qq if x.get('ran'))} of {len(sc['runs'])}; not clean {bad[:3]}; "
                    f"block values in the host's calls {sum(1 for n_ in named.values() if n_)} of {len(blk)}; reduced rc {rrc}, "
                    f"block runs {n_blk}, off {red_bad[:3]}")
    case("D20", all(oks) and len(oks) == 2, "; ".join(dets))

    n = sum(res)
    print(f"SELFTEST-MMS {n} of {len(res)} PASS")
    return 0 if n == len(res) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
