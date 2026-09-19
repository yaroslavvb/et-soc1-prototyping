# Host-side launchers.  Builds against the et-platform install (/opt/et) and
# reuses gp-sdk's GenericLauncher (target etsoc_gpsdk).
cmake_minimum_required(VERSION 3.16)
project(nekko-launchers LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(GP_SDK_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../external/et-platform/gp-sdk" CACHE PATH "gp-sdk source dir")
set(KERNELS_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../kernels")

set(BUILD_TESTS OFF CACHE BOOL "" FORCE)  # skip gp-sdk's own example launchers
add_subdirectory(${GP_SDK_DIR}/host gp-sdk-host EXCLUDE_FROM_ALL)

function(add_launcher NAME)
  add_executable(${NAME} ${ARGN})
  target_include_directories(${NAME} PRIVATE ${KERNELS_DIR} ${GP_SDK_DIR}/host/sdk/include)
  target_link_libraries(${NAME} PRIVATE etsoc_gpsdk)
endfunction()

add_launcher(hello_launcher hello/hello.cpp)
add_launcher(mmbench_launcher mmbench/mmbench.cpp)

# Device-trace decoder (et_printf output); header-only et-trace, no runtime deps.
find_package(esperantoTrace REQUIRED)
add_executable(trace_dump tools/trace_dump.cpp)
target_link_libraries(trace_dump PRIVATE esperantoTrace::et_trace)
