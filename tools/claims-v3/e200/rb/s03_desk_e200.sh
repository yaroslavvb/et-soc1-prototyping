#!/usr/bin/env bash
# E200 (Q192, lane kit-e200, Mon 16 Nov 2026, before any E200 datum), the box step "step 2" (this file is s03), each sitting's desk check
# before any box step, on the desk (aifoundry2, which is also the box), in E197's step 2 form (tools/claims-v3/e197/rb/s03_desk_e197.sh,
# unchanged beside it):
#   - the window first: RB_OUT's window written today (Pacific) for E200 and a sitting (e200_window), or refused (10) before any call;
#   - the pull under the lab-git lock (e200_pull: RB_GITLOCK required; this step takes the lock itself for the pull alone, so it is NEVER
#     run inside that lock: a nested lockf or flock exits 75 and this step stops with 16);
#   - HEAD descends from 72514ce5 (GitHub main when E200 was registered); from E197's registration commit, found by its content (the
#     commit that added tools/claims-v3/e197/E197.md, whose e197 subtree reads da6c3e89...), and E197's kit commit (the one that added
#     tools/claims-v3/e197/KIT.md): E200 runs E197's registered session and builds E197's proposal; from E200's registration commit (the
#     one that added tools/claims-v3/e200/E200.md, whose e200 subtree reads c479c271...: the registration as fixed before the land, its
#     freeze line in section 0) and E200's kit commit (the one that added
#     tools/claims-v3/e200/KIT.md);
#   - E200's paths clean; the history check (rb/check_history_e200.py tree): additions only since 72514ce5 on E200's paths, nothing under
#     tools/claims-v3/e200 or tools/claims-v3/e197 changed since their registrations or kits, nothing untracked, no shadowing addition and
#     no shadowing file not committed in the folders the day's Python puts ahead of the standard library;
#   - THE LISTS E200 READS at their pinned counts AND their own pinned sha256 AND every entry OK, with no override: E197's registration's
#     (SHA256SUMS-e197-registration, 35) and E197's kit's (SHA256SUMS-e197-kit, 39), E200's registration's (SHA256SUMS-e200-registration,
#     17) and E200's E197 references (SHA256SUMS-e200-e197-refs, 19), and THE KIT'S OWN (SHA256SUMS-e200-kit; this step is outside it: a
#     file cannot hold the sha256 of a list that holds its own; the land file's anchor lines give this step's sha256 beside the list's);
#     every file with "SHA256SUMS" ANYWHERE in its name under tools/claims-v3/e200 found: one this step does not pin is REPORTED, never a
#     gate (a dated note's own list, say: the freeze line's, E200.md 0);
#   - harness-e200.json re-made (CHECK PASS) and every file of it at its sha256 in the lab clone (HARNESS OK); A FWGATE RECORD ADDED SINCE
#     THE KIT (the harness check names it) is read before fwgate trusts it: `fwgate.py check-records` (desk, no device) must read it OK
#     against its committed sources, and it must name at least one source (a record with none is no read of record), else 16 (fix-e200,
#     verify-e200's F6); the preflight (dmcmd_audit_v2 GO, no WRITE); the kit's desk tests' logs as committed, each with its PASS line once;
#   - THE FREEZE LINE: E200.md 0's freeze line, whole and on one line (the model session's sealed aifoundry2 forecast, sha256 2eba6ef4...,
#     #2.5.1.2.3, 01:28:51 PST Mon 16 Nov 2026, registered before the land: fix-e200, verify-e200's F1), checked and printed; a later dated
#     freeze-line note beside E200.md (E200.md 0 item 2) is printed when one exists (reported, never a gate);
#   - HEAD unchanged across all of it, else 16;
#   - NO E200 DATUM IN ANY REF: before sitting 1, no docs/reports/data/*e200* path in any ref; before sitting 2, none but sitting 1's own
#     data directory (*-e200-regfile-sitting-1-aifoundry2/); else 16. A gate stop's record (docs/reports/gate-stops/<day>-e200-regfile-
#     sitting-<n>-T<T0>-aifoundry2/) is no datum and is not read here. E197's data, if they land first, are reported, never a gate (E200.md
#     preamble: E200 is not blind to them then; nothing of E200 changes after an E197 datum unless a dated amendment says so).
# The load is read by the card lane before this step (`uptime` on aifoundry2); this step does not read it.
#
#   RB_GITLOCK=<the lab-git lock> bash tools/claims-v3/e200/rb/s03_desk_e200.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e200.sh"
rb_init s03_desk
e200_window
E=tools/claims-v3/e200
E7=tools/claims-v3/e197
PINS="tools/claims-v3/e197/SHA256SUMS-e197-registration:35:992a35e577617489d571f1af6e37f78b08e967d82e6529261ebf7db19e05ad95:top
tools/claims-v3/e197/SHA256SUMS-e197-kit:39:0719a97ffa91d4e440ba507b3642cf0b1b6fea1dcf156d3a1a471dfdd2d16963:top
tools/claims-v3/e200/SHA256SUMS-e200-registration:17:3e3e7d40c5a8713c5fbc94c87310f86f1aacfc765fb5597e3bb45c46f5155be7:top
tools/claims-v3/e200/SHA256SUMS-e200-e197-refs:19:ecbc56d9b5304e6b051ec37fee379d5cef538f997f0b545a8f89184667de7593:top"   # list:count:its own sha256:paths from
KITPIN=${RB_E200_KITPIN:-tools/claims-v3/e200/SHA256SUMS-e200-kit:44:78c27c42305d76a9da66c82996c270dda90aa97144578a44af099209c6a35b97:top}   # the kit's own list, at its count and its own bytes
[ "${RB_DESKTEST:-}" = 1 ] || KITPIN=tools/claims-v3/e200/SHA256SUMS-e200-kit:44:78c27c42305d76a9da66c82996c270dda90aa97144578a44af099209c6a35b97:top
bad=""
e200_pull || bad="$bad pull"
[ -z "${RB_DRY:-}" ] && [ "${RB_RC:-0}" -ne 0 ] && bad="$bad pull(rc $RB_RC; a nested lab-git lock exits 75)"
rb_local read local "HEAD before the checks" git -C "$RB_REPO" rev-parse HEAD
h0=$(rb_val '^([0-9a-f]{40})$')
rb_local read local "HEAD descends from $RB_E200_BASE (GitHub main when E200 was registered)" git -C "$RB_REPO" merge-base --is-ancestor "$RB_E200_BASE" HEAD || bad="$bad ancestry"
reg=""; kit=""; reg7=""; kit7=""
for what in e197-registration e197-kit registration kit; do
  case "$what" in
    e197-registration) f=$E7/E197.md; want=da6c3e89d6d91473643d869d6041e842b4708b89; dir=$E7 ;;
    e197-kit) f=$E7/KIT.md; want=""; dir=$E7 ;;
    registration) f=$E/E200.md; want=c479c271a261633b83a2bb690130c1419a34be2d; dir=$E ;;
    kit) f=$E/KIT.md; want=""; dir=$E ;;
  esac
  rb_local read local "the $what commit, by its content (the commit that added $f)" git -C "$RB_REPO" log --diff-filter=A --format=%H -- "$f"
  c=$(rb_val '^([0-9a-f]{40})$')
  [ -n "${RB_DRY:-}" ] && continue
  if [ -z "$c" ]; then bad="$bad $what(missing)"; continue; fi
  rb_local read local "the $what commit is an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$c" HEAD || bad="$bad $what-ancestry"
  if [ -n "$want" ]; then
    rb_local read local "the $what commit's subtree $dir" git -C "$RB_REPO" rev-parse "$c:$dir"
    rb_has "^$want\$" || bad="$bad $what-subtree"
  fi
  case "$what" in e197-registration) reg7=$c ;; e197-kit) kit7=$c ;; registration) reg=$c ;; kit) kit=$c ;; esac
