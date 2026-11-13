#!/usr/bin/env bash
# E190 (Q169, the kit's dated note 1, lane fix-e190, Fri 13 Nov 2026, before any E190 datum), the box step "step 2" v2 (this file is
# s03 v2): the desk check before any box step, on the desk only (aifoundry2). Step 2 (rb/s03_desk_e190.sh, the kit, unchanged beside it)
# with note 1's files in place of the kit's where note 1 replaces them:
#   - the window first (e190_window), or refused (10) before any call; the pull under the lab-git lock (e190_pull; never run inside it);
#   - HEAD descends from E190's registration 508d48d9 (its tools/claims-v3/e190 subtree 4d4f7440...), from the kit commit (found by its
#     content: the commit that added KIT.md) AND from the note commit (found by its content: the commit that added KIT.md.dated-note-1.md);
#   - E190's paths clean; the history check (rb/check_history_e190.py, unchanged): additions only under tools/claims-v3/e190 since the
#     registration, no shadowing addition, nothing modified or untracked on E190's run paths;
#   - EVERY LIST E190 READS at its pinned count AND its own pinned sha256 AND every entry OK: the registration's (16), the kit's (56) and
#     NOTE 1'S (SHA256SUMS-e190-kit-note1, its count and bytes in NOTEPIN below; this step is outside it); any other file with SHA256SUMS
#     in its name under tools/claims-v3/e190 is REPORTED, never a gate;
#   - harness-e190-v2.json re-made (CHECK PASS) and every file of it at its sha256 in the lab clone (HARNESS OK); the common module's and
#     note 1's module's self-checks; the registration's forecast and plan re-made (--check) and the frozen scorer's stub self-test (PASS);
#     the preflight v2 (dmcmd_audit GO, no WRITE); note 1's desk tests' logs as committed, each with its PASS line once;
#   - HEAD unchanged across all of it, else 16; E190 data in any ref reported (want none before the session).
#   RB_GITLOCK=<the lab-git lock> bash tools/claims-v3/e190/rb/s03_desk_e190_v2.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e190_v2.sh"
rb_init s03_desk_v2
e190_window
E=tools/claims-v3/e190
PINS="tools/claims-v3/e190/SHA256SUMS-e190-registration:16:bfe58c588c011ae8c4aea8e39ea54f9941555147ad4aa1aff780d6ae1707509e:top tools/claims-v3/e190/SHA256SUMS-e190-kit:56:d176b11374dc081b7785373efe06af114fcaf7ed4a1456bc32df3b43be0f6567:top"
NOTEPIN=tools/claims-v3/e190/SHA256SUMS-e190-kit-note1:38:0b3c328b1c3c9df7fa7e62b4c5566daafb3b922d65218ac66ad6a0566d090b61:top   # note 1's own list, at its count and its own bytes (set at the note's commit)
bad=""
e190_pull || bad="$bad pull"
[ -z "${RB_DRY:-}" ] && [ "${RB_RC:-0}" -ne 0 ] && bad="$bad pull(rc $RB_RC; a nested lab-git lock exits 75)"
rb_local read local "HEAD before the checks" git -C "$RB_REPO" rev-parse HEAD
h0=$(rb_val '^([0-9a-f]{40})$')
rb_local read local "HEAD descends from E190's registration ${RB_E190_REG:0:12}" git -C "$RB_REPO" merge-base --is-ancestor "$RB_E190_REG" HEAD || bad="$bad registration-ancestry"
rb_local read local "the registration's e190 subtree" git -C "$RB_REPO" rev-parse "$RB_E190_REG:$E"
[ -n "${RB_DRY:-}" ] || rb_has "^$E190_REG_SUBTREE\$" || bad="$bad registration-subtree"
rb_local read local "E190's kit commit, by its content (the commit that added KIT.md)" git -C "$RB_REPO" log --diff-filter=A --format=%H -- $E/KIT.md
kit=$(rb_val '^([0-9a-f]{40})$')
rb_local read local "note 1's commit, by its content (the commit that added KIT.md.dated-note-1.md)" git -C "$RB_REPO" log --diff-filter=A --format=%H -- $E/KIT.md.dated-note-1.md
note=$(rb_val '^([0-9a-f]{40})$')
if [ -z "${RB_DRY:-}" ]; then
  if [ -z "$kit" ]; then bad="$bad kit(missing)"; else
    rb_local read local "the kit commit is an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$kit" HEAD || bad="$bad kit-ancestry"
  fi
  if [ -z "$note" ]; then bad="$bad note1(missing)"; else
    rb_local read local "note 1's commit is an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$note" HEAD || bad="$bad note1-ancestry"
  fi
fi
rb_local read local "E190's paths clean" git -C "$RB_REPO" status --short $E tools/claims-v3/e136/rgm136 tools/claims-v3/kinds/tiles \
  tools/claims-v3/q141k-runbook tools/claims-v3/dmcmd_audit.py tools/claims-v3/dmcmd_table.json
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
rb_local read local "the history check: additions only under $E since the registration, no shadowing addition (check_history_e190.py)" \
  /usr/bin/python3 -I -B $E/rb/check_history_e190.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || bad="$bad history"
paths=""; for spec in $PINS $NOTEPIN; do paths="$paths ${spec%%:*}"; done
rb_local read local "the own sha256 of the lists E190 reads (pinned)" sha256sum $paths
own=$RB_CAP
for spec in $PINS $NOTEPIN; do
  IFS=: read -r l pin hpin form <<EOF2
