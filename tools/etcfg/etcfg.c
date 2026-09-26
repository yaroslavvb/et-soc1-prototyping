/* Read a card's static device configuration over the driver's read-only ioctl, and print it as JSON.
 *
 *     etcfg [/dev/et0_mgmt ...]
 *
 * ETSOC1_IOCTL_GET_DEVICE_CONFIGURATION (et_ioctl.h) returns `struct dev_config`, which carries the board's
 * nameplate TDP in watts. The service processor's governor compares measured SoC power against its own TDP level
 * instead (`check_power_throttle_conditions()` in ServiceProcessorBL2/services/thermal_pwr_mgmt.c reads
 * `g_pmic_power_reg.module_tdp_level`), which this ioctl does not show: it reads 65 W on every lab card, including
 * aifoundry3, whose governor level a boot service sets to 0 so that it can only ever throttle down (E21;
 * `ettelem config` reads the governor's value). The ioctl only reads; it changes nothing on the card. */
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include "et_ioctl.h"

int main(int argc, char** argv)
{
    const char* def[] = {"/dev/et0_mgmt", "/dev/et1_mgmt"};
    int n = argc > 1 ? argc - 1 : 2;
    for (int i = 0; i < n; ++i) {
        const char* path = argc > 1 ? argv[i + 1] : def[i];
        int fd = open(path, O_RDWR);
        if (fd < 0) { if (argc > 1) printf("{\"dev\":\"%s\",\"error\":\"cannot open\"}\n", path); continue; }
        struct dev_config c;
        memset(&c, 0, sizeof c);
        if (ioctl(fd, ETSOC1_IOCTL_GET_DEVICE_CONFIGURATION, &c) < 0) {
            printf("{\"dev\":\"%s\",\"error\":\"ioctl failed\"}\n", path);
        } else {
            printf("{\"dev\":\"%s\",\"tdp_w\":%u,\"minion_boot_freq_mhz\":%u,\"cm_shire_mask\":\"0x%08x\","
                   "\"form_factor\":%u,\"arch_rev\":%u,\"devnum\":%u,\"l3_kb\":%u,\"l2_kb\":%u,\"scp_kb\":%u,"
                   "\"ddr_mb_s\":%u,\"line_b\":%u,\"l2_banks\":%u,\"sync_shire\":%u}\n",
                   path, c.tdp, c.minion_boot_freq, c.cm_shire_mask, c.form_factor, c.arch_rev, c.devnum,
                   c.total_l3_size, c.total_l2_size, c.total_scp_size, c.ddr_bandwidth, c.cache_line_size,
                   c.num_l2_cache_banks, c.sync_min_shire_id);
        }
        close(fd);
    }
    return 0;
}
