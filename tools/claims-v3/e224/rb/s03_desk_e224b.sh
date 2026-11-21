#!/usr/bin/env bash
# E224 ARM B (Q237, lane kit-e224, Fri 20 Nov 2026, before any E224 datum; E216's kit's rb/s03_desk_e216.sh form, landed in 59f5288b, with
# E215's lesson that step 2 never rewrites a registered file): runbook step 2, THE DESK CHECK (outside the kit's own list SHA256SUMS-e224-kit, so
# that it can pin that list's own bytes; nothing in HEAD pins this file, so the card lane compares its sha256 with the land's anchor before
# running it: the card-lane brief, step 2). Run in the lab clone LAB on aifoundry2, after step 1, inside THE ONE-LAB RULE's desk span (onelab
# desk before step 0, undesk right after this step), never inside the lab-git lock. Reads only, but for one thing: when LAB's HEAD is behind
# GitHub's main, clean, and an ancestor of it, it fast-forwards LAB under the lab-git lock. IT RUNS NO REGISTERED MAKER (forecast_e224.py,
# rules_e224.py, plan_e224.py, desk/point_rule_e224.py and the scorer's --selftest-* modes write registered files when run: never here); every
# output it makes goes to RB_OUT.
#   RB_OUT=<the day's folder> RB_GITLOCK=<W/locks/lab-git.lock> RB_W=<the round's folder> RB_LANE=<the card lane> \
#     [RB_SEALED=<the round's sealed-forecast record for E224>] bash tools/claims-v3/e224/rb/s03_desk_e224b.sh
# Checks, in order (any one not as stated: exit 10, nothing else done):
#   1. the window (step 1 today); 1o. outside a desk test, THE ONE-LAB RULE's desk span: RB_W's onelab.sh shows desk-<RB_LANE> (in a desk test
#   the span is reported, never required); 2. HEAD = GitHub's main (git ls-remote, the environment-only HTTPS rewrite), after the fast-forward
#   if one is due; 3. the paths E224 runs from are clean; 4. E224's registration and kit are in HEAD, found by content (the commits that added
#   E224.md and KIT.md), the registration first; 4h. THE HISTORY CHECK (rb/check_history_e224b.py tree: the registration's subtree a46c1682...,
#   additions only under tools/claims-v3/e224 since it, net and commit by commit, no shadowing module under tools/, the run paths clean); 5.
#   THE LISTS E224 READS at their pinned counts AND their own pinned sha256 AND every entry OK (no override outside a desk test): E224's
#   registration list, its kit list (both arms), MM1-v3.2's, MM1-v3.1's, MM1-v3's and MM1-v2's folders as landed, E208's registration list and
#   its kit's src/ list; every other file with "SHA256SUMS" in its name under tools/claims-v3/e224 is REPORTED (never a gate); 6. THE FROZEN
#   SCORER'S TWO SELF-TESTS through rb/scorer_check_e224.py (score_e224.py imported unchanged; its stand-in and real-bytes self-tests written
#   into RB_OUT and compared with the registered selftest-standins.json and selftest-real.json byte for byte: the scorer's own --selftest-*
#   modes write those registered files in place, so they are never run here); 6t. the kit's timeout table (desk/timeout_e224.py --check: re-made
#   from committed bytes, CHECK PASS: every process's plain 10 s); 7. make_box_e224b.py check: CHECK PASS (the box root's every file at its sha256:
#   E208's kit, E224's box files and inputs, rgm211's sources, fwgate; the schedule re-made from the registration's plan and points and the
#   timeout table); 8. preflight_e224b.sh: dmcmd_audit_v2 GO over every file whose commands the session or the runbook can send (no --allow);
#   8k. the kit's desk-test logs in HEAD, each ending in its PASS line; 9. THE FREEZE LINE: E224's registration commit in HEAD (its push froze
#   every E224 forecast), printed with its committer time and any sealed forecast registered for E224 (tools/claims-v3/sealed-e224/
#   e224-freeze-lines*.md); 10. THE SEALED RECORD (rb/s00_sealed_e224b.sh: every sha256 RB_SEALED lists on a line that is not a comment
#   registered in tools/claims-v3/sealed-e224/e224-freeze-lines.md at HEAD; else do not book, tell the orchestrator: the E206 lesson); 11. no
#   E224 arm B datum in any ref (docs/reports/data/*-e224-blind-matmul-aifoundry2*); 12. HEAD unchanged since check 2.
# Desk tests only (RB_DESKTEST=1): RB_GITHUB names GitHub's main (no fast-forward then), RB_E224B_KITPIN the kit list's pin (a stand-in kit).
# Writes RB_OUT/step2.txt and ends "STEP2 PASS (HEAD <sha>)". Exit 0 PASS; 10 refused; 17 call again (GitHub or the lab-git lock busy).
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e224b.sh"
rb_init s03_desk
e224b_window
cd "$RB_REPO" || rb_die 10 "cannot enter the lab clone"
E=$E224B_REL
# the lists, each <path>:<lines>:<its own sha256>:<where its paths start: top = the lab's top, dir = the list's folder, up = its parent>
REGPIN=tools/claims-v3/e224/SHA256SUMS-e224-registration:31:9420b5d1a4c88ad78f4e3141847e12aeb276b8ee4dc4ee239ce7aba045bf6355:top   # the registration's list (reg-e224's)
KITPIN=tools/claims-v3/e224/SHA256SUMS-e224-kit:120:3b8b2b9140dea4f82b38abf330f7dbd3633358f0e809cf75c54b93b24eec8249:top   # set at the kit's commit (its count and its own bytes; both arms' files)
[ -n "${RB_E224B_KITPIN:-}" ] && { [ "${RB_DESKTEST:-}" = 1 ] || rb_die 10 "RB_E224B_KITPIN outside a desk test: refused"; KITPIN=$RB_E224B_KITPIN; }
if [ "${RB_DESKTEST:-}" = 1 ]; then
  ONELAB_SPAN="not required in a desk test"
