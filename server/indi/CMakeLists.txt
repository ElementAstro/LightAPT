cmake_minimum_required(VERSION 3.13)
project(indiserver CXX)

set(CMAKE_INCLUDE_CURRENT_DIR ON)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++17 -Os")

INCLUDE(CheckSymbolExists)

LIST(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake_modules/")
LIST(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/../cmake_modules/")

if(WIN32 OR ANDROID)
    message(WARNING "INDI Server is only supported under Linux, BSD, MacOS, and Cygwin while current system is " ${CMAKE_SYSTEM_NAME})
else()
    find_package(Threads REQUIRED)
    find_package(Libev REQUIRED)
    find_package(Nova REQUIRED)

    add_subdirectory(core)

    add_executable(${PROJECT_NAME} indiserver.cpp)

    find_package(Boost 1.54.0 COMPONENTS system thread coroutine context REQUIRED)

    target_link_libraries(${PROJECT_NAME} ${Boost_LIBRARIES})
    find_package(OpenSSL REQUIRED)
    target_link_libraries(${PROJECT_NAME} ${OPENSSL_LIBRARIES})

    target_link_libraries(indiserver indicore ${CMAKE_THREAD_LIBS_INIT} ${LIBEV_LIBRARIES})
    target_include_directories(indiserver SYSTEM PRIVATE ${LIBEV_INCLUDE_DIRS})

    install(TARGETS indiserver RUNTIME DESTINATION bin)
endif(WIN32 OR ANDROID)