#!/usr/bin/env bash
# E222 (Q236, lane kit-e222, Fri 20 Nov 2026, before any E222 datum; E218's landed kit 5582edfc ported, the kit that ran E218 FULL on aifoundry3
# card 0 at 03:11-03:56 PST that day), the box step "step 2" (this file is s03; STEP 2, OUTSIDE THE KIT'S LIST: it pins the list by count and
# bytes, so it cannot be in it): the desk check before any box step, on the desk only (aifoundry2). E218's step 2 (tools/claims-v3/e218/rb/
# s03_desk_e218.sh, kit 5582edfc, run as stated by E218's card lane at 03:05 PST Fri 20 Nov 2026), itself E215 arm A's with fix-e215's no-write
# read, for E222; with E220's scorer-check form (tools/claims-v3/e220/rb/scorer_check_e220.py). STEP 2 NEVER REWRITES A REGISTERED FILE IN THE
# LAB CLONE (E213's lesson): every file it makes goes to RB_OUT; the registration's checks run in their --check form, which rebuild in memory and
# compare (their scratch - forecast_e222.py's candidate staging folder, made by tempfile under TMPDIR, and rules_e222.py's work folder - set into
# RB_OUT); E222's frozen scorer writes its two self-tests into its OWN folder when run as `--selftest-*` (score_e222.py main(): selftest-standins.json,
# selftest-real.json, registered files), so step 2 NEVER runs those modes: rb/scorer_check_e222.py imports the frozen scorer unchanged and calls the
# same two functions with output paths in RB_OUT, then compares each with the committed file byte for byte; and step 2 itself reads at its end
# that nothing under E222's registered files, MM1's folders, E218's and E220's folders (the scorer's pinned readers and inputs) or the seal note's
# folder was written or changed while it ran:
#   - the window first (e222_window: today, E222, arm A), or refused (10) before any call; the pull under the lab-git lock (e222_pull; never run
#     inside it);
#   - HEAD descends from E222's registration (found by its content: the commit that added E222.md, its tools/claims-v3/e222 subtree f8e6ec56...;
#     its push is E222's second freeze line) AND from the kit commit (found by its content: the commit that added KIT.md) AND from the code the
#     forecasts read in place: MM1-v3.2's land 4e386f75 and the three MM1-v3.3 candidates' lands (posimb badf08fa, gemmlnc-af4 911651ee, l3s
#     2a509f5a); HEAD is GitHub main after the pull;
#   - E222's paths clean (with every path the session, the gate, the forecasts' inputs, the registration's checks and the scorer read); the history
#     check (rb/check_history_e222.py): additions only under tools/claims-v3/e222 since the registration, no shadowing addition, nothing modified
#     or untracked on E222's run paths;
#   - EVERY LIST E222 READS at its pinned count AND its own pinned sha256 AND every entry OK: the registration's (SHA256SUMS-e222-registration,
#     REGPIN below: 30 entries) and the kit's (SHA256SUMS-e222-kit, KITPIN below, set at the kit's commit); any other file with SHA256SUMS in its
#     name under tools/claims-v3/e222 is REPORTED, never a gate;
#   - harness-e222.json re-made (CHECK PASS) and every file of it at its sha256 in the lab clone (HARNESS OK); the two modules' self-checks and the
#     kit's identity gate's pin check; the registration's own checks (forecast_e222 --check by one combined candidate call, rules_e222 --check
#     with its work in RB_OUT, plan_e222 --check, desk/kernel_e222 --check: each its --check and its SAME or PASS line; a few minutes in all,
#     single-threaded: rules_e222 reproduces MM1-v3.2's held-out record); the frozen scorer's stand-in and real-bytes self-tests through
#     rb/scorer_check_e222.py, each written into RB_OUT and byte-identical to the committed selftest-standins.json / selftest-real.json; the
#     sized plain timeout (desk/timeout_e222.py --check: CHECK PASS) and the no-kill audit (desk/nokill_e222.py: 0 lines toward a device process);
#     the preflight (dmcmd_audit_v2 GO, no WRITE); the kit's desk tests' logs as committed, each with its PASS line once, and the dry listing's
#     last line;
#   - NOTHING WRITTEN OR CHANGED BY THE CHECKS (fix-e215's form): a marker in RB_OUT is made right after the pull, and at the end no file under
#     E222's folder, tools/matmul/mm1 (MM1-v3.2's land, the candidates and the predictors and records the checks import), tools/claims-v3/e218,
#     tools/claims-v3/e220, tools/claims-v3/e220-notes or the sealed-forecast note's folder is newer than it (a rewrite with the same bytes, which
#     git status cannot see, is seen here), and E222's paths read clean again (git status, untracked files included), else 16;
#   - HEAD unchanged across all of it, else 16;
#   - NO E222 DATUM in any ref (a commit on a docs/reports/data FOLDER named *e222*-aifoundry3, read with git's glob magic: a FILE whose name holds
#     'e222' is not a datum): 16 if one exists; a gate stop's record (docs/reports/gate-stops/*e222*) and a sealed-forecast note
#     (tools/claims-v3/sealed-e222/) REPORTED.
# The numerical checks run single-threaded (OMP, OpenBLAS, MKL and NumExpr threads 1: THE CPU RULE); the card lane runs this step inside the
# round's slot (W/slot.sh).
#   RB_GITLOCK=<the lab-git lock> bash tools/claims-v3/e222/rb/s03_desk_e222.sh A
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e222.sh"
rb_init s03_desk
e222_arm "${1:-}"
e222_window
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
E=tools/claims-v3/e222
REGPIN=tools/claims-v3/e222/SHA256SUMS-e222-registration:30:de67150bee12bde15c50d0f1067d042a0cd0ca3a9a8ad74af577145d077acef7:top
KITPIN=tools/claims-v3/e222/SHA256SUMS-e222-kit:54:e2304daea2430f8b12b248a3a4fb72e16e13ffd231938344e1a23277c3079ab5:top   # the kit's own list, at its count and its own bytes (set at the kit's commit)
bad=""
e222_pull || bad="$bad pull"
[ -z "${RB_DRY:-}" ] && [ "${RB_RC:-0}" -ne 0 ] && bad="$bad pull(rc $RB_RC; a nested lab-git lock exits 75)"
rb_local read local "HEAD before the checks" git -C "$RB_REPO" rev-parse HEAD
h0=$(rb_val '^([0-9a-f]{40})$')
MARK="$RB_OUT/step2-$ARM-checks-start.marker"     # the no-write read at the end compares every registered file's time against it
TMPD="$RB_OUT/step2-$ARM-scratch-$(date +%Y%m%dT%H%M%S)-$$"   # the registration checks' scratch, new for each call (forecast_e222's staging, rules_e222's work)
if [ -n "${RB_DRY:-}" ]; then echo "--- desk: a marker file made now in <RB_OUT> (step2-$ARM-checks-start.marker), after the pull and before the checks: the no-write read at the end compares against it; the checks' scratch <RB_OUT>/step2-$ARM-scratch"
else touch -- "$MARK" || bad="$bad marker"; mkdir -p "$TMPD/rules-work" "$TMPD/tmp" || bad="$bad scratch"; fi
rb_local read local "E222's registration, by its content (the commit that added E222.md)" git -C "$RB_REPO" log --diff-filter=A --format=%H -- $E/E222.md
reg=$(rb_val '^([0-9a-f]{40})$')
rb_local read local "E222's kit commit, by its content (the commit that added KIT.md)" git -C "$RB_REPO" log --diff-filter=A --format=%H -- $E/KIT.md
kit=$(rb_val '^([0-9a-f]{40})$')
if [ -z "${RB_DRY:-}" ]; then
  if [ -z "$reg" ]; then bad="$bad registration(missing)"; else
    rb_local read local "the registration's e222 subtree" git -C "$RB_REPO" rev-parse "$reg:$E"
    rb_has "^$E222_REG_SUBTREE\$" || bad="$bad registration-subtree"
    rb_local read local "the registration is an ancestor of HEAD (its push froze every forecast, the points, the rules, the plan and the scorer)" git -C "$RB_REPO" merge-base --is-ancestor "$reg" HEAD || bad="$bad registration-ancestry"
  fi
  if [ -z "$kit" ]; then bad="$bad kit(missing)"; else
    rb_local read local "the kit commit is an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$kit" HEAD || bad="$bad kit-ancestry"
  fi
