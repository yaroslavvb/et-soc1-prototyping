#!/usr/bin/env python3
"""E184's host-only change to the energy catalogue's host (the kit; E184.md section 2.1): --schedule and --stop-file.

    python3 -B tools/claims-v3/e184/host_patch_e184.py --src workloads/enercat --dst build/enercat-e184-src   # copy, then patch
    python3 -B tools/claims-v3/e184/host_patch_e184.py --check workloads/enercat                             # the patch's sha256s

It copies the committed workloads/enercat into a build tree (nothing committed is edited) and makes four insertions in the copy's
host/main.cpp, each at an anchor that must occur exactly once in the committed file (sha256 3cad4adc...): the two options in the
Options struct, a runSchedule() function before run(), one line at the top of run()'s launch loop that hands a --schedule run to it,
and the two option words in main()'s parser. The kernel and every other file are copied unchanged. The input's and the output's sha256
must equal SRC_SHA256 and OUT_SHA256 below, else nothing is written (exit 2).

What runSchedule() does: reads the schedule ("<label> <launches> <image>" per line, 1-64 launches a segment), loads every image (each
exactly EC_MAX_HARTS x 256 B, one operand block per hart), and for each segment copies its image to the card's source buffer, then
launches; before every launch it checks the stop file (exit 8) and the device budget (exit 9). One ENERCAT line per launch, with the
catalogue's fields and "seg", "label" and "image". No device-management command: the copies and launches go through the runtime.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import os
import shutil
import sys

SRC_SHA256 = "3cad4adc16534b845cc142f78a28907192b62fe21081e282d6df67342200359c"
OUT_SHA256 = "7360e5e1501c66a1517a1173f188dcd2e4b4bb97b5049744374c8bf1152409c6"   # the patched host/main.cpp, pinned

A_OPTS = "  std::string kernel = KERNEL_ELF;\n"
B_OPTS = A_OPTS + "  std::string schedule, stopFile;   // E184 (tools/claims-v3/e184): --schedule <file>, --stop-file <path>\n"

A_RUN = "int run(const Options& o, Session& dev) {\n"
B_FUNC = r'''// E184 (tools/claims-v3/e184, the host-only change): --schedule <file> runs segments "<label> <launches> <image>" in order; each image is
// exactly EC_MAX_HARTS x 256 B (one 256 B operand block per hart), copied to the card's source buffer before the segment's first launch.
// --stop-file <path> is checked before every launch. One ENERCAT line per launch, with "seg", "label" and "image".
int runSchedule(const Options& o, Session& dev, const Pat& p, EcArgs a, std::byte* sbuf, size_t sbytes, uint64_t harts,
                uint64_t shireMaskUsed) {
  struct Seg { std::string label, image; long launches; };
  std::vector<Seg> segs;
  std::ifstream f(o.schedule);
  if (!f) throw std::runtime_error("--schedule: cannot read " + o.schedule);
  std::string label, image;
  long nl = 0;
  while (f >> label >> nl >> image) segs.push_back(Seg{label, image, nl});
  if (segs.empty()) throw std::runtime_error("--schedule: no segments in " + o.schedule);
  std::map<std::string, std::vector<std::byte>> imgs;
  for (const auto& s : segs) {
    if (s.launches < 1 || s.launches > 64) throw std::runtime_error("--schedule: 1-64 launches a segment");
    if (imgs.count(s.image)) continue;
    auto b = readFile(s.image);
    if (b.size() != sbytes) throw std::runtime_error("--schedule: " + s.image + " is not " + std::to_string(sbytes) + " bytes");
    imgs[s.image] = std::move(b);
  }
  for (size_t k = 0; k < segs.size(); ++k) {
    dev.put(imgs[segs[k].image].data(), sbuf, sbytes);
    const std::string base = fs::path(segs[k].image).filename().string();
    for (long i = 0; i < segs[k].launches; ++i) {
      if (!o.stopFile.empty() && fs::exists(o.stopFile)) {
        std::fprintf(stderr, "stop file %s: stopping before segment %zu launch %ld\n", o.stopFile.c_str(), k, i);
        return 8;
      }
      if (dev.overBudget()) {
        std::fprintf(stderr, "over the %.1f s budget before segment %zu launch %ld\n", o.budget, k, i);
        return 9;
      }
      std::vector<EcResult> res;
      double wallS = 0;
      const bool ok = dev.launch(a, res, wallS);
      uint64_t n = 0, iters = 0, cmax = 0;
      double csum = 0;
      for (const auto& r : res) {
        if (r.magic != EC_MAGIC) continue;
        ++n; iters += r.iters; cmax = std::max<uint64_t>(cmax, r.cycles); csum += double(r.cycles);
      }
      const double ops = double(iters) * double(p.opsPerIter);
      const double secs = cmax / 0.6e9;
      std::printf("ENERCAT {\"pattern\":\"%s\",\"unit\":\"%s\",\"operands\":\"schedule\",\"harts\":%llu,\"shires\":%d,"
                  "\"participants\":%llu,\"shire_mask_used\":\"0x%llx\",\"ops\":%.0f,\"cycles_max\":%llu,\"cycles_mean\":%.0f,"
                  "\"ops_per_s\":%.4e,\"ops_per_cycle_per_hart\":%.4f,\"wall_s\":%.4f,\"t_start_ms\":%lld,\"t_end_ms\":%lld,"
                  "\"seg\":%zu,\"label\":\"%s\",\"image\":\"%s\",\"ok\":%s}\n",
                  o.pattern.c_str(), p.unit, (unsigned long long)harts, __builtin_popcountll(shireMaskUsed),
                  (unsigned long long)n, (unsigned long long)shireMaskUsed, ops, (unsigned long long)cmax, n ? csum / double(n) : 0.0,
                  secs > 0 ? ops / secs : 0.0, (cmax && n) ? ops / double(cmax) / double(n) : 0.0, wallS, dev.t0Ms, dev.t1Ms, k,
                  segs[k].label.c_str(), base.c_str(), (ok && n) ? "true" : "false");
      std::fflush(stdout);
      if (!ok || !n) return 1;
    }
  }
  return 0;
}

'''

A_LOOP = "  const auto tStart = Clock::now();\n"
B_LOOP = ("  if (!o.schedule.empty()) return runSchedule(o, dev, p, a, sbuf, src.size() * 4, harts, shireMaskUsed);   // E184\n"
          + A_LOOP)

A_ARGS = '    else if (a == "--list") {\n'
B_ARGS = ('    else if (a == "--schedule") o.schedule = next();      // E184\n'
          '    else if (a == "--stop-file") o.stopFile = next();     // E184\n' + A_ARGS)

EDITS = [(A_OPTS, B_OPTS), (A_RUN, B_FUNC + A_RUN), (A_LOOP, B_LOOP), (A_ARGS, B_ARGS)]


def patched(text):
    for a, b in EDITS:
        if text.count(a) != 1:
            raise SystemExit("host_patch_e184: anchor %r occurs %d times, not once: refusing" % (a.strip()[:60], text.count(a)))
        text = text.replace(a, b)
    return text


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main(argv):
    if len(argv) == 2 and argv[0] == "--check":
        src = open(os.path.join(argv[1], "host", "main.cpp"), "rb").read()
        out = patched(src.decode()).encode()
        print("host_patch_e184 --check: input %s (%s), patched %s (%s)" % (
            sha(src), "the committed file" if sha(src) == SRC_SHA256 else "NOT the committed file", sha(out),
            "the pinned result" if sha(out) == OUT_SHA256 else "NOT the pinned result"))
        return 0 if sha(src) == SRC_SHA256 and sha(out) == OUT_SHA256 else 2
    if len(argv) == 4 and argv[0] == "--src" and argv[2] == "--dst":
        s, d = argv[1], argv[3]
        src = open(os.path.join(s, "host", "main.cpp"), "rb").read()
        if sha(src) != SRC_SHA256:
            print("host_patch_e184: %s/host/main.cpp is %s, not the committed %s: nothing written" % (s, sha(src), SRC_SHA256))
            return 2
        out = patched(src.decode()).encode()
        if sha(out) != OUT_SHA256:
            print("host_patch_e184: the patched file is %s, not the pinned %s: nothing written" % (sha(out), OUT_SHA256))
            return 2
        if os.path.exists(d):
            shutil.rmtree(d)
        shutil.copytree(s, d, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        open(os.path.join(d, "host", "main.cpp"), "wb").write(out)
        print("host_patch_e184: %s -> %s, host/main.cpp %s" % (s, d, sha(out)))
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
