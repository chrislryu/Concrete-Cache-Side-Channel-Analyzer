cmake_minimum_required(VERSION 3.4)
project(aes)
set(SOURCE_FILES aes.cpp)
set(OPENSSL_USE_STATIC_LIBS TRUE)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3")
find_package(OpenSSL REQUIRED)
add_executable(${PROJECT_NAME} ${SOURCE_FILES})
target_link_libraries(${PROJECT_NAME} OpenSSL::Crypto)