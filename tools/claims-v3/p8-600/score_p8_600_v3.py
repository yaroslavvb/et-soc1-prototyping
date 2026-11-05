#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q142(v2) fix pass, Thu 5 Nov 2026: score_p8_600_v3.py, P8-KA pooled v3, beside the committed P8 scorer at 600 MHz (score_p8_600.py,
lab a518aa11, sha256 cd5b6024..., which stays as committed and does all the scoring) and its v2 (score_p8_600_v2.py, lab 86d10a75,
sha256 1c044146..., which stays as committed). It supersedes v2's ka-pooled only, as dated note 2 beside each registration registers it
(tools/claims-v3/e171/E171.md.dated-note-2.md and tools/claims-v3/e172/E172.md.dated-note-2.md, committed before this file and before any
data). v2's scale-c is unchanged and stays the card day's (step 22 v3 calls it from v2). v3 imports v2's helpers only after v2's file has
been checked against its own list (SHA256SUMS-v2), as v2 checks the committed scorer against SHA256SUMS.

Why v3 (the first verifier of v2, verify-q142v2-code, Thu 5 Nov 2026, about 06:58-07:40 PST, "holds with fixes"):
  - its fault 1: v2's check (6) counted the rows a scored session holds, and the committed scorer writes no rows for a session that kept
    fewer than 2 passes, so v2 refused (exit 6) a genuine scored pair where E171.md and E172.md read "Fewer than 2 kept passes: every rule
    NOT SCORED"; step 22 v2 then stopped with 16 and a message that named a wrong pair;
  - its fault 2: v2's checks are by labels; E171's measurements laid out as E172's raw copy and scored --run E172 passed every v2 check
    (PASS, n 4: one session counted twice).

  ka-pooled  python3 -B score_p8_600_v3.py ka-pooled <E171 scored.json> <E172 scored.json>
                 [--scale-c <E171 scale-c.json> <E172 scale-c.json>] [--json <out>]

  It refuses, with exit 6 and nothing written, unless every one of these holds:
  (1)-(5) v2's checks, unchanged: the first file is run E171 on aifoundry3 and the second run E172 on aifoundry1c1; each names its card's
      frozen predictions file with the freeze's sha256; each was scored by the committed scorer, whose file still has its committed
      sha256; each passed the C gate (c_sessions.ok); the two are different files with different contents;
  (6) v3: each file is its own card's. Either its rows are (v2's check: every row's a-priori D equals its rate times that card's frozen
      per-op coefficient within 1e-9 W, and both check anchors have a row); or it is the committed scorer's own NOT SCORED session: its
      primary carries the scorer's mark "<k> kept passes, fewer than 2", with k the length of its kept_passes and k < 2, and holds no rows,
      no rule but P8-KC, and no verdict but NOT SCORED (score_p8_600.py score_reduction and score_session). A file with that mark and rows,
      a mark whose count is not its kept passes, a verdict other than NOT SCORED beside the mark, or no rows and no mark is refused;
  (7) v3, new: the two files are not one session's measurements under two names. Among the pool-8 tiles both files measured with a
      non-zero D (D_w, the mean over the kept passes), it refuses when at least 3 carry the same D to the bit and they are at least half of
      them. Two genuine sessions share none: E163's and E164's committed reductions share 65 tiles with a non-zero D and 0 bit-identical
      ones; only the zeros items, exactly 0 W by the footing, coincide (the self-test, W6).
  Then the committed ka_pooled over the two files, unchanged. A session with fewer than 2 kept passes holds no P8-KA block, so it adds no
  check anchor and the pooled reading is NOT SCORED ("<n> check anchors, fewer than 4"), as registered. With --scale-c (each the
  scale-c.json v2 wrote for that scored.json), v2's c_clean_pooled reading is reported beside, unchanged, never the verdict.

What v3 cannot tell (dated note 2): a copy whose measured numbers differ from the original's, for example one session's raw copy
re-reduced with the other card's footing, or values altered by hand. The runbook's fixed routes (E171 copied from aifoundry3's tree, E172
from aifoundry1's, each into its own raw directory) are what keep the pair right; checks (1)-(7) refuse the slips a hand call or a copied
file can make.

Exit codes: 0 written; 6 an identity check failed; 9 a predictions or intervals file is not the freeze's (the committed load_pred), or the
committed scorer or v2 is not its committed file; 1 the predictor's own stop when one of its hash lists differs ("POOL8 STOPPED" /
"POOL8-A2 STOPPED", raised as SystemExit); 2 a usage error. Nothing is written on any refusal. Python 3.9 with numpy (the predictor's chain
needs it): the Intel's /usr/bin/python3. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import score_p8_600 as SC  # noqa: E402  (the committed scorer, a518aa11, unchanged; importing it runs nothing)
import score_p8_600_v2 as V2  # noqa: E402  (v2, 86d10a75, unchanged; importing it runs nothing; its sha256 is checked before use)

