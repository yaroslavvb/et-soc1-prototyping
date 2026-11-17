#!/usr/bin/env python3
"""E209 (Q202, lane kit-e209, Tue 17 Nov 2026, before any E209 datum): E209's BOX ROOT - what runs on aifoundry2, from where, at which
bytes. Python's own modules only.

    /usr/bin/python3 -I -B tools/claims-v3/e209/make_box_e209.py make     writes box/a2c0-E209.json, box/SRC-SHA256SUMS-e209 and
                                                                           harness-e209.json beside this file (the desk, once)
    /usr/bin/python3 -I -B tools/claims-v3/e209/make_box_e209.py check    re-makes all three in memory, compares them byte for byte with
                                                                           the committed files and checks every source: CHECK PASS
    /usr/bin/python3 -I -B tools/claims-v3/e209/make_box_e209.py sync <root>   copies the harness's files from this checkout into the
                                                                           box root (step 5), then reads every one back at its sha256

THE BOX ROOT is E208's kit layout (tools/claims-v3/e208/proposal/src/README.md, "the kit's root"), in a folder of the card lane's own
(the card-lane brief names it; never the model session's folders, never inside the lab clone):
  src/                          E208's registered kit, every file UNCHANGED at its committed sha256 (run_mms.py, mms_common.py,
                                mms_ident.py, fake_card_mms.py, guard_ettelem.sh, build_mms.sh, preflight_mms.sh, check_mms.py,
                                status_mms.sh, stop_mms.sh, reduce_mms.py, the rgm136 and ettelem sources, the device-command
                                table, the tiles, ...), PLUS E209's four box files: src/sched/a2c0-E209.json, src/session_e209.sh,
                                src/start_e209.sh, src/dry_e209.sh, and E209's src/SRC-SHA256SUMS (the list E208's check_mms.py
                                --box reads: exactly what its --make writes for this src/);
  tools/claims-v3/kinds/real2/tiles/<fmt>/<name>.bin   E206's real tiles at the paths E209's registered schedule names, relative to
                                the root (the runner's working folder), each at points-e209.json's tiles_sha256;
  fwgate/fwgate.py, fwgate/records/*.json             the lab's reboot gate, unchanged (its records beside it, as it reads them);
  build/, run/, sessions/, dry/, first/               written on the box (the build, the box lock and STOP files, the session, the
                                dry passes, step 7's folders).
THE SCHEDULE: src/sched/a2c0-E209.json is the registered sched-e209.json with ONE key changed, "kit": "1116-mmsweep", the word E208's
runner's schedule reader (mms_common.load_sched, unchanged) requires; every run, the order, the forms, the timing, the process and the
smoke are the registration's bytes (checked here as JSON equal but for that key). E208's runner, mms_common.py and the reducer stay
byte for byte E208's (the registration pins the reducer with its mms_common.py).
SPDX-License-Identifier: Apache-2.0
"""
import fcntl
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
E = "tools/claims-v3/e209"
E208 = "tools/claims-v3/e208/proposal/src"
FWG = "tools/claims-v3/fwgate"
BOXF = {"src/session_e209.sh": f"{E}/box/session_e209.sh", "src/start_e209.sh": f"{E}/box/start_e209.sh",
        "src/dry_e209.sh": f"{E}/box/dry_e209.sh", "src/sched/a2c0-E209.json": f"{E}/box/a2c0-E209.json"}
GEN = {"box/a2c0-E209.json": None, "box/SRC-SHA256SUMS-e209": None, "harness-e209.json": None}
# the registration's own pins (SHA256SUMS-e209-registration): the schedule and the points this tool reads
REG_PINS = {f"{E}/sched-e209.json": "ec8713a7a69ddf5ee503f4efe6fd77bda3f63845aada69ac167fb9a2df0ec620",
            f"{E}/points-e209.json": "cfdda741bcc8cbd8555ff21809f2897fae0f734b66727b108795cd138fb07261"}
