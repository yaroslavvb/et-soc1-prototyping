#!/usr/bin/env python3
"""E184 arm S, dated note 2 (Sun 8 Nov 2026): the checks the collection of arm S's own session files was committed under, re-made from
the committed files alone. Run it from the top of the repository:

    /usr/bin/python3 -B docs/reports/data/2026-11-08-e184-sensor-validation/check_note2_e184.py docs/reports/data/2026-11-08-e184-sensor-validation

It prints a text report (the data directory's own relative names only, no clock, no path) and exits 0 only if every check holds:
  1. COPY-BACK EXACT: copyback-box-list-arm-s.txt is aifoundry3's own READ listing, taken right after kit note 4's step 11 v4, of the
     sha256 of every file that step copied (our tree's build/e184/ without its operand images, and the pass directories e184-smoke and
     e184-stoptest). raw/aifoundry3/logs/ and raw/aifoundry3/e184-smoke, e184-stoptest must hold exactly those names with those sha256
     (no file only on one side), the box must have no e184 pass directory, and the session's files must be there by name (the T0 log and
     .out, both session config reads with .time and .err, the preflight, step 7's two reads, one dry log).
  2. The collector re-made: reduce_e184_v4.py (dated amendment A4; kit note 3's collector) on raw/ for arm S with t0-S.txt and for arm B
     with t0-B.txt, then score_e184_v3.py on both, into a temporary directory. reduced-e184s-v4.json must be the committed one byte for
     byte; reduced-e184b-v4.json arm B's committed one (8bf74b26); the scored pair the committed scored-e184-v3-arms-bs.json and .md.
  3. Arm B's section of the both-arm files: scored-e184-v3-arms-bs.json's arm_B, and every top-level key but arm_S, equal to arm B's
     committed scored-e184-v3.json; the .md's header and its "## Arm B" section equal to arm B's committed scored-e184-v3.md.
  4. Arm S: the reducer's session gate (gate_ok and its reasons), every arm S rule's word, and the session's start and end config reads
     against the registered TDP 0 W, 65 C and 600 MHz ("as registered", else "MOVED", A4's word for a complete read not as registered).
  5. The readers f8d94224 committed, re-run on raw/aifoundry3/e184-smoke/p18401: check_e184_v2.py smoke and posthoc_arms_e184.py, each
     equal to its committed output (smoke-gate-desk-arm-s.txt, posthoc-arms-e184.json).
  6. The committed hash lists SHA256SUMS-arm-b, SHA256SUMS-arm-s and SHA256SUMS-note1, every entry.
Standard library only; it imports no lab module and writes nothing but its temporary directory, which it removes.
SPDX-License-Identifier: Apache-2.0"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

PY = "/usr/bin/python3"
E184 = os.path.join("tools", "claims-v3", "e184")
D = os.path.normpath(sys.argv[1])
T0S = open(os.path.join(D, "t0-S.txt")).read().strip()
T0B = open(os.path.join(D, "t0-B.txt")).read().strip()
REG = {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600}
out, bad = [], []


def say(s):
    out.append(s)


def check(name, ok, detail=""):
    say(f"{'OK  ' if ok else 'FAIL'} {name}{': ' + detail if detail else ''}")
    if not ok:
        bad.append(name)


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha(p):
    with open(p, "rb") as f:
        return sha_bytes(f.read())


def files_under(top):
    got = {}
    for dp, dns, fns in os.walk(top):
        dns.sort()
        for f in sorted(fns):
            p = os.path.join(dp, f)
            got[os.path.relpath(p, top)] = sha(p)
    return got


# 1. COPY-BACK EXACT --------------------------------------------------------------------------------------------------------------------
logs, passes, absent, nonreg, images = {}, {}, [], [], None
for ln in open(os.path.join(D, "copyback-box-list-arm-s.txt"), encoding="utf-8"):
    ln = ln.rstrip("\n")
    m = re.match(r"^LOGS ([0-9a-f]{64})  \./(.+)$", ln)
    if m:
        logs[m.group(2)] = m.group(1)
    m = re.match(r"^PASS ([0-9a-f]{64})  (.+)$", ln)
    if m:
        passes[m.group(2)] = m.group(1)
    m = re.match(r"^ABSENT (.+)$", ln)
    if m:
        absent.append(m.group(1))
    if re.match(r"^(LOGS|PASS)-NONREG ", ln):
        nonreg.append(ln)
    m = re.match(r"^IMAGES-LEFT-OUT files (\d+)$", ln)
    if m:
        images = int(m.group(1))
say("1. COPY-BACK EXACT, against aifoundry3's own listing (copyback-box-list-arm-s.txt)")
here_logs = files_under(os.path.join(D, "raw", "aifoundry3", "logs"))
here_pass = {}
for d in ("e184-smoke", "e184-stoptest"):
    here_pass.update({os.path.join(d, k): v for k, v in files_under(os.path.join(D, "raw", "aifoundry3", d)).items()})
check("the session's own files (build/e184/ on the box, its operand images left out)", here_logs == logs,
      f"{len(logs)} on the box, {len(here_logs)} here; only on the box {sorted(set(logs) - set(here_logs))}; only here "
      f"{sorted(set(here_logs) - set(logs))}; sha256 differ {sorted(k for k in set(logs) & set(here_logs) if logs[k] != here_logs[k])}")
check("the pass directories this T0's log names (e184-smoke, e184-stoptest)", here_pass == passes,
      f"{len(passes)} on the box, {len(here_pass)} here; sha256 differ "
      f"{sorted(k for k in set(passes) & set(here_pass) if passes[k] != here_pass[k])}")
check("no e184 pass directory on the box, and none here", "e184" in absent and not os.path.exists(os.path.join(D, "raw", "aifoundry3", "e184")),
      f"the box: absent {absent}")
check("no non-regular entry in the box's listing", not nonreg, f"{nonreg}")
say(f"     the operand images left out on the box, by step 11 v4's design: {images} files")
want = [f"session-S-t{T0S}.log", f"session-S-t{T0S}.out", f"dmcmd-preflight-S-t{T0S}.txt"]
for e in ("start", "end"):
    want += [f"config-S-t{T0S}-{e}.json", f"config-S-t{T0S}-{e}.json.time", f"config-S-t{T0S}-{e}.json.err"]
step7 = sorted(k for k in here_logs if re.match(r"^config-S-step7-\d+\.json$", k))
dry = sorted(k for k in here_logs if re.match(r"^session-S-dry-t\d+\.log$", k))
other = sorted(set(here_logs) - set(want) - set(step7) - set(dry))
check("the session's files by name", not (set(want) - set(here_logs)) and len(step7) == 2 and len(dry) == 1 and not other,
      f"missing {sorted(set(want) - set(here_logs))}; step 7's reads {step7}; dry logs {dry}; others {other}")

# 2. the collector re-made ------------------------------------------------------------------------------------------------------------
say("2. the collector re-made from the committed files (reduce_e184_v4.py with A4, score_e184_v3.py; kit note 3's collector)")
tmp = tempfile.mkdtemp(prefix="e184-note2-")
try:
    made = {}
    for arm, lc, t0 in (("S", "s", T0S), ("B", "b", T0B)):
        r = subprocess.run([PY, "-B", os.path.join(E184, "reduce_e184_v4.py"), os.path.join(D, "raw"), "--arm", arm, "--t0", t0],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=1800)
        made[lc] = os.path.join(tmp, f"reduced-e184{lc}-v4.json")
        open(made[lc], "wb").write(r.stdout)
        check(f"reduce_e184_v4.py --arm {arm} --t0 {t0}: rc 0 and reduced-e184{lc}-v4.json the committed one, byte for byte",
              r.returncode == 0 and r.stdout == open(os.path.join(D, f"reduced-e184{lc}-v4.json"), "rb").read(),
              f"rc {r.returncode}, sha256 {sha_bytes(r.stdout)[:16]}")
    r = subprocess.run([PY, "-B", os.path.join(E184, "score_e184_v3.py"), "--s", made["s"], "--b", made["b"], "--out", tmp],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=1800)
    for ext in ("json", "md"):
        p = os.path.join(tmp, f"scored-e184-v3.{ext}")
        same = os.path.exists(p) and open(p, "rb").read() == open(os.path.join(D, f"scored-e184-v3-arms-bs.{ext}"), "rb").read()
        check(f"score_e184_v3.py: rc 0 and scored-e184-v3.{ext} the committed scored-e184-v3-arms-bs.{ext}, byte for byte",
              r.returncode == 0 and same, f"rc {r.returncode}")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# 3. arm B's section ------------------------------------------------------------------------------------------------------------------
say("3. arm B's section of the both-arm files, against arm B's committed scored-e184-v3.json and .md (8bf74b26)")
both = json.load(open(os.path.join(D, "scored-e184-v3-arms-bs.json")))
armb = json.load(open(os.path.join(D, "scored-e184-v3.json")))
check("arm_B equal", both.get("arm_B") == armb.get("arm_B") and both.get("arm_B") is not None)
rest = sorted(k for k in set(both) | set(armb) if k not in ("arm_S", "arm_B"))
check("every other top-level key but arm_S equal", all(both.get(k) == armb.get(k) for k in rest), f"keys {rest}")
say(f"     arm_S in arm B's committed file: {json.dumps(armb.get('arm_S'))}")


def section(md, name):
    m = re.search(r"^## " + re.escape(name) + r"\n(.*?)(?=^## |\Z)", md, re.S | re.M)
    return m.group(1) if m else None


bm = open(os.path.join(D, "scored-e184-v3-arms-bs.md"), encoding="utf-8").read()
am = open(os.path.join(D, "scored-e184-v3.md"), encoding="utf-8").read()
check("the .md's '## Arm B' section equal", section(bm, "Arm B") is not None and section(bm, "Arm B") == section(am, "Arm B"))
check("the .md's header equal", bm.split("\n## ")[0] == am.split("\n## ")[0])
say(f"     arm B's committed .md, its '## Arm S' section: {section(am, 'Arm S')!r}")

# 4. arm S ----------------------------------------------------------------------------------------------------------------------------
say("4. arm S: the session gate (reduce_e184_v4.py, A3-3 with A4) and the session's config reads")
rs = json.load(open(os.path.join(D, "reduced-e184s-v4.json")))["session"]
say(f"     gate_ok {rs['gate_ok']}; reasons {rs['reasons']}; T0 {rs['t0']}; session logs found {rs['session_logs_found']}; "
    f"log_session_end {rs['log_session_end']}; log_smoke_gate_passed {rs['log_smoke_gate_passed']}; departures {rs['departures']}")
check("the session gate does not hold (A3-1: arm S not run)", rs["gate_ok"] is False)
for e in ("start", "end"):
    c = rs["config"][e]
    word = "as registered" if rs["config_status"][e] == "complete" and all(c.get(k) == v for k, v in REG.items()) else "MOVED"
    say(f"     the {e} read ({rs['config_from'][e]}, {rs['config_status'][e]}, attempted {rs['config_attempt_utc'][e]}): "
        f"{json.dumps(c, sort_keys=True)}: {word}")
    check(f"the {e} config read is TDP 0 W, 65 C, 600 MHz as registered", word == "as registered")
words = {k: v.get("verdict") for k, v in sorted(both.get("arm_S", {}).items()) if k.startswith("E184-") and isinstance(v, dict)}
say(f"     arm S's rules in the both-arm scored file: {words}")
check("every arm S rule NOT SCORED (E184-C, -J, -L, -N, -P)", sorted(words) == ["E184-C", "E184-J", "E184-L", "E184-N", "E184-P"]
      and set(words.values()) == {"NOT SCORED"})

# 5. the readers f8d94224 committed ---------------------------------------------------------------------------------------------------
say("5. the readers f8d94224 committed, re-run on raw/aifoundry3/e184-smoke/p18401")
p18401 = os.path.join(D, "raw", "aifoundry3", "e184-smoke", "p18401")
for cmd, ref in (([PY, "-B", os.path.join(E184, "check_e184_v2.py"), "smoke", p18401], "smoke-gate-desk-arm-s.txt"),
                 ([PY, "-B", os.path.join(D, "posthoc_arms_e184.py"), p18401], "posthoc-arms-e184.json")):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=600)
    check(f"{os.path.basename(cmd[2])}{' smoke' if 'check_e184' in cmd[2] else ''}: the committed {ref}, byte for byte (rc {r.returncode})",
          r.stdout == open(os.path.join(D, ref), "rb").read())

# 6. the committed hash lists ---------------------------------------------------------------------------------------------------------
say("6. the committed hash lists")
for name, want_n in (("SHA256SUMS-arm-b", 80), ("SHA256SUMS-arm-s", 23), ("SHA256SUMS-note1", 4)):
    rows = [ln.split("  ", 1) for ln in open(os.path.join(D, name)) if ln.strip()]
    ok_n = sum(1 for h, f in rows if os.path.isfile(os.path.join(D, f.strip())) and sha(os.path.join(D, f.strip())) == h)
    check(f"{name}: {ok_n} of {len(rows)} OK", ok_n == len(rows) == want_n, f"want {want_n}")

say(f"CHECK-NOTE2-E184 {'PASS' if not bad else 'FAIL'}: {len(bad)} failed{' (' + '; '.join(bad) + ')' if bad else ''}")
sys.stdout.write("\n".join(out) + "\n")
sys.exit(0 if not bad else 1)
