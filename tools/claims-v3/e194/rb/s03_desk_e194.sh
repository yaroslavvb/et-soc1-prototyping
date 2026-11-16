#!/usr/bin/env bash
# E194 (Q183, the kit, Sun 15 Nov 2026, after E194's registration 0d8e3de0 and before any E194 datum), the box step "step 2" (this file is
# s03): the desk check before any box step, on the desk (aifoundry2, which is also E194's box), in E191's step 2 form
# (tools/claims-v3/e191/rb/s03_desk_e191.sh, unchanged beside it) with E194's pins:
#   - the window first: RB_OUT's window written today (Pacific) for E194 (e194_window), or refused (10) before any call;
#   - the pull under the lab-git lock (e194_pull: RB_GITLOCK required; this step takes the lock itself for the pull alone, so it is NEVER
#     run inside that lock: a nested flock exits 75 and this step stops with 16);
#   - HEAD descends from 46a16bd0 (Q166's programs), from E194's registration (found by its content: the commit that added E194.md; it is
#     not pinned by its sha, which a landing re-makes, but by its list and E194.md's own bytes, below), from E191's registration
#     (300d76e4) and from E189's registration and kit (found by content);
#   - E194's paths clean; the history check (rb/check_history_e194.py tree);
#   - EVERY LIST E194 READS at its pinned count AND its own pinned sha256 AND every entry OK, with no override: E194's registration (17,
#     788af7da...) and its dated note 1 (1, fix-e194), E191's registration (11) and note 1 (3) (E194's forecast reads E191's frozen forecast; its kit ports E191's), E189's
#     registration (10) and kit (55: the host check, its frozen lines, the plan and the stand-ins E194's build and tests run), Q166's progs
#     (165), the ledger v2's two (17 and 6), the counter's (86), and THE KIT'S OWN LIST (SHA256SUMS-e194-kit) at its count and bytes (this
#     step is outside it); every file with "SHA256SUMS" anywhere in its name under tools/claims-v3/e194 found (one not pinned is REPORTED,
#     never a gate);
#   - E194.md's own sha256 a8ed7f50... and E189.md's 98b385b6... (the texts E194 cites);
#   - harness-e194.json re-made (CHECK PASS) and every file of it at its sha256 (HARNESS OK); E194's configurations equal E189's (PLANS
#     SAME); E189's host check's frozen lines against their sources; both modules' self-checks; the registration's plan and forecast re-made
#     (--check) and the scorer's E59 self-test (PASS); the preflight (dmcmd_audit GO, no WRITE);
#   - THE NEVER-RUN CHECK as E194.md 17 item 7 restates it: spp_never_ran.py with Q166's progs folder, E189's data folder and E191's left
#     out reads NEVER RAN, "E191's" read as BOTH of E191's data folders, its first session's (-c1) and the second session's E191.md A1
#     registers (-c1-s2) (fix-e194, verify-e194's finding 1; E194.md.dated-note-1.md section 3); and no docs/reports/data/*e194* path in any ref;
#   - fix-e194: E194's dated note 1 (E194.md.dated-note-1.md, landed with the registration) at its list SHA256SUMS-e194-note1 (1 entry);
#   - the kit's desk tests' logs as committed, each with its PASS line once;
#   - HEAD unchanged across all of it, else 16.
# The load (THE LOAD RULE) is read by the card lane before this step; this step does not read it. It reaches no box.
#   RB_GITLOCK=<the lab-git lock> bash tools/claims-v3/e194/rb/s03_desk_e194.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e194.sh"
rb_init s03_desk
e194_window
E=tools/claims-v3/e194
PINS="tools/claims-v3/e194/SHA256SUMS-e194-registration:17:788af7da85edd049db1a1e6cf8f273018472b1e576ab131ba9ffeb0d6dc8b7d0:top
tools/claims-v3/e194/SHA256SUMS-e194-note1:1:6679c26a92d44f137301cac3e07378886a3c3b3a14e347fa9c1984ec43459eb5:top
tools/claims-v3/e191/SHA256SUMS-e191-registration:11:e458fa827536b099b66af1352e2060950eb722bc755de51d810e78cb6015f5d3:top
tools/claims-v3/e191/SHA256SUMS-e191-note1:3:45ebe83172ddaaf7384534f2ba12ff7741a88d7050aa0e34706ea922b979909b:top
tools/claims-v3/e189/SHA256SUMS-e189-registration:10:bf1b1bbb4c2b34fcabf5b437cf98d602841315342a239303a11eb2eb72c79058:top
tools/claims-v3/e189/SHA256SUMS-e189-kit:55:1f9a322483b9cbb018a3dc384716d5c29184b5fad70c48d3fe1c91574e5c0afe:top
docs/reports/data/2026-11-12-q166-progs/SHA256SUMS:165:96493d9f5e19915057ebe3112bdac568460499920e2beb0e7c1b792a9b8a54b4:beside
docs/reports/data/2026-11-12-q166-ledger-v2/SHA256SUMS:17:aa6f7f733508d0c4be89c0b3aedcbe34be1d7bf809876bd9a50b56eaeed10921:top
docs/reports/data/2026-11-12-q166-ledger-v2/SHA256SUMS-freeze:6:8285585bfaa5923e4a1a50caa188a3eb9473a2bf48eb6df46d0699c59f5b43ee:top
docs/reports/data/2026-11-12-q166-counter-sparseparity/SHA256SUMS:86:8870e90967d11f095bc8cd0dfd641c1f47a68fa2b9f92d0ce99f8cbc2f5b426e:beside"   # list:count:its own sha256:paths from
KITPIN=tools/claims-v3/e194/SHA256SUMS-e194-kit:78:2f3da0247fca29b33a6e58994106139f8168ebda3a0efd1d9a4bff24518b72da:top   # the kit's own list (set at the kit's commit)
E189MD=98b385b6d8f081dd2d8704bfba6bb24bb20808001b55ab801e6d2cc1d4882e32
bad=""
e194_pull || bad="$bad pull"
[ -z "${RB_DRY:-}" ] && [ "${RB_RC:-0}" -ne 0 ] && bad="$bad pull(rc $RB_RC; a nested lab-git lock exits 75)"
rb_local read local "HEAD before the checks" git -C "$RB_REPO" rev-parse HEAD
h0=$(rb_val '^([0-9a-f]{40})$')
rb_local read local "HEAD descends from 46a16bd0 (Q166's programs)" git -C "$RB_REPO" merge-base --is-ancestor 46a16bd0 HEAD || bad="$bad ancestry"
rb_local read local "HEAD descends from E191's registration (300d76e4)" git -C "$RB_REPO" merge-base --is-ancestor 300d76e4c9ab5a76e5a1fc23f0ed08ac2477b868 HEAD || bad="$bad e191-ancestry"
rb_local read local "E194's registration commit, by its content (the commit that added E194.md)" git -C "$RB_REPO" log --diff-filter=A --format=%H -- $E/E194.md
reg=$(rb_val '^([0-9a-f]{40})$')
if [ -z "${RB_DRY:-}" ]; then
  if [ -z "$reg" ]; then bad="$bad registration(missing)"; else
    rb_local read local "the registration commit is an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$reg" HEAD || bad="$bad registration-ancestry"
  fi
