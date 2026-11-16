#!/usr/bin/env bash
# E194, dated amendment A1 (Q187, Sun 15 Nov 2026, before any E194 datum): the box step "step 2", v2 (this file is s03 v2): the desk check
# before any box step, on the desk (aifoundry2, which is also E194's box). It is the kit's step 2 (rb/s03_desk_e194.sh, f01e1cb2, unchanged
# beside it; E191's step 2 form) with every check and pin of it, and these changes, each named in the kit's dated note 1 (KIT.md.dated-note-1.md):
#   - THE AMENDMENT: E194.md's dated amendment A1, found by its content (the commit that added tools/claims-v3/e194/E194.md.dated-amendment-A1.md),
#     an ancestor of HEAD, as are the registration (by content) and THE KIT COMMIT (by content: the commit that added KIT.md); its list
#     SHA256SUMS-e194-amendment-A1 pinned at its count and its own sha256 (AMENDPIN below; this step is outside that list, as v1 is outside
#     the kit's: its own sha256 is in the amendment's anchor lines), every entry OK;
#   - THE FIRMWARE READ OF RECORD (fwread-e194's data commit 15cb0fcb): its list docs/reports/data/2026-11-15-e194-fwread-aifoundry2/SHA256SUMS
#     pinned at 8 entries and its own sha256, every entry OK; and E194's firmware gate's record check (rb/fwgate_e194.sh record: the record
#     as committed, its comparison re-run and the gate's own reading, EQUAL to E69's in all seven fields), FWGATE-E194 RECORD EQUAL;
#   - "E194 data in any ref" reads, in place of v1's "none": the commits of any ref that name a docs/reports/data/*e194* path are EXACTLY
#     fwread-e194's data commit 15cb0fcb, and every path any of them names lies in its directory (the firmware read, an identity read for the
#     reboot gate that holds no datum of E194's programs); any other commit or path there is E194 data: 16;
#   - the amendment's desk tests' logs as committed (rb/selftest_fwgate_e194.sh's and the v2 dry listing's), each with its PASS line once,
#     beside the kit's;
#   - THE NEVER-RUN CHECK also leaves out E191's third-session folders (A1-8, written before the land after verify-amend194's finding F2):
#     every directory at HEAD named exactly docs/reports/data/<YYYY-MM-DD>-e191-blind-day-aifoundry1-c1-s3, of any day (E191.md's dated
#     amendment A2's form), found by `git ls-tree` at HEAD and each named in the check's line and in the step's last line; a folder of any
#     other form, or one in the worktree that is not at HEAD, is not left out (it reads NAMED BEFORE: 16).
# Everything else is v1's, line for line: the window first; the pull under the lab-git lock (never run inside that lock); HEAD's ancestry;
# E194's paths clean; the history check; every list E194 reads at its pinned count and bytes (17; 1; 11; 3; 10; 55; 165; 17, 6; 86; the
# kit's 78); E194.md's and E189.md's bytes; the harness re-made and at its sha256; PLANS SAME; the host check's frozen lines; both modules'
# self-checks; the plan and forecast re-made; the E59 self-test; THE NEVER-RUN CHECK with Q166's progs folder, E189's data folder and both
# of E191's left out (and, by A1-8, E191's third-session folders); the preflight (dmcmd_audit GO); the kit's desk tests' logs; HEAD
# unchanged across all of it, else 16.
# The load (THE LOAD RULE) is read by the card lane before this step; this step does not read it. It reaches no box.
#   RB_GITLOCK=<the lab-git lock> bash tools/claims-v3/e194/rb/s03_desk_e194_v2.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e194.sh"
. "$(dirname "${BASH_SOURCE[0]}")/fwgate_e194.sh"
rb_init s03_desk_v2
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
AMENDPIN=tools/claims-v3/e194/SHA256SUMS-e194-amendment-A1:11:a5899e0fcc5b80cc2a172c081e805b495b5b2d3108b206ad454a5fa72bd4d002:top   # E194.md's dated amendment A1's own list (set at the amendment's commit)
FWPIN=docs/reports/data/2026-11-15-e194-fwread-aifoundry2/SHA256SUMS:8:daa088c8af935923ca3fb8654f84eee9b4f9311462b48484560928af4ee6772c:beside   # the firmware read of record's list
FWCOMMIT=$E194_FW_COMMIT; FWDIR=$E194_FW_DIR
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
for spec in "KIT.md:kit:E194's kit" "E194.md.dated-amendment-A1.md:amendment-A1:E194.md's dated amendment A1"; do
  IFS=: read -r fn tag what <<EOF2
