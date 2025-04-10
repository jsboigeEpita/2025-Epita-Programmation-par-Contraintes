cmake_minimum_required(VERSION 3.16)
project(graph CXX)

add_subdirectory(./graph)
add_subdirectory(./third_party/googletest)

# format
add_custom_target(clang-format
  COMMAND clang-format -i
  ../graph/include/*.hpp
  ../graph/src/*.cpp
  ../tests/*.cpp)