fi
rb_local read local "MM1-v3.2's land (the baseline the forecasts read in place), an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$E222_FREEZE" HEAD
[ -n "${RB_DRY:-}" ] || [ "$RB_RC" -eq 0 ] || bad="$bad mm1v32-land-ancestry"
for c in $E222_CANDS; do
  rb_local read local "an MM1-v3.3 candidate's land (${c:0:12}), an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$c" HEAD
  [ -n "${RB_DRY:-}" ] || [ "$RB_RC" -eq 0 ] || bad="$bad candidate-land-ancestry(${c:0:8})"
done
SP="$E tools/claims-v3/sealed-e222 tools/matmul/mm1/v3.2 tools/matmul/mm1/v3.2-terms tools/matmul/mm1/v3.3-cands tools/matmul/mm1/v3.1 \
  tools/matmul/mm1/v3 tools/matmul/mm1/v2 tools/claims-v3/e136/rgm136 tools/claims-v3/e211/rgm211 tools/claims-v3/e211/kernel-e211.json \
  tools/claims-v3/kinds/tiles tools/claims-v3/kinds/kinds.json tools/claims-v3/q141k-runbook tools/claims-v3/e128 tools/claims-v3/e206 \
  tools/claims-v3/e213 tools/claims-v3/e215 tools/claims-v3/e218 tools/claims-v3/e220 tools/claims-v3/e220-notes \
  docs/reports/data/2026-11-20-e218-blind-matmul-aifoundry3 docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry3 \
  docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry3 docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry1-c1 \
  workloads/nocbench/analyze.py tools/claims-v3/dmcmd_audit_v2.py tools/claims-v3/dmcmd_table_v2.json"     # E222's paths (one list, read here