else
  rb_local read local "the registration commit is an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "<reg>" HEAD
fi
for spec in "E189.md:E189's registration" "KIT.md:E189's kit"; do
  rb_local read local "${spec#*:} commit, by its content" git -C "$RB_REPO" log --diff-filter=A --format=%H -- "tools/claims-v3/e189/${spec%%:*}"
  c=$(rb_val '^([0-9a-f]{40})$')
  [ -n "${RB_DRY:-}" ] || { [ -n "$c" ] && git -C "$RB_REPO" merge-base --is-ancestor "$c" HEAD; } || bad="$bad e189-${spec%%.*}"
done
rb_local read local "E194's paths clean" git -C "$RB_REPO" status --short $E tools/claims-v3/e191 tools/claims-v3/e189 workloads/ledger workloads/sparseparity tools/ledger tools/counter \
  docs/reports/data/2026-11-12-q166-progs docs/reports/data/2026-11-12-q166-ledger-v2 docs/reports/data/2026-11-12-q166-counter-sparseparity
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
rb_local read local "the history check: additions only on E194's paths since 46a16bd0, since E194's registration and kit, and since E191's and E189's registrations and kits (check_history_e194.py)" \
  /usr/bin/python3 -I -B $E/rb/check_history_e194.py tree --base 46a16bd0
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || bad="$bad history"
paths=""; for spec in $PINS $KITPIN; do paths="$paths ${spec%%:*}"; done
rb_local read local "the own sha256 of the lists E194 reads (pinned), E194.md and E189.md" shasum -a 256 $paths $E/E194.md tools/claims-v3/e189/E189.md
own=$RB_CAP
if [ -z "${RB_DRY:-}" ]; then
  [ "$(awk -v p="$E/E194.md" '$2 == p {print $1}' "$own")" = "$E194_MD_SHA" ] || bad="$bad E194.md(not the registered text, ${E194_MD_SHA:0:8})"
  [ "$(awk '$2 == "tools/claims-v3/e189/E189.md" {print $1}' "$own")" = "$E189MD" ] || bad="$bad E189.md(not the text E194 cites, 98b385b6)"
