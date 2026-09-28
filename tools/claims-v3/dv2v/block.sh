#!/usr/bin/env bash
# DV2 validation on aifoundry2 (PREREG-VAL.md, frozen 28 Sep 2026): one read-only watch cycle, VZ. The procedure is the
# development Z1 cycle's (dv2/block.sh 1001-1999), unchanged: the gate (who, the process scan, et-who, the et_soc1 use
# count, no other framework queue), flock -n on the card lock (the cycle is skipped if it is held), sptrace (a BAR
# read), residency 2-6 + uptime, config (the threshold must read 65), one 1 s 10 Hz sample with one statistics reset at
# its start. About 1.5 s of card access. No heat, no set, no log-level change (a WARNING left pending by a killed
# development session is restored to INFO, as every Z1 cycle does).
#
#   bash tools/claims-v3/dv2v/block.sh <pass 9101-9499>          (queue.sh runs it as "dv2v <pass>")
#   bash tools/claims-v3/dv2v/block.sh <pass 9501-9599>          a VN candidate (dv2v/vn_check.py decides, reading
#        files only): the frozen NAT replication session, dv2/block.sh 6051-6099 with DV2_VAL=1, starts only if the
#        newest VZ cycle (<= 15 min old) read <= val.json nat.nat_cool_max, fewer than vn_sessions_max sessions
#        launched and fewer than vn_blocks_needed complete G4 blocks exist; otherwise it logs why and exits 0.
#   V3_DRY=1 DV2V_DRY_ANYTIME=1 bash tools/claims-v3/dv2v/block.sh 9101      no device (the dv2 simulator)
#
# It refuses (exit 2) unless every file listed in dv2v/LOCK.sha256 hashes as frozen (PREREG-VAL §6). A cycle waits
# (holding nothing) until the earliest start, the later of val.json's not_before and gap_h hours after the newest
# development pass (build/claims-v3/aifoundry2/dv2/p*/block.json t1_ms), and until period_s after the previous VZ
# cycle's start; it does nothing (exit 0, "skipped") if the earliest start is more than 8 h away, after val.json's hours
# from the first VZ cycle, or after max_cycles cycles. Data: build/claims-v3/aifoundry2/dv2v/.
set -u
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"           # cd's to the tree root
. tools/claims-v3/dv2/dv2lib.sh
PASS=${1:?usage: dv2v/block.sh <pass 9101-9499>}
case "$PASS" in 9[1-4][0-9][0-9]) VKIND=VZ ;; 95[0-9][0-9]) VKIND=VN ;; *) echo "dv2v: pass $PASS is not a VZ (9101-9499) or VN (9501-9599) pass" >&2; exit 2 ;; esac
[ -n "${DV2V_DRY_ANYTIME:-}" ] && ! dry && { log "dv2v: DV2V_DRY_ANYTIME without V3_DRY: refused"; exit 2; }
if ! bad=$("${DV2PY[@]}" envcheck); then log "dv2v: refused: dry-only variables without V3_DRY: $bad"; exit 2; fi
DEV_DATA=$DV2_DATA                                   # the development data root (build/claims-v3/<card>/dv2)
DV2_DATA=$DATA_ROOT/dv2v                             # the validation data root (queue.sh's exp dir)
DV2_LASTDUMP=$DV2_DATA/last-dump.bin                 # the error-line scan runs against the previous VZ dump
mkdir -p "$DV2_DATA"
VJ=tools/claims-v3/dv2v/val.json
# ---- the freeze: every locked file must hash as frozen
if ! ( sha256sum -c --quiet tools/claims-v3/dv2v/LOCK.sha256 ) > "$DV2_DATA/lock-check.txt" 2>&1; then
  log "dv2v p$PASS: refused: the files differ from the frozen PREREG-VAL lock ($(head -3 "$DV2_DATA/lock-check.txt" | tr '\n' ' '))"; exit 2
fi
if night_stopped; then log "dv2v p$PASS: the stop file is set ($DV2_DATA/NIGHT-STOP): nothing runs"; exit 0; fi
if ! dry; then [ -e "$ETTELEM" ] || { log "dv2v: missing $ETTELEM"; exit 1; }; fi
[ -e /run/lock/etsoc-shire0.lock ] || dry || { log "dv2v: /run/lock/etsoc-shire0.lock is missing: not starting"; exit 1; }
OUT=$DV2_DATA/p$PASS
skip_record() {
  mkdir -p "$OUT"
  printf '{"exp":"dv2v","pass":%s,"card":"%s","t0_ms":%s,"t1_ms":%s,"status":"skipped","note":%s}\n' "$PASS" "$CARD" \
    "$(now_ms)" "$(now_ms)" "$(jstr "$1")" > "$OUT/block.json"
  log "dv2v p$PASS skipped: $1"
}
# ---- when: not before val.json's not_before, >= gap_h after the last development pass, inside the window, period_s apart
read -r WAIT_MS WHY <<< "$(VKIND=$VKIND python3 - "$VJ" "$DEV_DATA" "$DV2_DATA" "$(now_ms)" "${DV2V_DRY_ANYTIME:-}" <<'PY'
import glob, json, os, sys, time
vj, dev, val, now, anytime = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
V = json.load(open(vj))
def t1(f):
    try:
        return json.load(open(f)).get("t1_ms") or 0
    except Exception:
        return 0