# and again at the end; the mesh map workloads/nocbench/analyze.py is read by MM1-v3.2's layout module through E215's v01_map.py, and E213 arm B's
# scores by run_v32; E218's and E220's folders hold the scorer's pinned reader and inputs, E220's dated note 1 the scanner's pinned reading)
rb_local read local "E222's paths clean" git -C "$RB_REPO" status --short $SP
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
rb_local read local "the history check: additions only under $E since the registration, no shadowing addition (check_history_e222.py)" \
  /usr/bin/python3 -I -B $E/rb/check_history_e222.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || bad="$bad history"
paths=""; for spec in $REGPIN $KITPIN; do paths="$paths ${spec%%:*}"; done
rb_local read local "the own sha256 of the lists E222 reads (pinned)" sha256sum $paths
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
rb_local desk local "harness-e222.json re-made" /usr/bin/python3 -I -B $E/check_e222.py --check
rb_has '^CHECK PASS' || bad="$bad harness-rebuild"
rb_local desk local "every harness file at its sha256 in the lab clone" /usr/bin/python3 -I -B $E/check_e222.py --box
rb_has '^HARNESS OK: ' || bad="$bad harness"
rb_local read local "the common module's self-check (the arm, the two families, the order, the G block last, the stops and the latch reading, the gates, the argv, the walk, the records, the forecasts)" /usr/bin/python3 -I -B $E/e222_common.py
rb_has '^E222-COMMON SELF-CHECK PASS' || bad="$bad common"
rb_local read local "the identity module's self-check" /usr/bin/python3 -I -B $E/e222_ident.py
rb_has '^E222-IDENT SELF-CHECK PASS' || bad="$bad ident"
rb_local read local "the kit's identity gate's pins (kernel-e222.json, E206's and E211's)" /usr/bin/python3 -I -B $E/ident_e222.py --check
rb_has '^CHECK PASS' || bad="$bad ident-gate"
for spec in "forecast_e222.py@--check ^forecast_e222.--check.\(one.combined.candidate.call\):.SAME$" \
            "rules_e222.py@--check@--work@$TMPD/rules-work ^rules_e222.--check:.SAME$" "plan_e222.py@--check ^plan_e222.--check:.SAME$" \
            "desk/kernel_e222.py@--check ^PASS$"; do
  set -- $spec
  cmd=$(echo "$1" | tr '@' ' ')
  rb_local desk local "the registration's $cmd (its scratch under RB_OUT: TMPDIR)" env TMPDIR="$TMPD/tmp" /usr/bin/python3 -I -B $E/$cmd
  [ -n "${RB_DRY:-}" ] || { [ "$RB_RC" -eq 0 ] && grep -qE "$2" "$RB_CAP"; } || bad="$bad $(basename "${cmd%% *}" .py)"
