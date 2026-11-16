#!/usr/bin/env bash
# E198, box step 2, THE DESK CHECK (Q191, lane kit-e198, Sun 15 Nov 2026, before any E198 datum). E193's step 2 (rb/s03_desk_e193.sh,
# unchanged beside it) for E198. OUTSIDE the kit's list (it pins the list's own sha256 and count, so it cannot be in it). In order:
#   the window (written today for E198 and the sitting); the pull under the lab-git lock (never nested: 16); HEAD and its descent from
#   f74c81e3, E198's registration (by its content; its e198 subtree 5434394b...) and the kit (by its content); E198's paths clean; the history
#   check (rb/check_history_e198.py: additions only); the pinned lists at their counts and their own bytes, every entry OK: E198's
#   registration (14), E198's kit (KITPIN), E193's registration (29) and kit (43) which E198 runs by reference; lists not pinned reported;
#   harness-e198.json re-made and at its sha256; the preflight GO; the kit's desk-test logs; HEAD unchanged; NO E198 DATUM in any ref
#   (before sitting A: no docs/reports/data/*e198* path; before sitting B: sitting A's own data directory only).
# THE SEALED CARD-1 NOTE (CONTEXT 122): a later dated note at tools/claims-v3/sealed-card1/e198-freeze-lines.md, outside E198's pinned
# subtree, is ACCEPTED: it is no datum, the history check allows its addition, and it is reported here with its sha256 and commit.
#   RB_OUT=<dir> RB_LOCK=<file> RB_GITLOCK=<lab-git lock> bash tools/claims-v3/e198/rb/s03_desk_e198.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e198.sh"
rb_init s03_desk
e198_window
E=tools/claims-v3/e198
PINS="$E/SHA256SUMS-e198-registration:14:f66bae0f9c84cdc09ed8e25fb3b193ae4bb0c43ae312284f20a9abad98a84c7c:top tools/claims-v3/e193/SHA256SUMS-e193-registration:29:6258cde38b9cff67c5c6c834e8f18c91f4f259ba64c402c5eaec75d61921e935:top tools/claims-v3/e193/SHA256SUMS-e193-kit:43:5c209cff3cedc4ace8b2c3371a9a67690ff00cd9962adfbfa1d642ce0b985aab:top"
KITPIN=tools/claims-v3/e198/SHA256SUMS-e198-kit:46:38de3b38bd84cc36075674cc8cb7358bf2332b4456ec247683ba998a85f85a57:top   # the kit's own list, at its count and its own bytes (filled when the kit was committed)
bad=""
e198_pull || bad="$bad pull"
[ -z "${RB_DRY:-}" ] && [ "${RB_RC:-0}" -ne 0 ] && bad="$bad pull(rc $RB_RC; a nested lab-git lock exits 75)"
rb_local read local "HEAD before the checks" git -C "$RB_REPO" rev-parse HEAD
h0=$(rb_val '^([0-9a-f]{40})$')
rb_local read local "HEAD descends from $RB_E198_BASE (GitHub main when E198 was registered)" git -C "$RB_REPO" merge-base --is-ancestor "$RB_E198_BASE" HEAD || bad="$bad ancestry"
reg=""; kit=""
for what in registration kit; do
  f=$E/E198.md; [ "$what" = kit ] && f=$E/KIT.md
  rb_local read local "E198's $what commit, by its content (the commit that added $(basename "$f"))" git -C "$RB_REPO" log --diff-filter=A --format=%H -- "$f"
  c=$(rb_val '^([0-9a-f]{40})$')
  [ -n "${RB_DRY:-}" ] && continue
  if [ -z "$c" ]; then bad="$bad $what(missing)"; continue; fi
  rb_local read local "the $what commit is an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$c" HEAD || bad="$bad $what-ancestry"
  if [ "$what" = registration ]; then
    reg=$c
    rb_local read local "the registration's e198 subtree" git -C "$RB_REPO" rev-parse "$c:$E"
    rb_has "^$E198_REG_SUBTREE\$" || bad="$bad registration-subtree"
  else
    kit=$c
  fi
