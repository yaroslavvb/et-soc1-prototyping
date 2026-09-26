# etcfg

Prints a card's static device configuration as JSON, straight from the driver:

```
$ gcc -O2 -I/opt/et/include -o etcfg etcfg.c && ./etcfg
{"dev":"/dev/et0_mgmt","tdp_w":65,"minion_boot_freq_mhz":600,"cm_shire_mask":"0xffffffff", ...}
```

One `ETSOC1_IOCTL_GET_DEVICE_CONFIGURATION` per device node. It reads and nothing else.

It exists because the governor's behaviour depends on the board's static TDP, and **the driver and the
firmware do not always agree about it**. On aifoundry3 this tool reports 65 W while the service processor
reports 0 W, which is why that card is pinned at 600 MHz. Ask the firmware too:

```
LD_LIBRARY_PATH=/opt/et/lib build/ettelem/ettelem config
{"tdp_w":0,"temp_threshold_c":65,"power_state":0,"power_state_name":"max_power","minion_mhz":600,"minion_mv":523}
```

Unlike `ettelem`, `etcfg` does not use `libDM.so` and does not open the management node, so it still works on
a machine whose library refuses the card (aifoundry1 until 25 September 2026) and while another process is sampling telemetry.