# E208's registered kit list (its SRC-SHA256SUMS, as committed in the lab) and the two files E209's registration pins in it
E208_SUMS_SHA = "543e9298d5a1013d"          # the prefix E208's data checks recorded (C0); the full file is read and hashed below
E208_PINS = {f"{E208}/reduce_mms.py": "b9e32618020d28a590a615f97e5655c1ea458a6a757bf5658f2517a87fc3e0a5",
             f"{E208}/mms_common.py": "c3fc7883544ad73c3e455f7e950b62b9b155fd2ed972cee5e3524d74a378569c"}
FWG_PIN = "4d529a5764a97373f451544821f0432ce31d6afaecad0f1e254d18d76e736b95"     # fwgate.py, as E200's reads recorded it
KIT_WORD = "1116-mmsweep"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def shab(b):
    return hashlib.sha256(b).hexdigest()


def rp(r):
    return os.path.join(REPO, r)


def e208_files():
    """E208's src/ files as its SRC-SHA256SUMS lists them (rel 'src/...') -> (repo path, sha256), each checked."""
    out, bad = {}, []
    sums = rp(f"{E208}/SRC-SHA256SUMS")
    if not sha(sums).startswith(E208_SUMS_SHA):
        bad.append(f"{E208}/SRC-SHA256SUMS is not the registered list (sha256 {sha(sums)[:16]}, want {E208_SUMS_SHA})")
    for ln in open(sums):
        h, r = ln.rstrip("\n").split("  ", 1)
        src = f"{E208}/{r[len('src/'):]}"
        got = sha(rp(src)) if os.path.isfile(rp(src)) else "missing"
        if got != h:
            bad.append(f"{src}: {got[:16]}, want {h[:16]}")
        out[r] = (src, h)
    listed = set(out)
    for dp, dn, fn in os.walk(rp(E208)):
        dn[:] = [d for d in dn if d != "__pycache__"]
        for n in fn:
            r = "src/" + os.path.relpath(os.path.join(dp, n), rp(E208))
            if r != "src/SRC-SHA256SUMS" and not n.endswith(".pyc") and r not in listed:
                bad.append(f"{E208}/{r[4:]}: in E208's src/ but not in its list")
    for p, want in E208_PINS.items():
        if sha(rp(p)) != want:
            bad.append(f"{p}: not the registration's pin {want[:16]}")
    return out, bad


def make_sched():
    s = json.load(open(rp(f"{E}/sched-e209.json")))
    d = dict(s)
    d["kit"] = KIT_WORD
    return json.dumps(d, indent=1, sort_keys=True) + "\n", s


