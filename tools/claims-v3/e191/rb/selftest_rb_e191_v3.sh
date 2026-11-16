#!/usr/bin/env bash
# E191's kit, dated note 3 (Q190, Sun 15 Nov 2026, PST; after E189's data commit fa9098c4 of Sat 14 Nov 2026, 20:34:12 PST, and after E191's
# second session's data commit 7156ac15 of Sun 15 Nov 2026, 14:32:17 PST; KIT.md.dated-note-3.md): THE RUNBOOK DESK TEST v3, E191.md's dated
# amendment A2's THIRD SESSION (a REPEAT) whole on a stand-in aifoundry1 left as the second session left it, in rb/selftest_rb_e191_v2.sh's
# form (unchanged beside it: its scratch repository with its own upstream, its fake ssh and rsync serving a stand-in ~/nekko, its stand-in
# hostname, uptime, et-who, cmake and objcopy; RB_DESKTEST=1 with the same stand-in pins). The scratch repository is a shared sparse clone at
# the commit before E191's kit, with E191's files (the kit, notes 2 and 3) and BOTH EARLIER RECORDS (1a4bc1e3's and 7156ac15's directories, the
# second with its data note 1) committed on top as one stand-in commit; the kit's, note 2's and A1's lists are the real ones, kit note 3's and
# A2's lists are made from the scratch's own files (stand-ins, as v2's test made note 2's) and step 2 v3's two pins set to them; note 3's logs are
# stand-ins (this test makes one of them). No lab box is reached. Cases (verdicts stated first):
#   A3    the dry listing v3: every step 0, no call reaches the stand-ins; step 2 v3, steps 9, 11 and 13 v3 and session v2 listed; its command
#         lines pass note 1's item 4 (drylisting_check_e191_v2.py);
#   P1v3  step 2 v3 on the scratch repository: 0, every list at its pin (the second session's record's two lists among them), NEVER RAN (a)
#         in A2's form (E191's two earlier records left out), (c) in A2's form (E191 data only in the first record, no pass in it, and the
#         second);
#   P2v3  A2's list one line short: 16, named;  H6v3 an ...-c1-s3 directory in a ref: 16;  H7v3 a passes/ file inside the first record in a
#         ref: 16;  N1v3 a file naming the instance in a folder that is not E194's exact form: 16 by (a);  N2v3 the same file in a folder of
#         E194's exact form (<day>-e194-blind-day-aifoundry2): left out by name, 0;
#   F2    THE SECOND SESSION's day on the stand-in box (its window, the look, step 5 v2, step 6 start and wait: one build start today) and both
#         committed records' session directories placed at build/e191/T1794766494 and build/e191/T1794780355, the box's T0 file the second's;
#   S5v3  the third session in a NEW RB_OUT: its window, the look, then step 5 v2 (both harnesses read on the box);
#   B6v3  step 6's WAIT ALONE on the build's own day (the kit's same-day rule: that day's build stands): 0, "ledger,spp", the box's start
#         count still 1 today;
#   B7v3  A LATER DAY (A2-5, Q191: the third session runs on Mon 16 Nov 2026 or later, so the build is that day's own): the stand-in box's
#         build re-dated to the day before (its count-file line, its job files' times, both build records' day): step 6's wait alone 10
#         ("no build job was started today", nothing written), then its start (E191-BUILDS-TODAY 0) and its wait: 0, "ledger,spp", one
#         start today, the earlier day's line kept, both records today's;
#   G1v3  step 9 v3 with no dry pass of runner v2 today: 10, nothing launched;  D3 step 8 v2 (runner v2's dry pass): 0, its E191-DRY-V2 line;
#   G2v3  step 9 v3 from the SECOND session's RB_OUT (its T0 a session that sent card commands): 10 by the box read, nothing launched;
#   LL3a  THE LAST LAUNCH v3, RB_OUT with no T0: the box's last E191 launch is the FIRST session's (v2's reference), then another T0: 10 each,
#         before the rest rule, nothing launched;
#   RS3   THE REST RULE through step 9 v3: the second session's committed log with its end moved to 10 minutes ago: 10 naming E191;
#   LA3   step 9 v3 launches the REAL session_e191_v2.sh and run_e191_v2.py (stopped at their box check before any device: this desk is not
#         aifoundry1), its LAUNCHED line naming A2's third session; step 10 v2 reads the gate (16), the manifest and "kit note 2";
#   LL3b  THE LAST LAUNCH with a T0 in RB_OUT: the box's last launch is not that T0: 10, no relaunch;
#   G4a3  THE RELAUNCH RULE: step 9 v3 again from that RB_OUT (its T0 opened no device): 0, a new T0, e191-relaunch.txt;  G4b3 a third: 10;
#   C3v3  step 11 v3 from the second session's RB_OUT (its T0 1794780355, whose log names kit note 2): 10, nothing written;
#   C5v3  step 11 v3 while an ...-c1-s3 directory of another day exists: 10, nothing copied;
#   C2v3  step 11 v3 on the relaunched session: COPY-BACK EXACT, COLLECTED into ...-c1-s3, SHA256SUMS and FILES.txt, no home path or login,
#         both earlier records untouched;  C4v3 step 11 v3 again: ...-c1-s3 exists: 10;
#   SC0v3 step 13 v3 before the data commit: 10;  SC3v3 committed and clean: 0, scores-e191-s3.json, scores-e191-s2.json at the registered
#         verdicts' bytes (23484c4f...), the repeat reading (every configuration NO DATA in the stand-in third session: no difference);
#   SC4v3 a changed byte committed in the second record: 16, nothing set beside it;
#   Z     no process of this test left running.
#   bash tools/claims-v3/e191/rb/selftest_rb_e191_v3_ns.sh <scratch dir> > <log>   (prints SELFTEST-RB-E191-V3 <n> of <m> PASS or FAIL)
# On a box with a card (aifoundry2) run it ONLY inside a sandbox with no /dev/et* and an empty /run/lock: case LA3 runs the real runner.
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
for v in RB_PROBE_S RB_READ_S RB_COPY_S RB_WAIT_S RB_LAUNCH_S RB_DESK_S RB_DESKTEST RB_GITLOCK; do
  [ -z "${!v:-}" ] || { echo "$v is set: this test runs with rb_run.py's own bounds"; exit 2; }
