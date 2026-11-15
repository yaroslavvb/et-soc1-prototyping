# Host program (card only): the runtime and the PCIe device layer.
find_package(runtime REQUIRED)
find_package(deviceLayer REQUIRED)

set(KERNEL_ELF "${CMAKE_BINARY_DIR}/kernel/x04clock.elf")
configure_file(Constants.h.in ${CMAKE_CURRENT_BINARY_DIR}/Constants.h)

add_executable(x04clock_host main.cpp)
target_include_directories(x04clock_host PRIVATE ${CMAKE_CURRENT_BINARY_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/..)
target_compile_features(x04clock_host PRIVATE cxx_std_17)
target_compile_options(x04clock_host PRIVATE -O2)
target_link_libraries(x04clock_host PRIVATE runtime::etrt deviceLayer::deviceLayer)
