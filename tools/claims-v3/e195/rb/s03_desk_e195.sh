#!/usr/bin/env bash
# E195 (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum), the box step "step 2" (this file is s03): the desk check before any
# box step, on the desk only (aifoundry2, Linux, or a Mac), in E192's step 2 form (tools/claims-v3/e192/rb/s03_desk_e192.sh):
#   - the window first: RB_OUT's window written today (Pacific) for E195 (e195_window), or refused (10) before any call;
#   - the pull under the lab-git lock (e195_pull: RB_GITLOCK required; this step takes the lock itself for the pull alone, so it is NEVER
#     run inside that lock: a nested flock or lockf exits 75 and this step stops with 16);
#   - HEAD descends from e8a85229 (GitHub main when E195 was registered), from E195's registration commit found by its content (the
#     commit that added tools/claims-v3/e195/E195.md, whose e195 subtree reads 7b9aa484...: the registration with its freeze line, before
#     any datum) and from the kit's (the commit that added tools/claims-v3/e195/KIT.md);
#   - E195's paths clean; THE HISTORY CHECK (rb/check_history_e195.py tree): nothing under tools/claims-v3/e195 changed or went since the
#     registration and since the kit, additions only on the files E195's day reads, nothing untracked, no shadowing addition and no
#     shadowing file not committed in the folders the day's Python puts ahead of the standard library;
#   - EVERY LIST at its pinned count AND its own pinned sha256 AND every entry OK, with no override: the registration's (41, ba6849ce...)
#     and THE KIT'S OWN LIST (KITPIN below; this step is outside it: a file cannot hold the sha256 of a list that holds its own; the land
#     file and KIT.md give this step's sha256 beside the list's); every file with "SHA256SUMS" anywhere in its name under
#     tools/claims-v3/e195 found: one this step does not pin is REPORTED, never a gate;
#   - the freeze line in E195.md (b950de39..., on exactly one line);
#   - harness-e195.json re-made (CHECK PASS) and every file of it at its sha256 in the lab clone (HARNESS OK); the two ports re-made from
#     their sources by their exact replacements (desk/port_e195.py --check: PORT CHECK PASS); the dry listing re-made from the kit's
#     runner in its own dry mode, equal to the registration's but for --no-ms (desk/drylisting_e195.py: DRYLISTING-E195 PASS; no device:
#     the runner's dry mode runs no command);
#   - NO E195 DATUM IN ANY REF (no docs/reports/data/*e195* path in any commit or any ref's tip): a datum before the session is a stop; a
#     gate stop's record (docs/reports/gate-stops/<day>-e195-...: step 11 puts a session that ended at a gate there) is no datum;
#   - the preflight (preflight_e195.sh: dmcmd_audit GO, every send site a READ but the reviewed lib.sh:154 exception);
#   - the kit's desk tests' logs as committed, each with its PASS line once;
#   - HEAD unchanged across all of it, else 16.
# The card lane reads `uptime` before this step (aifoundry2's load rule); this step does not read it.
#   RB_GITLOCK=<the lab-git lock> bash tools/claims-v3/e195/rb/s03_desk_e195.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e195.sh"
rb_init s03_desk
e195_window
E=tools/claims-v3/e195
REGPIN=tools/claims-v3/e195/SHA256SUMS-e195-registration:41:ba6849ce6e3d17cde3c46a2cba4ca9e70afd38fca831ac7edb91cf956a163cec:top
KITPIN=tools/claims-v3/e195/SHA256SUMS-e195-kit:74:e50a1082fe4a8050db0b0347ffbea6de9d9c1eaed8881745f9a8473eb8d2ef00:top   # the kit's own list, at its count and its own bytes
F1=b950de393cf6f8052c73a4c4185dc8b703b40152088ae0806a1715246578168a
bad=""
e195_pull || bad="$bad pull"
[ -z "${RB_DRY:-}" ] && [ "${RB_RC:-0}" -ne 0 ] && bad="$bad pull(rc $RB_RC; a nested lab-git lock exits 75)"
rb_local read local "HEAD before the checks" git -C "$RB_REPO" rev-parse HEAD
h0=$(rb_val '^([0-9a-f]{40})$')
rb_local read local "HEAD descends from $RB_E195_BASE (GitHub main when E195 was registered)" git -C "$RB_REPO" merge-base --is-ancestor "$RB_E195_BASE" HEAD || bad="$bad base-ancestry"
reg=""; kit=""
for what in registration kit; do
  f=$E/E195.md; [ "$what" = kit ] && f=$E/KIT.md
  rb_local read local "E195's $what commit, by its content (the commit that added $(basename "$f"))" git -C "$RB_REPO" log --diff-filter=A --format=%H -- "$f"
  c=$(rb_val '^([0-9a-f]{40})$')
  [ -n "${RB_DRY:-}" ] && continue
  if [ -z "$c" ]; then bad="$bad $what-not-found"; continue; fi
  rb_local read local "the $what commit is an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$c" HEAD || bad="$bad $what-ancestry"
  if [ "$what" = registration ]; then
    reg=$c
    rb_local read local "the registration's e195 subtree" git -C "$RB_REPO" rev-parse "$c:$E"
    [ "$(rb_val '^([0-9a-f]{40})$')" = "$E195_REG_SUBTREE" ] || bad="$bad registration-subtree"
  else
    kit=$c
  fi
