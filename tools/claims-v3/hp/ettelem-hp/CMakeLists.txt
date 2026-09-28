# ettelem-hp: tools/ettelem/ettelem.cpp with the loglevel fix (see ettelem.cpp's header). Build into its own directory:
#   cmake -S tools/claims-v3/hp/ettelem-hp -B build/ettelem-hp -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && nice cmake --build build/ettelem-hp -j4
# (never into build/ettelem, which the V3 blocks use)
cmake_minimum_required(VERSION 3.17)
project(ettelem_hp LANGUAGES CXX)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_PREFIX_PATH}/lib/cmake")
find_package(deviceLayer REQUIRED)
find_package(deviceManagement REQUIRED)
add_executable(ettelem ettelem.cpp)
target_compile_features(ettelem PRIVATE cxx_std_17)
target_link_libraries(ettelem PRIVATE deviceLayer::deviceLayer deviceManagement::DM dl)
