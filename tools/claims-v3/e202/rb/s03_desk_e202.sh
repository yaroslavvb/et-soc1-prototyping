#!/usr/bin/env bash
# E202 (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum), the box step "step 2" (this file is s03, OUTSIDE the kit's list: a
# list cannot hold the sha256 of a file that pins the list; the land file's anchor lines give this file's sha256 beside the list's): the
# desk check before any box step, on the desk only (aifoundry2, Linux), in E189's step 2 form (tools/claims-v3/e189/rb/s03_desk_e189.sh):
#   - the window first: RB_OUT's window written today (Pacific) for E202 (e202_window), or refused (10) before any call;
#   - the pull under the lab-git lock (e202_pull: RB_GITLOCK required; this step takes the lock itself for the pull alone, so it is NEVER
#     run inside that lock: a nested flock exits 75 and this step stops with 16);
#   - THE PROGRAM COMMIT and THE REGISTRATION COMMIT found by their content (the commit that added workloads/mnistmlp/kernel/mnistmlp.c,
#     its workloads/mnistmlp subtree fb102551...; the commit that added tools/claims-v3/e202/E202.md, its e202 subtree d95a19d9...), both
#     ancestors of HEAD;
#   - E202's paths clean; the history check (rb/check_history_e202.py tree): additions only since the program commit on E202's paths,
#     nothing under tools/claims-v3/e202 changed since the registration or the kit, workloads/mnistmlp unchanged, nothing untracked, no
#     shadowing addition or uncommitted shadowing file in the folders the day's Python puts ahead of the standard library;
#   - EVERY LIST E202 READS at its pinned count AND its own pinned sha256 AND every entry OK, with no override: E202's registration (12),
#     the program's records (75), the guards' list (Q188's, 23: dmcmd_audit_v2 and its table among them), k6's drivers (39), the ledger
#     v2's (17), and THE KIT'S OWN LIST (SHA256SUMS-e202-kit) at its count and its bytes; every other file with "SHA256SUMS" in its name
#     under tools/claims-v3/e202 is REPORTED, never a gate;
#   - harness-e202.json re-made (CHECK PASS) and every file of it at its sha256 in the lab clone (HARNESS OK); the common module's
#     self-check; the registration's forecast and plan re-made (--check); the scorer's self-test (PASS, its stub unchanged after); the
#     preflight (dmcmd_audit_v2 GO, no WRITE); the kit's desk tests' logs as committed, each with its PASS line once;
#   - NO E202 DATUM: no docs/reports/data/*e202* path in any ref (a gate stop's record lives under docs/reports/gate-stops/ and is not one);
#   - LEDGER V3 AND E202'S V3 NOTE (fix-e202, verify-e202's finding 3; E202.md 4.4): ledger v3 is in HEAD when tools/ledger/frozen-v3.json
#     is (it landed at 50795847, after the registration's freeze); then E202's v3 note must be in HEAD too, by its own names
#     (E202-ledger-v3-note.md, v3note_e202.py, v3note-e202.json, v3note-e202.txt, each in the kit's list, so its bytes are pinned) and
#     must re-make itself (v3note_e202.py --check: V3NOTE CHECK PASS), else 16: no E202 datum before the note;
#   - HEAD unchanged across all of it, else 16.
#   RB_GITLOCK=<the lab-git lock> bash tools/claims-v3/e202/rb/s03_desk_e202.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e202.sh"
rb_init s03_desk
e202_window
E=tools/claims-v3/e202
PINS="tools/claims-v3/e202/SHA256SUMS-e202-registration:12:3ff8830f002d0c772cceb875544b90aaeeb592ec57ab52c3f80bd229c88ac922:top
docs/reports/data/2026-11-16-q193-mnistmlp/SHA256SUMS:75:b1d06d236adb1ba386b429f5b89f510501981e787018ea6a3cbeb711a853b1df:beside
tools/claims-v3/SHA256SUMS-q188-guards:23:f78dcfd53065df83dcde2ea2c071015bd0b7e05da1347c47448ad27cd88510ad:top
tools/claims-v3/q141k-runbook/k6/SHA256SUMS-drivers-v3:39:673de2ca66e2bf6cef9bbf0fa99bffdd94d48d0fbe851ad30485697359a4b0cb:top
docs/reports/data/2026-11-12-q166-ledger-v2/SHA256SUMS:17:aa6f7f733508d0c4be89c0b3aedcbe34be1d7bf809876bd9a50b56eaeed10921:top"   # list:count:its own sha256:paths from
KITPIN=tools/claims-v3/e202/SHA256SUMS-e202-kit:50:4f1a0dfd326f087a3ba669e230a35c35ef8bbbfd7dcdc9eac426df888b1096b3:top   # the kit's own list, at its count and its own bytes
bad=""
e202_pull || bad="$bad pull"
[ -z "${RB_DRY:-}" ] && [ "${RB_RC:-0}" -ne 0 ] && bad="$bad pull(rc $RB_RC; a nested lab-git lock exits 75)"
rb_local read local "HEAD before the checks" git -C "$RB_REPO" rev-parse HEAD
h0=$(rb_val '^([0-9a-f]{40})$')
for spec in "program:workloads/mnistmlp/kernel/mnistmlp.c:workloads/mnistmlp:$E202_PROG_SUBTREE" "registration:$E/E202.md:$E:$E202_REG_SUBTREE"; do
  IFS=: read -r what added sub pin <<EOF2
