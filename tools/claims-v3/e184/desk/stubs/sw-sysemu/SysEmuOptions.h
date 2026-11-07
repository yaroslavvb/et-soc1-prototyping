// desk stub (E184 syntax check only)
#pragma once
#include <cstdint>
#include <string>
#include <vector>
namespace emu { struct SysEmuOptions { std::string bootromTrampolineToBL2ElfPath, spBL2ElfPath, masterMinionElfPath, machineMinionElfPath,
  workerMinionElfPath, executablePath, runDir, puUart0Path, puUart1Path, spUart0Path, spUart1Path; uint64_t maxCycles = 0,
  minionShiresMask = 0; bool startGdb = false; std::vector<std::string> additionalOptions; }; }
