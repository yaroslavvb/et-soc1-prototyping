#!/usr/bin/env bash
# E210 (Q202, lane kit-e210, Tue 17 Nov 2026, before any E210 datum; ported from kit-e207's E207 kit, its local commit 4bd6e38c), the box step
# "step 2" (this file is s03; STEP 2, OUTSIDE THE KIT'S LIST: it pins the list by count and bytes, so it cannot be in it): the desk check before
# any box step, on the desk only (aifoundry2). E206's step 2 (tools/claims-v3/e206/rb/s03_desk_e206.sh, landed in 906699ea) for E210:
#   - the window first (e210_window: today, E210, arm A), or refused (10) before any call; the pull under the lab-git lock (e210_pull; never
#     run inside it);
#   - HEAD descends from E210's registration (found by its content: the commit that added E210.md, its tools/claims-v3/e210 subtree
#     adef3701...) AND from the kit commit (found by its content: the commit that added KIT.md);
#   - E210's paths clean (with every path the session, the scorer and the frozen forecasts read: MM1-v1, rgm136, the kinds tiles, E206's,
#     E208's and E65's data the forecast reads); the history check (rb/check_history_e210.py): additions only under tools/claims-v3/e210 since
#     the registration (and a sealed-forecast note under tools/claims-v3/sealed-e210), no shadowing addition, nothing modified or untracked on
#     E210's run paths;
#   - EVERY LIST E210 READS at its pinned count AND its own pinned sha256 AND every entry OK: the registration's (SHA256SUMS-e210-registration,
#     523, anchor line 3's 4219474f...) and the kit's (SHA256SUMS-e210-kit, KITPIN below, set at the kit's commit); MM1-v1's folder list
#     (tools/matmul/mm1/v1/SHA256SUMS, 77, f77084ef...: forecast_e210.py calls MM1-v1 unchanged) every entry OK; any other file with SHA256SUMS
#     in its name under tools/claims-v3/e210 is REPORTED, never a gate;
#   - harness-e210.json re-made (CHECK PASS) and every file of it at its sha256 in the lab clone (HARNESS OK); the two modules' self-checks;
#     the registration's own checks (points_e210.py and forecast_e210.py <top> --check and desk/kernel_e210.py --check: PASS; the frozen
#     scorer's stand-in self-test, rc 0 and its two outputs byte-identical to the committed selftest-standins-e210.json and .txt); the preflight
#     (dmcmd_audit_v2 GO, no WRITE); the kit's desk tests' logs as committed, each with its PASS line once, and the dry listing's last line;
#   - HEAD unchanged across all of it, else 16;
#   - NO E210 DATUM in any ref (docs/reports/data/*e210*): 16 if one exists (E210 has run); a gate stop's record (docs/reports/gate-stops/
#     *e210*) and a sealed-forecast note (tools/claims-v3/sealed-e210/) REPORTED.
#   RB_GITLOCK=<the lab-git lock> bash tools/claims-v3/e210/rb/s03_desk_e210.sh A
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e210.sh"
rb_init s03_desk
e210_arm "${1:-}"
e210_window
E=tools/claims-v3/e210
REGPIN=tools/claims-v3/e210/SHA256SUMS-e210-registration:523:4219474f98341212572a1ae2d14601eb664e55ef1f340c2d7d9f60610cba29c4:top
KITPIN=tools/claims-v3/e210/SHA256SUMS-e210-kit:45:199a96b3de78fdd12755117b00ece632e92e457f36d5af5690649af39627c8f8:top   # the kit's own list, at its count and its own bytes (set at the kit's commit)
V1PIN=tools/matmul/mm1/v1/SHA256SUMS:77:f77084ef6342964eafbea14d104ffc4dd324e83ee14cc4241158840a51ae468f:dir   # MM1-v1's folder as landed (25d2e74e; E210.md 7)
bad=""
e210_pull || bad="$bad pull"
[ -z "${RB_DRY:-}" ] && [ "${RB_RC:-0}" -ne 0 ] && bad="$bad pull(rc $RB_RC; a nested lab-git lock exits 75)"
rb_local read local "HEAD before the checks" git -C "$RB_REPO" rev-parse HEAD
h0=$(rb_val '^([0-9a-f]{40})$')
rb_local read local "E210's registration, by its content (the commit that added E210.md)" git -C "$RB_REPO" log --diff-filter=A --format=%H -- $E/E210.md
reg=$(rb_val '^([0-9a-f]{40})$')
rb_local read local "E210's kit commit, by its content (the commit that added KIT.md)" git -C "$RB_REPO" log --diff-filter=A --format=%H -- $E/KIT.md
kit=$(rb_val '^([0-9a-f]{40})$')
if [ -z "${RB_DRY:-}" ]; then
  if [ -z "$reg" ]; then bad="$bad registration(missing)"; else
    rb_local read local "the registration's e210 subtree" git -C "$RB_REPO" rev-parse "$reg:$E"
    rb_has "^$E210_REG_SUBTREE\$" || bad="$bad registration-subtree"
    rb_local read local "the registration is an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$reg" HEAD || bad="$bad registration-ancestry"
  fi
  if [ -z "$kit" ]; then bad="$bad kit(missing)"; else
    rb_local read local "the kit commit is an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$kit" HEAD || bad="$bad kit-ancestry"
  fi
