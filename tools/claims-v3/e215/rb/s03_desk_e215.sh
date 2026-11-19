#!/usr/bin/env bash
# E215 (Q224, lane kit-e215, Thu 19 Nov 2026, before any E215 datum), the box step "step 2" (this file is s03; STEP 2, OUTSIDE THE KIT'S LIST:
# it pins the list by count and bytes, so it cannot be in it): the desk check before any box step, on the desk only (aifoundry2). E213's step 2
# (tools/claims-v3/e213/rb/s03_desk_e213.sh, landed in 6efdb002, run as stated by both of E213's card lanes) for E215; STEP 2 NEVER REWRITES A
# REGISTERED FILE IN THE LAB CLONE (E213's lesson): every file it makes goes to RB_OUT, the registration's checks run in their --check form,
# which rebuild in memory and compare, the frozen scorer's forecasts print runs through rb/forecasts_print_e215.py, which prints and writes
# nothing (the scorer's own --forecasts mode also writes forecasts-e215.txt over the registered file: fix-e215, answering verify-e215's
# finding 1), and step 2 itself reads at its end that nothing under E215's registered files was written or changed while it ran:
#   - the window first (e215_window: today, E215, this arm), or refused (10) before any call; the pull under the lab-git lock (e215_pull; never
#     run inside it);
#   - HEAD descends from E215's registration (found by its content: the commit that added E215.md, its tools/claims-v3/e215 subtree e89e512f...)
#     AND from the kit commit (found by its content: the commit that added KIT.md); arm A's freeze line (MM1-v3.1's land 2c971828) an ancestor of
#     HEAD (HEAD is GitHub main after the pull: the registration and, for arm A, MM1-v3.1's land are on GitHub main);
#   - E215's paths clean (with every path the session, the gate, the forecasts' inputs and the scorer read); the history check
#     (rb/check_history_e215.py): additions only under tools/claims-v3/e215 since the registration, no shadowing addition, nothing modified or
#     untracked on E215's run paths;
#   - EVERY LIST E215 READS at its pinned count AND its own pinned sha256 AND every entry OK: the registration's (SHA256SUMS-e215-registration,
#     REGPIN below: 35 entries) and the kit's (SHA256SUMS-e215-kit, KITPIN below, set at the kit's commit); any other file with SHA256SUMS in its
#     name under tools/claims-v3/e215 is REPORTED, never a gate;
#   - harness-e215.json re-made (CHECK PASS) and every file of it at its sha256 in the lab clone (HARNESS OK); the two modules' self-checks and
#     the kit's identity gate's pin check; the registration's own checks (points candidates and --check, forecast_e215, rules, plan,
#     desk/kernel_e215 --check, each its PASS line; forecast_e215 about two minutes and rules_e215 about one, single-threaded: rules_e215
#     reproduces MM1-v3.1's held-out record; ON ARM B ALSO desk/choose_e215b.py --check, which re-chooses arm B's 30 points from the
#     registration's scan, about ten minutes single-threaded: arm A's points are MM1-v3.1's land's, which points_e215 --check reads); the frozen
#     scorer's stand-in self-test (about 30 s) and its real-bytes self-test, each writing into RB_OUT, rc 0 and byte-identical to the committed
#     selftest-standins.json and selftest-real.json; its forecasts print by rb/forecasts_print_e215.py (the scorer loaded by its path and its
#     own forecasts_print() called: its pinned inputs checked, exit 4 if a byte changed; stdout only) into RB_OUT, rc 0 and byte-identical to the
#     COMMITTED forecasts-e215.txt (git show HEAD:..., read into RB_OUT) and to the file in the lab clone; the preflight (dmcmd_audit_v2 GO, no
#     WRITE); the kit's desk tests' logs as committed, each with its PASS line once, and both arms' dry listings' last lines;
#   - NOTHING WRITTEN OR CHANGED BY THE CHECKS (fix-e215): a marker in RB_OUT is made right after the pull, and at the end no file under E215's
#     folder, MM1-v3.1's out/e215 (arm A's frozen forecasts) or the sealed-forecast note's folder is newer than it (a rewrite with the same bytes,
#     which git status cannot see, is seen here), and E215's paths read clean again (git status, untracked files included), else 16;
#   - HEAD unchanged across all of it, else 16;
#   - NO E215 DATUM OF THIS ARM in any ref (a commit on a docs/reports/data FOLDER named *e215*-<aifoundry3 | aifoundry1-c1>, read with git's glob
#     magic: a FILE whose name holds 'e215', as one of E175's design tiles does, is not a datum): 16 if one exists (the arm has run); the other
#     arm's data, a gate stop's record (docs/reports/gate-stops/*e215*) and a sealed-forecast note (tools/claims-v3/sealed-e215/) REPORTED.
# The numerical checks run single-threaded (OMP, OpenBLAS, MKL and NumExpr threads 1: THE CPU RULE); the card lane runs this step inside the
# round's slot (W/slot.sh).
#   RB_GITLOCK=<the lab-git lock> bash tools/claims-v3/e215/rb/s03_desk_e215.sh A|B
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e215.sh"
rb_init s03_desk
e215_arm "${1:-}"
e215_window
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
E=tools/claims-v3/e215
REGPIN=tools/claims-v3/e215/SHA256SUMS-e215-registration:35:99439f8fabd33d027e0ad73c70e0aba57628a799237e25120ceae8fb93651195:top
KITPIN=tools/claims-v3/e215/SHA256SUMS-e215-kit:62:a609f0c1d2817bfd2933b9b1b0fb9a4878842ac68a8f690cf1ce0d837ddc35fd:top   # the kit's own list, at its count and its own bytes (set at the kit's commit)
bad=""
e215_pull || bad="$bad pull"
[ -z "${RB_DRY:-}" ] && [ "${RB_RC:-0}" -ne 0 ] && bad="$bad pull(rc $RB_RC; a nested lab-git lock exits 75)"
rb_local read local "HEAD before the checks" git -C "$RB_REPO" rev-parse HEAD
h0=$(rb_val '^([0-9a-f]{40})$')
MARK="$RB_OUT/step2-$ARM-checks-start.marker"     # fix-e215: the no-write read at the end compares every registered file's time against it
if [ -n "${RB_DRY:-}" ]; then echo "--- desk: a marker file made now in <RB_OUT> (step2-$ARM-checks-start.marker), after the pull and before the checks: the no-write read at the end compares against it"
else touch -- "$MARK" || bad="$bad marker"; fi
rb_local read local "E215's registration, by its content (the commit that added E215.md)" git -C "$RB_REPO" log --diff-filter=A --format=%H -- $E/E215.md
reg=$(rb_val '^([0-9a-f]{40})$')
rb_local read local "E215's kit commit, by its content (the commit that added KIT.md)" git -C "$RB_REPO" log --diff-filter=A --format=%H -- $E/KIT.md
kit=$(rb_val '^([0-9a-f]{40})$')
if [ -z "${RB_DRY:-}" ]; then
  if [ -z "$reg" ]; then bad="$bad registration(missing)"; else
    rb_local read local "the registration's e215 subtree" git -C "$RB_REPO" rev-parse "$reg:$E"
    rb_has "^$E215_REG_SUBTREE\$" || bad="$bad registration-subtree"
    rb_local read local "the registration is an ancestor of HEAD (arm B's freeze line on GitHub main)" git -C "$RB_REPO" merge-base --is-ancestor "$reg" HEAD || bad="$bad registration-ancestry"
  fi
  if [ -z "$kit" ]; then bad="$bad kit(missing)"; else
    rb_local read local "the kit commit is an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$kit" HEAD || bad="$bad kit-ancestry"
  fi
