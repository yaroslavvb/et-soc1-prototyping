/*-------------------------------------------------------------------------
 * pciebench's device kernel: it does nothing. Every hart of every shire in the launch's mask enters, returns 0 and
 * goes back to the firmware, so a launch's wall time on the host is the launch path alone: the command through the
 * submission queue, the master shire's dispatch to the compute shires, their start and return, and the completion
 * back to the host.
 *-------------------------------------------------------------------------*/
#include <stdint.h>

int64_t entry_point(const void* args);

int64_t entry_point(const void* args)
{
    (void)args;
    return 0;
}
