#!/usr/bin/env bash
# E211 (Q204, lane kit-e211, Tue 17 Nov 2026, before any E211 datum), the box step "step 2" (this file is s03; STEP 2, OUTSIDE THE KIT'S LIST:
# it pins the list by count and bytes, so it cannot be in it): the desk check before any box step, on the desk only (aifoundry2). E206's step 2
# (tools/claims-v3/e206/rb/s03_desk_e206.sh, landed in 906699ea), as E207's kit ported it (Q199), for E211:
#   - the window first (e211_window: today, E211, arm A), or refused (10) before any call; the pull under the lab-git lock (e211_pull; never
#     run inside it);
#   - HEAD descends from E211's registration (found by its content: the commit that added E211.md, its tools/claims-v3/e211 subtree
#     fa109d01...) AND from the kit commit (found by its content: the commit that added KIT.md);
#   - E211's paths clean (with every path the session, the gate, the forecasts' inputs and the scorer read); the history check
#     (rb/check_history_e211.py): additions only under tools/claims-v3/e211 since the registration, no shadowing addition, nothing modified or
#     untracked on E211's run paths;
#   - EVERY LIST E211 READS at its pinned count AND its own pinned sha256 AND every entry OK: the registration's (SHA256SUMS-e211-registration,
#     REGPIN below: 38 entries since fix-e211's Amendment A1, 37 at reg-e211's land) and the kit's (SHA256SUMS-e211-kit, KITPIN below, set at
#     the kit's commit); any other file with SHA256SUMS in its name under
#     tools/claims-v3/e211 is REPORTED, never a gate;
#   - harness-e211.json re-made (CHECK PASS) and every file of it at its sha256 in the lab clone (HARNESS OK); the two modules' self-checks;
#     the registration's own checks (make_rgm211, desk/kernel_e211, ident_e211, points, forecast, rules and plan --check, each its PASS or
#     SAME line; the map's --check, about 4 minutes, is the verifier's, not this step's); the frozen scorer's stand-in self-test, rc 0 and
#     byte-identical to the committed selftest-standins-e211.json; the preflight (dmcmd_audit_v2 GO, no WRITE); the kit's desk tests' logs as
#     committed, each with its PASS line once, the simulator check's record and the dry listing's last line;
#   - HEAD unchanged across all of it, else 16;
#   - NO E211 DATUM in any ref (docs/reports/data/*e211*): 16 if one exists (E211 has run); a gate stop's record (docs/reports/gate-stops/
#     *e211*) and a sealed-forecast note (tools/claims-v3/sealed-e211/) REPORTED;
#   - E207'S DATA AT HEAD (fix-e211, Tue 17 Nov 2026, before any E211 datum: E211.md section 8 and Amendment A1, clause 4; verify-e211's
#     finding that no kit code checked it): a docs/reports/data/ folder whose name holds e207, else 16 with the word "E207-data(...)" in the
#     failure list. E211 books no card before E207's data commit (its gemmL twins 2x3x2, 3x3x4 and 6x6x6 fp32 are E207 blind points), with
#     no exception for an E207 chain that stopped short (that needs the orchestrator's dated ruling and a dated amendment first). A readiness
#     lane that runs this step before E207's data commit reads "E207-data(...)" ALONE in the failure list as the queue's gate, not a defect:
#     every other check of this step still ran and printed its word.
#   RB_GITLOCK=<the lab-git lock> bash tools/claims-v3/e211/rb/s03_desk_e211.sh A
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e211.sh"
rb_init s03_desk
e211_arm "${1:-}"
e211_window
E=tools/claims-v3/e211
REGPIN=tools/claims-v3/e211/SHA256SUMS-e211-registration:38:477fb113cd6a6b6cd3cea12b1ff7ca6264e55a7b1e2fb5a40e9aeb3a99bac166:top
KITPIN=tools/claims-v3/e211/SHA256SUMS-e211-kit:70:3500fbc5033b64c2b780327e5eb2a20c91414dd5b216be21006338baa62b0872:top   # the kit's own list, at its count and its own bytes (set at the kit's commit)
bad=""
e211_pull || bad="$bad pull"
[ -z "${RB_DRY:-}" ] && [ "${RB_RC:-0}" -ne 0 ] && bad="$bad pull(rc $RB_RC; a nested lab-git lock exits 75)"
rb_local read local "HEAD before the checks" git -C "$RB_REPO" rev-parse HEAD
h0=$(rb_val '^([0-9a-f]{40})$')
rb_local read local "E211's registration, by its content (the commit that added E211.md)" git -C "$RB_REPO" log --diff-filter=A --format=%H -- $E/E211.md
reg=$(rb_val '^([0-9a-f]{40})$')
rb_local read local "E211's kit commit, by its content (the commit that added KIT.md)" git -C "$RB_REPO" log --diff-filter=A --format=%H -- $E/KIT.md
kit=$(rb_val '^([0-9a-f]{40})$')
if [ -z "${RB_DRY:-}" ]; then
  if [ -z "$reg" ]; then bad="$bad registration(missing)"; else
    rb_local read local "the registration's e211 subtree" git -C "$RB_REPO" rev-parse "$reg:$E"
    rb_has "^$E211_REG_SUBTREE\$" || bad="$bad registration-subtree"
    rb_local read local "the registration is an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$reg" HEAD || bad="$bad registration-ancestry"
  fi
  if [ -z "$kit" ]; then bad="$bad kit(missing)"; else
    rb_local read local "the kit commit is an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$kit" HEAD || bad="$bad kit-ancestry"
  fi