else
  rb_need RB_W RB_LANE
  [ -f "$RB_W/onelab.sh" ] || rb_die 10 "RB_W ($RB_W) holds no onelab.sh"
  bash "$RB_W/onelab.sh" show 2>/dev/null | grep -qx "  desk-$RB_LANE" || rb_die 10 "THE ONE-LAB RULE: $RB_LANE is not in its desk span (bash \$W/onelab.sh desk $RB_LANE before step 0)"
  ONELAB_SPAN="desk-$RB_LANE held"
fi
V32PIN=tools/matmul/mm1/v3.2/SHA256SUMS:58:d52c9cce15db12ed66873722b9ec5c07be1fdeec3027a23833c7e3d230d1d761:dir
V31PIN=tools/matmul/mm1/v3.1/SHA256SUMS:64:f6840d2de6617a739c30485904230e96b744b03b7c82c08b14b6de2d942528ed:dir
V3PIN=tools/matmul/mm1/v3/SHA256SUMS:170:c24efc149110d0cb3d1c8603f0bb7ee83db85eebf9af7ba4254d267c7c85dc74:dir
V2PIN=tools/matmul/mm1/v2/SHA256SUMS:114:eafb6558c4eaa053e4e33b8a4d6b2a644175f325df9e9ba56a1b6373b556f2f2:dir
E8RPIN=tools/claims-v3/e208/SHA256SUMS-e208-registration:57:74e483cfae187c0e2371ab3e3847079095bf650db82755c66ae36d59203696d2:top
E8SPIN=tools/claims-v3/e208/proposal/src/SRC-SHA256SUMS:48:543e9298d5a1013d348c3f38b9a9d9ae26479326a2393fb100c77e3b16b5a6d9:up
PINS="$REGPIN $KITPIN $V32PIN $V31PIN $V3PIN $V2PIN $E8RPIN $E8SPIN"
export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=url.https://github.com/.insteadOf GIT_CONFIG_VALUE_0=git@github.com:
OUTF="$RB_OUT/step2.txt"
: > "$OUTF"
say() { echo "$*"; echo "$*" >> "$OUTF"; }
# 2. GitHub's main
if [ -n "${RB_GITHUB:-}" ]; then MAIN=$RB_GITHUB; else MAIN=$(timeout 60 git ls-remote origin main 2>/dev/null | cut -f1); fi
[ -n "$MAIN" ] || rb_die 17 "GitHub's main could not be read (git ls-remote): call again"
HEAD=$(git rev-parse HEAD)
if [ "$HEAD" != "$MAIN" ]; then
  [ -z "$(git status --porcelain --untracked-files=no)" ] || rb_die 10 "LAB's HEAD $HEAD is not GitHub's main $MAIN and LAB has tracked changes: refused"
  [ -n "${RB_GITHUB:-}" ] && rb_die 10 "a desk test's GitHub stand-in differs from HEAD: refused (no fast-forward in a desk test)"
  rb_need RB_GITLOCK
  flock -w 600 "$RB_GITLOCK" timeout 300 git fetch -q origin main || rb_die 17 "the fetch under the lab-git lock did not end: call again"
  git merge-base --is-ancestor HEAD "$MAIN" 2>/dev/null || rb_die 10 "LAB's HEAD is not an ancestor of GitHub's main: refused"
  flock -w 600 "$RB_GITLOCK" git merge -q --ff-only "$MAIN" || rb_die 17 "the fast-forward under the lab-git lock did not end: call again"
  HEAD=$(git rev-parse HEAD)
  [ "$HEAD" = "$MAIN" ] || rb_die 10 "LAB's HEAD $HEAD is still not GitHub's main $MAIN"
  say "LAB fast-forwarded to GitHub's main under the lab-git lock"
