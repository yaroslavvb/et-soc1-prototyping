#!/usr/bin/env bash
# E196 (Q185, lane kit-e196, Sun 15 Nov 2026, PST, before any E196 datum), the box step "step 2" (this file is s03): the desk check before any
# box step, on the desk only (aifoundry2, Linux), in E192's step 2 form (tools/claims-v3/e192/rb/s03_desk_e192.sh):
#   - the window first: RB_OUT's window written today (Pacific) for E196 (e196_window), or refused (10) before any call;
#   - the pull under the lab-git lock (e196_pull: RB_GITLOCK required; this step takes the lock itself for the pull alone, so it is NEVER
#     run inside that lock: a nested flock or lockf exits 75 and this step stops with 16);
#   - E196's registration commit found by its content (the commit that added tools/claims-v3/e196/E196.md, whose e196 subtree reads
#     6f692709...: the registration with its freeze line, before any datum), an ancestor of HEAD;
#   - E196's paths clean; THE HISTORY CHECK (rb/check_history_e196.py tree): nothing under tools/claims-v3/e196 changed or went since the
#     registration and since the kit, additions only on the files E196's day reads, nothing untracked, no shadow in the folders the day's
#     Python puts ahead of the standard library;
#   - EVERY LIST at its pinned count AND its own pinned sha256 AND every entry OK, with no override: the registration's (49, 467ede78...)
#     and THE KIT'S OWN LIST (KITPIN below; this step is outside it: a file cannot hold the sha256 of a list that holds its own; the land
#     file and KIT.md give this step's sha256 beside the list's), and the shared list (SHA256SUMS-e196-shared, 17, pinned by the kit's
#     list); every file with "SHA256SUMS" anywhere in its name under tools/claims-v3/e196 found: one this step does not pin is REPORTED,
#     never a gate;
#   - the freeze line in E196.md (5c5acc16..., on exactly one line);
#   - NO E196 DATUM IN ANY REF (no docs/reports/data/*e196* path in any commit or any ref's tip): a datum before the session is a stop;
#   - the preflight (preflight_e196.sh: dmcmd_audit GO, the stock table, no --allow);
#   - the kit's desk tests' logs as committed, each with its PASS line;
#   - HEAD unchanged across all of it, else 16.
# The card lane reads `uptime` before this step (aifoundry2's load rule) and wraps it in THE ONE-LAB RULE (W/onelab.sh desk/undesk);
# this step does not read either.
#   RB_GITLOCK=<the lab-git lock> bash tools/claims-v3/e196/rb/s03_desk_e196.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e196.sh"
rb_init s03_desk
e196_window
E=tools/claims-v3/e196
REGPIN=tools/claims-v3/e196/SHA256SUMS-e196-registration:49:467ede7827f5ed33df6c883c9641caccb1e10ed78f88fbadc322a15a90137ce5:top
KITPIN=tools/claims-v3/e196/SHA256SUMS-e196-kit:46:3b8f8f38eeb08acfbc35cdb600b37743f0dc46ab1ec7c766fc843803fc356f7d:top   # the kit's own list, at its count and its own bytes
SHAREDN=17
F1=5c5acc1622e526aa20917a646a077763a630468ca2435ba3c05511408b148aba
bad=""
e196_pull || bad="$bad pull"
[ -z "${RB_DRY:-}" ] && [ "${RB_RC:-0}" -ne 0 ] && bad="$bad pull(rc $RB_RC; a nested lab-git lock exits 75)"
rb_local read local "HEAD before the checks" git -C "$RB_REPO" rev-parse HEAD
h0=$(rb_val '^([0-9a-f]{40})$')
rb_local read local "E196's registration commit, by its content (the commit that added E196.md)" git -C "$RB_REPO" log --diff-filter=A --format=%H -- $E/E196.md
reg=$(rb_val '^([0-9a-f]{40})$')
if [ -z "${RB_DRY:-}" ]; then
  [ -n "$reg" ] || bad="$bad registration-not-found"
  if [ -n "$reg" ]; then
    rb_local read local "the registration commit is an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$reg" HEAD || bad="$bad registration-ancestry"
    [ "$RB_RC" -eq 0 ] || bad="$bad registration-ancestry"
    rb_local read local "the registration's e196 subtree" git -C "$RB_REPO" rev-parse "$reg:$E"
    [ "$(rb_val '^([0-9a-f]{40})$')" = "$E196_REG_SUBTREE" ] || bad="$bad registration-subtree"
  fi
