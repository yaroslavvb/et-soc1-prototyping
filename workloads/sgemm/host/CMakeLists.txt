# Host program.  Links both device layers; --sysemu picks the simulator at run time.
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
set(KERNEL_ELF "${CMAKE_BINARY_DIR}/kernel/sgemm.elf")
configure_file(Constants.h.in ${CMAKE_CURRENT_BINARY_DIR}/Constants.h)

add_executable(sgemm_host main.cpp)
target_include_directories(sgemm_host PRIVATE ${CMAKE_CURRENT_BINARY_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/..)
target_compile_features(sgemm_host PRIVATE cxx_std_17)
target_compile_options(sgemm_host PRIVATE -O2)
target_link_libraries(sgemm_host PRIVATE runtime::etrt deviceLayer::deviceLayer sw-sysemu::sw-sysemu)
