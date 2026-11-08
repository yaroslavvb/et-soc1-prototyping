#!/usr/bin/env bash
# E185 (M11's session 3): the desk test of E185's runbook, with stand-in ssh, rsync and pgrep first on PATH serving a stand-in box (a local
# directory laid out like aifoundry3's ~/aifoundry); no lab box is reached. A date shim runs GNU date. Every tree is a scratch copy under
# <scratch dir>, never the lab clone. It is E181's selftest_rb_e181_v2.sh's form (dc35a540), with the cases E185's runbook adds:
#   A    the dry listing: every step exits 0, no ssh or rsync call, the look listed before the day's post;
#   K1   step 2 with no window: 10 before any call;  K2  step 2 with a window written on another day: 10 (E182's lesson);
#   P1   a file the runbook pins changed (v3.1's rb_run.py): 16 before any call;
#   O    ours_live's pattern names E185's, E181's, E182's, E183's and E184's processes, and none of the runbook's own step or helper names;
#   J1   step 11 beside a running dry job of the runbook (jobs_live): refused (10) before any launch;
#   J2   step 10's dry job beside a card session of ours (ours_live, through the stand-in pgrep): JOB-REFUSED, nothing started (14);
#   R1   the rest rule: E185's own T0-named real session ended 25 minutes ago: refused (10);
#   R2   E184's T0-named session log ended 30 minutes ago: refused (10);
#   R3   a dry T0 directory 5 minutes old and E181's real end 3 h ago: launched (0), rest 180 minutes, the T0 written for step 20;
#   W1   step 20: the session log says "session end" but no MANIFEST.sha256 was written, and no session runs: RUN-GONE (14);
#   W2   the manifest written: RUN-ENDED (0);  W3  "pass 18520 rc=6" in the log: the stop line named, ended (0);
#   C1   the real collector on a stand-in box holding E181's committed passes as E185's, its T0 directory and manifest: COPY-BACK EXACT;
#        the host windows picked by T0 (the start window 100 s before T0, not the one 4,000 s before; the end window after the session);
#        each C log moved into ccheck/ (no second copy in a pass directory);
#   C2   one byte appended on the box after the manifest: COPY-BACK DIFFERS (4);  C3  a stray file: COPY-BACK EXTRA (4);
#   C4   no manifest: COPY-BACK NO-MANIFEST (4);
#   G1   step 22 on C2's box: 16 on the copy-back, nothing scored;  G2  the session's last block says the smoke failed: 16 SMOKE-STOPPED;
#   E1   step 22 end to end on C1's box: the gates, the check of C, the scrub, then M11's scorer v5: 0, A10's reading SCORED, E185's rules
#        SCORED on the stand-in's holds (E181's: n 5), no staging file;
#   Z    nothing the test started is left running.
#
#   bash tools/claims-v3/e185/rb/selftest_rb_e185.sh <scratch dir> > <log>
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
mkdir -p "$S"
S=$(cd "$S" && pwd -P)
rm -rf "${S:?}/tree" "${S:?}/box" "${S:?}/bin" "${S:?}/out" "${S:?}/dry-out" "${S:?}/cache"
E181D=$SRC/docs/reports/data/2026-11-06-e181-m11-session2-aifoundry3
fail=0
ok() { if [ "$1" = "$2" ]; then echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
clean() { sed "s#$S#<scratch>#g" | cut -c1-240; }
t_begin=$(date +%s)

# ---- the scratch tree: the committed tools at HEAD, then E185's and M11's new files over them, the data dirs linked read-only
T=$S/tree; B=$S/box; BIN=$S/bin
mkdir -p "$T/docs/reports/data" "$B/aifoundry3/aifoundry" "$BIN" "$S/out" "$S/cache"
git -C "$SRC" archive HEAD tools workloads rtl-sim/fma_toggle_v2 | tar -x -C "$T"
for p in e185 e185/rb m11; do mkdir -p "$T/tools/claims-v3/$p"; cp -p "$SRC/tools/claims-v3/$p"/*.* "$T/tools/claims-v3/$p/" 2>/dev/null; done
for d in "$SRC"/docs/reports/data/*; do ln -s "$d" "$T/docs/reports/data/$(basename "$d")"; done
mklist() {  # the lists step 22 checks first, over the tree's own copies (the kit's lists are written after this test)
  ( cd "$T" && E=tools/claims-v3/e185 &&
    shasum -a 256 tools/claims-v3/m11/score_m11_v5.py > tools/claims-v3/m11/SHA256SUMS-score-m11-v5 &&
    shasum -a 256 $E/*.sh $E/*.py > $E/SHA256SUMS-e185-kit &&
    shasum -a 256 $E/rb/*.sh $E/rb/*.py > $E/rb/SHA256SUMS-rb-e185 )
}
mklist
REAL_RSYNC=$(command -v rsync)
REAL_PGREP=$(command -v pgrep)
GDATE=$(command -v gdate)
[ -n "$GDATE" ] || { echo "GNU date (gdate) is needed for the stand-in box"; exit 2; }
printf '#!/bin/sh\nexec "%s" "$@"\n' "$GDATE" > "$BIN/date"
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
[ "\$cmd" = true ] && exit 0
cat | HOME="${B}/\$host" bash -c "cd ~ && \$cmd"
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; a+=("${B}/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
cat > "$BIN/pgrep" <<EOF
#!/bin/bash
# the stand-in pgrep: with Q_OURS=1 a call that looks for our sessions (-f with a session_e pattern) names this test's own shell
if [ "\${Q_OURS:-}" = 1 ]; then case "\$*" in *session_e*) echo "\${Q_OURS_PID:-\$\$}"; exit 0 ;; esac; fi
exec "$REAL_PGREP" "\$@"
EOF
chmod +x "$BIN/ssh" "$BIN/rsync" "$BIN/date" "$BIN/pgrep"
export PATH="$BIN:$PATH" RB_REPO="$T" RB_OUT="$S/out" RB_LOCK="$S/lock.txt" CCHECK_CACHE="$S/cache"
: > "$S/calls.log"; : > "$RB_LOCK"
R=$T/tools/claims-v3/e185/rb
A3=$B/aifoundry3/aifoundry
DAY=$(date +%F)
cd "$T" || exit 2
win() { bash "$R/s02_window_e185.sh" "$DAY" 23:58 23:59 > /dev/null 2>&1; }

step "A. the dry listing: every step exits 0, no ssh or rsync call, the look before the post"
: > "$S/calls.log"
bash "$R/list_steps_e185.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing.txt"
lk=$(grep -nE 's05_look_e185.sh aifoundry3$|step 6: the day' "$S/dry-listing.txt" | cut -d: -f1 | tr '\n' ' ')
set -- $lk; order=$([ "${1:-0}" -lt "${2:-0}" ] && echo look-first || echo POST-FIRST)
echo "calls: $n; $order"
ok "$rc.$n.$order" "0.0.look-first" "the dry listing"

step "K. step 2 without the go's window: refused before any call"
rm -f "$RB_OUT/window.env"; : > "$S/calls.log"
bash "$R/s03_desk_e185.sh" > "$S/K1.txt" 2>&1; k1=$?; n1=$(grep -c . "$S/calls.log"); tail -n 1 "$S/K1.txt" | clean
win; touch -t "$(date -d '1 day ago' '+%Y%m%d%H%M')" "$RB_OUT/window.env"; : > "$S/calls.log"
bash "$R/s03_desk_e185.sh" > "$S/K2.txt" 2>&1; k2=$?; n2=$(grep -c . "$S/calls.log"); tail -n 1 "$S/K2.txt" | clean
ok "$k1.$n1.$k2.$n2" "10.0.10.0" "no window 10; a window from another day 10; no call either time"

step "P1. a file the runbook pins changed (v3.1's rb_run.py): 16 before any call"
cp -p "$T/tools/claims-v3/q141k-runbook/v3.1/rb_run.py" "$S/rb_run.keep"; echo "# a change" >> "$T/tools/claims-v3/q141k-runbook/v3.1/rb_run.py"
: > "$S/calls.log"
bash "$R/s05_look_e185.sh" aifoundry3 > "$S/P1.txt" 2>&1; p1=$?; n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/P1.txt" | clean
cp -p "$S/rb_run.keep" "$T/tools/claims-v3/q141k-runbook/v3.1/rb_run.py"
ok "$p1.$n" "16.0" "a pinned file changed: 16, no call"

step "O. ours_live's pattern names our sessions on this card, and none of the runbook's own names"
pat=$(grep -o "pgrep -u \"\$(id -u)\" -f '[^']*'" "$R/rb_common_e185.sh" | sed -E "s/^pgrep -u \"\\\$\(id -u\)\" -f '//; s/'$//")
hits=0
for c in "bash tools/claims-v3/e185/session_e185.sh" "bash tools/claims-v3/e185/block_e185.sh 18520" "python3 tools/claims-v3/e185/run_e185.py x" \
         "bash tools/claims-v3/e181/session_e181.sh" "python3 tools/claims-v3/e181/run_e181.py x" "bash tools/claims-v3/e182/session_e182.sh" \
         "python3 tools/claims-v3/e182/run_e182t.py x" "bash tools/claims-v3/e182/block_e182.sh 1" "bash tools/claims-v3/e184/session_e184b_v2.sh" \
         "bash tools/claims-v3/e184/block_e184s_v2.sh 1" "bash tools/claims-v3/e184/queue_e184_v2.sh" "python3 tools/claims-v3/e184/run_e184_v2.py x" \
         "bash tools/claims-v3/e183/session_e183.sh" "python3 tools/claims-v3/e183/run_e183.py x"; do
  printf '%s\n' "$c" | grep -qE "$pat" && hits=$((hits + 1))
done
miss=0
for c in "vim notes.txt" "bash tools/claims-v3/e185/rb/s11_a3_launch_e185.sh" "bash tools/claims-v3/e185/rb/s12_a3_host_e185.sh start" \
         "bash tools/claims-v3/e185/rb/s22_collect_e185.sh" "bash tools/claims-v3/e185/rb/selftest_rb_e185.sh x" "bash tools/claims-v3/e185/collect_e185.sh d" \
         "bash tools/claims-v3/e185/score_e185.sh d" "python3 -B tools/claims-v3/m11/score_m11_v5.py score" "bash tools/claims-v3/e185/dry_intel_e185.sh x" \
         "python3 -B tools/claims-v3/e185/rb/scrub_all_e185.py d"; do
  printf '%s\n' "$c" | grep -qE "$pat" && miss=$((miss + 1))
done
echo "named: $hits of 14; the runbook's own commands matched: $miss of 10"
ok "$hits.$miss" "14.0" "ours_live's names"

# ---- the stand-in box for the launch and wait cases: the dry job ended rc 0 today
newbox() { rm -rf "${B:?}"; mkdir -p "$A3/build/q141k/jobs" "$A3/build/e185"; echo 0 > "$A3/build/q141k/jobs/a3-dry-e185.rc"; echo "dry" > "$A3/build/q141k/jobs/a3-dry-e185.sh"; }
gdl() { date -d "$1" '+%F %T %Z'; }

step "J1. step 11 beside a running dry job of the runbook (jobs_live): refused before any launch"
newbox; win; echo $$ > "$A3/build/q141k/jobs/a3-other.pid"
bash "$R/s11_a3_launch_e185.sh" > "$S/J1.txt" 2>&1; j1=$?; grep -m1 -E 'REFUSED|STOP' "$S/J1.txt" | clean
l=$([ -e "$A3/build/q141k/e185.t0" ] && echo launched || echo none)
ok "$j1.$l" "10.none" "a dry pass still runs: refused, nothing launched"

step "J2. step 10's dry job beside a card session of ours (ours_live): JOB-REFUSED, nothing started"
newbox; win
Q_OURS=1 Q_OURS_PID=$$ bash "$R/s10_a3_dry_e185.sh" start > "$S/J2.txt" 2>&1; j2=$?; grep -m1 -E 'JOB-REFUSED|STOP' "$S/J2.txt" | clean
st=$([ -e "$A3/build/q141k/jobs/a3-dry-e185.pid" ] && echo started || echo none)
ok "$j2.$st" "14.none" "a session of ours runs: the dry job refused"

step "R1. the rest rule: E185's own T0-named real session ended 25 minutes ago"
newbox; win; mkdir -p "$A3/build/e185/T1000"
{ echo "$(gdl '50 min ago') session start (T0 x)"; echo "$(gdl '25 min ago') session end"; } > "$A3/build/e185/T1000/session.log"
bash "$R/s11_a3_launch_e185.sh" > "$S/R1.txt" 2>&1; r1=$?; grep -m1 -E 'REFUSED|LAUNCHED' "$S/R1.txt" | clean
ok "$r1" 10 "25 minutes since E185's session end: refused"

step "R2. the rest rule: E184's T0-named session log ended 30 minutes ago"
newbox; win; mkdir -p "$A3/build/e184"
{ echo "$(gdl '90 min ago') session start (arm s)"; echo "$(gdl '30 min ago') session end"; } > "$A3/build/e184/session-s-t1234.log"
bash "$R/s11_a3_launch_e185.sh" > "$S/R2.txt" 2>&1; r2=$?; grep -m1 -E 'REFUSED|LAUNCHED' "$S/R2.txt" | clean
ok "$r2" 10 "30 minutes since E184's session end: refused"

step "R3. a dry T0 directory 5 minutes old, E181's real end 3 h ago: launched, its T0 written"
newbox; win; mkdir -p "$A3/build/e185/T2000-dry" "$A3/build/e181"
{ echo "$(gdl '10 min ago') session start (T0 x) DRY"; echo "$(gdl '5 min ago') DRY session end"; } > "$A3/build/e185/T2000-dry/session-dry.log"
{ echo "$(gdl '4 hours ago') session start (T0 y)"; echo "$(gdl '3 hours ago') session end"; } > "$A3/build/e181/session.log"
bash "$R/s11_a3_launch_e185.sh" --after-noon > "$S/R3.txt" 2>&1; r3=$?; grep -E '^rest:|LAUNCHED' "$S/R3.txt" | clean | head -n 3
t0=$(cat "$A3/build/q141k/e185.t0" 2>/dev/null); rest=$(grep -c 'rest: 1[78][0-9] minutes since E181' "$S/R3.txt")
ok "$r3.$([ -n "$t0" ] && echo t0 || echo none).$rest" "0.t0.1" "launched, about 180 minutes of rest, the T0 written"

step "W. step 20 on the T0 directory: the manifest is the session's last act"
newbox; win; T0=$(date +%s); echo "$T0" > "$A3/build/q141k/e185.t0"; mkdir -p "$A3/build/e185/T$T0"
{ echo "$(gdl '100 min ago') session start (T0 $T0)"; echo "$(gdl '1 min ago') session end"; } > "$A3/build/e185/T$T0/session.log"
RB_WAIT_LOOP_S=5 bash "$R/s20_wait_e185.sh" > "$S/W1.txt" 2>&1; w1=$?; grep -m1 -E 'RUN-|STOP' "$S/W1.txt" | clean
echo "x  build/e185/T$T0/session.log" > "$A3/build/e185/T$T0/MANIFEST.sha256"
RB_WAIT_LOOP_S=5 bash "$R/s20_wait_e185.sh" > "$S/W2.txt" 2>&1; w2=$?; grep -m1 -E 'has ended|STOP' "$S/W2.txt" | clean
/usr/bin/python3 - "$A3/build/e185/T$T0/session.log" <<'PY'
import sys
p = sys.argv[1]
s = open(p).read().splitlines()
s.insert(len(s) - 1, s[-1].rsplit(" ", 2)[0] + " pass 18520 rc=6: a stop line ended the pass (E171's stops); the holds after it did not run")
open(p, "w").write("\n".join(s) + "\n")
PY
RB_WAIT_LOOP_S=5 bash "$R/s20_wait_e185.sh" > "$S/W3.txt" 2>&1; w3=$?; grep -m2 -E 'stop line|has ended' "$S/W3.txt" | clean
sl=$(grep -c 'a stop line ended the measured pass' "$S/W3.txt")
ok "$w1.$w2.$w3.$sl" "14.0.0.1" "no manifest and no session: RUN-GONE 14; the manifest: ended 0; a stop line named, ended 0"

# ---- the collector and step 22 on a stand-in box holding E181's committed passes as E185's
OWN=$(grep -ohaE '[^/ "]*/aifoundry/tools' "$E181D/aifoundry3/e181/p18120/runs.jsonl" | sort -u | head -n 1 | cut -d/ -f1)
mkbox() {  # mkbox [fault ...]
  rm -rf "${B:?}"; mkdir -p "$A3/build/e185/host"
  T0=1794000000
  /usr/bin/python3 -B "$R/selftest_data_e185.py" box "$E181D" aifoundry3/e181-smoke/p18101 aifoundry3/e181/p18120 "$B" "$T0" "$@" | clean
  for w in "start $((T0 - 100))" "start $((T0 - 4000))"; do set -- $w; echo "$DAY 09:00:00 PST" > "$A3/build/e185/host/$1-$2.out"
    printf 'nvme:temp1_input       mean 38.850  min 38.85  max 38.85  n 13\n' >> "$A3/build/e185/host/$1-$2.out"; done
  touch "$A3/build/e185/host/x"
}
D=docs/reports/data/$DAY-e185-m11-session3-aifoundry3
coll() {  # coll <case>: the real collector, alone, on the stand-in box (its end window named after the manifest's copy)
  rm -rf "${T:?}/$D"
  ( cd "$T" && env PY=/usr/bin/python3 bash tools/claims-v3/e185/collect_e185.sh "$D" ) > "$S/$1.txt" 2>&1
}

step "C1. the real collector: the exact copy-back, the host windows by T0, one copy of each C log"
mkbox
END=$(date +%s); echo "end window" > "$A3/build/e185/host/end-$((END + 30)).out"
coll C1; c1=$?; grep -E 'COPY-BACK|host window|ccheck rc|T0 ' "$S/C1.txt" | clean
ex=$(grep -c '^COPY-BACK EXACT' "$S/C1.txt"); hs=$(grep -c "host window start: start-$((T0 - 100)).out" "$S/C1.txt"); he=$(grep -c "host window end: end-" "$S/C1.txt")
cl=$(ls "$T/$D"/aifoundry3/e185*/p*/c-log.jsonl 2>/dev/null | wc -l | tr -d ' '); gz=$(ls "$T/$D"/ccheck/c-log-p185*.jsonl.gz 2>/dev/null | wc -l | tr -d ' ')
ok "$c1.$ex.$hs.$he.$cl.$gz" "0.1.1.1.0.2" "EXACT; the start window 100 s before T0; an end window; no C log left in a pass directory, two in ccheck/"

step "C2-C4. the copy-back refuses what the session did not write"
mkbox differs; coll C2; c2=$?; grep -m1 '^COPY-BACK' "$S/C2.txt" | clean
mkbox extra; coll C3; c3=$?; grep -m1 '^COPY-BACK' "$S/C3.txt" | clean
mkbox no-manifest; coll C4; c4=$?; grep -m1 '^COPY-BACK' "$S/C4.txt" | clean
w=$(grep -c '^COPY-BACK DIFFERS' "$S/C2.txt").$(grep -c '^COPY-BACK EXTRA' "$S/C3.txt").$(grep -c '^COPY-BACK NO-MANIFEST' "$S/C4.txt")
ok "$c2.$c3.$c4.$w" "4.4.4.1.1.1" "DIFFERS, EXTRA and NO-MANIFEST each stop the collector (4)"

run22() {  # run22 <case>: step 22 on the stand-in box, the window first
  rm -rf "${T:?}/$D"; win
  [ -n "$OWN" ] && echo "$OWN" > "$RB_OUT/box-login-aifoundry3.txt"
  bash "$R/s22_collect_e185.sh" > "$S/$1.txt" 2>&1
}
nscored() { ls "$T/$D"/scored-m11* 2>/dev/null | wc -l | tr -d ' '; }

step "G1. step 22 on a box whose copy-back differs: 16, nothing scored"
mkbox differs; run22 G1; g1=$?; grep -m1 -E 'COPY-BACK|STOP' "$S/G1.txt" | clean
ok "$g1.$(nscored)" "16.0" "the copy-back gate"

step "G2. step 22: the session's last block says the smoke or its gate failed: 16 SMOKE-STOPPED, nothing scored"
mkbox smoke-stopped; run22 G2; g2=$?; grep -m1 -E 'SMOKE-STOPPED|STOP' "$S/G2.txt" | clean
ok "$g2.$(nscored)" "16.0" "SMOKE-STOPPED"

step "E1. step 22 end to end: the gates, the check of C, the scrub, then M11's scorer v5"
mkbox; END=$(date +%s); echo "end window" > "$A3/build/e185/host/end-$((END + 30)).out"
run22 E1; e1=$?; grep -E 'COPY-BACK|COUNT-OK|score rc|collected and scored|STOP' "$S/E1.txt" | clean | head -n 8
sc=$(/usr/bin/python3 -B - "$T/$D" <<'PY'
import json, os, sys
d = sys.argv[1]
try:
    j = json.load(open(os.path.join(d, "scored-m11.json")))
except (OSError, ValueError):
    print("none"); sys.exit(0)
e = j.get("E185", {})
st = [json.loads(x)["stage"] for x in open(os.path.join(d, "scored-m11-lines.jsonl")) if x.strip()]
left = any(x.endswith(".staging") for x in os.listdir(d))
print(f"{j['scorer'].split('/')[-1]}|{j['A10']['reads']}|{e.get('reads')}|{e.get('rules', {}).get('n_scored_by_all_three')}|"
      f"{e.get('rules', {}).get('E185-BEST', {}).get('verdict')}|{max(st)}|{left}")
PY
)
echo "scored: $sc"
ok "$e1.${sc%%|*}.$(echo "$sc" | cut -d'|' -f2-4).$(echo "$sc" | cut -d'|' -f6-7)" "0.score_m11_v5.py.SCORED|SCORED|5.9|False" \
  "collected and scored: A10 SCORED, E185's rules SCORED on 5 holds, lines stages to 9, no staging file"

step "Z. nothing the test started is left running"
left=$("$REAL_PGREP" -f "$S/(tree|box)" 2>/dev/null | grep -vc "^$$\$")
echo "processes under the scratch tree or box: $left"
ok "$left" 0 "nothing left running"

echo
echo "network calls by the stand-ins: to the stand-in box only ($(grep -c '^ssh' "$S/calls.log") ssh, $(grep -c '^rsync' "$S/calls.log") rsync in the last cases); elapsed $(( $(date +%s) - t_begin )) s"
echo "SELFTEST-RB-E185 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
exit "$fail"
