#!/usr/bin/env bash
# E209 (Q202, lane kit-e209, Tue 17 Nov 2026, before any E209 datum; fix-e209, Q202c: the amended registration's pins, the history check
# commit by commit, THE ONE-LAB RULE's desk span, the post-scoring self-test's log): runbook step 2, THE DESK CHECK (outside the kit's own
# list SHA256SUMS-e209-kit, so that it can pin that list's own bytes: E207's and E200's step 2 form; nothing in HEAD pins this file, so the
# card lane compares its sha256 with the land's anchor before running it: the card-lane brief, step 2). Run in the lab clone LAB on aifoundry2, after
# step 1, inside THE ONE-LAB RULE's desk span (onelab desk before step 0, undesk right after this step), never inside the lab-git lock. Reads
# only, but for one thing: when LAB's HEAD is behind GitHub's main, clean, and an ancestor of it, it fast-forwards LAB under the lab-git lock.
#   RB_OUT=<the day's folder> RB_GITLOCK=<W/locks/lab-git.lock> RB_W=<the round's folder> RB_LANE=<the card lane> \
#     [RB_SEALED=<the round's sealed-forecast record for E209>] bash tools/claims-v3/e209/rb/s03_desk_e209.sh
# Checks, in order (any one not as stated: exit 10, nothing else done):
#   1. the window (step 1 today); 1o. outside a desk test, THE ONE-LAB RULE's desk span: RB_W's onelab.sh shows desk-<RB_LANE> (the card
#   lane ran onelab desk before step 0; verify-e209's finding 8; in a desk test the span is reported, never required); 2. HEAD = GitHub's main (git ls-remote, the environment-only HTTPS rewrite), after the fast-forward if one is
#   due; 3. the paths E209 runs from are clean; 4. E209's registration and kit are in HEAD, found by content (the commits that added E209.md and
#   KIT.md), the registration first; 4h. THE HISTORY CHECK (rb/check_history_e209.py tree: the registration's subtree afaa6053..., additions
#   only under tools/claims-v3/e209 since it, net and commit by commit, no shadowing module under tools/, the run paths clean); 5. THE LISTS E209 READS at their pinned
#   counts AND their own pinned sha256 AND every entry OK (no override outside a desk test): E209's registration list, its kit list, MM1-v2's
#   and MM1-v1's folders as landed, E208's registration list and its kit's src/ list; every other file with "SHA256SUMS" in its name under
#   tools/claims-v3/e209 is REPORTED (never a gate); 6. the registration's own checks: points, rules, plan, kernel --check PASS and
#   score_e209.py --forecasts byte for byte forecasts-e209.txt (it refuses, exit 4, if any frozen MM1-v2 or MM1-v1 file moved); 7.
#   make_box_e209.py check: CHECK PASS (the box root's every file at its sha256: E208's kit, E209's box files, the real tiles, fwgate); 8.
#   preflight_e209.sh: dmcmd_audit_v2 GO over every file whose commands the session or the runbook can send (no --allow); 8k. the kit's desk-test logs in HEAD, each ending
#   in its PASS line; 9. THE FREEZE LINE: MM1-v2's commit 3ca4b717 in HEAD, printed with any sealed forecast registered for E209
#   (tools/claims-v3/sealed-e209/e209-freeze-lines.md); 10. the round's sealed record (RB_SEALED), when it lists a sha256 on a line that is
#   not a comment, registered in that note at HEAD (else: do not book, tell the orchestrator: the E206 lesson); 11. no E209 datum in any ref
#   (docs/reports/data/*e209*); 12. HEAD unchanged since check 2.
# Desk tests only (RB_DESKTEST=1): RB_GITHUB names GitHub's main (no fast-forward then), RB_E209_KITPIN the kit list's pin (a stand-in kit).
# Writes RB_OUT/step2.txt and ends "STEP2 PASS (HEAD <sha>)". Exit 0 PASS; 10 refused; 17 call again (GitHub or the lab-git lock busy).
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e209.sh"
rb_init s03_desk
e209_window
cd "$RB_REPO" || rb_die 10 "cannot enter the lab clone"
E=$E209_REL
# the lists, each <path>:<lines>:<its own sha256>:<where its paths start: top = the lab's top, dir = the list's folder, up = its parent>
REGPIN=tools/claims-v3/e209/SHA256SUMS-e209-registration:22:c7da26bedcbf49980cc33c2475ffa6058bec679fcf38ee877ab7f35f2837b2ce:top
KITPIN=tools/claims-v3/e209/SHA256SUMS-e209-kit:47:35780e4d5be20d84fc9864ee40ea3fc200646690965103c0156c9f3116ad9a2e:top   # set at the kit's commit (the kit lane; fix-e209 re-sets it): its count and its own bytes
[ -n "${RB_E209_KITPIN:-}" ] && { [ "${RB_DESKTEST:-}" = 1 ] || rb_die 10 "RB_E209_KITPIN outside a desk test: refused"; KITPIN=$RB_E209_KITPIN; }
# 1o. THE ONE-LAB RULE's desk span (outside a desk test: required; in one: reported)
if [ "${RB_DESKTEST:-}" = 1 ]; then
  ONELAB_SPAN="not required in a desk test"
