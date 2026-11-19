# counts-e214 (Q225, track A): common settings, sourced by this lane's scripts. No device is opened by anything here.
W=<W>
L=$W/out/counts-e214
LAB=<LAB>
CORE=<CORE_ET>
CORE_REV=b38a1a31da67efe00c61e983e64b892c58080115   # the core-et commit E210, sw-design-a and v31-counts built against
MAINREV=8bde0182e66646cb67f9589b98c91a8b3a68b50e    # GitHub main = LAB HEAD when this lane started (09:14 PST Thu 19 Nov 2026)
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export GIT_OPTIONAL_LOCKS=0
export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=url.https://github.com/.insteadOf GIT_CONFIG_VALUE_0=git@github.com:
export PATH=<VERILATOR_BIN>:$PATH
PY="/usr/bin/python3 -I -B"
ts() { TZ=America/Los_Angeles date '+%a %d %b %Y %H:%M:%S %Z'; }
plog() { echo "$(ts) $*" >> "$L/logs/progress.txt"; }
quiet_flag() { [ -e "$W/locks/quiet-desk-aifoundry2" ]; }
load1() { cut -d' ' -f1 /proc/loadavg; }
# wait (at most $1 seconds, default 480) while the 1-minute load is above 6 or the quiet-desk flag stands; 0 when clear, 9 if not
wait_clear() {
  local lim=${1:-480} t0; t0=$(date +%s)
  while :; do
    if ! quiet_flag && awk -v l="$(load1)" 'BEGIN{exit !(l<=6.0)}'; then return 0; fi
    [ $(( $(date +%s) - t0 )) -ge "$lim" ] && return 9
    sleep 15
  done
}
