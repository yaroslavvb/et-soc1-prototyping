#!/bin/bash
# decl-e221 (Q235) step 3: FROZEN.txt, the freeze line's content (the declaration and the nominal forecasts, final), for the orchestrator to post
# on the Discussion (#15). Reads only this lane's files, out/orch/e221-releases.txt and the claim files (the claim state) and
# out/orch/q234-frozen-posts.txt (the candidates' post lines); writes FROZEN.txt once (refuses to overwrite). decl-e219's s03_frozen.sh in form.
#   bash s03_frozen.sh "<declared time>" "<declaration hash logged time>" "<forecasts made window>" "<forecast hash logged time>"
set -u
. <W>/out/decl-e221/scripts/env.sh
F=$L/FROZEN.txt
[ -e "$F" ] && { echo "FROZEN.txt exists: not overwritten"; exit 4; }
cd "$L" || exit 2
T1=${1:?declared time}; T1H=${2:?}; T2=${3:?}; T2H=${4:?}
NREL=$(grep -c '^#15' "$W/out/orch/e221-releases.txt")
LASTREL=$(grep '^#15' "$W/out/orch/e221-releases.txt" | tail -1 | cut -c1-48)
NCLAIM=$(ls "$W/out/orch" | grep -c '^claim-')
CLAIMS=$(ls "$W/out/orch" | grep '^claim-' | tr '\n' ' ')
E221CLAIM=$(grep '^#15' "$W/out/orch/e221-releases.txt" | grep -c 'CLAIM')
L3POST=$(grep -c 'l3-edge' "$W/out/orch/q234-frozen-posts.txt")
{
  echo "decl-e221 (round Q235): the lab's BLIND test of its frozen matmul models on E221 (#15, 1120-mmsweep6), DECLARED and its nominal forecasts FROZEN at $(ts), before any E221 datum it could read (no E221 run has run)."
  echo "MM1's domain first: all 733 of E221's cases (811 runs: 740 arm + 71 anchor, over 345 gemmL arms and the anchor in nine sessions) are IN DOMAIN: every arm is rgm136's cooperative gemmL loop, and every declared model has a form for every case (probe p01: 733/733 in MM1-v3.2, MM1-v3.1, MM1-v3 and MM1-v2); OUT OF DOMAIN: none. Classes: the core-group masks 392, the 1x1x1 cells at new masks 79, KB = 1 72, the int8 L2 point 54, MB = 3 ladders 47, deep K 30, the held walks 23, BW 18, NB = 1 15, the anchor 3; 461 cases at shire subsets (65 masks)."
  echo "Models frozen and unchanged: MM1-v3.2 (4e386f75, the lab's newest: the pass rule's model), MM1-v3.1 2c971828, MM1-v3 b1493082, MM1-v2, 'v3.1 + contention' F1 (#1.29.1), verify-lay's controls N1+N2, G1, G1+N1 and the layout-blind F1 (#1.29.1.1), 'v3.1 + both' (= F1 here); REPORTED: the MM1-v3.3 candidates 'MM1-v3.2 + posimb' (layout2, FROZEN 81d04c97, 05:39:48) at the subset masks and 'MM1-v3.2 + L3S' (l3-edge, FROZEN e8216cbb, 05:57:20; its post line in out/orch/q234-frozen-posts.txt: $L3POST) at the full chip, by their own frozen makers; NOT APPLICABLE (no gemmLnc arm): 'v3.1 + gemmLnc' and 'MM1-v3.2 + gemmLnc term AF4' (lnc-form, FROZEN 5373973f)."
  echo "Cards: aifoundry1 card 1 at 600 MHz; aifoundry1 card 0 low power and aifoundry2 card 0 under their governors (nominal 800 MHz). Kit copy out/orch/e221-src (SRC-SHA256SUMS.txt 5680112f...); E221 designs no tile: no counts are made."
  echo "sha256 (the freeze line):"
  sha256sum DECLARED-blind-e221.md DECLARED-blind-e221.json forecasts-nominal-e221.csv forecasts-nominal-e221.json
  echo "supporting (the makers and their records):"
  sha256sum scripts/s02b_nominal.py scripts/s02w_walk.py scripts/s02f_cands.py scripts/s02c_write.py work/step2/fc-nominal.json work/step2/walk-feats-e221.json work/step2/cand-feats-e221.json logs/step1-sha256.txt logs/step2-sha256.txt
  echo "Times (Pacific): declared $T1 (hash logged $T1H); nominal forecasts made $T2 (hash logged $T2H); this file $(ts)."
  echo "State at the freeze: out/orch/e221-releases.txt holds ${NREL} post lines (the last: '${LASTREL}...'), ${E221CLAIM} of them a CLAIM (#15.1, S1 on aifoundry1 card 1, whose start at 05:53:56 was stopped at 05:55:27 with no run run: #15.2.1, kept apart, not scored); ${NCLAIM} claim files in out/orch (${CLAIMS:-none})."
  echo "Label rule (the declaration's section g): BLIND for a session whose first datum (first card command) comes after this freeze is posted; a session whose first datum precedes the post is UNREAD for it (POST-READ if a lab lane read its data first). S1, claimed again whole after the post, is labelled by its own first card command."
} > "$F"
cat "$F"
echo "FROZEN.txt sha256 $(sha256sum "$F" | cut -c1-64)"
