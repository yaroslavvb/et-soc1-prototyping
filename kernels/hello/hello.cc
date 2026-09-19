// Hello world for ET-SoC-1: every hart that takes part in the launch fills in
// its own HelloRecord, and relative thread 0 also prints through the device
// trace buffer (decoded on the host with dt2json).
#include <etsoc/common/utils.h>
#include <etsoc/isa/hart.h>

#include "entryPoint.h"
#include "hello_args.h"

int hello(HelloArgs* args);
// Same entry point for hart 0 and hart 1 of every minion -> 2 threads per core.
DECLARE_KERNEL_ENTRY_POINTS(hello, hello);

int hello(HelloArgs* args) {
  const int tid = get_relative_thread_id();
  if (tid < 0 || static_cast<uint64_t>(tid) >= args->num_records) {
    return 0;
  }

  auto* rec = reinterpret_cast<HelloRecord*>(args->records) + tid;
  rec->hart_id = get_hart_id();
  rec->rel_tid = tid;
  rec->num_threads = static_cast<uint32_t>(get_num_threads());
  rec->shire_id = get_shire_id();
  rec->minion_id = get_minion_id();
  rec->thread_id = get_thread_id();
  rec->magic = HELLO_MAGIC;

  if (tid == 0) {
    et_printf("hello from hart %u: %d harts are running this kernel\n", get_hart_id(), get_num_threads());
  }
  return 0;
}
