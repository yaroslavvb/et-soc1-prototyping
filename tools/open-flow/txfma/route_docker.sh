#!/bin/bash
# Q129(a): run pnr_route.tcl in the ORFS container, which is the fix POWER.md asked for.
# The 2022 conda OpenROAD that Q126(e) could install without root stops at DRT-0255 on the
# top-level port nets; this image's OpenROAD is current and its ORFS checkout is the SAME
# commit (64939f371) the published run pinned, so the platform — LEF, liberty, setRC, the RCX
# rules — is byte-identical and the only pin that moves is the tool.
#
#   SQ=$HOME/scratch-q129-route bash tools/open-flow/txfma/route_docker.sh [tag]
#
# Needs: docker (as a user in the docker group, or as root — see the lab's root rule), the
# synthesized netlist in $SQ/in/, and this directory mounted read-only at /flow.
# Writes $SQ/work/pnr-route<tag>/ and $SQ/logs/route<tag>.log.
set -u
SQ=${SQ:-$HOME/scratch-q129-route}
IMG=${IMG:-openroad/orfs:26Q4-229-g64939f371}
TAG=${1:-}
FLOW=${FLOW:-$(cd "$(dirname "$0")" && pwd)}
UIDGID=${UIDGID:-$(id -u):$(id -g)}
CPUS=${CPUS:-8}
NETLIST=${NETLIST:-/sq/in/txfma_mixed.v}
mkdir -p "$SQ/work" "$SQ/logs"

# The container's own script: liberty out of the image's platform, then OpenROAD. Everything
# inside /sq is the host's scratch; /flow is this tool directory, read-only.
cat > "$SQ/run_in.sh" <<'INNER'
set -u
P=/OpenROAD-flow-scripts/flow/platforms/asap7
W=/sq/work
mkdir -p "$W/lib"
# One uncompressed liberty per ASAP7 cell group, the same five files Q126(e)'s setup.sh took.
for g in "$P"/lib/NLDM/asap7sc7p5t_{AO,INVBUF,OA,SIMPLE}_RVT_TT_nldm_*.lib.gz; do
  [ -e "$g" ] || continue
  o=$W/lib/$(basename "$g" .gz); [ -s "$o" ] || zcat "$g" > "$o"
done
for f in "$P"/lib/NLDM/asap7sc7p5t_SEQ_RVT_TT_nldm_*.lib; do
  [ -e "$f" ] || continue
  o=$W/lib/$(basename "$f"); [ -s "$o" ] || cp "$f" "$o"
done
ls -la "$W/lib"
export PATH=/OpenROAD-flow-scripts/tools/install/OpenROAD/bin:$PATH
export SCRATCH=/sq
export PLATFORM=$P
export LIBDIR=$W/lib
openroad -version
exec nice -n 19 openroad -no_init -exit "${TCL:-/flow/pnr_route.tcl}"
INNER

echo "=== $(date -Is) route$TAG: image $IMG, netlist $NETLIST, $CPUS cpus"
docker image inspect "$IMG" --format '{{index .RepoDigests 0}}' || true
nice -n 19 docker run --rm \
  --cpus "$CPUS" --cpu-shares 256 \
  --user "$UIDGID" \
  -e HOME=/sq -e NETLIST="$NETLIST" -e PNROUT="${PNROUT:-/sq/work/pnr-route$TAG}" \
  -e TCL="${TCL:-/flow/pnr_route.tcl}" -e STOP_AFTER="${STOP_AFTER:-}" \
  -e DEF="${DEF:-}" -e SPEF="${SPEF:-}" \
  -e UTIL="${UTIL:-30}" -e DENS="${DENS:-0.55}" \
  -e PINHOR="${PINHOR:-M4}" -e PINVER="${PINVER:-M5}" \
  -e SIGLAYERS="${SIGLAYERS:-M2-M7}" -e CLKLAYERS="${CLKLAYERS:-M4-M7}" \
  -e DRT_BOT="${DRT_BOT:-M2}" -e DRT_TOP="${DRT_TOP:-M9}" \
  -e DRT_ITERS="${DRT_ITERS:-10}" -e COUPLING="${COUPLING:-0.02}" \
  -e CORE_SPACE="${CORE_SPACE:-2}" \
  -v "$SQ":/sq -v "$FLOW":/flow:ro \
  "$IMG" bash /sq/run_in.sh > "$SQ/logs/route$TAG.log" 2>&1
rc=$?
echo "rc=$rc  log $SQ/logs/route$TAG.log"
tail -25 "$SQ/logs/route$TAG.log"
exit $rc