fi
rb_local read local "arm A's freeze line, MM1-v3.1's land, an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$E215_ARM_A_FREEZE" HEAD
[ -n "${RB_DRY:-}" ] || [ "$RB_RC" -eq 0 ] || bad="$bad mm1v31-land-ancestry"
SP="$E tools/claims-v3/sealed-e215 tools/matmul/mm1/v3.1 tools/matmul/mm1/v3 \
  tools/matmul/mm1/v2 tools/claims-v3/e136/rgm136 tools/claims-v3/e211/rgm211 tools/claims-v3/e211/kernel-e211.json tools/claims-v3/kinds/tiles \
  tools/claims-v3/kinds/kinds.json tools/claims-v3/kinds/blind3 tools/claims-v3/kinds/blind4 tools/claims-v3/e212/proposal/src/tiles \
  tools/claims-v3/e212/proposal/src/SRC-SHA256SUMS tools/claims-v3/q141k-runbook tools/claims-v3/e128 tools/claims-v3/e206 tools/claims-v3/e213 \
  tools/claims-v3/fwgate docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry3 docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry1-c1 \
  tools/claims-v3/dmcmd_audit_v2.py tools/claims-v3/dmcmd_table_v2.json"     # E215's paths (fix-e215: one list, read here and again at the end)
