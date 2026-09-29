#!/usr/bin/env bash
# memp2: run every new kernel path of build/memprobe2 in sys_emu, the functional simulator, before any card time
# (the TensorLoad encodings at every stride, the spreads, the arena source and its scalar warm-up, tensor_wait,
# tensor_error, the timed TensorLoad op). The simulator's checkers are on (mem_check, l1/l2_scp_check, ...).
#
#   bash tools/claims-v3/memp2/sysemu.sh [--quick] [--keep]      from the tree's root; V3_DRY=1 prints the commands
#
# No card is opened: every command carries --sysemu (checked below). But memprobe_host and sys_emu are "device
# processes" to the framework's checks (lib.sh DEV_COMM: ours_running, DV2's foreign_procs), so this refuses while
# any queue, block or series of the framework runs on the host, and on aifoundry2 while DV2 runs (its gate ends a DV2
# pass on such a process) or before MEMP2_AFTER_DV2=1. Run it on aifoundry1 in ~/nekko after deploy.sh --build.
# Slow: each run boots the simulated firmware (about 40 s); all checks about 15-25 min of one core at nice 19.
#
# Checks (shire 0; tloop: minions 0 and 1, 8 loads, one launch): tloop at s64, s256, s1k with the spreads same,
# bank, sub and onebank, the arena at s64 and s256; the four op programs at the smoke's sizes, treload first.
# --quick: treload, and tloop s64, s1k-onebank and the arena at s256 only.
# Pass: every run exits 0, every MEMPROBE line says ok with no tensor_error, every program's results are complete.
# Output: build/memp2-sysemu/<time>/ (the simulator's run directory; removed at the end unless --keep).
# Exit: 0 all pass, 1 a check failed, 2 refused.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
ROOT=$PWD
MP2=$ROOT/build/memprobe2/host/memprobe_host
QUICK=; KEEP=
for a in "$@"; do case "$a" in --quick) QUICK=1 ;; --keep) KEEP=1 ;; *) echo "unknown option $a" >&2; exit 2 ;; esac; done
dry() { [ -n "${V3_DRY:-}" ]; }
say() { echo "$(date +%FT%T) sysemu: $*"; }

# ---- refusals
host=$(hostname)
if [ "$host" = aifoundry2 ]; then
  [ "${MEMP2_AFTER_DV2:-}" = 1 ] || { say "aifoundry2: only after the DV2 validation ends (MEMP2_AFTER_DV2=1): refused"; exit 2; }
  if ! dry; then
    p=$(pgrep -af '[s]chedule-dv2|[t]ools/claims-v3/dv2v?/' 2>/dev/null | cut -c1-160 | tr '\n' ';')
    [ -n "$p" ] && { say "DV2 processes on aifoundry2 ($p): refused"; exit 2; }
  fi
fi
if ! dry; then
  p=$(pgrep -af '[t]ools/claims-v3/(queue\.sh|oh/run_queue\.sh|hp/run_queue\.sh|[a-z0-9_/-]+/(block|series)\.sh)' 2>/dev/null |
      cut -c1-160 | tr '\n' ';')
  [ -n "$p" ] && { say "a framework queue, block or series runs here ($p): refused"; exit 2; }
  [ -x "$MP2" ] || { say "missing $MP2 (deploy.sh <host> --build)"; exit 2; }
  grep -a -q -- '--tloop' "$MP2" || { say "$MP2 is not an MEMPROBE_EXT build"; exit 2; }
  tag="memp2-src:$(sha256sum workloads/memprobe/host/main.cpp | cut -c1-64):$(sha256sum workloads/memprobe/memprobe_args.h | cut -c1-64)"
  grep -a -q -- "$tag" "$MP2" || { say "$MP2 was not built from this tree's sources: rebuild it"; exit 2; }
  [ -x /opt/et/bin/sys_emu ] || { say "no /opt/et/bin/sys_emu"; exit 2; }
fi
case "$host" in aifoundry1) export ET_DEVICES=1 ;; esac   # belt and braces: nothing here opens a card

WD=$ROOT/build/memp2-sysemu/$(date +%Y%m%d-%H%M%S)
mkdir -p "$WD/mp" "$WD/tl"
python3 workloads/memprobe/gen_ops2.py all --out "$WD/mp" --seed 999 --smoke > "$WD/gen.log" 2>&1 || { say "gen_ops2.py failed"; exit 1; }

