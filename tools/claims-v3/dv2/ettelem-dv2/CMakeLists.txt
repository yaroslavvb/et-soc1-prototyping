# ettelem-dv2: tools/claims-v3/hp/ettelem-hp/ettelem.cpp (ettelem with the loglevel fix) plus the DV2 reads
# (residency, uptime, threshold get) and the sampler's one-shot statistics reset (--reset-once-file). Build into its own
# directory, never into build/ettelem or build/ettelem-hp:
#   cmake -S tools/claims-v3/dv2/ettelem-dv2 -B build/ettelem-dv2 -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && nice cmake --build build/ettelem-dv2 -j4
cmake_minimum_required(VERSION 3.17)
project(ettelem_dv2 LANGUAGES CXX)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_PREFIX_PATH}/lib/cmake")
find_package(deviceLayer REQUIRED)
find_package(deviceManagement REQUIRED)
add_executable(ettelem ettelem.cpp)
target_compile_features(ettelem PRIVATE cxx_std_17)
target_link_libraries(ettelem PRIVATE deviceLayer::deviceLayer deviceManagement::DM dl)
