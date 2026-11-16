#!/usr/bin/env bash
# E197 (Q185, the kit), the box step "step 2" (this file is s03), each sitting's desk check before any box step, on the desk only
# (aifoundry2, Linux, or the Intel), in E193's step 2 form (tools/claims-v3/e193/rb/s03_desk_e193.sh):
#   - the window first: RB_OUT's window written today (Pacific) for E197 and a sitting (e197_window), or refused (10) before any call;
#   - the pull under the lab-git lock (e197_pull: RB_GITLOCK required; this step takes the lock itself for the pull alone, so it is NEVER
#     run inside that lock: a nested lockf or flock exits 75 and this step stops with 16);
#   - HEAD descends from e8a85229 (GitHub main when E197 was registered), from E197's registration commit, found by its content (the
#     commit that added tools/claims-v3/e197/E197.md, whose e197 subtree reads da6c3e89...), and from the kit's (the one that added
#     tools/claims-v3/e197/KIT.md);
#   - E197's paths clean; the history check (rb/check_history_e197.py tree): additions only since e8a85229 on E197's paths, nothing under
#     tools/claims-v3/e197 changed since the registration or the kit, nothing untracked, no shadowing addition and no shadowing file not
#     committed in the folders the day's Python puts ahead of the standard library;
#   - BOTH LISTS E197 READS at their pinned counts AND their own pinned sha256 AND every entry OK, with no override: the registration's
#     (SHA256SUMS-e197-registration, 35) and THE KIT'S OWN (SHA256SUMS-e197-kit; this step is outside it: a file cannot hold the sha256
#     of a list that holds its own; the land file's anchor lines give this step's sha256 beside the list's); every file with "SHA256SUMS"
#     ANYWHERE in its name under tools/claims-v3/e197 found: one this step does not pin is REPORTED, never a gate (a dated amendment's
#     own list, say);
#   - harness-e197.json re-made (CHECK PASS) and every file of it at its sha256 in the lab clone (HARNESS OK); the preflight (dmcmd_audit
#     GO, no WRITE); the kit's desk tests' logs as committed, each with its PASS line once;
#   - HEAD unchanged across all of it, else 16;
#   - NO E197 DATUM IN ANY REF: before sitting 1, no docs/reports/data/*e197* path in any ref; before sitting 2, none but sitting 1's own
#     data directory (*-e197-regfile-sitting-1-aifoundry3/); else 16. A gate stop's record (docs/reports/gate-stops/<day>-e197-regfile-
#     sitting-<n>-T<T0>-aifoundry3/: E197.md 11's "no sitting: no data") is no datum and is not read here.
# The load is read by the card lane before this step (`uptime` on aifoundry2); this step does not read it.
#
#   RB_GITLOCK=<the lab-git lock> bash tools/claims-v3/e197/rb/s03_desk_e197.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e197.sh"
rb_init s03_desk
e197_window
E=tools/claims-v3/e197
PINS="tools/claims-v3/e197/SHA256SUMS-e197-registration:35:992a35e577617489d571f1af6e37f78b08e967d82e6529261ebf7db19e05ad95:top"   # list:count:its own sha256:paths from
KITPIN=${RB_E197_KITPIN:-tools/claims-v3/e197/SHA256SUMS-e197-kit:39:0719a97ffa91d4e440ba507b3642cf0b1b6fea1dcf156d3a1a471dfdd2d16963:top}   # the kit's own list, at its count and its own bytes
[ "${RB_DESKTEST:-}" = 1 ] || KITPIN=tools/claims-v3/e197/SHA256SUMS-e197-kit:39:0719a97ffa91d4e440ba507b3642cf0b1b6fea1dcf156d3a1a471dfdd2d16963:top
bad=""
e197_pull || bad="$bad pull"
[ -z "${RB_DRY:-}" ] && [ "${RB_RC:-0}" -ne 0 ] && bad="$bad pull(rc $RB_RC; a nested lab-git lock exits 75)"
rb_local read local "HEAD before the checks" git -C "$RB_REPO" rev-parse HEAD
h0=$(rb_val '^([0-9a-f]{40})$')
rb_local read local "HEAD descends from $RB_E197_BASE (GitHub main when E197 was registered)" git -C "$RB_REPO" merge-base --is-ancestor "$RB_E197_BASE" HEAD || bad="$bad ancestry"
reg=""; kit=""
for what in registration kit; do
  f=$E/E197.md; [ "$what" = kit ] && f=$E/KIT.md
  rb_local read local "E197's $what commit, by its content (the commit that added $(basename "$f"))" git -C "$RB_REPO" log --diff-filter=A --format=%H -- "$f"
  c=$(rb_val '^([0-9a-f]{40})$')
  [ -n "${RB_DRY:-}" ] && continue
  if [ -z "$c" ]; then bad="$bad $what(missing)"; continue; fi
  rb_local read local "the $what commit is an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$c" HEAD || bad="$bad $what-ancestry"
  if [ "$what" = registration ]; then
    reg=$c
    rb_local read local "the registration's e197 subtree" git -C "$RB_REPO" rev-parse "$c:$E"
    rb_has "^$E197_REG_SUBTREE\$" || bad="$bad registration-subtree"
  else
    kit=$c
  fi
