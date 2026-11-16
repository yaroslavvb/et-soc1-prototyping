#!/usr/bin/env python3
"""E200's harness (Q192, lane kit-e200, Mon 16 Nov 2026, before any E200 datum): every file the box runs or reads for E200, at its sha256,
in E197's harness form (tools/claims-v3/e197/harness_e197.py, unchanged beside it) for E200's root on aifoundry2.

    python3 -I -B harness_e200.py --list               the sync list, one repository path a line (harness-e200.json last)
    python3 -I -B harness_e200.py --make               write harness-e200.json from the files as they are (the kit's own step)
    python3 -I -B harness_e200.py --check              harness-e200.json re-made in memory equals the committed one: CHECK PASS
                                                       (a fwgate record added since is named, not pinned: see below)
    python3 -I -B harness_e200.py --box [--root DIR]   every file of harness-e200.json at its sha256 under DIR (default: the repository's
                                                       top): HARNESS OK: <n> files, or HARNESS FAIL naming each

The files: E197's registration (every path SHA256SUMS-e197-registration names, and the list itself: E197.md, its proposal/ byte for byte,
its lab/ runner and D1 diff, its desk/ with the registered dry listings and kind table), E200's departure W1 (lab/run_trains-e200-W1.diff:
the box makes E200's runner from it), the kit's box files (the session's wrapper, the watch, the checker, the build, the preflight, E200's
guard, this file), the device-command checker v2 with its table (the preflight runs them on the box), the lab's firmware gate with its
records (steps 4, 7 and 9 run it from E200's root: look, read, guard) and E194's common module (step 7 reads the config read's object with
its --config-line). E200's root is <box tree>/build/claims-v3/aifoundry2/e200 on aifoundry2 (the box tree ~/claude/et-soc1-prototyping),
where step 5's rsync -R puts each file at its repository path. The launch passes harness-e200.json's own sha256 (read from the lab clone,
where step 2 pins it by the kit's list) and the session checks it before this file runs. fwgate's records are pinned as they were when
the kit was made; a record a later commit adds under tools/claims-v3/fwgate/records/ (additions only there: the history check's rule)
is in --list, so the sync carries it and fwgate reads the same records on the box as at the desk's look (a record of this boot's read:
CONTINUITY, KIT.md 4), and --check names it and passes; any other difference fails. Exit 0, 3 a failed check, 2 usage.
SPDX-License-Identifier: Apache-2.0
"""
import glob
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
E = "tools/claims-v3/e200"
JSON = os.path.join(HERE, "harness-e200.json")
RECS = "tools/claims-v3/fwgate/records/"
REG_LIST = "tools/claims-v3/e197/SHA256SUMS-e197-registration"
E200_REG = [E + "/lab/run_trains-e200-W1.diff"]
KIT_BOX = [E + "/session_e200.sh", E + "/watch_e200.py", E + "/check_e200.py", E + "/build_e200.sh", E + "/preflight_e200.sh",
           E + "/harness_e200.py", E + "/ettelem_guard_e200.sh"]
OTHERS = ["tools/claims-v3/dmcmd_audit_v2.py", "tools/claims-v3/dmcmd_table_v2.json", "tools/claims-v3/fwgate/fwgate.py",
          "tools/claims-v3/e194/e194_common.py"]


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def paths():
    reg = []
    with open(os.path.join(REPO, REG_LIST)) as f:
        for ln in f:
            if ln.strip():
                reg.append(ln.rstrip("\n").split("  ", 1)[1])
    recs = sorted(os.path.relpath(p, REPO) for p in glob.glob(os.path.join(REPO, RECS + "*.json")))
    return sorted(set(reg + [REG_LIST] + E200_REG + KIT_BOX + OTHERS + recs))


def made():
    ps = paths()
    return {"schema": "e200-harness/1", "count": len(ps), "files": {p: sha(os.path.join(REPO, p)) for p in ps}}


def main(argv):
    if argv == ["--list"]:
        for p in paths():
            print(p)
        print(E + "/harness-e200.json")
        return 0
    if argv == ["--make"]:
        with open(JSON, "w") as f:
            json.dump(made(), f, indent=1, sort_keys=True)
            f.write("\n")
        print(f"harness-e200.json written: {made()['count']} files")
        return 0
    if argv == ["--check"]:
        with open(JSON) as f:
            have = json.load(f)
        want = made()
        hf, wf = have.get("files", {}), want["files"]
        new = sorted(p for p in wf if p not in hf and p.startswith(RECS))   # a fwgate record a later commit added: named, not pinned
        pinned = {p: h for p, h in wf.items() if p not in new}
        if pinned == hf and have.get("count") == len(hf) and have.get("schema") == want["schema"]:
            note = ("; fwgate records added since the kit, synced and read by fwgate, not pinned: " +
                    ", ".join(os.path.basename(p) for p in new)) if new else ""
            print(f"CHECK PASS: harness-e200.json re-made equals the committed one ({len(hf)} files{note})")
            return 0
        diff = sorted(set(hf.items()) ^ set(pinned.items()))
        print("CHECK FAIL: harness-e200.json differs from the files as they are: " + ", ".join(p for p, _ in diff[:8]))
        return 3
    if argv[:1] == ["--box"]:
        root = argv[argv.index("--root") + 1] if "--root" in argv else REPO
        with open(os.path.join(root, E, "harness-e200.json")) as f:
            h = json.load(f)
        bad = []
        for p, want in sorted(h["files"].items()):
            q = os.path.join(root, p)
            if not os.path.isfile(q):
                bad.append(f"missing {p}")
            elif sha(q) != want:
                bad.append(f"differs {p}")
        if bad or len(h["files"]) != h.get("count"):
            print("HARNESS FAIL: " + ", ".join(bad[:10]) + (f" (and {len(bad) - 10} more)" if len(bad) > 10 else ""))
            return 3
        print(f"HARNESS OK: {len(h['files'])} files at their sha256 under the root")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
