#!/usr/bin/env bash
# Q139(k): the C-logging host in place of build/sparsity/host/sparsity_host, for a runner that takes --sparsity <program>
# (run_e78.py and the runners built on it). Every argument passes through unchanged; it appends --kernel <the existing
# build's ELF, so the device code is byte-identical> and --c-log "$CCHECK_LOG" --c-poison. Only --test fma reads them.
# exec keeps the PID, so the runner's timeout and signals reach the host itself. No device command of its own.
#
#   CCHECK_LOG=<pass dir>/c-log.jsonl ... --sparsity tools/claims-v3/ccheck/sparsity_ccheck.sh ...
#
# CCHECK_HOST and CCHECK_KERNEL override the binary (build/ccheck/b/host/sparsity_host, from build_host_ccheck.sh) and
# the ELF (build/sparsity/kernel/sparsity.elf). A runner's preflight that greps its --sparsity for 'file:', 'int8',
# 'fp16', '--dump-tiles' or '--stop-file' finds them on this line: the patched host has them all (patch_host_ccheck.py).
set -u
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$HERE/../../.." && pwd)
BIN=${CCHECK_HOST:-$ROOT/build/ccheck/b/host/sparsity_host}
ELF=${CCHECK_KERNEL:-$ROOT/build/sparsity/kernel/sparsity.elf}
: "${CCHECK_LOG:?set CCHECK_LOG to the C log file of the pass}"
[ -x "$BIN" ] || { echo "sparsity_ccheck: no $BIN (run tools/claims-v3/ccheck/build_host_ccheck.sh)" >&2; exit 2; }
[ -f "$ELF" ] || { echo "sparsity_ccheck: no kernel $ELF" >&2; exit 2; }
exec "$BIN" "$@" --kernel "$ELF" --c-log "$CCHECK_LOG" --c-poison
