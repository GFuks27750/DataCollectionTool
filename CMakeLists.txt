cmake_minimum_required(VERSION 3.14)

project(dataCollectionTool)

find_package(OpenCV REQUIRED)

add_executable(dataCollectionTool main.cpp)
target_include_directories(dataCollectionTool PRIVATE ${OpenCV_INCLUDE_DIRS})
target_link_libraries(dataCollectionTool ${OpenCV_LIBS})