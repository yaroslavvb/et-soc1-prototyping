# E213 Amendment A3 (Q219, lane a3-e213, Wed 18 Nov 2026, before any datum of E213's arm B): the part A3's runbook steps source (bash 3.2 or later;
# the desk is aifoundry2). It sources Amendment A2's runbook file, tools/claims-v3/e213-a2/rb/rb_e213_a2.sh, UNCHANGED (and through it E213's
# tools/claims-v3/e213/rb/rb_e213.sh and k6's rb_common.sh, unchanged: the bounded runner, the probe, the login-link stop, the prelude, the holder
# rule, the exit codes; A2's pins, its read's folder and its launch guard), and adds only:
#   - e213a3_only_B: A3 is ARM B's alone (aifoundry1 card 1); arm A keeps the kit's steps as landed (a call for arm A is refused, 10);
#   - THE PINS of A3's three box files (the runner's wrapper run_e213_a3.py, its session wrapper session_e213.sh and the order sequence-B-a3.json),
#     each at its sha256 below. e213a3_check_desk reads them in the lab clone (committed, unmodified, at their sha256) before anything is synced
#     (row 5b); e213a3_box_text checks the same list in the box's tree and runs the wrapper's own check there (`run_e213_a3.py check`: the
#     sequence file at its pin and EQUAL to A3's order derived from the box's registered points-e213.json), in row 5b after the sync and in row
#     9's launch call after A2's guard, before the launch.
# Exit codes: k6's (0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder for 30 minutes; 16 a gate
# says stop; 17 call again).
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../../e213-a2/rb/rb_e213_a2.sh"
RB_E213A3_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
E213A3_BOXFILES="tools/claims-v3/e213-a3/run_e213_a3.py tools/claims-v3/e213-a3/session_e213.sh tools/claims-v3/e213-a3/sequence-B-a3.json"

e213a3_pins_text() {  # A3's box files, in sha256sum's form (as A3 commits them)
  cat <<'EOF'
2dc0786dedc907dea638297cba7f98d4bf7fd27fdb697cb699b2b9d85be8cd2f  tools/claims-v3/e213-a3/run_e213_a3.py
6d1b34dd690365fe3d0d399494047c43b48ac672ff579ebdb1ab548963e2e00c  tools/claims-v3/e213-a3/session_e213.sh
6aea5d8c6333bb89ffadd4ac383167e28e947f673bdaf261f90264c8a05b3842  tools/claims-v3/e213-a3/sequence-B-a3.json
EOF
}

e213a3_only_B() {  # A3 is arm B's alone
  [ "${ARM:-}" = B ] || rb_die $RB_E_USAGE "Amendment A3 is E213 arm B's alone (aifoundry1 card 1); arm A runs the kit's own steps as landed (its day has run)"
}

e213a3_check_desk() {  # the pins in the lab clone: A3's box files committed and unmodified, each at its sha256; else 16, nothing synced
  rb_local read local "A3's box files unmodified in the lab clone (the runner's wrapper, its session wrapper, the order)" git -C "$RB_REPO" status --short --untracked-files=all $E213A3_BOXFILES
  [ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "A3's box files have uncommitted changes in the lab clone: nothing is synced"
  local f="$RB_OUT/e213-a3-pins.txt"
  e213a3_pins_text > "$f"
  RB_CWD="$RB_REPO" rb_local read local "A3's box files at their pinned sha256 in the lab clone" sha256sum -c "$f"
  [ -n "${RB_DRY:-}" ] && return 0
  [ "$RB_RC" -eq 0 ] && [ "$(grep -c ': OK$' "$RB_CAP")" -eq "$(grep -c . "$f")" ] ||
    rb_die $RB_E_GATE "A3's box files are not at their pinned sha256 in the lab clone (the lines above): nothing is synced"
  return 0
}

e213a3_box_text() {  # e213a3_box_text <the words after a stop>: the remote lines that check A3's box files' pins and A3's order on the box:
  #                    "A3-PINS OK 3 of 3" and "A3-ORDER OK: ...", else "A3-STOP: ..." and exit 3
  local after=${1:-nothing launched}
  echo "mkdir -p build/e213"
  echo "cat > build/e213/a3-pins.sha256 <<'A3PINS'"
  e213a3_pins_text
  echo "A3PINS"
  echo "A3AFTER=$(printf '%q' "$after")"
  cat <<'EOF'
pins=$(sha256sum -c build/e213/a3-pins.sha256 2>&1); prc=$?
nok=$(printf '%s\n' "$pins" | grep -c ': OK$'); nall=$(grep -c . build/e213/a3-pins.sha256)
if [ "$prc" -ne 0 ] || [ "$nok" -ne "$nall" ]; then
  echo "A3-STOP: A3's box files are not at their pinned sha256 on $BOX ($(printf '%s\n' "$pins" | grep -v ': OK$' | head -n 2 | tr '\n' ';' | cut -c1-200)): $A3AFTER"
  exit 3
fi
echo "A3-PINS OK $nok of $nall"
ord=$(python3 -I -B tools/claims-v3/e213-a3/run_e213_a3.py check 2>&1); orc=$?
printf '%s\n' "$ord" | grep -v '^A3-ORDER OK: ' | sed 's/^/  | /' | head -n 12
if [ "$orc" -ne 0 ] || ! printf '%s\n' "$ord" | grep -q '^A3-ORDER OK: '; then
  echo "A3-STOP: A3's order check on $BOX exited $orc ($(printf '%s\n' "$ord" | grep -m1 '^A3-STOP: ' | cut -c10-220)): $A3AFTER"
  exit 3
fi
printf '%s\n' "$ord" | grep -m1 '^A3-ORDER OK: '
EOF
}