else
  rb_local read local "the registration commit is an ancestor of HEAD, and its e196 subtree reads $E196_REG_SUBTREE" git -C "$RB_REPO" rev-parse "<reg>:$E"
fi
rb_local read local "E196's paths clean" git -C "$RB_REPO" status --short --untracked-files=all -- $E
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad paths-not-clean"
rb_local read local "the history check (check_history_e196.py)" "$RB_PY" -I -B $E/rb/check_history_e196.py tree
rb_has '^HISTORY OK' || bad="$bad history"
paths=""; for spec in $REGPIN $KITPIN; do paths="$paths ${spec%%:*}"; done
rb_local read local "the own sha256 of the lists E196 reads (pinned)" sha256sum $paths
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
rb_local read local "the shared list (pinned by the kit's list), every entry" sha256sum -c $E/SHA256SUMS-e196-shared
[ -z "${RB_DRY:-}" ] && { [ "$RB_RC" -eq 0 ] && [ "$(grep -c ': OK$' "$RB_CAP")" = "$SHAREDN" ] || bad="$bad shared-list"; }
rb_local read local "every file with SHA256SUMS anywhere in its name under $E" find "$E" -name '*SHA256SUMS*' -type f
unknown=""
if [ -z "${RB_DRY:-}" ]; then
  for f in $(cat "$RB_CAP"); do
    case "$f" in */SHA256SUMS-e196-registration|*/SHA256SUMS-e196-kit|*/SHA256SUMS-e196-shared) continue ;; esac
    case "$f" in tools/claims-v3/e196/*) ;; *) continue ;; esac
    unknown="$unknown $(basename "$f")"
    rb_local read local "a list step 2 does not pin: $(basename "$f") (REPORTED, never a gate)" sha256sum -c "$f"
  done
fi
rb_local read local "the freeze line in E196.md, on one line" grep -c -e "$F1" $E/E196.md
[ -z "${RB_DRY:-}" ] && { [ "$(rb_val '^([0-9]+)$')" = 1 ] || bad="$bad freeze-line"; }
rb_local read local "no E196 datum in any commit of any ref" git -C "$RB_REPO" log --all --oneline -- 'docs/reports/data/*e196*'
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad E196-datum-in-a-ref"
rb_local read local "no E196 datum at any ref's tip, nor in any commit (check_history_e196.py nodatum)" "$RB_PY" -I -B $E/rb/check_history_e196.py nodatum
[ -z "${RB_DRY:-}" ] && { rb_has '^NO-DATUM OK' || bad="$bad E196-datum-at-a-tip"; }
rb_local desk local "the preflight: dmcmd_audit on the session's files, no WRITE allowed (the stock table)" bash $E/preflight_e196.sh
rb_has '^E196-PREFLIGHT: GO' || bad="$bad preflight"
for spec in "desktest-realpath-e196.txt:^DESKTEST-REALPATH-E196 ([0-9]+) of \\1 PASS\$" "selftest-rb-e196.txt:^SELFTEST-RB-E196 ([0-9]+) of \\1 PASS\$" \
            "selftest-rest-e196.txt:^SELFTEST-REST-E196 ([0-9]+) of \\1 PASS\$" "realbytes-e196.txt:^REALBYTES-E196 ([0-9]+) of \\1 PASS\$" \
            "dry-listing-e196.txt:^dry listing: .* 0 box calls\$" "dmcmd-audit-e196.txt:^E196-PREFLIGHT: GO"; do
  f=${spec%%:*}; pat=${spec#*:}
  rb_local read local "a desk test's log, as committed: $f" grep -cE "$pat" "$E/logs/$f"
  [ -z "${RB_DRY:-}" ] && { [ "$(rb_val '^([0-9]+)$')" = 1 ] || bad="$bad log-$f"; }
done
rb_local read local "HEAD after the checks" git -C "$RB_REPO" rev-parse HEAD
h1=$(rb_val '^([0-9a-f]{40})$')
[ -z "${RB_DRY:-}" ] && [ "$h0" != "$h1" ] && bad="$bad HEAD-moved"
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
rb_say "desk check: the window written today for E196; pulled under the lab-git lock; HEAD ${h1:0:12} descends from the registration ${reg:0:12} (subtree ${E196_REG_SUBTREE:0:8}); the paths clean; HISTORY OK; the lists at their pinned counts and bytes (49; the kit's $(echo "$KITPIN" | cut -d: -f2); the shared $SHAREDN), lists not pinned (reported):${unknown:- none}; the freeze line; no E196 datum in any ref; the preflight GO; the kit's desk tests' logs"
exit 0
