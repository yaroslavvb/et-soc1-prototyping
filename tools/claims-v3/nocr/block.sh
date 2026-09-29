#!/usr/bin/env bash
# nocr (hub rungs 31 and 32: the mesh's stops, and its routing order): one pass on the local card, from the tree's root.
#
#   bash tools/claims-v3/nocr/block.sh <pass>            (aifoundry1: V3_DEVICE=1; card 0 is never used)
#   V3_DRY=1 [NOCR_DRY_CARD=aifoundry1-c1] [NOCR_FAKE_THEORY=xy] bash tools/claims-v3/nocr/block.sh <pass>
#                                                        no device access: the host is replaced by a model (nocr.py fakehost);
#                                                        NOCR_FAKE_FAIL=<process> [NOCR_FAKE_RC=n], NOCR_FAKE_TIMEOUT=<process>,
#                                                        NOCR_FAKE_NOTOK=<process>, NOCR_FAKE_DIE=<C|none>,
#                                                        NOCR_FAKE_MHZ=<MHz> test the stops and the data rule
#
# pass 9 = the smoke (about 10 s of card time); 1-8 = development (aifoundry1 card 1 only); 11-19 = validation (a card
# other than the development card; needs the PREREG lock: PREREG.md frozen, PREREG.sha256, LOCK.sha256,
# kernel-text.sha256, all made by make_lock.sh). A pass other than 9 needs this card's smoke to have ended ok.
# Each pass runs, one device process at a time: R31's mesh launches, R32's read and write repeats interleaved, and
# R31's shire-32 launch last (the one call path no earlier work has used).
# Data: build/claims-v3/<card>/nocr/p<pass>/. Exit codes (V3): 0 ok, 1 fail, 2 refused, 3 someone else on the card.
#
# The HALT marker (build/claims-v3/<card>/nocr/HALT). A launch that timed out (the host's own 6 s limit or timeout 10's
# rc 124), any failure of an R31 process, any failure in the smoke, missing telemetry or a die at the stop temperature
# writes it and ends the block; every later nocr block on this card then refuses to start (exit 2) until a person has
# looked at the card and removed the marker. queue.sh only logs a failed block and starts the next one 20 s later:
# the marker is what stops a queue (or run.sh) from launching on a card that may be wedged.
#
# The card's etiquette, enforced here: et-who --check (this card's holders; a missing et-who refuses) and lib.sh's
# others_present before the block and before every device process; the card lock (lib.sh block_begin, fd 9) for the
# whole block, and a missing lock file refuses; timeout 10 on every device process (hold10, and the host's own 8 s
# budget); a stop at a 90 C die mean; never aifoundry1's card 0; never dev_mngt_service (on aifoundry1 the stock
# build opens card 0's management node too) and never a heater launch, so no sampler, no queue drain and no heat_to
# here: the only management-node reads are 1 s ettelem samples of this card (die temperature and clock).
set -u
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"          # cd's to the tree root; CARD, ETTELEM, hold10, block_begin, ...
NDIR=tools/claims-v3/nocr
NPY=(python3 "$NDIR/nocr.py")
dry() { [ -n "${V3_DRY:-}" ]; }
if dry && [ -n "${NOCR_DRY_CARD:-}" ]; then CARD=$NOCR_DRY_CARD; DATA_ROOT=$V3_ROOT/build/claims-v3-dry/$CARD; fi
case "$CARD" in aifoundry1-c0) log "nocr: aifoundry1 card 0 is never used: refused"; exit 2 ;; esac
if [ -n "${V3_FORCE:-}" ] && ! dry; then log "nocr: V3_FORCE is refused: a repeat gets a new pass number"; exit 2; fi

PASS=${1:?usage: block.sh <pass>}
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
PASS=$(( 10#$PASS ))
why=$("${NPY[@]}" check-card --pass "$PASS" --card "$CARD" $(dry && echo --dry) 2>&1) ||
  { log "nocr: ${why:-nocr.py check-card failed}: refused"; exit 2; }
case "$PASS" in 9) KIND=smoke ;; 1|2|3|4|5|6|7|8) KIND=dev ;; *) KIND=val ;; esac
HALT=$DATA_ROOT/nocr/HALT
if [ -e "$HALT" ]; then
  log "nocr: $HALT exists ($(tail -1 "$HALT")): refused until a person has looked at the card and removed it"; exit 2
