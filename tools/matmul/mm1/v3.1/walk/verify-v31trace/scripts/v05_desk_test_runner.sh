#!/bin/bash
# verify-v31trace (Q217) v05: desk test of this lane's runner vt_run.py with a stand-in host (fake_host.py: no device, no simulator),
# inside slot.sh and nodev.sh (the rule for every desk run of a runner or stand-in), only while THE QUIET DESK FLAG is absent.
set -u
W=<W>
L=$W/out/verify-v31trace
V=$W/out/v31-trace
[ -e "$W/locks/quiet-desk-aifoundry2" ] && { echo "QUIET DESK FLAG up: not running"; exit 9; }
read l1 rest < /proc/loadavg
awk -v l="$l1" 'BEGIN{exit !(l<=6.0)}' || { echo "LOAD $l1 ABOVE 6: not running"; exit 6; }
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
D=$L/work/desk_runner
mkdir -p "$D"
cp "$V/traces/trace_run.py" "$D/trace_run_v31.py"
sha256sum "$D/trace_run_v31.py"
cp "$L/scripts/fake_host.py" "$D/fake_host.py"; chmod +x "$D/fake_host.py"
rm -rf "${D:?}/run1"
mkdir -p "$D/fakebin"
printf '#!/bin/bash\n# desk stand-in for et-who inside nodev.sh (no card node there): the runner\x27s refusal path is tested on aifoundry3\necho "No process holds an ET-SoC-1 device node or card lock."\n' > "$D/fakebin/et-who"
chmod +x "$D/fakebin/et-who"
export PATH="$D/fakebin:$PATH"
cd "$D" || exit 3
bash "$W/slot.sh" bash "$W/nodev.sh" /usr/bin/python3 -I -B "$L/scripts/vt_run.py" --name deskrun1 --host "$D/fake_host.py" \
  --elf "$D/fake_host.py" --tile "$D/fake_host.py" --arm gemmL1x1x16 --mask 0x1111 --log-sel 0,ffffffffffffffff --log-sel 1,ffffffffffffffff \
  --log-sel 31,ffffffffffffffff --excerpt-hart 0 --excerpt-hart 1 --excerpt-shire 1 --excerpt-shire 31 --trace-run "$D/trace_run_v31.py" \
  --out "$D/run1" --timeout 60
echo "runner rc=$?"
ls -la "$D/run1"
/usr/bin/python3 -I -B - "$D/run1" <<'PY'
import gzip, json, sys, os
d = sys.argv[1]
s = json.load(gzip.open(os.path.join(d, "summary.json.gz"), "rt"))
m = json.load(gzip.open(os.path.join(d, "mine.json.gz"), "rt"))
print("summary harts", sorted(s["harts"], key=int), "warn", s["warn"], "unparsed", s["unparsed_tensor"])
h0 = s["harts"]["0"]
print("hart0 events", h0["events"])
print("hart0 lines_read", h0["lines_read"], "written", h0["lines_written"], "mismatch", h0["line_mismatch"], "instr", h0["instr_by_mode"])
print("mine lines", m["lines"], "instr", m["instr"], "start", m["start"])
print("meta sparsity", s["meta"]["sparsity"], "stderr", s["meta"]["stderr_lines"], "host_rc", s["meta"]["host_rc"])
for f in sorted(os.listdir(d)):
    if f.startswith("excerpt"):
        n = sum(1 for _ in gzip.open(os.path.join(d, f), "rb"))
        print(f, n, "lines")
PY
