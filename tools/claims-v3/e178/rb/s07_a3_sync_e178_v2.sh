#!/usr/bin/env bash
# E178 (Q146; the kit's dated note 1, ../KIT.md.dated-note-1.md section 1), step 7, v2: aifoundry3's one rsync for E178, after the look read
# FREE (k6's s05_look_k6.sh aifoundry3). It replaces s07_a3_sync_e178.sh (v1, which stays as committed) in the runbook.
# v1 synced E178's directory, E78's six committed one-number tiles and the three pinned watcher files, and relied on aifoundry3's
# ~/aifoundry still holding the harness's other 20 non-binary files at their committed hashes: E163's 14 card-code files (lib.sh, run_e78.py,
# e78_common.py, reduce_e78.py, kinds.json, the guard, dmcmd_audit.py and its table, the host source, the five ccheck files) and E78's six
# anchor tiles (fp32 and fp16 zeros and randn, int8 zeros and full), which E171 ran there on 5 Nov 2026 (the kit verifier's fault 1: the
# E174 class, mitigated). v2 syncs v1's paths AND every other file harness-e178.json names but its four box binaries, the list read from the
# harness itself by ../sync_paths_e178.py (Q143(k)'s s07_a3_sync_q143k.sh form, which synced E176's box list to this box the same way on
# 5 Nov), so step 8's check (HARNESS OK: 84 files) and this sync agree by construction. The binaries (build/...) are the box's own, built
# there, and step 8 checks them. rsync -c sends nothing where a file already matches; the form is v1's (and E171's, E176's) unchanged.
# Only the pushed commit is synced: uncommitted changes in these paths refuse. And nothing is synced unless the lab clone's 80 files read
# at the harness's sha256 (check_e178.py --desk, as step 3 runs it): v2 sends 20 files v1 never sent, so a later commit to one of them
# (lib.sh is shared by every kit) must stop here, before it can overwrite the box's good copy.
#
#   bash tools/claims-v3/e178/rb/s07_a3_sync_e178_v2.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e178.sh"
rb_init s07_a3_sync_v2
L=$("$RB_PY" -B tools/claims-v3/e178/sync_paths_e178.py tools/claims-v3/e178/harness-e178.json "${E178_PATHS[@]}") ||
  rb_die $RB_E_USAGE "the sync list could not be read from harness-e178.json: $L"
P=(); cover=""
while IFS= read -r ln; do
  case "$ln" in "SYNC "*) P+=("${ln#SYNC }") ;; "COVER "*) cover=${ln#COVER } ;; esac
done <<EOF2
$L
EOF2
set -- $cover
[ "$#" -eq 5 ] && [ "$1" -eq "$5" ] && [ "${#P[@]}" -eq $((${#E178_PATHS[@]} + $4)) ] ||
  rb_die $RB_E_USAGE "the sync list does not cover the harness (COVER '$cover', ${#P[@]} paths)"
rb_say "the sync list: v1's ${#E178_PATHS[@]} paths (they hold $3 of the harness's $1 files) and its $4 other files: all $5 of them; its $2 box binaries are checked in step 8"
rb_local read local "E178's paths clean before the sync (v1's and the harness's other $4 files)" git -C "$RB_REPO" status --short "${P[@]}"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "E178's paths have uncommitted changes: sync only the pushed commit"
# v2: the sync never sends a file that differs from the harness (a later commit to a shared file such as lib.sh would otherwise overwrite
# the box's good copy, which v1 never touched): the lab clone's 80 files must read at their sha256 first
rb_local read local "the lab clone's copies of the harness's $1 files at their sha256 (check_e178.py --desk)" \
  "$RB_PY" -B tools/claims-v3/e178/check_e178.py --desk
rb_has "^HARNESS OK: $1 files" || rb_die $RB_E_GATE "a file the sync would send differs from harness-e178.json (the lines above): nothing is synced; a dated amendment registers it first"
rb_probe aifoundry3
rb_local copy aifoundry3 "aifoundry3's rsync: E178's directory, E78's committed tiles, the pinned watcher files and the harness's card code" \
  rsync -a -c -R --exclude __pycache__ -e "$RB_RSH" "${P[@]}" aifoundry3:aifoundry/
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rsync exited non-zero"
rb_say "synced to aifoundry3:aifoundry/ every file of harness-e178.json but its box binaries ($5 files, in ${#P[@]} paths)"