def make_all():
    """-> ({gen name: bytes}, [problems])"""
    bad = []
    for p, want in REG_PINS.items():
        if sha(rp(p)) != want:
            bad.append(f"{p}: sha256 {sha(rp(p))[:16]}, not the registration's {want[:16]}")
    e208, b2 = e208_files()
    bad += b2
    sched_txt, s = make_sched()
    s2 = json.loads(sched_txt)
    if {k: v for k, v in s2.items() if k != "kit"} != {k: v for k, v in s.items() if k != "kit"} or s2["kit"] != KIT_WORD:
        bad.append("the box schedule is not the registered one but for its kit word")
    # the box's src/: E208's files plus E209's four
    src = {r: h for r, (_, h) in e208.items()}
    for r, f in BOXF.items():
        if r in src:
            bad.append(f"{r}: E209's box file would replace E208's")
        src[r] = shab(sched_txt.encode()) if r == "src/sched/a2c0-E209.json" else sha(rp(f))
    sums_txt = "".join(f"{h}  {r}\n" for r, h in sorted(src.items()))
    # the tiles: every --values file of the schedule (and the smoke) at points-e209.json's tiles_sha256
    pts = json.load(open(rp(f"{E}/points-e209.json")))
    tiles = pts["tiles_sha256"]
    used = set()
    for r in s["runs"] + s["smoke"]:
        if r.get("values"):
            for f in r["values"].split(":", 2)[2].split(","):
                used.add(f)
    for f in sorted(used):
        if f not in tiles:
            bad.append(f"tile {f}: named by the schedule, not in points-e209.json's tiles_sha256")
        elif f.startswith("src/"):
            if e208.get(f, (None, None))[1] != tiles[f]:
                bad.append(f"tile {f}: E208's kit copy is not points-e209.json's {tiles[f][:16]}")
        elif not os.path.isfile(rp(f)) or sha(rp(f)) != tiles[f]:
            bad.append(f"tile {f}: the lab's copy is not points-e209.json's {tiles[f][:16]}")
    rows = []
    for r, (from_, h) in sorted(e208.items()):
        rows.append({"dest": r, "from": from_, "sha256": h, "what": "E208's registered kit, unchanged"})
    for r, f in sorted(BOXF.items()):
        rows.append({"dest": r, "from": f, "sha256": src[r], "what": "E209's box file"})
    rows.append({"dest": "src/SRC-SHA256SUMS", "from": f"{E}/box/SRC-SHA256SUMS-e209", "sha256": shab(sums_txt.encode()),
                 "what": "E209's src/ list (E208's check_mms.py --box reads it)"})
    for f in sorted(x for x in used if not x.startswith("src/")):
        rows.append({"dest": f, "from": f, "sha256": tiles[f], "what": "E206's real tile, at the path E209's schedule names"})
    if sha(rp(f"{FWG}/fwgate.py")) != FWG_PIN:
        bad.append(f"{FWG}/fwgate.py: not {FWG_PIN[:16]}")
    rows.append({"dest": "fwgate/fwgate.py", "from": f"{FWG}/fwgate.py", "sha256": FWG_PIN, "what": "the lab's reboot gate, unchanged"})
    for n in sorted(os.listdir(rp(f"{FWG}/records"))):
        if n.endswith(".json"):
            rows.append({"dest": f"fwgate/records/{n}", "from": f"{FWG}/records/{n}", "sha256": sha(rp(f"{FWG}/records/{n}")),
                         "what": "fwgate's committed firmware records (it reads them beside itself)"})
    harness = {"experiment": "E209", "what": "every file of E209's box root, from this checkout, at its sha256 (make_box_e209.py sync)",
               "box": "aifoundry2", "card": "a2c0", "schedule": "src/sched/a2c0-E209.json",
               "schedule_from": {"registered": f"{E}/sched-e209.json", "sha256": REG_PINS[f"{E}/sched-e209.json"],
                                 "changed": {"kit": [s["kit"], KIT_WORD]}},
               "e208_src_list": {"file": f"{E208}/SRC-SHA256SUMS", "sha256": sha(rp(f"{E208}/SRC-SHA256SUMS")), "files": len(e208)},
               "n_files": len(rows), "files": rows}
    gen = {"box/a2c0-E209.json": sched_txt.encode(), "box/SRC-SHA256SUMS-e209": sums_txt.encode(),
           "harness-e209.json": (json.dumps(harness, indent=1, sort_keys=True) + "\n").encode()}
    return gen, bad


def cmd_make():
    gen, bad = make_all()
    if bad:
        print("MAKE REFUSED: " + "; ".join(bad))
        return 1
    for n, b in gen.items():
        with open(os.path.join(HERE, n), "wb") as f:
            f.write(b)
        print(f"wrote {E}/{n} ({len(b)} bytes, sha256 {shab(b)})")
    return 0