done
rb_local read local "E197's paths clean" git -C "$RB_REPO" status --short $E tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/dmcmd_audit.py \
  tools/claims-v3/dmcmd_table.json tools/claims-v3/q141k-runbook/k6 tools/claims-v3/q141k-runbook/v3.1 tools/claims-v3/e183/rb
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
rb_local read local "the history check: additions only on E197's paths since $RB_E197_BASE and since the registration and the kit (check_history_e197.py)" \
  /usr/bin/python3 -I -B $E/rb/check_history_e197.py tree --base "$RB_E197_BASE"
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || bad="$bad history"
paths=""; for spec in $PINS $KITPIN; do paths="$paths ${spec%%:*}"; done
rb_local read local "the own sha256 of the lists E197 reads (pinned)" shasum -a 256 $paths
own=$RB_CAP
for spec in $PINS $KITPIN; do
  IFS=: read -r l pin hpin form <<EOF2
$spec
EOF2
  RB_CWD="$RB_REPO" rb_local read local "the list $(basename "$l") (pinned at $pin entries and its own sha256)" shasum -a 256 -c "$l"
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
  RB_CWD="$RB_REPO" rb_local read local "a list step 2 does not pin: $(basename "$f") (REPORTED, never a gate)" shasum -a 256 -c "$f"
done
unset RB_CWD
rb_local desk local "harness-e197.json re-made" /usr/bin/python3 -I -B $E/harness_e197.py --check
rb_has '^CHECK PASS' || bad="$bad harness-rebuild"
rb_local desk local "every harness file at its sha256 in the lab clone" /usr/bin/python3 -I -B $E/harness_e197.py --box
rb_has '^HARNESS OK: ' || bad="$bad harness"
rb_local desk local "the preflight: dmcmd_audit on the session's files, no WRITE allowed" bash $E/preflight_e197.sh
rb_has '^dmcmd_audit: GO' || bad="$bad preflight"
for spec in "logs/desktest-realpath-e197.txt ^DESKTEST-REALPATH-E197.[0-9]+.of.[0-9]+.PASS" "logs/selftest-rb-e197.txt ^SELFTEST-RB-E197.[0-9]+.of.[0-9]+.PASS" \
            "logs/selftest-rest-e197.txt ^SELFTEST-REST-E197.[0-9]+.of.[0-9]+.PASS" "logs/realbytes-e197.txt ^REALBYTES-E197.[0-9]+.of.[0-9]+.PASS" \
            "logs/dry-listing-e197.txt ^dry.listing:.[0-9]+.steps.listed,.0.exited.non-zero,.0.box.calls$" "logs/dmcmd-audit-e197.txt ^dmcmd_audit:.GO"; do
  set -- $spec
  rb_local read local "a desk test's log, as committed: $1" grep -cE "$2" "$E/$1"
  rb_has '^1$' || bad="$bad $(basename "$1" .txt)"
done
rb_local read local "HEAD after the checks" git -C "$RB_REPO" rev-parse HEAD
h1=$(rb_val '^([0-9a-f]{40})$')
[ -n "${RB_DRY:-}" ] || [ "$h0" = "$h1" ] || bad="$bad HEAD-moved"
rb_local read local "E197 data in any ref (before sitting 1: none; before sitting 2: sitting 1's own directory only)" \
  git -C "$RB_REPO" log --all --name-only --format= -- 'docs/reports/data/*e197*'
nd=0; other=0
if [ -z "${RB_DRY:-}" ]; then
  nd=$(sort -u "$RB_CAP" | grep -c .)
  other=$(sort -u "$RB_CAP" | grep . | grep -vc -- '-e197-regfile-sitting-1-aifoundry3/')
  if [ "$E197_SIT" = 1 ] && [ "$nd" -gt 0 ]; then bad="$bad e197-datum($nd paths before sitting 1)"; fi
  if [ "$E197_SIT" = 2 ] && [ "$other" -gt 0 ]; then bad="$bad e197-datum($other paths besides sitting 1's before sitting 2)"; fi
fi
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
echo "$(date '+%F %T %Z') step=$RB_STEP sitting=$E197_SIT lists not pinned (reported):${unknown:- none}" >> "$RB_LOG"
rb_say "desk check for sitting $E197_SIT: the window written today for E197; pulled under the lab-git lock, HEAD ${h1:0:12} descends from $RB_E197_BASE, the registration ${reg:0:12} (subtree ${E197_REG_SUBTREE:0:8}) and the kit ${kit:0:12}; the paths clean, HISTORY OK, the lists at their pinned counts and bytes (35; the kit's $(echo "$KITPIN" | cut -d: -f2)), lists not pinned (reported):${unknown:- none}; the harness re-made and at its sha256, the preflight GO, the kit's desk tests' logs; E197 data paths in any ref: $nd (sitting 1's: $((nd - other)))"
