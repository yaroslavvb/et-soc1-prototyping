"""E212 (reg-e212, Q208): the lab's desk re-make of what the model session's plan made, without the plan (reads only; it imports
the proposal's own src/make_schedule2.py and src/tiles_gen.py and writes nothing but its standard output).

The plan (plan.json, "in the request's folder, beside src/") did not reach the lab, so make_schedule2.py --check and
tiles_gen.py --check cannot run here (both print FAIL with no plan: desk/desk-checks-e212.txt parts 3 and 6). What the lab can
re-make from the committed copy alone, through the generator's own functions:
  A. every plan tile's record in arms.json (sha256, toggle figures, element stats, the check of C at every K an arm runs it at)
     from the tile file's bytes, by tiles_gen.read_tile with the lab's randn tile as the toggle reference;
  B. every arm record in arms.json from its plan fields (id, mb, nb, kb, type, kind, shires, form, families, priority), by
     make_schedule2.arm_rec, and the anchor by anchor_rec; then arms.json itself, byte for byte, as make() writes it;
  C. each of the ten schedules, byte for byte, by make_schedule2.schedule from (i) the arm records, (ii) the session's blocks as
     the schedule records them (each block's name and arm set, in the order the runs show them), trying the plan's two free
     choices a schedule does not record directly: "reverse" (no / yes: then the plan's order is the runs' order reversed) and
     each block's "nulls" (unset, "through" or "none"); it prints the first choice that re-makes the file exactly.
What this cannot check: the plan's own words (its block lists, its tile patterns, its notes); the tile files are checked by
reading them back, not by re-drawing them from their patterns.
    /usr/bin/python3 -I -B remake_e212.py <the proposal's src dir>
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
import tiles_gen as TG  # noqa: E402

A = json.load(open(os.path.join(src, "arms.json")))
arms_bytes = open(os.path.join(src, "arms.json"), "rb").read()
print("# E212: the lab's re-make of arms.json and the ten schedules without the plan (make_schedule2.py and tiles_gen.py, "
      "the proposal's own functions)")
print("arms.json: kit %s, seed %s, %d arms (with the anchor), %d tiles, sessions %s" % (
    A["kit"], A["seed"], len(A["arms"]), len(A["tiles"]), json.dumps(A["sessions"], sort_keys=True)))
bad = 0

# A. the tile records
ref = {t: TG.rnd_ref(t, root) for t in M.TYPES}
print("\n## A. the plan tiles' records from their bytes (toggle reference: the lab's randn tile, int8 full.bin)")
print("reference toggles: " + ", ".join("%s %.6f" % (t, ref[t]) for t in M.TYPES))
remade_tiles = {}
for name, rec in sorted(A["tiles"].items()):
    data = open(os.path.join(root, rec["file"]), "rb").read()
    ks = sorted({M.K_PER_KB[a["type"]] * a["kb"] for a in A["arms"] if a["kind"] == name})
    r = TG.read_tile(data, rec["type"], ks, rec["gen"], False, ref[rec["type"]])
    r.update(name=name, file=rec["file"], est_as=rec["est_as"])
    sub = {k: v for k, v in r.items() if k in ("name", "type", "gen", "file", "sha256", "est_as", "toggle", "stats", "checks")}
    remade_tiles[name] = sub
    same = sub == rec
    bad += not same
    print("%s tile %-10s %s gen %-8s K %s: %s; toggle a %.4f b %.4f ratio %s; %s" % (
        "EQUAL  " if same else "DIFFERS", name, rec["type"], rec["gen"], ",".join(map(str, ks)),
        ", ".join("%s %s" % (k, v.get("result", v.get("bad"))) for k, v in sorted(r["checks"].items(), key=lambda kv: int(kv[0]))),
        r["toggle"]["a"], r["toggle"]["b"], r["toggle"].get("ratio"), "ok" if r["ok"] else "NOT OK: " + "; ".join(r["why"])))
    if not same:
        for k in sorted(set(sub) | set(rec)):
            if sub.get(k) != rec.get(k):
                print("    field %s: re-made %s / file %s" % (k, json.dumps(sub.get(k))[:200], json.dumps(rec.get(k))[:200]))


class _Plan:
    """The generator's Plan as make_schedule2 uses it after reading a plan: seed, tiles {name: {data, rec, spec}}, ref."""


P = _Plan()
P.seed = A["seed"]
P.tiles = {}
for name, rec in A["tiles"].items():
    P.tiles[name] = {"data": open(os.path.join(root, rec["file"]), "rb").read(), "rec": dict(rec, ok=True),
                     "spec": {"name": name, "type": rec["type"], "gen": rec["gen"], "est_as": rec["est_as"]}}
P.ref = ref

# B. the arm records and arms.json
print("\n## B. the arm records from their plan fields (make_schedule2.arm_rec), the anchor (anchor_rec), arms.json byte for byte")
anchor = M.anchor_rec()
by_id, nb_ok = {}, 0
for a in A["arms"]:
    if a["id"] == anchor["id"]:
        same = a == anchor
        print("anchor %s: %s" % (a["id"], "EQUAL" if same else "DIFFERS"))
        bad += not same
        continue
    plan_arm = {k: a[k] for k in ("id", "mb", "nb", "kb", "type", "kind", "shires", "form", "families", "priority")}
    r = M.arm_rec(P, plan_arm)
    by_id[r["id"]] = r
    if r == a:
        nb_ok += 1
    else:
        bad += 1
        print("DIFFERS arm %s: %s" % (a["id"], {k: (r.get(k), a.get(k)) for k in set(r) | set(a) if r.get(k) != a.get(k)}))
print("arm records equal: %d of %d" % (nb_ok, len(A["arms"]) - 1))
order_ok = [a["id"] for a in A["arms"]] == sorted(a["id"] for a in A["arms"])
print("arms.json's arms in id order (as make() sorts them): %s" % order_ok)
bad += not order_ok
remade = {"kit": M.KIT, "seed": P.seed, "arms": sorted(list(by_id.values()) + [anchor], key=lambda a: a["id"]),
          "tiles": remade_tiles, "sessions": A["sessions"]}
same = M.dump(remade).encode() == arms_bytes
print("arms.json re-made byte for byte: %s" % ("EQUAL" if same else "DIFFERS"))
bad += not same

# C. the schedules
print("\n## C. the ten schedules, byte for byte, from the arm records and each schedule's own blocks (make_schedule2.schedule)")
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
print("schedules re-made byte for byte: %d of %d" % (n_ok, sum(len(v) for v in A["sessions"].values())))
print("\nREMAKE %s (%d difference(s))" % ("PASS" if not bad else "FAIL", bad))
