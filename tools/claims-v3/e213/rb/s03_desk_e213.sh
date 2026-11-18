#!/usr/bin/env bash
# E213 (Q216, lane kit-e213, Tue 17 Nov 2026, before any E213 datum), the box step "step 2" (this file is s03; STEP 2, OUTSIDE THE KIT'S LIST:
# it pins the list by count and bytes, so it cannot be in it): the desk check before any box step, on the desk only (aifoundry2). E211's step 2
# (tools/claims-v3/e211/rb/s03_desk_e211.sh, landed in 2b7f261f) with E206's per-arm datum rule (tools/claims-v3/e206/rb/s03_desk_e206.sh), for
# E213:
#   - the window first (e213_window: today, E213, this arm), or refused (10) before any call; the pull under the lab-git lock (e213_pull; never
#     run inside it);
#   - HEAD descends from E213's registration (found by its content: the commit that added E213.md, its tools/claims-v3/e213 subtree 75778ad3...)
#     AND from the kit commit (found by its content: the commit that added KIT.md); arm A's freeze line (MM1-v3's land b1493082) an ancestor of
#     HEAD (HEAD is GitHub main after the pull: the registration and, for arm A, MM1-v3's land are on GitHub main);
#   - E213's paths clean (with every path the session, the gate, the forecasts' inputs and the scorer read); the history check
#     (rb/check_history_e213.py): additions only under tools/claims-v3/e213 since the registration, no shadowing addition, nothing modified or
#     untracked on E213's run paths;
#   - EVERY LIST E213 READS at its pinned count AND its own pinned sha256 AND every entry OK: the registration's (SHA256SUMS-e213-registration,
#     REGPIN below: 27 entries) and the kit's (SHA256SUMS-e213-kit, KITPIN below, set at the kit's commit); any other file with SHA256SUMS in its
#     name under tools/claims-v3/e213 is REPORTED, never a gate;
#   - harness-e213.json re-made (CHECK PASS) and every file of it at its sha256 in the lab clone (HARNESS OK); the two modules' self-checks and
#     the kit's identity gate's pin check; the registration's own checks (points candidates and --check, forecast_e213b, rules, plan,
#     desk/kernel_e213 --check, each its PASS line; rules_e213 reproduces MM1-v3's held-out record, about a minute single-threaded); the frozen
#     scorer's stand-in self-test (about 30 s), its real-bytes self-test and its forecasts print, each rc 0 and byte-identical to the committed
#     selftest-standins.json, selftest-real.json and forecasts-e213.txt; the preflight (dmcmd_audit_v2 GO, no WRITE); the kit's desk tests' logs
#     as committed, each with its PASS line once, and both arms' dry listings' last lines;
#   - HEAD unchanged across all of it, else 16;
#   - NO E213 DATUM OF THIS ARM in any ref (a commit on a docs/reports/data FOLDER named *e213*-<aifoundry3 | aifoundry1-c1>, read with git's glob
#     magic: a FILE whose name holds 'e213', as one of E175's design tiles does, is not a datum): 16 if one exists (the arm has run); the other
#     arm's data, a gate stop's record (docs/reports/gate-stops/*e213*) and a sealed-forecast note (tools/claims-v3/sealed-e213/) REPORTED.
# The numerical checks run single-threaded (OMP, OpenBLAS, MKL and NumExpr threads 1: THE CPU RULE); the card lane runs this step inside the
# round's slot (W/slot.sh).
#   RB_GITLOCK=<the lab-git lock> bash tools/claims-v3/e213/rb/s03_desk_e213.sh A|B
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e213.sh"
rb_init s03_desk
e213_arm "${1:-}"
e213_window
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
E=tools/claims-v3/e213
REGPIN=tools/claims-v3/e213/SHA256SUMS-e213-registration:27:96e5d1682a237c4de6eb6755da481795db9f6ff43b32791c1851c1a45872d2ce:top
KITPIN=tools/claims-v3/e213/SHA256SUMS-e213-kit:49:a4d45a97d6da745f6e23020aa788dd4258f455645d49578fe823d2ad7db526e2:top   # the kit's own list, at its count and its own bytes (set at the kit's commit)
bad=""
e213_pull || bad="$bad pull"
[ -z "${RB_DRY:-}" ] && [ "${RB_RC:-0}" -ne 0 ] && bad="$bad pull(rc $RB_RC; a nested lab-git lock exits 75)"
rb_local read local "HEAD before the checks" git -C "$RB_REPO" rev-parse HEAD
h0=$(rb_val '^([0-9a-f]{40})$')
rb_local read local "E213's registration, by its content (the commit that added E213.md)" git -C "$RB_REPO" log --diff-filter=A --format=%H -- $E/E213.md
reg=$(rb_val '^([0-9a-f]{40})$')
rb_local read local "E213's kit commit, by its content (the commit that added KIT.md)" git -C "$RB_REPO" log --diff-filter=A --format=%H -- $E/KIT.md
kit=$(rb_val '^([0-9a-f]{40})$')
if [ -z "${RB_DRY:-}" ]; then
  if [ -z "$reg" ]; then bad="$bad registration(missing)"; else
    rb_local read local "the registration's e213 subtree" git -C "$RB_REPO" rev-parse "$reg:$E"
    rb_has "^$E213_REG_SUBTREE\$" || bad="$bad registration-subtree"
    rb_local read local "the registration is an ancestor of HEAD (arm B's freeze line on GitHub main)" git -C "$RB_REPO" merge-base --is-ancestor "$reg" HEAD || bad="$bad registration-ancestry"
  fi
  if [ -z "$kit" ]; then bad="$bad kit(missing)"; else
    rb_local read local "the kit commit is an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$kit" HEAD || bad="$bad kit-ancestry"
  fi