fi
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
rb_local desk local "harness-e194.json re-made" /usr/bin/python3 -I -B $E/check_e194.py --check
rb_has '^CHECK PASS' || bad="$bad harness-rebuild"
rb_local desk local "every harness file at its sha256 in the lab clone" /usr/bin/python3 -I -B $E/check_e194.py --box
rb_has '^HARNESS OK: ' || bad="$bad harness"
rb_local read local "E194's six configurations equal E189's (E189's host check reads E194's hosts unchanged)" /usr/bin/python3 -I -B $E/check_e194.py --plans
rb_has '^PLANS SAME' || bad="$bad plans"
rb_local read local "E189's host check's frozen lines against their sources" /usr/bin/python3 -I -B tools/claims-v3/e189/hostcheck_e189.py --check-json
rb_has '^HOSTCHECK-JSON CHECK PASS' || bad="$bad hostcheck-json"
rb_local read local "the common module's self-check (the written order, K, the stop lines, the clock rule, the parser, the card)" /usr/bin/python3 -I -B $E/e194_common.py
rb_has '^E194-COMMON SELF-CHECK PASS' || bad="$bad common"
rb_local read local "the identity module's self-check (card 0's forms pass; a second card's and a missing node's refused)" /usr/bin/python3 -I -B $E/e194_ident.py
rb_has '^E194-IDENT SELF-CHECK PASS' || bad="$bad ident"
rb_local read local "the registration's plan re-made" /usr/bin/python3 -I -B $E/plan_e194.py --check
rb_has '^PLAN CHECK PASS' || bad="$bad plan"
rb_local desk local "the registration's forecast re-made" /usr/bin/python3 -I -B $E/forecast_e194.py --check
rb_has '^FORECAST CHECK PASS' || bad="$bad forecast"
rb_local desk local "the scorer's E59 self-test" /usr/bin/python3 -I -B $E/score_e194.py --selftest-e59
rb_has '"verdict": "PASS"' || bad="$bad selftest-e59"
rb_local desk local "the never-run check, E194.md 17 item 7: Q166's progs folder, E189's data folder and both of E191's left out (E194.md.dated-note-1.md 3)" /usr/bin/python3 -I -B workloads/ledger/spp_never_ran.py \
  --exclude docs/reports/data/2026-11-12-q166-progs --exclude docs/reports/data/2026-11-14-e189-blind-day-aifoundry3 \
  --exclude docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1 --exclude docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2 \
  --n 544 --k 4 --eta 0.39 --m 1792 --seed 3
