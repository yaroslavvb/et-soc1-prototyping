// ccheck's mock build: the SysEmuOptions fields main.cpp sets (the mock never starts a simulator).
#pragma once
#include <cstdint>
#include <string>
#include <vector>
namespace emu {
struct SysEmuOptions {
  std::string bootromTrampolineToBL2ElfPath, spBL2ElfPath, masterMinionElfPath, machineMinionElfPath, workerMinionElfPath;
  std::string executablePath, runDir;
  uint64_t maxCycles = 0, minionShiresMask = 0;
  std::string puUart0Path, puUart1Path, spUart0Path, spUart1Path;
  bool startGdb = false;
  std::vector<std::string> additionalOptions;
};
}  // namespace emu
