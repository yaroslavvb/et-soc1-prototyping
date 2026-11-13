#!/usr/bin/env bash
# One host run in the profiling simulator, counted: the emulator's instruction log streams through a FIFO into
# count_kernel.py (nothing of the log is kept), and its block profile and the host's own output are kept.
#
#   run_counted.sh --dis KERNEL.dis --out NEWDIR [--log-sel '-ls 0,ffffffffffffffff'] [--no-log] [--no-prof] \
#                  [--timeout S] -- HOST_PROGRAM --sysemu ... --sim-args @SIM@ ...
#
# Every word after `--` is the host command, run in NEWDIR (the runtime writes the emulator's log to sysemu.log in
# the host's working directory: the FIFO is put there). A word equal to @SIM@ becomes the simulator options:
# "-dump_prof NEWDIR/prof.txt" (unless --no-prof: a host built against the installed tree has no profile but logs the
# same way) plus, unless --no-log, "-l" and the log selection (default: every hart of shire 0;
# `-ls <shire>,<64-bit hex mask>` and `-lt <hart>` may repeat; logging every hart of a big run is slow, so log the
# shires that work). For the profile the host must be built against the profiling simulator's shadow prefix
# (README.md), or the emulator inside it rejects -dump_prof. Outputs in NEWDIR: counts-log.json (exact counts, every logged hart),
# prof.txt.gz, out.json and err.log (the host's stdout and stderr), counter.out, RUN.txt (the command and exit codes).
# No device: the host must carry --sysemu (refused otherwise). SPDX-License-Identifier: Apache-2.0
set -u
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
dis="" out="" logsel="-ls 0,ffffffffffffffff" log=1 prof=1 tmo=3000
while [ $# -gt 0 ]; do
  case "$1" in
    --dis) dis=$2; shift 2 ;;
    --out) out=$2; shift 2 ;;
    --log-sel) logsel=$2; shift 2 ;;
    --no-log) log=0; shift ;;
    --no-prof) prof=0; shift ;;
    --timeout) tmo=$2; shift 2 ;;
    --) shift; break ;;
    *) echo "run_counted: unknown option $1" >&2; exit 2 ;;
  esac
done
[ -n "$dis" ] && [ -n "$out" ] && [ $# -gt 0 ] || { echo "usage: see the header" >&2; exit 2; }
case " $* " in *" --sysemu "*) ;; *) echo "run_counted: the host command has no --sysemu: refused" >&2; exit 2 ;; esac
[ -e "$out" ] && { echo "run_counted: $out exists; give a new folder" >&2; exit 2; }
dis=$(cd "$(dirname "$dis")" && pwd)/$(basename "$dis")
mkdir -p "$out" && out=$(cd "$out" && pwd)
sim="-vpurf_warn"
[ $prof = 1 ] && sim="$sim -dump_prof $out/prof.txt"
[ $log = 1 ] && sim="$sim -l $logsel"
cmd=()
for w in "$@"; do [ "$w" = "@SIM@" ] && cmd+=("$sim") || cmd+=("$w"); done
cd "$out"
{ printf 'command:'; printf ' %q' "${cmd[@]}"; echo; } | sed "s#$HOME#~#g" > RUN.txt
cpid=""
if [ $log = 1 ]; then
  mkfifo sysemu.log
  timeout "$tmo" nice -n 19 python3 -I -B "$here/count_kernel.py" count --dis "$dis" --log sysemu.log \
    --out counts-log.json --label "$(basename "$out")" > counter.out 2>&1 &
  cpid=$!
fi
t0=$(date +%s)
timeout "$tmo" nice -n 19 "${cmd[@]}" > out.json 2> err.log < /dev/null
hrc=$?
t1=$(date +%s)
crc=0
if [ -n "$cpid" ]; then
  # a host that never opened the log leaves the counter waiting in open(): give it an empty writer
  kill -0 "$cpid" 2> /dev/null && timeout 5 dd if=/dev/null of=sysemu.log 2> /dev/null
  wait "$cpid"; crc=$?
  rm -f sysemu.log
fi
[ -f prof.txt ] && gzip -f prof.txt
echo "host rc=$hrc, ${t1}-${t0} = $((t1 - t0)) s; counter rc=$crc" >> RUN.txt
cat RUN.txt
[ -f counter.out ] && cat counter.out
exit $(( hrc != 0 ? hrc : crc ))
