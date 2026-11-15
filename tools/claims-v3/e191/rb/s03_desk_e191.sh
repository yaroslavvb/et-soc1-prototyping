#!/usr/bin/env bash
# E191 (Q178, the kit, Sat 14 Nov 2026, after E189's data commit fa9098c4 and before any E191 datum), the box step "step 2" (this file is
# s03): the desk check before any box step, on the desk only (aifoundry2), in E189's step 2 form (tools/claims-v3/e189/rb/s03_desk_e189.sh,
# unchanged beside it) with E191's pins and E191's dated note 1's checks (sections 2 and 4):
#   - the window first: RB_OUT's window written today (Pacific) for E191 (e191_window), or refused (10) before any call;
#   - the pull under the lab-git lock (e191_pull: RB_GITLOCK required; this step takes the lock itself for the pull alone, so it is NEVER
#     run inside that lock: a nested flock exits 75 and this step stops with 16);
#   - HEAD descends from 46a16bd0 (Q166's programs), from E191's registration (found by its content: the commit that added E191.md, its
#     e191 subtree 766e2463...), from E191's dated note 1 (8c8f825f) and from E189's registration and kit (found by content);
#   - E191's paths clean; the history check (rb/check_history_e191.py tree);
#   - EVERY LIST E191 READS at its pinned count AND its own pinned sha256 AND every entry OK, with no override: E191's registration (11),
#     E191's note 1 (3), E189's registration (10, bf1b1bbb...: note 1 section 4's check that E189.md is the text E191 cites, 98b385b6...),
#     E189's kit (55: the host check, its frozen lines and the plan E191's build runs), Q166's progs (165), the ledger v2's two (17 and 6),
#     the counter's (86), and THE KIT'S OWN LIST (SHA256SUMS-e191-kit) at its count and bytes (this step is outside it); every file with
#     "SHA256SUMS" anywhere in its name under tools/claims-v3/e191 found (one not pinned is REPORTED, never a gate);
#   - E189.md's own sha256 98b385b6... (note 1 section 4: the cited text, else no E191 day);
#   - harness-e191.json re-made (CHECK PASS) and every file of it at its sha256 (HARNESS OK); E191's configurations equal E189's (PLANS
#     SAME: E189's host check reads E191's hosts); E189's host check's frozen lines against their sources; both modules' self-checks; the
#     registration's plan and forecast re-made (--check) and the scorer's E59 self-test (PASS); the preflight (dmcmd_audit GO, no WRITE);
#   - THE NEVER-RUN CHECK as note 1 section 2 restates it: (a) spp_never_ran.py with Q166's progs folder and E189's data folder left out
#     reads NEVER RAN; (b) 300d76e4 is an ancestor of E189's data commit (found by its content) and was committed before it; (c) no
#     docs/reports/data/*e191* path in any ref;
#   - the kit's desk tests' logs as committed, each with its PASS line once (the real build's, desk/realbuild_e191.sh, among them: fix-e191k);
#   - HEAD unchanged across all of it, else 16.
# The load (THE LOAD RULE) is read by the card lane before this step; this step does not read it.
#   RB_GITLOCK=<the lab-git lock> bash tools/claims-v3/e191/rb/s03_desk_e191.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e191.sh"
rb_init s03_desk
e191_window
E=tools/claims-v3/e191
PINS="tools/claims-v3/e191/SHA256SUMS-e191-registration:11:e458fa827536b099b66af1352e2060950eb722bc755de51d810e78cb6015f5d3:top
tools/claims-v3/e191/SHA256SUMS-e191-note1:3:45ebe83172ddaaf7384534f2ba12ff7741a88d7050aa0e34706ea922b979909b:top
tools/claims-v3/e189/SHA256SUMS-e189-registration:10:bf1b1bbb4c2b34fcabf5b437cf98d602841315342a239303a11eb2eb72c79058:top
tools/claims-v3/e189/SHA256SUMS-e189-kit:55:1f9a322483b9cbb018a3dc384716d5c29184b5fad70c48d3fe1c91574e5c0afe:top
docs/reports/data/2026-11-12-q166-progs/SHA256SUMS:165:96493d9f5e19915057ebe3112bdac568460499920e2beb0e7c1b792a9b8a54b4:beside
docs/reports/data/2026-11-12-q166-ledger-v2/SHA256SUMS:17:aa6f7f733508d0c4be89c0b3aedcbe34be1d7bf809876bd9a50b56eaeed10921:top
docs/reports/data/2026-11-12-q166-ledger-v2/SHA256SUMS-freeze:6:8285585bfaa5923e4a1a50caa188a3eb9473a2bf48eb6df46d0699c59f5b43ee:top
docs/reports/data/2026-11-12-q166-counter-sparseparity/SHA256SUMS:86:8870e90967d11f095bc8cd0dfd641c1f47a68fa2b9f92d0ce99f8cbc2f5b426e:beside"   # list:count:its own sha256:paths from
KITPIN=tools/claims-v3/e191/SHA256SUMS-e191-kit:73:ec759bfa23d822c57609b1faf09053fc0028b96b0a1eda64d47a291cd3b2c666:top   # the kit's own list (set at the kit's commit)
E189MD=98b385b6d8f081dd2d8704bfba6bb24bb20808001b55ab801e6d2cc1d4882e32
bad=""
e191_pull || bad="$bad pull"
[ -z "${RB_DRY:-}" ] && [ "${RB_RC:-0}" -ne 0 ] && bad="$bad pull(rc $RB_RC; a nested lab-git lock exits 75)"
rb_local read local "HEAD before the checks" git -C "$RB_REPO" rev-parse HEAD
h0=$(rb_val '^([0-9a-f]{40})$')
rb_local read local "HEAD descends from 46a16bd0 (Q166's programs)" git -C "$RB_REPO" merge-base --is-ancestor 46a16bd0 HEAD || bad="$bad ancestry"
rb_local read local "HEAD descends from E191's dated note 1 ($RB_E191_NOTE1)" git -C "$RB_REPO" merge-base --is-ancestor "$RB_E191_NOTE1" HEAD || bad="$bad note1-ancestry"
rb_local read local "E191's registration commit, by its content (the commit that added E191.md)" git -C "$RB_REPO" log --diff-filter=A --format=%H -- $E/E191.md
reg=$(rb_val '^([0-9a-f]{40})$')
if [ -z "${RB_DRY:-}" ]; then
  if [ -z "$reg" ]; then bad="$bad registration(missing)"; else
    rb_local read local "the registration commit is an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$reg" HEAD || bad="$bad registration-ancestry"
    rb_local read local "the registration's e191 subtree" git -C "$RB_REPO" rev-parse "$reg:$E"
    rb_has "^$E191_REG_SUBTREE\$" || bad="$bad registration-subtree"
  fi
