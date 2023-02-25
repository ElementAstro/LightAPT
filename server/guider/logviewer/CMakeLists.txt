#
#  This file is part of guiderlogview
# 
#  Copyright (C) 2016 Andy Galasso
# 
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License along
#  with this program; if not, visit the http://fsf.org website.

cmake_minimum_required (VERSION 3.10)

# this must appear very early in the file
if (WIN32)
  set(CMAKE_GENERATOR_TOOLSET "v120_xp" CACHE STRING "Platform Toolset" FORCE)
endif()

if(COMMAND cmake_policy)
  cmake_policy(SET CMP0003 NEW)
  if (POLICY CMP0043)
    cmake_policy(SET CMP0043 NEW)
  endif()
endif(COMMAND cmake_policy)

if(APPLE)
  set(APPLE_ARCH "x86_64" CACHE STRING "Apple architecture: i386 or x86_64")
  if(APPLE_ARCH MATCHES "^i386")
    message(STATUS "configuring to build a 32-bit guiderlogview")
    set(APPLE32 1)
  elseif(APPLE_ARCH MATCHES "^x86_64")
    message(STATUS "configuring to build a 64-bit guiderlogview")
    SET(APPLE32 0)
  else()
    message(FATAL_ERROR "APPLE_ARCH must be i386 or x86_64")
  endif()
  if(APPLE32)
    set(CMAKE_OSX_DEPLOYMENT_TARGET "10.7" CACHE STRING "Minimum OSX deployment version")
    set(CMAKE_OSX_ARCHITECTURES i386 CACHE STRING "build architecture for OSX" FORCE)
  else()
    set(CMAKE_OSX_DEPLOYMENT_TARGET "10.14" CACHE STRING "Minimum OSX deployment version")
  endif()
  set(CMAKE_XCODE_ATTRIBUTE_CLANG_CXX_LIBRARY "libc++")
  set(CMAKE_CXX_STANDARD 11)
endif()

project (guiderlogview)

set(srcdir ${CMAKE_SOURCE_DIR})

include_directories(${CMAKE_BINARY_DIR})
#include_directories(${srcdir})

add_definitions(-D_USE_MATH_DEFINES)

if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  message(STATUS "Setting build type to 'Release' as none was specified.")
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build." FORCE)
  # Set the possible values of build type for cmake-gui
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release"
"MinSizeRel" "RelWithDebInfo")
endif()

include(CheckCXXCompilerFlag)

#################################################################################
#

check_cxx_compiler_flag(-std=c++11 HAS_CXX11_FLAG)
check_cxx_compiler_flag(-std=c++0x HAS_CXX0X_FLAG)

if(HAS_CXX11_FLAG)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
elseif(HAS_CXX0X_FLAG)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x")
endif()

