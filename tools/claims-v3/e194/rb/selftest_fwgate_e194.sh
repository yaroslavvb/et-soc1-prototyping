#!/usr/bin/env bash
# E194, dated amendment A1 (Q187, Sun 15 Nov 2026, before any E194 datum): the desk test of E194's OWN FIRMWARE GATE (rb/fwgate_e194.sh)
# and of the three step versions that read it (step 2 rb/s03_desk_e194_v2.sh, the look rb/s05_look_e194_v2.sh, the session
# rb/s11_session_e194_v2.sh), in the kit's runbook desk test's form (rb/selftest_rb_e194.sh, unchanged beside it): a scratch repository, a
# shared sparse clone of the lab clone this test runs from at the commit BEFORE the amendment (the parent of the commit that added
# tools/claims-v3/e194/E194.md.dated-amendment-A1.md, or HEAD when none has), with the amendment's files committed on top as one stand-in
# amendment commit and its own upstream (a bare copy of itself); a stand-in aifoundry2 whose box tree (~/claude/et-soc1-prototyping under a
# stand-in home) is a git clone of it, served by a FAKE ssh that refuses any other host; the box's `hostname` reads aifoundry2 and its
# `uptime -s` THIS BOX'S REAL BOOT (2026-11-13 16:53:28 PST, before the read of record) unless a case says otherwise. It runs in a
# PRIVATE PID NAMESPACE (rb/selftest_fwgate_e194_ns.sh). No lab box is reached, no device is opened (run it in the sandbox: W/nodev.sh).
# Cases (verdicts stated first):
#   G1  the record, as committed: FWGATE-E194 RECORD EQUAL (0), the gate's own reading naming all seven fields;
#   B1-B6 the boot rule by the very box lines (fwgate_e194.sh boot): this box's boot 2026-11-13 16:53:28 ok (0); a boot after the read
#       (2026-11-15 15:30:00) STOP (16); a boot at the read's own second (15:22:02) STOP; one second before it (15:22:01) ok; an unreadable
#       boot STOP; another box (aifoundry3) STOP;
#   D1  A DIFFERENT RECORD: the read's PMIC field changed (1.5.0 -> 1.5.1) in a commit: REFUSED (16) naming DIFFERENT(PMIC ...), the list,
#       the tree and the comparison's rc 1;  D2 the same change made consistent (its SHA256SUMS and comparison.txt re-made from it): REFUSED
#       (DIFFERENT, the list's bytes, the tree);  D3 E69's own statement changed instead (CHANGE-RECORD.md's PMIC): REFUSED (E69's bytes, the
#       comparison's PARSE-FAILED: the two statements disagree);
#   M1  A MISSING RECORD: the directory removed in a commit: REFUSED (missing);  M2 one file of it (fwread.stderr) gone from the worktree:
#       REFUSED (missing);  U1 an uncommitted edit of its README: REFUSED (its bytes, uncommitted);
#   K6  the v2 launch's guard text: its first three lines are k6's rb_guard_text's lines before k6's firmware block, byte for byte; k6's
#       FWREAD and E69 lines absent; E194's boot lines present;
#   LK1 the v2 look on the stand-in box, this boot, the record EQUAL: FREE (0), the identity line naming E194's firmware read of record;
#   LK2 the v2 look with a boot after the read: 16;  LK3 with the DIFFERENT record (D1's commit): 16 BEFORE ANY BOX CALL;  LK4 with the
#       record missing (M1's commit): 16 before any box call;
#   IS1 the v2 session step with a boot after the read: IDENTITY-STOP (16), nothing launched;  IS2 with the DIFFERENT record: 16 before any
#       box call, nothing launched;  IS3 with the record missing: 16 before any box call, nothing launched;
#   LA1 the v2 session step with this boot and the record EQUAL: past the gate (its identity line ok), the rest, today's dry pass and build
#       and the P2 count read, then LAUNCHED (0): the session it starts is a STAND-IN session_e194.sh in the stand-in box tree (writes one
#       file, opens nothing);
#   P1  step 2 v2 on the scratch repository: 0, every pin (the amendment's list and the read's among them), FWGATE-E194 RECORD EQUAL, the
#       only E194 data in any ref the read of record;  P2 a second E194 data commit in a ref: 16 naming e194-data;  P3 the DIFFERENT record
#       committed: 16 naming the read's list and fwgate-record;  P4 the amendment's list one line short: 16 naming it;
#   N1  (A1-8, added before the land after verify-amend194's finding F2) a stand-in E191 third-session folder at HEAD
#       (docs/reports/data/2026-11-16-e191-blind-day-aifoundry1-c1-s3/, E191's second session's committed bytes copied, so it names the
#       instance): step 2 v2 0, the folder left out and named in the never-run check's line and in the step's last line;  N2 a folder of
#       another form at HEAD (...-c1-s4, the same bytes): 16 naming never-ran;  N3 the third-session form in the worktree but not at HEAD
#       (uncommitted): 16 naming never-ran;
#   DL  the v2 dry listing: every step 0, no call to the stand-ins, every printed call to aifoundry2 alone; desk/drylisting_check_e194.py PASS;
#   Z   no process of this test left running.
#   bash tools/claims-v3/e194/rb/selftest_fwgate_e194_ns.sh <scratch dir> > <log>   (prints SELFTEST-FWGATE-E194 <n> of <m> PASS or FAIL)
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
for v in RB_PROBE_S RB_READ_S RB_COPY_S RB_WAIT_S RB_LAUNCH_S RB_DESK_S RB_DESKTEST RB_GITLOCK RB_REPO RB_OUT RB_QUIET; do
  [ -z "${!v:-}" ] || { echo "$v is set: this test sets its own"; exit 2; }