last_dev = max([t1(f) for f in glob.glob(os.path.join(dev, "p*", "block.json"))] or [0])
vz = sorted((json.load(open(f)) for f in glob.glob(os.path.join(val, "p9*", "block.json"))
             if os.path.getsize(f) > 0), key=lambda b: b.get("t0_ms") or 0)
vz = [b for b in vz if b.get("status") == "ok"]
nb = int(time.mktime(time.strptime(V["not_before"], "%Y-%m-%dT%H:%M")) * 1000)
earliest = 0
if not anytime:
    earliest = max(nb, last_dev + V["gap_h"] * 3600e3)
    if earliest - now > 8 * 3600e3:
        print(-1, "the earliest start (%s; >= %s h after the last development pass) is more than 8 h away" % (
            time.strftime("%Y-%m-%d %H:%M", time.localtime(earliest / 1e3)), V["gap_h"])); sys.exit()
    if vz and now > vz[0]["t0_ms"] + V["hours"] * 3600e3:
        print(-1, "the %s h validation window (from the first VZ cycle) is over" % V["hours"]); sys.exit()
    if len(vz) >= V["max_cycles"]:
        print(-1, "%d VZ cycles done" % len(vz)); sys.exit()
nxt = max((vz[-1]["t0_ms"] + V["period_s"] * 1000) if (vz and os.environ.get("VKIND") == "VZ") else now, earliest)
print(max(0, int(nxt - now)), "ok")
PY
)"
if [ "${WAIT_MS:--1}" -lt 0 ]; then skip_record "$WHY"; exit 0; fi
if [ "$VKIND" = VN ]; then     # decides only; dv2/block.sh does the gate, the lock, the probe and everything after
  read -r VN_OK VN_PASS VN_WHY <<< "$(python3 tools/claims-v3/dv2v/vn_check.py "$VJ" "$DV2_DATA" "$(now_ms)")"
  printf '{"t_ms":%s,"pass":%s,"ok":%s,"why":%s}\n' "$(now_ms)" "$PASS" "${VN_OK:-0}" "$(jstr "${VN_WHY:-}")" >> "$DV2_DATA/nat-candidates.jsonl"
  if [ "${VN_OK:-0}" != 1 ]; then log "dv2v VN p$PASS: not starting: $VN_WHY"; exit 0; fi
  touch "$DV2_DATA/NAT-AUTOSTART"
  log "dv2v VN p$PASS: $VN_WHY -> the frozen NAT replication session dv2/block.sh $VN_PASS (DV2_VAL=1)"
  exec env DV2_VAL=1 DV2_NO_WARNING=1 bash tools/claims-v3/dv2/block.sh "$VN_PASS"
fi
[ "$WAIT_MS" -gt 0 ] && { if dry; then sleep 0.2; else sleep "$(awk -v m="$WAIT_MS" 'BEGIN{printf "%.1f", m/1000}')"; fi; }
mkdir -p "$OUT"; : > "$OUT/marks.jsonl"
T0=$(now_ms)
if others_present || ours_running || [ -n "$(foreign_procs)" ] || [ -n "$(etwho_foreign)" ] || [ -n "$(other_framework)" ]; then
  skip_record "gate: another user, device process, holder or framework queue present"; exit 0
fi
if ! dry; then n=$(modcount); [ -n "$n" ] && [ "$n" != 0 ] && { skip_record "et_soc1 use count $n"; exit 0; }; fi
if ! dry; then exec 9<>/run/lock/etsoc-shire0.lock; flock -n 9 || { skip_record "the card lock is held"; exit 0; }; fi
mark vz_begin "\"lock\":\"$(sha256sum tools/claims-v3/dv2v/LOCK.sha256 | cut -c1-16)\""
dv2_level_pending_restore          # the development's level state (dv2/sp-level.json): a pending WARNING goes back to INFO
dv2_sptrace "$OUT/sp.bin"
dv2_dumpcheck "$OUT/sp.bin" || true
dv2_z2 "$OUT/z2"
dv2_config "$OUT/config.json"
if dry; then "${DV2PY[@]}" dry-sampler --card "$CARD" --out "$OUT/tel.jsonl" --seconds 1 --every-ms 100 --reset-ms 1000
else hold10 "$ETTELEM" sample --seconds 1 --every-ms 100 --reset-ms 1000 > "$OUT/tel.jsonl" 2>> "$OUT/mgmt.log"; fi
dry || exec 9>&-
read -r _ READING _ THR COOL <<< "$("${DV2PY[@]}" z1sum --dir "$OUT" --pass "$PASS")"
st=ok; note="reading $READING C, threshold $THR"
if [ "$THR" != 65 ]; then trc=0; dv2_threshold_ok "$OUT/config.json" || trc=$?
  case "$trc" in 1) st=fail; note="$note: THRESHOLD ALERT" ;; 2) st=fail; note="$note: config unreadable" ;; esac; fi
[ "$READING" = null ] && { st=fail; note="no reading"; }
printf '{"exp":"dv2v","pass":%s,"card":"%s","t0_ms":%s,"t1_ms":%s,"die_c_start":%s,"die_c_end":%s,"status":"%s","note":%s}\n' \
  "$PASS" "$CARD" "$T0" "$(now_ms)" "$READING" "$READING" "$st" "$(jstr "$note")" > "$OUT/block.json"
log "dv2v VZ p$PASS: $note"
exit 0
