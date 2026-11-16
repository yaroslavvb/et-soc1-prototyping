#!/usr/bin/env bash
# E199 (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum), the desk step "the desk check" (this file is s03; the card lane's step
# 2): E192's step 2 (tools/claims-v3/e192/rb/s03_desk_e192.sh, unchanged beside it) in E191's form for aifoundry1, at the desk, before any
# box step that day. It is OUTSIDE SHA256SUMS-e199-kit (a list cannot hold the sha256 of a file that pins the list): its own sha256 is in
# the land file's anchor lines and KIT.md section 8. It refuses (16) unless every line below reads as stated:
#   1. the window written today for E199 (e199_window); `git pull --ff-only` under the lab-git lock, RB_GITLOCK (never nested: a nested
#      lock exits 75 and this step reads 16); HEAD read before and after (HEAD unchanged);
#   2. E199's registration commit, found by its content (the commit that added tools/claims-v3/e199/E199.md), an ancestor of HEAD, its
#      tools/claims-v3/e199 subtree 070b4e2d...; E199's paths clean; THE HISTORY CHECK (rb/check_history_e199.py tree: additions only under
#      tools/claims-v3/e199/ since the registration and the kit, and under tools/claims-v3/e192/ and every other path the day reads; no
#      shadow of a module in the folders the day's Python puts first);
#   3. THE LISTS at their pinned counts and their own sha256, every entry OK: E199's registration (17, 4d05fe0a...), E192's registration
#      (30, dd0a8963...: the proposal E199 runs), E192's kit list (35, c89e91b9...: check_e192.py, E199's step 13 runs it unchanged) and
#      E199's kit list (KITPIN below); the shared list (6) every entry; any other list under tools/claims-v3/e199 REPORTED;
#   4. E199's two freeze lines in E199.md, each on one line and printed (1: the forecast, deb4a7d1...; 2: the model session's sealed
#      card-1 forecast, 1c5d8fa3..., posted 01:28:51 PST Mon 16 Nov 2026 and registered before the land: fix-e199, verify-e199 F2), and
#      THE SEALED CARD-1 NOTE for a later one (CONTEXT section 122 of the round: a sealed
#      card-1 forecast the model session posts after the land enters by a dated note OUTSIDE E199's pinned subtree,
#      tools/claims-v3/sealed-card1/e199-freeze-lines.md, committed under the desk-commit rule before E199's card day): when the note
#      exists it must be tracked and clean at HEAD, added after E199's registration and touched by that one commit only (a dated note is
#      never edited; it is never a change under tools/claims-v3/e199/);
#      every sha256 it names (64 hex digits) is printed as a sealed card-1 freeze line of E199 (REPORTED: the model session scores it
#      privately; no lab file holds its numbers); when it does not exist, "none" is printed. The history check and the no-datum checks
#      accept it (it is outside the pinned subtree and outside docs/reports/data);
#   5. no E199 datum in any ref (git log --all on docs/reports/data/*e199*; check_history_e199.py nodatum);
#   6. the preflight's plain chain GO (preflight_e199.sh); the kit's desk tests' logs as committed, each with its pass line.
#   RB_GITLOCK=<the lab-git lock> bash tools/claims-v3/e199/rb/s03_desk_e199.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e199.sh"
rb_init s03_desk
e199_window
E=tools/claims-v3/e199
REGPIN=tools/claims-v3/e199/SHA256SUMS-e199-registration:17:4d05fe0a7e6cadb6e3a2f0bf303d5f6804345c4ce9f738033a598ae926fff35f:top
E192REGPIN=tools/claims-v3/e192/SHA256SUMS-e192-registration:30:dd0a89635800818cd17c429be2d02c9710a434364f4196e6fd1a0f8e2dd74326:top
E192KITPIN=tools/claims-v3/e192/SHA256SUMS-e192-kit:35:c89e91b967ae19dd238c6863ddb485e21d6e978fabf2224d34edffd1df04f09f:top
KITPIN=tools/claims-v3/e199/SHA256SUMS-e199-kit:46:356c3756d20c28e0996591dc2756d9f0d5b0fbf0661e6f2f076abb22c2ff2034:top   # E199's kit list, at its count and its own bytes
SHAREDN=6
F1=deb4a7d114a3549b0f4da888cba06409b5cd0589de2e10b8e257f17cd413314a
F2=1c5d8fa3efa054272451017538cd42018b589050493b9e504a5d5d90bc1009c3   # E199.md's freeze line 2: the sealed card-1 forecast (#2.5.1.2.3, 01:28:51 PST Mon 16 Nov 2026)
NOTE=tools/claims-v3/sealed-card1/e199-freeze-lines.md
bad=""
e199_pull || bad="$bad pull"
[ -z "${RB_DRY:-}" ] && [ "${RB_RC:-0}" -ne 0 ] && bad="$bad pull(rc $RB_RC; a nested lab-git lock exits 75)"
rb_local read local "HEAD before the checks" git -C "$RB_REPO" rev-parse HEAD
h0=$(rb_val '^([0-9a-f]{40})$')
rb_local read local "E199's registration commit, by its content (the commit that added E199.md)" git -C "$RB_REPO" log --diff-filter=A --format=%H -- $E/E199.md
reg=$(rb_val '^([0-9a-f]{40})$')
if [ -z "${RB_DRY:-}" ]; then
  [ -n "$reg" ] || bad="$bad registration-not-found"
  if [ -n "$reg" ]; then
    rb_local read local "the registration commit is an ancestor of HEAD" git -C "$RB_REPO" merge-base --is-ancestor "$reg" HEAD || bad="$bad registration-ancestry"
    [ "$RB_RC" -eq 0 ] || bad="$bad registration-ancestry"
    rb_local read local "the registration's e199 subtree" git -C "$RB_REPO" rev-parse "$reg:$E"
    [ "$(rb_val '^([0-9a-f]{40})$')" = "$E199_REG_SUBTREE" ] || bad="$bad registration-subtree"
  fi