done
for c in timeout sha256sum flock git; do command -v "$c" > /dev/null || { echo "no $c on PATH"; exit 2; }; done
date --version 2> /dev/null | grep -q 'GNU coreutils' || { echo "no GNU date"; exit 2; }
ls /dev/et* > /dev/null 2>&1 && { echo "REFUSED: a /dev/et* node is visible: run this inside the sandbox"; exit 3; }
sedi() { local f=${!#} t; t=$(mktemp "${TMPDIR:-/tmp}/sedi.XXXXXX") || return 2; sed "${@:1:$(($# - 1))}" "$f" > "$t" && cat "$t" > "$f"; local r=$?; rm -f "$t"; return "$r"; }
REAL_TIMEOUT=$(command -v timeout)
mkdir -p "$S"; S=$(cd "$S" && pwd)
for d in tree box bin boxbin; do [ -e "$S/$d" ] && { echo "$S/$d exists: give an empty scratch directory"; exit 2; }; done
T=$S/tree; B=$S/box; BIN=$S/bin; BOXT=$B/aifoundry2/claude/et-soc1-prototyping
mkdir -p "$B/aifoundry2/claude" "$BIN" "$S/boxbin"
E=tools/claims-v3/e194
FW=docs/reports/data/2026-11-15-e194-fwread-aifoundry2
main() {
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
has() { grep -aq -- "$1" "$2" && echo 1 || echo 0; }
stopline() { grep -a 'STOP\|REFUSED' "$1" | tail -n 1 | cut -c1-400; }
calls() { grep -c . "$S/calls.log"; }
echo "selftest_fwgate_e194: $(date '+%F %T %Z'), processes visible: $(ls /proc | grep -c '^[0-9]')"
# ---- the scratch repository: a shared sparse clone at the commit before the amendment, its files as one stand-in commit, its own upstream
AMC=$(git -C "$SRC" log --diff-filter=A --format=%H -- $E/E194.md.dated-amendment-A1.md | tail -n 1)
if [ -n "$AMC" ]; then BASE=$(git -C "$SRC" rev-parse "$AMC^"); else BASE=$(git -C "$SRC" rev-parse HEAD); fi
git clone -q --shared --no-checkout "$SRC" "$T" || return 2
G="git -C $T -c user.name=e194-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G sparse-checkout set --no-cone /tools/ /workloads/ /docs/reports/data/2026-11-12-q166-progs/ /docs/reports/data/2026-11-12-q166-ledger-v2/ \
  /docs/reports/data/2026-11-12-q166-counter-sparseparity/ /docs/reports/data/2026-09-23-energy-manual/ /docs/reports/data/2026-10-26-load-model/ \
  /docs/reports/data/2026-11-13-e190-large-gemm/ /docs/reports/data/2026-11-14-e189-blind-day-aifoundry3/ \
  /docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1/ /docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2/ \
  /docs/reports/data/2026-10-27-e69-governor-knob/ '/docs/reports/data/*-e194-*/' || return 2
$G checkout -q -B main "$BASE" || return 2
( cd "$SRC" && git ls-files --others --exclude-standard -- $E; git diff --name-only -- $E; [ -n "$AMC" ] && git show "$AMC" --name-only --format= -- $E ) | sort -u | while IFS= read -r f; do
  [ -f "$SRC/$f" ] || continue; mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
for spec in "selftest-fwgate-e194.txt SELFTEST-FWGATE-E194 0 of 0 PASS" \
            "dry-listing-e194-v2.txt dry listing: 0 steps listed, 0 exited non-zero, 0 box calls beyond aifoundry2"; do
  f=${spec%% *}   # this test's own log (being written by this run) gets its stand-in line, as does a log the clone lacks
  if [ "$f" = selftest-fwgate-e194.txt ] || [ ! -f "$T/$E/logs/$f" ]; then printf '%s\n' "${spec#* }" > "$T/$E/logs/$f"; fi
done
[ -f "$T/$E/E194.md.dated-amendment-A1.md" ] || { echo "the amendment's text is not in the lab clone this test runs from"; return 2; }
mklist() {  # the stand-in amendment list (the real list's rule: every file of the amendment but the list itself and step 2 v2)
  ( cd "$T" && git status --porcelain --untracked-files=all -- $E | sed 's/^...//'; git diff --name-only "$BASE" -- $E ) | sort -u |
    grep -v -e "^$E/SHA256SUMS-e194-amendment-A1\$" -e "^$E/rb/s03_desk_e194_v2.sh\$" | grep -v '\.pyc$' | LC_ALL=C sort > "$S/amend-files.txt"
  ( cd "$T" && while IFS= read -r f; do [ -f "$f" ] && sha256sum "$f"; done < "$S/amend-files.txt" ) > "$S/amend-standin.txt"
  AMN=$(grep -c . "$S/amend-standin.txt"); cp "$S/amend-standin.txt" "$T/$E/SHA256SUMS-e194-amendment-A1"; AMH=$(sha256sum "$S/amend-standin.txt" | cut -d' ' -f1)
  sedi -e "s#^AMENDPIN=$E/SHA256SUMS-e194-amendment-A1:[^ ]*#AMENDPIN=$E/SHA256SUMS-e194-amendment-A1:$AMN:$AMH:top#" "$T/$E/rb/s03_desk_e194_v2.sh"
}
mklist
$G add -A $E && $G commit -q -m "E194 A1 desk test: the amendment's files (stand-in amendment commit)" || { echo "the scratch amendment commit failed"; return 2; }
grep -q "^AMENDPIN=$E/SHA256SUMS-e194-amendment-A1:$AMN:$AMH:top" "$T/$E/rb/s03_desk_e194_v2.sh" || { echo "the scratch step 2's AMENDPIN was not set"; return 2; }
git clone -q --bare "$T" "$S/origin.git" && $G remote set-url origin "$S/origin.git" && $G fetch -q origin && $G branch -q -u origin/main main || return 2
GOOD=$($G rev-parse HEAD)
echo "scratch repository: a shared sparse clone at ${BASE:0:12} (the commit before the amendment), the amendment as one stand-in commit ${GOOD:0:12} ($AMN files in its stand-in list), its own upstream"
# ---- the stand-ins
git clone -q "$T" "$BOXT" || { echo "the stand-in box tree clone failed"; return 2; }
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry2) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
[ "\$cmd" = true ] && exit 0
cat | HOME="$B/\$host" PATH="$S/boxbin:\$PATH" bash -c "cd ~ && \$cmd"
EOF
printf '#!/bin/sh\necho aifoundry2\n' > "$S/boxbin/hostname"
cat > "$S/boxbin/uptime" <<EOF
#!/bin/sh
if [ "\$1" = -s ]; then if [ -e "$S/boot-late" ]; then echo "2026-11-15 15:30:00"; else echo "2026-11-13 16:53:28"; fi; exit 0; fi
exec /usr/bin/uptime "\$@"
EOF
printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$S/boxbin/python3"
printf '#!/bin/sh\necho "No process holds an ET-SoC-1 device node or card lock."\n' > "$S/boxbin/et-who"
printf '#!/bin/sh\nexec "$@"\n' > "$S/boxbin/setsid"
printf '#!/bin/sh\nexec "%s" "$@"\n' "$REAL_TIMEOUT" > "$S/boxbin/timeout"
for n in rsync scp sudo dev_mngt_service ettelem; do printf '#!/bin/sh\necho "BOX STAND-IN: %s refused" >&2\nexit 97\n' "$n" > "$S/boxbin/$n"; done
chmod +x "$BIN/ssh" "$S/boxbin"/*
export PATH="$BIN:$PATH" RB_REPO="$T" RB_LOCK="$S/lock.txt" RB_DESKTEST=1 E194_DESK_BUDGET_S=60 RB_QUIET="$S/quiet-flag"
: > "$S/calls.log"; : > "$S/gitlock"; : > "$RB_LOCK"
R=$T/$E/rb
TODAY=$(TZ=America/Los_Angeles date +%F)
cd "$T" || return 2

step "G1. the record, as committed"
bash "$R/fwgate_e194.sh" record "$T" > "$S/g1.txt" 2>&1; g1=$?
cat "$S/g1.txt" | cut -c1-260
ok "$g1.$(has 'FWGATE-E194 RECORD EQUAL: ' "$S/g1.txt").$(has 'release=1.4.0 BL1=0.22.0 BL2=0.22.0 PMIC=1.5.0 Master Minion=0.25.1 Worker Minion=0.25.1 Machine Minion=0.25.1' "$S/g1.txt")" "0.1.1" \
  "G1 the record as committed reads EQUAL, by its comparison re-run and the gate's own reading of all seven fields"

step "B1-B6. the boot rule, by the box lines themselves"
br() { bash "$R/fwgate_e194.sh" boot "$@" > "$S/b.txt" 2>&1; echo "$?$(grep -c ': ok$' "$S/b.txt")"; }
b1=$(br '2026-11-13 16:53:28'); b2=$(br '2026-11-15 15:30:00'); b3=$(br '2026-11-15 15:22:02'); b4=$(br '2026-11-15 15:22:01'); b5=$(br 'not a time'); b6=$(br '2026-11-13 16:53:28' aifoundry3)
echo "   this boot $b1; after the read $b2; at the read's second $b3; one second before $b4; unreadable $b5; another box $b6 (rc then the count of ok lines)"
ok "$b1.$b2.$b3.$b4.$b5.$b6" "01.160.160.01.160.160" "B1 this boot ok; B2 after the read STOP; B3 at its second STOP; B4 a second before ok; B5 unreadable STOP; B6 another box STOP"

step "D1. a DIFFERENT record: the read's PMIC field 1.5.0 -> 1.5.1, committed"
sedi -e 's/PMIC Firmware versions: Major: 1 Minor: 5 Revision: 0$/PMIC Firmware versions: Major: 1 Minor: 5 Revision: 1/' "$T/$FW/fwread.stderr"
$G add --sparse "$FW/fwread.stderr" && $G commit -q -m "desk test: a DIFFERENT record (PMIC)"; DIFF1=$($G rev-parse HEAD)
bash "$R/fwgate_e194.sh" record "$T" > "$S/d1.txt" 2>&1; d1=$?
grep 'REFUSED' "$S/d1.txt" | cut -c1-400
ok "$d1.$(has 'DIFFERENT(PMIC reads 1.5.1, E69' "$S/d1.txt").$(has 'list(SHA256SUMS 7 OK of 8' "$S/d1.txt").$(has ' tree(' "$S/d1.txt").$(has 'compare(rc 1)' "$S/d1.txt")" "16.1.1.1.1" \
  "D1 refused, naming the DIFFERENT field, the list, the tree and the comparison's rc 1"

step "D2. the same change made consistent: its SHA256SUMS and comparison.txt re-made from the changed read"
( cd "$T" && /usr/bin/python3 -I -B "$FW/compare_fwread.py" "$FW" > "$FW/comparison.txt" 2> /dev/null
  cd "$T/$FW" && sha256sum compare_fwread.py comparison.txt etiquette-after.txt etiquette-before.txt fwread.meta.txt fwread.stderr fwread.stdout kernel-log-after.txt > SHA256SUMS )
$G add --sparse "$FW" && $G commit -q -m "desk test: the DIFFERENT record made consistent"
bash "$R/fwgate_e194.sh" record "$T" > "$S/d2.txt" 2>&1; d2=$?
grep 'REFUSED' "$S/d2.txt" | cut -c1-400
ok "$d2.$(has 'DIFFERENT(PMIC reads 1.5.1' "$S/d2.txt").$(has 'list-bytes(SHA256SUMS' "$S/d2.txt").$(has ' tree(' "$S/d2.txt").$(has 'list(SHA256SUMS' "$S/d2.txt")" "16.1.1.1.0" \
  "D2 refused: DIFFERENT by the gate's own reading, the list's bytes off their pin, the tree not as committed (its list itself reads OK)"
$G reset -q --hard "$GOOD"

step "D3. E69's own statement changed (CHANGE-RECORD.md's PMIC 1.5.0 -> 1.5.1), committed"
sedi -e '68s/PMIC \*\*1\.5\.0\*\*/PMIC **1.5.1**/' "$T/tools/claims-v3/knob/CHANGE-RECORD.md"
$G commit -q -am "desk test: E69's statement changed"
bash "$R/fwgate_e194.sh" record "$T" > "$S/d3.txt" 2>&1; d3=$?
grep 'REFUSED' "$S/d3.txt" | cut -c1-400
ok "$d3.$(has 'e69-change-record(' "$S/d3.txt").$(has 'PARSE-FAILED' "$S/d3.txt")" "16.1.1" "D3 refused: E69's statement off its pin; the comparison cannot parse two statements that disagree"
$G reset -q --hard "$GOOD"

step "M1, M2, U1. a missing record (its directory removed in a commit; one file gone from the worktree); an uncommitted edit"
$G rm -q -r --sparse "$FW" && $G commit -q -m "desk test: the record removed"; MISS=$($G rev-parse HEAD)
bash "$R/fwgate_e194.sh" record "$T" > "$S/m1.txt" 2>&1; m1=$?; grep 'REFUSED' "$S/m1.txt" | cut -c1-300
$G reset -q --hard "$GOOD"
rm -f "${T:?}/$FW/fwread.stderr"
bash "$R/fwgate_e194.sh" record "$T" > "$S/m2.txt" 2>&1; m2=$?; grep 'REFUSED' "$S/m2.txt" | cut -c1-300
$G checkout -q -- "$FW"
printf '\n' >> "$T/$FW/README.md"
bash "$R/fwgate_e194.sh" record "$T" > "$S/u1.txt" 2>&1; u1=$?; grep 'REFUSED' "$S/u1.txt" | cut -c1-300
$G checkout -q -- "$FW"
ok "$m1.$(has 'missing(the record' "$S/m1.txt").$m2.$(has 'missing(fwread.stderr)' "$S/m2.txt").$u1.$(has 'readme-bytes(' "$S/u1.txt").$(has 'uncommitted(1 path' "$S/u1.txt")" "16.1.16.1.16.1.1" \
  "M1 the directory gone: refused (missing); M2 one file gone: refused (missing); U1 an uncommitted README edit: refused (its bytes, uncommitted)"

step "K6. the v2 launch's guard text against k6's"
( . "$R/rb_e194.sh"; rb_guard_text | awk '/^case "\$BOX" in/ {exit} {print}' ) > "$S/k6-head.txt"
( . "$R/rb_e194.sh"; . "$R/fwgate_e194.sh"; e194_guard_text_a1 ) > "$S/a1-guard.txt"
head -n 3 "$S/a1-guard.txt" | cmp -s - "$S/k6-head.txt"; k6=$?
ok "$k6.$(grep -c . "$S/k6-head.txt").$(grep -c "2026-10-27 13:56:26\|E69's firmware read" "$S/a1-guard.txt").$(has 'FWREAD_EPOCH=1794784922' "$S/a1-guard.txt").$(has 'IDENTITY-STOP: ' "$S/a1-guard.txt")" "0.3.0.1.1" \
  "K6 k6's three lines byte for byte, k6's E69 block absent, E194's boot rule present"

export RB_OUT="$S/out-b"; mkdir -p "$RB_OUT"
bash "$R/s02_window_e194.sh" "$TODAY" 23:58 23:59 > "$S/window.txt" 2>&1 || { cat "$S/window.txt"; echo "the window could not be written"; return 2; }
bash "$R/quiet_e194.sh" raise card-e194-desktest > /dev/null
step "LK1-LK4. the v2 look"
: > "$S/calls.log"; bash "$R/s05_look_e194_v2.sh" > "$S/lk1.txt" 2>&1; lk1=$?
grep -E 'identity:|FREE|STOP' "$S/lk1.txt" | cut -c1-260
touch "$S/boot-late"; bash "$R/s05_look_e194_v2.sh" > "$S/lk2.txt" 2>&1; lk2=$?; rm -f "$S/boot-late"; stopline "$S/lk2.txt"
$G checkout -q "$DIFF1"; : > "$S/calls.log"; bash "$R/s05_look_e194_v2.sh" > "$S/lk3.txt" 2>&1; lk3=$?; lk3c=$(calls); stopline "$S/lk3.txt"
$G checkout -q "$MISS"; : > "$S/calls.log"; bash "$R/s05_look_e194_v2.sh" > "$S/lk4.txt" 2>&1; lk4=$?; lk4c=$(calls); stopline "$S/lk4.txt"
$G checkout -q main
ok "$lk1.$(has "identity: the host booted 2026-11-13 16:53:28, before E194's firmware read of record of 2026-11-15 15:22:02 PST" "$S/lk1.txt").$lk2.$(has "did not boot before E194's firmware read of record" "$S/lk2.txt").$lk3.$lk3c.$(has 'DIFFERENT(PMIC' "$S/lk3.txt").$lk4.$lk4c.$(has 'missing(' "$S/lk4.txt")" \
  "0.1.16.1.16.0.1.16.0.1" "LK1 FREE with the identity ok; LK2 a boot after the read: 16; LK3 the DIFFERENT record: 16 before any box call; LK4 the record missing: 16 before any box call"

step "IS1-IS3, LA1. the v2 session step"
rm -f "$RB_OUT/hold-aifoundry2.since"
echo "ledger,spp" > "$RB_OUT/e194-built.txt"
mkdir -p "$BOXT/build/q141k/jobs"
echo 0 > "$BOXT/build/q141k/jobs/a2-dry-e194.rc"
printf 'LEDGER-BUILT rc=0 (desk-test stand-in)\nSPP-BUILT rc=0 (desk-test stand-in)\n' > "$BOXT/build/q141k/jobs/a2-build-e194.out"
printf '#!/bin/bash\n# E194 A1 desk test: a STAND-IN session (it opens nothing)\nmkdir -p build/e194\necho "stand-in session ran: T0 ${E194_T0:-none} programs ${E194_PROGRAMS:-none}" > build/e194/standin-ran.txt\n' > "$BOXT/$E/session_e194.sh"
touch "$S/boot-late"; : > "$S/calls.log"; bash "$R/s11_session_e194_v2.sh" FULL > "$S/is1.txt" 2>&1; is1=$?; rm -f "$S/boot-late"; stopline "$S/is1.txt"
is1n=$(ls "$BOXT/build/e194" 2>/dev/null | grep -c .)
$G checkout -q "$DIFF1"; : > "$S/calls.log"; bash "$R/s11_session_e194_v2.sh" FULL > "$S/is2.txt" 2>&1; is2=$?; is2c=$(calls); stopline "$S/is2.txt"
$G checkout -q "$MISS"; : > "$S/calls.log"; bash "$R/s11_session_e194_v2.sh" FULL > "$S/is3.txt" 2>&1; is3=$?; is3c=$(calls); stopline "$S/is3.txt"
$G checkout -q main
is23n=$(ls "$BOXT/build/e194" 2>/dev/null | grep -c .)
ok "$is1.$(has "IDENTITY-STOP: aifoundry2 booted '2026-11-15 15:30:00', not before E194's firmware read of record" "$S/is1.txt").$is1n.$is2.$is2c.$(has 'DIFFERENT(PMIC' "$S/is2.txt").$is3.$is3c.$(has 'missing(' "$S/is3.txt").$is23n" \
  "16.1.0.16.0.1.16.0.1.0" "IS1 IDENTITY-STOP, nothing launched; IS2 the DIFFERENT record and IS3 the record missing: 16 before any box call, nothing launched"
bash "$R/s11_session_e194_v2.sh" FULL > "$S/la1.txt" 2>&1; la1=$?
grep -E 'identity:|LAUNCHED|rest:|quiet desk|STOP' "$S/la1.txt" | cut -c1-240
sleep 1
ok "$la1.$(has "identity: aifoundry2 booted 2026-11-13 16:53:28, before E194's firmware read of record" "$S/la1.txt").$(has 'LAUNCHED e194 T0 ' "$S/la1.txt").$(grep -c 'stand-in session ran: T0 [0-9]* programs ledger,spp' "$BOXT/build/e194/standin-ran.txt" 2>/dev/null)" "0.1.1.1" \
  "LA1 past the gate (identity ok), the rest, the dry pass, the build and the P2 count: LAUNCHED, the stand-in session ran"

step "P1-P4. step 2 v2"
RB_OUT="$S/out-p" bash "$R/s02_window_e194.sh" "$TODAY" 23:58 23:59 > /dev/null 2>&1
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e194_v2.sh" > "$S/p1.txt" 2>&1; p1=$?
grep -E 'desk check v2:|STOP' "$S/p1.txt" | cut -c1-700
$G branch -q e194-data-standin; $G checkout -q e194-data-standin; mkdir -p "$T/docs/reports/data/2026-11-15-e194-x"; echo x > "$T/docs/reports/data/2026-11-15-e194-x/README.md"
$G add --sparse docs/reports/data/2026-11-15-e194-x/README.md; $G commit -q -m "desk test: E194 data in a ref"; $G checkout -q main
rm -rf "${T:?}/docs/reports/data/2026-11-15-e194-x"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e194_v2.sh" > "$S/p2.txt" 2>&1; p2=$?; $G branch -q -D e194-data-standin; stopline "$S/p2.txt"
$G checkout -q "$DIFF1" -- "$FW/fwread.stderr" && $G commit -q -m "desk test: the DIFFERENT record (D1's change) on main"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e194_v2.sh" > "$S/p3.txt" 2>&1; p3=$?; $G reset -q --hard "$GOOD"; stopline "$S/p3.txt"
sedi -e '$d' "$T/$E/SHA256SUMS-e194-amendment-A1"; $G commit -q -am "desk test: the amendment's list one line short"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e194_v2.sh" > "$S/p4.txt" 2>&1; p4=$?; $G reset -q --hard "$GOOD"; stopline "$S/p4.txt"
ok "$p1.$(has "the amendment's ($AMN) and the firmware read's (8)" "$S/p1.txt").$(has 'the only E194 data in any ref the firmware read of record (15cb0fcbfb11), FWGATE-E194 RECORD EQUAL' "$S/p1.txt").$p2.$(has 'e194-data(2 commit(s)' "$S/p2.txt").$p3.$(has 'SHA256SUMS(7 OK of 8; pinned 8' "$S/p3.txt").$(has 'fwgate-record' "$S/p3.txt").$p4.$(has "SHA256SUMS-e194-amendment-A1($((AMN - 1)) OK of $((AMN - 1)); pinned $AMN" "$S/p4.txt")" \
  "0.1.1.16.1.16.1.1.16.1" "P1 step 2 v2 passes at every pin, the read of record the only E194 data, the gate's record EQUAL; P2 a second E194 data commit: 16; P3 the DIFFERENT record: 16 (its list, the gate); P4 the amendment's list short: 16"

step "N1-N3. step 2 v2's never-run check and E191's third-session folders (A1-8)"
S2D=docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2
standin() { mkdir -p "$T/docs/reports/data/$1" && cp -R "$T/$S2D/." "$T/docs/reports/data/$1/"; }   # s2's committed bytes under another name
inwt() { find "$T/docs/reports/data/$1" -type f 2> /dev/null | grep -c .; }
N3D=2026-11-16-e191-blind-day-aifoundry1-c1-s3; N4D=2026-11-16-e191-blind-day-aifoundry1-c1-s4
standin "$N3D"; $G add --sparse "docs/reports/data/$N3D" && $G commit -q -m "desk test: a stand-in E191 third-session folder at HEAD (s2's bytes)"
n1w=$(inwt "$N3D")
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e194_v2.sh" > "$S/n1.txt" 2>&1; n1=$?
grep -a -o "NEVER RAN with [^;]*" "$S/n1.txt" | cut -c1-300; stopline "$S/n1.txt"
n1l=$(has "and E191's third-session folders at HEAD (1: $N3D) (A1-8)" "$S/out-p/runbook.log")
rm -rf "${T:?}/docs/reports/data/${N3D:?}"; $G reset -q --hard "$GOOD"; n1g=$(inwt "$N3D")   # (the files go first: a sparse reset warns)
standin "$N4D"; $G add --sparse "docs/reports/data/$N4D" && $G commit -q -m "desk test: a stand-in folder of another form at HEAD (-s4, s2's bytes)"
n2w=$(inwt "$N4D")
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e194_v2.sh" > "$S/n2.txt" 2>&1; n2=$?; stopline "$S/n2.txt"
rm -rf "${T:?}/docs/reports/data/${N4D:?}"; $G reset -q --hard "$GOOD"; n2g=$(inwt "$N4D"); n2s=$($G status --porcelain | grep -c .)
standin "$N3D"; n3w=$(inwt "$N3D")
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e194_v2.sh" > "$S/n3.txt" 2>&1; n3=$?; stopline "$S/n3.txt"
rm -rf "${T:?}/docs/reports/data/${N3D:?}"
echo "   files in the worktree: N1 $n1w (after its reset $n1g), N2 $n2w (after its reset $n2g; status lines $n2s), N3 $n3w (uncommitted)"
ok "$n1.$([ "$n1w" -gt 0 ] && echo 1 || echo 0).$(has "and E191's third-session folders at HEAD (1: $N3D)" "$S/n1.txt").$n1l.$n1g.$n2.$([ "$n2w" -gt 0 ] && echo 1 || echo 0).$(has 'failed:.* never-ran' "$S/n2.txt").$n2g.$n2s.$n3.$([ "$n3w" -gt 0 ] && echo 1 || echo 0).$(has 'failed:.* never-ran' "$S/n3.txt")" \
  "0.1.1.1.0.16.1.1.0.0.16.1.1" "N1 a stand-in third-session folder at HEAD: 0, left out and named (the check's line, the last line); N2 a folder of another form (-s4) at HEAD: 16 (never-ran); N3 the third-session form in the worktree, not at HEAD (nothing else there): 16 (never-ran)"

step "DL. the v2 dry listing"
bash "$R/list_steps_e194_v2.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; dl=$?
/usr/bin/python3 -I -B "$T/$E/desk/drylisting_check_e194.py" "$S/dry-listing.txt" > "$S/dry-check.txt" 2>&1; dc=$?
tail -n 1 "$S/dry-listing.txt"; tail -n 1 "$S/dry-check.txt"
ok "$dl.$(grep -c . "$S/dry-out/box-calls.txt").$dc.$(grep -c 'fwgate_e194.sh record' "$S/dry-listing.txt")" "0.0.0.3" \
  "DL every step 0, no call to the stand-ins, every printed call to aifoundry2 alone, the listing check PASS; the gate's record named in steps 2, 4 and 9"
bash "$R/quiet_e194.sh" lower card-e194-desktest > /dev/null

step "Z. no process of this test left running"
sleep 1
z=$(pgrep -f "$S/" 2>/dev/null | grep -c .)
ok "$z" "0" "Z nothing left"
echo
echo "SELFTEST-FWGATE-E194 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
return "$fail"
}
main 2>&1 | sed "s#$S#<scratch>#g; s#$SRC#<lab clone>#g"
exit "${PIPESTATUS[0]}"