else
  rb_local read local "the registration commit is an ancestor of HEAD, and its e191 subtree reads $E191_REG_SUBTREE" git -C "$RB_REPO" rev-parse "<reg>:$E"
fi
for spec in "E189.md:E189's registration" "KIT.md:E189's kit"; do
  rb_local read local "${spec#*:} commit, by its content" git -C "$RB_REPO" log --diff-filter=A --format=%H -- "tools/claims-v3/e189/${spec%%:*}"
  c=$(rb_val '^([0-9a-f]{40})$')
  [ -n "${RB_DRY:-}" ] || { [ -n "$c" ] && git -C "$RB_REPO" merge-base --is-ancestor "$c" HEAD; } || bad="$bad e189-${spec%%.*}"
done
rb_local read local "E191's paths clean" git -C "$RB_REPO" status --short $E tools/claims-v3/e189 workloads/ledger workloads/sparseparity tools/ledger tools/counter \
  docs/reports/data/2026-11-12-q166-progs docs/reports/data/2026-11-12-q166-ledger-v2 docs/reports/data/2026-11-12-q166-counter-sparseparity
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
rb_local read local "the history check: additions only on E191's paths since 46a16bd0, since E191's registration, note 1 and kit, and since E189's registration and kit (check_history_e191.py)" \
  /usr/bin/python3 -I -B $E/rb/check_history_e191.py tree --base 46a16bd0
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || bad="$bad history"
paths=""; for spec in $PINS $KITPIN; do paths="$paths ${spec%%:*}"; done
rb_local read local "the own sha256 of the lists E191 reads (pinned)" shasum -a 256 $paths tools/claims-v3/e189/E189.md
own=$RB_CAP
if [ -z "${RB_DRY:-}" ]; then
  [ "$(awk '$2 == "tools/claims-v3/e189/E189.md" {print $1}' "$own")" = "$E189MD" ] || bad="$bad E189.md(not the text E191 cites, 98b385b6)"
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
rb_local desk local "harness-e191.json re-made" /usr/bin/python3 -I -B $E/check_e191.py --check
rb_has '^CHECK PASS' || bad="$bad harness-rebuild"
rb_local desk local "every harness file at its sha256 in the lab clone" /usr/bin/python3 -I -B $E/check_e191.py --box
rb_has '^HARNESS OK: ' || bad="$bad harness"
rb_local read local "E191's six configurations equal E189's (E189's host check reads E191's hosts unchanged)" /usr/bin/python3 -I -B $E/check_e191.py --plans
rb_has '^PLANS SAME' || bad="$bad plans"
rb_local read local "E189's host check's frozen lines against their sources" /usr/bin/python3 -I -B tools/claims-v3/e189/hostcheck_e189.py --check-json
rb_has '^HOSTCHECK-JSON CHECK PASS' || bad="$bad hostcheck-json"
rb_local read local "the common module's self-check (the written order, K, the commands, the adapter, the readings, the card)" /usr/bin/python3 -I -B $E/e191_common.py
rb_has '^E191-COMMON SELF-CHECK PASS' || bad="$bad common"
rb_local read local "the identity module's self-check (card 1's forms pass, card 0's refused)" /usr/bin/python3 -I -B $E/e191_ident.py
rb_has '^E191-IDENT SELF-CHECK PASS' || bad="$bad ident"
rb_local read local "the registration's plan re-made" /usr/bin/python3 -I -B $E/plan_e191.py --check
rb_has '^PLAN CHECK PASS' || bad="$bad plan"
rb_local desk local "the registration's forecast re-made" /usr/bin/python3 -I -B $E/forecast_e191.py --check
rb_has '^FORECAST CHECK PASS' || bad="$bad forecast"
rb_local desk local "the scorer's E59 self-test" /usr/bin/python3 -I -B $E/score_e191.py --selftest-e59
rb_has '"verdict": "PASS"' || bad="$bad selftest-e59"
rb_local desk local "the never-run check (a), note 1 section 2: Q166's progs folder and E189's data folder left out" /usr/bin/python3 -I -B workloads/ledger/spp_never_ran.py \
  --exclude docs/reports/data/2026-11-12-q166-progs --exclude docs/reports/data/2026-11-14-e189-blind-day-aifoundry3 --n 544 --k 4 --eta 0.39 --m 1792 --seed 3
