cmake_minimum_required(VERSION 3.16)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

project(mapf-refine CXX)

add_subdirectory(./mapf)

add_executable(app app.cpp)
target_compile_features(app PUBLIC cxx_std_17)
target_link_libraries(app lib-mapf)

# format
add_custom_target(clang-format
  COMMAND clang-format -i
  ../mapf/include/*.hpp
  ../mapf/src/*.cpp
  ../tests/*.cpp
  ../app.cpp)

