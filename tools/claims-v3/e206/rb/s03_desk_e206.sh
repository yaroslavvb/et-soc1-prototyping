#!/usr/bin/env bash
# E206 (Q198, lane kit-e206, Mon 16 Nov 2026, before any E206 datum), the box step "step 2" (this file is s03; STEP 2, OUTSIDE THE KIT'S LIST:
# it pins the list by count and bytes, so it cannot be in it): the desk check before any box step, on the desk only (aifoundry2), for one arm.
# E190's step 2 v2 and v3 (rb/s03_desk_e190_v2.sh, s03_desk_e190_v3.sh) for E206:
#   - the window first (e206_window: today, E206, this arm), or refused (10) before any call; the pull under the lab-git lock (e206_pull;
#     never run inside it);
#   - HEAD descends from E206's registration (found by its content: the commit that added E206.md, its tools/claims-v3/e206 subtree
#     114c094b...) AND from the kit commit (found by its content: the commit that added KIT.md);
#   - E206's paths clean; the history check (rb/check_history_e206.py): additions only under tools/claims-v3/e206 since the registration, no
#     shadowing addition, nothing modified or untracked on E206's run paths;
#   - EVERY LIST E206 READS at its pinned count AND its own pinned sha256 AND every entry OK: the registration's (SHA256SUMS-e206-registration,
#     25) and the kit's (SHA256SUMS-e206-kit, KITPIN below, set at the kit's commit); any other file with SHA256SUMS in its name under
#     tools/claims-v3/e206 is REPORTED, never a gate;
#   - harness-e206.json re-made (CHECK PASS) and every file of it at its sha256 in the lab clone (HARNESS OK); the two modules' self-checks;
#     the registration's own checks (points, forecast, plan and kernel --check: PASS; the frozen scorer's two self-tests: PASS); the preflight
#     (dmcmd_audit_v2 GO, no WRITE); the kit's desk tests' logs as committed, each with its PASS line once, and both dry listings' last lines;
#   - HEAD unchanged across all of it, else 16;
#   - NO E206 DATUM OF THIS ARM in any ref (docs/reports/data/*e206*-<arm's box>*): 16 if one exists (the arm has run); the other arm's data
#     REPORTED (the two arms run on two boxes, maybe on two days); a sealed-forecast note (tools/claims-v3/sealed-e206/) REPORTED.
#   RB_GITLOCK=<the lab-git lock> bash tools/claims-v3/e206/rb/s03_desk_e206.sh <A|B>
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e206.sh"
rb_init s03_desk
e206_arm "${1:-}"
e206_window
E=tools/claims-v3/e206
REGPIN=tools/claims-v3/e206/SHA256SUMS-e206-registration:25:d9fb06e4a96e58e146eb2ea4cd8400cc5bce97fd97f9e769b8e61e000f9e46fc:top
KITPIN=tools/claims-v3/e206/SHA256SUMS-e206-kit:44:676ef81aab20547a52e66a0eea4543226900db1e6cdb2c7a7603e4a2e2861517:top   # the kit's own list, at its count and its own bytes (set at the kit's commit)
bad=""
e206_pull || bad="$bad pull"
[ -z "${RB_DRY:-}" ] && [ "${RB_RC:-0}" -ne 0 ] && bad="$bad pull(rc $RB_RC; a nested lab-git lock exits 75)"
rb_local read local "HEAD before the checks" git -C "$RB_REPO" rev-parse HEAD
h0=$(rb_val '^([0-9a-f]{40})$')
rb_local read local "E206's registration, by its content (the commit that added E206.md)" git -C "$RB_REPO" log --diff-filter=A --format=%H -- $E/E206.md
reg=$(rb_val '^([0-9a-f]{40})$')
rb_local read local "E206's kit commit, by its content (the commit that added KIT.md)" git -C "$RB_REPO" log --diff-filter=A --format=%H -- $E/KIT.md
kit=$(rb_val '^([0-9a-f]{40})$')
if [ -z "${RB_DRY:-}" ]; then
  if [ -z "$reg" ]; then bad="$bad registration(missing)"; else
    rb_local read local "the registration's e206 subtree" git -C "$RB_REPO" rev-parse "$reg:$E"
    rb_has "^$E206_REG_SUBTREE\$" || bad="$bad registration-subtree"
    rb_local read local "the registration is an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$reg" HEAD || bad="$bad registration-ancestry"
  fi
  if [ -z "$kit" ]; then bad="$bad kit(missing)"; else
    rb_local read local "the kit commit is an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$kit" HEAD || bad="$bad kit-ancestry"
  fi
fi
rb_local read local "E206's paths clean" git -C "$RB_REPO" status --short $E tools/claims-v3/e136/rgm136 tools/claims-v3/kinds/tiles \
  tools/claims-v3/kinds/real2/tiles tools/claims-v3/kinds/kinds.json tools/claims-v3/kinds/real2/real2.json tools/claims-v3/q141k-runbook \
  tools/claims-v3/e172/box tools/claims-v3/e190 tools/ledger tools/claims-v3/dmcmd_audit_v2.py tools/claims-v3/dmcmd_table_v2.json
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
rb_local read local "the history check: additions only under $E since the registration, no shadowing addition (check_history_e206.py)" \
  /usr/bin/python3 -I -B $E/rb/check_history_e206.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || bad="$bad history"
paths=""; for spec in $REGPIN $KITPIN; do paths="$paths ${spec%%:*}"; done
rb_local read local "the own sha256 of the lists E206 reads (pinned)" sha256sum $paths
own=$RB_CAP
for spec in $REGPIN $KITPIN; do
  IFS=: read -r l pin hpin form <<EOF2