fi
rb_local read local "E210's paths clean" git -C "$RB_REPO" status --short $E tools/claims-v3/sealed-e210 tools/matmul/mm1/v1 tools/claims-v3/e136/rgm136 \
  tools/claims-v3/kinds/tiles tools/claims-v3/kinds/kinds.json tools/claims-v3/q141k-runbook tools/claims-v3/e128 tools/claims-v3/e206 \
  tools/claims-v3/dmcmd_audit_v2.py tools/claims-v3/dmcmd_table_v2.json docs/reports/data/2026-10-26-e65-bit-prices-hart-ladder \
  docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3 docs/reports/data/2026-11-16-e208-mmsweep-a1c1-S1 docs/reports/data/2026-11-16-e208-mmsweep-a1c1-S2
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
rb_local read local "the history check: additions only under $E since the registration, no shadowing addition (check_history_e210.py)" \
  /usr/bin/python3 -I -B $E/rb/check_history_e210.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || bad="$bad history"
paths=""; for spec in $REGPIN $KITPIN $V1PIN; do paths="$paths ${spec%%:*}"; done
rb_local read local "the own sha256 of the lists E210 reads (pinned)" sha256sum $paths
own=$RB_CAP
for spec in $REGPIN $KITPIN $V1PIN; do
  IFS=: read -r l pin hpin form <<EOF2
$spec
EOF2
  if [ "$form" = dir ]; then     # a folder's own list: its paths beside it (MM1-v1's SHA256SUMS)
    RB_CWD="$RB_REPO/$(dirname "$l")" rb_local read local "the list $l (pinned at $pin entries and its own sha256)" sha256sum -c "$(basename "$l")"
  else                          # paths from the repository's top
    RB_CWD="$RB_REPO" rb_local read local "the list $l (pinned at $pin entries and its own sha256)" sha256sum -c "$l"
  fi
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
rb_local desk local "harness-e210.json re-made" /usr/bin/python3 -I -B $E/check_e210.py --check
rb_has '^CHECK PASS' || bad="$bad harness-rebuild"
rb_local desk local "every harness file at its sha256 in the lab clone" /usr/bin/python3 -I -B $E/check_e210.py --box
rb_has '^HARNESS OK: ' || bad="$bad harness"
rb_local read local "the common module's self-check (the arm, the order, the opening, the probe's rule, the stops and the latch reading, the gate, the argv, the tiles, the records)" /usr/bin/python3 -I -B $E/e210_common.py
rb_has '^E210-COMMON SELF-CHECK PASS' || bad="$bad common"
rb_local read local "the identity module's self-check" /usr/bin/python3 -I -B $E/e210_ident.py
rb_has '^E210-IDENT SELF-CHECK PASS' || bad="$bad ident"
for s in points_e210.py forecast_e210.py; do
  rb_local desk local "the registration's $s <top> --check (recomputed from every pinned input, byte for byte)" /usr/bin/python3 -I -B $E/$s "$RB_REPO" --check
  rb_has "^$(basename "$s" .py) --check PASS" || bad="$bad $(basename "$s" .py)"