runs=()   # "name|args..."
for pr in treload rowalt rrd refphase; do
  [ -n "$QUICK" ] && [ "$pr" != treload ] && continue
  runs+=("prog-$pr|--arena 1G --out-dir $WD/mp --program $WD/mp/$pr.ops")
done
tl() { runs+=("tl-$1|--tloop --where $2 --stride $3 --spread $4 --tl-lines 16 --span $5 --shires 0x1 --minions 0x3 --iters 8 --reps 1 --name $1${6:+ $6}"); }
if [ -n "$QUICK" ]; then
  tl s64 scp 64 same 32768; tl s1kq scp 1024 onebank 32768; tl l2-s256 arena 256 same 8192 "--arena 16M"
else
  for st in 64 256 1024; do for sp in same bank sub onebank; do tl "s$st-$sp" scp "$st" "$sp" 32768; done; done
  tl l2-s64 arena 64 same 8192 "--arena 16M"; tl l2-s256 arena 256 same 8192 "--arena 16M"
fi

fails=0
for r in "${runs[@]}"; do
  name=${r%%|*}; args=${r#*|}
  cmd=("$MP2" --sysemu $args)          # --sysemu on every command: the simulator's device layer, never a card
  [[ " ${cmd[*]} " == *" --sysemu "* ]] || { say "internal: no --sysemu in $name"; exit 2; }
  if dry; then echo "DRY (cd $WD) timeout 1800 nice -n 19 ${cmd[*]}"; continue; fi
  say "$name"
  t0=$(date +%s)
  ( cd "$WD" && timeout 1800 nice -n 19 "${cmd[@]}" > "$WD/$name.out" 2> "$WD/$name.err" < /dev/null ); rc=$?
  verdict=$(python3 - "$WD/$name.out" "$name" "$rc" <<'EOF'
import json, sys
out, name, rc = sys.argv[1], sys.argv[2], int(sys.argv[3])
rows = [json.loads(l[9:]) for l in open(out) if l.startswith("MEMPROBE {")]
bad = []
if rc != 0:
    bad.append(f"exit {rc}")
if not rows:
    bad.append("no MEMPROBE line")
for r in rows:
    if not r.get("ok"):
        bad.append(f"{r.get('name')}: ok false")
    if r.get("test") == "tloop" and (r.get("tensor_errors") or r.get("launch_ok") is False):
        bad.append(f"tensor_errors {r.get('tensor_errors')}, launch_ok {r.get('launch_ok')}")
    if r.get("test") == "program" and not r.get("results"):
        bad.append("no results")
print("PASS" if not bad else "FAIL " + "; ".join(bad))
EOF
)
  if [ "$name" = prog-treload ] && [ -f "$WD/mp/treload.u32" ] && [ "${verdict%% *}" = PASS ]; then
    verdict=$(python3 - "$WD/mp" <<'EOF'
import json, os, sys
d = sys.argv[1]
labels = json.load(open(os.path.join(d, "treload.json")))["labels"]
raw = open(os.path.join(d, "treload.u32"), "rb").read()
v = [int.from_bytes(raw[i:i + 4], "little") for i in range(0, len(raw) - 3, 4)]
if len(v) != len(labels):
    print(f"FAIL {len(v)} results for {len(labels)} labels"); sys.exit()
e0 = [x for l, x in zip(labels, v) if l[0] == "terr0"]
new = [x for l, x in zip(labels, v) if l[0] in ("terr", "terr_end") and x & ~(e0[0] if e0 else 0)]
print("PASS" if not new else f"FAIL tensor_error gained bits {new[:4]} (before: {e0})")
EOF
)
  fi
  say "$name: $verdict ($(( $(date +%s) - t0 )) s)"
  [ "${verdict%% *}" = PASS ] || { fails=$((fails + 1)); tail -3 "$WD/$name.err" | sed 's/^/    /'; }
done
dry && { rm -rf "$WD"; exit 0; }
if [ $fails -eq 0 ]; then say "SYSEMU PASS: ${#runs[@]} runs"; [ -z "$KEEP" ] && rm -rf "$WD"; exit 0; fi
say "SYSEMU FAIL: $fails of ${#runs[@]} runs (logs in $WD)"; exit 1
