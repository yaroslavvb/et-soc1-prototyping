# decl-e219 (Q232): shared shell settings for this lane's scripts. Sourced, never run. (decl-e217's env.sh, the lane renamed.)
W=<W>
L=$W/out/decl-e219
LAB=<LAB>
PY=/usr/bin/python3
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=url.https://github.com/.insteadOf GIT_CONFIG_VALUE_0=git@github.com:
ts() { TZ=America/Los_Angeles date '+%a %d %b %Y %H:%M:%S %Z'; }
load1() { cut -d' ' -f1 /proc/loadavg; }
plog() { echo "$(ts) $*" >> "$L/logs/progress.txt"; }
# wait (bounded) while the 1-minute load is above 6; $1 = seconds at most; rc 0 when clear, 1 when not
wait_load() {
  local lim=${1:-480} t0
  t0=$(date +%s)
  while awk -v l="$(load1)" 'BEGIN{exit !(l > 6)}'; do
    [ $(( $(date +%s) - t0 )) -ge "$lim" ] && return 1
    sleep 20
  done
  return 0
}
