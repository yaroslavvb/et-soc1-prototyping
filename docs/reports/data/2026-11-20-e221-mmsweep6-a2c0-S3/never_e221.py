#!/usr/bin/env python3
"""data-e221 (Q235; data-e219's never_e219.py, Q232): the never-run labels of one E221 session's arms, RE-READ at this session's data
commit (the registration's labels, E219's form: the round's data lane re-reads them for each session against the lab's committed data
at that session's commit). LABELS ONLY, REPORTED; nothing is dropped.

It starts from the registration's own labels (tools/claims-v3/e221/desk/neverrun-e221.json: the rows for this session's card and arms,
keyed by the configuration (rgm136, the host's arm token, the format, the data, the shire mask)) and adds what was committed on that card
AFTER the registration's index was made (its desk/configs-e221.json names the committed session folders it read): every committed
session folder under the lab's docs/reports/data that holds run records (runs/*/run.json, with or without a session/ level), is on this
session's card by its folder name (the registration's folder_card rule, aifoundry2 card 0 included), and is not among the index's
folders: E221's own earlier sessions on the card and any other experiment's committed after the index, E220's among them (this
session's own folder is never read). Each device process of every run that ran is keyed by its own argv the
registration's way (the host's --values token, --type, --shires; the tile resolved by bytes against the lab's top, then against that
experiment's registered kit tools/claims-v3/e<N>/proposal/, then by that experiment's registered lists (proposal/src/SRC-SHA256SUMS,
box/SRC-SHA256SUMS-e<N>): the path's registered sha256; the data key by the lab's kinds tiles: randn over the lab's random tile is
'random', a kinds zeros or ones tile 'zeros' or 'ones', sparse50 over the lab's sparse50 tile 'sparse50', the lab's random tile held by
gen tiles 'held:<sha256>', any other tile 'tile:<sha256>').
The re-read label: REPEAT when the configuration has a committed run on the card (the registration's or a new one); SHAPE-ONLY when
only its token (shape) has; otherwise the registration's label (NEVER or NEVER-BY-INDEX) stands. Python's own modules only; reads only.

    /usr/bin/python3 -I -B never_e221.py <label> <registration's desk dir> <src dir> <lab top> --out never.json --txt never.txt
"""
import argparse
import glob
import hashlib
import json
import os
import re
import sys

CARD = {"a1c1": "aifoundry1 card 1", "a1c0": "aifoundry1 card 0", "a2c0": "aifoundry2 card 0"}
KINDS_TILES = "tools/claims-v3/kinds/tiles"


def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


class Kinds:
    def __init__(self, lab):
        self.map = {}
        for t, names in (("fp32", ("randn", "zeros", "ones", "sparse50")), ("fp16", ("randn", "zeros", "ones", "sparse50")),
                         ("int8", ("full", "zeros", "ones", "sparse50"))):
            for n in names:
                p = os.path.join(lab, KINDS_TILES, t, n + ".bin")
                if os.path.exists(p):
                    self.map[sha(p)] = {"randn": "random", "full": "random"}.get(n, n)

    def data_key(self, gen, tile_sha):
        lab = self.map.get(tile_sha)
        if gen == "randn":
            return "random" if lab == "random" else f"randn-over:{tile_sha}"
        if gen == "sparse50":
            return "sparse50" if lab == "sparse50" else f"sparse50-over:{tile_sha}"
        if gen == "tiles":
            if lab in ("zeros", "ones"):
                return lab
            if lab == "random":
                return f"held:{tile_sha}"
            return f"tile:{tile_sha}"
        return f"gen-{gen}:{tile_sha}"


def argval(argv, k):
    return argv[argv.index(k) + 1] if k in argv else None


def folder_card(name):
    """the registration's rule (tools/claims-v3/e221/desk/neverrun_e221.py's folder_card), for a committed data folder's name"""
    q = "/" + name
    for keys, c in ((("aifoundry3", "/a3-", "card-a3-", "-a3-"), "aifoundry3 card 0"),
                    (("aifoundry1-c1", "/a1c1-", "card-a1c1-", "a1c1", "-card1"), CARD["a1c1"]),
                    (("aifoundry1-card0", "/a1c0-", "card-a1c0-", "a1c0", "-card0"), CARD["a1c0"]),
                    (("aifoundry2", "/a2-", "card-a2-", "a2c0"), CARD["a2c0"]),
                    (("aifoundry1", "/a1-", "card-a1-"), "aifoundry1 (card not named)")):
        if any(k in q for k in keys):
            return c
    return None


