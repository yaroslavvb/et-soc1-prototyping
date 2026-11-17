#!/usr/bin/env bash
# E207 (Q199, lane kit-e207, Mon 16 Nov 2026, before any E207 datum), the box step "step 2" (this file is s03; STEP 2, OUTSIDE THE KIT'S LIST:
# it pins the list by count and bytes, so it cannot be in it): the desk check before any box step, on the desk only (aifoundry2). E206's step 2
# (tools/claims-v3/e206/rb/s03_desk_e206.sh, landed in 906699ea) for E207:
#   - the window first (e207_window: today, E207, arm A), or refused (10) before any call; the pull under the lab-git lock (e207_pull; never
#     run inside it);
#   - HEAD descends from E207's registration (found by its content: the commit that added E207.md, its tools/claims-v3/e207 subtree
#     d2089226..., the registration with amendment A1) AND from the kit commit (found by its content: the commit that added KIT.md);
#   - E207's paths clean (with every path the session, the scorer and its F2 route read); the history check (rb/check_history_e207.py):
#     additions only under tools/claims-v3/e207 since the registration, no shadowing addition, nothing modified or untracked on E207's run paths;
#   - EVERY LIST E207 READS at its pinned count AND its own pinned sha256 AND every entry OK: the registration's (SHA256SUMS-e207-registration,
#     24) and the kit's (SHA256SUMS-e207-kit, KITPIN below, set at the kit's commit); MM1-v1's folder list (tools/matmul/mm1/v1/SHA256SUMS,
#     77, E207.md section 0's anchor f77084ef...) every entry OK; any other file with SHA256SUMS in its name under tools/claims-v3/e207 is
#     REPORTED, never a gate;
#   - harness-e207.json re-made (CHECK PASS) and every file of it at its sha256 in the lab clone (HARNESS OK); the two modules' self-checks;
#     the registration's own checks (points, rules, plan and kernel --check: PASS; the frozen scorer's --forecasts and its two self-tests, each
#     rc 0 and byte-identical to the committed forecasts-e207.txt, selftest-standins.json / .txt and selftest-e206.json / .txt); the preflight
#     (dmcmd_audit_v2 GO, no WRITE); the kit's desk tests' logs as committed, each with its PASS line once, and the dry listing's last line;
#   - HEAD unchanged across all of it, else 16;
#   - NO E207 DATUM in any ref (docs/reports/data/*e207*): 16 if one exists (E207 has run); a gate stop's record (docs/reports/gate-stops/
#     *e207*) and a sealed-forecast note (tools/claims-v3/sealed-e207/) REPORTED.
#   RB_GITLOCK=<the lab-git lock> bash tools/claims-v3/e207/rb/s03_desk_e207.sh A
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e207.sh"
rb_init s03_desk
e207_arm "${1:-}"
e207_window
E=tools/claims-v3/e207
REGPIN=tools/claims-v3/e207/SHA256SUMS-e207-registration:24:b97becf29ff07c3b14c1f37068414042d3e3e0b6727afd726914687b09c215a2:top   # fix-e207: with amendment A1 (24 entries)
KITPIN=tools/claims-v3/e207/SHA256SUMS-e207-kit:45:82b101641f7dfdaec870cd8f6e183306da1466c269917c8819c64b304527faf2:top   # the kit's own list, at its count and its own bytes (set at the kit's commit)
V1PIN=tools/matmul/mm1/v1/SHA256SUMS:77:f77084ef6342964eafbea14d104ffc4dd324e83ee14cc4241158840a51ae468f:dir   # MM1-v1's folder as landed (E207.md 0)
bad=""
e207_pull || bad="$bad pull"
[ -z "${RB_DRY:-}" ] && [ "${RB_RC:-0}" -ne 0 ] && bad="$bad pull(rc $RB_RC; a nested lab-git lock exits 75)"
rb_local read local "HEAD before the checks" git -C "$RB_REPO" rev-parse HEAD
h0=$(rb_val '^([0-9a-f]{40})$')
rb_local read local "E207's registration, by its content (the commit that added E207.md)" git -C "$RB_REPO" log --diff-filter=A --format=%H -- $E/E207.md
reg=$(rb_val '^([0-9a-f]{40})$')
rb_local read local "E207's kit commit, by its content (the commit that added KIT.md)" git -C "$RB_REPO" log --diff-filter=A --format=%H -- $E/KIT.md
kit=$(rb_val '^([0-9a-f]{40})$')
if [ -z "${RB_DRY:-}" ]; then
  if [ -z "$reg" ]; then bad="$bad registration(missing)"; else
    rb_local read local "the registration's e207 subtree" git -C "$RB_REPO" rev-parse "$reg:$E"
    rb_has "^$E207_REG_SUBTREE\$" || bad="$bad registration-subtree"
    rb_local read local "the registration is an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$reg" HEAD || bad="$bad registration-ancestry"
  fi
  if [ -z "$kit" ]; then bad="$bad kit(missing)"; else
    rb_local read local "the kit commit is an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$kit" HEAD || bad="$bad kit-ancestry"
  fi
