#!/usr/bin/env bash
# E189 (Q167, the kit; re-pinned and ported Fri 13 Nov 2026, fix-e189b), the box step "step 2" (this file is s03): the desk check before
# any box step, on the desk only (the Intel, macOS, or aifoundry2, Linux), in E188's step 2 form (tools/claims-v3/e188/rb/s03_desk_e188.sh
# and its v2) and E183's step 2 v5's list rule:
#   - the window first: RB_OUT's window written today (Pacific) for E189 (e189_window), or refused (10) before any call;
#   - the pull under the lab-git lock (e189_pull: RB_GITLOCK required; this step takes the lock itself for the pull alone, so it is NEVER
#     run inside that lock: a nested lockf or flock exits 75 and this step stops with 16, as E188's step 2 v2);
#   - HEAD descends from 46a16bd0 (Q166's programs) and from E189's registration commit, found by its content (the commit that added
#     tools/claims-v3/e189/E189.md, whose e189 subtree reads 993e549a..., the registration as re-made before any datum);
#   - E189's paths clean; the history check (rb/check_history_e189.py tree): additions only since 46a16bd0 on E189's paths, nothing under
#     tools/claims-v3/e189 changed since the registration or the kit, nothing untracked, no shadowing addition and no shadowing file not
#     committed in the eight folders the day's Python puts ahead of the standard library (fix-fix189: the lab clone's top among them);
#   - EVERY LIST E189 READS at its pinned count AND its own pinned sha256 AND every entry OK, with no override: E189's registration (10),
#     Q166's progs (165), the ledger v2's two (17 and the freeze's 6), the counter's sparse-parity folder (86), and THE KIT'S OWN LIST
#     (SHA256SUMS-e189-kit) at its count and its bytes (this step is outside it: a file cannot hold the sha256 of a list that holds its
#     own; E189's anchor lines give this step's sha256 beside the list's); and every file with "SHA256SUMS" ANYWHERE in its name under
#     tools/claims-v3/e189 found: one this step does not pin is REPORTED, never a gate (E183 v5's rule);
#   - harness-e189.json re-made (CHECK PASS) and every file of it at its sha256 in the lab clone (HARNESS OK); the host check's frozen lines
#     against their sources; the common module's self-check; the registration's plan and forecast re-made (--check) and the scorer's E59
#     self-test (PASS); the never-run check at this HEAD (NEVER RAN; Q166's progs folder left out, as registered); the preflight (dmcmd_audit
#     GO, no WRITE); the kit's desk tests' logs as committed, each with its PASS line once;
#   - HEAD unchanged across all of it, else 16; E189 data in any ref reported (want none before the session).
# load_guard's tier is read by the card lane before this step (calm or warm only); this step does not read it.
#
#   RB_GITLOCK=<the lab-git lock> bash tools/claims-v3/e189/rb/s03_desk_e189.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e189.sh"
rb_init s03_desk
e189_window
E=tools/claims-v3/e189
PINS="tools/claims-v3/e189/SHA256SUMS-e189-registration:10:bf1b1bbb4c2b34fcabf5b437cf98d602841315342a239303a11eb2eb72c79058:top
docs/reports/data/2026-11-12-q166-progs/SHA256SUMS:165:96493d9f5e19915057ebe3112bdac568460499920e2beb0e7c1b792a9b8a54b4:beside
docs/reports/data/2026-11-12-q166-ledger-v2/SHA256SUMS:17:aa6f7f733508d0c4be89c0b3aedcbe34be1d7bf809876bd9a50b56eaeed10921:top
docs/reports/data/2026-11-12-q166-ledger-v2/SHA256SUMS-freeze:6:8285585bfaa5923e4a1a50caa188a3eb9473a2bf48eb6df46d0699c59f5b43ee:top
docs/reports/data/2026-11-12-q166-counter-sparseparity/SHA256SUMS:86:8870e90967d11f095bc8cd0dfd641c1f47a68fa2b9f92d0ce99f8cbc2f5b426e:beside"   # list:count:its own sha256:paths from
KITPIN=tools/claims-v3/e189/SHA256SUMS-e189-kit:55:1f9a322483b9cbb018a3dc384716d5c29184b5fad70c48d3fe1c91574e5c0afe:top   # the kit's own list, at its count and its own bytes
bad=""
e189_pull || bad="$bad pull"
[ -z "${RB_DRY:-}" ] && [ "${RB_RC:-0}" -ne 0 ] && bad="$bad pull(rc $RB_RC; a nested lab-git lock exits 75)"
rb_local read local "HEAD before the checks" git -C "$RB_REPO" rev-parse HEAD
h0=$(rb_val '^([0-9a-f]{40})$')
rb_local read local "HEAD descends from $RB_E189_BASE (Q166's programs, pinned by the registration)" git -C "$RB_REPO" merge-base --is-ancestor "$RB_E189_BASE" HEAD || bad="$bad ancestry"
rb_local read local "E189's registration commit, by its content (the commit that added E189.md)" git -C "$RB_REPO" log --diff-filter=A --format=%H -- $E/E189.md
reg=$(rb_val '^([0-9a-f]{40})$')
if [ -z "${RB_DRY:-}" ]; then
  if [ -z "$reg" ]; then bad="$bad registration(missing)"; else
    rb_local read local "the registration commit is an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$reg" HEAD || bad="$bad registration-ancestry"
    rb_local read local "the registration's e189 subtree" git -C "$RB_REPO" rev-parse "$reg:$E"
    rb_has "^$E189_REG_SUBTREE\$" || bad="$bad registration-subtree"
  fi
