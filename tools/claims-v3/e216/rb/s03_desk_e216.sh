#!/usr/bin/env bash
# E216 (Q227, lane kit-e216, Thu 19 Nov 2026, before any E216 datum; E209's kit's rb/s03_desk_e209.sh form, with E215's lesson that step 2 never
# rewrites a registered file): runbook step 2, THE DESK CHECK (outside the kit's own list SHA256SUMS-e216-kit, so that it can pin that list's own
# bytes; nothing in HEAD pins this file, so the card lane compares its sha256 with the land's anchor before running it: the card-lane brief,
# step 2). Run in the lab clone LAB on aifoundry2, after step 1, inside THE ONE-LAB RULE's desk span (onelab desk before step 0, undesk right
# after this step), never inside the lab-git lock. Reads only, but for one thing: when LAB's HEAD is behind GitHub's main, clean, and an ancestor
# of it, it fast-forwards LAB under the lab-git lock. IT RUNS NO REGISTERED MAKER (forecast_e216.py, rules_e216.py, plan_e216.py and
# point_rule_e216.py write registered files when run: never here); every output it makes goes to RB_OUT.
#   RB_OUT=<the day's folder> RB_GITLOCK=<W/locks/lab-git.lock> RB_W=<the round's folder> RB_LANE=<the card lane> \
#     [RB_SEALED=<the round's sealed-forecast record for E216>] bash tools/claims-v3/e216/rb/s03_desk_e216.sh
# Checks, in order (any one not as stated: exit 10, nothing else done):
#   1. the window (step 1 today); 1o. outside a desk test, THE ONE-LAB RULE's desk span: RB_W's onelab.sh shows desk-<RB_LANE> (in a desk test
#   the span is reported, never required); 2. HEAD = GitHub's main (git ls-remote, the environment-only HTTPS rewrite), after the fast-forward
#   if one is due; 3. the paths E216 runs from are clean; 4. E216's registration and kit are in HEAD, found by content (the commits that added
#   E216.md and KIT.md), the registration first; 4h. THE HISTORY CHECK (rb/check_history_e216.py tree: the registration's subtree a4cf984a...,
#   additions only under tools/claims-v3/e216 since it, net and commit by commit, no shadowing module under tools/, the run paths clean); 5.
#   THE LISTS E216 READS at their pinned counts AND their own pinned sha256 AND every entry OK (no override outside a desk test): E216's
#   registration list, its kit list, MM1-v3.1's, MM1-v3's and MM1-v2's folders as landed, E208's registration list and its kit's src/ list;
#   every other file with "SHA256SUMS" in its name under tools/claims-v3/e216 is REPORTED (never a gate); 6. THE FROZEN SCORER, print-only:
#   score_e216.py --forecasts (it refuses, exit 4, if a pinned file moved; it writes nothing) byte for byte the kit's logs/forecasts-print-e216.txt,
#   and score_e216.py --selftest-standins into RB_OUT byte for byte the registered selftest-standins.json; 7. make_box_e216.py check: CHECK PASS
#   (the box root's every file at its sha256: E208's kit, E216's box files and inputs, rgm211's sources, fwgate; the schedule re-made from the
#   registration's plan and points); 8. preflight_e216.sh: dmcmd_audit_v2 GO over every file whose commands the session or the runbook can send
#   (no --allow); 8k. the kit's desk-test logs in HEAD, each ending in its PASS line; 9. THE FREEZE LINE: E216's registration commit in HEAD,
#   printed with its committer time and any sealed forecast registered for E216 (tools/claims-v3/sealed-e216/e216-freeze-lines*.md); 10. THE
#   SEALED RECORD (rb/s00_sealed_e216.sh: every sha256 RB_SEALED lists on a line that is not a comment registered in
#   tools/claims-v3/sealed-e216/e216-freeze-lines.md at HEAD; else do not book, tell the orchestrator: the E206 lesson); 11. no E216 datum in
#   any ref (docs/reports/data/*e216*); 12. HEAD unchanged since check 2.
# Desk tests only (RB_DESKTEST=1): RB_GITHUB names GitHub's main (no fast-forward then), RB_E216_KITPIN the kit list's pin (a stand-in kit).
# Writes RB_OUT/step2.txt and ends "STEP2 PASS (HEAD <sha>)". Exit 0 PASS; 10 refused; 17 call again (GitHub or the lab-git lock busy).
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e216.sh"
rb_init s03_desk
e216_window
cd "$RB_REPO" || rb_die 10 "cannot enter the lab clone"
E=$E216_REL
# the lists, each <path>:<lines>:<its own sha256>:<where its paths start: top = the lab's top, dir = the list's folder, up = its parent>
REGPIN=tools/claims-v3/e216/SHA256SUMS-e216-registration:40:778c77aa7e96f81520132d1f349bbcd05f6484be7ec03a377443b87d9c5f0251:top   # fix-e216: the registration with Amendment 1
KITPIN=tools/claims-v3/e216/SHA256SUMS-e216-kit:58:085d46a6625730700ea74dd194e2f0b05a4b06507d5d208745914abc2b66bda7:top   # set at the kit's commit (its count and its own bytes)
[ -n "${RB_E216_KITPIN:-}" ] && { [ "${RB_DESKTEST:-}" = 1 ] || rb_die 10 "RB_E216_KITPIN outside a desk test: refused"; KITPIN=$RB_E216_KITPIN; }
if [ "${RB_DESKTEST:-}" = 1 ]; then
  ONELAB_SPAN="not required in a desk test"