$spec
EOF2
  rb_local read local "the $what commit, by its content (the commit that added $added)" git -C "$RB_REPO" log --diff-filter=A --format=%H -- "$added"
  c=$(rb_val '^([0-9a-f]{40})$' | tail -n 1)
  if [ -z "${RB_DRY:-}" ]; then
    c=$(grep -E '^[0-9a-f]{40}$' "$RB_CAP" | tail -n 1)
    if [ -z "$c" ]; then bad="$bad $what(missing)"; continue; fi
    rb_local read local "the $what commit is an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$c" HEAD || bad="$bad $what-ancestry"
    rb_local read local "the $what commit's $sub subtree" git -C "$RB_REPO" rev-parse "$c:$sub"
    rb_has "^$pin\$" || bad="$bad $what-subtree"
    [ "$what" = registration ] && reg=$c
  else
    rb_local read local "the $what commit is an ancestor of HEAD, and its $sub subtree reads $pin" git -C "$RB_REPO" rev-parse "<$what>:$sub"
  fi
done
rb_local read local "E202's paths clean" git -C "$RB_REPO" status --short $E workloads/mnistmlp docs/reports/data/2026-11-16-q193-mnistmlp \
  tools/ledger tools/counter tools/claims-v3/e128 tools/claims-v3/dmcmd_audit_v2.py tools/claims-v3/dmcmd_table_v2.json \
  tools/claims-v3/q141k-runbook/k6 workloads/sparseparity/tools
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
rb_local read local "the history check: additions only on E202's paths since the program commit and since the registration and the kit (check_history_e202.py)" \
  /usr/bin/python3 -I -B $E/rb/check_history_e202.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || bad="$bad history"
paths=""; for spec in $PINS $KITPIN; do paths="$paths ${spec%%:*}"; done
rb_local read local "the own sha256 of the lists E202 reads (pinned)" sha256sum $paths
own=$RB_CAP
for spec in $PINS $KITPIN; do
  IFS=: read -r l pin hpin form <<EOF2
$spec
EOF2
  if [ "$form" = beside ]; then RB_CWD="$RB_REPO/$(dirname "$l")"; arg=$(basename "$l"); else RB_CWD="$RB_REPO"; arg=$l; fi
  RB_CWD=$RB_CWD rb_local read local "the list $(basename "$l") (pinned at $pin entries and its own sha256)" sha256sum -c "$arg"
  if [ -z "${RB_DRY:-}" ]; then
    n=$(grep -c ': OK$' "$RB_CAP"); m=$(grep -c . "$RB_REPO/$l" 2>/dev/null); m=${m:-0}
    h=$(awk -v p="$l" '$2 == p {print $1}' "$own")
    why=""; [ "$h" = "$hpin" ] || why="; its own bytes differ from the pin"
    { [ "$RB_RC" -eq 0 ] && [ "$n" -eq "$m" ] && [ "$n" -eq "$pin" ] && [ -z "$why" ]; } || bad="$bad $(basename "$l")($n OK of $m; pinned $pin$why)"
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
  rb_local read local "a list step 2 does not pin: $(basename "$f") (REPORTED, never a gate)" sha256sum -c "$f"
