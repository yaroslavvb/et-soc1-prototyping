#!/usr/bin/env bash
# E185 (M11's session 3): the desk test of the kit's dated note 1 (KIT.md.dated-note-1.md): step 2 v2, step 10 v2, step 14 v2 and the
# collector v2, with stand-in ssh, rsync and pgrep first on PATH serving a stand-in box (a local directory laid out like aifoundry3's
# ~/aifoundry); no lab box is reached. A date shim runs GNU date. Every tree is a scratch copy under <scratch dir>, never the lab clone.
# It is selftest_rb_e185.sh's form (460c352f, which stays as committed), with these cases:
#   A2   the dry listing v2: every step exits 0, no ssh or rsync call, the look listed before the day's post;
#   K    step 2 v2 with no window: 10 before any call; with a window written on another day: 10;
#   R4   step 10's rest rule: E183's T0-named log (build/e183/session-t<T0>.log, "session end (T0 <epoch>)") ended 30 minutes ago:
#        v1 launches (the verifier's fault 6, shown), v2 refuses (10);
#   R5   E184 v2's T0-named log ended 3 h ago in the "(T0 <epoch>)" form: v2 launches, its rest about 180 minutes counted from that line
#        as a session end (no "note:" line); v1 prints the note (a block without its end);
#   R1-R3 v1's rest cases, under v1 and v2, with --after-noon so that the rest rule itself is reached (v1's committed desk test ran
#        them after 12:00 PST without it, so the noon gate refused R1 and R2 first): E185's own end 25 minutes ago (10, the rest rule's
#        words); E184's 30 minutes ago (10, the same); a dry T0 directory and E181's real end 3 h ago (launched);
#   L1   a later try's box: the first smoke moved aside as p18501.try1 and a measured pass's earlier attempt (p18520.attempt-<epoch>)
#        beside this session's: the collector v1 reads COPY-BACK EXTRA (4; the verifier's major fault 1, shown); v2 reads COPY-BACK EXACT
#        and names both as left on the box;
#   L2   a second collection into the data directory L1's left: v2 refuses (3) before any box call;
#   L3   the presence read fails (the stand-in ssh exits 255 on it): v2 names the failed read ("rsync ... rc=255") and stops (4), nothing
#        scored;
#   C2-C4 v2 on v1's faults: one byte appended after the manifest (DIFFERS, 4); a stray file inside the measured pass (EXTRA, 4); no
#        manifest (NO-MANIFEST, 4);
#   E2   step 14 v2 end to end on the later try's box: the lists, the collector v2 (EXACT), the gates, the check of C, the scrub, then
#        M11's scorer v5: 0, A10's reading SCORED, E185's rules SCORED on the stand-in's holds (E181's: n 5), no staging file, and the
#        "left on the box" line in the runbook's log;
#   G1   step 14 v2 again into E2's data directory: 16 on the collector's refusal, no rsync call;
#   S1   step 14 v2 with a stand-in scorer that exits 1 (RB_DESKTEST=1): 14, its message naming the data directory's removal first;
#   Z    nothing the test started is left running.
#
#   bash tools/claims-v3/e185/rb/selftest_rb_e185_v2.sh <scratch dir> > <log>
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