done
rb_local read local "E200's paths clean" git -C "$RB_REPO" status --short $E $E7 tools/claims-v3/e194/e194_common.py tools/claims-v3/dmcmd_audit_v2.py \
  tools/claims-v3/dmcmd_table_v2.json tools/claims-v3/fwgate tools/claims-v3/q141k-runbook/k6 tools/claims-v3/q141k-runbook/v3.1
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
rb_local read local "the history check: additions only on E200's paths since $RB_E200_BASE and since the registrations and the kits (check_history_e200.py)" \
  /usr/bin/python3 -I -B $E/rb/check_history_e200.py tree --base "$RB_E200_BASE"
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || bad="$bad history"
paths=""; for spec in $PINS $KITPIN; do paths="$paths ${spec%%:*}"; done
rb_local read local "the own sha256 of the lists E200 reads (pinned)" shasum -a 256 $paths
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
rb_local desk local "harness-e200.json re-made" /usr/bin/python3 -I -B $E/harness_e200.py --check
rb_has '^CHECK PASS' || bad="$bad harness-rebuild"
added=""; [ -z "${RB_DRY:-}" ] && added=$(sed -nE 's/^CHECK PASS: .*; fwgate records added since the kit, synced and read by fwgate, not pinned: (.*)\)$/\1/p' "$RB_CAP" | head -n 1 | tr -d ',')
if [ -n "$added" ] || [ -n "${RB_DRY:-}" ]; then   # fix-e200 (verify-e200's F6): a fwgate record added since the kit, read before it is trusted
  rb_local read local "fwgate's records against their committed sources (fwgate.py check-records; desk, no device): each one added since the kit OK" \
    /usr/bin/python3 -I -B tools/claims-v3/fwgate/fwgate.py check-records
  for r in $added; do rb_has "^${r//./\\.}: OK " || bad="$bad fwgate-record($r: not OK against its sources)"; done
  files=""; for r in $added; do files="$files tools/claims-v3/fwgate/records/$r"; done
  [ -n "${RB_DRY:-}" ] && files=" tools/claims-v3/fwgate/records/<each-record-added-since-the-kit>"
  rb_local read local "each fwgate record added since the kit names a committed source (a record with none is no read of record)" grep -H -c '"path":' $files
  for r in $added; do grep -qE "/${r//./\\.}:[1-9][0-9]*\$" "$RB_CAP" || bad="$bad fwgate-record($r: no committed source)"; done