done
rb_local desk local "the frozen scorer's two self-tests, written into RB_OUT only and compared with the committed files (rb/scorer_check_e222.py; the scorer refuses, 4, if a frozen file changed)" \
  env TMPDIR="$TMPD/tmp" /usr/bin/python3 -I -B $E/rb/scorer_check_e222.py "$RB_OUT/scorer-check-$ARM"
[ -n "${RB_DRY:-}" ] || { [ "$RB_RC" -eq 0 ] && rb_has '^SCORER-CHECK-E222: stand-ins PASS \(byte-identical to selftest-standins.json\); real bytes OK \(byte-identical to selftest-real.json\)$'; } || bad="$bad scorer-check"
rb_local desk local "the sized plain timeout (desk/timeout_e222.py --check: no frozen GEMM's check of C cut off; E218's R0 lesson)" /usr/bin/python3 -I -B $E/desk/timeout_e222.py --check
rb_has '^TIMEOUT-E222 CHECK PASS' || bad="$bad timeout"
rb_local read local "the no-kill audit (desk/nokill_e222.py: no line that could send SIGKILL toward a device process)" /usr/bin/python3 -I -B $E/desk/nokill_e222.py "$RB_REPO"
[ -n "${RB_DRY:-}" ] || { [ "$RB_RC" -eq 0 ] && rb_has '^NOKILL-E222: 0 lines that could send SIGKILL toward a device process'; } || bad="$bad nokill"
rb_local desk local "the preflight: dmcmd_audit_v2 on the session's files, no WRITE allowed" bash $E/preflight_e222.sh
rb_has '^dmcmd_audit: GO' || bad="$bad preflight"
for spec in "logs/selftest-run-e222.txt ^SELFTEST-RUN-E222.[0-9]+.of.[0-9]+.PASS$" "logs/realpath-e222.txt ^REALPATH-E222.[0-9]+.of.[0-9]+.PASS$" \
            "logs/realbytes-e222.txt ^REALBYTES-E222.[0-9]+.of.[0-9]+.PASS$" "logs/desktest-build-e222.txt ^DESKTEST-BUILD-E222.[0-9]+.of.[0-9]+.PASS$" \
            "logs/selftest-rb-e222.txt ^SELFTEST-RB-E222.[0-9]+.of.[0-9]+.PASS$" "logs/dry-listing-e222-A.txt ^dry.listing:.[0-9]+.steps.listed,.0.exited.non-zero,.0.box.calls$" \
            "logs/dmcmd-audit-e222.txt ^dmcmd_audit:.GO" "logs/nokill-e222.txt ^NOKILL-E222:.0.lines.that.could.send.SIGKILL.toward.a.device.process" \
            "logs/timeouts-e222.txt ^TIMEOUT-E222.CHECK.PASS"; do
  set -- $spec
  rb_local read local "a desk test's log, as committed: $1" grep -cE "$2" "$E/$1"
  rb_has '^1$' || bad="$bad $(basename "$1" .txt)"
