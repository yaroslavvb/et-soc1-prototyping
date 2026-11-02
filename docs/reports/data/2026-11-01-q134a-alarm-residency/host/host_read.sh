#!/bin/bash
# Q134(a): read-only host reads. Opens no ET device node and takes no card lock.
echo "== host $(hostname -s) $(date '+%F %T %Z') epoch $(date +%s)"
echo "== uptime: $(cat /proc/uptime)  btime: $(awk '/^btime/{print $2}' /proc/stat)"
echo "== et-who"; timeout 10 et-who 2>&1 | head -12
echo "== logins (count only): $(who | wc -l)"
for f in /sys/bus/pci/devices/*/err_stats/ce_count; do
  [ -r "$f" ] || continue
  echo "== $f"; cat "$f"
done
echo "== kernel log"
LOG=$(dmesg 2>/dev/null)
if [ -z "$LOG" ]; then LOG=$(journalctl -k -b --no-pager -o short-monotonic 2>/dev/null); echo "source: journalctl"; else echo "source: dmesg"; fi
echo "lines: $(printf '%s\n' "$LOG" | wc -l)"
echo "first: $(printf '%s\n' "$LOG" | head -1 | cut -c1-60)"
# one line per ET event: [monotonic s] device | desc | syndrome
printf '%s\n' "$LOG" | awk '
  /ET [0-9a-f:.]+: Error Event Detected/ { if (dev != "") print ts " | " dev " | " desc " | " syn; match($0, /\[ *[0-9.]+\]/); ts = substr($0, RSTART+1, RLENGTH-2); gsub(/ /, "", ts); match($0, /ET [0-9a-f:.]+/); dev = substr($0, RSTART+3, RLENGTH-3); desc = ""; syn = ""; next }
  dev != "" && /Desc *:/ { sub(/.*Desc *: */, ""); desc = $0; next }
  dev != "" && /Syndrome *:/ { sub(/.*Syndrome *: */, ""); syn = $0; next }
  END { if (dev != "") print ts " | " dev " | " desc " | " syn }
' > /tmp/q134a_events.$$ 
echo "events: $(wc -l < /tmp/q134a_events.$$)"
echo "== events by device and kind"; awk -F' [|] ' '{print $2 " | " $3}' /tmp/q134a_events.$$ | sort | uniq -c
echo "== PMIC and throttling events (all)"; grep -E "Power Management|Thermal Throttling|Temperature Overshoot" /tmp/q134a_events.$$
echo "== last SP Runtime Error"; grep "SP Runtime Error" /tmp/q134a_events.$$ | tail -1
rm -f /tmp/q134a_events.$$
