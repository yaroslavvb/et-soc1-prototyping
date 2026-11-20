#!/usr/bin/env bash
# E220 ARM A (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum), the box step "step 2" (this file is s03; STEP 2, OUTSIDE THE KIT'S
# LIST: it pins the list by count and bytes, so it cannot be in it): the desk check before any box step, on the desk only (aifoundry2). E218's
# step 2 (tools/claims-v3/e218/rb/s03_desk_e218.sh, landed in 5582edfc, run as stated by E218's card lane) for E220 arm A. STEP 2 NEVER REWRITES
# A REGISTERED FILE IN THE LAB CLONE (E213's lesson; verify-e215's finding 1): every file it makes goes to RB_OUT; the registration's checks run in
# their --check form, which rebuild in memory and compare (rules_e220.py's work folder set into RB_OUT); THE FROZEN SCORER'S TWO SELF-TESTS RUN
# THROUGH rb/scorer_check_e220.py, which imports score_e220.py unchanged and writes their outputs into RB_OUT, then compares them with the
# committed selftest-standins.json and selftest-real.json byte for byte - never through the scorer's own --selftest-* modes, which write those
# registered files in place; and step 2 itself reads at its end that nothing under E220's folder, MM1's folders or the seal note's folder was
# written or changed while it ran:
#   - the window first (e220a_window: today, E220, arm A), or refused (10) before any call; the pull under the lab-git lock (e220a_pull; never run
#     inside it);
#   - HEAD descends from E220's registration (found by its content: the commit that added E220.md, its tools/claims-v3/e220 subtree 46dde0fd...:
#     ITS PUSH IS THE FREEZE LINE of every E220 forecast) AND from the kit commit (found by its content: the commit that added KIT.md) AND from
#     MM1-v3.2's land 4e386f75 (HEAD is GitHub main after the pull);
#   - E220's paths clean (with every path the session, the gate, the forecasts' inputs, the registration's checks and the scorer read); the history
#     check (rb/check_history_e220a.py): additions only under tools/claims-v3/e220 since the registration, no shadowing addition, nothing modified
#     or untracked on E220's run paths;
#   - EVERY LIST E220 READS at its pinned count AND its own pinned sha256 AND every entry OK: the registration's (SHA256SUMS-e220-registration,
#     REGPIN below: 29 entries) and the kit's (SHA256SUMS-e220-kit, KITPIN below, set at the kit's commit: both arms' files but the two step 2s);
#     any other file with SHA256SUMS in its name under tools/claims-v3/e220 is REPORTED, never a gate;
#   - harness-e220a.json re-made (CHECK PASS) and every file of it at its sha256 in the lab clone (HARNESS OK); the two modules' self-checks and the
#     kit's identity gate's pin check; the kit's timeout table (desk/timeout_e220.py --check: re-made from committed bytes, CHECK PASS); the
#     registration's own checks (forecast_e220, rules_e220 with --work in RB_OUT, plan_e220 and desk/kernel_e220, each its --check and its line;
#     a few minutes in all, single-threaded: rules_e220 reproduces MM1-v3.2's held-out record); the frozen scorer's stand-in and real-bytes
#     self-tests through rb/scorer_check_e220.py, byte-identical; the preflight (dmcmd_audit_v2 GO, no WRITE); the kit's desk tests' logs as
#     committed, each with its PASS line once, and the dry listing's last line;
#   - NOTHING WRITTEN OR CHANGED BY THE CHECKS (fix-e215's form): a marker in RB_OUT is made right after the pull, and at the end no file under
#     E220's folder, tools/matmul/mm1 (MM1-v3.2's land and the predictors and records the checks import) or the sealed-forecast note's folder is
#     newer than it (a rewrite with the same bytes, which git status cannot see, is seen here), and E220's paths read clean again (git status,
#     untracked files included), else 16;
#   - HEAD unchanged across all of it, else 16;
#   - NO E220 ARM A DATUM in any ref (a commit on a docs/reports/data FOLDER named *-e220-*-aifoundry1-c1, read with git's glob magic: a FILE
#     whose name holds 'e220' is not a datum): 16 if one exists; a gate stop's record (docs/reports/gate-stops/*-e220-*) and a sealed-forecast
#     note (tools/claims-v3/sealed-e220/) REPORTED.
# The numerical checks run single-threaded (OMP, OpenBLAS, MKL and NumExpr threads 1: THE CPU RULE); the card lane runs this step inside the
# round's slot (W/slot.sh).
#   RB_GITLOCK=<the lab-git lock> bash tools/claims-v3/e220/rb/s03_desk_e220a.sh A
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e220a.sh"
rb_init s03_desk
e220a_arm "${1:-}"
e220a_window
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
E=tools/claims-v3/e220
REGPIN=tools/claims-v3/e220/SHA256SUMS-e220-registration:29:dc5d053f3a186c56f0006c8c6c88cdcc2729fc20456dff5dbe7a3e9e1357944b:top
KITPIN=tools/claims-v3/e220/SHA256SUMS-e220-kit:120:e2feca732b2a7c51a490e2000ac1116dc8841264d695e9f054ab461ee9965984:top   # the kit's own list (both arms), at its count and its own bytes (set at the kit's commit)
bad=""
e220a_pull || bad="$bad pull"
[ -z "${RB_DRY:-}" ] && [ "${RB_RC:-0}" -ne 0 ] && bad="$bad pull(rc $RB_RC; a nested lab-git lock exits 75)"
rb_local read local "HEAD before the checks" git -C "$RB_REPO" rev-parse HEAD
h0=$(rb_val '^([0-9a-f]{40})$')
MARK="$RB_OUT/step2-$ARM-checks-start.marker"     # the no-write read at the end compares every registered file's time against it
TMPD="$RB_OUT/step2-$ARM-scratch-$(date +%Y%m%dT%H%M%S)-$$"   # the registration checks' scratch, new for each call (forecast_e220's cache, rules_e220's work)
if [ -n "${RB_DRY:-}" ]; then echo "--- desk: a marker file made now in <RB_OUT> (step2-$ARM-checks-start.marker), after the pull and before the checks: the no-write read at the end compares against it; the checks' scratch <RB_OUT>/step2-$ARM-scratch"
else touch -- "$MARK" || bad="$bad marker"; mkdir -p "$TMPD/rules-work" || bad="$bad scratch"; fi
rb_local read local "E220's registration, by its content (the commit that added E220.md)" git -C "$RB_REPO" log --diff-filter=A --format=%H -- $E/E220.md
reg=$(rb_val '^([0-9a-f]{40})$')
rb_local read local "E220's kit commit, by its content (the commit that added KIT.md)" git -C "$RB_REPO" log --diff-filter=A --format=%H -- $E/KIT.md
kit=$(rb_val '^([0-9a-f]{40})$')
if [ -z "${RB_DRY:-}" ]; then
  if [ -z "$reg" ]; then bad="$bad registration(missing)"; else
    rb_local read local "the registration's e220 subtree" git -C "$RB_REPO" rev-parse "$reg:$E"
    rb_has "^$E220A_REG_SUBTREE\$" || bad="$bad registration-subtree"
    rb_local read local "the registration is an ancestor of HEAD (its push is the freeze line of every E220 forecast, the points, the rules and the scorer)" git -C "$RB_REPO" merge-base --is-ancestor "$reg" HEAD || bad="$bad registration-ancestry"
  fi
  if [ -z "$kit" ]; then bad="$bad kit(missing)"; else
    rb_local read local "the kit commit is an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$kit" HEAD || bad="$bad kit-ancestry"
  fi