$spec
EOF2
  if [ "$form" = beside ]; then RB_CWD="$RB_REPO/$(dirname "$l")"; arg=$(basename "$l"); else RB_CWD="$RB_REPO"; arg=$l; fi
  RB_CWD=$RB_CWD rb_local read local "the list $(basename "$l") (pinned at $pin entries and its own sha256)" sha256sum -c "$arg"
  if [ -z "${RB_DRY:-}" ]; then
    n=$(grep -c ': OK$' "$RB_CAP"); m=$(grep -c . "$RB_REPO/$l" 2>/dev/null); m=${m:-0}
    h=$(awk -v p="$l" '$2 == p {print $1}' "$own")
    why=""; [ "$h" = "$hpin" ] || why="; its own bytes differ from the pin"
    { [ "$RB_RC" -eq 0 ] && [ "$n" -eq "$m" ] && [ "$n" = "$pin" ] && [ -z "$why" ]; } || bad="$bad $(basename "$l")($n OK of $m; pinned $pin$why)"
  fi
done
unset RB_CWD
rb_local read local "every file with SHA256SUMS anywhere in its name under $E" find "$E" -name '*SHA256SUMS*' -type f
unknown=""
if [ -z "${RB_DRY:-}" ]; then
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    case " $paths " in *" $f "*) ;; *) unknown="$unknown $f" ;; esac
  done < "$RB_CAP"
fi
for f in $unknown; do
  rb_local read local "a list step 2 v2 does not pin: $(basename "$f") (REPORTED, never a gate)" sha256sum -c "$f"
done
rb_local desk local "harness-e190-v2.json re-made" /usr/bin/python3 -I -B $E/check_e190_v2.py --check
rb_has '^CHECK PASS' || bad="$bad harness-v2-rebuild"
rb_local desk local "every harness v2 file at its sha256 in the lab clone" /usr/bin/python3 -I -B $E/check_e190_v2.py --box
rb_has '^HARNESS OK: ' || bad="$bad harness-v2"
rb_local read local "the common module's self-check (the order, the stops, the gates, the argv)" /usr/bin/python3 -I -B $E/e190_common.py
rb_has '^E190-COMMON SELF-CHECK PASS' || bad="$bad common"
rb_local read local "note 1's module's self-check (the identity reads, the board's rise, the sampler's freshness)" /usr/bin/python3 -I -B $E/e190_note1.py
rb_has '^E190-NOTE1 SELF-CHECK PASS' || bad="$bad note1-module"
rb_local desk local "the registration's forecast re-made" /usr/bin/python3 -I -B $E/forecast_e190.py --check
rb_has '^PASS$' || bad="$bad forecast"
rb_local read local "the registration's plan re-made" /usr/bin/python3 -I -B $E/plan_e190.py --check
rb_has '^PASS$' || bad="$bad plan"
rb_local desk local "the frozen scorer's stub self-test" /usr/bin/python3 -I -B $E/score_e190.py --selftest-stub "$RB_OUT/selftest-stub-e190.json"
rb_has '^PASS$' || bad="$bad selftest-stub"
rb_local desk local "the preflight v2: dmcmd_audit on the session's files, no WRITE allowed" bash $E/preflight_e190_v2.sh
rb_has '^dmcmd_audit: GO' || bad="$bad preflight-v2"
for spec in "logs/selftest-run-e190-v2.txt ^SELFTEST-RUN-E190-V2.[0-9]+.of.[0-9]+.PASS$" "logs/realpath-e190-v2.txt ^REALPATH-E190-V2.[0-9]+.of.[0-9]+.PASS$" \
            "logs/desktest-build-e190-v2.txt ^DESKTEST-BUILD-E190-V2.[0-9]+.of.[0-9]+.PASS$" "logs/selftest-rb-e190-v2.txt ^SELFTEST-RB-E190-V2.[0-9]+.of.[0-9]+.PASS$" \
            "logs/dry-listing-e190-v2.txt ^dry.listing:.[0-9]+.steps.listed,.0.exited.non-zero,.0.box.calls$" "logs/dmcmd-audit-e190-v2.txt ^dmcmd_audit:.GO"; do
  set -- $spec
  rb_local read local "a desk test's log, as committed: $1" grep -cE "$2" "$E/$1"
  rb_has '^1$' || bad="$bad $(basename "$1" .txt)"
done
rb_local read local "HEAD after the checks" git -C "$RB_REPO" rev-parse HEAD
h1=$(rb_val '^([0-9a-f]{40})$')
[ -n "${RB_DRY:-}" ] || [ "$h0" = "$h1" ] || bad="$bad HEAD-moved"
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
rb_local read local "E190 data in any ref (want none before the session)" git -C "$RB_REPO" log --all --oneline -- 'docs/reports/data/*e190*'
nd=0; [ -z "${RB_DRY:-}" ] && nd=$(grep -c . "$RB_CAP")
echo "$(date '+%F %T %Z') step=$RB_STEP lists not pinned (reported):${unknown:- none}" >> "$RB_LOG"
rb_say "desk check v2: the window written today for E190; pulled under the lab-git lock, HEAD ${h1:0:12} descends from the registration ${RB_E190_REG:0:12} (subtree ${E190_REG_SUBTREE:0:8}), the kit ${kit:0:12} and note 1 ${note:0:12}, the paths clean, HISTORY OK, the lists at their pinned counts and bytes (16; the kit's 56; note 1's $(echo "$NOTEPIN" | cut -d: -f2)), lists not pinned (reported):${unknown:- none}; the harness v2 re-made and at its sha256, the common and note 1 self-checks, the forecast and plan re-made, the stub self-test, the preflight v2 GO, note 1's desk tests' logs; commits naming E190 data: $nd"