else
  rb_need RB_W RB_LANE
  [ -f "$RB_W/onelab.sh" ] || rb_die 10 "RB_W ($RB_W) holds no onelab.sh"
  bash "$RB_W/onelab.sh" show 2>/dev/null | grep -qx "  desk-$RB_LANE" || rb_die 10 "THE ONE-LAB RULE: $RB_LANE is not in its desk span (bash \$W/onelab.sh desk $RB_LANE before step 0)"
  ONELAB_SPAN="desk-$RB_LANE held"
fi
V31PIN=tools/matmul/mm1/v3.1/SHA256SUMS:64:f6840d2de6617a739c30485904230e96b744b03b7c82c08b14b6de2d942528ed:dir
V3PIN=tools/matmul/mm1/v3/SHA256SUMS:170:c24efc149110d0cb3d1c8603f0bb7ee83db85eebf9af7ba4254d267c7c85dc74:dir
V2PIN=tools/matmul/mm1/v2/SHA256SUMS:114:eafb6558c4eaa053e4e33b8a4d6b2a644175f325df9e9ba56a1b6373b556f2f2:dir
E8RPIN=tools/claims-v3/e208/SHA256SUMS-e208-registration:57:74e483cfae187c0e2371ab3e3847079095bf650db82755c66ae36d59203696d2:top
E8SPIN=tools/claims-v3/e208/proposal/src/SRC-SHA256SUMS:48:543e9298d5a1013d348c3f38b9a9d9ae26479326a2393fb100c77e3b16b5a6d9:up
PINS="$REGPIN $KITPIN $V31PIN $V3PIN $V2PIN $E8RPIN $E8SPIN"
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
D=$(git status --porcelain --untracked-files=all -- "$E" tools/claims-v3/e208 tools/claims-v3/fwgate tools/matmul/mm1/v3.1 tools/matmul/mm1/v3 \
  tools/matmul/mm1/v2 tools/claims-v3/e136 tools/claims-v3/e211/rgm211 tools/claims-v3/e206/check_e206.py tools/claims-v3/e206/e206_common.py \
  tools/claims-v3/e213/desk/neverrun_e213.py tools/claims-v3/sealed-e216 tools/claims-v3/dmcmd_audit_v2.py tools/claims-v3/dmcmd_table_v2.json)
[ -z "$D" ] || rb_die 10 "the paths E216 runs from are not clean: $(echo "$D" | head -n 3 | tr '\n' ' ')"
say "3. the paths clean"
# 4. the registration and the kit, by content
REG=$(git log --diff-filter=A --format=%H -- "$E/E216.md" | tail -n 1)
KIT=$(git log --diff-filter=A --format=%H -- "$E/KIT.md" | tail -n 1)
[ -n "$REG" ] && [ -n "$KIT" ] || rb_die 10 "E216's registration or kit is not in HEAD (registration '${REG:-none}', kit '${KIT:-none}')"
git merge-base --is-ancestor "$REG" "$KIT" || rb_die 10 "the kit's commit does not descend from the registration's"
say "4. the registration ${REG:0:12} ($(git log -1 --format='%cd' --date=iso "$REG")), the kit ${KIT:0:12} ($(git log -1 --format='%cd' --date=iso "$KIT")), both in HEAD"
H=$("$PY" -I -B "$E/rb/check_history_e216.py" tree --reg "$REG" 2>&1 | tail -n 1)
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
    *) if [ "$f" = "$E/box/SRC-SHA256SUMS-e216" ]; then unk="$unk $f(the box root's src/ list: check 7 re-makes it)"
       else unk="$unk $f($( (sha256sum -c "$f" 2>/dev/null) | grep -c ': OK$') OK of $(grep -c . "$f"))"; fi ;;
  esac