fi
rb_local read local "MM1-v3.2's land (the models E220's forecasts were made by), an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$E220A_FREEZE" HEAD
[ -n "${RB_DRY:-}" ] || [ "$RB_RC" -eq 0 ] || bad="$bad mm1v32-land-ancestry"
SP="$E tools/claims-v3/sealed-e220 tools/matmul/mm1/v3.2 tools/matmul/mm1/v3.2-terms tools/matmul/mm1/v3.1 tools/matmul/mm1/v3 \
  tools/matmul/mm1/v2 tools/claims-v3/e136/rgm136 tools/claims-v3/e211/rgm211 tools/claims-v3/e211/kernel-e211.json tools/claims-v3/kinds/tiles \
  tools/claims-v3/kinds/kinds.json tools/claims-v3/q141k-runbook tools/claims-v3/e128 tools/claims-v3/e206 tools/claims-v3/e213 tools/claims-v3/e215 \
  tools/claims-v3/e216 tools/claims-v3/e218 tools/claims-v3/fwgate \
  docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry1-c1 docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry1-c1 \
  docs/reports/data/2026-11-20-e218-blind-matmul-aifoundry3 docs/reports/data/2026-11-19-e216-blind-matmul-aifoundry2 \
  docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2 workloads/nocbench/analyze.py \
  tools/claims-v3/dmcmd_audit_v2.py tools/claims-v3/dmcmd_table_v2.json"     # E220's paths (one list, read here and again at the end: the