else
  rb_local read local "the registration commit is an ancestor of HEAD, and its e199 subtree reads $E199_REG_SUBTREE" git -C "$RB_REPO" rev-parse "<reg>:$E"
fi
rb_local read local "E199's paths clean" git -C "$RB_REPO" status --short --untracked-files=all -- $E
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad paths-not-clean"
rb_local read local "the history check (check_history_e199.py)" "$RB_PY" -I -B $E/rb/check_history_e199.py tree
rb_has '^HISTORY OK' || bad="$bad history"
paths=""; for spec in $REGPIN $E192REGPIN $E192KITPIN $KITPIN; do paths="$paths ${spec%%:*}"; done
rb_local read local "the own sha256 of the lists E199 reads (pinned)" sha256sum $paths
OWNCAP=$RB_CAP
for spec in $REGPIN $E192REGPIN $E192KITPIN $KITPIN; do
  l=${spec%%:*}; rest=${spec#*:}; pin=${rest%%:*}; rest=${rest#*:}; own=${rest%%:*}
  if [ -z "${RB_DRY:-}" ]; then
    [ "$(grep -E "^[0-9a-f]{64}  $l\$" "$OWNCAP" | cut -d' ' -f1)" = "$own" ] || bad="$bad $(basename "$l")-sha256"
    [ "$(grep -c . "$RB_REPO/$l" 2>/dev/null)" = "$pin" ] || bad="$bad $(basename "$l")-count"
  fi
  rb_local read local "the list $(basename "$l") (pinned at $pin entries and its own sha256), every entry" sha256sum -c "$l"
  [ -z "${RB_DRY:-}" ] && { [ "$RB_RC" -eq 0 ] && [ "$(grep -c ': OK$' "$RB_CAP")" = "$pin" ] || bad="$bad $(basename "$l")-entries"; }
done
rb_local read local "the shared list (pinned by the kit's list), every entry" sha256sum -c $E/SHA256SUMS-e199-shared
[ -z "${RB_DRY:-}" ] && { [ "$RB_RC" -eq 0 ] && [ "$(grep -c ': OK$' "$RB_CAP")" = "$SHAREDN" ] || bad="$bad shared-list"; }
rb_local read local "every file with SHA256SUMS anywhere in its name under $E" find "$E" -name '*SHA256SUMS*' -type f
unknown=""
if [ -z "${RB_DRY:-}" ]; then
  for f in $(cat "$RB_CAP"); do
    case "$f" in */SHA256SUMS-e199-registration|*/SHA256SUMS-e199-kit|*/SHA256SUMS-e199-shared) continue ;; esac
    case "$f" in tools/claims-v3/e199/*) ;; *) continue ;; esac
    unknown="$unknown $(basename "$f")"
    rb_local read local "a list step 2 does not pin: $(basename "$f") (REPORTED, never a gate)" sha256sum -c "$f"
  done
fi
rb_local read local "E199's freeze line in E199.md, on one line" grep -c -e "$F1" $E/E199.md
[ -z "${RB_DRY:-}" ] && { [ "$(rb_val '^([0-9]+)$')" = 1 ] || bad="$bad freeze-line"; }
rb_local read local "E199's freeze line 2 in E199.md (the sealed card-1 forecast, registered before the land), on one line" grep -c -e "$F2" $E/E199.md
[ -z "${RB_DRY:-}" ] && { [ "$(rb_val '^([0-9]+)$')" = 1 ] || bad="$bad freeze-line-2"; }
# THE SEALED CARD-1 NOTE (outside the pinned subtree), when it exists
sealed="none (no dated note at $NOTE)"
if [ -n "${RB_DRY:-}" ] || [ -e "$RB_REPO/$NOTE" ]; then
  rb_local read local "the sealed card-1 note tracked at HEAD (git ls-files)" git -C "$RB_REPO" ls-files -- "$NOTE"
  [ -z "${RB_DRY:-}" ] && { [ "$(grep -c . "$RB_CAP")" = 1 ] || bad="$bad sealed-note-untracked"; }
  rb_local read local "the sealed card-1 note clean" git -C "$RB_REPO" status --porcelain --untracked-files=all -- "$NOTE"
  [ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad sealed-note-not-clean"
  rb_local read local "the commit that added the note, after E199's registration" git -C "$RB_REPO" log --diff-filter=A --format=%H -- "$NOTE"
  addn=$(rb_val '^([0-9a-f]{40})$')
  if [ -z "${RB_DRY:-}" ]; then
    { [ -n "$addn" ] && [ -n "$reg" ] && git -C "$RB_REPO" merge-base --is-ancestor "$reg" "$addn" 2>/dev/null; } || bad="$bad sealed-note-not-after-registration"
  fi
  rb_local read local "the commits that touched the note (a dated note is added once and never edited)" git -C "$RB_REPO" log --format=%H -- "$NOTE"
  [ -z "${RB_DRY:-}" ] && { [ "$(grep -cE '^[0-9a-f]{40}$' "$RB_CAP")" = 1 ] || bad="$bad sealed-note-edited"; }
  rb_local read local "the sha256 the note names (64 hex digits a word)" grep -oE '\b[0-9a-f]{64}\b' "$NOTE"
  if [ -z "${RB_DRY:-}" ]; then
    hs=$(grep -oE '\b[0-9a-f]{64}\b' "$RB_REPO/$NOTE" 2>/dev/null | sort -u | tr '\n' ' ')
    sealed="the dated note ${NOTE##*/} (added ${addn:0:12}): ${hs:-no sha256 found}"
    [ -n "$hs" ] || bad="$bad sealed-note-names-no-sha256"
  fi