fi
rb_local read local "E207's paths clean" git -C "$RB_REPO" status --short $E tools/matmul/mm1/v1 tools/claims-v3/e136/rgm136 tools/claims-v3/kinds/tiles \
  tools/claims-v3/kinds/blind4 tools/claims-v3/kinds/blind3 tools/claims-v3/kinds/kinds.json tools/claims-v3/q141k-runbook tools/claims-v3/e128 \
  tools/claims-v3/e206 tools/claims-v3/e190 tools/ledger tools/claims-v3/dmcmd_audit_v2.py tools/claims-v3/dmcmd_table_v2.json
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
rb_local read local "the history check: additions only under $E since the registration, no shadowing addition (check_history_e207.py)" \
  /usr/bin/python3 -I -B $E/rb/check_history_e207.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || bad="$bad history"
paths=""; for spec in $REGPIN $KITPIN $V1PIN; do paths="$paths ${spec%%:*}"; done
rb_local read local "the own sha256 of the lists E207 reads (pinned)" sha256sum $paths
own=$RB_CAP
for spec in $REGPIN $KITPIN $V1PIN; do
  IFS=: read -r l pin hpin form <<EOF2
$spec
EOF2
  if [ "$form" = dir ]; then     # a folder's own list: its paths beside it (MM1-v1's SHA256SUMS)
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
rb_local desk local "harness-e207.json re-made" /usr/bin/python3 -I -B $E/check_e207.py --check
rb_has '^CHECK PASS' || bad="$bad harness-rebuild"
rb_local desk local "every harness file at its sha256 in the lab clone" /usr/bin/python3 -I -B $E/check_e207.py --box
rb_has '^HARNESS OK: ' || bad="$bad harness"
rb_local read local "the common module's self-check (the arm, the order, the stops and the latch reading, the gate, the argv, the records, MM1-v1's file)" /usr/bin/python3 -I -B $E/e207_common.py
rb_has '^E207-COMMON SELF-CHECK PASS' || bad="$bad common"
rb_local read local "the identity module's self-check" /usr/bin/python3 -I -B $E/e207_ident.py
rb_has '^E207-IDENT SELF-CHECK PASS' || bad="$bad ident"
for s in points_e207.py rules_e207.py plan_e207.py desk/kernel_e207.py; do
  rb_local desk local "the registration's $s --check" /usr/bin/python3 -I -B $E/$s --check
  rb_has '^PASS' || bad="$bad $(basename "$s" .py)"
