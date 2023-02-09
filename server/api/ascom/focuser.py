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

from time import sleep
from requests import exceptions
from json import dumps
from os import mkdir, path

from ._focuser import Focuser
from ._exceptions import (DriverException,
                                        NotConnectedException,
                                        NotImplementedException,
                                        InvalidValueException,
                                        InvalidOperationException)

from utils.i18n import _
from ...logging import ascom_logger as logger
from ...logging import return_error,return_success,return_warning

class AscomFocuserAPI(object):
    """
        ASCOM Focuser API Interface
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

    def __init__(self) -> None:
        """
            Construct a new ASCOM Focuser object
            Args : None
            Return : None
        """
        self.device = None

    def __del__(self) -> None:
        """
            Delete the device instance
            Args : None
            Return : None
        """
        if self._is_connected:
            self.disconnect()

    def __str__(self) -> str:
        return "LightAPT ASCOM Focuser API Interface"
    
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

    
    def connect(self, params: dict) -> dict:
        """
            Connect to ASCOM focuser | 连接ASCOM电调
            Args: 
                host: str # default is "127.0.0.1",
                port: int # default is 11111,
                device_number : int # default is 0
            Return : dict
                info : BasicFocuserInfo object
        """
        # Check if the focuser had already been connected , if true just return the current status
        if self._is_connected or self.device is not None:
            return return_warning(_("Focuser is connected"),{"info":self.get_dict()})
        # Check if the parameters are correct
        host = params.get('host')
        port = params.get('port')
        device_number = params.get('device_number')
        # If the host or port is null
        if host is None or port is None or device_number is None:\
            return return_warning(_("Host or port or device_number is None"),{})
        # Trying to connect to the specified focuser
        try:
            self.device = Focuser(host + ":" + str(port), device_number)
            self.device.Connected = True
        except DriverException as e:
            return return_error(_("Failed to connect to device"),{"error" : e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error while connecting to focuser"),{"error" : e})
        res = self.get_configration()
        if res.get('status') != 0:
            return return_error(_(f"Failed tp load focuser configuration"),{})
        self._is_connected = True
        self._type = "ascom"
        return return_success(_("Connect to focuser successfully"),{"info":self.get_dict()})

    def disconnect(self) -> dict:
        """
            Disconnect from ASCOM focuser | 断链
            Args: None
            Return : dict
            NOTE : This function must be called before destory all server
        """
        if not self._is_connected or self.device is None:
            return return_warning(_("Focuser is not connected"),{})
        try:
            self.device.Connected = False
        except DriverException as e:
            return return_error(_(f"Failed to disconnect from device"),{"error" : e})
        except exceptions.ConnectionError as e:
            return return_error(_(f"Network error"),{"error" : e})
        self.device = None
        self._is_connected = False
        return return_success(_("Disconnect from focuser successfully"),{})

    def reconnect(self) -> dict:
        """
            Reconnect to ASCOM focuser | 重连
            Args: None
            Return : dict
                info : BasicFocuserInfo object
        """
        if self.device is None or not self._is_connected:
            return return_warning(_("Focuser is not connected"),{}) 
        try:
            self.device.Connected = False
            sleep(1)
            self.device.Connected = True
        except DriverException as e:
            return return_error(_("Failed to reconnect to device"),{"error" : e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error" : e})
        self._is_connected = True
        return return_success(_("Reconnect focuser successfully"),{"info" : self.get_dict()})

    def polling(self) -> dict:
        """
            Polling for ASCOM focuser
            Args: None
            Return : dict
                info : BasicFocuserInfo object
        """
        if self.device is None or not self._is_connected:
            return return_warning(_("Focuser is not connected"),{})
        return return_success(_("Focuser's information is refreshed"),{"info":self.get_dict()})

    def get_configration(self) -> dict:
        """
            Get focuser infomation | 获取电调信息
            Args: None
            Return : dict
                info : BasicFocuserInfo object
        """
        try:
            self._name = self.device.Name
            logger.debug(_("Focuser name : {}").format(self._name))
            self._id = self.device._client_id
            logger.debug(_("Focuser ID : {}").format(self._id))
            self._description = self.device.Description
            logger.debug(_("Focuser description : {}").format(self._description))
            self._ipaddress = self.device.address
            logger.debug(_("Focuser IP address : {}").format(self._ipaddress))
            self._api_version = self.device.api_version
            logger.debug(_("Focuser API version : {}").format(self._api_version))

            # Get infomation about the focuser temperature ability
            self._can_temperature = self.device.TempCompAvailable
            logger.debug(_("Can focuser get temperature: {}").format(self._can_temperature))
            if self._can_temperature:
                try:
                    self._temperature = self.device.Temperature
                    logger.debug(_("Focuser current temperature : {}°C").format(self._temperature))
                except NotImplementedException as e:
                    logger.error(_("Failed to get current temperature , error: {}").format(e))
                    self._can_temperature = False
            else:
                self._temperature = -256

            # Get the max step the focuser can move to , this is for focuser safety purposes

            self._current_position = self.device.Position
            logger.debug(_("Focuser Current Position: {}").format(self._current_position))
            self._max_steps = self.device.MaxStep
            logger.debug(_("Focuser Max Step : {}").format(self._max_steps))
            self._max_increment = self.device.MaxIncrement
            logger.debug(_("Focuser Max Increment : {}").format(self._max_increment))

            # Get the current position of the focuser 

            self._current_position = self.device.Position
            logger.debug(_("Current Position : {}").format(self._current_position))
            self._step_size = self.device.StepSize
            logger.debug(_("Step Size : {}").format(self._step_size))
        
        except NotImplementedException as e:
            return return_error(_("Focuser is not supported"),{"error":e})
        except NotConnectedException as e:
            return return_error(_("Remote device is not connected"),{"error":e})
        except DriverException as e:
            return return_error(_("Drvier error"),{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error":e})

        return return_success(_("Get focuser configuration successfully"),{"info" : self.get_dict()})

    def set_configration(self, params: dict) -> dict:
        return super().set_configration(params)

    def load_configration(self) -> dict:
        return super().load_configration()

    def save_configration(self) -> dict:
        """
            Save configration of focuser
            Args : None
            Return : dict
        """
        _p = path.join
        _path = _p("config",_p("focuser",self._name+".json"))
        if not path.exists("config"):
            mkdir("config")
        if not path.exists(_p("config","focuser")):
            mkdir(_p("config","focuser"))
        self._configration = _path
        with open(_path,mode="w+",encoding="utf-8") as file:
            file.write(dumps(self.get_dict(),indent=4,ensure_ascii=False))
        return return_success(_("Save focuser information successfully"),{})

    def get_parameter(self, params : dict) -> dict:
        """
            Get the specified parameter and return the value
            Args : 
                params : dict
                    name : str # name of the parameter
        """

    def set_parameter(self, params = {}) -> dict:
        """
            Set the specified parameter of the filterwheel
            Args :
                params : dict
                    name : str
                    value : str
        """

    # #################################################################
    #
    # The following functions are used to control the focuser (all is non-blocking)
    #
    # #################################################################

    def move_to(self, params: dict) -> dict:
        """
            Let the focuser move to the specified position
            Args : 
                params : dict
                    position : int # position of the target
            Return : dict
        """
        if not self._is_connected or self.device is None:
            return return_error(_("Focuser is not connected"),{})
        if self._is_moving:
            return return_warning(_("Focuser is moving"),{})
        
        position = params.get("position")
        if position is None:
            return return_error(_("Target position is required"),{})
        
        if not isinstance(position,int) or not 0 <= position <= self._max_steps:
            return return_error(_("Position is not a valid value"),{})

        try:
            self.device.Move(Position=position)
        except InvalidValueException as e:
            return return_error(_("Invalid position value"),{"error":e})
        except DriverException as e:
            return return_error(_("Driver error: {}"),{"error":e})
        except NotConnectedException as e:
            return return_error(_("Focuser is not connected"),{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error: {}"),{"error":e})

        self._is_moving = True
        return return_success(_("Focuser started operation successfully"),{})

    def move_step(self, params: dict) -> dict:
        """
            Move to position which add a specified steps to the current position
            Args : 
                params : dict
                    step : int # step size
            Return : dict
        """
        if not self._is_connected or self.device is None:
            return return_error(_("Focuser is not connected"),{})

        if self._is_moving:
            return return_error(_("Focuser is moving"),{})

        step = params.get("step")

        if step is None or not isinstance(step,int):
            return return_error(_("Step size is required , but now it is not available"),{})

        if step > self._max_increment or not 0 <= self._current_position + step <= self._max_steps:
            return return_error(_("Given step is out of range and may cause the focuser broken"),{})

        try:
            self.device.Move(Position=self._current_position+step)
        except InvalidValueException as e:
            return return_error(_("Invalid step value"),{"error":e})
        except InvalidOperationException as e:
            return return_error(_("Invalid operation value"),{"error":e})
        except NotConnectedException as e:
            return return_error(_("Focuser is not connected"),{"error":e})
        except DriverException as e:
            return return_error(_("Focuser is not connected"),{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error":e})
        
        self._is_moving = True
        return return_success(_("Focuser started move operation successfully"),{})

    def abort_move(self):
        """
            Abort current move operation
            Args : None
            Return : dict
                position : int # current position after abort operation
        """
        if not self._is_connected or self.device is None:
            return return_error(_("Focuser is not connected"),{})
        
        if not self._is_moving:
            return return_error(_("Focuser is not moving"),{})

        try:
            self.device.Halt()
            sleep(0.5)
            if not self.device.IsMoving:
                self._is_moving = False
        except NotImplementedException as e:
            return return_error(_("Failed to abort focuser"),{"error":e})
        except NotConnectedException as e:
            return return_error(_("Focuser is not connected"),{"error":e})
        except DriverException as e:
            return return_error(_("Driver error"),{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error":e})
            
        return return_success(_("Abort focuser move operation successfully"),{"position" : self.device.Position})
    
    def get_movement_status(self) -> dict:
        """
            Get the status of the current move operation
            Args : None
            Return : dict
                status : int # status of the operation
                position : int # position of the current position
        """
        if not self._is_connected or self.device is None:
            return return_error(_("Focuser is not connected"),{})

        if not self._is_moving:
            return return_error(_("Focuser is not moving"),{})

        try:
            status = self.device.IsMoving
            self._is_moving = status
            position = self.device.Position
            self._current_position = position
        except NotImplementedException as e:
            return return_error(_("Failed to get status of the operation"),{"error":e})
        except NotConnectedException as e:
            return return_error(_("Failed to get status of the operation"),{"error":e})
        except DriverException as e:
            return return_error(_("Driver error"),{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error":e})

        return return_success(_("Get focuser status successfully"),{"status" : status,"position":position})

    def get_temperature(self) -> dict:
        """
            Get the current temperature of the focuser
            Args : None
            Return : dict
                temperature : float
            NOTE : This function needs focuser supported
        """
        # Check if the focuser is connected
        if not self._is_connected or self.device is None:
            return return_error(_("Focuser is not connected"),{})

        if not self._can_temperature:
            return return_error(_("Focuser is not supported to get temperature"))

        try:
            self._temperature = self.device.Temperature
        except NotImplementedException as e:
            self._can_temperature = False
            return return_error(_("Focuser is not supported to get temperature"),{"error":e})
        except NotConnectedException as e:
            self._is_connected = False
            return return_error(_("Focuser is not connected"),{"error":e})
        except DriverException as e:
            return return_error(_("Driver error"),{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error":e})

        logger.debug(_("Current Focuser Temperature : {}").format(self._temperature))

        return return_success(_("Get focuser temperature successfully"),{"temperature":self._temperature})

    def get_current_position(self) -> dict:
        """
            Get the current position of the focuser
            Args : None
            Return : dict
                position : int
        """
        if not self._is_connected or self.device is None:
            return return_error(_("Focuser is not connected"),{})

        try:
            position = self.device.Position
        except NotImplementedException as e:
            return return_error(_("Failed to get current position of the focuser"),{"error":e})
        except NotConnectedException as e:
            return return_error(_("Failed to get current position of the focuser"),{"error":e})
        except DriverException as e:
            return return_error(_("Driver error"),{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error":e})

        return return_success(_("Get the focuser current position successfully"),{"position":position})
    
import asyncio
import tornado.ioloop
import tornado.websocket

class WSAscomFocuser(object):
    """
        Websocket focuser interface
    """

    def __init__(self) -> None:
        """
            Initial a new WSFocuser
            Args : None
            Returns : None
        """
        self.device = AscomFocuserAPI()
        self.ws = None
        self.thread = None

    def __del__(self) -> None:
        """
            Delete a WSFocuser
            Args : None
            Returns : None
        """

    def __str__(self) -> str:
        """
            Returns the name of the WSFocuser class
            Args : None
            Returns : None
        """
        return "LightAPT Ascom Focuser Websocket Wrapper Class"

    async def connect(self , params = {}) -> None:
        """
            Async connect to the focuser 
            Args : 
                params : dict
                    device_name : str
                    host : str # both indi and ascom default is "127.0.0.1"
                    port : int # for indi port is 7624 , for ascom port is 11111
            Returns : dict
                info : dict # BasicaFocuserInfo object
        """
        if self.device is not None:
            logger.info(_("Disconnecting from existing focuser ..."))
            self.disconnect()

        _device_name = params.get('device_name')
        if  _device_name is None:
            return return_error(_("Type or device name must be specified"))
        
        return self.device.connect(params=params)

    async def disconnect(self,params = {}) -> dict:
        """
            Async disconnect from the device
            Args : None
            Returns : dict
        """
        if self.device is None:
            return return_error(_("Focuser is not connected"))
        
        return self.device.disconnect()

    async def reconnect(self,params = {}) -> dict:
        """
            Async reconnect to the device
            Args : None
            Returns : dict
                info : dict # just like connect()
            NOTE : This function is just allowed to be called when the focuser had already connected
        """
        if self.device is None:
            return return_error(_("Focuser is not connected"))

        return self.device.reconnect()

    async def polling(self,params = {}) -> dict:
        """
            Async polling method to get the newest focuser information
            Args : None
            Returns : dict
                info : dict # usually generated from get_dict() function
        """
        if self.device is None:
            return return_error(_("Focuser is not connected"))

        return self.device.polling()

    async def get_parameter(self, params = {}) -> dict:
        """
            Get the specified parameter and return the value
            Args : 
                params : dict
                    name : str # name of the parameter
        """
        if self.device is None:
            return return_error(_("Focuser is not connected"))

        return self.get_parameter(params=params)

    async def set_parameter(self, params = {}) -> dict:
        """
            Set the specified parameter of the camera
            Args :
                params : dict
                    name : str
                    value : str
        """
        if self.device is None:
            return return_error(_("Focuser is not connected"))

        return self.set_parameter(params=params)

    # #############################################################
    #
    # Following methods are used to control the focuser
    #
    # #############################################################

    # #############################################################
    # Current position
    # #############################################################

    async def get_current_position(self,params = {}) -> dict:
        """
            Get the current position of the focuser
            Args : None
            Returns : dict
                position : int
        """
        if self.device is None:
            return return_error(_("Focuser is not connected"))

        return self.get_current_position()

    # #############################################################
    # Move
    # #############################################################

    async def move_step(self,params = {}) -> dict:
        """
            Move in or out in a distance of the specified step
            Args : 
                params : dict
                    step : int
            Returns : dict
        """
        if self.device is None:
            return return_error(_("Focuser is not connected"))
        
        step = params.get('step')
        if step is None or not isinstance(step, int) or not 0 <= step <= self.device.info._max_steps:
            return return_error(_("Invalid step value was provided"),{})

        res = self.device.move_step(params)
        
        tornado.ioloop.IOLoop.instance().add_callback(self.move_thread)

        return res

    async def move_to(self,params = {}) -> dict:
        """
            Move to a specific position
            Args :
                params : dict
                    position : int
            Returns : dict
        """
        if self.device is None:
            return return_error(_("Focuser is not connected"))

        position = params.get('position')
        if position is None or not isinstance(position,int) or not 0 <= position <= self.device.info._max_steps:
            return return_error(_("Invalid target position was provided"),{})

        res = self.device.move_to(params)

        tornado.ioloop.IOLoop.instance().add_callback(self.move_thread)

        return res

    async def move_thread(self) -> None:
        """
            Movement monitoring thread
        """
        used_time = 0
        while used_time <= self.device.info._timeout:
            res = await self.get_movement_status()
            
            if not res.get("params").get('status'):
                break
            await asyncio.sleep(0.5)
            used_time += 0.5


    async def get_movement_status(self,params = {}) -> dict:
        """
            Get the status of movement
            Args : None
            Returns : dict
                status : bool # True if the focuser is moving
                position : int # current position
        """
        if self.device is None:
            return return_error(_("Focuser is not connected"))

        res = self.device.get_movement_status()

        await self.ws.write_message(res)

        return res

    # #############################################################
    # Temperature
    # #############################################################

    async def get_temperature(self , params = {}) -> dict:
        """
            Async get the current temperature of the focuser
            Args : None
            Returns : dict
                temperature : float
            NOTE : This function need focuser supported
        """
        if self.device is None:
            return return_error(_("Focuser is not connected"))

        return self.device.get_temperature()

    async def get_current_position(self) -> dict:
        """
            Async get the current position of the focuser
            Args : None
            Return : dict
                position : int
        """
        if self.device is None:
            return return_error(_("Focuser is not connected"))

        return self.device.get_current_position()