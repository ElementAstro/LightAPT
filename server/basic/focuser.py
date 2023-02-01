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

from .device import BasicDeviceAPI

class BasicFocuserInfo(object):
    """
        Focuser Info class for containing focuser information
    """

    _type = "" # type of the camera , must be given
    _name : str # name of the camera
    _id : int # id of the camera
    _description : str
    _timeout = 300
    _configration = "" # path to the configuration file

    _ipaddress : str # IP address only ASCOM and INDI
    _api_version : str # API version only ASCOM and INDI

    _current_position : int
    _step_size : int # current step size
    _temperature : float

    _max_steps : int # Focuser true limit for steps
    _max_increment : int # Max steps per move operation
    
    _is_connected = False
    _is_moving = False
    _is_compensation = False

    _can_temperature = False

    def get_dict(self) -> dict:
        """
            Return focuser information in a dictionary
            Args: None
            Return: dict
        """
        return {
            "type": self._type,
            "name": self._name,
            "id": self._id,
            "description": self._description,
            "timeout": self._timeout,
            "configration": self._configration,
            "current" : {
                "position" : self._current_position,
                "step_size" : self._step_size,
                "temperature" : self._temperature
            },
            "abilitiy" : {
                "can_temperature" : self._can_temperature
            },
            "status" : {
                "is_connected" : self._is_connected,
                "is_moving" : self._is_moving
            },
            "properties" : {
                "max_steps" : self._max_steps,
                "max_increment" : self._max_increment
            },
            "network" : {
                "ipaddress" : self._ipaddress,
                "api_version" : self._api_version,
            }
        }

class BasicFocuserAPI(BasicDeviceAPI):
    """
        Basic Focuser API Interface
    """

    # #################################################################
    #
    # Focuser Basic API
    #
    # #################################################################

    async def move_step(self, params = {}) -> dict:
        """
            Focuser move given step | 电调移动指定步数
            Args :
                params : 
                    step : int
            Return : dict
        """

    async def move_to(self , params = {}) -> dict:
        """
            Move to target position | 移动至指定位置
            Args :
                params : 
                    position : int
            Return : dict
        """

    async def abort_movement(self , params = {}) -> dict:
        """
            Abort movement | 停止
            Args : None
            Return : dict
        """

    async def get_temperature(self) -> dict:
        """
            Get focuser temperature | 获取电调温度
            Args : None
            Return : dict
                temperature : float
            NOTE : This function needs focuser support
        """

    async def get_movement_status(self) -> dict:
        """
            Get focuser movement status
            Args : None
            Return : dict
                status : int
                position : int
        """