done
for c in timeout sha256sum g++-13 flock; do command -v "$c" > /dev/null || { echo "no $c on PATH"; exit 2; }; done
date --version 2> /dev/null | grep -q 'GNU coreutils' || { echo "no GNU date"; exit 2; }
ls /dev/et* > /dev/null 2>&1 && { echo "REFUSED: a /dev/et* node is visible: run this inside the sandbox"; exit 3; }
sedi() { local f=${!#} t; t=$(mktemp "${TMPDIR:-/tmp}/sedi.XXXXXX") || return 2; sed "${@:1:$(($# - 1))}" "$f" > "$t" && cat "$t" > "$f"; local r=$?; rm -f "$t"; return "$r"; }
REAL_TIMEOUT=$(command -v timeout); REAL_RSYNC=$(command -v rsync)
mkdir -p "$S"; S=$(cd "$S" && pwd)
for d in tree box bin out boxbin; do [ -e "$S/$d" ] && { echo "$S/$d exists: give an empty scratch directory"; exit 2; }; done
T=$S/tree; B=$S/box; BIN=$S/bin; BOXT=$B/aifoundry1/nekko
mkdir -p "$BOXT" "$BIN" "$S/boxbin" "$S/standin"
E=tools/claims-v3/e191
FIRST=docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1
SECOND=docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2
FT0=1794766494; ST0=1794780355
S2SHA=23484c4f546595a728f0c7ffe59e9414d125473108f06891e5dd53283d62ecb8
main() {
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
has() { grep -aq -- "$1" "$2" && echo 1 || echo 0; }
stopline() { grep -a 'STOP' "$1" | tail -n 1 | cut -c1-300; }
echo "selftest_rb_e191_v3: $(date '+%F %T %Z'), processes visible: $(ls /proc | grep -c '^[0-9]')"
# ---- the scratch repository: v2's form, with notes 2 and 3's files and both earlier records in the stand-in commit
KITC=$(git -C "$SRC" log --diff-filter=A --format=%H -- $E/KIT.md | tail -n 1)
if [ -n "$KITC" ]; then BASE=$(git -C "$SRC" rev-parse "$KITC^"); else BASE=$(git -C "$SRC" rev-parse HEAD); fi
git clone -q --shared --no-checkout "$SRC" "$T" || return 2
G="git -C $T -c user.name=e191-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G sparse-checkout set --no-cone /tools/ /workloads/ /docs/reports/data/2026-11-12-q166-progs/ /docs/reports/data/2026-11-12-q166-ledger-v2/ \
  /docs/reports/data/2026-11-12-q166-counter-sparseparity/ /docs/reports/data/2026-09-23-energy-manual/ /docs/reports/data/2026-10-26-load-model/ \
  /docs/reports/data/2026-11-13-e190-large-gemm/ /docs/reports/data/2026-11-08-e184-sensor-validation/raw/aifoundry1-c1/logs/ \
  /docs/reports/data/2026-11-04-e170-blind7-card0/ /docs/reports/data/2026-11-14-e189-blind-day-aifoundry3/session/ \
  '/docs/reports/data/*-e191-*/' || return 2
$G checkout -q -B main "$BASE" || return 2
( cd "$SRC" && git ls-files --others --exclude-standard -- $E; git diff --name-only -- $E; git ls-files -- $E ) | sort -u | while IFS= read -r f; do
  [ -f "$SRC/$f" ] || continue; mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
for d in "$FIRST" "$SECOND"; do mkdir -p "$T/$d"; cp -rp "$SRC/$d/." "$T/$d/"; done
mkdir -p "$T/$E/logs"
for spec in "selftest-rb-e191-v3.txt SELFTEST-RB-E191-V3 0 of 0 PASS" "checks-e191-v3.txt CHECKS-E191-V3 0 of 0 PASS" \
            "repeat-selftest-e191.txt REPEAT-E191 SELFTEST 0 of 0 PASS" "dry-listing-e191-v3.txt dry listing: 0 steps listed, 0 exited non-zero, 0 box calls"; do
  printf '%s\n' "${spec#* }" > "$T/$E/logs/${spec%% *}"      # note 3's logs: stand-ins always (this test makes one of them; note 3's list is a stand-in too)
done
# kit note 3's and A2's lists as stand-ins made from the scratch's own files (the real ones pin this test's own log); step 2 v3's pins set to them
( cd "$T" && git -C "$SRC" ls-tree -r --name-only 7156ac15 -- $E > "$S/e191-at-s2.txt"
  find $E -type f ! -name '*.pyc' ! -name 'SHA256SUMS-e191-kit-note3' ! -name 'SHA256SUMS-e191-a2' ! -path "$E/rb/s03_desk_e191_v3.sh" | LC_ALL=C sort |
    grep -v -x -F -f "$S/e191-at-s2.txt" | while IFS= read -r f; do sha256sum "$f"; done ) > "$S/note3-standin.txt"
( cd "$T" && for f in $E/E191.md.dated-amendment-A2.md $E/E191.md $E/SHA256SUMS-e191-registration $E/KIT.md.dated-note-3.md; do [ -f "$f" ] && sha256sum "$f"; done ) > "$S/a2-standin.txt"
cp "$S/note3-standin.txt" "$T/$E/SHA256SUMS-e191-kit-note3"; cp "$S/a2-standin.txt" "$T/$E/SHA256SUMS-e191-a2"
NOTE3_COUNT=$(grep -c . "$S/note3-standin.txt"); NOTE3_SHA=$(sha256sum "$S/note3-standin.txt" | cut -c1-64)
A2_COUNT=$(grep -c . "$S/a2-standin.txt"); A2_SHA=$(sha256sum "$S/a2-standin.txt" | cut -c1-64)
sedi -e "s#^NOTE3PIN=$E/SHA256SUMS-e191-kit-note3:[^ ]*#NOTE3PIN=$E/SHA256SUMS-e191-kit-note3:$NOTE3_COUNT:$NOTE3_SHA:top#" \
     -e "s#^A2PIN=$E/SHA256SUMS-e191-a2:[^ ]*#A2PIN=$E/SHA256SUMS-e191-a2:$A2_COUNT:$A2_SHA:top#" "$T/$E/rb/s03_desk_e191_v3.sh"
grep -q "^NOTE3PIN=$E/SHA256SUMS-e191-kit-note3:$NOTE3_COUNT:$NOTE3_SHA:top" "$T/$E/rb/s03_desk_e191_v3.sh" &&
  grep -q "^A2PIN=$E/SHA256SUMS-e191-a2:$A2_COUNT:$A2_SHA:top" "$T/$E/rb/s03_desk_e191_v3.sh" || { echo "the scratch step 2 v3's pins were not set"; return 2; }
$G add -A $E && $G add --sparse -A "$FIRST" "$SECOND" && $G commit -q -m "E191 runbook desk test v3: the kit's, note 2's and note 3's files and both earlier records (stand-in commit)" || { echo "the scratch commit failed"; return 2; }
git clone -q --bare "$T" "$S/origin.git" && $G remote set-url origin "$S/origin.git" && $G fetch -q origin && $G branch -q -u origin/main main || return 2
for r in $($G for-each-ref --format='%(refname)' refs/remotes/origin | grep -v -e '/main$' -e '/HEAD$'); do $G update-ref -d "$r"; done
echo "scratch repository: a shared sparse clone at ${BASE:0:12} (the commit before E191's kit), the stand-in commit $($G rev-parse --short=12 HEAD) (the kit, notes 2 and 3, both earlier records), its own upstream; note 3's list stand-in $NOTE3_COUNT files, A2's $A2_COUNT"
# ---- the stand-ins (v2's)
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry1) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
[ "\$cmd" = true ] && exit 0
cat | HOME="$B/\$host" PATH="$S/boxbin:\$PATH" FAKE_CMAKE_REPO="$T" bash -c "cd ~ && \$cmd"
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; case "\$h" in aifoundry1) ;; *) echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97 ;; esac; a+=("$B/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
printf '#!/bin/sh\necho aifoundry1\n' > "$S/boxbin/hostname"
cat > "$S/boxbin/uptime" <<EOF
#!/bin/sh
if [ "\$1" = -s ]; then echo "2026-10-26 15:02:04"; exit 0; fi
exec /usr/bin/uptime "\$@"
EOF
printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$S/boxbin/python3"
printf '#!/bin/sh\necho "No process holds an ET-SoC-1 device node or card lock."\n' > "$S/boxbin/et-who"
printf '#!/bin/sh\necho "et-lab-manifest (desk-test stand-in): sysfs and files only"\n' > "$S/boxbin/et-lab-manifest"
printf '#!/bin/sh\nexec "$@"\n' > "$S/boxbin/setsid"
printf '#!/bin/sh\nexec "%s" "$@"\n' "$REAL_TIMEOUT" > "$S/boxbin/timeout"
printf '#!/bin/sh\n[ "$1" = "-O" ] && [ "$6" = /dev/stdout ] && exec cat "$5"\nexit 2\n' > "$S/boxbin/objcopy"
printf '#!/bin/sh\nexec bash "%s" "$@"\n' "$SRC/$E/rb/fake_cmake_e191.sh" > "$S/boxbin/cmake"
for n in ssh rsync scp sudo; do printf '#!/bin/sh\necho "BOX STAND-IN: %s refused" >&2\nexit 97\n' "$n" > "$S/boxbin/$n"; done
chmod +x "$BIN/ssh" "$BIN/rsync" "$S/boxbin"/*
printf 'lib stand-in ET_DEVICES\n' > "$S/devicelayer-standin.a"
ledpin=$(printf 'E189 desk-test stand-in kernel: ledger\n' | sha256sum | cut -c1-64); spppin=$(printf 'E189 desk-test stand-in kernel: sparse parity\n' | sha256sum | cut -c1-64)
printf '{"kernels": {"ledger": {"elf_sha256": "%s", "text_sha256": "%s"}, "spp": {"elf_sha256": "%s", "text_sha256": "%s"}}}\n' "$ledpin" "$ledpin" "$spppin" "$spppin" > "$S/standin-pins.json"
export PATH="$BIN:$PATH" RB_REPO="$T" RB_LOCK="$S/lock.txt" RB_DESKTEST=1 E191_KERNEL_PINS="$S/standin-pins.json" E191_OBJCOPY="$S/boxbin/objcopy" \
  E191_DEVICELAYER="$S/devicelayer-standin.a" E191_DESK_BUDGET_S=60
: > "$S/calls.log"; : > "$RB_LOCK"; : > "$S/gitlock"
R=$T/$E/rb
TODAY=$(TZ=America/Los_Angeles date +%F)
cd "$T" || return 2

step "A3. the dry listing v3 (the third session's order), and its command lines (note 1, item 4)"
bash "$R/list_steps_e191_v3.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
/usr/bin/python3 -I -B "$T/$E/desk/drylisting_check_e191_v2.py" "$S/dry-listing.txt" > "$S/dry-check.txt" 2>&1; dc=$?
tail -n 1 "$S/dry-listing.txt"; tail -n 1 "$S/dry-check.txt"
ok "$rc.$(grep -c . "$S/calls.log").$dc.$(has 's03_desk_e191_v3.sh' "$S/dry-listing.txt").$(has 's11_a1_session_e191_v3.sh FULL' "$S/dry-listing.txt").$(has 's22_collect_e191_v3.sh' "$S/dry-listing.txt").$(has 's24_score_e191_v3.sh' "$S/dry-listing.txt").$(has 'session_e191_v2.sh' "$S/dry-listing.txt")" "0.0.0.1.1.1.1.1" \
  "A3 every step 0, no call to the stand-ins; step 2 v3, steps 9, 11 and 13 v3 and session v2 listed; every device-opening line carries ET_DEVICES=1, none of card 0"

step "P1v3. step 2 v3 on the scratch repository"
mkdir -p "$S/out-p"; RB_OUT="$S/out-p" bash "$R/s02_window_e191.sh" "$TODAY" 23:58 23:59 > /dev/null 2>&1
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e191_v3.sh" > "$S/p1.txt" 2>&1; p1=$?
grep -E 'desk check|STOP' "$S/p1.txt" | cut -c1-700
ok "$p1.$(has 'desk check v3 (kit note 3' "$S/p1.txt").$(has "note 3's ($NOTE3_COUNT)" "$S/p1.txt").$(has "A2's ($A2_COUNT)" "$S/p1.txt").$(has "the second session's record 257 and its note 1's 7" "$S/p1.txt").$(has 'NEVER RAN (a) with E189.s data, E191.s two earlier records and 0 E194 folder' "$S/p1.txt").$(has 'E191 data only in the first session.s record (no pass in it) and the second session.s' "$S/p1.txt")" \
  "0.1.1.1.1.1.1" "P1v3 step 2 v3 passes at every pin (the second session's record's two lists among them), NEVER RAN (a) and (c) in A2's form"

step "P2v3, H6v3, H7v3. A2's list one line short; an ...-c1-s3 directory in a ref; a pass inside the first record in a ref"
sedi -e '$d' "$T/$E/SHA256SUMS-e191-a2"; $G commit -q -am "desk test: A2's list one line short"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e191_v3.sh" > "$S/p2.txt" 2>&1; p2=$?; $G reset -q --hard HEAD~1
D3T=docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s3
$G branch -q e191-s3-standin; $G checkout -q e191-s3-standin; mkdir -p "$T/$D3T"; echo x > "$T/$D3T/README.md"
$G add --sparse "$D3T/README.md"; $G commit -q -m "desk test: an -s3 directory in a ref"; $G checkout -q main
rm -rf "${T:?}/$D3T"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e191_v3.sh" > "$S/h6.txt" 2>&1; h6=$?; $G branch -q -D e191-s3-standin
$G branch -q e191-pass-standin; $G checkout -q e191-pass-standin; mkdir -p "$T/$FIRST/passes/copy-zeros/p1"; echo x > "$T/$FIRST/passes/copy-zeros/p1/pass.json"
$G add --sparse "$FIRST/passes/copy-zeros/p1/pass.json"; $G commit -q -m "desk test: a pass in the first record"; $G checkout -q main
rm -rf "${T:?}/$FIRST/passes"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e191_v3.sh" > "$S/h7.txt" 2>&1; h7=$?; $G branch -q -D e191-pass-standin
ok "$p2.$(has "SHA256SUMS-e191-a2($((A2_COUNT - 1)) OK of $((A2_COUNT - 1)); pinned $A2_COUNT" "$S/p2.txt").$h6.$(has 'never-ran(c: 1 E191 data path(s) outside the first and second sessions' "$S/h6.txt").$h7.$(has 'never-ran(c: 0 E191 data path(s) outside the first and second sessions. records, 1 under the first.s passes/' "$S/h7.txt")" \
  "16.1.16.1.16.1" "P2v3 A2's pin refused and named; H6v3 an -s3 directory in a ref refused; H7v3 a pass in the first record refused"

step "N1v3, N2v3. the never-run check (a): a file naming the instance in a folder not of E194's exact form, then in one of that form"
NR1=docs/reports/data/2026-11-15-e194-standin-aifoundry2; NR2=docs/reports/data/2026-11-15-e194-blind-day-aifoundry2
mkdir -p "$T/$NR1"; printf 'a stand-in line: --n 544 --k 4 --eta 0.39 --m 1792 --seed 3\n' > "$T/$NR1/README.md"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e191_v3.sh" > "$S/n1.txt" 2>&1; n1=$?
rm -rf "${T:?}/$NR1"; mkdir -p "$T/$NR2"; printf 'a stand-in line: --n 544 --k 4 --eta 0.39 --m 1792 --seed 3\n' > "$T/$NR2/README.md"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e191_v3.sh" > "$S/n2.txt" 2>&1; n2=$?
rm -rf "${T:?}/$NR2"
grep -E 'STOP' "$S/n1.txt" | cut -c1-300
ok "$n1.$(has 'never-ran(a)' "$S/n1.txt").$n2.$(has 'and 1 E194 folder(s) left out' "$S/n2.txt").$(grep -c "E194 folders left out of (a): 1 (--exclude $NR2)" "$S/out-p/runbook.log")" "16.1.0.1.1" \
  "N1v3 a run of the instance outside the registered folders refuses by (a); N2v3 E194's folder of its exact form is left out by name and named"

step "F2. the second session's day on the stand-in box: its window, the look, step 5 v2, step 6 start and wait; both records placed, the box's T0 the second's"
export RB_OUT="$S/out-2"; mkdir -p "$RB_OUT"
bash "$R/s02_window_e191.sh" "$TODAY" 23:58 23:59 > /dev/null 2>&1
bash "$R/s05_look_e191.sh" > "$S/f2-look.txt" 2>&1; f2a=$?
bash "$R/s07_a1_sync_e191_v2.sh" > "$S/f2-s5.txt" 2>&1; f2b=$?
bash "$R/s08_a1_build_e191.sh" start > "$S/f2-s6a.txt" 2>&1; f2c=$?
for i in $(seq 1 30); do bash "$R/s08_a1_build_e191.sh" wait > "$S/f2-s6b.txt" 2>&1; f2d=$?; [ "$f2d" -eq 17 ] || break; done
for p in "$FT0:$FIRST" "$ST0:$SECOND"; do
  t=${p%%:*}; d=${p#*:}; mkdir -p "$BOXT/build/e191/T$t"
  cp -p "$SRC/$d/session/"*.json "$SRC/$d/session/"*.log "$SRC/$d/session/MANIFEST.sha256" "$SRC/$d/session/runner.rc" "$BOXT/build/e191/T$t/"
done
mkdir -p "$BOXT/build/q141k"; echo "$ST0" > "$BOXT/build/q141k/e191.T0"; echo "$ST0" > "$RB_OUT/e191-T0.txt"
grep -E 'built today' "$S/f2-s6b.txt" | cut -c1-200
ok "$f2a.$f2b.$f2c.$f2d.$(cat "$RB_OUT/e191-built.txt" 2>/dev/null).$(grep -c 'a1-build-e191 started' "$BOXT/build/e191-build-attempts.txt" 2>/dev/null).$(cat "$BOXT/build/q141k/e191.T0")" "0.0.0.0.ledger,spp.1.$ST0" \
  "F2 the second session's day on the stand-in box: one build start today; both records' session directories in place; the box's T0 the second session's"

step "S5v3. the third session in a NEW RB_OUT: its window, the look, then step 5 v2"
export RB_OUT="$S/out-3"; mkdir -p "$RB_OUT"
bash "$R/s02_window_e191.sh" "$TODAY" 23:58 23:59 > /dev/null 2>&1
bash "$R/s05_look_e191.sh" > "$S/s5-look.txt" 2>&1; lk=$?
bash "$R/s07_a1_sync_e191_v2.sh" > "$S/s5.txt" 2>&1; s5=$?
grep -E 'HARNESS|STOP' "$S/s5.txt" | cut -c1-220
ok "$lk.$s5.$(has 'HARNESS OK and HARNESS-V2 OK on the box' "$S/s5.txt")" "0.0.1" "S5v3 the look FREE; step 5 v2 read both harnesses on the box"

step "B6v3. step 6's WAIT ALONE in the new RB_OUT on the build's own day (the kit's same-day rule: the day's build is re-read, no start)"
bash "$R/s08_a1_build_e191.sh" wait > "$S/b6.txt" 2>&1; b6=$?
grep -E 'built today|STOP' "$S/b6.txt" | cut -c1-220
ok "$b6.$(cat "$RB_OUT/e191-built.txt" 2>/dev/null).$(grep -c 'a1-build-e191 started' "$BOXT/build/e191-build-attempts.txt")" "0.ledger,spp.1" \
  "B6v3 the day's build re-read into this RB_OUT; still one build start today"

step "B7v3. A LATER DAY (A2-5: the third session on Mon 16 Nov 2026 or later): the stand-in box's build re-dated to the day before; step 6's wait alone, then its start and its wait"
YDAY=$(TZ=America/Los_Angeles date -d "$TODAY -1 day" +%F)
sedi -e "s/^$TODAY /$YDAY /" "$BOXT/build/e191-build-attempts.txt"
for p in e191ledger e191spp; do sedi -e "s/\"day\": \"$TODAY\"/\"day\": \"$YDAY\"/" "$BOXT/build/$p/BUILD-e191.json"; done
for f in "$BOXT"/build/q141k/jobs/a1-build-e191.*; do TZ=America/Los_Angeles touch -d "$YDAY 12:00:00" "$f"; done
b7y=$(grep -c "^$YDAY .* a1-build-e191 started\$" "$BOXT/build/e191-build-attempts.txt")
b7r=$(cat "$BOXT"/build/e191ledger/BUILD-e191.json "$BOXT"/build/e191spp/BUILD-e191.json | grep -o "\"day\": \"$YDAY\"" | wc -l)
rm -f "${RB_OUT:?}/e191-built.txt"
bash "$R/s08_a1_build_e191.sh" wait > "$S/b7a.txt" 2>&1; b7a=$?
b7n=$([ -e "$RB_OUT/e191-built.txt" ] && echo written || echo none)
bash "$R/s08_a1_build_e191.sh" start > "$S/b7b.txt" 2>&1; b7b=$?
for i in $(seq 1 30); do bash "$R/s08_a1_build_e191.sh" wait > "$S/b7c.txt" 2>&1; b7c=$?; [ "$b7c" -eq 17 ] || break; done
grep -E 'E191-BUILDS-TODAY|built today|STOP' "$S/b7a.txt" "$S/b7b.txt" "$S/b7c.txt" | sed "s#$S/##" | cut -c1-220
b7t=$(cat "$BOXT"/build/e191ledger/BUILD-e191.json "$BOXT"/build/e191spp/BUILD-e191.json | grep -o "\"day\": \"$TODAY\"" | wc -l)
ok "$b7y.$b7r.$b7a.$(has 'no build job was started today' "$S/b7a.txt").$b7n.$b7b.$(has 'E191-BUILDS-TODAY 0' "$S/b7b.txt").$b7c.$(cat "$RB_OUT/e191-built.txt" 2>/dev/null).$(grep -c "^$TODAY .* a1-build-e191 started\$" "$BOXT/build/e191-build-attempts.txt").$(grep -c "^$YDAY .* a1-build-e191 started\$" "$BOXT/build/e191-build-attempts.txt").$b7t" \
  "1.2.10.1.none.0.1.0.ledger,spp.1.1.2" \
  "B7v3 an earlier day's build does not stand: the wait alone refused (10, nothing written); the day's first start (count 0 today), its wait 0 with today's records, the earlier day's line kept"

step "G1v3, D3. step 9 v3 with no dry pass of runner v2 today; then step 8 v2 (runner v2's dry pass)"
bash "$R/s11_a1_session_e191_v3.sh" FULL > "$S/g1.txt" 2>&1; g1=$?; stopline "$S/g1.txt"
g1t=$(cat "$BOXT/build/q141k/e191.T0")
bash "$R/s10_a1_dry_e191_v2.sh" start > "$S/d3a.txt" 2>&1; d3a=$?
for i in $(seq 1 30); do bash "$R/s10_a1_dry_e191_v2.sh" wait > "$S/d3b.txt" 2>&1; d3b=$?; [ "$d3b" -eq 17 ] || break; done
grep -E 'E191-DRY' "$S/d3b.txt" | cut -c1-240
ok "$g1.$(has 'a1-dry-e191-v2) has not ended rc 0 today' "$S/g1.txt").$g1t.$d3a.$d3b.$(grep -qE '^E191-DRY-V2 rc=0 passes=6 dry-check=1 identity-lines=2 note2=1 runtime-dropped=[1-9]' "$S/d3b.txt" && echo 1 || echo 0)" "10.1.$ST0.0.0.1" \
  "G1v3 refused (10) without today's dry pass of runner v2, nothing launched; D3 runner v2's dry pass rc 0 with its kit note 2 line"

step "G2v3. step 9 v3 from the SECOND session's RB_OUT (its T0 a session that sent card commands)"
RB_OUT="$S/out-2" bash "$R/s11_a1_session_e191_v3.sh" FULL > "$S/g2.txt" 2>&1; g2=$?; stopline "$S/g2.txt"
ok "$g2.$(has 'sent a card command' "$S/g2.txt").$(has "A2's third session is E191's last" "$S/g2.txt").$(cat "$BOXT/build/q141k/e191.T0")" "10.1.1.$ST0" \
  "G2v3 refused (10) by the box read: one session an RB_OUT; nothing launched"

step "LL3a. THE LAST LAUNCH v3, RB_OUT with no T0: the box's last E191 launch is the first session's (v2's reference), then another T0"
echo "$FT0" > "$BOXT/build/q141k/e191.T0"
bash "$R/s11_a1_session_e191_v3.sh" FULL > "$S/ll3a.txt" 2>&1; ll3a=$?; stopline "$S/ll3a.txt"
echo 1794700002 > "$BOXT/build/q141k/e191.T0"
bash "$R/s11_a1_session_e191_v3.sh" FULL > "$S/ll3a2.txt" 2>&1; ll3a2=$?; stopline "$S/ll3a2.txt"
ll3at=$(cat "$BOXT/build/q141k/e191.T0"); ll3ar=$([ -e "$RB_OUT/e191-T0.txt" ] && echo 1 || echo 0)
echo "$ST0" > "$BOXT/build/q141k/e191.T0"
ok "$ll3a.$(has "reads $FT0, not $ST0, the second session" "$S/ll3a.txt").$(has 'rest: ' "$S/ll3a.txt").$ll3a2.$(has "reads 1794700002, not $ST0" "$S/ll3a2.txt").$ll3at.$ll3ar" \
  "10.1.0.10.1.1794700002.0" "LL3a refused (10) twice by the box read before the rest rule: the first session's T0 (v2's reference) and another; nothing launched, no T0 written"

step "RS3. the rest rule through step 9 v3: the second session's committed log with its end moved to 10 minutes ago"
cp -p "$BOXT/build/e191/T$ST0/session.log" "$S/s2-session.log.keep"
sedi -e "s/^2026-11-15 14:21:46 PST session end/$(TZ=America/Los_Angeles date -d '-10 min' '+%F %T %Z') session end/" "$BOXT/build/e191/T$ST0/session.log"
bash "$R/s11_a1_session_e191_v3.sh" FULL > "$S/rs3.txt" 2>&1; rs3=$?; stopline "$S/rs3.txt"
cp -p "$S/s2-session.log.keep" "$BOXT/build/e191/T$ST0/session.log"
ok "$rs3.$(has 'REFUSED: 10 minutes since E191' "$S/rs3.txt").$(cat "$BOXT/build/q141k/e191.T0")" "10.1.$ST0" "RS3 refused (10) naming E191, nothing launched"

step "LA3. step 9 v3 launches the REAL session_e191_v2.sh (its box check stops it: this desk is not aifoundry1); step 10 v2 reads the gate"
bash "$R/s11_a1_session_e191_v3.sh" FULL > "$S/la3.txt" 2>&1; la3=$?
grep -E 'LAUNCHED|rest:|last launch:|relaunch' "$S/la3.txt" | cut -c1-260
sleep 3
for i in 1 2 3 4; do RB_WAIT_LOOP_S=20 bash "$R/s20_wait_e191_v2.sh" > "$S/la3w.txt" 2>&1; w=$?; [ "$w" -eq 17 ] || break; done
grep -E 'box check|GATE|MANIFEST|NOTE2' "$S/la3w.txt" | cut -c1-220
t1=$(cat "$RB_OUT/e191-T0.txt" 2>/dev/null)
ok "$la3.$(has "A2's third session, a REPEAT" "$S/la3.txt").$(has "last launch: the box's build/q141k/e191.T0 reads $ST0, the second session's T0" "$S/la3.txt").$(has 'rest: ' "$S/la3.txt").$w.$(has 'MANIFEST-WRITTEN' "$S/la3w.txt").$(has 'NOTE2-SESSION yes' "$S/la3w.txt").$(has 'the box check: this host is' "$S/la3w.txt").$(grep -c 'plan FULL; kit note 2;' "$BOXT/build/e191/T$t1/session.log" 2>/dev/null)" \
  "0.1.1.1.16.1.1.1.1" "LA3 session v2 launched after the last launch and the rest; the real runner v2 stopped at its box check before any device, with its manifest; step 10 v2 reads the gate (16)"

step "LL3b. THE LAST LAUNCH, RB_OUT with a T0: the box's last launch is not that T0"
t1x=$((${t1:-0} + 7)); echo "$t1x" > "$BOXT/build/q141k/e191.T0"
bash "$R/s11_a1_session_e191_v3.sh" FULL > "$S/ll3b.txt" 2>&1; ll3b=$?; stopline "$S/ll3b.txt"
ll3bt=$(cat "$BOXT/build/q141k/e191.T0"); ll3br=$([ -e "$RB_OUT/e191-relaunch.txt" ] && echo 1 || echo 0); ll3bk=$(cat "$RB_OUT/e191-T0.txt" 2>/dev/null)
echo "$t1" > "$BOXT/build/q141k/e191.T0"
ok "$ll3b.$(has "reads $t1x, not $t1, this RB_OUT's e191-T0.txt" "$S/ll3b.txt").$(has 'relaunch: ' "$S/ll3b.txt").$ll3bt.$ll3br.$ll3bk" \
  "10.1.0.$t1x.0.$t1" "LL3b refused (10): the box's last launch is not this RB_OUT's T0; no relaunch, nothing launched"

step "G4a3, G4b3. THE RELAUNCH RULE: step 9 v3 again from that RB_OUT (its T0 opened no device), then a third time"
bash "$R/s11_a1_session_e191_v3.sh" FULL > "$S/g4a.txt" 2>&1; g4a=$?
grep -E 'LAUNCHED|relaunch' "$S/g4a.txt" | cut -c1-240
t2=$(cat "$RB_OUT/e191-T0.txt" 2>/dev/null)
sleep 3
for i in 1 2 3 4; do RB_WAIT_LOOP_S=20 bash "$R/s20_wait_e191_v2.sh" > "$S/g4aw.txt" 2>&1; w2=$?; [ "$w2" -eq 17 ] || break; done
bash "$R/s11_a1_session_e191_v3.sh" FULL > "$S/g4b.txt" 2>&1; g4b=$?; stopline "$S/g4b.txt"
ok "$g4a.$(has "relaunch: this RB_OUT's launch T0 $t1 opened no device" "$S/g4a.txt").$([ -n "$t2" ] && [ "$t2" != "$t1" ] && echo 1 || echo 0).$(grep -c "^$t1 relaunch:" "$RB_OUT/e191-relaunch.txt" 2>/dev/null).$w2.$g4b.$(has 'launched twice already' "$S/g4b.txt").$(cat "$BOXT/build/q141k/e191.T0")" \
  "0.1.1.1.16.10.1.$t2" "G4a3 one launch more after a launch that opened no device (a new T0, e191-relaunch.txt); G4b3 a third launch refused (10) before any call"

step "C3v3, C5v3. step 11 v3 from the second session's RB_OUT; then while an -s3 directory of another day exists"
D3=docs/reports/data/$TODAY-e191-blind-day-aifoundry1-c1-s3
RB_OUT="$S/out-2" bash "$R/s22_collect_e191_v3.sh" > "$S/c3.txt" 2>&1; c3=$?; stopline "$S/c3.txt"
c3n=$(grep -c 'rsync' "$S/calls.log")
OD=docs/reports/data/2026-11-14-e191-blind-day-aifoundry1-c1-s3; [ "$TODAY" = 2026-11-14 ] && OD=docs/reports/data/2026-11-13-e191-blind-day-aifoundry1-c1-s3
mkdir -p "$T/$OD"; echo x > "$T/$OD/README.md"
bash "$R/s22_collect_e191_v3.sh" > "$S/c5.txt" 2>&1; c5=$?; stopline "$S/c5.txt"
rm -rf "${T:?}/$OD"
ok "$c3.$(has 'is an earlier E191 session' "$S/c3.txt").$c5.$(has 'exists already: A2 allows one third session' "$S/c5.txt").$([ -e "$T/$D3" ] && echo 1 || echo 0).$(grep -c 'rsync' "$S/calls.log").$c3n" \
  "10.1.10.1.0.$c3n.$c3n" "C3v3 refused (10): the second session's T0 is never collected into -s3; C5v3 refused (10) while an -s3 of another day exists; nothing written or copied"

step "C2v3, C4v3. step 11 v3 on the relaunched session, then again"
bash "$R/s22_collect_e191_v3.sh" > "$S/c2.txt" 2>&1; c2=$?
grep -E 'COPY-BACK|COLLECTED|HISTORY|STOP' "$S/c2.txt" | cut -c1-220
bash "$R/s22_collect_e191_v3.sh" > "$S/c4.txt" 2>&1; c4=$?
ok "$c2.$(has 'COPY-BACK EXACT' "$S/c2.txt").$(has "COLLECTED $D3" "$S/c2.txt").$([ -f "$T/$D3/SHA256SUMS" ] && [ -f "$T/$D3/FILES.txt" ] && echo 1 || echo 0).$(grep -rlE "/home/|(^|[^A-Za-z0-9_.-])$(id -un)([^A-Za-z0-9_-]|$)" "$T/$D3" 2>/dev/null | grep -c .).$(git -C "$T" status --short -- "$FIRST" "$SECOND" | grep -c .).$c4.$(has 'exists already' "$S/c4.txt")" \
  "0.1.1.1.0.0.10.1" "C2v3 collected exactly into ...-c1-s3 (both earlier records untouched), no home path or login; C4v3 refused (10) the second time"

step "SC0v3, SC3v3, SC4v3. step 13 v3 before the data commit; committed and clean; a changed byte committed in the second record"
bash "$R/s24_score_e191_v3.sh" > "$S/sc0.txt" 2>&1; sc0=$?
$G add --sparse "$D3" > /dev/null 2>&1 && $G commit -q -m "desk test: the third session's collected data directory" > /dev/null 2>&1 || echo "data commit failed"
bash "$R/s24_score_e191_v3.sh" > "$S/sc3.txt" 2>&1; sc3=$?
grep -E 'scored|STOP' "$S/sc3.txt" | cut -c1-400
s2h=$(sha256sum "$RB_OUT/scores-e191-s2.json" 2>/dev/null | cut -c1-64)
f=$SECOND/passes/copy-zeros/p1/energy.txt; echo " " >> "$T/$f"; $G add --sparse "$f" && $G commit -q -m "desk test: a changed byte in the second record" > /dev/null 2>&1
bash "$R/s24_score_e191_v3.sh" > "$S/sc4.txt" 2>&1; sc4=$?; stopline "$S/sc4.txt"
$G reset -q --hard HEAD~1
ok "$sc0.$sc3.$(has 'scored (REPORTED' "$S/sc3.txt").$(has 'REPEAT-E191 REPORTED: 0 configurations compared, 6 with NO DATA' "$S/sc3.txt").$([ -s "$RB_OUT/scores-e191-s3.json" ] && [ -s "$RB_OUT/repeat-e191-s3.json" ] && [ -s "$RB_OUT/repeat-e191-s3.txt" ] && echo 1 || echo 0).$s2h.$sc4.$(has "the second session's SHA256SUMS does not read every entry OK" "$S/sc4.txt").$(git -C "$T" status --short -- "$FIRST" "$SECOND" | grep -c .)" \
  "10.0.1.1.1.$S2SHA.16.1.0" "SC0v3 not committed: 10; SC3v3 scored (REPORTED), the second session's output at the registered bytes, the repeat reading written; SC4v3 a changed byte in the second record: 16"

step "Z. no process of this test left running"
sleep 1
z=$(pgrep -f "$S/" 2>/dev/null | grep -c .)
ok "$z" "0" "Z nothing left"
echo
echo "SELFTEST-RB-E191-V3 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
return "$fail"
}
main 2>&1 | sed "s#$S#<scratch>#g; s#$SRC#<lab clone>#g"
exit "${PIPESTATUS[0]}"