# ---- the scratch tree: the committed tools at HEAD, then E185's and M11's working files over them, the data dirs linked read-only
T=$S/tree; B=$S/box; BIN=$S/bin
mkdir -p "$T/docs/reports/data" "$B/aifoundry3/aifoundry" "$BIN" "$S/out" "$S/cache"
git -C "$SRC" archive HEAD tools workloads rtl-sim/fma_toggle_v2 | tar -x -C "$T"
for p in e185 e185/rb m11; do mkdir -p "$T/tools/claims-v3/$p"; cp -p "$SRC/tools/claims-v3/$p"/*.* "$T/tools/claims-v3/$p/" 2>/dev/null; done
for d in "$SRC"/docs/reports/data/*; do ln -s "$d" "$T/docs/reports/data/$(basename "$d")"; done
mklist() {  # the lists step 14 v2 checks first, over the tree's own copies (the kit note's list is written after this test)
  ( cd "$T" && E=tools/claims-v3/e185 &&
    shasum -a 256 tools/claims-v3/m11/score_m11_v5.py > tools/claims-v3/m11/SHA256SUMS-score-m11-v5 &&
    shasum -a 256 $E/*.sh $E/*.py > $E/SHA256SUMS-e185-kit &&
    shasum -a 256 $E/rb/*.sh $E/rb/*.py > $E/rb/SHA256SUMS-rb-e185 &&
    shasum -a 256 $E/collect_e185_v2.sh $E/rb/s03_desk_e185_v2.sh $E/rb/s11_a3_launch_e185_v2.sh $E/rb/s22_collect_e185_v2.sh \
      $E/rb/list_steps_e185_v2.sh > $E/SHA256SUMS-e185-kit-note1 )
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
if [ -n "\${SSH_FAIL_ON:-}" ]; then case "\$cmd" in *"\$SSH_FAIL_ON"*) cat > /dev/null; echo "ssh: connect to host \$host: stand-in failure" >&2; exit 255 ;; esac; fi
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
if [ "\${Q_OURS:-}" = 1 ]; then case "\$*" in *session_e*) echo "\${Q_OURS_PID:-\$\$}"; exit 0 ;; esac; fi
exec "$REAL_PGREP" "\$@"
EOF
printf '#!/bin/bash\necho "stand-in scorer: exits 1 before writing anything"\necho "score rc=1"\nexit 1\n' > "$S/fake_score.sh"
chmod +x "$BIN/ssh" "$BIN/rsync" "$BIN/date" "$BIN/pgrep" "$S/fake_score.sh"
export PATH="$BIN:$PATH" RB_REPO="$T" RB_OUT="$S/out" RB_LOCK="$S/lock.txt" CCHECK_CACHE="$S/cache"
: > "$S/calls.log"; : > "$RB_LOCK"
R=$T/tools/claims-v3/e185/rb
A3=$B/aifoundry3/aifoundry
DAY=$(date +%F)
WDAY=$(date -d tomorrow +%F)   # the stand-in window is tomorrow's, so that the launch cases' 105 minutes fit at any hour of the run
cd "$T" || exit 2
win() { bash "$R/s02_window_e185.sh" "$WDAY" 23:58 23:59 > /dev/null 2>&1; }

step "A2. the dry listing v2: every step exits 0, no ssh or rsync call, the look before the post"
: > "$S/calls.log"
bash "$R/list_steps_e185_v2.sh" "$S/dry-out" > "$S/dry-listing-v2.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing-v2.txt"
lk=$(grep -nE 's05_look_e185.sh aifoundry3$|step 6: the day' "$S/dry-listing-v2.txt" | cut -d: -f1 | tr '\n' ' ')
set -- $lk; order=$([ "${1:-0}" -lt "${2:-0}" ] && echo look-first || echo POST-FIRST)
v2=$(grep -cE '^################ s(03_desk|11_a3_launch|22_collect)_e185_v2\.sh' "$S/dry-listing-v2.txt")
echo "calls: $n; $order; v2 steps listed: $v2"
ok "$rc.$n.$order.$v2" "0.0.look-first.4" "the dry listing v2 (s03 v2, s11 v2 twice, s22 v2)"

step "K. step 2 v2 without the go's window: refused before any call"
rm -f "$RB_OUT/window.env"; : > "$S/calls.log"
bash "$R/s03_desk_e185_v2.sh" > "$S/K1.txt" 2>&1; k1=$?; n1=$(grep -c . "$S/calls.log"); tail -n 1 "$S/K1.txt" | clean
win; touch -t "$(date -d '1 day ago' '+%Y%m%d%H%M')" "$RB_OUT/window.env"; : > "$S/calls.log"
bash "$R/s03_desk_e185_v2.sh" > "$S/K2.txt" 2>&1; k2=$?; n2=$(grep -c . "$S/calls.log"); tail -n 1 "$S/K2.txt" | clean
ok "$k1.$n1.$k2.$n2" "10.0.10.0" "no window 10; a window from another day 10; no call either time"

# ---- the stand-in box for the launch cases: the dry job ended rc 0 today
newbox() { rm -rf "${B:?}"; mkdir -p "$A3/build/q141k/jobs" "$A3/build/e185"; echo 0 > "$A3/build/q141k/jobs/a3-dry-e185.rc"; echo "dry" > "$A3/build/q141k/jobs/a3-dry-e185.sh"; }
gdl() { date -d "$1" '+%F %T %Z'; }
launched() { [ -e "$A3/build/q141k/e185.t0" ] && echo launched || echo none; }

step "R4. the rest rule: E183's T0-named log, its session ended 30 minutes ago ('session end (T0 <epoch>)')"
newbox; win; mkdir -p "$A3/build/e183"
{ echo "$(gdl '60 min ago') session start (T0 1794000100 = 09:00:00 PST), kit v1; plan FULL"; echo "$(gdl '30 min ago') session end (T0 1794000100)"; } > "$A3/build/e183/session-t1794000100.log"
bash "$R/s11_a3_launch_e185.sh" --after-noon > "$S/R4v1.txt" 2>&1; r4a=$?; l1=$(launched); grep -m1 -E '^rest:|REFUSED|LAUNCHED' "$S/R4v1.txt" | clean
newbox; win; mkdir -p "$A3/build/e183"
{ echo "$(gdl '60 min ago') session start (T0 1794000100 = 09:00:00 PST), kit v1; plan FULL"; echo "$(gdl '30 min ago') session end (T0 1794000100)"; } > "$A3/build/e183/session-t1794000100.log"
touch -t "$(date -d '30 min ago' '+%Y%m%d%H%M')" "$A3/build/e183/session-t1794000100.log"
bash "$R/s11_a3_launch_e185_v2.sh" --after-noon > "$S/R4v2.txt" 2>&1; r4b=$?; l2=$(launched); grep -m1 -E 'REFUSED|LAUNCHED' "$S/R4v2.txt" | clean
ok "$r4a.$l1.$r4b.$l2" "0.launched.10.none" "v1 cannot see E183's log and launches; v2 refuses, 30 minutes after E183's session end"

step "R5. the rest rule: E184 v2's log ended 3 h ago in the '(T0 <epoch>)' form: a session end, with no note"
newbox; win; mkdir -p "$A3/build/e184"
{ echo "$(gdl '5 hours ago') session start (arm s, T0 1793990000)"; echo "$(gdl '3 hours ago') session end (T0 1793990000)"; } > "$A3/build/e184/session-s-t1793990000.log"
touch -t "$(date -d '3 hours ago' '+%Y%m%d%H%M')" "$A3/build/e184/session-s-t1793990000.log"
bash "$R/s11_a3_launch_e185.sh" --after-noon > "$S/R5v1.txt" 2>&1; r5a=$?; n5a=$(grep -c '^note: ' "$S/R5v1.txt")
newbox; win; mkdir -p "$A3/build/e184"
{ echo "$(gdl '5 hours ago') session start (arm s, T0 1793990000)"; echo "$(gdl '3 hours ago') session end (T0 1793990000)"; } > "$A3/build/e184/session-s-t1793990000.log"
touch -t "$(date -d '3 hours ago' '+%Y%m%d%H%M')" "$A3/build/e184/session-s-t1793990000.log"
bash "$R/s11_a3_launch_e185_v2.sh" --after-noon > "$S/R5v2.txt" 2>&1; r5b=$?; n5b=$(grep -c '^note: ' "$S/R5v2.txt")
grep -m1 '^rest:' "$S/R5v2.txt" | clean
rs=$(grep -c "^rest: 1[78][0-9] minutes since E184's session end" "$S/R5v2.txt")
ok "$r5a.$n5a.$r5b.$n5b.$rs" "0.1.0.0.1" "v1 notes a block without its end; v2 reads the (T0) form as the end: rest about 180 minutes, no note"

step "R1-R3. v1's rest cases, run after noon with --after-noon so the rest rule is reached (v1's committed desk test ran them without it, after 12:00 PST, so its R1 and R2 were refused by the noon gate first)"
rcase() {  # rcase <v1|v2> <case>: one rest case on a new box; prints the exit code and whether the refusal named the rest rule
  local f=s11_a3_launch_e185.sh; [ "$1" = v2 ] && f=s11_a3_launch_e185_v2.sh
  newbox; win
  case "$2" in
    R1) mkdir -p "$A3/build/e185/T1000"
        { echo "$(gdl '50 min ago') session start (T0 x)"; echo "$(gdl '25 min ago') session end"; } > "$A3/build/e185/T1000/session.log"
        touch -t "$(date -d '25 min ago' '+%Y%m%d%H%M')" "$A3/build/e185/T1000/session.log" ;;
    R2) mkdir -p "$A3/build/e184"
        { echo "$(gdl '90 min ago') session start (arm s)"; echo "$(gdl '30 min ago') session end"; } > "$A3/build/e184/session-s-t1234.log"
        touch -t "$(date -d '30 min ago' '+%Y%m%d%H%M')" "$A3/build/e184/session-s-t1234.log" ;;
    R3) mkdir -p "$A3/build/e185/T2000-dry" "$A3/build/e181"
        { echo "$(gdl '10 min ago') session start (T0 x) DRY"; echo "$(gdl '5 min ago') DRY session end"; } > "$A3/build/e185/T2000-dry/session-dry.log"
        { echo "$(gdl '4 hours ago') session start (T0 y)"; echo "$(gdl '3 hours ago') session end"; } > "$A3/build/e181/session.log"
        touch -t "$(date -d '3 hours ago' '+%Y%m%d%H%M')" "$A3/build/e181/session.log" ;;
  esac
  bash "$R/$f" --after-noon > "$S/$2$1.txt" 2>&1; local rc=$?
  local why=other
  grep -qE "REFUSED: [0-9]+ minutes since E18[45]'s session end" "$S/$2$1.txt" && why=rest
  grep -qE "^rest: 1[78][0-9] minutes since E181's session end" "$S/$2$1.txt" && [ -e "$A3/build/q141k/e185.t0" ] && why=launched
  echo "$rc:$why"
}
got=""
for v in v1 v2; do for c in R1 R2 R3; do got="$got $(rcase $v $c)"; done; done
echo "v1 R1 R2 R3, v2 R1 R2 R3:$got"
ok "$(echo $got)" "10:rest 10:rest 0:launched 10:rest 10:rest 0:launched" "both versions: E185's own end 25 min ago and E184's 30 min ago refused by the rest rule itself; a dry log skipped and E181 3 h ago launched"

# ---- the collector cases on a stand-in box holding E181's committed passes as E185's
OWN=$(grep -ohaE '[^/ "]*/aifoundry/tools' "$E181D/aifoundry3/e181/p18120/runs.jsonl" | sort -u | head -n 1 | cut -d/ -f1)
mkbox() {  # mkbox [fault ...]
  rm -rf "${B:?}"; mkdir -p "$A3/build/e185/host"
  T0=1794000000
  /usr/bin/python3 -B "$R/selftest_data_e185.py" box "$E181D" aifoundry3/e181-smoke/p18101 aifoundry3/e181/p18120 "$B" "$T0" "$@" | clean
  for w in "start $((T0 - 100))" "start $((T0 - 4000))"; do set -- $w; echo "$DAY 09:00:00 PST" > "$A3/build/e185/host/$1-$2.out"
    printf 'nvme:temp1_input       mean 38.850  min 38.85  max 38.85  n 13\n' >> "$A3/build/e185/host/$1-$2.out"; done
  echo "end window" > "$A3/build/e185/host/end-$(( $(date +%s) + 30 )).out"
}
latertry() {  # what s11 --later-try and the block leave beside this session's passes
  cp -Rp "$A3/build/claims-v3/aifoundry3/e185-smoke/p18501" "$A3/build/claims-v3/aifoundry3/e185-smoke/p18501.try1"
  mkdir -p "$A3/build/claims-v3/aifoundry3/e185/p18520.attempt-1793990000"
  echo '{"status":"gate"}' > "$A3/build/claims-v3/aifoundry3/e185/p18520.attempt-1793990000/block.json"
}
D=docs/reports/data/$WDAY-e185-m11-session3-aifoundry3          # step 14 names its data directory by the window's day
coll() {  # coll <case> <collector>: the collector alone on the stand-in box, into a fresh data directory unless KEEP=1
  [ "${KEEP:-}" = 1 ] || rm -rf "${T:?}/$D"
  ( cd "$T" && env PY=/usr/bin/python3 bash "tools/claims-v3/e185/$2" "$D" ) > "$S/$1.txt" 2>&1
}

