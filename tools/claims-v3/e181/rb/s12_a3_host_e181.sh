#!/usr/bin/env bash
# E181, step 12 (new; the E181 kit verifier's fault 3, Fri 6 Nov 2026; the kit's README.md.dated-note-1.md): A6-5's reported host readings,
# the host's own temperature sensors at the session's start and end, as E176's lane read them (its room-rule/hostwin-*.out, committed with
# E176's data, 5db7bcf7): hwmon's nvme (temp1, the composite), coretemp (temp1-temp9), acpitz_0 and acpitz_1, every 10 s for 120 s (13
# samples), each sensor's mean, min, max and count. READ only: sysfs files under /sys/class/hwmon, no device opened, no lock, no command to
# the card, never et-who's names. `start` runs after step 10 and right before step 11's launch; `end` after step 20 reads the session's end
# (exit 0, or 16 at a gate). Each refuses (10) while a card session of ours runs on the box, so it never runs beside one. It writes
# build/e181/host-start.out or host-end.out on the box (collected with the logs by step 22 v2 into logs/, where M11's scorer v4 reports
# them under A6-5) and prints the NVMe composite and the coretemp 2-9 mean. Reported, never a gate.
#
#   bash tools/claims-v3/e181/rb/s12_a3_host_e181.sh start|end
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common_e181.sh"
rb_init s12_a3_host
act=${1:-}
case "$act" in start|end) ;; *) rb_die $RB_E_USAGE "usage: s12_a3_host_e181.sh start|end" ;; esac
HW=/sys/class/hwmon; EVERY=10
if [ "${RB_DESKTEST:-}" = 1 ]; then HW=${RB_HWMON:-$HW}; EVERY=${RB_HOST_EVERY_S:-$EVERY}; fi   # the desk test's stand-ins, read only with RB_DESKTEST=1
f=$(rb_file "host-$act")
{ rb_prelude aifoundry3
  echo "ACT=$act; HW=$(printf '%q' "$HW"); EVERY=$EVERY"
  cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on aifoundry3: the host window waits (A6-5 reads the host before and after the session)"; exit 3; fi
mkdir -p build/e181
O=build/e181/host-$ACT.out
{ date '+%F %T %Z'
  HW="$HW" EVERY="$EVERY" python3 - <<'PY'
import glob, os, time
hw, every = os.environ["HW"], float(os.environ["EVERY"])
def read():
    out = {}
    for h in sorted(glob.glob(hw + "/hwmon*")):
        try:
            name = open(h + "/name").read().strip()
        except OSError:
            continue
        if name not in ("coretemp", "acpitz_0", "acpitz_1", "nvme"):
            continue
        for t in sorted(glob.glob(h + "/temp*_input")):
            try:
                out[name + ":" + os.path.basename(t)] = int(open(t).read()) / 1000.0
            except (OSError, ValueError):
                pass
    return out
acc = {}
for i in range(13):
    for k, v in read().items():
        acc.setdefault(k, []).append(v)
    if i < 12:
        time.sleep(every)
for k, v in acc.items():
    print("%-22s mean %.3f  min %.2f  max %.2f  n %d" % (k, sum(v) / len(v), min(v), max(v), len(v)))
if not acc:
    print("no hwmon sensor read (coretemp, acpitz_0, acpitz_1, nvme)")
PY
  date '+%F %T %Z'
  uptime
} > "$O" 2>&1
cat "$O" | cut -c1-200
nv=$(awk '$1 == "nvme:temp1_input" {print $3}' "$O")
ct=$(awk '$1 ~ /^coretemp:temp[2-9]_input$/ {s += $3; n++} END {if (n) printf "%.3f (%d sensors)", s / n, n}' "$O")
echo "HOST-WINDOW $ACT: nvme temp1 ${nv:-none} C; coretemp 2-9 mean ${ct:-none} C; written to $O"
EOF2
} > "$f"
rb_probe aifoundry3
rb_remote wait aifoundry3 "A6-5's host window ($act): 13 samples 10 s apart, sysfs only" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_refused
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the host window exited $RB_RC: read the output above (A6-5's readings are reported, never a gate)"
rb_has '^HOST-WINDOW ' || rb_die $RB_E_FAIL "no HOST-WINDOW line came back: read the output above"
rb_say "$(grep -m1 '^HOST-WINDOW ' "$RB_CAP") (A6-5: reported, never a gate)"