rb_has '^NEVER RAN' || bad="$bad never-ran"
rb_local read local "E194 data in any ref (want none before the session)" git -C "$RB_REPO" log --all --oneline -- 'docs/reports/data/*e194*'
nd=0; [ -z "${RB_DRY:-}" ] && nd=$(grep -c . "$RB_CAP")
[ "$nd" -eq 0 ] || bad="$bad e194-data($nd commits name E194 data)"
rb_local desk local "the preflight: dmcmd_audit on the session's files, no WRITE allowed" bash $E/preflight_e194.sh
rb_has '^dmcmd_audit: GO' || bad="$bad preflight"
for spec in "logs/selftest-run-e194.txt ^SELFTEST-RUN-E194.[0-9]+.of.[0-9]+.PASS" "logs/realpath-e194.txt ^REALPATH-E194.[0-9]+.of.[0-9]+.PASS" \
            "logs/dry-audit-e194.txt ^DRY-AUDIT-E194.[0-9]+.of.[0-9]+.COVERED" "logs/selftest-rest-e194.txt ^SELFTEST-REST-E194.[0-9]+.of.[0-9]+.PASS" \
            "logs/selftest-rb-e194.txt ^SELFTEST-RB-E194.[0-9]+.of.[0-9]+.PASS" "logs/selftest-wait-e194.txt ^SELFTEST-WAIT-E194.[0-9]+.of.[0-9]+.PASS" \
            "logs/selftest-quiet-e194.txt ^SELFTEST-QUIET-E194.[0-9]+.of.[0-9]+.PASS" "logs/parser-e194.txt ^PARSER-E194.[0-9]+.of.[0-9]+.PASS" \
            "logs/identity-e194.txt ^IDENTITY-E194.[0-9]+.of.[0-9]+.PASS" "logs/checks-e194.txt ^CHECKS-E194.[0-9]+.of.[0-9]+.PASS" \
            "logs/realbuild-e194.txt ^REALBUILD-E194.[0-9]+.of.[0-9]+.PASS" \
            "logs/dry-listing-e194.txt ^dry.listing:.[0-9]+.steps.listed,.0.exited.non-zero,.0.box.calls.beyond.aifoundry2$" "logs/dmcmd-audit-e194.txt ^dmcmd_audit:.GO"; do
  set -- $spec
  rb_local read local "a desk test's log, as committed: $1" grep -cE "$2" "$E/$1"
  rb_has '^1$' || bad="$bad $(basename "$1" .txt)"
done
rb_local read local "HEAD after the checks" git -C "$RB_REPO" rev-parse HEAD
h1=$(rb_val '^([0-9a-f]{40})$')
[ -n "${RB_DRY:-}" ] || [ "$h0" = "$h1" ] || bad="$bad HEAD-moved"
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
echo "$(date '+%F %T %Z') step=$RB_STEP lists not pinned (reported):${unknown:- none}" >> "$RB_LOG"
rb_say "desk check: the window written today for E194; pulled under the lab-git lock, HEAD ${h1:0:12} descends from 46a16bd0, E194's registration ${reg:0:12}, E191's registration and E189's registration and kit; the paths clean, HISTORY OK, the lists at their pinned counts and bytes (17; 1; 11; 3; 10; 55; 165; 17, 6; 86) and the kit's ($(echo "$KITPIN" | cut -d: -f2)), E194.md and E189.md the registered and cited texts, lists not pinned (reported):${unknown:- none}; the harness re-made and at its sha256, PLANS SAME, the host check's lines, both self-checks, the plan and forecast re-made, the E59 self-test, NEVER RAN with E189's and both of E191's data folders left out, no E194 data in any ref; the preflight GO, the kit's desk tests' logs"
