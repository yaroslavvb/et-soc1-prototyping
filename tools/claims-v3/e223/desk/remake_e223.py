"""E223 (reg-e223, Q239): the lab's desk re-make of what the model session's plan made, without the plan (reads only; it imports
the proposal's own src/make_schedule2.py and writes nothing but its standard output).

The plan (plan.json, "in the request's folder, beside src/") did not reach the lab, so make_schedule2.py --check cannot re-make
the files here (desk/desk-checks-e223.txt part 3). What the lab can re-make from the committed copy alone, through the
generator's own functions:
  A. the plan tiles' records: this sweep has none ("this sweep designs no tiles": arms.json's "tiles" is empty and src/tiles holds
     the lab's nine kind files alone), so part A checks only that;
  B. every arm record in arms.json from its plan fields, by make_schedule2.arm_rec: a gemmL arm from (id, mb, nb, kb, type, kind,
     shires, form, families, priority), a block, stream or TenB arm (E219's; this sweep has none, nor had E221) from (id, arm, type, kind, shires,
     form, families, priority) through make_schedule2.block_rec and the host's grammar mms_common.arm_of; the anchor by anchor_rec; then
     arms.json itself, byte for byte, as make() writes it;
  C. each of the nine schedules, byte for byte, by make_schedule2.schedule from (i) the arm records, (ii) the session's blocks as
     the schedule records them (each block's name and arm set, in the order the runs show them), trying the plan's two free
     choices a schedule does not record directly: "reverse" (no / yes: then the plan's order is the runs' order reversed) and
     each block's "nulls" (unset, "through" or "none"); it prints the first choice that re-makes the file exactly.
What this cannot check: the plan's own words (its block lists, its notes, its families' meanings).
    /usr/bin/python3 -I -B remake_e223.py <the proposal's src dir>
(E221's remake_e221.py, itself E219's, E217's, E214's and E212's, with this sweep's names; this sweep's arms are gemmL arms only;
no tile is read: there is no plan tile.)
SPDX-License-Identifier: Apache-2.0
"""
import itertools
import json
import os
import sys

src = os.path.abspath(sys.argv[1])
root = os.path.dirname(src)
sys.path.insert(0, src)
import make_schedule2 as M  # noqa: E402

A = json.load(open(os.path.join(src, "arms.json")))
arms_bytes = open(os.path.join(src, "arms.json"), "rb").read()
print("# E223: the lab's re-make of arms.json and the nine schedules without the plan (make_schedule2.py, the proposal's own "
      "functions, with the host's grammar mms_common.arm_of)")
print("arms.json: kit %s, seed %s, %d arms (with the anchor), %d tiles, sessions %s" % (
    A["kit"], A["seed"], len(A["arms"]), len(A["tiles"]), json.dumps(A["sessions"], sort_keys=True)))
bad = 0

# A. no plan tiles
tile_files = sorted(os.path.relpath(os.path.join(dp, f), src) for dp, dn, fs in os.walk(os.path.join(src, "tiles")) for f in fs)
lab_nine = sorted("tiles/%s/%s.bin" % (t, n) for t in M.TYPES for n in (("full",) if t == "int8" else ("randn",)) + ("zeros", "ones"))
print("\n## A. the plan tiles: arms.json names %d; src/tiles holds %d files: %s" % (len(A["tiles"]), len(tile_files),
                                                                              "the lab's nine kinds only" if tile_files == lab_nine
                                                                              else "NOT the lab's nine alone: " + ", ".join(tile_files)))
bad += bool(A["tiles"]) or tile_files != lab_nine
kinds_used = sorted({a["kind"] for a in A["arms"]})
print("kinds the arms use: %s" % ", ".join(kinds_used))
bad += any(k not in M.KINDS for k in kinds_used)


class _Plan:
    """The generator's Plan as make_schedule2 uses it after reading a plan: seed, tiles {name: {data, rec, spec}}, ref."""


P = _Plan()
P.seed = A["seed"]
P.tiles = {}
P.ref = {}

# B. the arm records and arms.json
print("\n## B. the arm records from their plan fields (make_schedule2.arm_rec / block_rec), the anchor (anchor_rec), arms.json "
      "byte for byte")
