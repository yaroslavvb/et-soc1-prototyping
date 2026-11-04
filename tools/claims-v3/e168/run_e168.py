#!/usr/bin/env python3
"""E168 (Q141(o)): the session runner. It is E159's run_e159.py with E168's names and ONE ADDITION: E119's run_e119.py, imported and run
unchanged (E105's run_e105.py with its admission rule, E101 session 2's run_e101s.py, E80's run_kspeed.py, E64's run_hpl.py; E111's
idle-login rule; the residency query E119 sends, which this ettelem build refuses at its argument check before it opens the device),
after E146's preflight, unchanged, and E159's two refusals, unchanged:

  PREFLIGHT (E146's, imported): before anything opens the card, the three device programs must be byte-identical to E136's registered
  build (the heater build/e136/host/sparsity_host and its kernel build/e136/kernel/sparsity.elf, rgm136, built on aifoundry2 at 15:37
  PST on 2 Nov 2026; E168's three shapes are its arguments, gemmL<MB>x<NB>x<KB>; the sampler build/ettelem-hpl/ettelem). The README
  classifies every device-management command they send; a different binary could send something else, so a mismatch refuses the
  session (exit 2) before the card lock is taken. Under --dry it is skipped.
  THE STOPS (Q139's rule for aifoundry2, kept in Q141: "every registered board stop is at most 85 W on live samples"): a protocol whose
  safety block lacks abs_stop_c, board_cap_w or cap_consecutive, whose board_cap_w is above 85 W, or whose admission limit
  limit_p800_w is above 82 W ("no tile, shape or hold whose predicted peak board power exceeds 82 W runs as designed") is refused
  (exit 2), under --dry too.

  THE ADDITION, POOL 6's W8A8 TILE. Q140(q)'s frozen hold 8, S2-int8-real_smol_w8a8_down-warm55, runs rgm136's generator `tiles` on
  tools/claims-v3/kinds/blind6/tiles/int8/int8.real_smol_w8a8_down.bin. E101's run_e101s.verify_tiles checks every file a GEMM value
  names against its own registry (E101's items and real set) and refuses the whole session at load, --dry included, for a file it does
  not hold: "... is not a registered tile". Pool 6's tiles are not in it. So, as E160's run_e160.py does for pool 6's `file:` values, a
  GEMM value whose files lie under tools/claims-v3/kinds/blind6/tiles/ is checked here instead: pool 6's manifest blind6.json and its
  MANIFEST hash as committed in Q139(x)'s d98d2e34 (E160's pins, e160_common.FROZEN), the file is a tile of the manifest of the run's
  own type, and it is 2,048 B with the manifest's sha256 of the whole, of A (the first 1,024 B) and of B (the last 1,024 B). Any
  mismatch refuses the session (exit 2, SystemExit as the imported check's) before the card lock is taken. Every other value goes
  through the imported check unchanged. Nothing about the hold changes: the value string and the bytes are the frozen design's.

Everything that touches the card -- the card lock held for the session, the other-user checks before every launch process, `timeout 10`
on every launch and config read, the sampler WITHOUT --reset-ms, the trace ring and `ettelem config` after every run, the safety stops
under the keys run_hpl.py's watcher reads, the end of the session unless the TDP and the threshold read back 65, and the admission rule
-- is the imported code. Nothing is set on the card.

The design and the predictions are Q140(q)'s, frozen at e39d06da (docs/reports/data/2026-11-04-q140q-gemm-g4-stride/predictions-e168.json),
with amendment A2 (226249e1, tools/claims-v3/e168/predictions-e168-a2.json); the protocol is written from them by
make_protocol_e168.py. The runner records the protocol's sha256, the frozen files' registered and present sha256 in e168.json.

    python3 run_e168.py --protocol protocol.json --out <RUNDIR> [--dry] [--only BLOCK ...] [--max-card-min N] [--list]
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "e146"))
sys.path.insert(0, os.path.join(HERE, "..", "e160"))
import run_e146 as R146  # noqa: E402  (E146's runner: its preflight, E136's registered sha256, and run_e119 as R146.R119)
import e160_common as C6  # noqa: E402  (pool 6's paths, pins and tile check; standard library only)

MAX_BOARD_STOP_W = 85.0
MAX_LIMIT_W = 82.0
PREDICTIONS = "docs/reports/data/2026-11-04-q140q-gemm-g4-stride/predictions-e168.json"
PREDICTIONS_SHA256 = "430f4afa266a30c35f3e4da44ebef9fbf1d1186c00ceb5e2e8ae312c8c168583"   # frozen-sha256-e168.json at e39d06da
AMENDMENT = "tools/claims-v3/e168/predictions-e168-a2.json"
AMENDMENT_SHA256 = "2afb290f62f7cc722c1f58837c18ab545f914863107a162653c38459c35fafe6"     # as committed in 226249e1
POOL6_TILES = f"{C6.POOL_REL}/tiles/"
POOL6_PINS = {C6.MAN_REL: C6.FROZEN[C6.MAN_REL], C6.MANIFEST_REL: C6.FROZEN[C6.MANIFEST_REL]}   # Q139(x)'s d98d2e34

K = R146.R119.RE.RS.K          # run_kspeed, whose main() calls verify_tiles (run_e101s.py's, which wraps run_kspeed.py's)
_prev_verify = K.verify_tiles


def stops_ok(proto):
    """None if the protocol's stops and admission limit are inside the brief's, else why not (selftest_e168.py runs it)"""
    sf = proto.get("safety", {})
    bad = [f"protocol safety lacks {k}" for k in ("abs_stop_c", "board_cap_w", "cap_consecutive") if k not in sf]
    if "board_cap_w" in sf and float(sf["board_cap_w"]) > MAX_BOARD_STOP_W:
        bad.append(f"board_cap_w {sf['board_cap_w']} W is above {MAX_BOARD_STOP_W:g} W")
    lim = proto.get("limit_p800_w")
    if lim is None or float(lim) > MAX_LIMIT_W:
        bad.append(f"limit_p800_w {lim} is missing or above {MAX_LIMIT_W:g} W")
    return "; ".join(bad) if bad else None


def gemm_files(values):
    """the files a GEMM value names (its third field, comma-separated), or [] for any other value"""
    v = str(values)
    if not v.startswith("gemm") or v.count(":") < 2:
        return []
    return v.split(":", 2)[2].split(",")


def is_pool6_value(values):
    fs = gemm_files(values)
    return bool(fs) and all(f.startswith(POOL6_TILES) and f.endswith(".bin") and ".." not in f for f in fs)


def pool6_why(root, runs):
    """[] if every pool-6 GEMM value's files are the manifest's tiles of the run's own type, else what is wrong (the addition)"""
    bad = []
    for rel, want in POOL6_PINS.items():
        p = os.path.join(root, rel)
        got = C6.sha256_file(p) if os.path.isfile(p) else None
        if got != want:
            bad.append(f"{rel}: sha256 {got}, frozen {want}")
    if bad:
        return bad
    by_file = {f"{C6.POOL_REL}/{t['file']}": t for t in C6.manifest(root).values()}
    for r in runs:
        for rel in gemm_files(r.values):
            t = by_file.get(rel)
            if t is None:
                bad.append(f"{r.values}: {rel} is not a tile of {C6.MAN_REL}")
                continue
            if t["type"] != r.type:
                bad.append(f"{r.values}: a {t['type']} tile, run {r.name} is {r.type}")
            why = C6.check_tile(root, t)
            if why:
                bad.append(why)
    return bad