done
say "5. lists step 2 does not pin (REPORTED, never a gate):${unk:- none}"
# 6. the frozen scorer, print-only (no registered maker is run)
OMP_NUM_THREADS=1 timeout 900 nice -n 10 "$PY" -I -B "$E/score_e216.py" --forecasts > "$RB_OUT/forecasts-now.txt" 2>&1
rc=$?
[ "$rc" -eq 0 ] && cmp -s "$RB_OUT/forecasts-now.txt" "$E/logs/forecasts-print-e216.txt" || rb_die 10 "score_e216.py --forecasts (rc $rc) is not logs/forecasts-print-e216.txt byte for byte (a frozen file moved?)"
say "6. score_e216.py --forecasts: byte for byte logs/forecasts-print-e216.txt ($(tail -n 1 "$RB_OUT/forecasts-now.txt" | cut -c1-120))"
OMP_NUM_THREADS=1 timeout 900 nice -n 10 "$PY" -I -B "$E/score_e216.py" --selftest-standins "$RB_OUT/selftest-standins-now.json" > "$RB_OUT/selftest-now.txt" 2>&1
rc=$?
[ "$rc" -eq 0 ] && cmp -s "$RB_OUT/selftest-standins-now.json" "$E/selftest-standins.json" || rb_die 10 "score_e216.py --selftest-standins (rc $rc) is not the registered selftest-standins.json byte for byte"
say "6. score_e216.py --selftest-standins into RB_OUT: byte for byte the registered selftest-standins.json ($(tail -n 1 "$RB_OUT/selftest-now.txt"))"
# 7. the box root's harness and the schedule
r=$("$PY" -I -B "$E/make_box_e216.py" check 2>&1 | tail -n 1)
[ "$r" = "CHECK PASS" ] || rb_die 10 "make_box_e216.py check: $r"
say "7. make_box_e216.py check: CHECK PASS ($(grep -c '"dest"' "$E/harness-e216.json") files; the schedule re-made from plan-e216.json and points-e216.json)"
# 8. the device-command audit
AUD=$(timeout 300 bash "$E/preflight_e216.sh" 2>&1)
echo "$AUD" > "$RB_OUT/dmcmd-audit-v2.txt"
echo "$AUD" | grep -q '^dmcmd_audit: GO' || rb_die 10 "dmcmd_audit_v2 is not GO (RB_OUT/dmcmd-audit-v2.txt)"
say "8. dmcmd_audit_v2: $(echo "$AUD" | grep '^dmcmd_audit:' | head -n 1)"
# 8k. the kit's desk-test logs
bad=""
for spec in "realpath-e216.txt:DESKTEST-REALPATH-E216 [0-9]+ of [0-9]+ PASS" "selftest-rb-e216.txt:SELFTEST-RB-E216 [0-9]+ of [0-9]+ PASS" \
            "realbytes-e216.txt:REALBYTES-E216 [0-9]+ of [0-9]+ PASS" "desktest-build-e216.txt:DESKTEST-BUILD-E216 [0-9]+ of [0-9]+ PASS" \
            "selftest-run-e216.txt:SELFTEST-RUN-E216 [0-9]+ of [0-9]+ PASS" "drypass-e216.txt:DRY PASS a2c0 E216" \
            "dryaudit-e216.txt:DRY-AUDIT-E216 [0-9]+ of [0-9]+ COVERED" "dry-listing-e216.txt:dry listing: [0-9]+ steps listed, 0 run, 0 box calls" \
            "dmcmd-audit-e216.txt:dmcmd_audit: GO" "selftest-post-e216.txt:SELFTEST-POST-E216 [0-9]+ of [0-9]+ PASS" \
            "neverrun-desk-e216.txt:NEVER-RUN-E216: "; do
  f=$E/logs/${spec%%:*}; want=${spec#*:}
  if [ ! -f "$f" ]; then bad="$bad ${spec%%:*}(missing)"; elif ! grep -qE "^$want" "$f"; then bad="$bad ${spec%%:*}(no '$want')"; fi
done
[ -z "$bad" ] || rb_die 10 "the kit's desk-test logs:$bad"
say "8k. the kit's desk-test logs: each in HEAD with its PASS line"
# 9. the freeze line
SN=tools/claims-v3/sealed-e216
say "9. THE FREEZE LINE: E216's registration ${REG:0:12} (committed $(git log -1 --format='%cd' --date=iso "$REG")), forecast-e216.json $(sha256sum "$E/forecast-e216.json" | cut -c1-16); sealed forecasts registered for E216: $(cat "$SN"/e216-freeze-lines*.md 2>/dev/null | grep -oE '\b[0-9a-f]{64}\b' | sort -u | tr '\n' ' ' || true)$( [ -d "$SN" ] || echo none)"
# 10. the round's sealed record
SL=$(RB_SEALED="${RB_SEALED:-}" bash "$RB_E216_DIR/s00_sealed_e216.sh" 2>&1); src=$?
say "10. $(echo "$SL" | tail -n 1)"
[ "$src" -eq 0 ] || rb_die 10 "the round's sealed record: $(echo "$SL" | tail -n 1): do not book; tell the orchestrator"
# 11. no E216 datum
X=$(git log --all --format=%H -- 'docs/reports/data/*e216*' | head -n 3)
[ -z "$X" ] || rb_die 10 "an E216 data path exists in a ref ($X): E216 has run already"
say "11. no E216 datum in any ref"
[ "$(git rev-parse HEAD)" = "$HEAD" ] || rb_die 10 "HEAD moved during the check"
say "12. HEAD unchanged"
say "STEP2 PASS (HEAD $HEAD)"
rb_ok "STEP2 PASS"
