# coding=utf-8

"""

Copyright(c) 2022-2023 Max Qian  <lightapt.com>

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Library General Public
License version 3 as published by the Free Software Foundation.
This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Library General Public License for more details.
You should have received a copy of the GNU Library General Public License
along with this library; see the file COPYING.LIB.  If not, write to
the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
Boston, MA 02110-1301, USA.

"""

from server.basic.camera import BasicCameraAPI,BasicCameraInfo

from utils.utility import switch
from utils.i18n import _
from ...logging import logger,return_error,return_success,return_warning

import ctypes
import numpy as np
import astropy.io.fits as fits
from base64 import b64encode
from datetime import datetime
from io import BytesIO
from json import dumps,JSONDecodeError
from os import mkdir,path,environ,getcwd
from time import sleep

class ASI_BAYER_PATTERN:
    ASI_BAYER_RG = 0
    ASI_BAYER_BG = 1
    ASI_BAYER_GR = 2
    ASI_BAYER_RB = 3

class ASI_IMGTYPE:
    ASI_IMG_RAW8 = 0
    ASI_IMG_RGB24 = 1
    ASI_IMG_RAW16 = 2
    ASI_IMG_Y8 = 3
    ASI_IMG_END = -1

class ASI_GUIDE_DIRECTION:
    ASI_GUIDE_NORTH = 0
    ASI_GUIDE_SOUTH = 1
    ASI_GUIDE_EAST = 2
    ASI_GUIDE_WEST = 3

class ASI_CONTROL_TYPE:
    ASI_GAIN = 0
    ASI_EXPOSURE = 1
    ASI_GAMMA = 2
    ASI_WB_R = 3
    ASI_WB_B = 4
    ASI_BRIGHTNESS = 5
    ASI_OFFSET = 5
    ASI_BANDWIDTHOVERLOAD = 6
    ASI_OVERCLOCK = 7
    ASI_TEMPERATURE = 8  # return 10*temperature
    ASI_FLIP = 9
    ASI_AUTO_MAX_GAIN = 10
    ASI_AUTO_MAX_EXP = 11
    ASI_AUTO_MAX_BRIGHTNESS = 12
    ASI_HARDWARE_BIN = 13
    ASI_HIGH_SPEED_MODE = 14
    ASI_COOLER_POWER_PERC = 15
    ASI_TARGET_TEMP = 16  # not need *10
    ASI_COOLER_ON = 17
    ASI_MONO_BIN = 18  # lead to less grid at software bin mode for color camera
    ASI_FAN_ON = 19
    ASI_PATTERN_ADJUST = 20

class ASI_CAMERA_MODE:
    ASI_MODE_NORMAL = 0 
    ASI_MODE_TRIG_SOFT_EDGE = 1
    ASI_MODE_TRIG_RISE_EDGE = 2
    ASI_MODE_TRIG_FALL_EDGE = 3
    ASI_MODE_TRIG_SOFT_LEVEL = 4
    ASI_MODE_TRIG_HIGH_LEVEL = 5
    ASI_MODE_TRIG_LOW_LEVEL = 6
    ASI_MODE_END = -1

class ASI_TRIG_OUTPUT:
    ASI_TRIG_OUTPUT_PINA = 0
    ASI_TRIG_OUTPUT_PINB = 1
    ASI_TRIG_OUTPUT_NONE = -1

class ASI_EXPOSURE_STATUS:
    ASI_EXP_IDLE = 0
    ASI_EXP_WORKING = 1
    ASI_EXP_SUCCESS = 2
    ASI_EXP_FAILED = 3

class _ASI_CAMERA_INFO(ctypes.Structure):
    """ASI camera info"""
    _fields_ = [
        ('Name', ctypes.c_char * 64),
        ('CameraID', ctypes.c_int),
        ('MaxHeight', ctypes.c_long),
        ('MaxWidth', ctypes.c_long),
        ('IsColorCam', ctypes.c_int),
        ('BayerPattern', ctypes.c_int),
        ('SupportedBins', ctypes.c_int * 16),
        ('SupportedVideoFormat', ctypes.c_int * 8),
        ('PixelSize', ctypes.c_double),  # in um
        ('MechanicalShutter', ctypes.c_int),
        ('ST4Port', ctypes.c_int),
        ('IsCoolerCam', ctypes.c_int),
        ('IsUSB3Host', ctypes.c_int),
        ('IsUSB3Camera', ctypes.c_int),
        ('ElecPerADU', ctypes.c_float),
        ('BitDepth', ctypes.c_int),
        ('IsTriggerCam', ctypes.c_int),

        ('Unused', ctypes.c_char * 16)
    ]

