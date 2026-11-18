#!/bin/bash
# verify-v31trace (Q217), run ON aifoundry3 by a3.sh look: READ ONLY. The state before any simulator run: load, memory, disk, et-who,
# any simulator run of this user, v31-trace's built kit copies (hashes only; nothing there is written), and this lane's own folder.
echo "host $(hostname) at $(date '+%F %T %Z'); load $(cut -d' ' -f1-3 /proc/loadavg); mem avail $(free -g | awk '/Mem:/{print $7}') GB; disk $(df -h "$HOME" | awk 'NR==2{print $5" used, "$4" free"}')"
if command -v et-who >/dev/null 2>&1; then timeout 20 et-who 2>&1 | head -3; else echo "no et-who on PATH"; fi
echo "sim runs of this user: $(pgrep -u "$(id -u)" -f 'sparsity_host --sysemu' | wc -l); sys_emu: $(pgrep -u "$(id -u)" -x sys_emu | wc -l)"
V="$HOME/claude/work/q217-v31-trace"
for f in bin/rgm136/sparsity_host bin/rgm136/sparsity.elf bin/rgm211/sparsity_host bin/rgm211/sparsity.elf tiles/fp32/zeros.bin trace_run.py; do
  [ -f "$V/$f" ] && echo "v31-trace $f $(stat -c %s "$V/$f") B $(sha256sum "$V/$f" | cut -d' ' -f1)" || echo "v31-trace $f: absent"
done
ls -la "$HOME/claude/work/q217-verify-v31trace" 2>&1 | head -5
python3 --version 2>&1; ls -la /usr/bin/bwrap 2>&1; command -v prlimit
