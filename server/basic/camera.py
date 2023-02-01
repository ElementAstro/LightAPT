# coding=utf-8

"""

Copyright(c) 2022 Max Qian  <astroair.cn>

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

from .device import BasicDeviceAPI

class BasicCameraInfo(object):
    """
        Basic camera information container
    """

    _type = "" # type of the camera , must be given
    _name : str # name of the camera
    _id : int # id of the camera
    _description : str
    _timeout = 5
    _configration = "" # path to the configuration file

    _exposure = 0
    _gain = 0
    _offset = 0
    _iso = 0
    _binning = [1,1]
    _temperature = -256
    _cool_power = 0
    _last_exposure = 0
    _percent_complete = 0

    _image_id = 0
    _image_path = ""
    _image_type = ""
    _image_name_format = ""

    _ipaddress : str # IP address only ASCOM and INDI
    _api_version : str # API version only ASCOM and INDI

    _can_binning = False
    _can_cooling = False
    _can_gain = False
    _can_get_coolpower = False
    _can_has_shutter = False
    _can_iso = False
    _can_offset = False
    _can_save = True

    _is_color = False
    _is_connected = False
    _is_cooling = False
    _is_exposure = False
    _is_imageready = False

    _max_gain : int
    _min_gain : int
    _max_offset : int
    _min_offset : int
    _max_exposure : float
    _min_exposure : float
    _min_exposure_increment : float
    _max_binning : list

    _height : int
    _width : int
    _max_height : int
    _min_height : int
    _max_width : int
    _min_width : int
    _depth : int
    _max_adu : int
    _imgarray = False    # Now is just for ASCOM
    _bayer_pattern : int
    _bayer_offset_x : int
    _bayer_offset_y : int
    _pixel_height : float
    _pixel_width : float
    _start_x : int
    _start_y : int
    _subframe_x : int
    _subframe_y : int
    _sensor_type : str
    _sensor_name : str

    def get_dict(self) -> dict:
        """
            Return a dictionary containing camera information
            Args : None
            Return : dict
        """
        return {
            "type": self._type,
            "name": self._name,
            "id": self._id,
            "description": self._description,
            "timeout": self._timeout,
            "configration": self._configration,
            "current" : {
                "exposure": self._exposure,
                "gain": self._gain,
                "offset": self._offset,
                "iso": self._iso,
                "binning": self._binning,
                "temperature": self._temperature,
                "cool_power": self._cool_power,
                "percent_complete": self._percent_complete,
            },
            "ability": {
                "can_binning" : self._can_binning,
                "can_cooling" : self._can_cooling,
                "can_gain" : self._can_gain,
                "can_get_coolpower" : self._can_get_coolpower,
                "can_has_shutter" : self._can_has_shutter,
                "can_iso" : self._can_iso,
                "can_offset" : self._can_offset,
            },
            "status" : {
                "is_connected" : self._is_connected,
                "is_cooling" : self._is_cooling,
                "is_exposure" : self._is_exposure,
                "is_imageready" : self._is_imageready
            },
            "properties" : {
                "max_gain" : self._max_gain,
                "min_gain" : self._min_gain,
                "max_offset" : self._max_offset,
                "min_offset" : self._min_offset,
                "max_exposure" : self._max_exposure,
                "min_exposure" : self._min_exposure,
                "max_binning" : self._max_binning,
            },
            "frame" : {
                "height" : self._height,
                "width" : self._width,
                "max_height" : self._max_height,
                "min_height" : self._min_height,
                "max_width" : self._max_width,
                "min_width" : self._min_width,
                "depth" : self._depth if self._depth is not None else 0,
                "max_adu" : self._max_adu,
                "imgarray" : self._imgarray,
                "bayer_pattern" : self._bayer_pattern,
                "bayer_offset_x" : self._bayer_offset_x,
                "bayer_offset_y" : self._bayer_offset_y,
                "pixel_height" : self._pixel_height,
                "pixel_width" : self._pixel_width,
                "start_x" : self._start_x,
                "start_y" : self._start_y,
                "subframe_x" : self._subframe_x,
                "subframe_y" : self._subframe_y,
                "sensor_type" : self._sensor_type,
                "sensor_name" : self._sensor_name,
            },
            "network" : {
                "ipaddress" : self._ipaddress,
                "api_version" : self._api_version,
            }
        }

class BasicCameraAPI(BasicDeviceAPI):
    """
        Basic Camera API Interface
    """

    # #################################################################
    #
    # Camera Basic API (These will be called by client applications)
    #
    # #################################################################

    async def start_exposure(self, params : dict) -> dict:
        """
            Start exposure function | 开始曝光
            Args :
                params :
                    exposure : float # exposure time
            Return : dict
        """

    async def abort_exposure(self, params : dict) -> dict:
        """
            Abort exposure function | 关闭曝光
            Args : None
            Return : dict
        """

    async def get_exposure_status(self, params : dict) -> dict:
        """
            Get exposure status function | 获取曝光状态
            Args : None
            Return : dict
                status" : Exposure Status Object
            NOTE : This function should not be called if the camera is not in exposure
            NOTE : This function should be called just like a looping function
        """

    async def get_exposure_result(self, params : dict) -> dict:
        """
            Get exposure result function | 获取曝光结果
            Args : None
            Return : dict
                image : Base64 Encode Image Data,
                histogram : List,
                info : dict
        """

    async def cooling(self, params : dict) -> dict:
        """
            Cooling function | 制冷
            Args : 
                params :
                    enable : boolean
            Return : dict
            NOTE : This function needs camera supported
        """

    async def cooling_to(self, params : dict) -> dict:
        """
            Cooling to temperature function | 制冷到指定温度
            Args :
                params : 
                    temperature : float
            Return : dict
            NOTE : This function needs camera support
        """

    async def get_cooling_status(self, params : dict) -> dict:
        """
            Get cooling status function | 获取当前制冷状态
            Args : None
            Return : dict
                status : Cooling Status Object
            NOTE : This function needs camera support
        """

    async def get_current_temperature(self, params : dict) -> dict:
        """
            Get current temperature of the camera | 获取相机当前温度
            Args : None
            Return : dict
                temperature : float
        """

    async def get_cooling_power(self , params : dict ) -> dict:
        """
            Get the cooling power of the camera
            Args : None
            Return : dict
                power : float
            NOTE : This function needs camera supported
        """

    # #################################################################
    #
    # Camera Settings
    #
    # #################################################################

    # #################################################################
    # Parameters about the Exposure
    # #################################################################

    @property
    async def gain(self) -> int:
        """
            Get the current gain of this camera
            Args : None
            Return : int
        """

    @gain.setter
    async def gain(self, value : int) -> dict:
        """
            Set the gain of this camera
            Args : value : int
            Return : dict
        """

    @property
    async def offset(self) -> int:
        """
            Get the current offset of this camera
            Args : None
            Return : int
        """

    @offset.setter
    async def offset(self, value : int) -> dict:
        """
            Set the current offset of this camera
            Args : value : int
            Return : dict
        """

    @property
    async def binning(self) -> int | list:
        """
            Get the current binning mode of this camera
            Args : None
            Return : int | list
            NOTE : Some advanced cameras support to set binx and biny
        """

    @binning.setter
    async def binning(self, value : int | list) -> dict:
        """
            Set the binning mode of this camera
            Args : 
                value : list or int based on the camera
            Return : dict
        """

    @property
    async def iso(self) -> int:
        """
            Get the current iso of the camera
            Args : None
            Return : int
        """

    @iso.setter
    async def iso(self, value : int) -> dict:
        """
            Set the iso of the camera
            Args : 
                value : int
            Return : dict
        """

    # #########################################################################
    # Parameters about the Cooling
    # #########################################################################

    @property
    async def temperature(self) -> float:
        """
            Get the current temperature of the camera
            Args : None
            Return : float
            NOTE : This function needs camera supported
        """

    @temperature.setter
    async def temperature(self , value : float) -> dict:
        """
            Set the current temperature of the camera
            Args : 
                value : float
            Return : dict
            NOTE : This function needs camera supported
        """

    @property
    async def cooling_power(self) -> float:
        """
            Get the current Cool power of the camera
            Args : None
            Return : float
            NOTE : This function needs camera supported
        """

    # #################################################################
    # Parameters about the Image
    # #################################################################

    @property
    async def image_height(self) -> int:
        """
            Get the current Image height of the camera
            Args : None
            Return : int
        """

    @image_height.setter
    async def image_height(self , value : int) -> dict:
        """
            Set the frame height of the camera
            Args : 
                value : int
            Return : dict
        """

    @property
    async def image_width(self) -> int:
        """
            Get the frame width of the camera
            Args : None
            Return : int
        """

    @image_width.setter
    async def image_width(self , value : int) -> dict:
        """
            Set the frame width of the camera
            Args : 
                value : int # width of the frame
            Return : dict
        """

    @property
    async def frame_start_x(self) -> int:
        """
            Get the x position of the camera frame start position
            Args : None
            Return : int
        """

    @frame_start_x.setter
    async def frame_start_x(self, value : int) -> dict:
        """
            Set the x position of the camera frame start position
            Args : value : int
            Return : dict
        """

    @property
    async def frame_start_y(self) -> int:
        """
            Get the y position of the camera frame start position
            Args : None
            Return : int
        """

    @frame_start_y.setter
    async def frame_start_y(self, value : int) -> dict:
        """
            Set the y position of the camera frame start position
            Args : value : int
            Return : dict
        """