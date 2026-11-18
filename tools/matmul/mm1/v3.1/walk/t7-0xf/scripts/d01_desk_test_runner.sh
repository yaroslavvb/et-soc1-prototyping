#!/bin/bash
# t7-0xf (Q221) d01: desk test of the runner (verify-v31trace's vt_run.py, unchanged, bd7f945b...) with this lane's argument form for run
# u2 (mask 0xf; excerpt harts 0, 1, 254; excerpt shires 4 and 31) and a stand-in host (verify-v31trace's fake_host.py, unchanged: no device,
# no simulator), inside slot.sh and nodev.sh (the rule for every desk run of a runner or stand-in), only while THE QUIET DESK FLAG is absent
# and the 1-minute load is at or below 6. The et-who stand-in exists only inside this desk test (nodev.sh has no card node to read).
set -u
W=<W>
L=$W/out/t7-0xf
V=$W/out/v31-trace
[ -e "$W/locks/quiet-desk-aifoundry2" ] && { echo "QUIET DESK FLAG up: not running"; exit 9; }
read l1 rest < /proc/loadavg
awk -v l="$l1" 'BEGIN{exit !(l<=6.0)}' || { echo "LOAD $l1 ABOVE 6: not running"; exit 6; }
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
D=$L/work/desk_runner
mkdir -p "$D"
cp "$V/traces/trace_run.py" "$D/trace_run_v31.py"
sha256sum "$D/trace_run_v31.py" "$L/scripts/vt_run.py"
cp "$L/scripts/fake_host.py" "$D/fake_host.py"; chmod +x "$D/fake_host.py"
rm -rf "${D:?}/run1"
mkdir -p "$D/fakebin"
printf '#!/bin/bash\n# desk stand-in for et-who inside nodev.sh (no card node there): the runner\x27s refusal path is tested on aifoundry3\necho "No process holds an ET-SoC-1 device node or card lock."\n' > "$D/fakebin/et-who"
chmod +x "$D/fakebin/et-who"
export PATH="$D/fakebin:$PATH"
cd "$D" || exit 3
sel=()
for s in 0 1 2 3 4 31; do sel+=(--log-sel "$s,ffffffffffffffff"); done
bash "$W/slot.sh" bash "$W/nodev.sh" /usr/bin/python3 -I -B "$L/scripts/vt_run.py" --name deskrun-u2form --host "$D/fake_host.py" \
  --elf "$D/fake_host.py" --tile "$D/fake_host.py" --arm gemmL1x1x16 --mask 0xf "${sel[@]}" \
  --excerpt-hart 0 --excerpt-hart 1 --excerpt-hart 254 --excerpt-shire 4 --excerpt-shire 31 --trace-run "$D/trace_run_v31.py" \
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
print("hart0 n_events", h0["n_events"], "lines_read", h0["lines_read"], "written", h0["lines_written"], "mismatch", h0["line_mismatch"], "instr", h0["instr_by_mode"])
print("mine lines", m["lines"], "instr", m["instr"], "start", m["start"])
print("meta mask", s["meta"]["mask"], "log_sel", s["meta"]["log_sel"], "sparsity", s["meta"]["sparsity"], "host_rc", s["meta"]["host_rc"])
for f in sorted(os.listdir(d)):
    if f.startswith("excerpt"):
        n = sum(1 for _ in gzip.open(os.path.join(d, f), "rb"))
        print(f, n, "lines")
PY