def verify_tiles(root, runs):
    """the imported verify_tiles for every other value, plus every pool-6 GEMM value against pool 6's manifest (the addition)"""
    pool = [r for r in runs if is_pool6_value(r.values)]
    out, kinds_sha, kinds_rev = _prev_verify(root, [r for r in runs if not is_pool6_value(r.values)])
    if not pool:
        return out, kinds_sha, kinds_rev
    bad = pool6_why(root, pool)
    if bad:
        raise SystemExit("refused: " + "; ".join(bad))
    man = {f"{C6.POOL_REL}/{t['file']}": t for t in C6.manifest(root).values()}
    for r in pool:
        files = gemm_files(r.values)
        out[str(r.values)] = {"type": r.type, "kind": r.label, "values": str(r.values), "pool": "blind6",
                              "files": {f: {"bytes": 2048, "sha256": man[f]["sha256"]["whole"], "sha256_a": man[f]["sha256"]["a"],
                                            "sha256_b": man[f]["sha256"]["b"], "name": man[f]["name"]} for f in files}}
    return out, kinds_sha, kinds_rev


K.verify_tiles = verify_tiles


def main():
    pr = sys.argv[sys.argv.index("--protocol") + 1]
    proto = json.load(open(pr))
    dry = "--dry" in sys.argv
    root = ROOT
    if "--root" in sys.argv:
        root = os.path.abspath(sys.argv[sys.argv.index("--root") + 1])
    if "--list" not in sys.argv:
        why = stops_ok(proto)
        if why is not None:
            print(f"refused: {why}", file=sys.stderr)
            return 2
    got = {}
    if not dry and "--list" not in sys.argv:
        why = R146.preflight(proto, root)
        if why is not None:
            print(f"refused: {why}", file=sys.stderr)
            return 2
        got = dict(R146.E136_SHA256)
    if "--out" in sys.argv and "--list" not in sys.argv:
        rd = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
        os.makedirs(rd, exist_ok=True)
        if not os.path.exists(os.path.join(rd, "e168.json")):
            pp, pa = os.path.join(root, PREDICTIONS), os.path.join(root, AMENDMENT)
            json.dump({"experiment": "E168", "request": "Q141", "wrapper": "tools/claims-v3/e168/run_e168.py", "wrapper_sha256": R146.sha256(__file__),
                       "run_e146_sha256": R146.sha256(R146.__file__), "run_e119_sha256": R146.sha256(R146.R119.__file__),
                       "e160_common_sha256": R146.sha256(C6.__file__), "protocol": os.path.basename(pr), "protocol_sha256": R146.sha256(pr),
                       "predictions": PREDICTIONS, "predictions_sha256_registered": PREDICTIONS_SHA256,
                       "predictions_sha256_here": R146.sha256(pp) if os.path.isfile(pp) else None,
                       "amendment": AMENDMENT, "amendment_sha256_registered": AMENDMENT_SHA256,
                       "amendment_sha256_here": R146.sha256(pa) if os.path.isfile(pa) else None, "binaries_checked": got, "dry": dry,
                       "safety": proto.get("safety"), "limit_p800_w": proto.get("limit_p800_w"), "peak_lock_w": proto.get("peak_lock_w"),
                       "t_ms": int(time.time() * 1000), "zone": time.strftime("%Z"), "argv": sys.argv}, open(os.path.join(rd, "e168.json"), "w"), indent=1)
    return R146.R119.main()


if __name__ == "__main__":
    sys.exit(main())