$spec
EOF2
  rb_local read local "$what commit, by its content (the commit that added $fn)" git -C "$RB_REPO" log --diff-filter=A --format=%H -- "$E/$fn"
  c=$(rb_val '^([0-9a-f]{40})$')
  [ -n "${RB_DRY:-}" ] || { [ -n "$c" ] && git -C "$RB_REPO" merge-base --is-ancestor "$c" HEAD; } || bad="$bad e194-$tag(${c:-missing})"
done
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
paths=""; for spec in $PINS $KITPIN $AMENDPIN $FWPIN; do paths="$paths ${spec%%:*}"; done
rb_local read local "the own sha256 of the lists E194 reads (pinned), E194.md and E189.md" shasum -a 256 $paths $E/E194.md tools/claims-v3/e189/E189.md
own=$RB_CAP
if [ -z "${RB_DRY:-}" ]; then
  [ "$(awk -v p="$E/E194.md" '$2 == p {print $1}' "$own")" = "$E194_MD_SHA" ] || bad="$bad E194.md(not the registered text, ${E194_MD_SHA:0:8})"
  [ "$(awk '$2 == "tools/claims-v3/e189/E189.md" {print $1}' "$own")" = "$E189MD" ] || bad="$bad E189.md(not the text E194 cites, 98b385b6)"
fi
for spec in $PINS $KITPIN $AMENDPIN $FWPIN; do
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
S3RE='^docs/reports/data/[0-9]{4}-[0-9]{2}-[0-9]{2}-e191-blind-day-aifoundry1-c1-s3$'   # A1-8: E191's third-session folders, of any day
rb_local read local "E191's third-session folders at HEAD (docs/reports/data/<YYYY-MM-DD>-e191-blind-day-aifoundry1-c1-s3, of any day; E194.md.dated-amendment-A1.md A1-8)" \
  git -C "$RB_REPO" ls-tree -d --name-only HEAD docs/reports/data/
EXS3=""; NAMES3=""; s3n=0
if [ -z "${RB_DRY:-}" ]; then
  [ "$RB_RC" -eq 0 ] || bad="$bad s3-folders(git ls-tree rc $RB_RC)"
  for d in $(grep -E "$S3RE" "$RB_CAP"); do EXS3="$EXS3 --exclude $d"; NAMES3="$NAMES3 ${d#docs/reports/data/}"; s3n=$((s3n + 1)); done
fi
rb_local desk local "the never-run check, E194.md 17 item 7: Q166's progs folder, E189's data folder and both of E191's left out (E194.md.dated-note-1.md 3), and E191's third-session folders at HEAD ($s3n${NAMES3:+:$NAMES3}) (A1-8)" /usr/bin/python3 -I -B workloads/ledger/spp_never_ran.py \
  --exclude docs/reports/data/2026-11-12-q166-progs --exclude docs/reports/data/2026-11-14-e189-blind-day-aifoundry3 \
  --exclude docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1 --exclude docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2 $EXS3 \
  --n 544 --k 4 --eta 0.39 --m 1792 --seed 3
rb_has '^NEVER RAN' || bad="$bad never-ran"
rb_local read local "the commits of any ref that name E194 data (want exactly fwread-e194's data commit ${FWCOMMIT:0:12}, the firmware read of record)" git -C "$RB_REPO" log --all --format=%H -- 'docs/reports/data/*e194*'
if [ -z "${RB_DRY:-}" ]; then
  nd=$(grep -c . "$RB_CAP"); nf=$(grep -cx "$FWCOMMIT" "$RB_CAP")
  { [ "$nd" -eq 1 ] && [ "$nf" -eq 1 ]; } || bad="$bad e194-data($nd commit(s) name a docs/reports/data/*e194* path; want exactly ${FWCOMMIT:0:12})"
fi
rb_local read local "every path those commits name (want each inside $FWDIR/)" git -C "$RB_REPO" log --all --format= --name-only -- 'docs/reports/data/*e194*'
if [ -z "${RB_DRY:-}" ]; then
  np=$(grep -c . "$RB_CAP"); nx=$(grep . "$RB_CAP" | grep -vc "^$FWDIR/")
  { [ "$np" -ge 1 ] && [ "$nx" -eq 0 ]; } || bad="$bad e194-data-paths($nx of $np path(s) outside the firmware read's directory)"