done
rb_local desk local "the registration's desk/kernel_e210.py --check (rgm136's sources re-hashed)" /usr/bin/python3 -I -B $E/desk/kernel_e210.py --check
rb_has '^kernel_e210 --check: .* equal to kernel-e210.json: True' || bad="$bad kernel_e210"
same() {  # same <rc> <made file> <committed file> [<made> <committed>]: rc 0 and every pair byte-identical (never false in a dry listing)
  [ -n "${RB_DRY:-}" ] && return 0
  local rc=$1; shift
  [ "$rc" -eq 0 ] || return 1
  while [ $# -ge 2 ]; do cmp -s "$1" "$RB_REPO/$2" || return 1; shift 2; done
  return 0
}
[ -n "${RB_DRY:-}" ] || mkdir -p "$RB_OUT/scorer-selftest"
rb_local desk local "the frozen scorer's stand-in self-test (it refuses, 4, if a frozen file changed)" /usr/bin/python3 -I -B $E/score_e210.py --selftest "$RB_OUT/scorer-selftest"
same "$RB_RC" "$RB_OUT/scorer-selftest/selftest-standins-e210.json" "$E/selftest-standins-e210.json" "$RB_OUT/scorer-selftest/selftest-standins-e210.txt" \
  "$E/selftest-standins-e210.txt" || bad="$bad scorer-selftest"
rb_local desk local "the preflight: dmcmd_audit_v2 on the session's files, no WRITE allowed" bash $E/preflight_e210.sh
rb_has '^dmcmd_audit: GO' || bad="$bad preflight"
for spec in "logs/selftest-run-e210.txt ^SELFTEST-RUN-E210.[0-9]+.of.[0-9]+.PASS$" "logs/realpath-e210.txt ^REALPATH-E210.[0-9]+.of.[0-9]+.PASS$" \
            "logs/realbytes-e210.txt ^REALBYTES-E210.[0-9]+.of.[0-9]+.PASS$" "logs/desktest-build-e210.txt ^DESKTEST-BUILD-E210.[0-9]+.of.[0-9]+.PASS$" \
            "logs/selftest-rb-e210.txt ^SELFTEST-RB-E210.[0-9]+.of.[0-9]+.PASS$" \
            "logs/dry-listing-e210.txt ^dry.listing:.[0-9]+.steps.listed,.0.exited.non-zero,.0.box.calls$" "logs/dmcmd-audit-e210.txt ^dmcmd_audit:.GO"; do
  set -- $spec
  rb_local read local "a desk test's log, as committed: $1" grep -cE "$2" "$E/$1"
  rb_has '^1$' || bad="$bad $(basename "$1" .txt)"
done
rb_local read local "HEAD after the checks" git -C "$RB_REPO" rev-parse HEAD
h1=$(rb_val '^([0-9a-f]{40})$')
[ -n "${RB_DRY:-}" ] || [ "$h0" = "$h1" ] || bad="$bad HEAD-moved"
rb_local read local "E210 data in any ref (want none before its session)" git -C "$RB_REPO" log --all --oneline -- 'docs/reports/data/*e210*'
nd=0; [ -z "${RB_DRY:-}" ] && nd=$(grep -c . "$RB_CAP")
[ "$nd" -eq 0 ] || bad="$bad E210-has-data($nd commit(s))"
rb_local read local "E210 gate-stop records in any ref (REPORTED)" git -C "$RB_REPO" log --all --oneline -- 'docs/reports/gate-stops/*e210*'
no=0; [ -z "${RB_DRY:-}" ] && no=$(grep -c . "$RB_CAP")
rb_local read local "a sealed-forecast note for E210 (REPORTED; E210.md 0)" git -C "$RB_REPO" log --oneline -- tools/claims-v3/sealed-e210
ns=0; [ -z "${RB_DRY:-}" ] && ns=$(grep -c . "$RB_CAP")
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
echo "$(date '+%F %T %Z') step=$RB_STEP arm=$ARM lists not pinned (reported):${unknown:- none}; E210 gate-stop commits: $no; sealed-forecast note commits: $ns" >> "$RB_LOG"
rb_say "desk check: the window written today for E210; pulled under the lab-git lock, HEAD ${h1:0:12} descends from the registration ${reg:0:12} (subtree ${E210_REG_SUBTREE:0:8}) and the kit ${kit:0:12}, the paths clean, HISTORY OK, the lists at their pinned counts and bytes (523; the kit's $(echo "$KITPIN" | cut -d: -f2); MM1-v1's 77), lists not pinned (reported):${unknown:- none}; the harness re-made and at its sha256, both self-checks, the registration's checks, the scorer's self-test byte-identical, the preflight GO, the desk tests' logs; E210 data commits: $nd; gate-stop commits (reported): $no; sealed-forecast note commits (reported): $ns"
