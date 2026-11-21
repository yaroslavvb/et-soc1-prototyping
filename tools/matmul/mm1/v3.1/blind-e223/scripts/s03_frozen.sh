#!/bin/bash
# decl-e223 (Q239) step 3: FROZEN.txt, the moment steps 1-2 are final: the sha256 lines of the declaration and the nominal forecasts (the
# freeze line), the step hash files, the time; W/out/orch/q238-frozen-posts.txt read once more just before (copied to
# work/q238-frozen-posts-at-freeze.txt; what it held is named); the frozen files made read-only (444); msg/to-orchestrator-frozen.txt
# (one line: the time and FROZEN.txt's sha256) for the orchestrator to post on #16. Refuses to overwrite.
set -u
. <W>/out/decl-e223/scripts/env.sh
cd "$L" || exit 2
[ -e FROZEN.txt ] && { echo "FROZEN.txt exists: not overwritten"; exit 4; }
for f in logs/step1-sha256.txt logs/step2-sha256.txt; do [ -e "$f" ] || { echo "$f missing: stop"; exit 3; }; done
sha256sum -c logs/step1-sha256.txt > logs/step1-recheck.txt 2>&1 || { echo "step 1 files changed: stop"; cat logs/step1-recheck.txt | grep -v ': OK$'; exit 5; }
sha256sum -c logs/step2-sha256.txt > logs/step2-recheck.txt 2>&1 || { echo "step 2 files changed: stop"; exit 5; }
cp -a "$W/out/orch/q238-frozen-posts.txt" work/q238-frozen-posts-at-freeze.txt
QT=$(ts)
mm_disk=$( [ -e "$W/out/mask-mesh/FROZEN.txt" ] && sha256sum "$W/out/mask-mesh/FROZEN.txt" | cut -c1-64 || echo none)
mc_disk=$( [ -e "$W/out/mask-ceiling/FROZEN.txt" ] && sha256sum "$W/out/mask-ceiling/FROZEN.txt" | cut -c1-64 || echo none)
mm_posted=$(grep -c "mask-mesh .*FROZEN.txt $mm_disk" work/q238-frozen-posts-at-freeze.txt)
mc_posted=$(grep -c "mask-ceiling .*FROZEN.txt $mc_disk" work/q238-frozen-posts-at-freeze.txt)
NOW=$(ts)
{
  echo "# decl-e223 (round Q239): FROZEN at $NOW (Pacific): the lab's declaration and nominal forecasts for its BLIND test of E223, before any E223 datum"
  echo "# the freeze line (post these on #16): the declaration, then the nominal forecasts"
  sha256sum DECLARED-blind-e223.md DECLARED-blind-e223.json forecasts-nominal-e223.csv forecasts-nominal-e223.json
  echo "# the order: the declaration hashed $(grep -m1 'step 01 DECLARED' logs/progress.txt | cut -c1-24) (logs/step1-sha256.txt $(sha256sum logs/step1-sha256.txt | cut -c1-16)...), then the nominal forecasts made 02:19:40-02:21:38 PST and hashed (logs/step2-sha256.txt $(sha256sum logs/step2-sha256.txt | cut -c1-16)...), then this file"
  sha256sum logs/step1-sha256.txt logs/step2-sha256.txt work/step2/fc-nominal.json
  echo "# models: MM1-v3.2 (the registered baseline, 4e386f75), MM1-v3.3 = 'MM1-v3.2 + AF4' (E222's SEL; equal to MM1-v3.2 on every E223 case), MM1-v3.1 (2c971828), MM1-v3 (b1493082), MM1-v2; REPORTED: Q234's posimb and L3S, the compositions by E222's and E224's construction, Q238's 'MM1-v3.2 + posimb-mask' and 'MM1-v3.2 + AF4 + posimb-mask'"
  echo "# W/out/orch/q238-frozen-posts.txt read again at $QT (work/q238-frozen-posts-at-freeze.txt): mask-posimb posted 0cd8e9da = on disk: IN this freeze; mask-mesh on disk $mm_disk, posted lines matching it: $mm_posted (the line posted at 02:03:18 reads 3d4942fa): NOT in this freeze; mask-ceiling on disk $mc_disk, matching posted lines: $mc_posted: NOT in this freeze (the declaration's rule: a candidate qualifying after its 02:19:24 read joins only by a dated amendment hashed before E223's first datum)"
  echo "# 695 cases (803 runs) x 13 models, all IN MM1's domain (none OUT OF DOMAIN); step 4 (switch counts) NOT NEEDED: E223 designs no tile; no E223 datum read by this lane; /usr/bin/python3 3.12.3"
} > FROZEN.txt
chmod 444 DECLARED-blind-e223.md DECLARED-blind-e223.json forecasts-nominal-e223.csv forecasts-nominal-e223.json FROZEN.txt
FS=$(sha256sum FROZEN.txt | cut -c1-64)
echo "$NOW decl-e223 FROZEN.txt sha256 $FS" > msg/to-orchestrator-frozen.txt
cat FROZEN.txt
echo "FROZEN.txt $FS"
cat msg/to-orchestrator-frozen.txt