EXIT_ID = V2.EXIT_ID                     # 6
V2_REL = "tools/claims-v3/p8-600/score_p8_600_v2.py"
MARK_TAIL = " kept passes, fewer than 2"  # score_p8_600.py score_reduction: out["NOT SCORED"] = f"{len(...)} kept passes, fewer than 2"
SAME_D_MIN = 3                           # check (7): at least 3 bit-identical non-zero D, and at least half of the shared ones
sha = SC.sha


def committed_v2_sha(listpath=None):
    """v2's sha256 from its own list (p8-600/SHA256SUMS-v2, 86d10a75); the file the import loaded must still have it (exit 9 if not)"""
    listpath = listpath or os.path.join(HERE, "SHA256SUMS-v2")
    want = None
    for line in open(listpath):
        parts = line.split(None, 1)
        if len(parts) == 2 and parts[1].strip().lstrip("*") == V2_REL:
            want = parts[0]
    have = sha(os.path.abspath(V2.__file__))
    if not want or have != want:
        raise SC.Refuse(SC.EXIT_FROZEN, f"{V2_REL}: sha256 {have[:12]} is not its committed {str(want)[:12]} (p8-600/SHA256SUMS-v2)")
    return want


def not_scored_session(o):
    """(True, the mark) when o is the committed scorer's NOT SCORED session (fewer than 2 kept passes); (False, why) when it carries the
    mark in a form the committed scorer never writes; (None, None) when it carries no mark"""
    prim = o.get("primary") or {}
    if "NOT SCORED" not in prim:
        return None, None
    mark, kept, bad = prim.get("NOT SCORED"), prim.get("kept_passes"), []
    if not isinstance(kept, list):
        bad.append("no kept_passes list")
    else:
        if len(kept) >= 2:
            bad.append(f"{len(kept)} kept passes, not fewer than 2")
        if mark != f"{len(kept)}{MARK_TAIL}":
            bad.append(f"the mark {str(mark)[:60]!r} is not the committed scorer's for {len(kept)} kept passes")
    if prim.get("rows"):
        bad.append(f"{len(prim['rows'])} rows beside the mark")
    extra = sorted(r for r in (prim.get("rules") or {}) if r != "P8-KC")
    if extra:
        bad.append(f"rules beside the mark ({', '.join(extra[:3])})")
    top = o.get("verdicts") or {}
    if sorted(top) != sorted(SC.RULES):
        bad.append("its verdicts are not the 19 rules'")
    other = sorted(r for r, v in list(top.items()) + list((prim.get("verdicts") or {}).items()) if v != "NOT SCORED")
    if other:
        bad.append(f"a verdict other than NOT SCORED beside the mark ({', '.join(sorted(set(other))[:3])})")
    return (False, "; ".join(bad)) if bad else (True, mark)


def same_d(objs):
    """check (7)'s reading: (the shared tiles with a non-zero D in either file, those whose D is the same to the bit)"""
    ra = ((objs[0].get("primary") or {}).get("rows") or {})
    rb = ((objs[1].get("primary") or {}).get("rows") or {})
    num = lambda r: isinstance(r.get("D_w"), (int, float)) and not isinstance(r.get("D_w"), bool)  # noqa: E731
    shared = [t for t in sorted(set(ra) & set(rb)) if num(ra[t]) and num(rb[t]) and (float(ra[t]["D_w"]) != 0.0 or float(rb[t]["D_w"]) != 0.0)]
    same = [t for t in shared if float(ra[t]["D_w"]) == float(rb[t]["D_w"])]
    return shared, same


def one_session_twice(shared, same):
    return len(same) >= SAME_D_MIN and 2 * len(same) >= len(shared)


