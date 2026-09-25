#!/bin/bash
# Read-only fact collection for the ET-SoC-1 driver/runtime. Never opens /dev/et* (only stat/ls).
# No sudo, no writes except to stdout.
exec 2>&1
export LC_ALL=C
sec(){ echo; echo "===== $* ====="; }
run(){ echo "\$ $*"; timeout 20 "$@"; echo "[rc=$?]"; }

sec identity
run date -Is
run hostname
run id
run uname -a
cat /etc/os-release 2>/dev/null | grep -E '^(PRETTY_NAME|VERSION_ID)='
run uptime
echo "boot time: $(uptime -s 2>/dev/null)"
cat /proc/cmdline

sec who / users
run who
run w -h
echo "--- non-kernel-thread processes by user (count) ---"
ps -eo user= | sort | uniq -c | sort -rn
echo "--- processes whose name/args mention et tools ---"
ps -eo user,pid,lstart,args | grep -E -i 'dev_mngt|ettelem|_host|et_soc1|et-soc1|etcfg|sparsity|runtime|et0_|et1_|nocbench|sgemm|/opt/et' | grep -v -E 'grep -E|collect.sh'

sec lsmod
lsmod | head -1; lsmod | grep -i -E '^et|esperanto|et_soc1'

sec modinfo et_soc1
run modinfo et_soc1
for f in filename srcversion vermagic version name depends license author description; do
  printf '%-11s: %s\n' "$f" "$(modinfo -F $f et_soc1 2>&1)"; done
echo "--- modinfo for other possible names ---"
for n in esperanto et-soc1 etsoc1; do modinfo -F filename $n 2>&1 | sed "s/^/$n: /"; done

sec /sys/module/et_soc1
ls -la --time-style=full-iso /sys/module/et_soc1/ 2>&1
for f in srcversion version refcnt initstate taint coresize initsize; do
  if [ -e /sys/module/et_soc1/$f ]; then
    printf '%-10s: [%s] (bytes: %s)\n' "$f" "$(cat /sys/module/et_soc1/$f 2>&1)" "$(wc -c < /sys/module/et_soc1/$f 2>&1)"
    [ "$f" = version ] && { echo -n "version hexdump: "; od -An -c /sys/module/et_soc1/version 2>&1; }
  else
    printf '%-10s: <absent>\n' "$f"
  fi
done
echo "--- parameters ---"
for p in /sys/module/et_soc1/parameters/*; do [ -e "$p" ] && printf '%s = %s\n' "$(basename $p)" "$(cat $p 2>&1)"; done
echo "--- holders/drivers ---"
ls -la /sys/module/et_soc1/holders /sys/module/et_soc1/drivers 2>&1
echo "--- sections .text addr (usually 0 for non-root) ---"
cat /sys/module/et_soc1/sections/.text 2>&1 | head -1

sec module files on disk
KO=$(modinfo -F filename et_soc1 2>/dev/null)
echo "modinfo filename: $KO"
if [ -n "$KO" ] && [ -e "$KO" ]; then
  ls -la --time-style=full-iso "$KO"; stat "$KO"; sha256sum "$KO"
  readlink -f "$KO"
fi
echo "--- every et_soc1 / et-soc1 / esperanto .ko under /lib/modules (all kernels) ---"
find /lib/modules /usr/lib/modules -regextype egrep -iregex '.*/(et[-_]soc1|esperanto)[^/]*\.ko(\.[a-z]+)?' -printf '%TY-%Tm-%Td %TH:%TM:%TS  %10s  %p\n' 2>/dev/null | sort -u
echo "--- modules.dep entry ---"
grep -i -E 'et[-_]soc1|esperanto' /lib/modules/$(uname -r)/modules.dep 2>&1
echo "--- installed kernels ---"
ls -la --time-style=full-iso /lib/modules/ 2>&1
ls -la --time-style=full-iso /boot/ 2>&1 | grep -E 'vmlinuz|initrd'
echo "--- updates/extra/kernel/extra dirs ---"
for d in updates updates/dkms extra kernel/extra; do echo "## /lib/modules/$(uname -r)/$d"; ls -la --time-style=full-iso /lib/modules/$(uname -r)/$d 2>&1 | head -20; done