fi
rb_local read local "arm A's freeze line, MM1-v3's land, an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$E213_ARM_A_FREEZE" HEAD
[ -n "${RB_DRY:-}" ] || [ "$RB_RC" -eq 0 ] || bad="$bad mm1v3-land-ancestry"
rb_local read local "E213's paths clean" git -C "$RB_REPO" status --short $E tools/claims-v3/sealed-e213 tools/matmul/mm1/v3 tools/matmul/mm1/v2 \
  tools/claims-v3/e136/rgm136 tools/claims-v3/e211/rgm211 tools/claims-v3/e211/kernel-e211.json tools/claims-v3/kinds/tiles tools/claims-v3/kinds/kinds.json \
  tools/claims-v3/q141k-runbook tools/claims-v3/e128 tools/claims-v3/e206 docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3 \
  docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1 docs/reports/data/2026-11-17-e211-second-kernel-aifoundry3 \
  tools/claims-v3/dmcmd_audit_v2.py tools/claims-v3/dmcmd_table_v2.json
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
rb_local read local "the history check: additions only under $E since the registration, no shadowing addition (check_history_e213.py)" \
  /usr/bin/python3 -I -B $E/rb/check_history_e213.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || bad="$bad history"
paths=""; for spec in $REGPIN $KITPIN; do paths="$paths ${spec%%:*}"; done
rb_local read local "the own sha256 of the lists E213 reads (pinned)" sha256sum $paths
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
rb_local desk local "harness-e213.json re-made" /usr/bin/python3 -I -B $E/check_e213.py --check
rb_has '^CHECK PASS' || bad="$bad harness-rebuild"
rb_local desk local "every harness file at its sha256 in the lab clone" /usr/bin/python3 -I -B $E/check_e213.py --box
rb_has '^HARNESS OK: ' || bad="$bad harness"
rb_local read local "the common module's self-check (both arms, the four families, the order, the stops and the latch reading, the gates, the argv, the walk, the records, the forecasts)" /usr/bin/python3 -I -B $E/e213_common.py
rb_has '^E213-COMMON SELF-CHECK PASS' || bad="$bad common"
rb_local read local "the identity module's self-check" /usr/bin/python3 -I -B $E/e213_ident.py
rb_has '^E213-IDENT SELF-CHECK PASS' || bad="$bad ident"
rb_local read local "the kit's identity gate's pins (kernel-e213.json, E206's and E211's)" /usr/bin/python3 -I -B $E/ident_e213.py --check
rb_has '^CHECK PASS' || bad="$bad ident-gate"
for spec in "points_e213.py@candidates@--check ^points_e213.candidates.--check:.desk/candidates-e213.json.rebuilt.==.committed:.True$" \
            "points_e213.py@--check ^PASS$" "forecast_e213b.py@--check ^PASS$" "rules_e213.py@--check ^PASS$" "plan_e213.py@--check ^PASS$" \
            "desk/kernel_e213.py@--check ^PASS$"; do
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
RB_STDOUT="$RB_OUT/selftest-standins-e213-check.txt" rb_local desk local "the frozen scorer's stand-in self-test (it refuses, 4, if a frozen file changed)" /usr/bin/python3 -I -B $E/score_e213.py --selftest-standins "$RB_OUT/selftest-standins-e213-check.json"
same "$RB_RC" "$RB_OUT/selftest-standins-e213-check.json" "$E/selftest-standins.json" || bad="$bad selftest-standins"
[ -n "${RB_DRY:-}" ] || grep -q '^score_e213 --selftest-standins: PASS' "$RB_OUT/selftest-standins-e213-check.txt" || bad="$bad selftest-standins-words"
RB_STDOUT="$RB_OUT/selftest-real-e213-check.txt" rb_local desk local "the frozen scorer's real-bytes self-test (E207's and E206 arm B's committed runs)" /usr/bin/python3 -I -B $E/score_e213.py --selftest-real "$RB_OUT/selftest-real-e213-check.json"
same "$RB_RC" "$RB_OUT/selftest-real-e213-check.json" "$E/selftest-real.json" || bad="$bad selftest-real"
RB_STDOUT="$RB_OUT/forecasts-e213-check.txt" rb_local desk local "the frozen scorer's forecasts print (the given() self-check)" /usr/bin/python3 -I -B $E/score_e213.py --forecasts
same "$RB_RC" "$RB_OUT/forecasts-e213-check.txt" "$E/forecasts-e213.txt" || bad="$bad forecasts"
rb_local desk local "the preflight: dmcmd_audit_v2 on the session's files, no WRITE allowed" bash $E/preflight_e213.sh
rb_has '^dmcmd_audit: GO' || bad="$bad preflight"
for spec in "logs/selftest-run-e213.txt ^SELFTEST-RUN-E213.[0-9]+.of.[0-9]+.PASS$" "logs/realpath-e213.txt ^REALPATH-E213.[0-9]+.of.[0-9]+.PASS$" \
            "logs/realbytes-e213.txt ^REALBYTES-E213.[0-9]+.of.[0-9]+.PASS$" "logs/desktest-build-e213.txt ^DESKTEST-BUILD-E213.[0-9]+.of.[0-9]+.PASS$" \
            "logs/selftest-rb-e213.txt ^SELFTEST-RB-E213.[0-9]+.of.[0-9]+.PASS$" "logs/dry-listing-e213-A.txt ^dry.listing:.[0-9]+.steps.listed,.0.exited.non-zero,.0.box.calls$" \
            "logs/dry-listing-e213-B.txt ^dry.listing:.[0-9]+.steps.listed,.0.exited.non-zero,.0.box.calls$" "logs/dmcmd-audit-e213.txt ^dmcmd_audit:.GO"; do
  set -- $spec
  rb_local read local "a desk test's log, as committed: $1" grep -cE "$2" "$E/$1"
  rb_has '^1$' || bad="$bad $(basename "$1" .txt)"