fi
rb_local desk local "every harness file at its sha256 in the lab clone" /usr/bin/python3 -I -B $E/harness_e200.py --box
rb_has '^HARNESS OK: ' || bad="$bad harness"
rb_local desk local "the preflight: dmcmd_audit_v2 on the session's files, no WRITE allowed" bash $E/preflight_e200.sh
rb_has '^dmcmd_audit: GO' || bad="$bad preflight"
for spec in "logs/desktest-realpath-e200.txt ^DESKTEST-REALPATH-E200.[0-9]+.of.[0-9]+.PASS" "logs/selftest-rb-e200.txt ^SELFTEST-RB-E200.[0-9]+.of.[0-9]+.PASS" \
            "logs/selftest-rest-e200.txt ^SELFTEST-REST-E200.[0-9]+.of.[0-9]+.PASS" "logs/realbytes-e200.txt ^REALBYTES-E200.[0-9]+.of.[0-9]+.PASS" \
            "logs/checks-e200.txt ^CHECKS-E200.[0-9]+.of.[0-9]+.PASS" "logs/selftest-fwgate-e200.txt ^SELFTEST-FWGATE-E200.[0-9]+.of.[0-9]+.PASS" \
            "logs/dry-listing-e200.txt ^dry.listing:.[0-9]+.steps.listed,.0.exited.non-zero,.0.box.calls.beyond.aifoundry2$" "logs/dmcmd-audit-e200.txt ^dmcmd_audit:.GO"; do
  set -- $spec
  rb_local read local "a desk test's log, as committed: $1" grep -cE "$2" "$E/$1"
  rb_has '^1$' || bad="$bad $(basename "$1" .txt)"