fi
say "1o. THE ONE-LAB RULE: $ONELAB_SPAN"
say "2. HEAD $HEAD = GitHub's main"
# 3. clean
D=$(git status --porcelain --untracked-files=all -- "$E" tools/claims-v3/e208 tools/claims-v3/fwgate tools/matmul/mm1/v3.2 tools/matmul/mm1/v3.2-terms \
  tools/matmul/mm1/v3.1 tools/matmul/mm1/v3 tools/claims-v3/e215 tools/claims-v3/e216 tools/claims-v3/e218 workloads/nocbench/analyze.py \
  docs/reports/data/2026-11-19-e216-blind-matmul-aifoundry2 docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry1-c1 \
  tools/matmul/mm1/v2 tools/claims-v3/e136 tools/claims-v3/e211/rgm211 tools/claims-v3/e206/check_e206.py tools/claims-v3/e206/e206_common.py \
  tools/claims-v3/e213/desk/neverrun_e213.py tools/claims-v3/sealed-e224 tools/claims-v3/dmcmd_audit_v2.py tools/claims-v3/dmcmd_table_v2.json)
[ -z "$D" ] || rb_die 10 "the paths E224 runs from are not clean: $(echo "$D" | head -n 3 | tr '\n' ' ')"
say "3. the paths clean"
# 4. the registration and the kit, by content
REG=$(git log --diff-filter=A --format=%H -- "$E/E224.md" | tail -n 1)
KIT=$(git log --diff-filter=A --format=%H -- "$E/KIT.md" | tail -n 1)
[ -n "$REG" ] && [ -n "$KIT" ] || rb_die 10 "E224's registration or kit is not in HEAD (registration '${REG:-none}', kit '${KIT:-none}')"
git merge-base --is-ancestor "$REG" "$KIT" || rb_die 10 "the kit's commit does not descend from the registration's"
say "4. the registration ${REG:0:12} ($(git log -1 --format='%cd' --date=iso "$REG")), the kit ${KIT:0:12} ($(git log -1 --format='%cd' --date=iso "$KIT")), both in HEAD"
H=$("$PY" -I -B "$E/rb/check_history_e224b.py" tree --reg "$REG" 2>&1 | tail -n 1)
case "$H" in "HISTORY OK"*) ;; *) rb_die 10 "$H" ;; esac
say "4h. $H"
# 5. the lists, pinned
for spec in $PINS; do
  IFS=: read -r l pin hpin form <<EOF2
$spec
EOF2
  [ -f "$l" ] || rb_die 10 "no $l"
  case "$form" in top) cdir=. ;; dir) cdir=$(dirname "$l") ;; up) cdir=$(dirname "$(dirname "$l")") ;; *) rb_die 10 "a pin form '$form'" ;; esac
  m=$(grep -c . "$l"); h=$(sha256sum "$l" | cut -d' ' -f1)
  n=$( (cd "$cdir" && sha256sum -c "$RB_REPO/$l" 2>/dev/null) | grep -c ': OK$')
  why=""; [ "$h" = "$hpin" ] || why="; its own bytes ${h:0:16}, not the pin ${hpin:0:16}"
  [ "$n" -eq "$m" ] && [ "$m" = "$pin" ] && [ -z "$why" ] || rb_die 10 "$(basename "$l"): $n OK of $m lines; pinned $pin$why"
  say "5. $l: $n of $m OK, its own sha256 ${h:0:16} = the pin"
done
unk=""
for f in $(git ls-files -- "$E" | grep SHA256SUMS); do
  case " $PINS " in
    *" $f:"*) ;;
    *) if [ "$f" = "$E/box/SRC-SHA256SUMS-e224b" ]; then unk="$unk $f(the box root's src/ list: check 7 re-makes it)"
       else unk="$unk $f($( (sha256sum -c "$f" 2>/dev/null) | grep -c ': OK$') OK of $(grep -c . "$f"))"; fi ;;
  esac
