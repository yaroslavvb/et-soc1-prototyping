#!/usr/bin/env bash
# Q139(k): the C-logging host in place of a runner's sparsity_host, for a runner that takes --sparsity <program>
# (run_e78.py and the runners built on it). Every argument passes through unchanged; it appends --c-log "$CCHECK_LOG"
# --c-poison, and --kernel <ELF> only when the runner passes no --kernel of its own. Only --test fma reads them.
# exec keeps the PID, so the runner's timeout and signals reach the host itself. No device command of its own.
#
#   CCHECK_LOG=<pass dir>/c-log.jsonl ... --sparsity tools/claims-v3/ccheck/sparsity_ccheck.sh ...
#
# The kernel (fix pass of Tue 3 Nov 2026). The host keeps the LAST --kernel it is given, so the wrapper never appends one
# over the runner's: E143's runner on aifoundry2 passes --kernel build/sparsity_t2/kernel/sparsity.elf, and E160's
# C-checked launches must run that ELF, as E143's power passes did. With no --kernel from the runner the wrapper adds
# CCHECK_KERNEL, else build/sparsity/kernel/sparsity.elf (the ELF the run_e78 runners' host loads). CCHECK_KERNEL set
# AND a runner's --kernel whose sha256 differs: refused (exit 2) before the host starts.
# Before the host starts, the wrapper appends one record to the C log naming both binaries and their sha256
# ({"ccheck":1,"kind":"host",...}); ccheck.py attaches it to every launch that follows it in the log.
#
# CCHECK_HOST overrides the binary (build/ccheck/b/host/sparsity_host, from build_host_ccheck.sh). A runner's preflight
# that greps its --sparsity for 'file:', 'int8', 'fp16', '--dump-tiles' or '--stop-file' finds them on this line: the
# patched host has them all (patch_host_ccheck.py).
set -u
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$HERE/../../.." && pwd)
BIN=${CCHECK_HOST:-$ROOT/build/ccheck/b/host/sparsity_host}
: "${CCHECK_LOG:?set CCHECK_LOG to the C log file of the pass}"
[ -x "$BIN" ] || { echo "sparsity_ccheck: no $BIN (run tools/claims-v3/ccheck/build_host_ccheck.sh)" >&2; exit 2; }
sha() {
  if command -v sha256sum > /dev/null 2>&1; then sha256sum "$1"; else shasum -a 256 "$1"; fi | cut -d' ' -f1
}
esc() {
  local s=${1//\\/\\\\}
  printf '%s' "${s//\"/\\\"}"
}
RUNNER_ELF=
prev=
for x in "$@"; do
  [ "$prev" = "--kernel" ] && RUNNER_ELF=$x
  prev=$x
done
if [ -n "$RUNNER_ELF" ]; then
  ELF=$RUNNER_ELF
  FROM=runner
else
  ELF=${CCHECK_KERNEL:-$ROOT/build/sparsity/kernel/sparsity.elf}
  FROM=default
  [ -n "${CCHECK_KERNEL:-}" ] && FROM=CCHECK_KERNEL
fi
[ -f "$ELF" ] || { echo "sparsity_ccheck: no kernel $ELF" >&2; exit 2; }
ELF_SHA=$(sha "$ELF")
if [ "$FROM" = runner ] && [ -n "${CCHECK_KERNEL:-}" ]; then
  [ -f "$CCHECK_KERNEL" ] || { echo "sparsity_ccheck: no kernel $CCHECK_KERNEL (CCHECK_KERNEL)" >&2; exit 2; }
  if [ "$(sha "$CCHECK_KERNEL")" != "$ELF_SHA" ]; then
    echo "sparsity_ccheck: the runner's --kernel $ELF is not CCHECK_KERNEL $CCHECK_KERNEL (sha256 differ): refused" >&2
    exit 2
  fi
fi
printf '{"ccheck":1,"kind":"host","host":"%s","host_sha256":"%s","kernel":"%s","kernel_sha256":"%s","kernel_from":"%s"}\n' \
  "$(esc "$BIN")" "$(sha "$BIN")" "$(esc "$ELF")" "$ELF_SHA" "$FROM" >> "$CCHECK_LOG"
if [ "$FROM" = runner ]; then
  exec "$BIN" "$@" --c-log "$CCHECK_LOG" --c-poison
fi
exec "$BIN" "$@" --kernel "$ELF" --c-log "$CCHECK_LOG" --c-poison