fi
rb_local read local "E211's paths clean" git -C "$RB_REPO" status --short $E tools/matmul/mm1/v1 tools/claims-v3/e136/rgm136 tools/claims-v3/kinds/tiles \
  tools/claims-v3/kinds/kinds.json tools/claims-v3/q141k-runbook tools/claims-v3/e128 tools/claims-v3/e206 tools/claims-v3/e190 tools/ledger \
  docs/reports/data/2026-11-01-e101-real-matmul tools/claims-v3/dmcmd_audit_v2.py tools/claims-v3/dmcmd_table_v2.json
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
rb_local read local "the history check: additions only under $E since the registration, no shadowing addition (check_history_e211.py)" \
  /usr/bin/python3 -I -B $E/rb/check_history_e211.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || bad="$bad history"
paths=""; for spec in $REGPIN $KITPIN; do paths="$paths ${spec%%:*}"; done
rb_local read local "the own sha256 of the lists E211 reads (pinned)" sha256sum $paths
own=$RB_CAP
for spec in $REGPIN $KITPIN; do
  IFS=: read -r l pin hpin form <<EOF2
$spec
EOF2
  if [ "$form" = dir ]; then     # a folder's own list: its paths beside it (none of E211's: both are top-relative)
    RB_CWD="$RB_REPO/$(dirname "$l")" rb_local read local "the list $l (pinned at $pin entries and its own sha256)" sha256sum -c "$(basename "$l")"
  else                          # paths from the repository's top
    RB_CWD="$RB_REPO" rb_local read local "the list $l (pinned at $pin entries and its own sha256)" sha256sum -c "$l"
  fi
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
rb_local desk local "harness-e211.json re-made" /usr/bin/python3 -I -B $E/check_e211.py --check
rb_has '^CHECK PASS' || bad="$bad harness-rebuild"
rb_local desk local "every harness file at its sha256 in the lab clone" /usr/bin/python3 -I -B $E/check_e211.py --box
rb_has '^HARNESS OK: ' || bad="$bad harness"
rb_local read local "the common module's self-check (the arm, the order, the stops and the latch reading, the gate, the argv, the walk, the records, the forecast)" /usr/bin/python3 -I -B $E/e211_common.py
rb_has '^E211-COMMON SELF-CHECK PASS' || bad="$bad common"
rb_local read local "the identity module's self-check" /usr/bin/python3 -I -B $E/e211_ident.py
rb_has '^E211-IDENT SELF-CHECK PASS' || bad="$bad ident"
for spec in "make_rgm211.py ^make_rgm211.--check:.PASS" "desk/kernel_e211.py ^CHECK.PASS" "ident_e211.py ^CHECK.PASS" \
            "points_e211.py ^points_e211.--check:.PASS" "forecast_e211.py ^forecast_e211.--check:.json.SAME,.csv.SAME,.txt.SAME" \
            "rules_e211.py ^rules_e211.--check:.PASS" "plan_e211.py ^plan_e211.--check:.PASS"; do
  set -- $spec
  rb_local desk local "the registration's $1 --check" /usr/bin/python3 -I -B $E/$1 --check
  [ -n "${RB_DRY:-}" ] || grep -qE "$2" "$RB_CAP" || bad="$bad $(basename "$1" .py)"