step "L1. a later try's box: p18501.try1 and p18520.attempt-* beside this session's passes"
mkbox; latertry
coll L1v1 collect_e185.sh; l1a=$?; grep -m1 '^COPY-BACK' "$S/L1v1.txt" | cut -c1-160 | clean
mkbox; latertry
coll L1v2 collect_e185_v2.sh; l1b=$?; grep -E '^COPY-BACK|^left on the box' "$S/L1v2.txt" | clean
ex=$(grep -c '^COPY-BACK EXACT 37 files' "$S/L1v2.txt")
lf=$(grep -c '^left on the box .*e185-smoke/p18501.try1 e185/p18520.attempt-1793990000$' "$S/L1v2.txt")
tr1=$(ls -d "$T/$D"/aifoundry3/e185-smoke/p18501.try1 "$T/$D"/aifoundry3/e185/p18520.attempt-* 2>/dev/null | wc -l | tr -d ' ')
ok "$l1a.$l1b.$ex.$lf.$tr1" "4.0.1.1.0" "v1 EXTRA (4); v2 EXACT 37 files, both earlier entries named and left on the box, none copied"

step "L2. a second collection into the data directory L1 left: refused before any box call"
: > "$S/calls.log"
KEEP=1 coll L2 collect_e185_v2.sh; l2=$?; grep -m1 '^refusing: ' "$S/L2.txt" | cut -c1-200 | clean
n=$(grep -c . "$S/calls.log")
ok "$l2.$n" "3.0" "refused (3), no ssh or rsync call"