else
  rb_need RB_W RB_LANE
  [ -f "$RB_W/onelab.sh" ] || rb_die 10 "RB_W ($RB_W) holds no onelab.sh"
  bash "$RB_W/onelab.sh" show 2>/dev/null | grep -qx "  desk-$RB_LANE" || rb_die 10 "THE ONE-LAB RULE: $RB_LANE is not in its desk span (bash \$W/onelab.sh desk $RB_LANE before step 0)"
  ONELAB_SPAN="desk-$RB_LANE held"
fi
V2PIN=tools/matmul/mm1/v2/SHA256SUMS:114:eafb6558c4eaa053e4e33b8a4d6b2a644175f325df9e9ba56a1b6373b556f2f2:dir
V1PIN=tools/matmul/mm1/v1/SHA256SUMS:77:f77084ef6342964eafbea14d104ffc4dd324e83ee14cc4241158840a51ae468f:dir
E8RPIN=tools/claims-v3/e208/SHA256SUMS-e208-registration:57:74e483cfae187c0e2371ab3e3847079095bf650db82755c66ae36d59203696d2:top
E8SPIN=tools/claims-v3/e208/proposal/src/SRC-SHA256SUMS:48:543e9298d5a1013d348c3f38b9a9d9ae26479326a2393fb100c77e3b16b5a6d9:up
PINS="$REGPIN $KITPIN $V2PIN $V1PIN $E8RPIN $E8SPIN"
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
D=$(git status --porcelain --untracked-files=all -- "$E" tools/claims-v3/e208 tools/claims-v3/fwgate tools/matmul/mm1 tools/claims-v3/e136 \
  tools/claims-v3/kinds tools/claims-v3/dmcmd_audit_v2.py tools/claims-v3/dmcmd_table_v2.json)
[ -z "$D" ] || rb_die 10 "the paths E209 runs from are not clean: $(echo "$D" | head -n 3 | tr '\n' ' ')"
say "3. the paths clean"
# 4. the registration and the kit, by content
REG=$(git log --diff-filter=A --format=%H -- "$E/E209.md" | tail -n 1)
KIT=$(git log --diff-filter=A --format=%H -- "$E/KIT.md" | tail -n 1)
[ -n "$REG" ] && [ -n "$KIT" ] || rb_die 10 "E209's registration or kit is not in HEAD (registration '${REG:-none}', kit '${KIT:-none}')"
git merge-base --is-ancestor "$REG" "$KIT" || rb_die 10 "the kit's commit does not descend from the registration's"
say "4. the registration ${REG:0:12} ($(git log -1 --format='%cd' --date=iso "$REG")), the kit ${KIT:0:12} ($(git log -1 --format='%cd' --date=iso "$KIT")), both in HEAD"
H=$("$PY" -I -B "$E/rb/check_history_e209.py" tree --reg "$REG" 2>&1 | tail -n 1)
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
    *) if [ "$f" = "$E/box/SRC-SHA256SUMS-e209" ]; then unk="$unk $f(the box root's src/ list: check 7 re-makes it)"
       else unk="$unk $f($( (sha256sum -c "$f" 2>/dev/null) | grep -c ': OK$') OK of $(grep -c . "$f"))"; fi ;;
  esac
done
say "5. lists step 2 does not pin (REPORTED, never a gate):${unk:- none}"
# 6. the registration's own checks
for c in "points_e209.py --check" "rules_e209.py --check" "plan_e209.py --check" "desk/kernel_e209.py --check"; do
  # shellcheck disable=SC2086
  r=$(OMP_NUM_THREADS=1 timeout 900 nice -n 10 "$PY" -I -B $E/$c 2>&1 | tail -n 1)
  case "$r" in *PASS*) ;; *) rb_die 10 "$c: '$r'" ;; esac
  say "6. $c: $r"