def registered_sha(lab, exp_n, f):
    """the path's registered sha256 by that experiment's registered lists, when its bytes are nowhere in the lab"""
    for lst, pre in ((os.path.join(lab, "tools", "claims-v3", "e" + exp_n, "proposal", "src", "SRC-SHA256SUMS"), ""),
                     (os.path.join(lab, "tools", "claims-v3", "e" + exp_n, "box", "SRC-SHA256SUMS-e" + exp_n), "")):
        if os.path.exists(lst):
            for ln in open(lst, errors="replace"):
                p = ln.split()
                if len(p) == 2 and (p[1] == f or p[1].endswith("/" + f) or f.endswith("/" + p[1].split("src/", 1)[-1])):
                    return p[0]
    return None


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("label")
    ap.add_argument("desk")
    ap.add_argument("src")
    ap.add_argument("lab")
    ap.add_argument("--out", required=True)
    ap.add_argument("--txt", required=True)
    ap.add_argument("--this-dir", default=None, help="this session's own data folder name (never read)")
    a = ap.parse_args(argv)
    card_code, sess = a.label.split("-")
    card = CARD[card_code]
    nr = json.load(open(os.path.join(a.desk, "neverrun-e221.json")))
    cf = json.load(open(os.path.join(a.desk, "configs-e221.json")))
    indexed = {s["folder"].split("/")[0] for s in cf.get("sessions", [])}
    rows = {(r["arm"], r["card"]): r for r in nr["rows"]}
    sched = json.load(open(os.path.join(a.src, "sched", a.label + ".json")))
    arms = []
    for r in sched["runs"]:
        if r.get("role") in ("arm", "time", "anchor") and r["arm"] not in arms:
            arms.append(r["arm"])
    K = Kinds(a.lab)
    ddir = os.path.join(a.lab, "docs", "reports", "data")
    new_cfg, new_tok, new_folders = {}, {}, []
    cache = {}
    for d in sorted(os.listdir(ddir)):
        top = os.path.join(ddir, d)
        if not os.path.isdir(top) or d in indexed or folder_card(d) != card:
            continue
        if a.this_dir and d == a.this_dir:
            continue
        em = re.search(r"-e(\d{2,3})-", d)
        exp = "E" + em.group(1) if em else d
        sm = re.search(r"-(a\dc\d-S\d+r?)", d)
        tag = f"{exp} {sm.group(1)}" if sm else f"{exp} {d}"
        nrec = 0
        for rj in sorted(glob.glob(os.path.join(top, "runs", "*", "run.json")) + glob.glob(os.path.join(top, "session", "runs", "*", "run.json"))):
            try:
                R = json.load(open(rj))
            except ValueError:
                continue
            if R.get("ran") is False:
                continue
            for pr in R.get("procs") or []:
                av = pr.get("argv") or []
                v = argval(av, "--values")
                if not v:
                    continue
                parts = v.split(":")
                tok, gen, f = parts[0], (parts[1] if len(parts) > 1 else ""), (parts[2] if len(parts) > 2 else "")
                host = av[0] if av else ""
                if "rgm211" in host or "rgm211" in (argval(av, "--kernel") or ""):
                    continue
                tsha = ""
                if f:
                    cands = [os.path.join(a.lab, f)]
                    if em:
                        cands.append(os.path.join(a.lab, "tools", "claims-v3", "e" + em.group(1), "proposal", f))
                    for cp in cands:
                        if os.path.exists(cp):
                            cache.setdefault(cp, sha(cp))
                            tsha = cache[cp]
                            break
                    else:
                        tsha = (registered_sha(a.lab, em.group(1), f) if em else None) or ("MISSING:" + f)
                key = (tok, argval(av, "--type"), K.data_key(gen, tsha), argval(av, "--shires"))
                new_cfg.setdefault(key, set()).add(tag)
                new_tok.setdefault(tok, set()).add(tag)
                nrec += 1
        if nrec:
            new_folders.append(f"{d} ({nrec} process records)")
    out_rows, changed, tally = [], [], {}
    for arm in arms:
        rr = rows.get((arm, card))
        if rr is None:
            out_rows.append({"arm": arm, "card": card, "registered": "NO ROW", "now": "NO ROW"})
            tally["NO ROW"] = tally.get("NO ROW", 0) + 1
            continue
        reg = rr["label"]
        k = (rr["token"], rr["fmt"], rr["data"], rr["mask"])
        why, now = [], reg
        if k in new_cfg:
            why.append("configuration committed after the registration's index by " + ", ".join(sorted(new_cfg[k])))
            now = "REPEAT"
        elif reg in ("NEVER", "NEVER-BY-INDEX") and rr["token"] in new_tok:
            why.append(f"shape {rr['token']} committed after the registration's index by " + ", ".join(sorted(new_tok[rr['token']])))
            now = "SHAPE-ONLY"
        row = {"arm": arm, "card": card, "token": k[0], "fmt": k[1], "data": k[2], "mask": k[3], "registered": reg, "now": now, "why": why}
        out_rows.append(row)
        tally[now] = tally.get(now, 0) + 1
        if now != reg:
            changed.append(row)
    e221_s = sorted({t.split(" ", 1)[1] for v in new_tok.values() for t in v if t.startswith("E221 ")})
    oth_s = sorted({t for v in new_tok.values() for t in v if not t.startswith("E221 ")})
    res = {"what": "data-e221's re-read of E221's never-run labels for one session at its data commit (the registration's labels; "
                   "labels only, REPORTED, nothing dropped)", "session": a.label, "card": card, "arms": len(arms), "tally_now": tally,
           "changed": len(changed), "index_folders": len(indexed), "folders_after_index_on_card": new_folders,
           "e221_sessions_committed_on_card": e221_s, "others_after_index_on_card": oth_s,
           "registration_labels_configs_sha256": nr.get("configs_sha256"), "rows": out_rows,
           "python": sys.version.split()[0], "interpreter": sys.executable}
    json.dump(res, open(a.out, "w"), indent=1)
    L = [f"N never-run labels re-read for {a.label} ({card}): {len(arms)} arms; now {dict(sorted(tally.items()))}; changed from the "
         f"registration's labels: {len(changed)}; folders on the card committed after the registration's index: "
         f"{'; '.join(new_folders) or 'none'}"]
    for r in changed[:60]:
        L.append(f"  {r['arm']}: {r['registered']} -> {r['now']} ({'; '.join(r['why'])})")
    open(a.txt, "w").write("\n".join(L) + "\n")
    print("\n".join(L[:12]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
