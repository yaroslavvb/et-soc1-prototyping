#!/usr/bin/env bash
# NV's two freezes (README.md). No device access. Run in the git checkout.
#   bash tools/claims-v3/nv/freeze.sh --predictions
#     before the first card write (the development probe): writes nv/PREDICTIONS.sha256 over predictions.json (the
#     bands, the E42 references, the controls' rules, the pass-count rule). Commit it, and record its SHA-256 in
#     docs/findings/03-experiments.md, before the probe. Every real block refuses unless it checks. Refuses if it
#     already exists and no longer checks: a change after the predictions were fixed is an amendment.
#   bash tools/claims-v3/nv/freeze.sh --binaries <file>
#     the validation freeze, after development and after PREREG.md and prereg.json are complete. <file>: the
#     validation host's binaries, one sha256sum line each, taken on that host at the tree root with
#       sha256sum build/ettelem/ettelem build/enercat_v2/host/enercat_host /opt/et/bin/dev_mngt_service \
#                 build/sparsity_t2/host/sparsity_host
#     It refuses unless PREDICTIONS.sha256 checks, PREREG.md holds no "TBD", and prereg.json has nD, sdD, nDev, tol and
#     val_passes, val_passes being the rule's N for sdD (nvlib.py nrule); then writes nv/PREREG.sha256 (PREREG.md) and
#     nv/LOCK.sha256 (the runner, its helper and queue, the analysis, both JSON files, PREREG.md, prereg.json, the
#     validation schedule, the shared lib.sh, the wire configurations and pipeline, and the four binaries).
#   bash tools/claims-v3/nv/freeze.sh --check          sha256sum -c of all three files (run it on the validation host too)
# --out-dir DIR writes (and --binaries reads PREDICTIONS.sha256 from) DIR instead of nv/ (for testing).
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
WD=tools/claims-v3/nv
OUTD=$WD; BIN=; CHECK=; PRED=
while [ $# -gt 0 ]; do
  case "$1" in --binaries) BIN=$2; shift 2 ;; --check) CHECK=1; shift ;; --predictions) PRED=1; shift ;;
    --out-dir) OUTD=$2; shift 2 ;;
    *) echo "usage: freeze.sh --predictions | --binaries <file> | --check  [--out-dir DIR]" >&2; exit 2 ;; esac
done
if [ -n "$CHECK" ]; then
  sha256sum -c "$OUTD/PREDICTIONS.sha256" && sha256sum -c "$OUTD/PREREG.sha256" && sha256sum -c "$OUTD/LOCK.sha256"; exit $?
fi
if [ -n "$PRED" ]; then
  if [ -e "$OUTD/PREDICTIONS.sha256" ]; then
    if sha256sum -c --quiet "$OUTD/PREDICTIONS.sha256" > /dev/null 2>&1; then
      echo "freeze: the predictions are already fixed: $(cut -c1-16 "$OUTD/PREDICTIONS.sha256")..."; exit 0
    fi
    echo "freeze: $WD/predictions.json no longer matches $OUTD/PREDICTIONS.sha256: a change after the fix is an amendment (DESIGN.md §5), not a new fix" >&2
    exit 1
  fi
  python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$WD/predictions.json" || { echo "freeze: predictions.json does not parse" >&2; exit 1; }
  mkdir -p "$OUTD"
  sha256sum "$WD/predictions.json" > "$OUTD/PREDICTIONS.sha256"
  echo "predictions fixed: $OUTD/PREDICTIONS.sha256 ($(cut -c1-16 "$OUTD/PREDICTIONS.sha256")...)"
  echo "commit it and record the SHA-256 in docs/findings/03-experiments.md before the development probe"
  exit 0
fi
[ -n "$BIN" ] && [ -r "$BIN" ] || { echo "freeze: --binaries <file> is required" >&2; exit 2; }
PF=$OUTD/PREDICTIONS.sha256; [ -e "$PF" ] || PF=$WD/PREDICTIONS.sha256
sha256sum -c --quiet "$PF" > /dev/null 2>&1 || { echo "freeze: $PF is missing or does not check: the predictions must be fixed before development" >&2; exit 1; }
if grep -n 'TBD' "$WD/PREREG.md"; then echo "freeze: PREREG.md still has TBD (above)" >&2; exit 1; fi
python3 - "$WD/prereg.json" "$WD" <<'PY' || exit 1
import json, subprocess, sys
try:
    p = json.load(open(sys.argv[1]))
except Exception as e:
    sys.exit(f"freeze: {sys.argv[1]}: {e}")
num = lambda k: isinstance(p.get(k), (int, float)) and not isinstance(p.get(k), bool)
for k in ("nD", "sdD", "tol"):
    if not num(k) or (k != "nD" and p[k] <= 0):
        sys.exit(f"freeze: prereg.json needs a number for {k!r} (the development n_D, its per-pass SD, the replication tolerance)")
if not isinstance(p.get("nDev"), int) or p["nDev"] < 3:
    sys.exit("freeze: prereg.json needs nDev, the number of valid development passes (>= 3)")
r = subprocess.run([sys.executable, "-B", f"{sys.argv[2]}/nvlib.py", "nrule", str(p["sdD"])], capture_output=True, text=True)
if r.returncode != 0:
    sys.exit("freeze: " + r.stderr.strip())
if p.get("val_passes") != int(r.stdout):
    sys.exit(f"freeze: prereg.json val_passes is {p.get('val_passes')!r}; the rule gives {int(r.stdout)} for sdD {p['sdD']}")
PY
BINS="build/ettelem/ettelem build/enercat_v2/host/enercat_host /opt/et/bin/dev_mngt_service build/sparsity_t2/host/sparsity_host"
for want in $BINS; do
  grep -Eq "^[0-9a-f]{64}  $want\$" "$BIN" || { echo "freeze: $BIN has no sha256 line for $want" >&2; exit 1; }
done
mkdir -p "$OUTD"
sha256sum "$WD/PREREG.md" > "$OUTD/PREREG.sha256"
{ sha256sum "$WD/block.sh" "$WD/nvlib.py" "$WD/run-queue.sh" "$WD/reduce.py" "$WD/nv.json" "$WD/predictions.json" \
    "$WD/PREREG.md" "$WD/prereg.json" "$WD/schedule-val-aifoundry2.txt" tools/claims-v3/lib.sh \
    tools/claims-v3/wire/configs.json workloads/enercat/analyze_wire.py workloads/enercat/run_wire.py
  grep -E "  ($(echo "$BINS" | tr ' ' '|'))\$" "$BIN"; } > "$OUTD/LOCK.sha256"
echo "frozen: $OUTD/PREREG.sha256 ($(cut -c1-16 "$OUTD/PREREG.sha256")...), $OUTD/LOCK.sha256 ($(wc -l < "$OUTD/LOCK.sha256") files)"
echo "record PREREG.md's sha256 in docs/findings/03-experiments.md with the commit that freezes it"
