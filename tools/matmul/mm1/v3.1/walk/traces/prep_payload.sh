#!/bin/bash
# v31-trace (Q217): gather what the traced runs need on aifoundry3 into one tar: trace_run.py, r_prep.sh, r_trace.sh, and E212's fp32 zeros
# tile file (the mech-MK arms' tile, read from the shared lab clone, read only). Usage: bash prep_payload.sh <version>. No build inputs: the kernels and hosts are kit-e211's
# aifoundry3 builds, copied and checked against E211's pins by r_prep.sh.
set -u
W=<W>
LAB=<LAB>
L=$W/out/v31-trace
V=${1:?give a payload version, e.g. v2}
P=$L/work/payload-$V/q217-v31-trace
[ -e "$P" ] && { echo "payload dir exists: $P"; exit 3; }
mkdir -p "$P/tiles/fp32"
cp "$L/traces/trace_run.py" "$L/traces/r_prep.sh" "$L/traces/r_trace.sh" "$P/"
cp "$LAB/tools/claims-v3/e212/proposal/src/tiles/fp32/zeros.bin" "$P/tiles/fp32/zeros.bin"
( cd "$LAB" && echo "LAB HEAD $(git rev-parse HEAD)" ) > "$P/SOURCE.txt"
echo "tiles/fp32/zeros.bin = tools/claims-v3/e212/proposal/src/tiles/fp32/zeros.bin (E212's mech-MK tile)" >> "$P/SOURCE.txt"
cd "$P" && find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS
cd "$L/work/payload-$V" && tar czf q217-v31-trace-$V.tgz q217-v31-trace && sha256sum q217-v31-trace-$V.tgz
cat "$P/SHA256SUMS"
