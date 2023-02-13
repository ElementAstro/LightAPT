#############################################
# wxWidgets
# The usage is a bit different on all the platforms. For having version >= 3.0, a version of cmake >= 3.0 should be used on Windows (on Linux/OSX it works properly this way).
if(WIN32)
  # wxWidgets
  set(wxWidgets_CONFIGURATION msw)

  if(NOT wxWidgets_PREFIX_DIRECTORY OR NOT EXISTS ${wxWidgets_PREFIX_DIRECTORY})
    message(FATAL_ERROR "The variable wxWidgets_PREFIX_DIRECTORY should be defined and should point to a valid wxWindows installation path. See the open-phd-guiding wiki for more information.")
  endif()

  set(wxWidgets_ROOT_DIR ${wxWidgets_PREFIX_DIRECTORY})
  set(wxWidgets_USE_STATIC ON)
  set(wxWidgets_USE_DEBUG ON)
  set(wxWidgets_USE_UNICODE OFF)
  find_package(wxWidgets REQUIRED COMPONENTS propgrid base core aui adv html net)
  include(${wxWidgets_USE_FILE})
  #message(${wxWidgets_USE_FILE})

elseif(${CMAKE_SYSTEM_NAME} MATCHES "FreeBSD")
  if(NOT DEFINED wxWidgets_PREFIX_DIRECTORY)
    set(wxWidgets_PREFIX_DIRECTORY "/usr/local")
  endif()
  set(wxWidgets_CONFIG_OPTIONS --prefix=${wxWidgets_PREFIX_DIRECTORY})

  find_program(wxWidgets_CONFIG_EXECUTABLE
    NAMES "wxgtk3u-3.1-config"
    PATHS ${wxWidgets_PREFIX_DIRECTORY}/bin NO_DEFAULT_PATH)
  if(NOT wxWidgets_CONFIG_EXECUTABLE)
    message(FATAL_ERROR "Cannot find wxWidgets_CONFIG_EXECUTABLE from the given directory ${wxWidgets_PREFIX_DIRECTORY}")
  endif()

  set(wxRequiredLibs aui core base adv html net)
  execute_process(COMMAND ${wxWidgets_CONFIG_EXECUTABLE} --libs ${wxRequiredLibs}
	  OUTPUT_VARIABLE wxWidgets_LIBRARIES
	  OUTPUT_STRIP_TRAILING_WHITESPACE)
  separate_arguments(${wxWidgets_LIBRARIES})
  execute_process(COMMAND ${wxWidgets_CONFIG_EXECUTABLE} --cflags ${wxRwxRequiredLibs}
	  OUTPUT_VARIABLE wxWidgets_CXXFLAGS
	  OUTPUT_STRIP_TRAILING_WHITESPACE)
  separate_arguments(wxWidgets_CXX_FLAGS UNIX_COMMAND "${wxWidgets_CXXFLAGS}")
  separate_arguments(wxWidgets_LDFLAGS UNIX_COMMAND "${wxWidgets_LDFLAGS}")
else()
  if(wxWidgets_PREFIX_DIRECTORY)
    set(wxWidgets_CONFIG_OPTIONS --prefix=${wxWidgets_PREFIX_DIRECTORY})

    find_program(wxWidgets_CONFIG_EXECUTABLE NAMES "wx-config" PATHS ${wxWidgets_PREFIX_DIRECTORY}/bin NO_DEFAULT_PATH)
    if(NOT wxWidgets_CONFIG_EXECUTABLE)
      message(FATAL_ERROR "Cannot find wxWidgets_CONFIG_EXECUTABLE from the given directory ${wxWidgets_PREFIX_DIRECTORY}")
    endif()
  endif()

  find_package(wxWidgets REQUIRED COMPONENTS aui core base adv html net)
  if(NOT wxWidgets_FOUND)
    message(FATAL_ERROR "WxWidget cannot be found. Please use wx-config prefix")
  endif()
  #if(APPLE)
  #  set(PHD_LINK_EXTERNAL ${PHD_LINK_EXTERNAL} wx_osx_cocoau_aui-3.0)
  #endif()
  #message("wxLibraries ${wxWidgets_LIBRARIES}")
endif()

set(PHD_LINK_EXTERNAL ${PHD_LINK_EXTERNAL} ${wxWidgets_LIBRARIES})