anchor = M.anchor_rec()
by_id, nb_ok, nblk = {}, 0, 0
GEMML_FIELDS = ("id", "mb", "nb", "kb", "type", "kind", "shires", "form", "families", "priority")
BLOCK_FIELDS = ("id", "arm", "type", "kind", "shires", "form", "families", "priority")
for a in A["arms"]:
    if a["id"] == anchor["id"]:
        same = a == anchor
        print("anchor %s: %s" % (a["id"], "EQUAL" if same else "DIFFERS"))
        bad += not same
        continue
    plan_arm = {k: a[k] for k in (BLOCK_FIELDS if "arm" in a else GEMML_FIELDS)}
    nblk += "arm" in a
    try:
        r = M.arm_rec(P, plan_arm)
    except ValueError as e:
        bad += 1
        print("REFUSED arm %s: %s" % (a["id"], e))
        continue
    by_id[r["id"]] = r
    if r == a:
        nb_ok += 1
    else:
        bad += 1
        print("DIFFERS arm %s: %s" % (a["id"], {k: (r.get(k), a.get(k)) for k in set(r) | set(a) if r.get(k) != a.get(k)}))
print("arm records equal: %d of %d (%d block, stream or TenB arms, %d gemmL arms besides the anchor)" % (
    nb_ok, len(A["arms"]) - 1, nblk, len(A["arms"]) - 1 - nblk))
order_ok = [a["id"] for a in A["arms"]] == sorted(a["id"] for a in A["arms"])
print("arms.json's arms in id order (as make() sorts them): %s" % order_ok)
bad += not order_ok
remade = {"kit": M.KIT, "seed": P.seed, "arms": sorted(list(by_id.values()) + [anchor], key=lambda a: a["id"]),
          "tiles": {}, "sessions": A["sessions"]}
same = M.dump(remade).encode() == arms_bytes
print("arms.json re-made byte for byte: %s" % ("EQUAL" if same else "DIFFERS"))
bad += not same

# C. the schedules
nsched = sum(len(v) for v in A["sessions"].values())
print("\n## C. the %d schedules, byte for byte, from the arm records and each schedule's own blocks (make_schedule2.schedule)" % nsched)
n_ok = 0
for card in sorted(A["sessions"]):
    for s in A["sessions"][card]:
        p = os.path.join(src, "sched", "%s-%s.json" % (card, s))
        want = open(p).read()
        sc = json.loads(want)
        names, members = [], {}
        for r in sc["runs"]:
            if r["block"] not in names:
                names.append(r["block"])
            if r["role"] in ("arm", "time"):
                members.setdefault(r["block"], []).append(r["arm"])
        hit = None
        for rev in (False, True):
            order = names[::-1] if rev else names
            for nulls in itertools.product((None, "through", "none"), repeat=len(order)):
                blocks = []
                for nm, nu in zip(order, nulls):
                    b = {"name": nm, "arms": members.get(nm, [])}
                    if nu is not None:
                        b["nulls"] = nu
                    blocks.append(b)
                if any(not b["arms"] for b in blocks):
                    continue
                sess = {"S": s, "blocks": blocks}
                if rev:
                    sess["reverse"] = True
                try:
                    got = M.dump(M.schedule(P, card, sess, by_id, anchor))
                except ValueError as e:
                    got = "REFUSED " + str(e)
                if got == want:
                    hit = (rev, nulls)
                    break
            if hit:
                break
        if hit:
            n_ok += 1
            nl = [("%s:%s" % (nm, nu)) for nm, nu in zip(names[::-1] if hit[0] else names, hit[1]) if nu is not None]
            print("EQUAL   %s-%s: %d runs, blocks %s; reverse %s; nulls set %s; planned %s, rule %g, cap %g, line %g W, highest "
                  "estimate %s W" % (card, s, len(sc["runs"]), " ".join(names), "yes" if hit[0] else "no", " ".join(nl) or "none",
                                     sc["planned_min"], sc["timing"]["rule_min"], sc["timing"]["cap_min"], sc["line_w"],
                                     max(r["est_peak_w"] for r in sc["runs"])))
        else:
            bad += 1
            print("DIFFERS %s-%s: no choice of reverse and nulls re-makes the file" % (card, s))
print("schedules re-made byte for byte: %d of %d" % (n_ok, nsched))
print("\nREMAKE %s (%d difference(s))" % ("PASS" if not bad else "FAIL", bad))