done
NW="$E tools/matmul/mm1 tools/claims-v3/e218 tools/claims-v3/e220 tools/claims-v3/e220-notes"
[ -d "$RB_REPO/tools/claims-v3/sealed-e222" ] && NW="$NW tools/claims-v3/sealed-e222"
rb_local read local "nothing written by the checks in E222's registered files, MM1's, E218's or E220's folders: every file under $NW newer than the marker (want none)" find $NW -type f -newer "$MARK"
[ -z "${RB_DRY:-}" ] && { [ "$RB_RC" -ne 0 ] || [ -s "$RB_CAP" ]; } && bad="$bad wrote-in-lab(rc $RB_RC; $(grep -c . "$RB_CAP") file(s):$(head -n 3 "$RB_CAP" | sed 's#^# #' | tr -d '\n'))"
rb_local read local "E222's paths clean again after the checks, untracked files included" git -C "$RB_REPO" status --porcelain --untracked-files=all -- $SP
[ -z "${RB_DRY:-}" ] && { [ "$RB_RC" -ne 0 ] || [ -s "$RB_CAP" ]; } && bad="$bad status-after($(grep -c . "$RB_CAP") line(s))"
rb_local read local "HEAD after the checks" git -C "$RB_REPO" rev-parse HEAD
h1=$(rb_val '^([0-9a-f]{40})$')
[ -n "${RB_DRY:-}" ] || [ "$h0" = "$h1" ] || bad="$bad HEAD-moved"
rb_local read local "E222 data in any ref: a commit on a docs/reports/data folder named *e222*-$DATA_SUFFIX (want none before its session)" \
  git -C "$RB_REPO" log --all --oneline -- ":(glob)docs/reports/data/*e222*-$DATA_SUFFIX/**"
nd=0; [ -z "${RB_DRY:-}" ] && nd=$(grep -c . "$RB_CAP")
[ "$nd" -eq 0 ] || bad="$bad E222-has-data($nd commit(s))"
rb_local read local "E222 gate-stop records in any ref (REPORTED)" git -C "$RB_REPO" log --all --oneline -- ':(glob)docs/reports/gate-stops/*e222*/**'
no=0; [ -z "${RB_DRY:-}" ] && no=$(grep -c . "$RB_CAP")
rb_local read local "a sealed-forecast note for E222 (REPORTED; E222.md 0: step 0's S1 gates on it)" git -C "$RB_REPO" log --oneline -- tools/claims-v3/sealed-e222
ns=0; [ -z "${RB_DRY:-}" ] && ns=$(grep -c . "$RB_CAP")
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
echo "$(date '+%F %T %Z') step=$RB_STEP arm=$ARM lists not pinned (reported):${unknown:- none}; E222 gate-stop commits: $no; sealed-forecast note commits: $ns" >> "$RB_LOG"
rb_say "desk check: the window written today for E222 arm $ARM; pulled under the lab-git lock, HEAD ${h1:0:12} descends from the registration ${reg:0:12} (subtree ${E222_REG_SUBTREE:0:8}), the kit ${kit:0:12}, MM1-v3.2's land ${E222_FREEZE:0:12} and the three candidates' lands, the paths clean, HISTORY OK, the lists at their pins, the harness, the modules, the gate's pins, the registration's checks, the scorer's two self-tests byte-identical (written in RB_OUT only), the sized timeout, the no-kill audit, the preflight GO, the desk tests' logs, nothing written in E222's registered files, MM1's, E218's or E220's folders and the paths clean again; no E222 datum in any ref (E222 gate-stop commits: $no; sealed-forecast note commits: $ns)"
exit 0