# ------------------------------------------------------------------------------------------------- the pooled read, v3
def pair_check(paths):
    """checks (1)-(7), or a refusal (exit 6) naming every check that failed"""
    if len(paths) != 2:
        raise SC.Refuse(EXIT_ID, "ka-pooled takes two files: <E171 scored.json> <E172 scored.json>")
    committed_v2_sha()
    scorer = V2.committed_scorer_sha()
    fz = SC.freeze_sums()
    bad, objs, info = [], [], []
    for q, (run, card) in zip(paths, V2.PAIR):
        o = V2.load_json(q, "scored.json")
        objs.append(o)
        tag = f"{V2.rel(q)} (the {run} argument)"
        rec = {"argument": run, "file": V2.rel(q), "sha256": sha(q), "run": o.get("run"), "card": o.get("card")}
        if o.get("run") != run or o.get("card") != card:
            bad.append(f"{tag}: run {o.get('run')} on {o.get('card')}, not {run} on {card} (the registered order: <E171 scored.json> "
                       f"<E172 scored.json>)")
        relp = f"tools/claims-v3/kinds/blind8/predictions-pool8-{card}.json"
        if o.get("predictions") != relp:
            bad.append(f"{tag}: predictions {o.get('predictions')}, not {relp}")
        if o.get("predictions_sha256") != fz.get(relp):
            bad.append(f"{tag}: predictions_sha256 {str(o.get('predictions_sha256'))[:12]} is not the freeze's {str(fz.get(relp))[:12]}")
        if o.get("scorer_sha256") != scorer:
            bad.append(f"{tag}: scorer_sha256 {str(o.get('scorer_sha256'))[:12]} is not the committed scorer's {scorer[:12]}")
        if not (o.get("c_sessions") or {}).get("ok"):
            bad.append(f"{tag}: not scored through the C gate (no c_sessions.ok)")
        if not isinstance(o.get("primary"), dict) or "scale" not in o["primary"]:
            bad.append(f"{tag}: no primary block")
        else:
            _, pred = SC.load_pred(card)          # exit 9 if the frozen file is not the freeze's
            ns, why = not_scored_session(o)
            if ns is True:
                rec["rows_checked"] = 0
                rec["not_scored"] = why           # the committed scorer's own mark: no rows to check, NOT SCORED as registered
            elif ns is False:
                bad.append(f"{tag}: a NOT SCORED mark in a form the committed scorer never writes ({why})")
            else:
                n, rb = V2.card_rows(o, pred)
                rec["rows_checked"] = n
                if n == 0 or rb:
                    bad.append(f"{tag}: its rows are not {card}'s and it is not the committed scorer's NOT SCORED session ({n} checked; "
                               + "; ".join(rb[:3]) + ")")
        info.append(rec)
    if os.path.realpath(paths[0]) == os.path.realpath(paths[1]):
        bad.append("the two arguments are the same file")
    elif info[0]["sha256"] == info[1]["sha256"]:
        bad.append("the two files have the same contents")
    shared, same = same_d(objs)
    dchk = {"shared_nonzero_D": len(shared), "bit_identical_D": len(same), "examples": same[:3], "refused_when": f"at least {SAME_D_MIN} "
            "bit-identical and at least half of the shared"}
    if one_session_twice(shared, same):
        bad.append(f"the two files carry the same measured D on {len(same)} of the {len(shared)} pool-8 tiles both measured with a non-zero D "
                   f"(e.g. {', '.join(same[:2])}): one session's measurements under two names")
    if bad:
        raise SC.Refuse(EXIT_ID, "ka-pooled v3 reads only E171's and E172's scored sessions as registered (dated note 2): " + "; ".join(bad))
    return objs, info, dchk


def ka_pooled_v3(paths, scale_c=None):
    objs, info, dchk = pair_check(paths)
    out = dict(SC.ka_pooled(list(paths)))           # the committed reading, unchanged
    out["identity"] = {"pair": info, "measured_D": dchk, "scorer_sha256": V2.committed_scorer_sha(), "v2_sha256": committed_v2_sha(),
                       "v3_sha256": sha(os.path.abspath(__file__)),
                       "checks": ["run and card in the registered order", "the freeze's predictions file and sha256", "the committed scorer",
                                  "C-gated", "two different files", "each card's own rows, or the committed scorer's NOT SCORED session",
                                  "not one session's measured D under two names"]}
    if scale_c:
        out["beside"] = {"c_clean_scale": V2.c_clean_pooled(objs, info, scale_c)}
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    k = sub.add_parser("ka-pooled")
    k.add_argument("scored", nargs=2)
    k.add_argument("--scale-c", nargs=2)
    k.add_argument("--json")
    a = ap.parse_args(argv)
    try:
        o = ka_pooled_v3([os.path.abspath(x) for x in a.scored], [os.path.abspath(x) for x in a.scale_c] if a.scale_c else None)
    except SC.Refuse as e:
        print(f"REFUSED (exit {e.code}): {e}")
        return e.code
    if a.json:
        open(a.json, "w").write(json.dumps(V2.scrub(o), indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps({k_: o[k_] for k_ in ("verdict", "n") if k_ in o}))
    if "beside" in o:
        b = o["beside"]["c_clean_scale"]
        print(json.dumps({"beside_c_clean_scale": {k_: b[k_] for k_ in ("verdict", "n") if k_ in b}}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
