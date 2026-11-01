# ettelem-e77: E77's no-PMIC-read telemetry (ettelem.cpp's header lists every request it can send). Build into its own
# directory, never over build/ettelem, build/ettelem-hpl or build/ettelem-dv2:
#   cmake -S tools/claims-v3/e77/ettelem-e77 -B build/ettelem-e77 -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && nice cmake --build build/ettelem-e77 -j2
cmake_minimum_required(VERSION 3.17)
project(ettelem_e77 LANGUAGES CXX)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_PREFIX_PATH}/lib/cmake")
find_package(deviceLayer REQUIRED)
find_package(deviceManagement REQUIRED)
add_executable(ettelem ettelem.cpp)
target_compile_features(ettelem PRIVATE cxx_std_17)
target_link_libraries(ettelem PRIVATE deviceLayer::deviceLayer deviceManagement::DM dl)
