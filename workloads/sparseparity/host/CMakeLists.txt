# Host program (links both device layers; --sysemu picks the simulator at run time) and the CPU-only self-test.
find_package(runtime REQUIRED)
find_package(deviceLayer REQUIRED)
find_package(sw-sysemu REQUIRED)
find_package(EsperantoBootLoader REQUIRED)
find_package(EsperantoDeviceMinionRuntime REQUIRED)

# Firmware that the simulator has to boot (a real card boots its own from flash).
get_property(BOOTROM_TRAMPOLINE_TO_BL2_ELF TARGET EsperantoBootLoader::BootromTrampolineToBL2.elf PROPERTY LOCATION)
get_property(BL2_ELF TARGET EsperantoBootLoader::ServiceProcessorBL2_fast-boot.elf PROPERTY LOCATION)
get_property(MASTER_MINION_ELF TARGET EsperantoDeviceMinionRuntime::MasterMinion.elf PROPERTY LOCATION)
get_property(MACHINE_MINION_ELF TARGET EsperantoDeviceMinionRuntime::MachineMinion.elf PROPERTY LOCATION)
get_property(WORKER_MINION_ELF TARGET EsperantoDeviceMinionRuntime::WorkerMinion.elf PROPERTY LOCATION)
set(SYSEMU_INSTALL_DIR "${CMAKE_PREFIX_PATH}/bin/")
set(KERNEL_ELF "${CMAKE_BINARY_DIR}/kernel/sparseparity.elf")
configure_file(Constants.h.in ${CMAKE_CURRENT_BINARY_DIR}/Constants.h)

find_package(Threads REQUIRED)  # stage 2 of the two-stage screen (M5) rescoring on host threads

add_executable(sparseparity_host main.cpp)
target_include_directories(sparseparity_host PRIVATE ${CMAKE_CURRENT_BINARY_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/..)
target_compile_features(sparseparity_host PRIVATE cxx_std_17)
target_compile_options(sparseparity_host PRIVATE -O2 -mpopcnt)  # the CPU oracle is popcount-bound
target_link_libraries(sparseparity_host PRIVATE runtime::etrt deviceLayer::deviceLayer sw-sysemu::sw-sysemu Threads::Threads)

# CPU only: no runtime, no device (safe to run anywhere; its process name is not a device process's).
add_executable(spp_selftest spp_selftest.cpp)
target_include_directories(spp_selftest PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/..)
target_compile_features(spp_selftest PRIVATE cxx_std_17)
target_compile_options(spp_selftest PRIVATE -O2 -mpopcnt)
target_link_libraries(spp_selftest PRIVATE Threads::Threads)