done
F1=2eba6ef4b60241674628dde125273db4547b0ba17dd6d5a3e30935c7c6e89733   # E200.md 0's freeze line: the sealed aifoundry2 forecast (#2.5.1.2.3, 01:28:51 PST Mon 16 Nov 2026)
FLINE="1. \`E200 sealed aifoundry2 forecast (the model session's, X02 on aifoundry2 card 0, with 800, 700 and 600 MHz columns as read), posted as #2.5.1.2.3 in the owner's coordination thread at 01:28:51 PST Mon 16 Nov 2026, frozen before any datum of E200, sha256 $F1\`"
rb_local read local "E200's freeze line in E200.md 0, whole and on one line (the sealed aifoundry2 forecast, registered before the land)" grep -c -F -x -e "$FLINE" $E/E200.md
[ -z "${RB_DRY:-}" ] && { [ "$(rb_val '^([0-9]+)$')" = 1 ] || bad="$bad freeze-line"; }
rb_local read local "a later dated freeze-line note beside E200.md (E200.md 0 item 2; reported, never a gate)" find "$E" -maxdepth 1 -type f -iname '*freeze*'
later="none"; [ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && later=$(sed 's#.*/##' "$RB_CAP" | tr '\n' ' ' | sed 's/ $//')
rb_local read local "HEAD after the checks" git -C "$RB_REPO" rev-parse HEAD
h1=$(rb_val '^([0-9a-f]{40})$')
[ -n "${RB_DRY:-}" ] || [ "$h0" = "$h1" ] || bad="$bad HEAD-moved"
rb_local read local "E200 data in any ref (before sitting 1: none; before sitting 2: sitting 1's own directory only)" \
  git -C "$RB_REPO" log --all --name-only --format= -- 'docs/reports/data/*e200*'
nd=0; other=0
if [ -z "${RB_DRY:-}" ]; then
  nd=$(sort -u "$RB_CAP" | grep -c .)
  other=$(sort -u "$RB_CAP" | grep . | grep -vc -- '-e200-regfile-sitting-1-aifoundry2/')
  if [ "$E200_SIT" = 1 ] && [ "$nd" -gt 0 ]; then bad="$bad e200-datum($nd paths before sitting 1)"; fi
  if [ "$E200_SIT" = 2 ] && [ "$other" -gt 0 ]; then bad="$bad e200-datum($other paths besides sitting 1's before sitting 2)"; fi
fi
rb_local read local "E197 data in any ref (reported, never a gate: E200 is not blind to E197's data once they land, E200.md's preamble)" \
  git -C "$RB_REPO" log --all --name-only --format= -- 'docs/reports/data/*e197*'
n7=0; [ -z "${RB_DRY:-}" ] && n7=$(sort -u "$RB_CAP" | grep -c .)
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
echo "$(date '+%F %T %Z') step=$RB_STEP sitting=$E200_SIT lists not pinned (reported):${unknown:- none}; E197 data paths in any ref (reported): $n7; the freeze line $F1 (E200.md 0); later freeze-line notes: $later; fwgate records added since the kit: ${added:-none}" >> "$RB_LOG"
rb_say "desk check for sitting $E200_SIT: the window written today for E200; pulled under the lab-git lock, HEAD ${h1:0:12} descends from $RB_E200_BASE, E197's registration ${reg7:0:12} (subtree da6c3e89) and kit ${kit7:0:12}, E200's registration ${reg:0:12} (subtree c479c271) and kit ${kit:0:12}; the paths clean, HISTORY OK, the lists at their pinned counts and bytes (35, 39, 17, 19; the kit's $(echo "$KITPIN" | cut -d: -f2)), lists not pinned (reported):${unknown:- none}; the harness re-made and at its sha256 (fwgate records added since the kit, each read OK against its sources: ${added:-none}), the preflight GO, the kit's desk tests' logs; the freeze line $F1 (E200.md 0), later notes: $later; E200 data paths in any ref: $nd (sitting 1's: $((nd - other))); E197 data paths (reported): $n7"
