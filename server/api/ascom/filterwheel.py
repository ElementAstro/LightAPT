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

from server.basic.filterwheel import BasicFilterwheelAPI,BasicFilterwheelInfo
from _filterwheel import FilterWheel
from _exceptions import (DriverException,
                                        NotConnectedException,
                                        InvalidValueException)

from utils.i18n import _
from ...logging import logger,return_error,return_success,return_warning

class AscomFilterwheelAPI(BasicFilterwheelAPI):
    """
        ASCOM Filterwheel API Interface
    """

    def __init__(self) -> None:
        """
            Initialize the ASCOM Filterwheel object
            Args : None
            Return : None
        """
        self.info = BasicFilterwheelInfo()
        self.device = None

    def __del__(self) -> None:
        """
            Delete the ASCOM Filterwheel object
            Args : None
            Return : None
        """
        if self.info._is_connected:
            self.disconnect()

    def __str__(self) -> str:
        """
            Return the name of the ASCOM Filterwheel object
            Args : None
            Return : str
        """
        return _("LightAPT Ascom Filterwheel Interface")

    def connect(self, params : dict) -> dict:
        """
            Connect to ASCOM filterwheel | 连接ASCOM滤镜轮
            Args : 
                host: str # default is "127.0.0.1",
                port: int # default is 11111,
                device_number : int # default is 0
            Return : dict
                info : BasicFilterwheelInfo object
        """
        # Check if the filterwheel had already been connected , if true just return the current status
        if self.info._is_connected or self.device is not None:
            return return_warning(_("Filterwheel is connected"),{"info":self.info.get_dict()})
        # Check if the parameters are correct
        host = params.get('host')
        port = params.get('port')
        device_number = params.get('device_number')
        # If the host or port is null
        if host is None or port is None or device_number is None:
            return return_warning(_("Host or port or device_number is None"),{})
        # Trying to connect to the specified filterwheel
        try:
            self.device = FilterWheel(host + ":" + str(port), device_number)
            self.device.Connected = True
        except DriverException as e:
            return return_error(_("Failed to connect to filterwheel"),{"error" : e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error while connecting to filterwheel"),{"error" : e})
        res = self.get_configration()
        if res.get('status') != 0:
            return return_error(_(f"Failed tp load filterwheel configuration"),{})
        self.info._is_connected = True
        self.info._type = "ascom"
        return return_success(_("Connect to filterwheel successfully"),{"info":self.info.get_dict()})

    def disconnect(self) -> dict:
        """
            Disconnect from ASCOM filterwheel | 断链
            Args : None
            Return : dict
            NOTE : This function must be called before destory all server
        """
        if not self.info._is_connected or self.device is None:
            return return_warning(_("Filterwheel is not connected"),{})
        try:
            self.device.Connected = False
        except DriverException as e:
            return return_error(_("Failed to disconnect from device"),{"error" : e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error" : e})
        self.device = None
        self.info._is_connected = False
        return return_success(_("Disconnect from filterwheel successfully"),{})

    def reconnect(self) -> dict:
        """
            Reconnect to ASCOM filterwheel | 重连
            Args : None
            Return : dict
                info : BasicFilterwheelInfo object
        """
        if self.device is None or not self.info._is_connected:
            return return_warning(_("Filterwheel is not connected"),{}) 
        try:
            self.device.Connected = False
            sleep(1)
            self.device.Connected = True
        except DriverException as e:
            return return_error(_("Failed to reconnect to device"),{"error" : e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error" : e})
        self.info._is_connected = True
        return return_success(_("Reconnect filterwheel successfully"),{"info" : self.info.get_dict()})

    def polling(self) -> dict:
        """
            Polling for ASCOM filterwheel
            Args : None
            Return : dict
                info : BasicFilterwheelInfo object
        """
        if self.device is None or not self.info._is_connected:
            return return_warning(_("Filterwheel is not connected"),{})
        return return_success(_("Filterwheel's information is refreshed"),{"info":self.info.get_dict()})

    def get_configration(self) -> dict:
        """
            Get filterwheel infomation | 获取滤镜轮信息
            Args : None
            Return : dict
                info : BasicFilterwheelInfo object
        """
        try:
            self.info._name = self.device.Name
            logger.debug(_("Filterwheel name : {}").format(self.info._name))
            self.info._id = self.device._client_id
            logger.debug(_("Filterwheel ID : {}").format(self.info._id))
            self.info._description = self.device.Description
            logger.debug(_("Filterwheel description : {}").format(self.info._description))
            self.info._ipaddress = self.device.address
            logger.debug(_("Filterwheel IP address : {}").format(self.info._ipaddress))
            self.info._api_version = self.device.api_version
            logger.debug(_("Filterwheel API version : {}").format(self.info._api_version))

            self.info._filter_offset = self.device.FocusOffsets
            logger.debug(_("Filterwheel Filter Offset : {}").format(self.info._filter_offset))
            self.info._filter_name = self.device.Names
            logger.debug(_("Filterwheel Filter Name : {}").format(self.info._filter_name))
            self.info._current_position = self.device.Position
            logger.debug(_("Filterwheel Current Position : {}").format(self.info._current_position))

        except NotConnectedException as e:
            return return_error(_("Remote device is not connected"),{"error":e})
        except DriverException as e:
            return return_error(_("Drvier error"),{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error":e})

        return return_success(_("Get filterwheel configuration successfully"),{"info" : self.info.get_dict()})

    def set_configration(self, params: dict) -> dict:
        return super().set_configration(params)

    def load_configration(self) -> dict:
        return super().load_configration()

    def save_configration(self) -> dict:
        """
            Save configration of filterwheel
            Args : None
            Return : dict
        """
        _p = path.join
        _path = _p("config",_p("filterwheel",self.info._name+".json"))
        if not path.exists("config"):
            mkdir("config")
        if not path.exists(_p("config","filterwheel")):
            mkdir(_p("config","filterwheel"))
        self.info._configration = _path
        with open(_path,mode="w+",encoding="utf-8") as file:
            file.write(dumps(self.info.get_dict(),indent=4,ensure_ascii=False))
        return return_success(_("Save filterwheel information successfully"),{})

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
    # The following functions are used to control the filterwheel (all is non-blocking)
    #
    # #################################################################

    def slew_to(self, params: dict) -> dict:
        """
            Let the filterwheel slew to the specified position
            Args :
                params : dict
                    id : int
            Return : dict
        """
        if not self.info._is_connected or self.device is None:
            return return_error(_("Filterwheel is not connected"),{})

        _id = params.get('id')

        if _id is None or not isinstance(_id,int):
            return return_error(_("Provided _id is not valid"),{})

        if not 0 <= _id <= len(self.info._filter_name):
            return return_error(_("Provided _id is out of range"),{})

        try:
            self.device.Position = _id
            self.info._current_position = _id
        except InvalidValueException as e:
            return return_error(_("Provided id is not valid"),{"error" : e})
        except NotConnectedException as e:
            return return_error(_("Remote device is not connected"),{"error":e})
        except DriverException as e:
            return return_error(_("Drvier error"),{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error":e})

        return return_success(_("Filterwheel slewed to target position {} successfully").format(self.info._current_position),{})

    def get_filters_list(self) -> dict:
        """
            Get a list of filter name and offset
            Args : None
            Reterns : dict
                offset : list
                name : list
        """
        if not self.info._is_connected or self.device is None:
            return return_error(_("Filterwheel is not connected"),{})

        try:
            self.info._filter_name = self.device.Names
            self.info._filter_offset = self.device.FocusOffsets
        except NotConnectedException as e:
            return return_error(_("Remote device is not connected"),{"error":e})
        except DriverException as e:
            return return_error(_("Drvier error"),{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error":e})

    def get_current_filter(self) -> dict:
        """
            Get the current position of the filterwheel
            Args : None
            Return : dict
                position : int
        """
        if not self.info._is_connected or self.device is None:
            return return_error(_("Filterwheel is not connected"),{})

        try:
            self.info._current_position = self.device.Position
        except NotConnectedException as e:
            return return_error(_("Remote device is not connected"),{"error":e})
        except DriverException as e:
            return return_error(_("Drvier error"),{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error":e})

        logger.info(_("Get the filterwheel filter name list : {}").format(self.info._filter_name))
        logger.info(_("Get the filterwheel filter offset list : {}").format(self.info._filter_offset))

        return return_success(_("Get the filterwheel current position successfully"),{
            "offset" : self.info._filter_offset,
            "name" : self.info._filter_name,
            "position" : self.info._current_position
        })
    
import asyncio
import tornado.ioloop
import tornado.websocket

class WSAscomFilterwheel(object):
    """
        Websocket filterwheel interface of the AscomFilterwheelAPI class
    """

    def __init__(self) -> None:
        """
            Initial a new WSFilterwheel
            Args : None
            Returns : None
        """
        self.thread = None
        self.device = AscomFilterwheelAPI()

    def __del__(self) -> None:
        """
            Delete a WSFilterwheel
            Args : None
            Returns : None
        """

    def __str__(self) -> str:
        """
            Returns the name of the WSFilterwheel class
            Args : None
            Returns : None
        """
        return "LightAPT Ascom Filterwheel Websocket Wrapper Class"  
    
    async def connect(self , params = {} , ws = None) -> None:
        """
            Async connect to the filterwheel 
            Args : 
                params : dict
                    device_name : str
                    host : str # both indi and ascom default is "127.0.0.1"
                    port : int # for indi port is 7624 , for ascom port is 11111
            Returns : dict
                info : dict # BasicaFilterwheelInfo object
        """
        if self.device is not None:
            logger.info(_("Disconnecting from existing filterwheel ..."))
            await self.disconnect()

        _device_name = params.get('device_name')

        if  _device_name is None:
            return return_error(_("Type or device name must be specified"))
        
        return self.device.connect(params=params)

    async def disconnect(self,params = {} , ws = None) -> dict:
        """
            Async disconnect from the device
            Args : None
            Returns : dict
        """
        if self.device is None:
            return return_error(_("Filterwheel is not connected"))
        
        return self.device.disconnect()

    async def reconnect(self,params = {} , ws = None) -> dict:
        """
            Async reconnect to the device
            Args : None
            Returns : dict
                info : dict # just like connect()
            NOTE : This function is just allowed to be called when the filterwheel had already connected
        """
        if self.device is None:
            return return_error(_("Filterwheel is not connected"))

        return self.device.reconnect()

    async def polling(self,params = {} , ws = None) -> dict:
        """
            Async polling method to get the newest filterwheel information
            Args : None
            Returns : dict
                info : dict # usually generated from get_dict() function
        """
        if self.device is None:
            return return_error(_("Filterwheel is not connected"))

        return self.device.polling()

    # #############################################################
    #
    # Following methods are used to control the filterwheel
    #
    # #############################################################

    # #############################################################
    # Current filter
    # #############################################################

    async def get_current_filter(self,params = {}) -> dict:
        """
            Get the current filter of the filter wheel
            Args : None
            Returns : dict
                filter_id : int # id of the current filter
        """
        if self.device is None:
            return return_error(_("Filterwheel is not connected"))

        return self.device.get_current_filter()

    # #############################################################
    # Slew
    # #############################################################

    async def slew_to(self,params = {}) -> dict:
        """
            Filter wheel slew to the current filter
            Args : dict
                id : int # id of the target filter
            Returns : dict
        """
        if self.device is None:
            return return_error(_("Filterwheel is not connected"))

        _id = params.get('id')
        if _id is None or not isinstance(_id, int):
            return return_error(_("Invalid filter id specified"))

        res = self.device.slew_to(params)
        if res.get("status") != 0:
            return res

        tornado.ioloop.IOLoop.instance().add_callback(self.slew_thread,_id)

        return res

    async def slew_thread(self , target_id : int) -> None:
        """
            Slewing status monitor thread
        """
        used_time = 0
        while used_time <= self.device.info._timeout:
            res = await self.get_current_filter()
            
            if res.get("params").get('position') == target_id:
                break
            await asyncio.sleep(0.5)
            used_time += 0.5

    # ###############################################################
    # Get all of the available filters
    # ###############################################################

    async def get_filter_list(self, params = {}) -> dict:
        """
            Async get all of the available filters
            Args : None
            Returns : dict
                offset : a list of the filters offsets
                name : a list of the names of the filters
        """
        if self.device is None:
            return return_error(_("Filterwheel is not connected"))

        return self.device.get_filter_list()