# registration's inputs - MM1-v3.2's layout module reads the mesh map workloads/nocbench/analyze.py through E215's v01_map.py; the scorer's
# real-bytes self-test reads E215 arm B's and E216's data; the timeout table reads E215 arm B's, E213 arm B's, E216's, E209's and E218's)
rb_local read local "E220's paths clean" git -C "$RB_REPO" status --short $SP
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
rb_local read local "the history check: additions only under $E since the registration, no shadowing addition (check_history_e220a.py)" \
  /usr/bin/python3 -I -B $E/rb/check_history_e220a.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || bad="$bad history"
paths=""; for spec in $REGPIN $KITPIN; do paths="$paths ${spec%%:*}"; done
rb_local read local "the own sha256 of the lists E220 reads (pinned)" sha256sum $paths
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
rb_local desk local "harness-e220a.json re-made" /usr/bin/python3 -I -B $E/check_e220a.py --check
rb_has '^CHECK PASS' || bad="$bad harness-rebuild"
rb_local desk local "every harness file at its sha256 in the lab clone" /usr/bin/python3 -I -B $E/check_e220a.py --box
rb_has '^HARNESS OK: ' || bad="$bad harness"
rb_local read local "the common module's self-check (the arm, the two families, the order, the G block last, the stops and the latch reading, the gates, the argv, the walk, the records, the forecasts)" /usr/bin/python3 -I -B $E/e220a_common.py
rb_has '^E220A-COMMON SELF-CHECK PASS' || bad="$bad common"
rb_local read local "the identity module's self-check" /usr/bin/python3 -I -B $E/e220a_ident.py
rb_has '^E220A-IDENT SELF-CHECK PASS' || bad="$bad ident"
rb_local read local "the kit's identity gate's pins (kernel-e220.json, E206's and E211's)" /usr/bin/python3 -I -B $E/ident_e220a.py --check
rb_has '^CHECK PASS' || bad="$bad ident-gate"
for spec in "forecast_e220.py@--check ^forecast_e220.--check:.SAME$" "rules_e220.py@--check@--work@$TMPD/rules-work ^rules_e220.--check:.SAME$" \
            "plan_e220.py@--check ^plan_e220.--check:.SAME$" "desk/kernel_e220.py@--check ^PASS$" "desk/timeout_e220.py@--check ^TIMEOUT-E220.CHECK.PASS$"; do
  set -- $spec
  cmd=$(echo "$1" | tr '@' ' ')
  E220A_TMP="$TMPD" rb_local desk local "the registration's $cmd" /usr/bin/python3 -I -B $E/$cmd
  [ -n "${RB_DRY:-}" ] || { [ "$RB_RC" -eq 0 ] && grep -qE "$2" "$RB_CAP"; } || bad="$bad $(basename "${cmd%% *}" .py)"
