# Host program for the card: the runtime over the PCIe device layer only.
find_package(runtime REQUIRED)
find_package(deviceLayer REQUIRED)

set(KERNEL_ELF "${CMAKE_BINARY_DIR}/kernel/x09mem.elf")
configure_file(Constants.h.in ${CMAKE_CURRENT_BINARY_DIR}/Constants.h)

add_executable(x09mem_host main.cpp)
target_include_directories(x09mem_host PRIVATE ${CMAKE_CURRENT_BINARY_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/..)
target_compile_features(x09mem_host PRIVATE cxx_std_17)
target_compile_options(x09mem_host PRIVATE -O2)
target_link_libraries(x09mem_host PRIVATE runtime::etrt deviceLayer::deviceLayer)
