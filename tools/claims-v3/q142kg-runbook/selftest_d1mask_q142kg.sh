#!/bin/bash
# The desk test of d1mask_q142kg.sh (README.md.dated-note-3.md): E173's departure D1 replayed from the committed files, then the cases the
# rule refuses or stops on. Written Thu 5 Nov 2026 (week 45), PST, in the E173 card lane's fix pass. It never reaches a lab box (stand-in ssh
# and rsync first on PATH log and refuse every call; the test counts them), never writes in the lab clone, and reads only committed blobs there:
# E173's data dir as of commit 571d0482 (the data commit ed8b5761 with its README's time fixed), through git archive, never the work tree, so a
# later dated note beside that README cannot change the replay.
#
#   bash tools/claims-v3/q142kg-runbook/selftest_d1mask_q142kg.sh <a new, empty scratch dir outside the lab clone>
#
# Each case builds its own tree under the scratch dir: E173's committed data dir set back to its file set at 12:30:54 PST, when the collect
# step stopped (ccheck-s1.json gunzipped beside its .gz, as the collector's gzip -n -k left both; README.md, written after the collection,
# moved aside: 425 files, the count the gate read then; every file's time the extraction's, as a collection's are), logs/cclist.txt rebuilt
# as collected by putting the case's own RB_OUT back where the committed file says <RB_OUT> (the verifier of E173 found the committed file to
# be the bytes as collected with exactly that prefix masked), and a runbook log holding the collect step's probe line and its desk-path stop.
# The helper then runs with RB_REPO set to that tree. P1 must give back the committed logs/cclist.txt byte for byte. The summary goes to
# stdout with no path in it.
# SPDX-License-Identifier: Apache-2.0
set -u
S=${1:-}
[ -n "$S" ] || { echo "usage: selftest_d1mask_q142kg.sh <a new, empty scratch dir outside the lab clone>"; exit 2; }
KG=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
LAB=$(cd "$KG/../../.." && pwd -P)
mkdir -p "$S" || exit 2
S=$(cd "$S" && pwd -P)
case "$S/" in "$LAB/"*) echo "refused: the scratch dir is inside the lab clone"; exit 2 ;; esac
[ -z "$(ls -A "$S" 2>/dev/null)" ] || { echo "refused: the scratch dir is not empty"; exit 2; }
E=docs/reports/data/2026-11-05-e173-blind8-aifoundry2
C=571d0482   # E173's data as committed: ed8b5761 (12:47:48 PST), its README's time fixed in 571d0482 (12:51:14 PST); 425 files
PY=/usr/bin/python3
mkdir -p "$S/committed" || exit 2
git -C "$LAB" show "$C:$E/logs/cclist.txt" > "$S/committed/cclist.txt" || { echo "refused: $C:$E/logs/cclist.txt is not readable"; exit 2; }
WANT=$("$PY" -B "$KG/d1mask_q142kg.py" sha "$S/committed/cclist.txt")
mkdir -p "$S/standin"
for t in ssh rsync; do
  printf '#!/bin/bash\necho "%s $*" >> "%s/standin/calls.txt"\nexit 99\n' "$t" "$S" > "$S/standin/$t"
  chmod +x "$S/standin/$t"
done
: > "$S/standin/calls.txt"
echo "# selftest_d1mask_q142kg.sh: $(TZ=America/Los_Angeles date '+%a %d %b %Y %H:%M:%S %Z'), on the Intel, at the desk; the replay's source is $E as committed at $C"
echo "# the committed logs/cclist.txt: sha256 $WANT"
pass=0
fail=0

ts() { TZ=America/Los_Angeles date -r "$1" '+%Y-%m-%d %H:%M:%S %Z'; }

mk() {  # mk <case>: a fresh tree for one case; prints nothing
  T=$S/$1
  mkdir -p "$T/repo" "$T/rb" "$T/aside" || exit 2
  git -C "$LAB" archive --format=tar "$C" -- "$E" | tar -xmf - -C "$T/repo" || exit 2
  CD=$T/repo/$E
  [ "$(find "$CD" -type f | wc -l | tr -d ' ')" = 425 ] || { echo "refused: $C's $E did not extract as 425 files"; exit 2; }
  gunzip -c "$CD/ccheck-s1.json.gz" > "$CD/ccheck-s1.json" || exit 2
  mv "$CD/README.md" "$T/aside/" || exit 2
  sed "s#<RB_OUT>#$T/rb#g" "$S/committed/cclist.txt" > "$CD/logs/cclist.txt" || exit 2
  : > "$T/lock.txt"
  local now
  now=$(date +%s)
  P_LINE="$(ts $((now - 120))) step=e173_collect_q142kg3 class=probe host=aifoundry2 bound=15s secs=0.2 rc=0 child_rc=0 status=ok what='probe' cmd=ssh aifoundry2 true"
  S_LINE="$(ts $((now - 10))) step=e173_collect_q142kg3 exit=16 a desk path reached what this step wrote (the HIT lines above): commit nothing; fix the route, remove the outputs, collect again"
  printf '%s\n%s\n' "$P_LINE" "$S_LINE" > "$T/rb/runbook.log"
  IN=$("$PY" -B "$KG/d1mask_q142kg.py" sha "$CD/logs/cclist.txt")
}