done
OMP_NUM_THREADS=1 timeout 900 nice -n 10 "$PY" -I -B "$E/score_e209.py" --forecasts > "$RB_OUT/forecasts-now.txt" 2>&1
rc=$?
[ "$rc" -eq 0 ] && cmp -s "$RB_OUT/forecasts-now.txt" "$E/forecasts-e209.txt" || rb_die 10 "score_e209.py --forecasts (rc $rc) is not forecasts-e209.txt byte for byte (a frozen file moved?)"
say "6. score_e209.py --forecasts: byte for byte forecasts-e209.txt ($(tail -n 1 "$RB_OUT/forecasts-now.txt" | cut -c1-120))"
# 7. the box root's harness
r=$("$PY" -I -B "$E/make_box_e209.py" check 2>&1 | tail -n 1)
[ "$r" = "CHECK PASS" ] || rb_die 10 "make_box_e209.py check: $r"
say "7. make_box_e209.py check: CHECK PASS ($(grep -c '"dest"' "$E/harness-e209.json") files)"
# 8. the device-command audit
AUD=$(timeout 300 bash "$E/preflight_e209.sh" 2>&1)
echo "$AUD" > "$RB_OUT/dmcmd-audit-v2.txt"
echo "$AUD" | grep -q '^dmcmd_audit: GO' || rb_die 10 "dmcmd_audit_v2 is not GO (RB_OUT/dmcmd-audit-v2.txt)"
say "8. dmcmd_audit_v2: $(echo "$AUD" | grep '^dmcmd_audit:' | head -n 1)"
# 8k. the kit's desk-test logs
bad=""
for spec in "realpath-e209.txt:DESKTEST-REALPATH-E209 [0-9]+ of [0-9]+ PASS" "selftest-rb-e209.txt:SELFTEST-RB-E209 [0-9]+ of [0-9]+ PASS" \
            "realbytes-e209.txt:REALBYTES-E209 [0-9]+ of [0-9]+ PASS" "desktest-build-e209.txt:DESKTEST-BUILD-E209 PASS" \
            "drypass-e209.txt:DRY PASS a2c0 E209" "dryaudit-e209.txt:DRY-AUDIT-E209 [0-9]+ of [0-9]+ COVERED" \
            "dry-listing-e209.txt:dry listing: [0-9]+ steps listed, 0 run, 0 box calls" "dmcmd-audit-e209.txt:dmcmd_audit: GO" \
            "selftest-post-e209.txt:SELFTEST-POST-E209 [0-9]+ of [0-9]+ PASS"; do
  f=$E/logs/${spec%%:*}; want=${spec#*:}
  if [ ! -f "$f" ]; then bad="$bad ${spec%%:*}(missing)"; elif ! grep -qE "^$want" "$f"; then bad="$bad ${spec%%:*}(no '$want')"; fi
done
[ -z "$bad" ] || rb_die 10 "the kit's desk-test logs:$bad"
say "8k. the kit's desk-test logs: each in HEAD with its PASS line"
# 9. the freeze line
git merge-base --is-ancestor 3ca4b71799793ef35ce0811390b6b44dacb2d323 HEAD || rb_die 10 "MM1-v2's freeze commit 3ca4b717 is not in HEAD"
SN=tools/claims-v3/sealed-e209/e209-freeze-lines.md
say "9. THE FREEZE LINE: MM1-v2 3ca4b717 (pushed 01:44:48 PST Tue 17 Nov 2026), tools/matmul/mm1/v2/out/mm1_v2_e209.csv $(sha256sum tools/matmul/mm1/v2/out/mm1_v2_e209.csv | cut -c1-16); sealed forecasts registered for E209: $( [ -f "$SN" ] && grep -oE '\b[0-9a-f]{64}\b' "$SN" | sort -u | tr '\n' ' ' || echo none)"
# 10. the round's sealed record
if [ -n "${RB_SEALED:-}" ] && [ -f "$RB_SEALED" ]; then
  for h in $(grep -v '^[[:space:]]*#' "$RB_SEALED" | grep -oE '\b[0-9a-f]{64}\b' | sort -u); do
    [ -f "$SN" ] && grep -q "$h" "$SN" || rb_die 10 "the round's sealed record lists $h, which $SN at HEAD does not register: do not book; tell the orchestrator"
  done
  say "10. the round's sealed record: every sha256 it lists on a line that is not a comment is registered at HEAD"
else
  say "10. the round's sealed record: none kept (RB_SEALED ${RB_SEALED:+absent at $RB_SEALED}${RB_SEALED:-not set})"
fi
# 11. no E209 datum
X=$(git log --all --format=%H -- 'docs/reports/data/*e209*' | head -n 3)
[ -z "$X" ] || rb_die 10 "an E209 data path exists in a ref ($X): E209 has run already"
say "11. no E209 datum in any ref"
[ "$(git rev-parse HEAD)" = "$HEAD" ] || rb_die 10 "HEAD moved during the check"
say "12. HEAD unchanged"
say "STEP2 PASS (HEAD $HEAD)"
rb_ok "STEP2 PASS"
