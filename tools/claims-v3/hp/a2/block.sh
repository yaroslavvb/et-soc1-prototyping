#!/usr/bin/env bash
# Heat placement (HP, DESIGN2 §3.5): aifoundry2's same-day clock-step session (owner decision O3, 27 Sep 2026).
#
#   bash tools/claims-v3/hp/a2/block.sh 1            the session: gate, R0 probe (R and the class), smoke, then the
#                                                     branch on the rest reading R (fixed in PREREG-A2)
#   bash tools/claims-v3/hp/a2/block.sh 2|3|4        a re-check after a WARM reading: gate and one 1 s reading, each
#                                                     >= 2 h after the previous, the last before 22:00 local time; the
#                                                     session runs at the first reading <= 65; nothing carries to
#                                                     another day
#   V3_DRY=1 HP_DRY_REST=61 bash tools/claims-v3/hp/a2/block.sh 1     no device: the simulator at a 61 C rest
#
# Branches (params-a2.json): R <= 62 COOL: up to 2 A2 blocks from S_A2 = 63 (the 64 -> 63 falling edge); R = 63 COOL-:
# the same from 64; R 64-65 MARGINAL: 1 block from 65; R >= 66 WARM: one documentation run (a 7 s UNI32@4 launch with
# the sampler; expected 600 MHz throughout, mean >= 66), then stop: TRIG-A, TRIG-B and H12 are NOT OBSERVABLE.
# An A2 block: one warm-up run from rest (a 7 s UNI32@4 launch, discarded), then 8 runs in a seeded shuffle (INT16@8
# x2, PER16@8 x2, UNI32@4 x2, B4C@32 x2; 128 minions each). Each run, inside its own 10 Hz --reset-ms 1000 sampler: if
# the mean reads below S_A2 + 1, light lifts (7 s UNI32@4 launches, at most 6, discarded) until it does (a 128-minion
# run's heat is transient: after its 10 s tail a cool die has already fallen below the edge, so a separate warm-up run
# could not give the next run a falling edge); then the falling S_A2+1 -> S_A2 edge (cap 300 s, else void); one 7 s
# launch under hold10; 10 s more of sampling (the exit event); then (TRIG-B registered) an SP dump. A second block runs
# only if the first block's last run reached its edge within 300 s. The session stops launching at 30 min of card time.
# TRIG-B is registered only if the probe is ALIVE (or ALIVE_CANDIDATE): WARNING is set for the session (O2) and the
# level found is restored at the end.
#
# The frozen copies in this directory (hplib.sh, hplib.py, sptrace_events.py, placements.json) are this script's own:
# development edits to ../ never reach it. It refuses to run if any file here or any binary it runs differs from the
# lock in PREREG-A2.md, or PREREG-A2.md from PREREG-A2.sha256 (prereg.py --a2 wrote them before the session). The
# limits (caps, stale sampler) are hplib.py's fixed DEFAULTS: no params file and no HP_PARAMS_DIR is read. The bypass
# variables HP_A2_ANY_DAY, HP_A2_NO_GAP and HP_A2_IN_QUEUE work only under V3_DRY=1, and are then recorded.
# An aborted attempt (exit 1 or 3) writes a2.json with branch ABORTED, so a re-check (2-4) can follow; its data are
# never used. A set of the log level the abort left pending is restored before the next attempt's probe.
set -u
. "$(dirname "${BASH_SOURCE[0]}")/../../lib.sh"           # cd's to the tree root
[ "$CARD" = aifoundry2 ] || { echo "a2/block.sh runs on aifoundry2 only (this is $CARD): refused" >&2; exit 2; }
HP_DIR=tools/claims-v3/hp/a2
. "$HP_DIR/hplib.sh"
if [ "${1:-}" = --binhash ]; then hp_binaries_json; exit 0; fi
PASS=${1:?usage: a2/block.sh <attempt 1-4>}
case "$PASS" in 1|2|3|4) ;; *) echo "attempt must be 1 (the session) or 2-4 (re-checks)" >&2; exit 2 ;; esac
hp_envcheck a2                             # HP_PARAMS_DIR, HP_PREREG_DIR and the a2 bypasses: V3_DRY only
A2J=$HP_DIR/params-a2.json
pa() { python3 -c "import json,sys; d=json.load(open(sys.argv[1])); v=d
for k in sys.argv[2].split('.'): v=v[k]
print(v if not isinstance(v,(list,dict)) else json.dumps(v))" "$A2J" "$1"; }

# ---- the lock (files and binaries), the date, the gate
BINS_JSON=$(hp_binaries_json); BJ=$(mktemp); echo "$BINS_JSON" > "$BJ"
why=$("${HPPY[@]}" a2lock --prereg "$HP_DIR/prereg-a2.json" --bins "$BJ") || { rm -f "$BJ"; log "a2: PREREG-A2 lock: $why"; exit 1; }
rm -f "$BJ"; log "a2: $why"
DAY=$(pa date)
if [ -z "${HP_A2_ANY_DAY:-}" ] && [ "$(date +%F)" != "$DAY" ]; then log "a2: today is $(date +%F), the pre-registered day is $DAY (O3: nothing carries over)"; exit 1; fi
others_present && exit 3
ours_running && { log "a2: a device process of this user is running"; exit 3; }
if pgrep -u "$(id -u)" -f 'tools/claims-v3/queue\.sh' > /dev/null && [ -z "${HP_A2_IN_QUEUE:-}" ]; then log "a2: a queue of ours is running"; exit 3; fi
hp_lock_present
if ! dry; then for b in "$HEATER" "$ETTELEM" "$ETTELEM_HP"; do [ -x "$b" ] || { log "a2: missing $b"; exit 1; }; done; fi
N0=$(modcount); if [ -n "$N0" ] && [ "$N0" != 0 ]; then log "a2: et_soc1 use count $N0"; exit 3; fi
A2ROOT=$DATA_ROOT/hp/a2
prev=$(python3 - "$A2ROOT" <<'PY'
import glob, json, os, sys
att = []
for f in sorted(glob.glob(os.path.join(sys.argv[1], "p*", "a2.json"))):
    try: att.append(json.load(open(f)))
    except Exception: pass
ran = [a for a in att if a.get("branch") in ("COOL", "COOL-", "MARGINAL")]
# an ABORTED attempt is no reading for the 2 h gap (its data are never used); a WARM or other reading is
last = max((a.get("reading_t_ms") or 0 for a in att if a.get("branch") != "ABORTED"), default=0)
print("%d %d %d" % (len(att), 1 if ran else 0, last))
PY
)
read -r N_ATT RAN LAST_READ <<< "$prev"
[ "$RAN" = 1 ] && { log "a2: the session already ran today: nothing more"; exit 0; }
if [ "$PASS" -gt 1 ]; then
  [ "$N_ATT" -ge 1 ] || { log "a2: re-check $PASS without a first attempt"; exit 2; }
  gap=$(pa recheck_gap_s); hh=$(pa recheck_last_local_hour)
  if [ -z "${HP_A2_NO_GAP:-}" ] && [ $(( $(now_ms) - LAST_READ )) -lt $(( gap * 1000 )) ]; then log "a2: < $gap s since the last reading"; exit 3; fi
  if [ -z "${HP_A2_NO_GAP:-}" ] && [ "$(date +%-H)" -ge "$hh" ]; then log "a2: after ${hh}:00 local: no more re-checks today"; exit 0; fi
fi

# ---- begin (the card lock is held from here to the end)
block_begin hp/a2 "$PASS"
trap 'hp_cleanup' EXIT
SESSION_T0=$(now_ms)
sha256sum "$HP_DIR"/* >> "$OUT/code.sha256" 2>/dev/null
echo "$BINS_JSON" > "$OUT/binaries.json"
for b in "$HEATER" "$ETTELEM" "$ETTELEM_HP"; do [ -f "$b" ] && sha256sum "$b" >> "$OUT/binaries.sha256"; done
: > "$OUT/runs.jsonl"; : > "$OUT/launches.jsonl"; : > "$OUT/marks.jsonl"
command -v et-lab-manifest > /dev/null && ! dry && timeout 30 et-lab-manifest > "$OUT/manifest.txt" 2>&1
mark a2_begin "\"attempt\":$PASS,\"dry\":$(dry && echo true || echo false),\"overrides\":\"$HP_OVERRIDES\""
# every limit of hplib.py's fixed DEFAULTS (the caps, the stale sampler) as P_*; no params file is read
eval "$("${HPPY[@]}" params --a2 | sed 's/^SET //')"
R=; R_T=0; BRANCH=
write_a2() {   # write_a2 <branch> <note>
  python3 - "$OUT/a2.json" "$PASS" "${R:-}" "${R_T:-0}" "$1" "$2" "${PROBE_CLASS:-}" "${S_A2:-}" "${BLOCKS_RUN:-0}" "$HP_OVERRIDES" "${BRANCH:-}" <<'PY'
import json, sys
f, p, R, t, br, note, cls, s, nb, ov, br0 = sys.argv[1:12]
d = {"attempt": int(p), "rest_c": int(R) if R.lstrip("-").isdigit() else None, "reading_t_ms": int(t), "branch": br,
     "note": note, "probe_class": cls or None, "S_A2": int(s) if s.lstrip("-").isdigit() else None, "blocks_run": int(nb)}
if ov and ov != "-":
    d["overrides"] = ov.split()          # dry only (hplib.py envcheck refuses them on the card)
if br == "ABORTED":
    d["branch_at_abort"] = br0 or None
json.dump(d, open(f, "w"), indent=1)
PY
}
# an abort (exit 1, or exit 3 with the card left at once) records the attempt as ABORTED: a re-check may follow
hp_on_abort() { write_a2 ABORTED "aborted (exit $1): $2; data never used"; }

# ---- the reading (a re-check) or the probe (the session)
PROBE_CLASS=
hp_level_pending_restore          # a WARNING an aborted attempt left: restored before anything reads the ring
if [ "$PASS" -gt 1 ]; then
  R=$(die_c); R_T=$(now_ms)
  mark reading "\"die_c\":$(jnum "$R")"
  if [ "$R" = null ] || [ "$R" -ge 66 ]; then
    write_a2 WARM "re-check $PASS: rest $R C >= 66"; trap - EXIT; block_end ok "re-check: rest $R C: WARM"; exit 0
  fi
fi
hp_probe "$OUT/probe" | tee -a "$OUT/probe.log"
PROBE_CLASS=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('class') or '')" "$OUT/probe/probe.json" 2>/dev/null)
if [ "$PASS" = 1 ]; then
  R=$(python3 -c "import json,sys; v=json.load(open(sys.argv[1])).get('rest_c'); print('null' if v is None else v)" "$OUT/probe/probe.json"); R_T=$(now_ms)
fi
[ "$R" = null ] && hp_abort 1 "no die reading"

# ---- the smoke: the sampler, one 2 s UNI32@4 launch, an SP dump, reduce_a2.py --check-pass
RUN_STOP=; CH_T0=; CH_T1=; CH_N=0; CH_F66=; CH_CENS=; CH_RCS=; PREHEAT_BURSTS=0; PREHEAT_WHY=; EDGE_OK=; EDGE_T=; EDGE_TAUC=; EDGE_S1=; TRIGB_DUMP=
hp_run_begin smoke
hp_sleep 2
CH_T0=$(now_ms); hp_between; hp_launch smoke single 0xffffffff 4 "$(pa smoke_launch_s)" "$RUN_SF"; CH_N=1; CH_RCS=$LAST_RC
hp_sleep 3; hp_live || true; CH_T1=$(now_ms)
hp_run_end_quiet
hp_sptrace "$OUT/sp-smoke.bin"; TRIGB_DUMP=sp-smoke.bin
hp_record_run '"smoke"' 0 1 smoke UNI32@4 0xffffffff 4 128 A2 - -
note=$(python3 "$HP_DIR/reduce_a2.py" --check-pass "$OUT" 2>&1) || hp_abort 1 "smoke: $note"
log "a2 smoke: $note"

# ---- the branch on R (PREREG-A2)
BR=$(python3 - "$A2J" "$R" <<'PY'
import json, sys
b = json.load(open(sys.argv[1]))["branches"]; R = int(sys.argv[2])
for name in ("COOL", "COOL-", "MARGINAL"):
    if R <= b[name]["rest_max"]:
        print(name, b[name]["S_A2"], b[name]["blocks"]); break
else:
    print("WARM - 0")
PY
)
read -r BRANCH S_A2 NBLK <<< "$BR"
[ "$S_A2" = - ] && S_A2=
mark branch "\"rest_c\":$R,\"branch\":\"$BRANCH\",\"S_A2\":$(jnum "$S_A2"),\"blocks\":$NBLK,\"probe_class\":\"$PROBE_CLASS\""
log "a2: rest $R C -> $BRANCH (S_A2 ${S_A2:-none}, up to $NBLK blocks), probe class $PROBE_CLASS"
BLOCKS_RUN=0
if [ "$BRANCH" = WARM ]; then
  if [ "$PASS" = 1 ]; then        # the documentation run: 600 MHz throughout and the mean >= 66 expected
    RUN_STOP=; hp_run_begin doc; hp_sleep 5
    hp_single doc 0xffffffff 4 "$(pa launch_s)" "$(pa idle_after_s)"
    hp_run_end_quiet
    hp_record_run '"doc"' 0 1 doc UNI32@4 0xffffffff 4 128 A2 - -
  fi
  write_a2 WARM "rest $R C >= 66: the governor sits in its thermal loop at 600 MHz; TRIG-A, TRIG-B and H12 NOT OBSERVABLE this attempt"
  hp_gzip_all; trap - EXIT
  block_end ok "WARM (rest $R C): documentation only; re-checks allowed (>= 2 h apart, before 22:00)"
  exit 0
fi

# ---- TRIG-B (O2): WARNING only on an ALIVE probe
TRIGB=
case "$PROBE_CLASS" in ALIVE|ALIVE_CANDIDATE) TRIGB=1 ;; esac
TRIGB_REG=$TRIGB
if [ -n "$TRIGB" ]; then
  hp_level_begin sp-before                 # may clear TRIGB: the level found is unknown, so nothing is set
  [ -n "$TRIGB" ] && hp_sptrace "$OUT/sp-idle.bin"
fi
mark trigb "\"registered\":$([ -n "$TRIGB_REG" ] && echo true || echo false),\"tested\":$([ -n "$TRIGB" ] && echo true || echo false),\"level_found\":\"${LEVEL_FOUND:-}\",\"level_set\":$([ -n "$LEVEL_SET" ] && echo true || echo false)"

# ---- the A2 blocks
mapfile -t ORDER < <(python3 - "$A2J" <<'PY'
import json, random, sys
d = json.load(open(sys.argv[1]))
for b in (1, 2):
    r = list(d["runs"]); random.Random(d["seed_base"] + b).shuffle(r)
    print(" ".join(r))
PY
)
PL=$HP_DIR/placements.json
pl() { python3 -c "import json,sys; r=json.load(open(sys.argv[1]))['runs'][sys.argv[2]]; print(r['mask'], r['per_shire'], r['minions'])" "$PL" "$1"; }
n=0
# the session cap (30 min of card time) holds for the whole run: a run starts only if its worst case fits (review F15)
RUN_WORST_S=$(( $(pa warmup_max) * ($(pa launch_s) + 3) + $(pa edge_cap_s) + $(pa launch_s) + $(pa idle_after_s) + 30 ))
WARMUP_WORST_S=$(( $(pa pre_launch_min_s) + $(pa launch_s) + $(pa idle_after_s) + 30 ))
time_left() {   # time_left [worst-case seconds of the next run]
  [ $(( $(now_ms) - SESSION_T0 + ${1:-$RUN_WORST_S} * 1000 )) -le $(( $(pa session_cap_s) * 1000 )) ]
}
a2_run() {   # a2_run <role> <name> <block> <slot>
  local role=$1 name=$2 blk=$3 slot=$4 mask per mins
  read -r mask per mins <<< "$(pl "$name")"
  n=$(( n + 1 ))
  RUN_STOP=; PREHEAT_BURSTS=0; PREHEAT_WHY=; EDGE_OK=; EDGE_T=; EDGE_TAUC=; EDGE_S1=; CH_T0=; CH_T1=; CH_N=0; CH_F66=; CH_CENS=; CH_RCS=; TRIGB_DUMP=
  hp_run_begin "$n"
  mark run_begin "\"idx\":$n,\"block\":$blk,\"slot\":$slot,\"role\":\"$role\",\"name\":\"$name\""
  if [ "$role" = meas ]; then
    local wr wm wp
    read -r wm wp _ <<< "$(pl "$(pa warmup_run)")"
    hp_preheat $(( S_A2 + 1 )) "$wm" "$wp" "$(pa launch_s)" "$(pa warmup_max)" || true
    if [ -z "${RUN_STOP:-}" ] && hp_edge_wait "$S_A2" "$(pa edge_cap_s)"; then
      hp_single "$n" "$mask" "$per" "$(pa launch_s)" "$(pa idle_after_s)"
    fi
  else
    hp_sleep "$(pa pre_launch_min_s)"
    hp_single "$n" "$mask" "$per" "$(pa launch_s)" "$(pa idle_after_s)"
  fi
  hp_run_end_quiet
  for f in "$OUT/tel-$n.jsonl" "$OUT/heater-$n.out"; do [ -f "$f" ] && gzip -f "$f"; done
  if [ -n "$TRIGB" ]; then hp_sptrace "$OUT/sp-$n.bin"; TRIGB_DUMP=sp-$n.bin; fi
  hp_record_run "$n" "$slot" 1 "$role" "$name" "$mask" "$per" "$mins" A2 "${S_A2}" -
  python3 - "$OUT/runs.jsonl" "$blk" <<'PY'
import json, sys
p, b = sys.argv[1], int(sys.argv[2])
L = open(p).read().splitlines(); r = json.loads(L[-1]); r["a2_block"] = b; L[-1] = json.dumps(r)
open(p, "w").write("\n".join(L) + "\n")
PY
  log "a2 run $n (block $blk, $role $name): edge $([ -n "$EDGE_OK" ] && echo ok || echo -), launches $CH_N, stop ${RUN_STOP:-none}"
}
for b in $(seq 1 "$NBLK"); do
  time_left $(( WARMUP_WORST_S + RUN_WORST_S )) || { mark cap "\"why\":\"session card-time cap before block $b\""; break; }
  mark a2_block_begin "\"block\":$b"
  [ "$b" = 1 ] && a2_run warmup "$(pa warmup_run)" "$b" 0     # the first run of a period starts from rest: discarded
  slot=0; LAST_EDGE_OK=
  for name in ${ORDER[$((b - 1))]}; do
    time_left || { mark cap "\"why\":\"session card-time cap: < ${RUN_WORST_S} s (a run's worst case) left\""; break; }
    slot=$(( slot + 1 ))
    a2_run meas "$name" "$b" "$slot"
    LAST_EDGE_OK=$EDGE_OK
  done
  BLOCKS_RUN=$b
  mark a2_block_end "\"block\":$b,\"last_edge_ok\":$([ -n "$LAST_EDGE_OK" ] && echo true || echo false)"
  [ -n "$LAST_EDGE_OK" ] || break                 # a second block only if the last run reached its edge
done

# ---- end
LEVEL_CHECK=
hp_level_restore                   # restores and checks with a dump only if this session set the level
write_a2 "$BRANCH" "rest $R C; $BLOCKS_RUN block(s); TRIG-B $([ -n "$TRIGB" ] && echo registered || echo "not registered (probe $PROBE_CLASS)")${LEVEL_CHECK:+; $LEVEL_CHECK}"
hp_gzip_all
trap - EXIT
block_end ok "$BRANCH at rest $R C: $BLOCKS_RUN A2 block(s), probe $PROBE_CLASS${LEVEL_CHECK:+; $LEVEL_CHECK}"
exit 0