$spec
EOF2
  RB_CWD="$RB_REPO" rb_local read local "the list $(basename "$l") (pinned at $pin entries and its own sha256)" sha256sum -c "$l"
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
rb_local desk local "harness-e206.json re-made" /usr/bin/python3 -I -B $E/check_e206.py --check
rb_has '^CHECK PASS' || bad="$bad harness-rebuild"
rb_local desk local "every harness file at its sha256 in the lab clone" /usr/bin/python3 -I -B $E/check_e206.py --box
rb_has '^HARNESS OK: ' || bad="$bad harness"
rb_local read local "the common module's self-check (the arms, the order, the stops and the latch reading, the gates, the argv, the records)" /usr/bin/python3 -I -B $E/e206_common.py
rb_has '^E206-COMMON SELF-CHECK PASS' || bad="$bad common"
rb_local read local "the identity module's self-check" /usr/bin/python3 -I -B $E/e206_ident.py
rb_has '^E206-IDENT SELF-CHECK PASS' || bad="$bad ident"
for s in points_e206.py forecast_e206.py plan_e206.py desk/kernel_e206.py; do
  rb_local desk local "the registration's $s --check" /usr/bin/python3 -I -B $E/$s --check
  rb_has '^PASS' || bad="$bad $(basename "$s" .py)"
done
rb_local desk local "the frozen scorer's stand-in self-test" /usr/bin/python3 -I -B $E/score_e206.py --selftest-standins "$RB_OUT/selftest-standins-e206-$ARM.json"
rb_has '^PASS$' || bad="$bad selftest-standins"
rb_local desk local "the frozen scorer's E190 self-test" /usr/bin/python3 -I -B $E/score_e206.py --selftest-e190 "$RB_OUT/selftest-e190-e206-$ARM.json"
rb_has '^PASS$' || bad="$bad selftest-e190"
rb_local desk local "the preflight: dmcmd_audit_v2 on the session's files, no WRITE allowed" bash $E/preflight_e206.sh
rb_has '^dmcmd_audit: GO' || bad="$bad preflight"
for spec in "logs/selftest-run-e206.txt ^SELFTEST-RUN-E206.[0-9]+.of.[0-9]+.PASS$" "logs/realpath-e206.txt ^REALPATH-E206.[0-9]+.of.[0-9]+.PASS$" \
            "logs/realbytes-e206.txt ^REALBYTES-E206.[0-9]+.of.[0-9]+.PASS$" "logs/desktest-build-e206.txt ^DESKTEST-BUILD-E206.[0-9]+.of.[0-9]+.PASS$" \
            "logs/selftest-rb-e206.txt ^SELFTEST-RB-E206.[0-9]+.of.[0-9]+.PASS$" \
            "logs/dry-listing-e206-A.txt ^dry.listing:.[0-9]+.steps.listed,.0.exited.non-zero,.0.box.calls$" \
            "logs/dry-listing-e206-B.txt ^dry.listing:.[0-9]+.steps.listed,.0.exited.non-zero,.0.box.calls$" "logs/dmcmd-audit-e206.txt ^dmcmd_audit:.GO"; do
  set -- $spec
  rb_local read local "a desk test's log, as committed: $1" grep -cE "$2" "$E/$1"
  rb_has '^1$' || bad="$bad $(basename "$1" .txt)"
done
rb_local read local "HEAD after the checks" git -C "$RB_REPO" rev-parse HEAD
h1=$(rb_val '^([0-9a-f]{40})$')
[ -n "${RB_DRY:-}" ] || [ "$h0" = "$h1" ] || bad="$bad HEAD-moved"
rb_local read local "E206 data of arm $ARM ($DATA_SUFFIX) in any ref (want none before its session)" git -C "$RB_REPO" log --all --oneline -- "docs/reports/data/*e206*-$DATA_SUFFIX*"
nd=0; [ -z "${RB_DRY:-}" ] && nd=$(grep -c . "$RB_CAP")
[ "$nd" -eq 0 ] || bad="$bad arm-$ARM-has-data($nd commit(s))"
rb_local read local "the other arm's E206 data and the gate-stop records in any ref (REPORTED)" git -C "$RB_REPO" log --all --oneline -- 'docs/reports/data/*e206*' 'docs/reports/gate-stops/*e206*'
no=0; [ -z "${RB_DRY:-}" ] && no=$(grep -c . "$RB_CAP")
rb_local read local "a sealed-forecast note for E206 (REPORTED; E206.md 0)" git -C "$RB_REPO" log --oneline -- tools/claims-v3/sealed-e206
ns=0; [ -z "${RB_DRY:-}" ] && ns=$(grep -c . "$RB_CAP")
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
echo "$(date '+%F %T %Z') step=$RB_STEP arm=$ARM lists not pinned (reported):${unknown:- none}; E206 data and gate-stop commits (any arm): $no; sealed-forecast note commits: $ns" >> "$RB_LOG"
rb_say "desk check (arm $ARM): the window written today for E206 arm $ARM; pulled under the lab-git lock, HEAD ${h1:0:12} descends from the registration ${reg:0:12} (subtree ${E206_REG_SUBTREE:0:8}) and the kit ${kit:0:12}, the paths clean, HISTORY OK, the lists at their pinned counts and bytes (25; the kit's $(echo "$KITPIN" | cut -d: -f2)), lists not pinned (reported):${unknown:- none}; the harness re-made and at its sha256, both self-checks, the registration's checks and the scorer's self-tests, the preflight GO, the desk tests' logs; arm $ARM data commits: $nd; any E206 data or gate-stop commits (reported): $no; sealed-forecast note commits (reported): $ns"