rb_local read local "E215's paths clean" git -C "$RB_REPO" status --short $SP
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
rb_local read local "the history check: additions only under $E since the registration, no shadowing addition (check_history_e215.py)" \
  /usr/bin/python3 -I -B $E/rb/check_history_e215.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || bad="$bad history"
paths=""; for spec in $REGPIN $KITPIN; do paths="$paths ${spec%%:*}"; done
rb_local read local "the own sha256 of the lists E215 reads (pinned)" sha256sum $paths
own=$RB_CAP
for spec in $REGPIN $KITPIN; do
  IFS=: read -r l pin hpin form <<EOF2
$spec
EOF2
  RB_CWD="$RB_REPO" rb_local read local "the list $l (pinned at $pin entries and its own sha256)" sha256sum -c "$l"
  if [ -z "${RB_DRY:-}" ]; then
    n=$(grep -c ': OK$' "$RB_CAP"); m=$(grep -c . "$RB_REPO/$l" 2>/dev/null); m=${m:-0}
    h=$(awk -v p="$l" '$2 == p {print $1}' "$own")
    why=""; [ "$h" = "$hpin" ] || why="; its own bytes differ from the pin"
    { [ "$RB_RC" -eq 0 ] && [ "$n" -eq "$m" ] && [ "$n" = "$pin" ] && [ -z "$why" ]; } || bad="$bad $(basename "$l")($n OK of $m; pinned $pin$why)"
  fi
done
rb_local read local "every file with SHA256SUMS anywhere in its name under $E" find "$E" -name '*SHA256SUMS*' -type f
unknown=""
if [ -z "${RB_DRY:-}" ]; then
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    case " $paths " in *" $f "*) ;; *) unknown="$unknown $f" ;; esac
  done < "$RB_CAP"
fi
for f in $unknown; do
  RB_CWD="$RB_REPO" rb_local read local "a list step 2 does not pin: $(basename "$f") (REPORTED, never a gate)" sha256sum -c "$f"
done
rb_local desk local "harness-e215.json re-made" /usr/bin/python3 -I -B $E/check_e215.py --check
rb_has '^CHECK PASS' || bad="$bad harness-rebuild"
rb_local desk local "every harness file at its sha256 in the lab clone" /usr/bin/python3 -I -B $E/check_e215.py --box
rb_has '^HARNESS OK: ' || bad="$bad harness"
rb_local read local "the common module's self-check (both arms, the four families, the order, the stops and the latch reading, the gates, the argv, the walk, the records, the forecasts)" /usr/bin/python3 -I -B $E/e215_common.py
rb_has '^E215-COMMON SELF-CHECK PASS' || bad="$bad common"
rb_local read local "the identity module's self-check" /usr/bin/python3 -I -B $E/e215_ident.py
rb_has '^E215-IDENT SELF-CHECK PASS' || bad="$bad ident"
rb_local read local "the kit's identity gate's pins (kernel-e215.json, E206's and E211's)" /usr/bin/python3 -I -B $E/ident_e215.py --check
rb_has '^CHECK PASS' || bad="$bad ident-gate"
CHOOSE=""; [ "$ARM" = B ] && CHOOSE="desk/choose_e215b.py@--scan@$E/desk/scan-e215.json@--check ^PASS$"   # arm B's points (about ten minutes)
if [ "${RB_DESKTEST:-}" = 1 ] && [ -n "${E215_DESK_NO_CHOOSE:-}" ] && [ -n "$CHOOSE" ]; then     # the runbook desk test's other step-2 runs only
  CHOOSE=""; echo "--- the runbook desk test (RB_DESKTEST=1, E215_DESK_NO_CHOOSE): this step-2 run leaves out choose_e215b.py --check (its case P1B runs it)"
