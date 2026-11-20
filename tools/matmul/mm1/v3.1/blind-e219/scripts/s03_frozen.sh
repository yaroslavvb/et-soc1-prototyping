#!/bin/bash
# decl-e219 (Q232) step 3: FROZEN.txt, the freeze line's content (the declaration and the nominal forecasts, final), for the orchestrator to post
# on the Discussion. Reads only this lane's files and out/orch/e219-releases.txt (the claim state); writes FROZEN.txt once (refuses to overwrite).
#   bash s03_frozen.sh "<declared time>" "<declaration hash logged time>" "<forecasts made window>" "<forecast hash logged time>"
set -u
. <W>/out/decl-e219/scripts/env.sh
F=$L/FROZEN.txt
[ -e "$F" ] && { echo "FROZEN.txt exists: not overwritten"; exit 4; }
cd "$L" || exit 2
T1=${1:?declared time}; T1H=${2:?}; T2=${3:?}; T2H=${4:?}
NREL=$(grep -c '^#14' "$W/out/orch/e219-releases.txt")
LASTREL=$(grep '^#14' "$W/out/orch/e219-releases.txt" | tail -1 | cut -c1-40)
NCLAIM=$(ls "$W/out/orch" | grep -c '^claim-')
CLAIMS=$(ls "$W/out/orch" | grep '^claim-' | tr '\n' ' ')
E219CLAIM=$(grep '^#14' "$W/out/orch/e219-releases.txt" | grep -c 'CLAIM')
V32=$(python3 -c "import json; d=json.load(open('$L/work/v32-status.json')); print(d['status'])")
MODELS="MM1-v3.1 2c971828, MM1-v3 b1493082, MM1-v2 3ca4b717"
[ "$V32" = INCLUDED ] && MODELS="$MODELS, MM1-v3.2 (GitHub main $(cut -c1-8 "$L/work/lab-commit-v32.txt"))"
{
  echo "decl-e219 (round Q232): the lab's BLIND test of its frozen matmul models on E219 (#14, 1119-mmsweep5), DECLARED and its nominal forecasts FROZEN at $(ts), before any E219 datum exists."
  echo "MM1's domain first: 139 of E219's 314 cases are IN DOMAIN (rgm136's gemmL loop: the 1x1x1 controls, the gap cells and the anchor, 44 cases; run_gemm's c-arms in the models' table: gemmc1, gemmc4s, gemmc8s, gemmc16, gemmc16s, 22 cases, and the gemmc16r<R> ladder, 73 cases) and forecast; 175 are OUT OF DOMAIN (gemmc at other B, R or shared C 121, gemmh 32, gemm packed by k 10, mm16 and mm128 6, tenb 6): no frozen MM1 has a form for them, so no forecast; the scores report them apart."
  echo "Models frozen and unchanged: $MODELS, 'v3.1 + contention' F1 (#1.29.1), verify-lay's controls N1+N2, G1, G1+N1 and the layout-blind F1 (#1.29.1.1), 'v3.1 + both' (= F1 here); 'v3.1 + gemmLnc' NOT APPLICABLE (E219 runs no gemmLnc arm). MM1-v3.2: $V32 at the declaration (work/v32-status.json)."
  echo "Scope: 392 runs (arm + anchor) in 314 cases over E219's five sessions (aifoundry1 card 1 S1-S3 at 600 MHz, card 0 S1-S2 low power), from the kit copy out/orch/e219-src (SRC-SHA256SUMS.txt 247456da...); E219 designs no tile: no counts are made."
  echo "sha256 (the freeze line):"
  sha256sum DECLARED-blind-e219.md DECLARED-blind-e219.json forecasts-nominal-e219.csv forecasts-nominal-e219.json
  echo "supporting (the makers and their records):"
  sha256sum scripts/s02b_nominal.py scripts/s02w_walk.py scripts/s02c_write.py work/step2/fc-nominal.json work/step2/walk-feats-e219.json logs/step1-sha256.txt logs/step2-sha256.txt
  echo "Times (Pacific): declared $T1 (hash logged $T1H); nominal forecasts made $T2 (hash logged $T2H); this file $(ts)."
  if [ "$E219CLAIM" = 0 ]; then
    echo "State at the freeze: out/orch/e219-releases.txt holds ${NREL} post lines (the last: '${LASTREL}...') and no E219 claim; ${NCLAIM} claim files in out/orch (${CLAIMS:-none}; the claim file names the session it holds); no E219 session has run, so no E219 datum exists."
  else
    echo "State at the freeze: out/orch/e219-releases.txt holds ${NREL} post lines (the last: '${LASTREL}...') and ${E219CLAIM} E219 CLAIM lines: a claim came before this freeze, so each session's label follows the freeze post's time against its first card command; ${NCLAIM} claim files in out/orch (${CLAIMS:-none})."
  fi
  echo "Label rule (the declaration's section g): BLIND for a session whose first datum comes after this freeze is posted; a session whose first datum precedes the post is UNREAD for it (POST-READ if a lab lane read its data first)."
} > "$F"
cat "$F"
echo "FROZEN.txt sha256 $(sha256sum "$F" | cut -c1-64)"