done
rb_local read local "E198's paths clean" git -C "$RB_REPO" status --short $E tools/claims-v3/e193 tools/claims-v3/e191/ettelem_guard_e191.sh \
  tools/claims-v3/e191/e191_ident.py tools/claims-v3/e191/etdevices_e191.sh tools/claims-v3/e191/rb/rest_rule_e191.sh tools/claims-v3/dmcmd_audit.py \
  tools/claims-v3/dmcmd_table.json tools/claims-v3/q141k-runbook/k6 tools/claims-v3/q141k-runbook/v3.1 tools/claims-v3/e183/rb tools/claims-v3/sealed-card1
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
rb_local read local "the history check: additions only on E198's paths since $RB_E198_BASE and since the registration and the kit (check_history_e198.py)" \
  /usr/bin/python3 -I -B $E/rb/check_history_e198.py tree --base "$RB_E198_BASE"
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || bad="$bad history"
paths=""; for spec in $PINS $KITPIN; do paths="$paths ${spec%%:*}"; done
rb_local read local "the own sha256 of the lists E198 reads (pinned)" sha256sum $paths
own=$RB_CAP
for spec in $PINS $KITPIN; do
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
  RB_CWD="$RB_REPO" rb_local read local "a list step 2 does not pin: $(basename "$f") (REPORTED, never a gate)" sha256sum -c "$f"
done
unset RB_CWD
rb_local read local "the sealed card-1 note, if any ($E198_SEALED: accepted, outside the pinned subtree; CONTEXT 122)" \
  git -C "$RB_REPO" log --format='%h %cI' -- "$E198_SEALED"
sealed=none
if [ -z "${RB_DRY:-}" ] && [ -f "$RB_REPO/$E198_SEALED" ]; then
  sealed="$(sha256sum "$RB_REPO/$E198_SEALED" | cut -c1-16)... committed $(head -n 1 "$RB_CAP" | cut -c1-40)"
fi
rb_local desk local "harness-e198.json re-made" /usr/bin/python3 -I -B $E/harness_e198.py --check
rb_has '^CHECK PASS' || bad="$bad harness-rebuild"
rb_local desk local "every harness file at its sha256 in the lab clone" /usr/bin/python3 -I -B $E/harness_e198.py --box
rb_has '^HARNESS OK: ' || bad="$bad harness"
rb_local desk local "the preflight: dmcmd_audit on the session's files, no WRITE allowed" bash $E/preflight_e198.sh
rb_has '^dmcmd_audit: GO' || bad="$bad preflight"
for spec in "logs/desktest-realpath-e198.txt ^DESKTEST-REALPATH-E198.[0-9]+.of.[0-9]+.PASS" "logs/realbytes-e198.txt ^REALBYTES-E198.[0-9]+.of.[0-9]+.PASS" \
            "logs/selftest-rb-e198.txt ^SELFTEST-RB-E198.[0-9]+.of.[0-9]+.PASS" "logs/ident-selfcheck-e198.txt ^E198-IDENT.SELF-CHECK.PASS" \
            "logs/dry-listing-e198.txt ^dry.listing:.[0-9]+.steps.listed,.0.exited.non-zero,.0.box.calls$" "logs/dmcmd-audit-e198.txt ^dmcmd_audit:.GO"; do
  set -- $spec
  rb_local read local "a desk test's log, as committed: $1" grep -cE "$2" "$E/$1"
  rb_has '^1$' || bad="$bad $(basename "$1" .txt)"
done
rb_local read local "HEAD after the checks" git -C "$RB_REPO" rev-parse HEAD
h1=$(rb_val '^([0-9a-f]{40})$')
[ -n "${RB_DRY:-}" ] || [ "$h0" = "$h1" ] || bad="$bad HEAD-moved"
rb_local read local "E198 data in any ref (before sitting A: none; before sitting B: sitting A's own directory only)" \
  git -C "$RB_REPO" log --all --name-only --format= -- 'docs/reports/data/*e198*'
nd=0; other=0
if [ -z "${RB_DRY:-}" ]; then
  nd=$(sort -u "$RB_CAP" | grep -c .)
  other=$(sort -u "$RB_CAP" | grep . | grep -vc -- '-e198-x04-clock-sitting-a-aifoundry1-c1/')
  if [ "$E198_SIT" = A ] && [ "$nd" -gt 0 ]; then bad="$bad e198-datum($nd paths before sitting A)"; fi
  if [ "$E198_SIT" = B ] && [ "$other" -gt 0 ]; then bad="$bad e198-datum($other paths besides sitting A's before sitting B)"; fi
fi
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
echo "$(date '+%F %T %Z') step=$RB_STEP sitting=$E198_SIT lists not pinned (reported):${unknown:- none}; the sealed card-1 note: $sealed" >> "$RB_LOG"
rb_say "desk check for sitting $E198_SIT: the window written today for E198; pulled under the lab-git lock, HEAD ${h1:0:12} descends from $RB_E198_BASE, the registration ${reg:0:12} (subtree ${E198_REG_SUBTREE:0:8}) and the kit ${kit:0:12}; the paths clean, HISTORY OK, the lists at their pinned counts and bytes, lists not pinned (reported):${unknown:- none}; the sealed card-1 note: $sealed; the harness re-made and at its sha256, the preflight GO, the kit's desk tests' logs; E198 data paths in any ref: $nd (sitting A's: $((nd - other)))"