sec strings of the .ko
# no temp files: operate on the .ko directly when uncompressed, else stream it
if [ -n "$KO" ] && [ -e "$KO" ]; then
  case "$KO" in
    *.zst) CAT="zstd -dc";; *.xz) CAT="xz -dc";; *.gz) CAT="gzip -dc";; *) CAT=cat;;
  esac
  if [ "$CAT" = cat ]; then
    echo "--- .modinfo section ---"; readelf -p .modinfo "$KO" 2>&1 | head -40
    echo "--- .comment ---"; readelf -p .comment "$KO" 2>&1 | head -10
  fi
  echo "--- strings matching version/build/gcc ---"
  $CAT "$KO" 2>/dev/null | strings -a | grep -E -i 'version=|srcversion=|vermagic=|GCC: |^0\.[0-9]+\.[0-9]+|name=|depends=|retpoline=|intree=' | sort | uniq -c | sort -rn | head -30
  echo "--- signature trailer ---"
  $CAT "$KO" 2>/dev/null | tail -c 40 | strings -a
fi

sec how the module got there: dkms / packages / config
run dkms status
ls -la --time-style=full-iso /var/lib/dkms/ 2>&1
find /var/lib/dkms -maxdepth 4 -printf '%TY-%Tm-%Td %TH:%TM  %p -> %l\n' 2>/dev/null | head -40
for f in /var/lib/dkms/*/*/source/dkms.conf /var/lib/dkms/*/*/source/VERSION; do [ -e "$f" ] && { echo "## $f"; cat "$f"; }; done
find /var/lib/dkms -name make.log 2>/dev/null | while read f; do echo "## $f"; ls -la --time-style=full-iso "$f"; head -20 "$f" 2>&1; done
echo "--- /usr/src ---"
ls -la --time-style=full-iso /usr/src/ 2>&1
for d in /usr/src/et* /usr/src/esperanto*; do [ -d "$d" ] && { echo "## $d"; ls -la --time-style=full-iso "$d"; cat "$d/VERSION" "$d/dkms.conf" 2>&1; head -8 "$d/Makefile" 2>&1; }; done
echo "--- dpkg ---"
dpkg -l 2>/dev/null | grep -i -E 'esperanto|et-soc|etsoc|et_soc|ainekko|nekko|et-platform|et-driver|dkms'
[ -n "$KO" ] && dpkg -S "$KO" 2>&1
dpkg -S /opt/et/lib/libDM.so 2>&1 | head -3
echo "--- modprobe.d / modules-load.d / udev ---"
grep -r -i -E 'et[-_]soc1|esperanto' /etc/modprobe.d /etc/modules-load.d /etc/modules /usr/lib/modprobe.d /usr/lib/modules-load.d 2>/dev/null
grep -r -l -i -E 'et[-_]soc1|esperanto|KERNEL=="et' /etc/udev/rules.d /lib/udev/rules.d /usr/lib/udev/rules.d 2>/dev/null | while read f; do echo "## $f"; ls -la --time-style=full-iso "$f"; cat "$f"; done
echo "--- systemd units ---"
systemctl list-unit-files --no-pager 2>/dev/null | grep -i -E 'dev_mngt|dev-mngt|esperanto|et[-_]soc|etsoc|et-'
systemctl list-units --all --no-pager 2>/dev/null | grep -i -E 'dev_mngt|dev-mngt|esperanto|et[-_]soc|etsoc'
for u in $(systemctl list-unit-files --no-pager --plain --no-legend 2>/dev/null | awk '{print $1}' | grep -i -E 'dev_mngt|dev-mngt|esperanto|et[-_]soc|etsoc'); do
  echo "## unit $u"; systemctl cat --no-pager "$u" 2>&1 | head -40; systemctl status --no-pager "$u" 2>&1 | head -15; done