fi
rb_local read local "E194's firmware gate, the record (E194.md A1): fwread-e194's read as committed, its comparison re-run, the gate's own reading, EQUAL to E69's" \
  bash $E/rb/fwgate_e194.sh record "$RB_REPO"
rb_has '^FWGATE-E194 RECORD EQUAL: ' || bad="$bad fwgate-record"
rb_local desk local "the preflight: dmcmd_audit on the session's files, no WRITE allowed" bash $E/preflight_e194.sh
rb_has '^dmcmd_audit: GO' || bad="$bad preflight"
for spec in "logs/selftest-run-e194.txt ^SELFTEST-RUN-E194.[0-9]+.of.[0-9]+.PASS" "logs/realpath-e194.txt ^REALPATH-E194.[0-9]+.of.[0-9]+.PASS" \
            "logs/dry-audit-e194.txt ^DRY-AUDIT-E194.[0-9]+.of.[0-9]+.COVERED" "logs/selftest-rest-e194.txt ^SELFTEST-REST-E194.[0-9]+.of.[0-9]+.PASS" \
            "logs/selftest-rb-e194.txt ^SELFTEST-RB-E194.[0-9]+.of.[0-9]+.PASS" "logs/selftest-wait-e194.txt ^SELFTEST-WAIT-E194.[0-9]+.of.[0-9]+.PASS" \
            "logs/selftest-quiet-e194.txt ^SELFTEST-QUIET-E194.[0-9]+.of.[0-9]+.PASS" "logs/parser-e194.txt ^PARSER-E194.[0-9]+.of.[0-9]+.PASS" \
            "logs/identity-e194.txt ^IDENTITY-E194.[0-9]+.of.[0-9]+.PASS" "logs/checks-e194.txt ^CHECKS-E194.[0-9]+.of.[0-9]+.PASS" \
            "logs/realbuild-e194.txt ^REALBUILD-E194.[0-9]+.of.[0-9]+.PASS" \
            "logs/dry-listing-e194.txt ^dry.listing:.[0-9]+.steps.listed,.0.exited.non-zero,.0.box.calls.beyond.aifoundry2$" "logs/dmcmd-audit-e194.txt ^dmcmd_audit:.GO" \
            "logs/selftest-fwgate-e194.txt ^SELFTEST-FWGATE-E194.[0-9]+.of.[0-9]+.PASS" \
            "logs/dry-listing-e194-v2.txt ^dry.listing:.[0-9]+.steps.listed,.0.exited.non-zero,.0.box.calls.beyond.aifoundry2$"; do
  set -- $spec
  rb_local read local "a desk test's log, as committed: $1" grep -cE "$2" "$E/$1"
  rb_has '^1$' || bad="$bad $(basename "$1" .txt)"
done
rb_local read local "HEAD after the checks" git -C "$RB_REPO" rev-parse HEAD
h1=$(rb_val '^([0-9a-f]{40})$')
[ -n "${RB_DRY:-}" ] || [ "$h0" = "$h1" ] || bad="$bad HEAD-moved"
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
echo "$(date '+%F %T %Z') step=$RB_STEP lists not pinned (reported):${unknown:- none}; E191's third-session folders left out of the never-run check (A1-8): $s3n${NAMES3:+ (${NAMES3# })}" >> "$RB_LOG"
rb_say "desk check v2: the window written today for E194; pulled under the lab-git lock, HEAD ${h1:0:12} descends from 46a16bd0, E194's registration ${reg:0:12}, its kit and its dated amendment A1, E191's registration and E189's registration and kit; the paths clean, HISTORY OK, the lists at their pinned counts and bytes (17; 1; 11; 3; 10; 55; 165; 17, 6; 86), the kit's ($(echo "$KITPIN" | cut -d: -f2)), the amendment's ($(echo "$AMENDPIN" | cut -d: -f2)) and the firmware read's ($(echo "$FWPIN" | cut -d: -f2)), E194.md and E189.md the registered and cited texts, lists not pinned (reported):${unknown:- none}; the harness re-made and at its sha256, PLANS SAME, the host check's lines, both self-checks, the plan and forecast re-made, the E59 self-test, NEVER RAN with E189's and both of E191's data folders left out, and E191's third-session folders at HEAD ($s3n${NAMES3:+:$NAMES3}); the only E194 data in any ref the firmware read of record (${FWCOMMIT:0:12}), FWGATE-E194 RECORD EQUAL; the preflight GO, the kit's and the amendment's desk tests' logs"
