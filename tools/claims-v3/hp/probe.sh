#!/usr/bin/env bash
# Heat placement (HP, DESIGN2 §3.2): the R0 probe of the local card. It changes no state.
#
#   bash tools/claims-v3/hp/probe.sh <pass 8xx>         (block.sh execs it for T=8; aifoundry1: V3_DEVICE=1)
#
#   1 nobody else on the card (lib others_present, ours_running, the et_soc1 use count, no CI job) and et-who, who, ps
#     recorded; lib block_begin takes the card lock; one 1 s die reading gives R;
#   2 ettelem sptrace p0.bin (the level is inferred in step 5 from the entries new between p0 and p1 only: MS nn
#     Voltage -> DEBUG; Host_Iface/pc_vq -> INFO; else WARNING or lower; INFO-era lines left in the ring do not count);
#   3 one 2 s heater launch under hold10 with NO sampler open: UNI32@4 (128 minions, --seconds 2);
#   4 ettelem sptrace p1.bin immediately, then ettelem config (read-only);
#   5 sptrace_events.py classify: ALIVE (power lines and an "event received" after them), STUCK (power lines only),
#     SILENT (no governor line: latched, DVFS off, or aifoundry2's thermal loop at rest >= 66); probe.json holds the
#     class, the level, R and the prediction fixed in DESIGN2 before any data.
# On aifoundry1 card 1 the card-0 guard runs through the probe, as through every card-1 block. Refused (exit 2):
# aifoundry1 card 0, aifoundry2 (its probe is part of a2/block.sh), and any pass that is not an R0 probe (8xx);
# V3_FORCE without V3_DRY on card 1 (hplib.py envcheck).
# A log level an earlier block left pending (sp-level.json) is restored before the probe reads the ring.
# About 20 s of card time.
set -u
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
case "$CARD" in
  aifoundry1-c0) echo "probe: aifoundry1 card 0 is never used (owner decision, DESIGN2 §0): refused" >&2; exit 2 ;;
  aifoundry2) echo "probe: aifoundry2's probe runs inside tools/claims-v3/hp/a2/block.sh only: refused" >&2; exit 2 ;;
esac
HP_DIR=tools/claims-v3/hp
. "$HP_DIR/hplib.sh"
PASS=${1:?usage: probe.sh <pass>}
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
PASS=$(( 10#$PASS ))
why=$("${HPPY[@]}" check-card --pass "$PASS" --card "$CARD") || { log "probe: pass $PASS on $CARD $why"; exit 2; }
[ $(( PASS / 100 )) = 8 ] || { log "probe: pass $PASS is not an R0 probe (8xx): refused"; exit 2; }
hp_envcheck dev
eval "$("${HPPY[@]}" params --pass "$PASS" --card "$CARD" | sed 's/^SET //')"   # the guard limits (P_guard_*)

others_present && exit 3
ours_running && { log "probe: a device process of this user is running on this card"; exit 3; }
hp_orphan_guards                        # an orphaned card-0 guard of ours first (it would count as card-0 activity)
hp_card0_check "probe start"
hp_lock_present
if ! dry; then for b in "$HEATER" "$ETTELEM"; do [ -x "$b" ] || { log "probe: missing $b"; exit 1; }; done
  [ -f "$HEATER_KERNEL" ] || { log "probe: missing the heater kernel $HEATER_KERNEL"; exit 1; }; fi
N0=$(modcount)
if [ -n "$N0" ] && [ "$N0" != 0 ]; then log "probe: et_soc1 use count $N0"; exit 3; fi

block_begin hp "$PASS"
trap 'hp_cleanup' EXIT
: > "$OUT/marks.jsonl"; : > "$OUT/launches.jsonl"
sha256sum "$HP_DIR"/*.py "$HP_DIR"/*.sh >> "$OUT/code.sha256" 2>/dev/null
hp_binaries_json > "$OUT/binaries.json"
ps -eo user,pid,etime,comm > "$OUT/ps.txt" 2>&1
if [ -n "$GUARD_ON" ]; then
  hp_guard_start || { hp_guard_stop; block_end fail "card-0 guard gate failed"; exit 3; }
fi
hp_level_pending_restore
hp_probe "$OUT" | tee -a "$OUT/probe.log"
hp_guard_stop
hp_gzip_all
cls=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('class'))" "$OUT/probe.json" 2>/dev/null)
trap - EXIT
if [ -z "$cls" ] || [ "$cls" = None ]; then block_end fail "probe: no class (see class.err)"; exit 1; fi
block_end ok "probe class $cls"
exit 0
