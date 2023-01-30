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

from os import getcwd, path
from platform import uname
from server.basic.camera import BasicCameraAPI,BasicCameraInfo

from utils.utility import switch
from utils.i18n import _
from ...logging import logger,return_error,return_success,return_warning

import ctypes

class CONTROL_ID:
    CONTROL_BRIGHTNESS = ctypes.c_short(0) # image brightness
    CONTROL_CONTRAST = ctypes.c_short(1)   # image contrast
    CONTROL_WBR  = ctypes.c_short(2)       # red of white balance
    CONTROL_WBB = ctypes.c_short(3)        # blue of white balance
    CONTROL_WBG = ctypes.c_short(4)        # the green of white balance
    CONTROL_GAMMA = ctypes.c_short(5)      # screen gamma
    CONTROL_GAIN = ctypes.c_short(6)       # camera gain
    CONTROL_OFFSET = ctypes.c_short(7)     # camera offset
    CONTROL_EXPOSURE = ctypes.c_short(8)   # expose time (us)
    CONTROL_SPEED = ctypes.c_short(9)      # transfer speed
    CONTROL_TRANSFERBIT = ctypes.c_short(10)  # image depth bits
    CONTROL_CHANNELS = ctypes.c_short(11)     # image channels
    CONTROL_USBTRAFFIC = ctypes.c_short(12)   # hblank
    CONTROL_ROWNOISERE = ctypes.c_short(13)   # row denoise
    CONTROL_CURTEMP = ctypes.c_short(14)      # current cmos or ccd temprature
    CONTROL_CURPWM = ctypes.c_short(15)       # current cool pwm
    CONTROL_MANULPWM = ctypes.c_short(16)     # set the cool pwm
    CONTROL_CFWPORT = ctypes.c_short(17)      # control camera color filter wheel port
    CONTROL_COOLER = ctypes.c_short(18)       # check if camera has cooler
    CONTROL_ST4PORT = ctypes.c_short(19)      # check if camera has st4port
    CAM_COLOR = ctypes.c_short(20)
    CAM_BIN1X1MODE = ctypes.c_short(21)       # check if camera has bin1x1 mode
    CAM_BIN2X2MODE = ctypes.c_short(22)       # check if camera has bin2x2 mode
    CAM_BIN3X3MODE = ctypes.c_short(23)       # check if camera has bin3x3 mode
    CAM_BIN4X4MODE = ctypes.c_short(24)       # check if camera has bin4x4 mode
    CAM_MECHANICALSHUTTER = ctypes.c_short(25)# mechanical shutter
    CAM_TRIGER_INTERFACE = ctypes.c_short(26) # triger
    CAM_TECOVERPROTECT_INTERFACE = ctypes.c_short(27)  # tec overprotect
    CAM_SINGNALCLAMP_INTERFACE = ctypes.c_short(28)    # singnal clamp
    CAM_FINETONE_INTERFACE = ctypes.c_short(29)        # fine tone
    CAM_SHUTTERMOTORHEATING_INTERFACE = ctypes.c_short(30)  # shutter motor heating
    CAM_CALIBRATEFPN_INTERFACE = ctypes.c_short(31)         # calibrated frame
    CAM_CHIPTEMPERATURESENSOR_INTERFACE = ctypes.c_short(32)# chip temperaure sensor
    CAM_USBREADOUTSLOWEST_INTERFACE = ctypes.c_short(33)    # usb readout slowest

    CAM_8BITS = ctypes.c_short(34)                          # 8bit depth
    CAM_16BITS = ctypes.c_short(35)                         # 16bit depth
    CAM_GPS = ctypes.c_short(36)                            # check if camera has gps

    CAM_IGNOREOVERSCAN_INTERFACE = ctypes.c_short(37)       # ignore overscan area

    QHYCCD_3A_AUTOBALANCE = ctypes.c_short(38)
    QHYCCD_3A_AUTOEXPOSURE = ctypes.c_short(39)
    QHYCCD_3A_AUTOFOCUS = ctypes.c_short(40)
    CONTROL_AMPV = ctypes.c_short(41)                       # ccd or cmos ampv
    CONTROL_VCAM = ctypes.c_short(42)                       # Virtual Camera on off
    CAM_VIEW_MODE = ctypes.c_short(43)

    CONTROL_CFWSLOTSNUM = ctypes.c_short(44)         # check CFW slots number
    IS_EXPOSING_DONE = ctypes.c_short(45)
    ScreenStretchB = ctypes.c_short(46)
    ScreenStretchW = ctypes.c_short(47)
    CONTROL_DDR = ctypes.c_short(48)
    CAM_LIGHT_PERFORMANCE_MODE = ctypes.c_short(49)

    CAM_QHY5II_GUIDE_MODE = ctypes.c_short(50)
    DDR_BUFFER_CAPACITY = ctypes.c_short(51)
    DDR_BUFFER_READ_THRESHOLD = ctypes.c_short(52)
    DefaultGain = ctypes.c_short(53)
    DefaultOffset = ctypes.c_short(54)
    OutputDataActualBits = ctypes.c_short(55)
    OutputDataAlignment = ctypes.c_short(56)

    CAM_SINGLEFRAMEMODE = ctypes.c_short(57)
    CAM_LIVEVIDEOMODE = ctypes.c_short(58)
    CAM_IS_COLOR = ctypes.c_short(59)
    hasHardwareFrameCounter = ctypes.c_short(60)
    CONTROL_MAX_ID = ctypes.c_short(71)
    CAM_HUMIDITY = ctypes.c_short(72)
    #check if camera has	 humidity sensor 

class QHYERR:
    QHYCCD_READ_DIRECTLY = 0x2001
    QHYCCD_DELAY_200MS   = 0x2000
    QHYCCD_SUCCESS       = 0
    QHYCCD_ERROR         = 0xFFFFFFFF


class QHYCameraAPI(BasicCameraAPI):
    """
        QHY Camera API Interface
    """

    def __init__(self) -> None:
        self.info = BasicCameraInfo()
        self.device = None

    def __del__(self) -> None:
        if self.info._is_connected:
            self.disconnect()

    def __str__(self) -> str:
        return "LightAPT QHY Camera API Interface"

    def init_dll(self) -> None:
        """
            Initialize the dll library | 加载dll
            Args: None
            Returns: None
        """
        if self.device is not None:
            return
        _p = path.join
        libpath = path.join(getcwd(),"server","api","driver")
        # 判断系统位数 - 32/64
        if uname().system == 'Windows':
            libpath = path.join(libpath,"windows","qhyccd.dll")
        elif uname().system == 'Linux':
            if uname().machine == 'x86_64':
                libpath = path.join(libpath,"x64","libqhyccd.so")

        self.device = ctypes.CDLL(libpath)

        self.device.GetQHYCCDParam.restype = ctypes.c_double
        self.device.OpenQHYCCD.restype = ctypes.POINTER(ctypes.c_uint32)

    def connect(self, params = {}) -> dict:
        """
            Connect to the specified QHY camera via ASISDK
            Args :
                params : dict
                    name : str # name of the ASI camera
            Returns : dict
                info : dict # BasicCameraInfo object
        """
        if self.device is not None and  self.info._is_connected:
            return return_error(_("Camera is already connected"),{"info" : self.info.get_dict()})

        name = params.get('name')
        if name is None or not isinstance(name,str):
            return return_error(_("Invalid camera name is provided"),{})

        