go() {  # go [VAR=value ...]: run the helper in the case's tree; sets rc
  (cd "$T/repo" && env RB_REPO="$T/repo" RB_OUT="$T/rb" RB_LOCK="$T/lock.txt" PATH="$S/standin:$PATH" "$@" \
    bash "$KG/d1mask_q142kg.sh" E173 "$E" aifoundry2) > "$T/out.txt" 2>&1
  rc=$?
}

has() { grep -qE "$1" "$T/out.txt"; }
now_sha() { "$PY" -B "$KG/d1mask_q142kg.py" sha "$CD/logs/cclist.txt"; }

check() {  # check <case> <want rc> <what> <condition result 0|1>
  if [ "$rc" = "$2" ] && [ "$4" = 0 ]; then
    pass=$((pass + 1)); echo "$1 PASS: rc $rc (want $2); $3"
  else
    fail=$((fail + 1)); echo "$1 FAIL: rc $rc (want $2); $3; the case's output is out.txt in its scratch tree"
  fi
}

# P1: E173's D1, replayed
mk P1; go
ok=1
[ "$(now_sha)" = "$WANT" ] && [ -f "$T/rb/e173-d1/cclist.txt.as-collected" ] \
  && [ "$("$PY" -B "$KG/d1mask_q142kg.py" sha "$T/rb/e173-d1/cclist.txt.as-collected")" = "$IN" ] \
  && has 'D1MASK-PLAN: 3 occurrence' && has 'D1MASK-DONE: 3 occurrence' && has 'D1MASK-COMPARE: of the data dir.s 425 files only logs/cclist.txt changed' \
  && has 'cclist v3: 3 required \(v2 3, v1 3\), 0 without a C log' && has 'ccdone: 3 of 3 C checks finished \(3 of them all PASS\): FINISHED' \
  && has 'nopath: 425 files read under 1 path\(s\); 0 missing; 0 hit\(s\): CLEAN' && has "D1's rule applied" \
  && grep -q 'step=e173_collect_d1_q142kg3 done' "$T/rb/runbook.log" && ok=0
check P1 0 "E173's D1 replayed: the masked list equals the committed logs/cclist.txt byte for byte, the bytes as collected kept under RB_OUT, of 425 files only logs/cclist.txt changed, the C-log gate 3 of 3 finished, the desk-path gate 425 files CLEAN" $ok

# R1: a desk path in another file too: outside the rule, nothing changed, no copy kept
mk R1; echo "$T/rb/e173-raw/x" >> "$CD/logs/queue.out"; go
ok=1; [ "$(now_sha)" = "$IN" ] && [ ! -e "$T/rb/e173-d1/cclist.txt.as-collected" ] && has '^D1MASK-OUTSIDE-RULE' && ok=0
check R1 16 "a desk path in logs/queue.out as well: stopped before the mask, logs/cclist.txt as collected, no copy kept" $ok

# R2: RB_OUT on a line the C-log list never prints
mk R2; echo "note $T/rb/x" >> "$CD/logs/cclist.txt"; IN=$(now_sha); go
ok=1; [ "$(now_sha)" = "$IN" ] && has '^D1MASK-OUTSIDE-RULE' && ok=0
check R2 16 "RB_OUT on a line that is not a REQUIRED line: stopped, nothing changed" $ok

# R3: nothing to mask (the list already masked)
mk R3; cp "$S/committed/cclist.txt" "$CD/logs/cclist.txt"; IN=$(now_sha); go
ok=1; [ "$(now_sha)" = "$IN" ] && has 'reads .* clean: nothing to mask' && ok=0
check R3 10 "a clean data dir: refused, nothing changed" $ok

# R4: the collect step's last stop is not the desk-path gate's
mk R4; printf '%s\n%s\n' "$P_LINE" "${S_LINE/exit=16 a desk path reached what this step wrote/exit=14 a call failed}" > "$T/rb/runbook.log"; go
ok=1; [ "$(now_sha)" = "$IN" ] && has "last stop is not the desk-path gate" && ok=0
check R4 10 "the step's last stop is exit 14, not the desk-path gate's: refused, nothing changed" $ok

