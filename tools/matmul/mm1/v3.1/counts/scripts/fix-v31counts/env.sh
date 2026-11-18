# fix-v31counts (Q217): common settings, sourced by this lane's scripts. No device is opened by anything here.
W=<W>
L=$W/out/fix-v31counts
VC=$W/out/v31-counts                 # the lane whose counts this lane fixes (read only)
VV=$W/out/verify-v31counts           # its verifier (read only)
LAB=<LAB>
MAINREV=6efdb0024cc5a44b46c4d11f71047bc1d12f611c   # GitHub main = LAB HEAD at 06:09 PST Wed 18 Nov 2026 (the counts' sources)
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export GIT_OPTIONAL_LOCKS=0
export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=url.https://github.com/.insteadOf GIT_CONFIG_VALUE_0=git@github.com:
PY="/usr/bin/python3 -I -B"
ts() { TZ=America/Los_Angeles date '+%a %d %b %Y %H:%M:%S %Z'; }
plog() { echo "$(ts) $*" >> "$L/logs/progress.txt"; }
quiet_flag() { [ -e "$W/locks/quiet-desk-aifoundry2" ]; }
load1() { cut -d' ' -f1 /proc/loadavg; }
# wait (at most $1 seconds, default 480) while the 1-minute load is above 6 or the quiet-desk flag stands; return 0 when clear, 9 if not
wait_clear() {
  local lim=${1:-480} t0; t0=$(date +%s)
  while :; do
    if ! quiet_flag && awk -v l="$(load1)" 'BEGIN{exit !(l<=6.0)}'; then return 0; fi
    [ $(( $(date +%s) - t0 )) -ge "$lim" ] && return 9
    sleep 15
  done
}