done
say "5. lists step 2 does not pin (REPORTED, never a gate):${unk:- none}"
# 6. the frozen scorer's two self-tests, into RB_OUT (no registered maker is run; the scorer's own --selftest-* modes write registered files)
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 timeout 900 nice -n 10 "$PY" -I -B "$E/rb/scorer_check_e224.py" "$RB_OUT/scorer-check-B" > "$RB_OUT/scorer-check-B.txt" 2>&1
rc=$?
[ "$rc" -eq 0 ] && grep -q '^SCORER-CHECK-E224: stand-ins PASS' "$RB_OUT/scorer-check-B.txt" || rb_die 10 "rb/scorer_check_e224.py (rc $rc): $(tail -n 1 "$RB_OUT/scorer-check-B.txt" | cut -c1-160)"
say "6. $(tail -n 1 "$RB_OUT/scorer-check-B.txt")"
r=$(OMP_NUM_THREADS=1 timeout 300 nice -n 10 "$PY" -I -B "$E/desk/timeout_e224.py" --check 2>&1 | tail -n 1)
[ "$r" = "TIMEOUT-E224 CHECK PASS" ] || rb_die 10 "desk/timeout_e224.py --check: $r"
say "6t. the kit's timeout table: $r (every E224 process's plain timeout 10 s)"
# 7. the box root's harness and the schedule
r=$("$PY" -I -B "$E/make_box_e224b.py" check 2>&1 | tail -n 1)
[ "$r" = "CHECK PASS" ] || rb_die 10 "make_box_e224b.py check: $r"
say "7. make_box_e224b.py check: CHECK PASS ($(grep -c '"dest"' "$E/harness-e224b.json") files; the schedule re-made from plan-e224.json, points-e224.json and the timeout table)"
# 8. the device-command audit
AUD=$(timeout 300 bash "$E/preflight_e224b.sh" 2>&1)
echo "$AUD" > "$RB_OUT/dmcmd-audit-v2.txt"
echo "$AUD" | grep -q '^dmcmd_audit: GO' || rb_die 10 "dmcmd_audit_v2 is not GO (RB_OUT/dmcmd-audit-v2.txt)"
say "8. dmcmd_audit_v2: $(echo "$AUD" | grep '^dmcmd_audit:' | head -n 1)"
# 8k. the kit's desk-test logs
bad=""
for spec in "realpath-e224b.txt:DESKTEST-REALPATH-E224B [0-9]+ of [0-9]+ PASS" "selftest-rb-e224b.txt:SELFTEST-RB-E224B [0-9]+ of [0-9]+ PASS" \
            "realbytes-e224b.txt:REALBYTES-E224B [0-9]+ of [0-9]+ PASS" "desktest-build-e224b.txt:DESKTEST-BUILD-E224B [0-9]+ of [0-9]+ PASS" \
            "selftest-run-e224b.txt:SELFTEST-RUN-E224B [0-9]+ of [0-9]+ PASS" "drypass-e224b.txt:DRY PASS a2c0 E224" \
            "dryaudit-e224b.txt:DRY-AUDIT-E224B [0-9]+ of [0-9]+ COVERED" "dry-listing-e224b.txt:dry listing: [0-9]+ steps listed, 0 run, 0 box calls" \
            "dmcmd-audit-e224b.txt:dmcmd_audit: GO" "selftest-post-e224b.txt:SELFTEST-POST-E224B [0-9]+ of [0-9]+ PASS" \
            "neverrun-desk-e224b.txt:NEVER-RUN-E224 arm B: "; do
  f=$E/logs/${spec%%:*}; want=${spec#*:}
  if [ ! -f "$f" ]; then bad="$bad ${spec%%:*}(missing)"; elif ! grep -qE "^$want" "$f"; then bad="$bad ${spec%%:*}(no '$want')"; fi
done
[ -z "$bad" ] || rb_die 10 "the kit's desk-test logs:$bad"
say "8k. the kit's desk-test logs: each in HEAD with its PASS line"
# 9. the freeze line
SN=tools/claims-v3/sealed-e224
say "9. THE FREEZE LINE: E224's registration ${REG:0:12} (committed $(git log -1 --format='%cd' --date=iso "$REG")), forecast-e224.csv $(sha256sum "$E/forecast-e224.csv" | cut -c1-16); sealed forecasts registered for E224: $(cat "$SN"/e224-freeze-lines*.md 2>/dev/null | grep -oE '\b[0-9a-f]{64}\b' | sort -u | tr '\n' ' ' || true)$( [ -d "$SN" ] || echo none)"
# 10. the round's sealed record
SL=$(RB_SEALED="${RB_SEALED:-}" bash "$RB_E224B_DIR/s00_sealed_e224b.sh" 2>&1); src=$?
say "10. $(echo "$SL" | tail -n 1)"
[ "$src" -eq 0 ] || rb_die 10 "the round's sealed record: $(echo "$SL" | tail -n 1): do not book; tell the orchestrator"
# 11. no E224 datum
X=$(git log --all --format=%H -- ':(glob)docs/reports/data/*-e224-blind-matmul-aifoundry2*/**' | head -n 3)
[ -z "$X" ] || rb_die 10 "an E224 arm B data path exists in a ref ($X): E224 arm B has run already"
say "11. no E224 arm B datum in any ref"
[ "$(git rev-parse HEAD)" = "$HEAD" ] || rb_die 10 "HEAD moved during the check"
say "12. HEAD unchanged"
say "STEP2 PASS (HEAD $HEAD)"
rb_ok "STEP2 PASS"