done
rb_local read local "HEAD after the checks" git -C "$RB_REPO" rev-parse HEAD
h1=$(rb_val '^([0-9a-f]{40})$')
[ -n "${RB_DRY:-}" ] || [ "$h0" = "$h1" ] || bad="$bad HEAD-moved"
rb_local read local "E213 data of arm $ARM in any ref: a commit on a docs/reports/data folder named *e213*-$DATA_SUFFIX (want none before its session)" \
  git -C "$RB_REPO" log --all --oneline -- ":(glob)docs/reports/data/*e213*-$DATA_SUFFIX/**"
nd=0; [ -z "${RB_DRY:-}" ] && nd=$(grep -c . "$RB_CAP")
[ "$nd" -eq 0 ] || bad="$bad E213-arm-$ARM-has-data($nd commit(s))"
rb_local read local "the other arm's E213 data in any ref (REPORTED: never a gate for this arm)" git -C "$RB_REPO" log --all --oneline -- ':(glob)docs/reports/data/*e213*/**'
na=0; [ -z "${RB_DRY:-}" ] && na=$(( $(grep -c . "$RB_CAP") - nd ))
rb_local read local "E213 gate-stop records in any ref (REPORTED)" git -C "$RB_REPO" log --all --oneline -- ':(glob)docs/reports/gate-stops/*e213*/**'
no=0; [ -z "${RB_DRY:-}" ] && no=$(grep -c . "$RB_CAP")
rb_local read local "a sealed-forecast note for E213 (REPORTED; E213.md 0: step 0's S1 gates on it)" git -C "$RB_REPO" log --oneline -- tools/claims-v3/sealed-e213
ns=0; [ -z "${RB_DRY:-}" ] && ns=$(grep -c . "$RB_CAP")
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
echo "$(date '+%F %T %Z') step=$RB_STEP arm=$ARM lists not pinned (reported):${unknown:- none}; the other arm's data commits: $na; E213 gate-stop commits: $no; sealed-forecast note commits: $ns" >> "$RB_LOG"
rb_say "desk check: the window written today for E213 arm $ARM; pulled under the lab-git lock, HEAD ${h1:0:12} descends from the registration ${reg:0:12} (subtree ${E213_REG_SUBTREE:0:8}), the kit ${kit:0:12} and MM1-v3's land ${E213_ARM_A_FREEZE:0:12}, the paths clean, HISTORY OK, the lists at their pins, the harness, the modules, the gate's pins, the registration's checks, the scorer's three self-checks byte-identical, the preflight GO, the desk tests' logs; no E213 datum of arm $ARM in any ref (the other arm's data commits: $na; E213 gate-stop commits: $no; sealed-forecast note commits: $ns)"
exit 0
