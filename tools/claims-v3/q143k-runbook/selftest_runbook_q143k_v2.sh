#!/usr/bin/env bash
# Q143(k)'s fix pass, Thu 5 Nov 2026: the desk test of step 22 v2 (s22_collect_q143k_v2.sh), its launch gate (cclaunch_q143k.py) and the
# collector v2 (../e176/collect_e176_v2.sh), for M11's E176 session. selftest_runbook_q143k.sh (lab 92a1b27f) stays as committed and is
# re-run here first. Stand-in ssh and rsync sit first on PATH and serve a stand-in box (a local directory laid out like aifoundry3's
# ~/aifoundry); no lab box is reached. A date shim runs GNU date. Every tree is a scratch copy under <scratch dir>, never the lab clone.
#   V1  v1's desk test, unchanged: 20 of 20;
#   A2  the dry listing with step 22 v2: every step exits 0 and no ssh or rsync call is made;
#   step 22 v2 with a stand-in collector that writes a small synthetic session (selftest_data_q143k.py synth, with the fault named):
#   C1  a good collection: 0, "E176 collected and scored";   C2  no check file (the check crashed): 14;   C3  a failed copy: 14;
#   C4  the scorer not rc 0: 14;   C5  a check file from an earlier try: 14;   C6  a desk path in an output: 16;
#   C7  the stand-in named without RB_DESKTEST=1: 10;
#   C8  the measured pass p17620 carries no C log and the smoke's is checked (the verifier's M1): 14, MISSING-CLOG p17620;
#   C9  a short check (the measured pass's last process one launch short): 14, COUNT-SHORT;
#   C10 the smoke's marks show launches and it carries no C log: 14, MISSING-CLOG p17601;
#   C11 the smoke ran no launch and carries no C log: 0, NOT-REQUIRED p17601;
#   C12 a checked launch outside every launch mark's window: 14, ORPHAN;   C13 the measured pass ran no launch: 14, NO-LAUNCH;
#   C14 the measured pass's C log empty: 14, MISSING-CLOG;   C15 a launch mark without records: 14, COUNT-UNREAD;
#   C16 a v2 file that differs from its list: 16, before any box call;
#   the gate on committed sessions, renamed to E176's passes (selftest_data_q143k.py committed):
#   U1  E166's (4 Nov): 0, COUNT-OK 6,644 / 493 and 48 / 6;   U2  E154's (3 Nov): 0, COUNT-OK 6,288 / 474 and 58 / 7;
#   U3  E166's without the measured pass's C log: 4;   U4  E166's one launch short: 4;
#   the real collector v2, end to end through step 22 v2 (ccheck.py and score_m11_v2.py as committed), on a stand-in box holding E154's
#   committed passes (the measured pass's holds renamed to M11's), in a scratch tree of tools/, workloads/ and rtl-sim/fma_toggle_v2/ (git
#   archive HEAD, plus this commit's new files) whose docs/reports/data/* are read-only links to the lab clone's (ccheck's cache in the
#   scratch, CCHECK_CACHE):
#   E1  both C logs there: 0, "E176 collected and scored", the scorer's three stages in its lines file;
#   E2  the measured pass's C log absent on the box: 14, MISSING-CLOG p17620 (v1's step said "collected and scored" here).
#
#   bash tools/claims-v3/q143k-runbook/selftest_runbook_q143k_v2.sh <scratch dir> > <log>
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
mkdir -p "$S"
S=$(cd "$S" && pwd -P)
rm -rf "${S:?}/v1" "${S:?}/tree" "${S:?}/tree2" "${S:?}/box" "${S:?}/box2" "${S:?}/bin" "${S:?}/out" "${S:?}/out2" "${S:?}/dry-out" "${S:?}/u" "${S:?}/cache"
DATA=$SRC/tools/claims-v3/q143k-runbook/selftest_data_q143k.py
E166=$SRC/docs/reports/data/2026-11-04-e166-heat-replicate-aifoundry3
E154=$SRC/docs/reports/data/2026-11-03-e154-heat-e2e-aifoundry3
NEW_RB="s22_collect_q143k_v2.sh cclaunch_q143k.py selftest_data_q143k.py list_steps_q143k_v2.sh selftest_runbook_q143k_v2.sh"
fail=0
ok() { if [ "$1" = "$2" ]; then echo "-> PASS ($3)"; else echo "-> FAIL ($3: rc $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
t_begin=$(date +%s)

step "V1. v1's desk test, unchanged (selftest_runbook_q143k.sh), in its own scratch"
bash "$SRC/tools/claims-v3/q143k-runbook/selftest_runbook_q143k.sh" "$S/v1" > "$S/v1.txt" 2>&1; rc=$?
tail -n 1 "$S/v1.txt"; n=$(grep -c -- '-> PASS' "$S/v1.txt")
ok "$rc.$n" "0.20" "v1's 20 cases"

# ---- the scratch tree for the stand-in cases: v1's layout, plus M11's v2 scorer files (for step 22 v2's list check)
T=$S/tree; B=$S/box; BIN=$S/bin
mkdir -p "$T/tools/claims-v3" "$B/aifoundry3/aifoundry" "$BIN" "$S/out"
for p in q143k-runbook q141k-runbook/v3.1 e176; do mkdir -p "$T/tools/claims-v3/$p"; cp -p "$SRC/tools/claims-v3/$p"/*.* "$T/tools/claims-v3/$p/" 2>/dev/null; done
cp -p "$SRC/tools/claims-v3/e176/collect_e176_v2.sh" "$T/tools/claims-v3/e176/"
mkdir -p "$T/tools/claims-v3/e164" "$T/tools/claims-v3/m11"; cp -p "$SRC/tools/claims-v3/e164/scrub_etwho_e164.py" "$T/tools/claims-v3/e164/"
for f in $(awk '{print $2}' "$SRC/tools/claims-v3/m11/SHA256SUMS-score-m11-v2") tools/claims-v3/m11/SHA256SUMS-score-m11-v2; do cp -p "$SRC/$f" "$T/$f"; done
mklist() {  # mklist <tree>: that tree's SHA256SUMS-q143k-v2 over its copies of the v2 files (the committed list also pins the logs and notes)
  ( cd "$1" && shasum -a 256 $(for f in $NEW_RB; do echo tools/claims-v3/q143k-runbook/$f; done) tools/claims-v3/e176/collect_e176_v2.sh \
      > tools/claims-v3/q143k-runbook/SHA256SUMS-q143k-v2 )
}
mklist "$T"
REAL_RSYNC=$(command -v rsync)
GDATE=$(command -v gdate)
[ -n "$GDATE" ] || { echo "GNU date (gdate) is needed for the stand-in box"; exit 2; }
cat > "$BIN/date" <<EOF
#!/bin/sh
exec "$GDATE" "\$@"
EOF
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
if [ "\$cmd" = true ]; then exit 0; fi
HOME="\${Q_BOX:-$B}/\$host" bash -c "cd ~ && \$cmd"
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; a+=("\${Q_BOX:-$B}/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
chmod +x "$BIN/ssh" "$BIN/rsync" "$BIN/date"
export PATH="$BIN:$PATH"
: > "$S/calls.log"
R=$T/tools/claims-v3/q143k-runbook

step "A2. the dry listing with step 22 v2: every step exits 0, no ssh or rsync call"
( export RB_REPO="$T" RB_OUT="$S/out" RB_LOCK="$S/lock.txt"; bash "$R/list_steps_q143k_v2.sh" "$S/dry-out" > "$S/dry-listing-v2.txt" 2>&1 ); rc=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing-v2.txt"; echo "calls: $n"
ok "$rc.$n" "0.0" "dry listing with step 22 v2"

# the window for the collections
export RB_REPO="$T" RB_OUT="$S/out" RB_LOCK="$S/lock.txt"
: > "$RB_LOCK"
bash "$R/s02_window_q143k.sh" "$(date +%F)" 23:58 23:59 > "$S/window.txt" 2>&1
cd "$T" || exit 2
# the stand-in collector v2: what collect_e176_v2.sh writes, from a synthetic session (MODE names the fault)
cat > "$S/collect_stub_v2.sh" <<EOF
#!/bin/bash
D=\$1
mkdir -p "\$D/ccheck" "\$D/logs"
f=""
case "\${MODE:-}" in
  noclog) f=no-measured-clog ;; short) f=short-measured ;; smokenolog) f=no-smoke-clog ;; smokenolaunch) f=smoke-nolaunch ;;
  orphan) f=orphan ;; nolaunch) f=measured-nolaunch ;; emptyclog) f=empty-measured-clog ;; norecords) f=no-records ;;
esac
/usr/bin/python3 -B "$DATA" synth "\$D" \$f > /dev/null || exit 9
[ "\${MODE:-}" = copy ] && echo "rsync e176 rc=23"
[ "\${MODE:-}" = crash ] && rm -f "\$D/ccheck/ccheck-all.json"
[ "\${MODE:-}" != crash ] && echo "ccheck rc=0"
[ "\${MODE:-}" = stale ] && touch -t 202611050001 "\$D/ccheck/ccheck-all.json"
echo "# M11 on aifoundry3 (stand-in)" > "\$D/scored-m11.md"; echo '{}' > "\$D/scored-m11.json"; echo '{"stage": 1}' > "\$D/scored-m11-lines.jsonl"
[ "\${MODE:-}" = path ] && echo "a desk path: \$PWD/build/e176" >> "\$D/scored-m11.md"
if [ "\${MODE:-}" = score ]; then echo "score rc=1"; else echo "score rc=0"; fi
EOF
chmod +x "$S/collect_stub_v2.sh"
cn() {  # cn <case> <want rc> <want line> <mode>
  local c=$1 want=$2 line=$3 mode=$4
  rm -rf "${T:?}/docs"
  MODE=$mode RB_DESKTEST=1 Q143K_COLLECT_E176="$S/collect_stub_v2.sh" bash "$R/s22_collect_q143k_v2.sh" > "$S/$c.txt" 2>&1; rc=$?
  grep -E "$line|STOP" "$S/$c.txt" | head -n 3 | sed "s#$S#<scratch>#g" | cut -c1-260
  local seen=0; grep -qE "$line" "$S/$c.txt" && seen=1
  ok "$rc.$seen" "$want.1" "$c"
}
step "C1. a good collection (the check finished and covers every launch the marks record; the scorer rc 0)"
cn C1 0 'E176 collected and scored' ""
step "C2. no check file (the check of C crashed)"
cn C2 14 'CCHECK-MISSING' crash
step "C3. a failed copy inside the collector"
cn C3 14 'a copy inside collect_e176_v2.sh failed' copy
step "C4. the scorer not rc 0"
cn C4 14 "scorer did not read rc 0" score
step "C5. a check file from an earlier try (backdated)"
cn C5 14 'CCHECK-STALE' stale
step "C6. a desk path in what the collector wrote"
cn C6 16 'HIT ' path
step "C7. the stand-in named without RB_DESKTEST=1"
Q143K_COLLECT_E176="$S/collect_stub_v2.sh" bash "$R/s22_collect_q143k_v2.sh" > "$S/C7.txt" 2>&1; rc=$?
grep -m1 STOP "$S/C7.txt" | cut -c1-200; ok "$rc" 10 "exit 10"
step "C8. the measured pass carries no C log, the smoke's is checked (the verifier's M1)"
cn C8 14 'MISSING-CLOG p17620' noclog
step "C9. a short check: the measured pass's last process one launch short"
cn C9 14 'COUNT-SHORT p17620' short
step "C10. the smoke's marks show launches and it carries no C log"
cn C10 14 'MISSING-CLOG p17601' smokenolog
step "C11. the smoke ran no launch and carries no C log (not required)"
cn C11 0 'NOT-REQUIRED p17601' smokenolaunch
step "C12. a checked launch outside every launch mark's window"
cn C12 14 'ORPHAN p17620' orphan
step "C13. the measured pass ran no launch (no hold ran)"
cn C13 14 'NO-LAUNCH p17620' nolaunch
step "C14. the measured pass's C log empty"
cn C14 14 'MISSING-CLOG p17620' emptyclog
step "C15. a launch mark without records"
cn C15 14 'COUNT-UNREAD p17620' norecords
step "C16. a v2 file that differs from its list: 16, before any box call"
cp -p "$R/cclaunch_q143k.py" "$S/cclaunch.keep"; echo "# a change" >> "$R/cclaunch_q143k.py"
: > "$S/calls.log"
RB_DESKTEST=1 Q143K_COLLECT_E176="$S/collect_stub_v2.sh" bash "$R/s22_collect_q143k_v2.sh" > "$S/C16.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); grep -m1 STOP "$S/C16.txt" | sed "s#$S#<scratch>#g" | cut -c1-220
seen=0; grep -q 'STOP: a file of tools/claims-v3/q143k-runbook/SHA256SUMS-q143k-v2 differs' "$S/C16.txt" && seen=1
cp -p "$S/cclaunch.keep" "$R/cclaunch_q143k.py"
ok "$rc.$n.$seen" "16.0.1" "exit 16, no box call, the list named"
cd "$S" || exit 2

# ---- the gate on committed sessions, renamed to E176's passes
uc() {  # uc <case> <want rc> <want lines (grep -E, each must match)> <source> <smoke rel> <measured rel> [fault ...]
  local c=$1 want=$2 lines=$3 src=$4 s=$5 m=$6; shift 6
  /usr/bin/python3 -B "$DATA" committed "$src" "$s" "$m" "$S/u/$c" "$@" > /dev/null || { echo "data maker failed"; fail=1; return; }
  /usr/bin/python3 -B "$SRC/tools/claims-v3/q143k-runbook/cclaunch_q143k.py" "$S/u/$c" > "$S/u-$c.txt" 2>&1; local rc=$?
  grep -E '^(COUNT|MISSING|cclaunch)' "$S/u-$c.txt" | cut -c1-230
  local seen=1 l
  IFS='|' read -r -a want_lines <<< "$lines"
  for l in "${want_lines[@]}"; do grep -qE "$l" "$S/u-$c.txt" || seen=0; done
  ok "$rc.$seen" "$want.1" "$c"
}
step "U1. E166's committed session (4 Nov), renamed"
uc U1 0 'COUNT-OK p17620: 6644 checked launches in 493 processes|COUNT-OK p17601: 48 checked launches in 6 processes' \
  "$E166" aifoundry3/e166-smoke/p16601 aifoundry3/e166/p16620
step "U2. E154's committed session (3 Nov), renamed"
uc U2 0 'COUNT-OK p17620: 6288 checked launches in 474 processes|COUNT-OK p17601: 58 checked launches in 7 processes' \
  "$E154" aifoundry3/e154-smoke/p15401 aifoundry3/e154/p15420
step "U3. E166's without the measured pass's C log"
uc U3 4 'MISSING-CLOG p17620' "$E166" aifoundry3/e166-smoke/p16601 aifoundry3/e166/p16620 no-measured-clog
step "U4. E166's, the check one launch short"
uc U4 4 'COUNT-SHORT p17620' "$E166" aifoundry3/e166-smoke/p16601 aifoundry3/e166/p16620 short-measured

# ---- the real collector v2 end to end, on a stand-in box with E154's committed passes
T2=$S/tree2; B2=$S/box2
mkdir -p "$T2/docs/reports/data" "$S/out2" "$S/cache"
git -C "$SRC" archive HEAD tools workloads rtl-sim/fma_toggle_v2 | tar -x -C "$T2"   # ccheck's engine source and M11's one rtl-sim pin are there
for p in q143k-runbook e176; do cp -p "$SRC/tools/claims-v3/$p"/*.* "$T2/tools/claims-v3/$p/" 2>/dev/null; done
mklist "$T2"
for d in "$SRC"/docs/reports/data/*; do ln -s "$d" "$T2/docs/reports/data/$(basename "$d")"; done
DAY=$(date +%F)
DD=$T2/docs/reports/data/$DAY-e176-m11-holds-aifoundry3
[ -e "$DD" ] && { echo "refused: $DD exists (a link to the lab clone's E176 data?)"; exit 2; }
e2e() {  # e2e <case> <want rc> <want line> [fault ...]
  local c=$1 want=$2 line=$3; shift 3
  rm -rf "${DD:?}" "${B2:?}"
  /usr/bin/python3 -B "$DATA" box "$E154" aifoundry3/e154-smoke/p15401 aifoundry3/e154/p15420 "$B2" "$@" | sed "s#$S#<scratch>#g"
  : > "$S/calls.log"
  ( export RB_REPO="$T2" RB_OUT="$S/out2" RB_LOCK="$S/lock2.txt" Q_BOX="$B2" CCHECK_CACHE="$S/cache"
    unset RB_DESKTEST Q143K_COLLECT_E176
    cd "$T2" && bash tools/claims-v3/q143k-runbook/s02_window_q143k.sh "$DAY" 23:58 23:59 > /dev/null 2>&1
    cd "$T2" && bash tools/claims-v3/q143k-runbook/s22_collect_q143k_v2.sh ) > "$S/$c.txt" 2>&1; local rc=$?
  grep -E "$line|STOP|COUNT-|MISSING-|CCHECK-DONE|score rc|ccheck rc" "$S/$c.txt" | sed "s#$S#<scratch>#g" | cut -c1-240 | head -n 8
  local seen=0; grep -qE "$line" "$S/$c.txt" && seen=1
  echo "stand-in calls: $(grep -c '^rsync' "$S/calls.log") rsync, $(grep -c '^ssh' "$S/calls.log") ssh (the stand-in box only)"
  ok "$rc.$seen" "$want.1" "$c"
}
step "E1. the real collector v2: both C logs on the box"
e2e E1 0 'E176 collected and scored'
if [ -f "$DD/scored-m11.json" ]; then
  /usr/bin/python3 -B - "$DD" <<'PY'
import json, os, sys
d = sys.argv[1]
j = json.load(open(os.path.join(d, "scored-m11.json")))
st = [json.loads(x)["stage"] for x in open(os.path.join(d, "scored-m11-lines.jsonl")) if x.strip()]
s = list(j["sessions"].values())[0]
a = j["aifoundry3"]
print(f"   scored-m11.json: scorer {j['scorer']}; holds scored {sum(1 for h in s['holds'].values() if h.get('scored'))} of 5; "
      f"HM-CAL-I8 {a['HM_CAL_I8']['verdict']}; HM-I8-AG {a['HM_I8_AG']['verdict']}; M11 carries: {a['M11_carries']}; label: {j['label'][:9]}; "
      f"lines file stages {st}")
PY
fi
step "E2. the real collector v2: the measured pass's C log absent on the box"
e2e E2 14 'MISSING-CLOG p17620' no-measured-clog
rm -rf "${DD:?}"

echo
echo "network calls by the stand-ins: to the stand-in boxes only; elapsed $(( $(date +%s) - t_begin )) s"
echo "SELFTEST-RUNBOOK-Q143K-V2 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
exit "$fail"