# R5: an absolute REQUIRED path that is not under RB_OUT
mk R5; sed -i '' "s#$T/rb/e173-raw/cc/ccheck-s1.json#$T/repo/build/e173-raw/cc/ccheck-s1.json#" "$CD/logs/cclist.txt"; IN=$(now_sha); go
ok=1; [ "$(now_sha)" = "$IN" ] && has 'absolute or climbs out without being under RB_OUT' && ok=0
check R5 16 "a REQUIRED path under the lab clone, not RB_OUT: stopped, nothing changed" $ok

# R6: the C-log gate fails after the mask: the bytes as collected are put back
mk R6; mv "$CD/ccheck-smoke.json" "$T/aside/"; go
ok=1; [ "$(now_sha)" = "$IN" ] && has 'D1MASK-DONE' && has 'CCHECK-MISSING' && has 'D1MASK-RESTORED' \
  && grep -q 'step=e173_collect_d1_q142kg3 put back logs/cclist.txt as collected' "$T/rb/runbook.log" && ok=0
check R6 14 "a listed check of C missing after the mask: the C-log gate stops (14) and logs/cclist.txt is put back as collected" $ok

# R7: RB_OUT not set
mk R7
(cd "$T/repo" && env -u RB_OUT RB_REPO="$T/repo" RB_LOCK="$T/lock.txt" PATH="$S/standin:$PATH" bash "$KG/d1mask_q142kg.sh" E173 "$E" aifoundry2) > "$T/out.txt" 2>&1
rc=$?
ok=1; [ "$(now_sha)" = "$IN" ] && has 'RB_OUT is not set' && ok=0
check R7 10 "RB_OUT not set: refused, nothing changed" $ok

# R8: a dry listing is refused
mk R8; go RB_DRY=1
ok=1; [ "$(now_sha)" = "$IN" ] && has 'no dry listing' && ok=0
check R8 10 "RB_DRY=1: refused, nothing changed" $ok

# R9: the list committed already
mk R9
git -C "$T/repo" init -q && git -C "$T/repo" add "$E" && git -C "$T/repo" -c user.name=desktest -c user.email=desktest@localhost commit -q -m t
go
ok=1; [ "$(now_sha)" = "$IN" ] && has 'is committed' && ok=0
check R9 10 "the data dir committed: refused (a correction is a dated note), nothing changed" $ok

# R10: the collect step ran again after its desk-path stop
mk R10; echo "${P_LINE/class=probe/class=probe}" >> "$T/rb/runbook.log"; go
ok=1; [ "$(now_sha)" = "$IN" ] && has 'ran again after its desk-path stop' && ok=0
check R10 10 "a later line of the same collect step after its stop: refused, nothing changed" $ok

# U1: the compare refuses a second changed file
T=$S/U1; mkdir -p "$T"
printf 'aa  logs/cclist.txt\nbb  results.json\n' > "$T/b.txt"; printf 'cc  logs/cclist.txt\ndd  results.json\n' > "$T/a.txt"
"$PY" -B "$KG/d1mask_q142kg.py" compare "$T/b.txt" "$T/a.txt" logs/cclist.txt > "$T/out.txt" 2>&1; rc=$?
ok=1; has '^D1MASK-OUTSIDE-RULE: the files changed are' && ok=0
check U1 16 "two files changed: compare stops" $ok

# U2: the probe line's time to epoch seconds, against E173's own D1 (12:17:15 PST, the re-gate's --since 1793909835)
T=$S/U2; mkdir -p "$T"
printf '%s\n%s\n' "2026-11-05 12:17:15 PST step=e173_collect_q142kg3 class=probe host=aifoundry2 bound=15s rc=0 what='probe'" \
  "2026-11-05 12:30:54 PST step=e173_collect_q142kg3 exit=16 a desk path reached what this step wrote (the HIT lines above)" > "$T/runbook.log"
"$PY" -B "$KG/d1mask_q142kg.py" since "$T/runbook.log" e173_collect_q142kg3 > "$T/out.txt" 2>&1; rc=$?
ok=1; has '^SINCE 1793909835 2026-11-05 12:17:15 PST' && ok=0
check U2 0 "E173's collect step's probe line, 12:17:15 PST, reads 1793909835, the --since D1's re-gate used" $ok

n=$(wc -l < "$S/standin/calls.txt" | tr -d ' ')
echo "SUMMARY: $pass of $((pass + fail)) PASS; stand-in ssh and rsync calls: $n"
[ "$fail" = 0 ] && [ "$n" = 0 ]