else
  rb_local read local "the registration commit is an ancestor of HEAD, and its e189 subtree reads $E189_REG_SUBTREE" git -C "$RB_REPO" rev-parse "<reg>:$E"
fi
rb_local read local "E189's paths clean" git -C "$RB_REPO" status --short $E workloads/ledger workloads/sparseparity tools/ledger tools/counter \
  docs/reports/data/2026-11-12-q166-progs docs/reports/data/2026-11-12-q166-ledger-v2 docs/reports/data/2026-11-12-q166-counter-sparseparity
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
rb_local read local "the history check: additions only on E189's paths since $RB_E189_BASE and since the registration and the kit (check_history_e189.py)" \
  /usr/bin/python3 -I -B $E/rb/check_history_e189.py tree --base "$RB_E189_BASE"
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || bad="$bad history"
paths=""; for spec in $PINS $KITPIN; do paths="$paths ${spec%%:*}"; done
rb_local read local "the own sha256 of the lists E189 reads (pinned)" shasum -a 256 $paths
own=$RB_CAP
for spec in $PINS $KITPIN; do
  IFS=: read -r l pin hpin form <<EOF2
$spec
EOF2
  if [ "$form" = beside ]; then RB_CWD="$RB_REPO/$(dirname "$l")"; arg=$(basename "$l"); else RB_CWD="$RB_REPO"; arg=$l; fi
  RB_CWD=$RB_CWD rb_local read local "the list $(basename "$l") (pinned at $pin entries and its own sha256)" shasum -a 256 -c "$arg"
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
  rb_local read local "a list step 2 does not pin: $(basename "$f") (REPORTED, never a gate)" shasum -a 256 -c "$f"