step "L3. the presence read fails: named as a failed read, and the collector stops"
mkbox
export SSH_FAIL_ON="bash -s"; coll L3 collect_e185_v2.sh; l3=$?; unset SSH_FAIL_ON; grep -E '^rsync .* rc=255|^COPY-BACK' "$S/L3.txt" | cut -c1-200 | clean
fr=$(grep -cE '^rsync e185(-smoke)?/p185(01|20) rc=255' "$S/L3.txt")
ok "$l3.$fr" "4.2" "both pass directories named as not copied (rc 255), the copy-back not exact (4)"

step "C2-C4. v2 on v1's copy-back faults"
mkbox differs; coll C2 collect_e185_v2.sh; c2=$?
mkbox extra; coll C3 collect_e185_v2.sh; c3=$?
mkbox no-manifest; coll C4 collect_e185_v2.sh; c4=$?
w=$(grep -c '^COPY-BACK DIFFERS' "$S/C2.txt").$(grep -c '^COPY-BACK EXTRA: .*p18520/stray.txt' "$S/C3.txt").$(grep -c '^COPY-BACK NO-MANIFEST' "$S/C4.txt")
ok "$c2.$c3.$c4.$w" "4.4.4.1.1.1" "DIFFERS, EXTRA (a stray inside the measured pass) and NO-MANIFEST each stop v2 (4)"

