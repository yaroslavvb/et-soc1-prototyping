// Decode a device trace dump written by GenericLauncher::dumpTracesToFile()
// (traceKernels_dev<N>_<i>.bin) and print the et_printf() strings.  A minimal
// stand-in for Esperanto's dt2json, which is not part of the open-source tree.
//   trace_dump [-a] <trace.bin>     -a: also list non-string events
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iterator>
#include <map>
#include <string>
#include <vector>

#define ET_TRACE_DECODER_IMPL
#include <et-trace/decoder.h>
#include <et-trace/layout.h>

int main(int argc, char** argv) {
  bool all = false;
  const char* path = nullptr;
  for (int i = 1; i < argc; ++i) {
    if (!std::strcmp(argv[i], "-a")) {
      all = true;
    } else {
      path = argv[i];
    }
  }
  if (!path) {
    std::fprintf(stderr, "usage: %s [-a] <trace.bin>\n", argv[0]);
    return 2;
  }
  std::ifstream in(path, std::ios::binary);
  std::vector<char> buf((std::istreambuf_iterator<char>(in)), std::istreambuf_iterator<char>());
  if (buf.size() < sizeof(trace_buffer_std_header_t)) {
    std::fprintf(stderr, "%s: too small to be a trace buffer\n", path);
    return 1;
  }
  const auto* tb = reinterpret_cast<const trace_buffer_std_header_t*>(buf.data());
  if (tb->magic_header != TRACE_MAGIC_HEADER) {
    std::fprintf(stderr, "%s: bad magic 0x%x (tracing disabled or buffer not written?)\n", path, tb->magic_header);
    return 1;
  }

  std::map<int, size_t> counts;
  for (const trace_entry_header_t* e = Trace_Decode(tb, nullptr); e; e = Trace_Decode(tb, e)) {
    counts[e->type]++;
    if (e->type == TRACE_TYPE_STRING) {
      const auto* s = reinterpret_cast<const trace_string_t*>(e);
      std::string text(s->string, strnlen(s->string, e->payload_size));
      while (!text.empty() && text.back() == '\n') text.pop_back();
      std::printf("[cycle %llu hart %u] %s\n", (unsigned long long)e->cycle, e->hart_id, text.c_str());
    } else if (all) {
      std::printf("[cycle %llu hart %u] event type %d, %u payload bytes\n", (unsigned long long)e->cycle,
                  e->hart_id, e->type, e->payload_size);
    }
  }
  if (all || counts.size() > counts.count(TRACE_TYPE_STRING)) {
    for (auto [type, n] : counts) std::fprintf(stderr, "event type %d: %zu entries\n", type, n);
  }
  return 0;
}