fi
rb_local read local "no E199 datum in any commit of any ref" git -C "$RB_REPO" log --all --oneline -- 'docs/reports/data/*e199*'
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad E199-datum-in-a-ref"
rb_local read local "no E199 datum at any ref's tip, nor in any commit (check_history_e199.py nodatum)" "$RB_PY" -I -B $E/rb/check_history_e199.py nodatum
[ -z "${RB_DRY:-}" ] && { rb_has '^NO-DATUM OK' || bad="$bad E199-datum-at-a-tip"; }
rb_local desk local "the preflight: dmcmd_audit on the session's files, no WRITE allowed (two tables)" bash $E/preflight_e199.sh
rb_has '^PLAIN-CHAIN: GO' || bad="$bad preflight"
pv=$(rb_val '^PVT-CHAIN: ([A-Z-]+).*$')
for spec in "desktest-realpath-e199.txt:^DESKTEST-REALPATH-E199 ([0-9]+) of \\1 PASS\$" "selftest-rb-e199.txt:^SELFTEST-RB-E199 ([0-9]+) of \\1 PASS\$" \
            "selftest-rest-e199.txt:^SELFTEST-REST-E199 ([0-9]+) of \\1 PASS\$" "realbytes-e199.txt:^REALBYTES-E199 ([0-9]+) of \\1 PASS\$" \
            "realbuild-e199.txt:^REALBUILD-E199 ([0-9]+) of \\1 PASS\$" "dry-audit-e199.txt:^DRY-AUDIT-E199 ([0-9]+) of \\1 COVERED\$" \
            "dry-listing-e199.txt:^dry listing: .* 0 box calls\$" "dmcmd-audit-e199.txt:^PLAIN-CHAIN: GO"; do
  f=${spec%%:*}; pat=${spec#*:}
  rb_local read local "a desk test's log, as committed: $f" grep -cE "$pat" "$E/logs/$f"
  [ -z "${RB_DRY:-}" ] && { [ "$(rb_val '^([0-9]+)$')" = 1 ] || bad="$bad log-$f"; }
done
rb_local read local "HEAD after the checks" git -C "$RB_REPO" rev-parse HEAD
h1=$(rb_val '^([0-9a-f]{40})$')
[ -z "${RB_DRY:-}" ] && [ "$h0" != "$h1" ] && bad="$bad HEAD-moved"
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
echo "$(date '+%F %T %Z') step=$RB_STEP sealed card-1 freeze lines: E199.md line 2 $F2 (registered); the later note: $sealed" >> "$RB_LOG"
rb_say "desk check: the window written today for E199; pulled under the lab-git lock; HEAD ${h1:0:12} descends from the registration ${reg:0:12} (subtree ${E199_REG_SUBTREE:0:8}); the paths clean; HISTORY OK; the lists at their pinned counts and bytes (E199's 17; E192's 30 and its kit's 35; E199's kit $(echo "$KITPIN" | cut -d: -f2); the shared $SHAREDN), lists not pinned (reported):${unknown:- none}; the two freeze lines; sealed card-1 freeze lines: E199.md line 2 $F2 (registered); the later note: $sealed; no E199 datum in any ref; the preflight's plain chain GO (the per-sensor chain ${pv:-?}); the kit's desk tests' logs"
exit 0