class _ASI_CONTROL_CAPS(ctypes.Structure):
    _fields_ = [
        ('Name', ctypes.c_char * 64),
        ('Description', ctypes.c_char * 128),
        ('MaxValue', ctypes.c_long),
        ('MinValue', ctypes.c_long),
        ('DefaultValue', ctypes.c_long),
        ('IsAutoSupported', ctypes.c_int),
        ('IsWritable', ctypes.c_int),
        ('ControlType', ctypes.c_int),
        ('Unused', ctypes.c_char * 32),
        ]

class _ASI_ID(ctypes.Structure):
    _fields_ = [('id', ctypes.c_char * 8)]

class _ASI_SUPPORTED_MODE(ctypes.Structure):
    _fields_ = [('SupportedCameraMode', ctypes.c_int * 16)]

class ASICameraAPI(BasicCameraAPI):
    """
        ASI Camera API via ASICamera2.dll/so
    """

    def __init__(self) -> None:
        self.info = BasicCameraInfo()
        self.device = None
        self.info._is_connected = False
        self.info._percent_complete = 0

    def __del__(self) -> None:
        if self.info._is_connected:
            self.disconnect()

    def init_dll(self) -> None:
        """
            Initialize the dll library | 加载dll
            Args: None
            Returns: None
        """

        if self.device is not None:
            return
        _p = path.join
        libpath = _p(getcwd(),"libs","zwoasi")
        # 判断系统位数 - 32/64
        if 'PROGRAMFILES(X86)' in environ:
            libpath = _p(libpath,"x64","ASICamera2.dll")
        # Load dymical libraries
        self.device = ctypes.cdll.LoadLibrary(libpath)

        self.device.ASIGetNumOfConnectedCameras.argtypes = []
        self.device.ASIGetNumOfConnectedCameras.restype = ctypes.c_int

        self.device.ASIGetCameraProperty.argtypes = [ctypes.POINTER(_ASI_CAMERA_INFO), ctypes.c_int]
        self.device.ASIGetCameraProperty.restype = ctypes.c_int

        self.device.ASIOpenCamera.argtypes = [ctypes.c_int]
        self.device.ASIOpenCamera.restype = ctypes.c_int

        self.device.ASIInitCamera.argtypes = [ctypes.c_int]
        self.device.ASIInitCamera.restype = ctypes.c_int

        self.device.ASICloseCamera.argtypes = [ctypes.c_int]
        self.device.ASICloseCamera.restype = ctypes.c_int

        self.device.ASIGetNumOfControls.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        self.device.ASIGetNumOfControls.restype = ctypes.c_int

        self.device.ASIGetControlCaps.argtypes = [ctypes.c_int, ctypes.c_int,
                                            ctypes.POINTER(_ASI_CONTROL_CAPS)]
        self.device.ASIGetControlCaps.restype = ctypes.c_int

        self.device.ASIGetControlValue.argtypes = [ctypes.c_int,
                                            ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_long),
                                            ctypes.POINTER(ctypes.c_int)]
        self.device.ASIGetControlValue.restype = ctypes.c_int

        self.device.ASISetControlValue.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_long, ctypes.c_int]
        self.device.ASISetControlValue.restype = ctypes.c_int

        self.device.ASIGetROIFormat.argtypes = [ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_int),
                                        ctypes.POINTER(ctypes.c_int),
                                        ctypes.POINTER(ctypes.c_int),
                                        ctypes.POINTER(ctypes.c_int)]
        self.device.ASIGetROIFormat.restype = ctypes.c_int

        self.device.ASISetROIFormat.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.device.ASISetROIFormat.restype = ctypes.c_int

        self.device.ASIGetStartPos.argtypes = [ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_int),
                                        ctypes.POINTER(ctypes.c_int)]
        self.device.ASIGetStartPos.restype = ctypes.c_int

        self.device.ASISetStartPos.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.device.ASISetStartPos.restype = ctypes.c_int

        self.device.ASIGetDroppedFrames.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        self.device.ASIGetDroppedFrames.restype = ctypes.c_int

        self.device.ASIEnableDarkSubtract.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_char)]
        self.device.ASIEnableDarkSubtract.restype = ctypes.c_int

        self.device.ASIDisableDarkSubtract.argtypes = [ctypes.c_int]
        self.device.ASIDisableDarkSubtract.restype = ctypes.c_int

        self.device.ASIStartVideoCapture.argtypes = [ctypes.c_int]
        self.device.ASIStartVideoCapture.restype = ctypes.c_int

        self.device.ASIStopVideoCapture.argtypes = [ctypes.c_int]
        self.device.ASIStopVideoCapture.restype = ctypes.c_int

        self.device.ASIGetVideoData.argtypes = [ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_char),
                                        ctypes.c_long,
                                        ctypes.c_int]
        self.device.ASIGetVideoData.restype = ctypes.c_int

        self.device.ASIPulseGuideOn.argtypes = [ctypes.c_int, ctypes.c_int]
        self.device.ASIPulseGuideOn.restype = ctypes.c_int

        self.device.ASIPulseGuideOff.argtypes = [ctypes.c_int, ctypes.c_int]
        self.device.ASIPulseGuideOff.restype = ctypes.c_int

        self.device.ASIStartExposure.argtypes = [ctypes.c_int, ctypes.c_int]
        self.device.ASIStartExposure.restype = ctypes.c_int

        self.device.ASIStopExposure.argtypes = [ctypes.c_int]
        self.device.ASIStopExposure.restype = ctypes.c_int

        self.device.ASIGetExpStatus.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        self.device.ASIGetExpStatus.restype = ctypes.c_int

        self.device.ASIGetDataAfterExp.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_char), ctypes.c_long]
        self.device.ASIGetDataAfterExp.restype = ctypes.c_int

        self.device.ASIGetID.argtypes = [ctypes.c_int, ctypes.POINTER(_ASI_ID)]
        self.device.ASIGetID.restype = ctypes.c_int

        self.device.ASISetID.argtypes = [ctypes.c_int, _ASI_ID]
        self.device.ASISetID.restype = ctypes.c_int


        self.device.ASIGetGainOffset.argtypes = [ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_int)]
        self.device.ASIGetGainOffset.restype = ctypes.c_int

        self.device.ASISetCameraMode.argtypes = [ctypes.c_int, ctypes.c_int]
        self.device.ASISetCameraMode.restype = ctypes.c_int

        self.device.ASIGetCameraMode.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        self.device.ASIGetCameraMode.restype = ctypes.c_int

        self.device.ASIGetCameraSupportMode.argtypes = [ctypes.c_int, ctypes.POINTER(_ASI_SUPPORTED_MODE)]
        self.device.ASIGetCameraSupportMode.restype = ctypes.c_int

        self.device.ASISendSoftTrigger.argtypes = [ctypes.c_int, ctypes.c_int]
        self.device.ASISendSoftTrigger.restype = ctypes.c_int

        self.device.ASISetTriggerOutputIOConf.argtypes = [ctypes.c_int,
                                                    ctypes.c_int,
                                                    ctypes.c_int,
                                                    ctypes.c_long,
                                                    ctypes.c_long]
        self.device.ASISetTriggerOutputIOConf.restype = ctypes.c_int

        self.device.ASIGetTriggerOutputIOConf.argtypes = [ctypes.c_int,
                                                    ctypes.c_int,
                                                    ctypes.POINTER(ctypes.c_int),
                                                    ctypes.POINTER(ctypes.c_long),
                                                    ctypes.POINTER(ctypes.c_long)]
        self.device.ASIGetTriggerOutputIOConf.restype = ctypes.c_int

        self.device.ASIGetSDKVersion.restype = ctypes.c_char_p