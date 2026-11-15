#!/usr/bin/env bash
# E192 (Q176, lane kit-e192, Sat 14 Nov 2026, before any E192 datum), the box step "step 2" (this file is s03): the desk check before any
# box step, on the desk only (aifoundry2, Linux, or a Mac), in E189's step 2 form (tools/claims-v3/e189/rb/s03_desk_e189.sh):
#   - the window first: RB_OUT's window written today (Pacific) for E192 (e192_window), or refused (10) before any call;
#   - the pull under the lab-git lock (e192_pull: RB_GITLOCK required; this step takes the lock itself for the pull alone, so it is NEVER
#     run inside that lock: a nested flock or lockf exits 75 and this step stops with 16);
#   - E192's registration commit found by its content (the commit that added tools/claims-v3/e192/E192.md, whose e192 subtree reads
#     c78351f9...: the registration with both freeze lines, before any datum), an ancestor of HEAD;
#   - E192's paths clean; THE HISTORY CHECK (rb/check_history_e192.py tree): nothing under tools/claims-v3/e192 changed or went since the
#     registration and since the kit, additions only on the files E192's day reads, nothing untracked, no shadowing addition and no
#     shadowing file not committed in the folders the day's Python puts ahead of the standard library;
#   - EVERY LIST at its pinned count AND its own pinned sha256 AND every entry OK, with no override: the registration's (30, dd0a8963...)
#     and THE KIT'S OWN LIST (KITPIN below; this step is outside it: a file cannot hold the sha256 of a list that holds its own; the land
#     file and KIT.md give this step's sha256 beside the list's), and the shared list (SHA256SUMS-e192-shared, 6, pinned by the kit's
#     list); every file with "SHA256SUMS" anywhere in its name under tools/claims-v3/e192 found: one this step does not pin is
#     REPORTED, never a gate;
#   - both freeze lines in E192.md (fa385703... and 49bec965..., each on exactly one line);
#   - NO E192 DATUM IN ANY REF (no docs/reports/data/*e192* path in any commit or any ref's tip): a datum before the session is a stop;
#   - the preflight (preflight_e192.sh: the plain chain GO with the stock table; the per-sensor chain's verdict reported);
#   - the kit's desk tests' logs as committed, each with its PASS line;
#   - HEAD unchanged across all of it, else 16.
# The card lane reads `uptime` before this step (aifoundry2's load rule); this step does not read it.
#   RB_GITLOCK=<the lab-git lock> bash tools/claims-v3/e192/rb/s03_desk_e192.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e192.sh"
rb_init s03_desk
e192_window
E=tools/claims-v3/e192
REGPIN=tools/claims-v3/e192/SHA256SUMS-e192-registration:30:dd0a89635800818cd17c429be2d02c9710a434364f4196e6fd1a0f8e2dd74326:top
KITPIN=tools/claims-v3/e192/SHA256SUMS-e192-kit:35:c89e91b967ae19dd238c6863ddb485e21d6e978fabf2224d34edffd1df04f09f:top   # the kit's own list, at its count and its own bytes
SHAREDN=6
F1=fa385703ee5b385a2bb54834644d5e34a999ddbb2fd8a2eeeb2ead83ae9cc461
F2=49bec965bf6921ba40aa1eb22bd364a41062893ff3b8109be14116ee44e49b74
bad=""
e192_pull || bad="$bad pull"
[ -z "${RB_DRY:-}" ] && [ "${RB_RC:-0}" -ne 0 ] && bad="$bad pull(rc $RB_RC; a nested lab-git lock exits 75)"
rb_local read local "HEAD before the checks" git -C "$RB_REPO" rev-parse HEAD
h0=$(rb_val '^([0-9a-f]{40})$')
rb_local read local "E192's registration commit, by its content (the commit that added E192.md)" git -C "$RB_REPO" log --diff-filter=A --format=%H -- $E/E192.md
reg=$(rb_val '^([0-9a-f]{40})$')
if [ -z "${RB_DRY:-}" ]; then
  [ -n "$reg" ] || bad="$bad registration-not-found"
  if [ -n "$reg" ]; then
    rb_local read local "the registration commit is an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$reg" HEAD || bad="$bad registration-ancestry"
    [ "$RB_RC" -eq 0 ] || bad="$bad registration-ancestry"
    rb_local read local "the registration's e192 subtree" git -C "$RB_REPO" rev-parse "$reg:$E"
    [ "$(rb_val '^([0-9a-f]{40})$')" = "$E192_REG_SUBTREE" ] || bad="$bad registration-subtree"
  fi
else
  rb_local read local "the registration commit is an ancestor of HEAD, and its e192 subtree reads $E192_REG_SUBTREE" git -C "$RB_REPO" rev-parse "<reg>:$E"