done
rb_local desk local "harness-e202.json re-made" /usr/bin/python3 -I -B $E/check_e202.py --check
rb_has '^CHECK PASS' || bad="$bad harness-rebuild"
rb_local desk local "every harness file at its sha256 in the lab clone" /usr/bin/python3 -I -B $E/check_e202.py --box
rb_has '^HARNESS OK: ' || bad="$bad harness"
rb_local read local "the common module's self-check (the smoke, the order, the R rule, the adapter, the stop lines)" /usr/bin/python3 -I -B $E/e202_common.py
rb_has '^E202-COMMON SELF-CHECK PASS' || bad="$bad common"
rb_local desk local "the registration's forecast re-made" /usr/bin/python3 -I -B $E/forecast_e202.py --check
rb_has '"check": "PASS"' || bad="$bad forecast"
rb_local read local "the registration's plan re-made" /usr/bin/python3 -I -B $E/plan_e202.py --check
rb_has '"check": "PASS"' || bad="$bad plan"
mkdir -p "$RB_OUT/selftest-e202"
rb_local desk local "the scorer's stand-in self-test (its stub must come out unchanged)" /usr/bin/python3 -I -B $E/score_e202.py --selftest "$RB_OUT/selftest-e202"
rb_has '"selftest": "PASS"' || bad="$bad scorer-selftest"
rb_local read local "the scorer's stub unchanged after its self-test" git -C "$RB_REPO" status --short $E/selftest-stub-e202.json
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad scorer-stub-changed"
rb_local desk local "the preflight: dmcmd_audit_v2 on the session's files, no WRITE allowed" bash $E/preflight_e202.sh
rb_has '^dmcmd_audit: GO' || bad="$bad preflight"
for spec in "logs/desktest-build-e202.txt ^DESKTEST-BUILD-E202.[0-9]+.of.[0-9]+.PASS" "logs/selftest-run-e202.txt ^SELFTEST-RUN-E202.[0-9]+.of.[0-9]+.PASS" \
            "logs/desktest-realpath-e202.txt ^DESKTEST-REALPATH-E202.[0-9]+.of.[0-9]+.PASS" "logs/realbytes-e202.txt ^REALBYTES-E202.[0-9]+.of.[0-9]+.PASS" \
            "logs/selftest-rb-e202.txt ^SELFTEST-RB-E202.[0-9]+.of.[0-9]+.PASS" "logs/selftest-rest-e202.txt ^SELFTEST-REST-E202.[0-9]+.of.[0-9]+.PASS" \
            "logs/dry-listing-e202.txt ^dry.listing:.[0-9]+.steps.listed,.0.exited.non-zero,.0.box.calls$" "logs/dmcmd-audit-e202.txt ^dmcmd_audit:.GO" \
            "logs/checks-e202.txt ^CHECKS-E202.[0-9]+.of.[0-9]+.PASS"; do
  set -- $spec
  rb_local read local "a desk test's log, as committed: $1" grep -cE "$2" "$E/$1"
  rb_has '^1$' || bad="$bad $(basename "$1" .txt)"
done
rb_local read local "HEAD after the checks" git -C "$RB_REPO" rev-parse HEAD
h1=$(rb_val '^([0-9a-f]{40})$')
[ -n "${RB_DRY:-}" ] || [ "$h0" = "$h1" ] || bad="$bad HEAD-moved"
rb_local read local "E202 data in any ref (a gate: none before the session)" git -C "$RB_REPO" log --all --oneline -- 'docs/reports/data/*e202*'
nd=0; [ -z "${RB_DRY:-}" ] && nd=$(grep -c . "$RB_CAP")
[ "$nd" -eq 0 ] || bad="$bad e202-datum-exists($nd)"
rb_local read local "ledger v3 and E202's v3 note in HEAD (fix-e202: once v3 is in HEAD the note is required, E202.md 4.4)" \
  git -C "$RB_REPO" ls-files -- tools/ledger/frozen-v3.json "$E/E202-ledger-v3-note.md" "$E/v3note_e202.py" "$E/v3note-e202.json" "$E/v3note-e202.txt"
v3=no; v3n=no
if [ -z "${RB_DRY:-}" ]; then
  grep -qx 'tools/ledger/frozen-v3.json' "$RB_CAP" && v3=yes
  [ "$(grep -cxE "$E/(E202-ledger-v3-note[.]md|v3note_e202[.]py|v3note-e202[.]json|v3note-e202[.]txt)" "$RB_CAP")" -eq 4 ] && v3n=yes
fi
if [ "$v3" = yes ] || [ -n "${RB_DRY:-}" ]; then
  rb_local desk local "E202's ledger v3 note re-made (v3note_e202.py --check: ledger v3's forecast of the same load, REPORTED beside v2)" \
    /usr/bin/python3 -I -B $E/v3note_e202.py --check
  [ -n "${RB_DRY:-}" ] || { [ "$v3n" = yes ] && rb_has '^V3NOTE CHECK PASS'; } || bad="$bad ledger-v3-note(ledger v3 in HEAD; the note in HEAD: $v3n)"
fi
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
echo "$(date '+%F %T %Z') step=$RB_STEP lists not pinned (reported):${unknown:- none}; ledger v3 in HEAD: $v3; an E202 v3 note: $v3n" >> "$RB_LOG"
rb_say "desk check: the window written today for E202; pulled under the lab-git lock, HEAD ${h1:0:12} descends from the program and the registration ${reg:0:12} (subtrees ${E202_PROG_SUBTREE:0:8}, ${E202_REG_SUBTREE:0:8}), the paths clean, HISTORY OK, the lists at their pinned counts and bytes (12; 75; 23; 39; 17) and the kit's ($(echo "$KITPIN" | cut -d: -f2)), lists not pinned (reported):${unknown:- none}; the harness re-made and at its sha256, the common self-check, the forecast and plan re-made, the scorer's self-test, the preflight GO, the kit's desk tests' logs; E202 data in any ref: $nd; ledger v3 in HEAD $v3, E202's v3 note in HEAD $v3n$([ "$v3" = yes ] && echo ' (V3NOTE CHECK PASS)')"