fi
if [ "$KIND" != smoke ] && ! grep -q '"status":"ok"' "$DATA_ROOT/nocr/p9/block.json" 2>/dev/null; then
  log "nocr: this card's smoke (pass 9) has not ended ok: refused"; exit 2
fi
HOST_BIN=build/nocroute/host/nocroute_host
KERNEL=build/nocroute/kernel/nocroute.elf
LOCKF=/run/lock/etsoc-shire${V3_DEVICE:-0}.lock
STOP_C=$(python3 -c "import json;print(json.load(open('$NDIR/params.json'))['safety']['stop_die_c'])")
BUDGET=$(python3 -c "import json;print(json.load(open('$NDIR/params.json'))['safety']['host_budget_s'])")
PAUSE=$(python3 -c "import json;print(json.load(open('$NDIR/params.json'))['safety']['pause_between_processes_s'])")

if ! dry; then
  for b in "$HOST_BIN" "$ETTELEM"; do [ -x "$b" ] || { log "nocr: missing $b"; exit 1; }; done
  [ -f "$KERNEL" ] || { log "nocr: missing $KERNEL"; exit 1; }
  command -v et-who > /dev/null || { log "nocr: et-who not installed: refused"; exit 2; }
  [ -e "$LOCKF" ] || { log "nocr: no card lock file $LOCKF: refused"; exit 2; }
fi
"${NPY[@]}" check-sets > /dev/null || { log "nocr: $("${NPY[@]}" check-sets)"; exit 1; }
if [ "$KIND" = val ]; then
  kargs=(); [ -f "$KERNEL" ] && kargs=(--kernel "$KERNEL")
  why=$("${NPY[@]}" lockcheck "${kargs[@]}") || { log "nocr: PREREG lock: $why"; exit 1; }
  log "nocr: $why"
fi
if [ "$CARD" = aifoundry2 ] && pgrep -af '[d]v2v/block.sh|[s]chedule-dv2' > /dev/null; then
  log "nocr: DV2 runs on aifoundry2: refused"; exit 2
fi

