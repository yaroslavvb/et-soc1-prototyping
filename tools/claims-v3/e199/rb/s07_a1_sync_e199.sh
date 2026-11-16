#!/usr/bin/env bash
# E199 (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum; E192's file, a6fe5c20, unchanged beside it, ported to aifoundry1 card 1), the box step "the sync" (this file is s07): aifoundry1's one rsync for
# E199, after the look read FREE. E189's step 5's form (rb/s07_a3_sync_e189.sh), with E199's own root on the box:
#   1. the window rule first (written today for E199; now before the last start);
#   2. the box read first: k6's ours_live (any session_eNNN.sh of ours) and jobs_live (a runbook job still running); either above 0 is
#      REFUSED on the box and 10 here, before anything is synced; E199's root (build/claims-v3/aifoundry1-c1/e199 in the box's tree) is made
#      there if it is not yet (E199's own directory; nothing of another run's is written);
#   3. the sync list is boxfiles-e199.txt's paths, and nothing is synced unless they are committed (uncommitted changes refuse, 16) and
#      the lab clone's copies read at their sha256 by the four lists (E192's registration's, E199's registration's, the kit's, the shared); the rsync is E189's form
#      with -c -R -i into aifoundry1:nekko/build/claims-v3/aifoundry1-c1/e199/, its itemized lines naming every file whose content it sent;
#   4. the box's copies read at their pins (one 60 s read): BOX-PINS OK.
#   bash tools/claims-v3/e199/rb/s07_a1_sync_e199.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e199.sh"
rb_init s07_a1_sync
e199_window
rb_need_start
rb_probe aifoundry1
f=$(rb_file notours)
{ rb_prelude aifoundry1
  echo "ER=$E199_R"
  cat <<'EOF3'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: E199's sync never runs beside one"; exit 3; fi
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: E199's sync never runs under one"; exit 3; fi
[ -d build/claims-v3/aifoundry1-c1 ] || { echo "REFUSED: no build/claims-v3/aifoundry1-c1 (lib.sh's card-1 data root) in the box's tree"; exit 3; }
mkdir -p "$ER" && echo "ROOT-READY $ER"
echo "NOT-BESIDE-OURS: no card session of ours and no runbook job on $BOX"
EOF3
} > "$f"
rb_remote read aifoundry1 "no card session of ours and no runbook job on the box before the sync; E199's root made" "$f"
rb_refused
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read before the sync exited $RB_RC: nothing synced"
[ -n "${RB_DRY:-}" ] || rb_has '^NOT-BESIDE-OURS: ' || rb_die $RB_E_FAIL "the read before the sync gave no answer: nothing synced"
P=()
while IFS= read -r p; do case "$p" in ''|'#'*) ;; *) P+=("$p") ;; esac; done < tools/claims-v3/e199/boxfiles-e199.txt
[ "${#P[@]}" -ge 30 ] || rb_die $RB_E_USAGE "the sync list could not be read from boxfiles-e199.txt"
rb_local read local "the synced paths clean before the sync" git -C "$RB_REPO" status --short -- "${P[@]}"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "the synced paths have uncommitted changes: sync only the pushed commit"
rb_local read local "the lab clone's copies at their sha256 (the registration's, the kit's and the shared list)" sha256sum -c \
  tools/claims-v3/e192/SHA256SUMS-e192-registration tools/claims-v3/e199/SHA256SUMS-e199-registration tools/claims-v3/e199/SHA256SUMS-e199-kit tools/claims-v3/e199/SHA256SUMS-e199-shared
[ -z "${RB_DRY:-}" ] && { [ "$RB_RC" -eq 0 ] && ! grep -qv ': OK$' "$RB_CAP" || rb_die $RB_E_GATE "a file of the lists is off its sha256 in the lab clone: nothing is synced"; }
rb_probe aifoundry1
rb_local copy aifoundry1 "aifoundry1's rsync: boxfiles-e199.txt's files into E199's root (itemized)" \
  rsync -a -c -R -i --exclude __pycache__ -e "$RB_RSH" "${P[@]}" "aifoundry1:nekko/$E199_R/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rsync exited non-zero"
sent=$(grep -cE '^[<>]f' "$RB_CAP" 2>/dev/null)
rb_probe aifoundry1
f=$(rb_file boxpins)
{ rb_prelude aifoundry1
  echo "ER=$E199_R"
  cat <<'EOF3'
cd "$ER" || { echo "REFUSED: no E199 root"; exit 3; }
n=0; bad=0
for L in tools/claims-v3/e192/SHA256SUMS-e192-registration tools/claims-v3/e199/SHA256SUMS-e199-registration tools/claims-v3/e199/SHA256SUMS-e199-kit tools/claims-v3/e199/SHA256SUMS-e199-shared; do
  while read -r h p; do
    [ -e "$p" ] || continue
    n=$((n + 1)); [ "$(sha256sum "$p" | cut -d' ' -f1)" = "$h" ] || { bad=$((bad + 1)); echo "OFF-PIN $p"; }
  done < "$L"
done
m=0; while IFS= read -r p; do case "$p" in ''|'#'*) continue ;; esac; [ -e "$p" ] || { m=$((m + 1)); echo "ABSENT $p"; }; done < tools/claims-v3/e199/boxfiles-e199.txt
[ "$bad" -eq 0 ] && [ "$m" -eq 0 ] && echo "BOX-PINS OK $n files at their pins; every synced path present"
EOF3
} > "$f"
rb_remote read aifoundry1 "the box's copies at their pins" "$f"
rb_refused
[ -n "${RB_DRY:-}" ] || rb_has '^BOX-PINS OK ' || rb_die $RB_E_GATE "the box's copies are not all at their pins (the lines above)"
rb_say "synced to aifoundry1:nekko/$E199_R/ (${#P[@]} paths; the rsync sent ${sent:-?} files' contents); the box's copies at their pins"
exit 0