done
rb_local desk local "harness-e189.json re-made" /usr/bin/python3 -I -B $E/check_e189.py --check
rb_has '^CHECK PASS' || bad="$bad harness-rebuild"
rb_local desk local "every harness file at its sha256 in the lab clone" /usr/bin/python3 -I -B $E/check_e189.py --box
rb_has '^HARNESS OK: ' || bad="$bad harness"
rb_local read local "the host check's frozen lines against their sources" /usr/bin/python3 -I -B $E/hostcheck_e189.py --check-json
rb_has '^HOSTCHECK-JSON CHECK PASS' || bad="$bad hostcheck-json"
rb_local read local "the common module's self-check (the written order, K, the commands, the adapter)" /usr/bin/python3 -I -B $E/e189_common.py
rb_has '^E189-COMMON SELF-CHECK PASS' || bad="$bad common"
rb_local read local "the registration's plan re-made" /usr/bin/python3 -I -B $E/plan_e189.py --check
rb_has '^PLAN CHECK PASS' || bad="$bad plan"
rb_local desk local "the registration's forecast re-made" /usr/bin/python3 -I -B $E/forecast_e189.py --check
rb_has '^FORECAST CHECK PASS' || bad="$bad forecast"
rb_local desk local "the scorer's E59 self-test" /usr/bin/python3 -I -B $E/score_e189.py --selftest-e59
rb_has '"verdict": "PASS"' || bad="$bad selftest-e59"
rb_local desk local "the never-run check at this HEAD (Q166's progs folder left out, as registered)" /usr/bin/python3 -I -B workloads/ledger/spp_never_ran.py \
  --exclude docs/reports/data/2026-11-12-q166-progs --n 544 --k 4 --eta 0.39 --m 1792 --seed 3
rb_has '^NEVER RAN' || bad="$bad never-ran"
rb_local desk local "the preflight: dmcmd_audit on the session's files, no WRITE allowed" bash $E/preflight_e189.sh
rb_has '^dmcmd_audit: GO' || bad="$bad preflight"
for spec in "logs/desktest-hosts-e189.txt ^DESKTEST-HOSTS-E189.[0-9]+.of.[0-9]+.PASS" "logs/selftest-run-e189.txt ^SELFTEST-RUN-E189.[0-9]+.of.[0-9]+.PASS" \
            "logs/selftest-rest-e189.txt ^SELFTEST-REST-E189.[0-9]+.of.[0-9]+.PASS" "logs/selftest-rb-e189.txt ^SELFTEST-RB-E189.[0-9]+.of.[0-9]+.PASS" \
            "logs/dry-listing-e189.txt ^dry.listing:.[0-9]+.steps.listed,.0.exited.non-zero,.0.box.calls$" "logs/dmcmd-audit-e189.txt ^dmcmd_audit:.GO"; do
  set -- $spec
  rb_local read local "a desk test's log, as committed: $1" grep -cE "$2" "$E/$1"
  rb_has '^1$' || bad="$bad $(basename "$1" .txt)"
done
rb_local read local "HEAD after the checks" git -C "$RB_REPO" rev-parse HEAD
h1=$(rb_val '^([0-9a-f]{40})$')
[ -n "${RB_DRY:-}" ] || [ "$h0" = "$h1" ] || bad="$bad HEAD-moved"
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
rb_local read local "E189 data in any ref (want none before the session)" git -C "$RB_REPO" log --all --oneline -- 'docs/reports/data/*e189*'
nd=0; [ -z "${RB_DRY:-}" ] && nd=$(grep -c . "$RB_CAP")
echo "$(date '+%F %T %Z') step=$RB_STEP lists not pinned (reported):${unknown:- none}" >> "$RB_LOG"
rb_say "desk check: the window written today for E189; pulled under the lab-git lock, HEAD ${h1:0:12} descends from $RB_E189_BASE and the registration ${reg:0:12} (subtree ${E189_REG_SUBTREE:0:8}), the paths clean, HISTORY OK, the lists at their pinned counts and bytes (10; 165; 17, 6; 86) and the kit's ($(echo "$KITPIN" | cut -d: -f2)), lists not pinned (reported):${unknown:- none}; the harness re-made and at its sha256, the host check's lines, the common self-check, the plan and forecast re-made, the E59 self-test, NEVER RAN, the preflight GO, the kit's desk tests' logs; commits naming E189 data: $nd"
