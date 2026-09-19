# Build and run ET-SoC-1 prototypes.  Everything here runs on Linux, so from
# the Mac prefix commands with scripts/vm, e.g.
#   scripts/vm make                      # build kernels + launchers
#   scripts/vm make run-hello            # run hello on the sysemu simulator
#   make run-hello DEVICE=silicon        # (on a lab machine with a card)

ET         ?= /opt/et
GP_SDK     := $(CURDIR)/external/et-platform/gp-sdk
BUILD      ?= $(CURDIR)/build
RUN_DIR    ?= $(BUILD)/run
ADDRESS    ?= 0x8006335000
JOBS       ?= $(shell nproc)
DEVICE     ?= sysemu
# Extra sys_emu flags for DEVICE=sysemu, e.g. SIM_PARAMS="-vpurf_check -mem_check"
SIM_PARAMS ?=

CMAKE_PATHS := -DCMAKE_PREFIX_PATH="$(ET);$(ET)/lib/cmake" \
               -DCMAKE_MODULE_PATH="$(ET)/lib/cmake;$(ET)/lib/cmake/cmake-modules"

.PHONY: all kernels launchers run-hello trace upstream-test upstream-hello sgemm run-sgemm clean

all: kernels launchers

$(BUILD)/kernels/CMakeCache.txt:
	cmake -S $(GP_SDK)/device -B $(BUILD)/kernels $(CMAKE_PATHS) \
	  -DCMAKE_TOOLCHAIN_FILE=$(ET)/lib/cmake/riscv64-ec-toolchain.cmake \
	  -DCMAKE_BUILD_TYPE=Release -DADDRESS:STRING=$(ADDRESS) -DBUILD_TESTS=OFF \
	  -DCUSTOM_KERNELS_SRC_DIR=$(CURDIR)/kernels -DCUSTOM_KERNELS_BIN_DIR=$(BUILD)/kernels/nekko

kernels: $(BUILD)/kernels/CMakeCache.txt
	cmake --build $(BUILD)/kernels -j$(JOBS)

$(BUILD)/launchers/CMakeCache.txt:
	cmake -S launchers -B $(BUILD)/launchers $(CMAKE_PATHS) -DCMAKE_BUILD_TYPE=Release

launchers: $(BUILD)/launchers/CMakeCache.txt
	cmake --build $(BUILD)/launchers -j$(JOBS)

# The launcher writes sys_emu UART logs and trace dumps to the current dir.
run-hello: all
	mkdir -p $(RUN_DIR)
	cd $(RUN_DIR) && $(BUILD)/launchers/hello_launcher \
	  --kernel_path=$(BUILD)/kernels/nekko/hello.elf --device_type=$(DEVICE) \
	  $(if $(SIM_PARAMS),--simulator_params="$(SIM_PARAMS)")

# Standalone workload (et-testdrive style, no gp-sdk): see workloads/sgemm/README.md.
# On a lab machine: scripts/deploy-lab.sh aifoundry3 workloads/sgemm
sgemm:
	cmake -S workloads/sgemm -B $(BUILD)/sgemm -DCMAKE_PREFIX_PATH=$(ET) -Wno-dev > /dev/null
	cmake --build $(BUILD)/sgemm -j$(JOBS)

run-sgemm: sgemm
	mkdir -p $(BUILD)/sgemm/run
	cd $(BUILD)/sgemm/run && $(BUILD)/sgemm/host/sgemm_host --sysemu -n 128 --reps 1 $(if $(SIM_PARAMS),--sim-args "$(SIM_PARAMS)")

# Print et_printf() output from the last run's device trace dump.
trace:
	$(BUILD)/launchers/trace_dump $(RUN_DIR)/traceKernels_dev0_0.bin

# The hello world from et-platform's README / CI.
upstream-test:
	mkdir -p $(RUN_DIR)
	cd $(RUN_DIR) && $(ET)/bin/it_test_code_loading

# gp-sdk's own hello world (needs patches/et-platform-0002 to boot sysemu).
upstream-hello:
	mkdir -p $(RUN_DIR)
	cd $(RUN_DIR) && $(ET)/bin/hello_world_launcher --kernel_path=$(ET)/kernels/print.elf --device_type=$(DEVICE)
	$(BUILD)/launchers/trace_dump $(RUN_DIR)/traceKernels_dev0_0.bin

clean:
	rm -rf $(BUILD)