done
rb_local read local "E195's paths clean" git -C "$RB_REPO" status --short --untracked-files=all -- $E tools/claims-v3/lib.sh tools/claims-v3/text_hash.sh \
  tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/dmcmd_audit.py tools/claims-v3/dmcmd_table.json tools/claims-v3/runitems.py \
  tools/claims-v3/q141k-runbook/k6 tools/claims-v3/q141k-runbook/v3.1 tools/claims-v3/e183/rb tools/claims-v3/e178
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad paths-not-clean"
rb_local read local "the history check (check_history_e195.py)" "$RB_PY" -I -B $E/rb/check_history_e195.py tree
rb_has '^HISTORY OK' || bad="$bad history"
paths=""; for spec in $REGPIN $KITPIN; do paths="$paths ${spec%%:*}"; done
rb_local read local "the own sha256 of the lists E195 reads (pinned)" sha256sum $paths
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
rb_local read local "every file with SHA256SUMS anywhere in its name under $E" find "$E" -name '*SHA256SUMS*' -type f
unknown=""
if [ -z "${RB_DRY:-}" ]; then
  for f in $(cat "$RB_CAP"); do
    case "$f" in */SHA256SUMS-e195-registration|*/SHA256SUMS-e195-kit) continue ;; esac
    case "$f" in tools/claims-v3/e195/*) ;; *) continue ;; esac
    unknown="$unknown $(basename "$f")"
    rb_local read local "a list step 2 does not pin: $(basename "$f") (REPORTED, never a gate)" sha256sum -c "$f"
  done
fi
rb_local read local "the freeze line in E195.md, on one line" grep -c -e "$F1" $E/E195.md
[ -z "${RB_DRY:-}" ] && { [ "$(rb_val '^([0-9]+)$')" = 1 ] || bad="$bad freeze-line"; }
rb_local desk local "harness-e195.json re-made" "$RB_PY" -I -B $E/harness_e195.py --check
rb_has '^CHECK PASS' || bad="$bad harness-rebuild"
rb_local desk local "every harness file at its sha256 in the lab clone" "$RB_PY" -I -B $E/harness_e195.py --box
rb_has '^HARNESS OK: ' || bad="$bad harness"
rb_local desk local "the two ports re-made from their sources (desk/port_e195.py --check)" "$RB_PY" -I -B $E/desk/port_e195.py --check
rb_has '^PORT CHECK PASS' || bad="$bad ports"
[ -n "${RB_DRY:-}" ] || { rm -rf "${RB_OUT:?}/drylisting"; mkdir -p "$RB_OUT/drylisting"; }
rb_local desk local "the dry listing re-made from the kit's runner, equal to the registration's but for --no-ms (desk/drylisting_e195.py)" \
  "$RB_PY" -I -B $E/desk/drylisting_e195.py "$RB_OUT/drylisting"
rb_has '^DRYLISTING-E195 PASS' || bad="$bad dry-listing"
rb_local read local "no E195 datum in any commit of any ref" git -C "$RB_REPO" log --all --oneline -- 'docs/reports/data/*e195*'
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad E195-datum-in-a-ref"
rb_local read local "no E195 datum at any ref's tip, nor in any commit (check_history_e195.py nodatum)" "$RB_PY" -I -B $E/rb/check_history_e195.py nodatum
[ -z "${RB_DRY:-}" ] && { rb_has '^NO-DATUM OK' || bad="$bad E195-datum-at-a-tip"; }
rb_local desk local "the preflight: dmcmd_audit on the session's files, no WRITE allowed" bash $E/preflight_e195.sh
rb_has '^dmcmd_audit: GO' || bad="$bad preflight"
for spec in "desktest-realpath-e195.txt:^DESKTEST-REALPATH-E195 ([0-9]+) of \\1 PASS\$" "realbytes-e195.txt:^REALBYTES-E195 ([0-9]+) of \\1 PASS\$" \
            "selftest-rb-e195.txt:^SELFTEST-RB-E195 ([0-9]+) of \\1 PASS\$" "selftest-rest-e195.txt:^SELFTEST-REST-E195 ([0-9]+) of \\1 PASS\$" \
            "dry-listing-e195.txt:^dry listing: .* 0 box calls\$" "dmcmd-audit-e195.txt:^dmcmd_audit: GO" \
            "checks-e195.txt:^CHECKS-E195 ([0-9]+) of \\1 PASS\$"; do
  f=${spec%%:*}; pat=${spec#*:}
  rb_local read local "a desk test's log, as committed: $f" grep -cE "$pat" "$E/logs/$f"
  [ -z "${RB_DRY:-}" ] && { [ "$(rb_val '^([0-9]+)$')" = 1 ] || bad="$bad log-$f"; }
done
rb_local read local "HEAD after the checks" git -C "$RB_REPO" rev-parse HEAD
h1=$(rb_val '^([0-9a-f]{40})$')
[ -z "${RB_DRY:-}" ] && [ "$h0" != "$h1" ] && bad="$bad HEAD-moved"
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
rb_say "desk check: the window written today for E195; pulled under the lab-git lock; HEAD ${h1:0:12} descends from $RB_E195_BASE, the registration ${reg:0:12} (subtree ${E195_REG_SUBTREE:0:8}) and the kit ${kit:0:12}; the paths clean; HISTORY OK; the lists at their pinned counts and bytes (41; the kit's $(echo "$KITPIN" | cut -d: -f2)), lists not pinned (reported):${unknown:- none}; the freeze line; the harness re-made and at its sha256; PORT CHECK PASS; DRYLISTING-E195 PASS; no E195 datum in any ref; the preflight GO; the kit's desk tests' logs"
exit 0