ls -la --time-style=full-iso /etc/systemd/system/ 2>/dev/null | grep -i -E 'dev_mngt|et|esperanto'

sec /opt/et install
ls -la --time-style=full-iso /opt/ 2>&1
ls -la --time-style=full-iso /opt/et 2>&1
readlink -f /opt/et
ls -la --time-style=full-iso /opt/et/lib 2>&1 | head -80
ls -la --time-style=full-iso /opt/et/bin 2>&1 | head -60
echo "--- version-ish files ---"
find /opt/et -maxdepth 4 \( -iname '*version*' -o -iname 'VERSION' -o -iname '*.txt' -o -iname 'BUILD*' -o -iname '*manifest*' \) -not -path '*/include/*' -type f 2>/dev/null | head -40 | while read f; do echo "## $f"; head -c 600 "$f"; echo; done
echo "--- cmake Version files ---"
for f in /opt/et/lib/cmake/*/*Version.cmake /opt/et/lib/cmake/*/*/*Version.cmake; do [ -e "$f" ] && printf '%s: %s\n' "$f" "$(grep -m1 -E 'set\(PACKAGE_VERSION' "$f")"; done
echo "--- libDM ---"
ls -la --time-style=full-iso /opt/et/lib/libDM* /opt/et/lib/libdevice* /opt/et/lib/libetrt* /opt/et/lib/libdevicelayer* 2>&1
for f in $(ls /opt/et/lib/libDM*.so* /opt/et/lib/libdevicelayer*.so* 2>/dev/null); do [ -f "$f" ] && ! [ -L "$f" ] && sha256sum "$f"; done
readlink -f /opt/et/lib/libDM.so
echo "--- strings in libDM / devicelayer / dev_mngt_service: version checks ---"
for f in /opt/et/lib/libDM.so /opt/et/lib/libdevicelayer.so /opt/et/lib/libdevicelayer*.so* /opt/et/bin/dev_mngt_service; do
  [ -e "$f" ] || continue
  echo "## $(readlink -f $f)"
  strings -a "$(readlink -f $f)" | grep -E 'evaluate compatibility|Driver version is incompatible|driver/module/version|^0\.[0-9]+\.[0-9]+$|/sys/bus/pci|srcversion|kMinReq|GCC: ' | sort | uniq -c | head -20
done
echo "--- which binary contains the check ---"
grep -l -a 'evaluate compatibility' /opt/et/lib/*.so* /opt/et/bin/* 2>/dev/null
echo "--- ldd dev_mngt_service ---"
ldd /opt/et/bin/dev_mngt_service 2>&1 | grep -E '/opt/et|not found'
sha256sum /opt/et/bin/dev_mngt_service 2>&1

sec PCIe view
run lspci -nn -k -d 1e0a:
echo "--- lspci -vv (as user) ---"
timeout 20 lspci -vv -nn -d 1e0a: 2>&1
echo "--- upstream bridges ---"
lspci -tv 2>&1 | head -40
for d in /sys/bus/pci/devices/*; do
  [ "$(cat $d/vendor 2>/dev/null)" = "0x1e0a" ] || continue
  echo "## $d"
  for a in vendor device subsystem_vendor subsystem_device class revision current_link_speed current_link_width max_link_speed max_link_width numa_node enable power_state local_cpulist irq msi_bus d3cold_allowed reset_method; do
    printf '  %-20s %s\n' "$a" "$(cat $d/$a 2>&1 | tr '\n' ' ')"; done
  printf '  %-20s %s\n' driver "$(readlink $d/driver 2>&1)"
  printf '  %-20s %s\n' driver_module "$(readlink $d/driver/module 2>&1)"
  printf '  %-20s [%s]\n' "driver/module/version" "$(cat $d/driver/module/version 2>&1)"
  echo "  resource (start end flags):"; cat $d/resource 2>&1 | awk '$1!="0x0000000000000000"{printf "    %s %s %s  size=%d MiB\n",$1,$2,$3,(strtonum($2)-strtonum($1)+1)/1048576}'
  echo "  aer:"; for a in aer_dev_correctable aer_dev_fatal aer_dev_nonfatal; do [ -e $d/$a ] && { echo "   $a:"; cat $d/$a | awk '$2!=0' | sed 's/^/     /'; }; done
  printf '  %-20s %s\n' devnum "$(cat $d/devnum 2>&1)"
  echo "  attribute files present:"; ls $d 2>&1 | tr '\n' ' '; echo
  for g in mem_stats err_stats mgmt_vq_stats ops_vq_stats soc_reset; do
    [ -d $d/$g ] && { echo "  -- $g/"; for x in $d/$g/msg_count $d/$g/byte_count $d/$g/ce_count $d/$g/uce_count $d/$g/cma_allocated $d/$g/pcilink_max_estim_downtime_ms; do [ -f "$x" ] && printf '     %s: %s\n' "$(basename $x)" "$(timeout 3 head -c 300 $x 2>&1 | tr '\n' ' ')"; done; }; done
  up=$(dirname $(readlink -f $d)); echo "  upstream port: $up"
  for a in current_link_speed current_link_width max_link_speed max_link_width; do printf '    up.%-18s %s\n' $a "$(cat $up/$a 2>&1)"; done
done

sec device nodes and sysfs class
ls -la --time-style=full-iso /dev/et* 2>&1
stat -c '%n %A %U:%G dev=%t:%T mtime=%y' /dev/et* 2>&1
find /sys/class -maxdepth 2 -name 'et*' 2>/dev/null | while read c; do echo "## $c -> $(readlink -f $c)"; cat $c/dev 2>/dev/null; done
ls -la /sys/bus/pci/drivers/ 2>/dev/null | grep -i -E 'et|esperanto'
for dr in /sys/bus/pci/drivers/et*soc* /sys/bus/pci/drivers/esperanto*; do [ -d "$dr" ] && { echo "## $dr"; ls -la $dr; }; done

sec kernel log
echo "--- dmesg ---"
timeout 10 dmesg 2>&1 | grep -i -E 'et_soc1|et-soc1|esperanto|1e0a|taint' | tail -60
dmesg >/dev/null 2>&1 || echo "dmesg: $(dmesg 2>&1 | head -1)"
echo "--- journalctl -k -b ---"
timeout 20 journalctl -k -b --no-pager 2>&1 | grep -i -E 'et_soc1|et-soc1|esperanto|1e0a|Hint|No journal|permission|insufficient' | head -80
echo "--- journalctl -k all boots, et_soc1 lines (last 60) ---"
timeout 30 journalctl -k --no-pager 2>&1 | grep -i -E 'et_soc1|et-soc1|esperanto' | tail -60
echo "--- journalctl list-boots ---"
timeout 10 journalctl --list-boots --no-pager 2>&1 | tail -10
echo "--- /var/log ---"
ls -la --time-style=full-iso /var/log/kern.log* /var/log/syslog* /var/log/dmesg* 2>&1
for f in /var/log/kern.log /var/log/syslog /var/log/dmesg; do [ -r "$f" ] && { echo "## $f"; grep -a -i -E 'et_soc1|et-soc1|esperanto' "$f" | tail -40; }; done
echo "--- dpkg / apt history mentioning dkms, linux-image, et ---"
for f in /var/log/dpkg.log /var/log/apt/history.log; do [ -r "$f" ] && { echo "## $f"; grep -a -E 'linux-image|linux-headers|dkms|esperanto|et-soc' "$f" | tail -30; }; done
zcat -f /var/log/apt/history.log.*.gz 2>/dev/null | grep -a -E 'Start-Date|Commandline' | grep -a -B1 -E 'linux-image|dkms' | tail -20

sec kernel taint
cat /proc/sys/kernel/tainted
cat /proc/sys/kernel/dmesg_restrict 2>&1

echo; echo "===== END ====="
