#!/usr/bin/env python3
"""E185's runbook desk test: its stand-in box (desk only; it reads committed files and writes only under the scratch directory it is given).

  box <committed data dir> <smoke rel> <measured rel> <box root> <T0> [fault ...]
      lays out aifoundry3's ~/aifoundry as a real E185 session leaves it: the committed smoke and measured passes copied as
      build/claims-v3/aifoundry3/e185-smoke/p18501/ and e185/p18520/ (their files byte for byte); build/e185/T<T0>/ with a session.log
      whose last block passed every gate and ended, the committed config reads, smoke gate and preflight; build/e185/LAST_T0; then the
      session's MANIFEST.sha256 over the T0 directory and both pass directories (telemetry.jsonl.raw and tiles/ left out), as
      session_e185.sh writes it. Faults, each applied AFTER the manifest unless said: differs (one byte appended to the measured pass's
      marks.jsonl), extra (a stray file in the measured pass), no-manifest (the manifest removed), smoke-stopped (the session's last block
      says the smoke or its gate failed; before the manifest).
Python 3.9, standard library. SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import os
import shutil
import sys


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def box(src, smoke_rel, meas_rel, root, t0, faults):
    a = os.path.join(root, "aifoundry3", "aifoundry")
    dr = os.path.join(a, "build", "claims-v3", "aifoundry3")
    for rel, dst in ((smoke_rel, os.path.join(dr, "e185-smoke", "p18501")), (meas_rel, os.path.join(dr, "e185", "p18520"))):
        shutil.copytree(os.path.join(src, rel), dst, ignore=shutil.ignore_patterns("telemetry.jsonl.raw", "tiles"))
    sd = os.path.join(a, "build", "e185", f"T{t0}")
    os.makedirs(sd)
    logs = os.path.join(src, "logs")
    for f in ("config-session-start.json", "config-session-end.json", "smoke-gate.json", "dmcmd-preflight.txt"):
        if os.path.exists(os.path.join(logs, f)):
            shutil.copy2(os.path.join(logs, f), os.path.join(sd, f))
    lines = ["session start (T0 09:49:14 PST; its files in build/e185/T%s)" % t0, "the full design (no subset): budget 6300 s from T0",
             "frozen-e185.sha256: every file as registered", "dmcmd_audit preflight rc=0 (dmcmd_audit: GO (38 send site(s), 0 disallowed))",
             "config config-session-start.json: {}", "smoke and stop tests rc=0"]
    if "smoke-stopped" in faults:
        lines += ["smoke gate rc=1: {}", "the smoke or its gate failed: no measured pass"]
    else:
        lines += ["smoke gate rc=0: {}", "pass 18520 starts: the full design", "pass 18520 rc=0"]
    lines += ["config config-session-end.json: {}", "session end"]
    with open(os.path.join(sd, "session.log"), "w") as f:
        for i, x in enumerate(lines):
            f.write(f"2026-11-06 09:{49 + i // 60:02d}:{i % 60:02d} PST {x}\n")
    os.makedirs(os.path.join(a, "build", "e185"), exist_ok=True)
    open(os.path.join(a, "build", "e185", "LAST_T0"), "w").write(f"{t0}\n")
    files = []
    for top in (sd, os.path.join(dr, "e185-smoke", "p18501"), os.path.join(dr, "e185", "p18520")):
        for dp, dn, fn in os.walk(top):
            for x in fn:
                if x == "MANIFEST.sha256" or x == "telemetry.jsonl.raw" or "/tiles/" in os.path.join(dp, x):
                    continue
                files.append(os.path.relpath(os.path.join(dp, x), a))
    with open(os.path.join(sd, "MANIFEST.sha256"), "w") as f:
        for rel in sorted(files):
            f.write(f"{sha(os.path.join(a, rel))}  {rel}\n")
    if "differs" in faults:
        open(os.path.join(dr, "e185", "p18520", "marks.jsonl"), "a").write("\n")
    if "extra" in faults:
        open(os.path.join(dr, "e185", "p18520", "stray.txt"), "w").write("a file the session never listed\n")
    if "no-manifest" in faults:
        os.remove(os.path.join(sd, "MANIFEST.sha256"))
    print(f"stand-in box: {len(files)} files in the manifest; T0 {t0}; faults {faults or 'none'}")


def main():
    a = sys.argv[1:]
    if len(a) >= 6 and a[0] == "box":
        box(a[1], a[2], a[3], a[4], int(a[5]), a[6:])
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
