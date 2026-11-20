#!/bin/bash
# decl-e217 (Q228) step 3: FROZEN.txt, the freeze line's content (the declaration and the nominal forecasts, final), for the orchestrator to post
# on the Discussion. Reads only this lane's files and out/orch/e217-releases.txt (the claim state); writes FROZEN.txt once (refuses to overwrite).
set -u
. <W>/out/decl-e217/scripts/env.sh
F=$L/FROZEN.txt
[ -e "$F" ] && { echo "FROZEN.txt exists: not overwritten"; exit 4; }
cd "$L" || exit 2
NREL=$(grep -c '^#13' "$W/out/orch/e217-releases.txt")
LASTREL=$(grep '^#13' "$W/out/orch/e217-releases.txt" | tail -1 | cut -c1-40)
NCLAIM=$(ls "$W/out/orch" | grep -c '^claim-')
{
  echo "decl-e217 (round Q228): the lab's BLIND test of its frozen matmul models on E217 (#13, 1119-mmsweep4), DECLARED and its nominal forecasts FROZEN at $(ts), before any E217 datum exists."
  echo "Models frozen and unchanged: MM1-v3.1 2c971828, MM1-v3 b1493082, MM1-v2 3ca4b717, 'v3.1 + contention' F1 (#1.29.1), verify-lay's controls N1+N2, G1, G1+N1 and the layout-blind F1 (#1.29.1.1), 'v3.1 + both' (= F1 here); 'v3.1 + gemmLnc' NOT APPLICABLE (E217 runs no gemmLnc arm)."
  echo "Scope: 599 runs (544 arm + 55 anchor) in 486 cases over E217's seven sessions (aifoundry1 card 1 S1-S4 at 600 MHz, card 0 S1-S3 low power), from the kit copy out/orch/e217-src (SRC-SHA256SUMS.txt 854bd075...)."
  echo "sha256 (the freeze line):"
  sha256sum DECLARED-blind-e217.md DECLARED-blind-e217.json forecasts-nominal-e217.csv forecasts-nominal-e217.json
  echo "supporting (the makers and their records):"
  sha256sum scripts/s02b_nominal.py scripts/s02w_walk.py scripts/s02c_write.py work/step2/fc-nominal.json work/step2/walk-feats-e217.json logs/step1-sha256.txt logs/step2-sha256.txt
  echo "Times (Pacific): declared 11:35:59 (hash logged 11:36:23); nominal forecasts made 11:36:27-11:37:07, files written 11:37:13 (hash logged 11:37:24); this file $(ts)."
  echo "State at the freeze: out/orch/e217-releases.txt holds ${NREL} post lines (the last: '${LASTREL}...'), ${NCLAIM} claim files in out/orch; no E217 session has run, so no E217 datum exists."
  echo "Label rule (the declaration's section g): BLIND for a session whose first datum comes after this freeze is posted; a session whose first datum precedes the post is UNREAD for it (POST-READ if a lab lane read its data first)."
  echo "Still to come (step 4): counts-e217, the switch counts of E217's 21 new tile kinds from the tile files alone (RTL bench, Verilator 5.042), then COUNTS-FROZEN.txt; group S's switch-route energy takes COUNTS-FROZEN.txt's post time by the same rule."
} > "$F"
cat "$F"
echo "FROZEN.txt sha256 $(sha256sum "$F" | cut -c1-64)"