fi
rb_local read local "E192's paths clean" git -C "$RB_REPO" status --short --untracked-files=all -- $E
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad paths-not-clean"
rb_local read local "the history check (check_history_e192.py)" "$RB_PY" -I -B $E/rb/check_history_e192.py tree
rb_has '^HISTORY OK' || bad="$bad history"
paths=""; for spec in $REGPIN $KITPIN; do paths="$paths ${spec%%:*}"; done
rb_local read local "the own sha256 of the lists E192 reads (pinned)" sha256sum $paths
OWNCAP=$RB_CAP
for spec in $REGPIN $KITPIN; do
  l=${spec%%:*}; rest=${spec#*:}; pin=${rest%%:*}; rest=${rest#*:}; own=${rest%%:*}
  if [ -z "${RB_DRY:-}" ]; then
    [ "$(grep -E "^[0-9a-f]{64}  $l\$" "$OWNCAP" | cut -d' ' -f1)" = "$own" ] || bad="$bad $(basename "$l")-sha256"
    [ "$(grep -c . "$RB_REPO/$l" 2>/dev/null)" = "$pin" ] || bad="$bad $(basename "$l")-count"
  fi
  rb_local read local "the list $(basename "$l") (pinned at $pin entries and its own sha256), every entry" sha256sum -c "$l"
  [ -z "${RB_DRY:-}" ] && { [ "$RB_RC" -eq 0 ] && [ "$(grep -c ': OK$' "$RB_CAP")" = "$pin" ] || bad="$bad $(basename "$l")-entries"; }
done
rb_local read local "the shared list (pinned by the kit's list), every entry" sha256sum -c $E/SHA256SUMS-e192-shared
[ -z "${RB_DRY:-}" ] && { [ "$RB_RC" -eq 0 ] && [ "$(grep -c ': OK$' "$RB_CAP")" = "$SHAREDN" ] || bad="$bad shared-list"; }
rb_local read local "every file with SHA256SUMS anywhere in its name under $E" find "$E" -name '*SHA256SUMS*' -type f
unknown=""
if [ -z "${RB_DRY:-}" ]; then
  for f in $(cat "$RB_CAP"); do
    case "$f" in */SHA256SUMS-e192-registration|*/SHA256SUMS-e192-kit|*/SHA256SUMS-e192-shared) continue ;; esac
    case "$f" in tools/claims-v3/e192/*) ;; *) continue ;; esac
    unknown="$unknown $(basename "$f")"
    rb_local read local "a list step 2 does not pin: $(basename "$f") (REPORTED, never a gate)" sha256sum -c "$f"
  done
fi
rb_local read local "the two freeze lines in E192.md, each on one line" grep -c -e "$F1" $E/E192.md
[ -z "${RB_DRY:-}" ] && { [ "$(rb_val '^([0-9]+)$')" = 1 ] || bad="$bad freeze-line-1"; }
rb_local read local "the second freeze line" grep -c -e "$F2" $E/E192.md
[ -z "${RB_DRY:-}" ] && { [ "$(rb_val '^([0-9]+)$')" = 1 ] || bad="$bad freeze-line-2"; }
rb_local read local "no E192 datum in any commit of any ref" git -C "$RB_REPO" log --all --oneline -- 'docs/reports/data/*e192*'
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad E192-datum-in-a-ref"
rb_local read local "no E192 datum at any ref's tip, nor in any commit (check_history_e192.py nodatum)" "$RB_PY" -I -B $E/rb/check_history_e192.py nodatum
[ -z "${RB_DRY:-}" ] && { rb_has '^NO-DATUM OK' || bad="$bad E192-datum-at-a-tip"; }
rb_local desk local "the preflight: dmcmd_audit on the session's files, no WRITE allowed (two tables)" bash $E/preflight_e192.sh
rb_has '^PLAIN-CHAIN: GO' || bad="$bad preflight"
pv=$(rb_val '^PVT-CHAIN: ([A-Z-]+).*$')
for spec in "desktest-realpath-e192.txt:^DESKTEST-REALPATH-E192 ([0-9]+) of \\1 PASS\$" "selftest-rb-e192.txt:^SELFTEST-RB-E192 ([0-9]+) of \\1 PASS\$" \
            "selftest-rest-e192.txt:^SELFTEST-REST-E192 ([0-9]+) of \\1 PASS\$" "dry-listing-e192.txt:^dry listing: .* 0 box calls\$" \
            "dmcmd-audit-e192.txt:^PLAIN-CHAIN: GO"; do
  f=${spec%%:*}; pat=${spec#*:}
  rb_local read local "a desk test's log, as committed: $f" grep -cE "$pat" "$E/logs/$f"
  [ -z "${RB_DRY:-}" ] && { [ "$(rb_val '^([0-9]+)$')" = 1 ] || bad="$bad log-$f"; }
done
rb_local read local "HEAD after the checks" git -C "$RB_REPO" rev-parse HEAD
h1=$(rb_val '^([0-9a-f]{40})$')
[ -z "${RB_DRY:-}" ] && [ "$h0" != "$h1" ] && bad="$bad HEAD-moved"
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
rb_say "desk check: the window written today for E192; pulled under the lab-git lock; HEAD ${h1:0:12} descends from the registration ${reg:0:12} (subtree ${E192_REG_SUBTREE:0:8}); the paths clean; HISTORY OK; the lists at their pinned counts and bytes (30; the kit's $(echo "$KITPIN" | cut -d: -f2); the shared $SHAREDN), lists not pinned (reported):${unknown:- none}; both freeze lines; no E192 datum in any ref; the preflight's plain chain GO (the per-sensor chain ${pv:-?}); the kit's desk tests' logs"
exit 0