# ---- the card's own reads: die temperature and clock (a 1 s ettelem sample of this card, timeout 10)
LIVE_C=; LIVE_MHZ=
nocr_tel() {
  LIVE_C=; LIVE_MHZ=
  if dry; then                          # dry: NOCR_FAKE_DIE / NOCR_FAKE_MHZ test the stops ("none": no telemetry)
    [ "${NOCR_FAKE_DIE:-}" = none ] && return 1
    LIVE_C=${NOCR_FAKE_DIE:-80}; LIVE_MHZ=${NOCR_FAKE_MHZ:-600}; return 0
  fi
  local i out
  for i in 1 2 3; do      # ettelem sample fails to start about one time in three right after another instance
    out=$(timeout 10 "$ETTELEM" sample --seconds 1 --every-ms 500 2>/dev/null < /dev/null | "${NPY[@]}" tel)
    if [ -n "$out" ]; then read -r LIVE_C LIVE_MHZ <<< "$out"; return 0; fi
    sleep 2
  done
  return 1
}
if ! dry; then die_c() { nocr_tel && echo "$LIVE_C"; }; fi   # lib.sh's die_c allows 20 s; this one 10
# ---- et-who --check, this card only (on a two-card host the other card's holders do not block; our own lock does not)
etwho_ok() {
  dry && return 0
  command -v et-who > /dev/null || { log "nocr: et-who not installed"; return 1; }
  local out rc lines
  out=$(et-who --check 9>&- 2>&1); rc=$?
  [ $rc -eq 0 ] && return 0
  [ $rc -eq 2 ] && { log "nocr: et-who --check failed: $out"; return 1; }
  local n=${V3_DEVICE:-0}
  lines=$(printf '%s\n' "$out" | awk -v n="$n" -v me="$USER" -v pid="$$" '
    $1 ~ ("^/dev/et" n "_") { print; next }
    $1 ~ ("^lock:.*etsoc-shire" n "\\.lock$") && !($2 == me) { print }')
  if [ -n "$lines" ]; then log "nocr: et-who: card ${n} held: $(echo "$lines" | tr '\n' ';')"; return 1; fi
  return 0
}
# ---- the HALT marker: no further nocr block starts on this card until a person has looked and removed it
halt() {
  mkdir -p "$DATA_ROOT/nocr"
  printf '{"t_ms":%s,"pass":%s,"why":"%s"}\n' "$(now_ms)" "$PASS" "${1//\"/\'}" >> "$HALT"
  log "nocr: HALT written ($HALT): $1"
}

# ---- 1. the card must be free
others_present && exit 3
ours_running && { log "nocr: a device process of this user is running: not starting"; exit 3; }
etwho_ok || exit 3

# ---- 2. begin (block_begin takes the card lock for the whole block)
block_begin nocr "$PASS"
mkdir -p "$OUT"
MARKS=$OUT/marks.jsonl; : > "$MARKS"
mark() { echo "{\"t_ms\":$(now_ms),\"ev\":\"$1\"${2:+,$2}}" >> "$MARKS"; }
sha256sum "$NDIR"/*.py "$NDIR"/*.sh "$NDIR"/*.json "$NDIR"/*.md "$NDIR"/*.txt workloads/nocroute/*.py \
  workloads/nocroute/*.h workloads/nocroute/CMakeLists.txt workloads/nocroute/host/* workloads/nocroute/kernel/* \
  tools/claims-v3/queue.sh >> "$OUT/code.sha256" 2>/dev/null
if ! dry; then
  printf '{"host":"%s","host_sha256":"%s","kernel_sha256":"%s","kernel_text_sha256":"%s"}\n' "$HOST_BIN" \
    "$(sha256sum "$HOST_BIN" | cut -c1-64)" "$(sha256sum "$KERNEL" | cut -c1-64)" "$("${NPY[@]}" texthash "$KERNEL")" \
    > "$OUT/binaries.json"
  command -v et-lab-manifest > /dev/null && timeout 30 et-lab-manifest > "$OUT/manifest.txt" 2>&1
fi
"${NPY[@]}" plan --pass "$PASS" --out "$OUT" > /dev/null || { block_end fail "plan"; exit 1; }
mark begin "\"kind\":\"$KIND\",\"card\":\"$CARD\",\"dry\":$(dry && echo true || echo false),\"die_c\":${BLOCK_C0:-null}"

STATUS=ok; NOTE=; HALTED=
stop_halt() { STATUS=fail; NOTE="$NOTE $1;"; mark stop "\"why\":\"${1//\"/\'}\",\"halt\":true"; halt "$1"; HALTED=1; }
exec 3< "$OUT/procs.txt"      # the process list on its own descriptor: no child can read the loop's input
while read -r name plan jsonl odir <&3; do
  # before every device process: nobody else, a die below the stop, the clock recorded
  if others_present || ! etwho_ok; then STATUS=fail; NOTE="$NOTE someone else appeared before $name;"
    mark stop "\"why\":\"others\""; break; fi
  if ! nocr_tel; then stop_halt "no telemetry before $name"; break; fi
  if [ "$LIVE_C" -ge "$STOP_C" ]; then stop_halt "die ${LIVE_C} C >= ${STOP_C} C before $name"; break; fi
  # A process off the registered 600 MHz is dropped by the data rule, so it is not run at all: no card time is spent
  # on data that cannot count. (aifoundry1's card 1 and aifoundry3 hold 600 MHz; aifoundry2 leaves it only below
  # about 68 C, and is never heated here.)
  if [ "$LIVE_MHZ" != 600 ]; then NOTE="$NOTE $name skipped at ${LIVE_MHZ} MHz;"
    mark skip "\"name\":\"$name\",\"die_c\":$LIVE_C,\"mhz\":$LIVE_MHZ"
    [ "$KIND" = smoke ] && STATUS=fail
    continue; fi
  t0=$(now_ms)
  for try in 1 2; do
    if dry; then
      "${NPY[@]}" fakehost --plan "$plan" --out-dir "$odir" --theory "${NOCR_FAKE_THEORY:-xy}" --seed "$((PASS * 100 + try))" \
        > "$jsonl" 2> "$jsonl.err"; rc=$?
      [ "${NOCR_FAKE_FAIL:-}" = "$name" ] && rc=${NOCR_FAKE_RC:-1}   # dry: a failing process, to test the stops
      if [ "${NOCR_FAKE_TIMEOUT:-}" = "$name" ]; then            # dry: a launch the host gave up on after 6 s
        sed -i '0,/"timed_out":false,"ok":true/s//"timed_out":true,"ok":false/' "$jsonl"; rc=1; fi
      if [ "${NOCR_FAKE_NOTOK:-}" = "$name" ]; then              # dry: the process's last launch reports not ok
        sed -i '$s/"timed_out":false,"ok":true}$/"timed_out":false,"ok":false}/' "$jsonl"; rc=1; fi
    else
      hold10 "$HOST_BIN" --plan "$plan" --out-dir "$odir" --budget "$BUDGET" > "$jsonl" 2> "$jsonl.err"; rc=$?
    fi
    # a host that died before its first launch (aifoundry3's old 1.08 s crash, rc 139) is run once more; nothing else is
    if [ $rc -eq 139 ] && ! grep -q '^NOCR ' "$jsonl"; then mv "$jsonl" "$jsonl.crash$try"; continue; fi
    break
  done
  [ -f "$jsonl" ] || : > "$jsonl"
  n_bad=$(grep '^NOCR ' "$jsonl" | grep -c '"ok":false')
  timed=$(grep -c '"timed_out":true' "$jsonl")
  mark proc "\"name\":\"$name\",\"rc\":$rc,\"t0_ms\":$t0,\"die_c\":$LIVE_C,\"mhz\":$LIVE_MHZ,\"launches\":$(grep -c '^NOCR ' "$jsonl"),\"launches_not_ok\":$n_bad,\"timed_out\":$timed"
  # A launch that did not finish (the host aborted it after 6 s, or timeout 10 killed the host: rc 124) may have left a
  # hart wedged; any failure of R31's calls (M-mode code on every caller) or anything failing in the smoke may mean
  # the card needs a look: HALT, and end the block.
  if [ $rc -eq 124 ] || [ "$timed" -gt 0 ] || grep -q 'did not finish' "$jsonl.err" 2>/dev/null; then
    stop_halt "$name rc $rc, a launch did not finish"; break; fi
  if [ $rc -ne 0 ]; then
    case "$name" in r31-*) stop_halt "$name rc $rc"; break ;; esac
    if [ "$KIND" = smoke ]; then stop_halt "smoke: $name rc $rc"; break; fi
    # An R32 process that failed otherwise (a minion error, a stream error, the budget) is recorded and the next one
    # runs: its launches that the host reported not ok are dropped by the data rule (PREREG.md), the others count,
    # so the pass stays ok.
    NOTE="$NOTE $name rc $rc ($n_bad launches not ok);"
    mark r32fail "\"name\":\"$name\",\"rc\":$rc,\"launches_not_ok\":$n_bad"
  fi
  sleep "$PAUSE"
done
exec 3<&-

if [ -z "$HALTED" ] && nocr_tel; then mark end "\"die_c\":$LIVE_C,\"mhz\":$LIVE_MHZ"; fi
[ -n "$HALTED" ] && die_c() { :; }   # after a HALT, leave the management node alone: block.json records no end die
block_end "$STATUS" "$KIND${NOTE:+:$NOTE}"
# the reduction of this card's passes so far (no device): what the main session reads first
python3 "$NDIR/reduce.py" "$DATA_ROOT/nocr" --passes "$PASS" --include-smoke --out "$OUT/reduce.json" > "$OUT/reduce.txt" 2>&1
[ "$STATUS" = ok ] && exit 0 || exit 1