done
same() {  # same <rc> <made file> <committed file> [<made> <committed>]: rc 0 and every pair byte-identical (never false in a dry listing)
  [ -n "${RB_DRY:-}" ] && return 0
  local rc=$1; shift
  [ "$rc" -eq 0 ] || return 1
  while [ $# -ge 2 ]; do cmp -s "$1" "$RB_REPO/$2" || return 1; shift 2; done
  return 0
}
RB_STDOUT="$RB_OUT/selftest-standins-e211-check.txt" rb_local desk local "the frozen scorer's stand-in self-test (it refuses, 4, if a frozen file changed)" /usr/bin/python3 -I -B $E/score_e211.py --selftest-standins "$RB_OUT/selftest-standins-e211-check.json"
same "$RB_RC" "$RB_OUT/selftest-standins-e211-check.json" "$E/selftest-standins-e211.json" || bad="$bad selftest-standins"
[ -n "${RB_DRY:-}" ] || grep -q '^SELFTEST PASS' "$RB_OUT/selftest-standins-e211-check.txt" || bad="$bad selftest-standins-words"
rb_local desk local "the preflight: dmcmd_audit_v2 on the session's files, no WRITE allowed" bash $E/preflight_e211.sh
rb_has '^dmcmd_audit: GO' || bad="$bad preflight"
for spec in "logs/selftest-run-e211.txt ^SELFTEST-RUN-E211.[0-9]+.of.[0-9]+.PASS$" "logs/realpath-e211.txt ^REALPATH-E211.[0-9]+.of.[0-9]+.PASS$" \
            "logs/realbytes-e211.txt ^REALBYTES-E211.[0-9]+.of.[0-9]+.PASS$" "logs/desktest-build-e211.txt ^DESKTEST-BUILD-E211.[0-9]+.of.[0-9]+.PASS$" \
            "logs/selftest-rb-e211.txt ^SELFTEST-RB-E211.[0-9]+.of.[0-9]+.PASS$" "logs/simcheck-e211.txt ^SIMCHECK-E211.[0-9]+.of.[0-9]+.AS.STATED$" \
            "logs/dry-listing-e211.txt ^dry.listing:.[0-9]+.steps.listed,.0.exited.non-zero,.0.box.calls$" "logs/dmcmd-audit-e211.txt ^dmcmd_audit:.GO"; do
  set -- $spec
  rb_local read local "a desk test's log, as committed: $1" grep -cE "$2" "$E/$1"
  rb_has '^1$' || bad="$bad $(basename "$1" .txt)"
done
rb_local read local "HEAD after the checks" git -C "$RB_REPO" rev-parse HEAD
h1=$(rb_val '^([0-9a-f]{40})$')
[ -n "${RB_DRY:-}" ] || [ "$h0" = "$h1" ] || bad="$bad HEAD-moved"
rb_local read local "E211 data in any ref (want none before its session)" git -C "$RB_REPO" log --all --oneline -- 'docs/reports/data/*e211*'
nd=0; [ -z "${RB_DRY:-}" ] && nd=$(grep -c . "$RB_CAP")
[ "$nd" -eq 0 ] || bad="$bad E211-has-data($nd commit(s))"
rb_local read local "E207's data at HEAD (E211.md 8, A1 clause 4: E211 books no card before E207's data commit; a docs/reports/data folder named *e207*)" \
  git -C "$RB_REPO" ls-tree -d --name-only HEAD docs/reports/data/
n7=0; [ -z "${RB_DRY:-}" ] && n7=$(grep -c -- '^docs/reports/data/[^/]*e207' "$RB_CAP")
[ -n "${RB_DRY:-}" ] || [ "$n7" -gt 0 ] || bad="$bad E207-data(no docs/reports/data/*e207* folder at HEAD: E211 books no card before E207's data commit, E211.md 8 and A1 clause 4)"
rb_local read local "E211 gate-stop records in any ref (REPORTED)" git -C "$RB_REPO" log --all --oneline -- 'docs/reports/gate-stops/*e211*'
no=0; [ -z "${RB_DRY:-}" ] && no=$(grep -c . "$RB_CAP")
rb_local read local "a sealed-forecast note for E211 (REPORTED; E211.md 0)" git -C "$RB_REPO" log --oneline -- tools/claims-v3/sealed-e211
ns=0; [ -z "${RB_DRY:-}" ] && ns=$(grep -c . "$RB_CAP")
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
echo "$(date '+%F %T %Z') step=$RB_STEP arm=$ARM lists not pinned (reported):${unknown:- none}; E211 gate-stop commits: $no; sealed-forecast note commits: $ns; E207 data folders at HEAD: $n7" >> "$RB_LOG"
rb_say "desk check: the window written today for E211; pulled under the lab-git lock, HEAD ${h1:0:12} descends from the registration ${reg:0:12} (subtree ${E211_REG_SUBTREE:0:8}) and the kit ${kit:0:12}, the paths clean, HISTORY OK, the lists at their pinned counts and bytes (the registration's $(echo "$REGPIN" | cut -d: -f2); the kit's $(echo "$KITPIN" | cut -d: -f2)), lists not pinned (reported):${unknown:- none}; the harness re-made and at its sha256, both self-checks, the registration's checks, the scorer's forecasts and self-tests byte-identical, the preflight GO, the desk tests' logs; E211 data commits: $nd; E207 data folders at HEAD: $n7; gate-stop commits (reported): $no; sealed-forecast note commits (reported): $ns"