done
same() {  # same <rc> <made file> <committed file> [<made> <committed>]: rc 0 and every pair byte-identical (never false in a dry listing)
  [ -n "${RB_DRY:-}" ] && return 0
  local rc=$1; shift
  [ "$rc" -eq 0 ] || return 1
  while [ $# -ge 2 ]; do cmp -s "$1" "$RB_REPO/$2" || return 1; shift 2; done
  return 0
}
RB_STDOUT="$RB_OUT/forecasts-e207-check.txt" rb_local desk local "the frozen scorer's --forecasts (refuses, 4, if a frozen file changed)" /usr/bin/python3 -I -B $E/score_e207.py --forecasts
same "$RB_RC" "$RB_OUT/forecasts-e207-check.txt" "$E/forecasts-e207.txt" || bad="$bad forecasts"
RB_STDOUT="$RB_OUT/selftest-standins-e207-check.txt" rb_local desk local "the frozen scorer's stand-in self-test" /usr/bin/python3 -I -B $E/score_e207.py --selftest-standins "$RB_OUT/selftest-standins-e207-check.json"
same "$RB_RC" "$RB_OUT/selftest-standins-e207-check.json" "$E/selftest-standins.json" "$RB_OUT/selftest-standins-e207-check.txt" "$E/selftest-standins.txt" || bad="$bad selftest-standins"
RB_STDOUT="$RB_OUT/selftest-e206-e207-check.txt" rb_local desk local "the frozen scorer's E206 self-test" /usr/bin/python3 -I -B $E/score_e207.py --selftest-e206 "$RB_OUT/selftest-e206-e207-check.json"
same "$RB_RC" "$RB_OUT/selftest-e206-e207-check.json" "$E/selftest-e206.json" "$RB_OUT/selftest-e206-e207-check.txt" "$E/selftest-e206.txt" || bad="$bad selftest-e206"
rb_local desk local "the preflight: dmcmd_audit_v2 on the session's files, no WRITE allowed" bash $E/preflight_e207.sh
rb_has '^dmcmd_audit: GO' || bad="$bad preflight"
for spec in "logs/selftest-run-e207.txt ^SELFTEST-RUN-E207.[0-9]+.of.[0-9]+.PASS$" "logs/realpath-e207.txt ^REALPATH-E207.[0-9]+.of.[0-9]+.PASS$" \
            "logs/realbytes-e207.txt ^REALBYTES-E207.[0-9]+.of.[0-9]+.PASS$" "logs/desktest-build-e207.txt ^DESKTEST-BUILD-E207.[0-9]+.of.[0-9]+.PASS$" \
            "logs/selftest-rb-e207.txt ^SELFTEST-RB-E207.[0-9]+.of.[0-9]+.PASS$" \
            "logs/dry-listing-e207.txt ^dry.listing:.[0-9]+.steps.listed,.0.exited.non-zero,.0.box.calls$" "logs/dmcmd-audit-e207.txt ^dmcmd_audit:.GO"; do
  set -- $spec
  rb_local read local "a desk test's log, as committed: $1" grep -cE "$2" "$E/$1"
  rb_has '^1$' || bad="$bad $(basename "$1" .txt)"
done
rb_local read local "HEAD after the checks" git -C "$RB_REPO" rev-parse HEAD
h1=$(rb_val '^([0-9a-f]{40})$')
[ -n "${RB_DRY:-}" ] || [ "$h0" = "$h1" ] || bad="$bad HEAD-moved"
rb_local read local "E207 data in any ref (want none before its session)" git -C "$RB_REPO" log --all --oneline -- 'docs/reports/data/*e207*'
nd=0; [ -z "${RB_DRY:-}" ] && nd=$(grep -c . "$RB_CAP")
[ "$nd" -eq 0 ] || bad="$bad E207-has-data($nd commit(s))"
rb_local read local "E207 gate-stop records in any ref (REPORTED)" git -C "$RB_REPO" log --all --oneline -- 'docs/reports/gate-stops/*e207*'
no=0; [ -z "${RB_DRY:-}" ] && no=$(grep -c . "$RB_CAP")
rb_local read local "a sealed-forecast note for E207 (REPORTED; E207.md 0)" git -C "$RB_REPO" log --oneline -- tools/claims-v3/sealed-e207
ns=0; [ -z "${RB_DRY:-}" ] && ns=$(grep -c . "$RB_CAP")
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
echo "$(date '+%F %T %Z') step=$RB_STEP arm=$ARM lists not pinned (reported):${unknown:- none}; E207 gate-stop commits: $no; sealed-forecast note commits: $ns" >> "$RB_LOG"
rb_say "desk check: the window written today for E207; pulled under the lab-git lock, HEAD ${h1:0:12} descends from the registration ${reg:0:12} (subtree ${E207_REG_SUBTREE:0:8}) and the kit ${kit:0:12}, the paths clean, HISTORY OK, the lists at their pinned counts and bytes ($(echo "$REGPIN" | cut -d: -f2); the kit's $(echo "$KITPIN" | cut -d: -f2); MM1-v1's 77), lists not pinned (reported):${unknown:- none}; the harness re-made and at its sha256, both self-checks, the registration's checks, the scorer's forecasts and self-tests byte-identical, the preflight GO, the desk tests' logs; E207 data commits: $nd; gate-stop commits (reported): $no; sealed-forecast note commits (reported): $ns"
