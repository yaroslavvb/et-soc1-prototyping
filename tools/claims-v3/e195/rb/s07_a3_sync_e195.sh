#!/usr/bin/env bash
# E195 (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum), the box step "the sync" (this file is s07): aifoundry3's one rsync for
# E195, after the look read FREE. E192's step 5's form (rb/s07_a3_sync_e192.sh), with E193's sync list (the harness's):
#   1. the window rule first (written today for E195; now before the last start);
#   2. the box read first: k6's ours_live (any session_eNNN.sh of ours) and jobs_live (a runbook job still running); either above 0 is
#      REFUSED on the box and 10 here, before anything is synced; E195's root (build/claims-v3/aifoundry3/e195 in the box's tree) is made
#      there if it is not yet (E195's own directory; nothing of another run's is written);
#   3. the sync list is harness_e195.py --list (every file harness-e195.json pins, and that file last: the registration's 41 and its list,
#      the kit's box files, the lab's block library, text hash, E128's guard and the device-command checker with its table), and nothing is
#      synced unless they are committed (uncommitted changes refuse, 16) and the lab clone's copies read at their sha256 (harness_e195.py
#      --check and --box in the lab clone); the rsync is E192's form with -c -R -i into aifoundry3:aifoundry/build/claims-v3/aifoundry3/e195/,
#      its itemized lines naming every file whose content it sent;
#   4. the box's copies read at their pins (one 60 s read: harness_e195.py --box on the box, from E195's root): HARNESS OK.
#   bash tools/claims-v3/e195/rb/s07_a3_sync_e195.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e195.sh"
rb_init s07_a3_sync
e195_window
rb_need_start
rb_probe aifoundry3
f=$(rb_file notours)
{ rb_prelude aifoundry3
  echo "ER=$E195_R"
  cat <<'EOF3'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: E195's sync never runs beside one"; exit 3; fi
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: E195's sync never runs under one"; exit 3; fi
[ -d build/claims-v3/aifoundry3 ] || { echo "REFUSED: no build/claims-v3/aifoundry3 in the box's tree"; exit 3; }
mkdir -p "$ER" && echo "ROOT-READY $ER"
echo "NOT-BESIDE-OURS: no card session of ours and no runbook job on $BOX"
EOF3
} > "$f"
rb_remote read aifoundry3 "no card session of ours and no runbook job on the box before the sync; E195's root made" "$f"
rb_refused
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read before the sync exited $RB_RC: nothing synced"
[ -n "${RB_DRY:-}" ] || rb_has '^NOT-BESIDE-OURS: ' || rb_die $RB_E_FAIL "the read before the sync gave no answer: nothing synced"
P=()
if [ -n "${RB_DRY:-}" ]; then
  P=("<every path harness_e195.py --list prints>")
else
  while IFS= read -r p; do [ -n "$p" ] && P+=("$p"); done < <("$RB_PY" -I -B tools/claims-v3/e195/harness_e195.py --list)
  [ "${#P[@]}" -ge 50 ] || rb_die $RB_E_USAGE "the sync list could not be read from harness_e195.py --list"
fi
rb_local read local "the synced paths clean before the sync" git -C "$RB_REPO" status --short -- "${P[@]}"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "the synced paths have uncommitted changes: sync only the pushed commit"
rb_local desk local "harness-e195.json re-made in the lab clone (CHECK PASS)" "$RB_PY" -I -B tools/claims-v3/e195/harness_e195.py --check
[ -n "${RB_DRY:-}" ] || rb_has '^CHECK PASS' || rb_die $RB_E_GATE "harness-e195.json does not re-make from the lab clone's files: nothing is synced"
rb_local desk local "every harness file at its sha256 in the lab clone (HARNESS OK)" "$RB_PY" -I -B tools/claims-v3/e195/harness_e195.py --box
[ -n "${RB_DRY:-}" ] || rb_has '^HARNESS OK: ' || rb_die $RB_E_GATE "a harness file is off its sha256 in the lab clone: nothing is synced"
rb_probe aifoundry3
rb_local copy aifoundry3 "aifoundry3's rsync: harness-e195.json's files into E195's root (itemized)" \
  rsync -a -c -R -i --exclude __pycache__ -e "$RB_RSH" "${P[@]}" "aifoundry3:aifoundry/$E195_R/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rsync exited non-zero"
sent=$(grep -cE '^[<>]f' "$RB_CAP" 2>/dev/null)
rb_probe aifoundry3
f=$(rb_file boxpins)
{ rb_prelude aifoundry3
  echo "ER=$E195_R"
  cat <<'EOF3'
cd "$ER" || { echo "REFUSED: no E195 root"; exit 3; }
python3 -I -B tools/claims-v3/e195/harness_e195.py --box --root . 2>&1 | tail -n 3
EOF3
} > "$f"
rb_remote read aifoundry3 "the box's copies at their pins (harness_e195.py --box)" "$f"
rb_refused
[ -n "${RB_DRY:-}" ] || rb_has '^HARNESS OK: ' || rb_die $RB_E_GATE "the box's copies are not all at their pins (the lines above)"
rb_say "synced to aifoundry3:aifoundry/$E195_R/ (${#P[@]} paths; the rsync sent ${sent:-?} files' contents); the box's copies at their pins (HARNESS OK)"
exit 0