fi
for spec in "points_e215.py@candidates@--check ^points_e215.candidates.--check:.desk/candidates-e215.json.rebuilt.==.committed:.True$" \
            "points_e215.py@--check ^PASS$" "forecast_e215.py@--check ^PASS$" "rules_e215.py@--check ^PASS$" "plan_e215.py@--check ^PASS$" \
            "desk/kernel_e215.py@--check ^PASS$" ${CHOOSE:+"$CHOOSE"}; do
  set -- $spec
  cmd=$(echo "$1" | tr '@' ' ')
  rb_local desk local "the registration's $cmd" /usr/bin/python3 -I -B $E/$cmd
  [ -n "${RB_DRY:-}" ] || { [ "$RB_RC" -eq 0 ] && grep -qE "$2" "$RB_CAP"; } || bad="$bad $(basename "${cmd%% *}" .py)$(case "$cmd" in *candidates*) echo -candidates ;; esac)"
done
same() {  # same <rc> <made file> <committed file> [<made> <committed>]: rc 0 and every pair byte-identical (never false in a dry listing)
  [ -n "${RB_DRY:-}" ] && return 0
  local rc=$1; shift
  [ "$rc" -eq 0 ] || return 1
  while [ $# -ge 2 ]; do cmp -s "$1" "$RB_REPO/$2" || return 1; shift 2; done
  return 0
}
RB_STDOUT="$RB_OUT/selftest-standins-e215-check.txt" rb_local desk local "the frozen scorer's stand-in self-test (it refuses, 4, if a frozen file changed)" /usr/bin/python3 -I -B $E/score_e215.py --selftest-standins "$RB_OUT/selftest-standins-e215-check.json"
same "$RB_RC" "$RB_OUT/selftest-standins-e215-check.json" "$E/selftest-standins.json" || bad="$bad selftest-standins"
[ -n "${RB_DRY:-}" ] || grep -q '^score_e215 --selftest-standins: PASS' "$RB_OUT/selftest-standins-e215-check.txt" || bad="$bad selftest-standins-words"
RB_STDOUT="$RB_OUT/selftest-real-e215-check.txt" rb_local desk local "the frozen scorer's real-bytes self-test (E213's committed runs, both arms)" /usr/bin/python3 -I -B $E/score_e215.py --selftest-real "$RB_OUT/selftest-real-e215-check.json"
same "$RB_RC" "$RB_OUT/selftest-real-e215-check.json" "$E/selftest-real.json" || bad="$bad selftest-real"
RB_STDOUT="$RB_OUT/forecasts-e215-check.txt" rb_local desk local "the frozen scorer's forecasts print (the given() self-check), print only: rb/forecasts_print_e215.py writes nothing (fix-e215)" /usr/bin/python3 -I -B $E/rb/forecasts_print_e215.py
frc=$RB_RC
RB_STDOUT="$RB_OUT/forecasts-e215-committed.txt" rb_local read local "the committed forecasts-e215.txt, as HEAD holds it (git show HEAD:...)" git -C "$RB_REPO" show "HEAD:$E/forecasts-e215.txt"
crc=$RB_RC
same "$frc" "$RB_OUT/forecasts-e215-check.txt" "$E/forecasts-e215.txt" || bad="$bad forecasts"
[ -n "${RB_DRY:-}" ] || { [ "$crc" -eq 0 ] && [ -s "$RB_OUT/forecasts-e215-committed.txt" ] && cmp -s "$RB_OUT/forecasts-e215-check.txt" "$RB_OUT/forecasts-e215-committed.txt"; } || bad="$bad forecasts-committed"
rb_local desk local "the preflight: dmcmd_audit_v2 on the session's files, no WRITE allowed" bash $E/preflight_e215.sh
rb_has '^dmcmd_audit: GO' || bad="$bad preflight"
for spec in "logs/selftest-run-e215.txt ^SELFTEST-RUN-E215.[0-9]+.of.[0-9]+.PASS$" "logs/realpath-e215.txt ^REALPATH-E215.[0-9]+.of.[0-9]+.PASS$" \
            "logs/realbytes-e215.txt ^REALBYTES-E215.[0-9]+.of.[0-9]+.PASS$" "logs/desktest-build-e215.txt ^DESKTEST-BUILD-E215.[0-9]+.of.[0-9]+.PASS$" \
            "logs/selftest-rb-e215.txt ^SELFTEST-RB-E215.[0-9]+.of.[0-9]+.PASS$" "logs/dry-listing-e215-A.txt ^dry.listing:.[0-9]+.steps.listed,.0.exited.non-zero,.0.box.calls$" \
            "logs/dry-listing-e215-B.txt ^dry.listing:.[0-9]+.steps.listed,.0.exited.non-zero,.0.box.calls$" "logs/dmcmd-audit-e215.txt ^dmcmd_audit:.GO"; do
  set -- $spec
  rb_local read local "a desk test's log, as committed: $1" grep -cE "$2" "$E/$1"
  rb_has '^1$' || bad="$bad $(basename "$1" .txt)"
done
NW="$E tools/matmul/mm1/v3.1/out/e215"; [ -d "$RB_REPO/tools/claims-v3/sealed-e215" ] && NW="$NW tools/claims-v3/sealed-e215"
rb_local read local "nothing written by the checks in E215's registered files: every file under $NW newer than the marker (want none; fix-e215)" find $NW -type f -newer "$MARK"
[ -z "${RB_DRY:-}" ] && { [ "$RB_RC" -ne 0 ] || [ -s "$RB_CAP" ]; } && bad="$bad wrote-in-lab(rc $RB_RC; $(grep -c . "$RB_CAP") file(s):$(head -n 3 "$RB_CAP" | sed 's#^# #' | tr -d '\n'))"
rb_local read local "E215's paths clean again after the checks, untracked files included (fix-e215)" git -C "$RB_REPO" status --porcelain --untracked-files=all -- $SP
[ -z "${RB_DRY:-}" ] && { [ "$RB_RC" -ne 0 ] || [ -s "$RB_CAP" ]; } && bad="$bad status-after($(grep -c . "$RB_CAP") line(s))"
rb_local read local "HEAD after the checks" git -C "$RB_REPO" rev-parse HEAD
h1=$(rb_val '^([0-9a-f]{40})$')
[ -n "${RB_DRY:-}" ] || [ "$h0" = "$h1" ] || bad="$bad HEAD-moved"
rb_local read local "E215 data of arm $ARM in any ref: a commit on a docs/reports/data folder named *e215*-$DATA_SUFFIX (want none before its session)" \
  git -C "$RB_REPO" log --all --oneline -- ":(glob)docs/reports/data/*e215*-$DATA_SUFFIX/**"
nd=0; [ -z "${RB_DRY:-}" ] && nd=$(grep -c . "$RB_CAP")
[ "$nd" -eq 0 ] || bad="$bad E215-arm-$ARM-has-data($nd commit(s))"
rb_local read local "the other arm's E215 data in any ref (REPORTED: never a gate for this arm)" git -C "$RB_REPO" log --all --oneline -- ':(glob)docs/reports/data/*e215*/**'
na=0; [ -z "${RB_DRY:-}" ] && na=$(( $(grep -c . "$RB_CAP") - nd ))
rb_local read local "E215 gate-stop records in any ref (REPORTED)" git -C "$RB_REPO" log --all --oneline -- ':(glob)docs/reports/gate-stops/*e215*/**'
no=0; [ -z "${RB_DRY:-}" ] && no=$(grep -c . "$RB_CAP")
rb_local read local "a sealed-forecast note for E215 (REPORTED; E215.md 0: step 0's S1 gates on it)" git -C "$RB_REPO" log --oneline -- tools/claims-v3/sealed-e215
ns=0; [ -z "${RB_DRY:-}" ] && ns=$(grep -c . "$RB_CAP")
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
echo "$(date '+%F %T %Z') step=$RB_STEP arm=$ARM lists not pinned (reported):${unknown:- none}; the other arm's data commits: $na; E215 gate-stop commits: $no; sealed-forecast note commits: $ns" >> "$RB_LOG"
rb_say "desk check: the window written today for E215 arm $ARM; pulled under the lab-git lock, HEAD ${h1:0:12} descends from the registration ${reg:0:12} (subtree ${E215_REG_SUBTREE:0:8}), the kit ${kit:0:12} and MM1-v3.1's land ${E215_ARM_A_FREEZE:0:12}, the paths clean, HISTORY OK, the lists at their pins, the harness, the modules, the gate's pins, the registration's checks, the scorer's three self-checks byte-identical (the forecasts print, print only, equal to the committed bytes), the preflight GO, the desk tests' logs, nothing written in E215's registered files and the paths clean again; no E215 datum of arm $ARM in any ref (the other arm's data commits: $na; E215 gate-stop commits: $no; sealed-forecast note commits: $ns)"
exit 0