def cmd_check():
    gen, bad = make_all()
    for n, b in gen.items():
        p = os.path.join(HERE, n)
        if not os.path.exists(p) or open(p, "rb").read() != b:
            bad.append(f"{E}/{n}: differs from its re-make")
        else:
            print(f"{E}/{n}: equal to its re-make (sha256 {shab(b)[:16]})")
    h = json.loads(gen["harness-e209.json"])
    for row in h["files"]:
        got = sha(rp(row["from"])) if os.path.isfile(rp(row["from"])) else "missing"
        if got != row["sha256"]:
            bad.append(f"{row['from']}: {got[:16]}, want {row['sha256'][:16]}")
    print(f"harness: {h['n_files']} files (E208's {h['e208_src_list']['files']}, E209's box files 4 and its list, the real tiles, fwgate)")
    print("CHECK PASS" if not bad else "CHECK FAIL: " + "; ".join(bad))
    return 0 if not bad else 1


def cmd_sync(root):
    root = os.path.abspath(root)
    repo_real = os.path.realpath(REPO)
    if os.path.realpath(root) == repo_real or os.path.realpath(root).startswith(repo_real + os.sep):
        print("SYNC REFUSED: the box root is inside the lab checkout")
        return 3
    if os.path.basename(root).startswith("ee-"):
        print("SYNC REFUSED: a folder named ee-* is the model session's")
        return 3
    h = json.load(open(os.path.join(HERE, "harness-e209.json")))
    os.makedirs(os.path.join(root, "run"), exist_ok=True)
    lk = open(os.path.join(root, "run", "box.lock"), "a+")
    try:
        fcntl.flock(lk.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("SYNC REFUSED: run/box.lock is held (a session, a build or a dry pass of the kit runs in this root)")
        return 3
    bad = []
    for row in h["files"]:
        src = rp(row["from"])
        if not os.path.isfile(src) or sha(src) != row["sha256"]:
            bad.append(f"{row['from']}: not at its sha256 in this checkout")
    if bad:
        print("SYNC REFUSED: " + "; ".join(bad))
        return 3
    want = {row["dest"] for row in h["files"]}
    n_new = n_same = 0
    for row in h["files"]:
        dst = os.path.join(root, row["dest"])
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.isfile(dst) and not os.path.islink(dst) and sha(dst) == row["sha256"]:
            n_same += 1
            continue
        tmp = dst + ".sync-tmp"
        shutil.copyfile(rp(row["from"]), tmp)
        os.chmod(tmp, 0o644)
        os.replace(tmp, dst)
        n_new += 1
    pruned = []
    for top in ("src", "fwgate", "tools"):
        for dp, dn, fn in os.walk(os.path.join(root, top)):
            dn[:] = [d for d in dn if d != "__pycache__"]
            for n in fn:
                p = os.path.join(dp, n)
                r = os.path.relpath(p, root)
                if r not in want and not os.path.islink(p) and os.path.isfile(p):
                    os.remove(p)
                    pruned.append(r)
    for row in h["files"]:
        dst = os.path.join(root, row["dest"])
        got = sha(dst) if os.path.isfile(dst) and not os.path.islink(dst) else "missing"
        if got != row["sha256"]:
            bad.append(f"{row['dest']}: {got[:16]} after the copy, want {row['sha256'][:16]}")
    try:
        head = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=30).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        head = None
    rec = {"experiment": "E209", "synced": time.strftime("%Y-%m-%d %H:%M:%S %Z"), "from_head": head,
           "harness_sha256": sha(os.path.join(HERE, "harness-e209.json")), "files": len(want), "copied": n_new, "already": n_same,
           "pruned": pruned, "verdict": "SYNCED" if not bad else "SYNC FAILED", "problems": bad}
    with open(os.path.join(root, "SYNC-e209.json"), "w") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
    print(f"{rec['verdict']}: {len(want)} files at the harness's sha256 ({n_new} copied, {n_same} already there, {len(pruned)} pruned "
          f"{pruned[:6]}) from HEAD {head}" + (f"; {'; '.join(bad)}" if bad else ""))
    return 0 if not bad else 14


def main(argv):
    if argv[:1] == ["make"]:
        return cmd_make()
    if argv[:1] == ["check"]:
        return cmd_check()
    if argv[:1] == ["sync"] and len(argv) == 2:
        return cmd_sync(argv[1])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