run22() {  # run22 <case> [keep]: step 14 v2 on the stand-in box, the window first
  [ "${2:-}" = keep ] || rm -rf "${T:?}/$D"
  win
  [ -n "$OWN" ] && echo "$OWN" > "$RB_OUT/box-login-aifoundry3.txt"
  bash "$R/s22_collect_e185_v2.sh" > "$S/$1.txt" 2>&1
}
nscored() { ls "$T/$D"/scored-m11* 2>/dev/null | wc -l | tr -d ' '; }

step "E2. step 14 v2 end to end on the later try's box: the lists, the collector v2, the gates, the check of C, the scrub, the scorer v5"
mkbox; latertry
: > "$RB_OUT/runbook.log"
run22 E2; e2=$?; grep -E 'COPY-BACK|left on the box|COUNT-OK|score rc|collected and scored|STOP' "$S/E2.txt" | clean | head -n 8
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
lg=$(grep -c "step=s22_collect_v2_e185 left on the box .*p18501.try1" "$RB_OUT/runbook.log")
ok "$e2.${sc%%|*}.$(echo "$sc" | cut -d'|' -f2-4).$(echo "$sc" | cut -d'|' -f6-7).$lg" "0.score_m11_v5.py.SCORED|SCORED|5.9|False.1" \
  "collected (EXACT) and scored after a later try: A10 SCORED, E185's rules SCORED on 5 holds, stages to 9, no staging file, the left line logged"

step "G1. step 14 v2 again into E2's data directory: the collector refuses (16), no rsync call"
: > "$S/calls.log"
run22 G1 keep; g1=$?; grep -m1 -E 'STOP' "$S/G1.txt" | cut -c1-200 | clean
nr=$(grep -c '^rsync' "$S/calls.log")
ok "$g1.$nr" "16.0" "a used data directory: 16 on the refusal, nothing copied"

step "S1. step 14 v2 with a stand-in scorer that exits 1: 14, and the message says to remove the data directory first"
mkbox
export RB_DESKTEST=1 E185_SCORE="$S/fake_score.sh"; run22 S1; s1=$?; unset RB_DESKTEST E185_SCORE; grep -m1 -E 'STOP' "$S/S1.txt" | cut -c1-260 | clean
rm1=$(grep -c "To collect again, remove $D first" "$S/S1.txt")
ok "$s1.$rm1.$(nscored)" "14.1.0" "the scorer failed: 14, the removal named, no scored file"

step "Z. nothing the test started is left running"
left=$("$REAL_PGREP" -f "$S/(tree|box)" 2>/dev/null | grep -vc "^$$\$")
echo "processes under the scratch tree or box: $left"
ok "$left" 0 "nothing left running"

echo
echo "network calls by the stand-ins: to the stand-in box only; elapsed $(( $(date +%s) - t_begin )) s"
echo "SELFTEST-RB-E185-V2 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
exit "$fail"