if(wxWidgets_PREFIX_DIRECTORY)
    set(wxWidgets_CONFIG_OPTIONS --prefix=${wxWidgets_PREFIX_DIRECTORY})

    find_program(wxWidgets_CONFIG_EXECUTABLE NAMES "wx-config" PATHS
${wxWidgets_PREFIX_DIRECTORY}/bin NO_DEFAULT_PATH)
    if(NOT wxWidgets_CONFIG_EXECUTABLE)
      message(FATAL_ERROR "Cannot find wxWidgets_CONFIG_EXECUTABLE from the
given directory ${wxWidgets_PREFIX_DIRECTORY}")
    endif()
  endif()

  find_package(wxWidgets REQUIRED COMPONENTS aui core base adv html net)
  if(NOT wxWidgets_FOUND)
    message(FATAL_ERROR "WxWidget cannot be found. Please use wx-config
prefix")
endif()

set(APP_LINK_EXTERNAL ${APP_LINK_EXTERNAL} ${wxWidgets_LIBRARIES})

set(SRC
  ${srcdir}/server/guider/logviewer/AnalysisWin.cpp
  ${srcdir}/server/guider/logviewer/AnalysisWin.h
  ${srcdir}/server/guider/logviewer/LogViewApp.cpp
  ${srcdir}/server/guider/logviewer/LogViewApp.h
  ${srcdir}/server/guider/logviewer/LogViewFrame.cpp
  ${srcdir}/server/guider/logviewer/LogViewFrame.h
  ${srcdir}/server/guider/logviewer/logparser.cpp
  ${srcdir}/server/guider/logviewer/logparser.h
  ${srcdir}/server/guider/logviewer/guiderlogview.ico
  ${srcdir}/server/guider/logviewer/guiderlogview.rc
  ${srcdir}/server/guider/logviewer/small.ico
)

set (FBSRC
  ${CMAKE_CURRENT_BINARY_DIR}/server/guider/logviewer/LogViewFrameBase.cpp
  ${CMAKE_CURRENT_BINARY_DIR}/server/guider/logviewer/LogViewFrameBase.h
)
set (ALL_SRC
  ${SRC}
  ${FBSRC}
)

if(WIN32)
  add_executable(guiderlogview WIN32 ${ALL_SRC})
elseif(APPLE)
  add_executable(guiderlogview MACOSX_BUNDLE ${ALL_SRC})
elseif(UNIX)
  add_executable(guiderlogview ${ALL_SRC})
endif()

# ===== GSL =====
if(WIN32)
  set(gsl_ver "2.4.0.8788")
  set(gsl_dir ${CMAKE_BINARY_DIR}/gsl-msvc-x86.${gsl_ver})
  if(NOT EXISTS ${gsl_dir})
    execute_process(
      COMMAND ${CMAKE_COMMAND} -E tar xf ${CMAKE_SOURCE_DIR}/3rdparty/gsl-msvc-x86.${gsl_ver}.zip --format=zip
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR})
  endif()
  add_definitions(-DGSL_DLL)
  include_directories(${gsl_dir}/build/native)
#  set(gsl_lib_dir ${gsl_dir}/build/native/dll/Win32/${CMAKE_BUILD_TYPE})  # requies vcruntime140d.dll
  set(gsl_lib_dir ${gsl_dir}/build/native/dll/Win32/Release)
  set(APP_LINK_EXTERNAL ${APP_LINK_EXTERNAL} ${gsl_lib_dir}/gsl.lib)
  add_custom_command(TARGET guiderlogview POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
      "${gsl_lib_dir}/gsl.dll"
      "${gsl_lib_dir}/cblas.dll"
      "${CMAKE_SOURCE_DIR}/3rdparty/msvcp120.dll"
      "${CMAKE_SOURCE_DIR}/3rdparty/msvcr120.dll"
      "${CMAKE_SOURCE_DIR}/3rdparty/vcruntime140.dll"
      $<TARGET_FILE_DIR:guiderlogview>)
else()
  find_package(GSL REQUIRED)
  if(APPLE)
    # force static loining on OSX to avoid redistributing GSL .dylib files
    # this is a hack... what's the real way to do this in CMake?
    string(REPLACE ".dylib" ".a" GSL_LIBRARIES "${GSL_LIBRARIES}")
    set(APP_LINK_EXTERNAL ${APP_LINK_EXTERNAL} ${GSL_LIBRARIES})
    include_directories(${GSL_INCLUDE_DIR})
  else()
    target_link_libraries(guiderlogview GSL::gsl GSL::gslcblas)
  endif()
endif()

target_compile_definitions( guiderlogview PRIVATE "${wxWidgets_DEFINITIONS}" "HAVE_TYPE_TRAITS")
target_compile_options(     guiderlogview PRIVATE "${wxWidgets_CXX_FLAGS};")
target_link_libraries(guiderlogview ${APP_LINK_EXTERNAL})
target_include_directories(guiderlogview PRIVATE ${wxWidgets_INCLUDE_DIRS})

if(UNIX AND NOT APPLE)
  install(TARGETS guiderlogview
          RUNTIME DESTINATION bin)
  install(FILES ${CMAKE_SOURCE_DIR}/guiderlogview.png
          DESTINATION ${CMAKE_INSTALL_PREFIX}/share/pixmaps/ )
  install(FILES ${CMAKE_SOURCE_DIR}/guiderlogview.desktop
          DESTINATION ${CMAKE_INSTALL_PREFIX}/share/applications/ )
endif()
