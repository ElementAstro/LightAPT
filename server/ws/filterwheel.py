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

from utils.i18n import _
from ..logging import logger,return_error

class WSFilterwheel(object):
    """
        Websocket filterwheel interface
    """

    def __init__(self,ws) -> None:
        """
            Initial a new WSFilterwheel
            Args : None
            Returns : None
        """
        self.device = None
        self.ws = ws
        self.thread = None

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
        return self.__class__.__name__

    async def connect(self , params = {}) -> None:
        """
            Async connect to the filterwheel 
            Args : 
                params : dict
                    type : str # ascom or indi
                    device_name : str
                    host : str # both indi and ascom default is "127.0.0.1"
                    port : int # for indi port is 7624 , for ascom port is 11111
            Returns : dict
                info : dict # BasicaFilterwheelInfo object
        """
        if self.device is not None:
            logger.info(_("Disconnecting from existing filterwheel ..."))
            self.disconnect()

        _type = params.get('type')
        _device_name = params.get('device_name')

        if _type is None or _device_name is None:
            return return_error(_("Type or device name must be specified"))
        
        if _type == "indi":
            """from server.api.indi.filterwheel import INDIFilterwheelAPI
            self.device = INDIFilterwheelAPI()"""
        elif _type == "ascom":
            from server.api.ascom.filterwheel import AscomFilterwheelAPI
            self.device = AscomFilterwheelAPI()
        else:
            return return_error(_("Unknown device type"))

        return self.device.connect(params=params)

    async def disconnect(self,params = {}) -> dict:
        """
            Async disconnect from the device
            Args : None
            Returns : dict
        """
        if self.device is None or not self.device.info._is_connected:
            return return_error(_("Filterwheel is not connected"))
        
        return self.device.disconnect()

    async def reconnect(self,params = {}) -> dict:
        """
            Async reconnect to the device
            Args : None
            Returns : dict
                info : dict # just like connect()
            NOTE : This function is just allowed to be called when the filterwheel had already connected
        """
        if self.device is None or not self.device.info._is_connected:
            return return_error(_("Filterwheel is not connected"))

        return self.device.reconnect()

    async def scanning(self,params = {}) -> dict:
        """
            Async scanning all of the devices available
            Args : None
            Returns : dict
                list : list # a list of filterwheels available
        """
        if self.device is not None or self.device.info._is_connected:
            return return_error(_("Filterwheel has already been connected"))

        return self.device.scanning()

    async def polling(self,params = {}) -> dict:
        """
            Async polling method to get the newest filterwheel information
            Args : None
            Returns : dict
                info : dict # usually generated from get_dict() function
        """
        if self.device is not None or self.device.info._is_connected:
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
        if self.device is not None or self.device.info._is_connected:
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
        if self.device is not None or self.device.info._is_connected:
            return return_error(_("Filterwheel is not connected"))

        return self.device.slew_to(params)

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
        if self.device is not None or self.device.info._is_connected:
            return return_error(_("Filterwheel is not connected"))

        return self.device.get_filter_list()