rb_has '^NEVER RAN' || bad="$bad never-ran(a)"
rb_local read local "the never-run check (b): E189's data commit, by its content" git -C "$RB_REPO" log --diff-filter=A --format='%H %ct' -- 'docs/reports/data/*-e189-blind-day-aifoundry3/README.md'
if [ -z "${RB_DRY:-}" ]; then
  e189d=$(rb_val '^([0-9a-f]{40}) [0-9]+$'); e189t=$(rb_val '^[0-9a-f]{40} ([0-9]+)$')
  regt=$(git -C "$RB_REPO" log -1 --format=%ct "$RB_E191_REG" 2>/dev/null)
  if [ -z "$e189d" ]; then bad="$bad never-ran(b: no E189 data commit)"
  else
    git -C "$RB_REPO" merge-base --is-ancestor "$RB_E191_REG" "$e189d" && [ -n "$regt" ] && [ "$regt" -lt "$e189t" ] || bad="$bad never-ran(b)"
  fi
fi
rb_local read local "the never-run check (c): E191 data in any ref (want none before the session)" git -C "$RB_REPO" log --all --oneline -- 'docs/reports/data/*e191*'
nd=0; [ -z "${RB_DRY:-}" ] && nd=$(grep -c . "$RB_CAP")
[ "$nd" -eq 0 ] || bad="$bad never-ran(c: $nd commits name E191 data)"
rb_local desk local "the preflight: dmcmd_audit on the session's files, no WRITE allowed" bash $E/preflight_e191.sh
rb_has '^dmcmd_audit: GO' || bad="$bad preflight"
for spec in "logs/selftest-run-e191.txt ^SELFTEST-RUN-E191.[0-9]+.of.[0-9]+.PASS" "logs/realpath-e191.txt ^REALPATH-E191.[0-9]+.of.[0-9]+.PASS" \
            "logs/dry-audit-e191.txt ^DRY-AUDIT-E191.[0-9]+.of.[0-9]+.COVERED" "logs/selftest-rest-e191.txt ^SELFTEST-REST-E191.[0-9]+.of.[0-9]+.PASS" \
            "logs/selftest-rb-e191.txt ^SELFTEST-RB-E191.[0-9]+.of.[0-9]+.PASS" "logs/selftest-wait-e191.txt ^SELFTEST-WAIT-E191.[0-9]+.of.[0-9]+.PASS" \
            "logs/etdevices-e191.txt ^ETDEVICES-E191.[0-9]+.of.[0-9]+.PASS" "logs/checks-e191.txt ^CHECKS-E191.[0-9]+.of.[0-9]+.PASS" \
            "logs/realbuild-e191.txt ^REALBUILD-E191.[0-9]+.of.[0-9]+.PASS" \
            "logs/dry-listing-e191.txt ^dry.listing:.[0-9]+.steps.listed,.0.exited.non-zero,.0.box.calls$" "logs/dmcmd-audit-e191.txt ^dmcmd_audit:.GO"; do
  set -- $spec
  rb_local read local "a desk test's log, as committed: $1" grep -cE "$2" "$E/$1"
  rb_has '^1$' || bad="$bad $(basename "$1" .txt)"
done
rb_local read local "HEAD after the checks" git -C "$RB_REPO" rev-parse HEAD
h1=$(rb_val '^([0-9a-f]{40})$')
[ -n "${RB_DRY:-}" ] || [ "$h0" = "$h1" ] || bad="$bad HEAD-moved"
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
echo "$(date '+%F %T %Z') step=$RB_STEP lists not pinned (reported):${unknown:- none}" >> "$RB_LOG"
rb_say "desk check: the window written today for E191; pulled under the lab-git lock, HEAD ${h1:0:12} descends from 46a16bd0, E191's registration ${reg:0:12} (subtree ${E191_REG_SUBTREE:0:8}) and note 1, and E189's registration and kit; the paths clean, HISTORY OK, the lists at their pinned counts and bytes (11; 3; 10; 55; 165; 17, 6; 86) and the kit's ($(echo "$KITPIN" | cut -d: -f2)), E189.md the cited text, lists not pinned (reported):${unknown:- none}; the harness re-made and at its sha256, PLANS SAME, the host check's lines, both self-checks, the plan and forecast re-made, the E59 self-test, NEVER RAN (a) with E189's data left out, (b) 300d76e4 before E189's data, (c) no E191 data in any ref; the preflight GO, the kit's desk tests' logs"