done
same() {  # same <rc> <made file> <committed file> [<made> <committed>]: rc 0 and every pair byte-identical (never false in a dry listing)
  [ -n "${RB_DRY:-}" ] && return 0
  local rc=$1; shift
  [ "$rc" -eq 0 ] || return 1
  while [ $# -ge 2 ]; do cmp -s "$1" "$RB_REPO/$2" || return 1; shift 2; done
  return 0
}
rb_local desk local "the frozen scorer's two self-tests through rb/scorer_check_e220.py: score_e220.py imported unchanged, its stand-in and real-bytes self-tests written into RB_OUT and compared with the committed files byte for byte (the scorer's own --selftest-* modes write registered files: never run here)" \
  /usr/bin/python3 -I -B $E/rb/scorer_check_e220.py "$RB_OUT/scorer-check-$ARM"
[ -n "${RB_DRY:-}" ] || { [ "$RB_RC" -eq 0 ] && rb_has '^SCORER-CHECK-E220: stand-ins PASS'; } || bad="$bad scorer-selftests"
rb_local desk local "the preflight: dmcmd_audit_v2 on the session's files, no WRITE allowed" bash $E/preflight_e220a.sh
rb_has '^dmcmd_audit: GO' || bad="$bad preflight"
for spec in "logs/selftest-run-e220a.txt ^SELFTEST-RUN-E220A.[0-9]+.of.[0-9]+.PASS$" "logs/realpath-e220a.txt ^REALPATH-E220A.[0-9]+.of.[0-9]+.PASS$" \
            "logs/realbytes-e220a.txt ^REALBYTES-E220A.[0-9]+.of.[0-9]+.PASS$" "logs/desktest-build-e220a.txt ^DESKTEST-BUILD-E220A.[0-9]+.of.[0-9]+.PASS$" \
            "logs/selftest-rb-e220a.txt ^SELFTEST-RB-E220A.[0-9]+.of.[0-9]+.PASS$" "logs/dry-listing-e220a-A.txt ^dry.listing:.[0-9]+.steps.listed,.0.exited.non-zero,.0.box.calls$" \
            "logs/dmcmd-audit-e220a.txt ^dmcmd_audit:.GO" "a2/logs/selftest-a2-e220a.txt ^SELFTEST-A2-E220A.[0-9]+.of.[0-9]+.PASS$" \
            "a2/logs/dry-listing-a2-A.txt ^dry.listing.\(A2,.arm.A\):.[0-9]+.steps.listed,.0.exited.non-zero,.0.box.calls$"; do
  set -- $spec
  rb_local read local "a desk test's log, as committed: $1" grep -cE "$2" "$E/$1"
  rb_has '^1$' || bad="$bad $(basename "$1" .txt)"
done
NW="$E tools/matmul/mm1"; [ -d "$RB_REPO/tools/claims-v3/sealed-e220" ] && NW="$NW tools/claims-v3/sealed-e220"
rb_local read local "nothing written by the checks in E220's registered files or MM1's folders: every file under $NW newer than the marker (want none)" find $NW -type f -newer "$MARK"
[ -z "${RB_DRY:-}" ] && { [ "$RB_RC" -ne 0 ] || [ -s "$RB_CAP" ]; } && bad="$bad wrote-in-lab(rc $RB_RC; $(grep -c . "$RB_CAP") file(s):$(head -n 3 "$RB_CAP" | sed 's#^# #' | tr -d '\n'))"
rb_local read local "E220's paths clean again after the checks, untracked files included" git -C "$RB_REPO" status --porcelain --untracked-files=all -- $SP
[ -z "${RB_DRY:-}" ] && { [ "$RB_RC" -ne 0 ] || [ -s "$RB_CAP" ]; } && bad="$bad status-after($(grep -c . "$RB_CAP") line(s))"
rb_local read local "HEAD after the checks" git -C "$RB_REPO" rev-parse HEAD
h1=$(rb_val '^([0-9a-f]{40})$')
[ -n "${RB_DRY:-}" ] || [ "$h0" = "$h1" ] || bad="$bad HEAD-moved"
rb_local read local "E220 arm A data in any ref: a commit on a docs/reports/data folder named *-e220-*-$DATA_SUFFIX (want none before its session)" \
  git -C "$RB_REPO" log --all --oneline -- ":(glob)docs/reports/data/*-e220-*-$DATA_SUFFIX/**"
nd=0; [ -z "${RB_DRY:-}" ] && nd=$(grep -c . "$RB_CAP")
[ "$nd" -eq 0 ] || bad="$bad E220-has-data($nd commit(s))"
rb_local read local "E220 gate-stop records in any ref (REPORTED)" git -C "$RB_REPO" log --all --oneline -- ':(glob)docs/reports/gate-stops/*-e220-*/**'
no=0; [ -z "${RB_DRY:-}" ] && no=$(grep -c . "$RB_CAP")
rb_local read local "a sealed-forecast note for E220 (REPORTED; E220.md 0: step 0's S1 gates on it)" git -C "$RB_REPO" log --oneline -- tools/claims-v3/sealed-e220
ns=0; [ -z "${RB_DRY:-}" ] && ns=$(grep -c . "$RB_CAP")
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
echo "$(date '+%F %T %Z') step=$RB_STEP arm=$ARM lists not pinned (reported):${unknown:- none}; E220 gate-stop commits: $no; sealed-forecast note commits: $ns" >> "$RB_LOG"
rb_say "desk check: the window written today for E220 arm $ARM; pulled under the lab-git lock, HEAD ${h1:0:12} descends from the registration ${reg:0:12} (subtree ${E220A_REG_SUBTREE:0:8}: the freeze line), the kit ${kit:0:12} and MM1-v3.2's land ${E220A_FREEZE:0:12}, the paths clean, HISTORY OK, the lists at their pins, the harness, the modules, the gate's pins, the timeout table, the registration's checks, the scorer's two self-tests byte-identical (into RB_OUT), the preflight GO, the desk tests' logs, nothing written in E220's registered files or MM1's folders and the paths clean again; no E220 arm A datum in any ref (E220 gate-stop commits: $no; sealed-forecast note commits: $ns)"
exit 0
