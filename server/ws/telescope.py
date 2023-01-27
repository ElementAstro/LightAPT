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
from ..logging import logger , return_error,return_success,return_warning

class WSTelescope(object):
    """
        Websocket telescope interface
    """

    def __init__(self,ws) -> None:
        """
            Initial a new WSTelescope
            Args : None
            Returns : None
        """
        self.device = None
        self.ws = ws
        self.thread = None

    def __del__(self) -> None:
        """
            Delete a WSTelescope
            Args : None
            Returns : None
        """

    def __str__(self) -> str:
        """
            Returns the name of the WSTelescope class
            Args : None
            Returns : None
        """
        return self.__class__.__name__

    async def connect(self , params = {}) -> None:
        """
            Async connect to the telescope 
            Args : 
                params : dict
                    type : str # ascom or indi
                    device_name : str
                    host : str # both indi and ascom default is "127.0.0.1"
                    port : int # for indi port is 7624 , for ascom port is 11111
            Returns : dict
                info : dict # BasicaTelescopeInfo object
        """
        if self.device is not None:
            logger.info(_("Disconnecting from existing telescope ..."))
            self.disconnect()

        _type = params.get('type')
        _device_name = params.get('device_name')

        if _type is None or _device_name is None:
            logger.error(_("Type or device name must be specified"))
            return return_error(_("Type or device name must be specified"))
        
        if _type == "indi":
            """from server.api.indi.telescope import INDITelescopeAPI
            self.device = INDITelescopeAPI()"""
        elif _type == "ascom":
            from server.api.ascom.telescope import AscomTelescopeAPI
            self.device = AscomTelescopeAPI()
        else:
            logger.error(_("Unknown device type : {}").format(_type))
            return return_error(_("Unknown device type"))

        return self.device.connect(params=params)

    async def disconnect(self,params = {}) -> dict:
        """
            Async disconnect from the device
            Args : None
            Returns : dict
        """
        if self.device is None or not self.device.info._is_connected:
            logger.warning(_("Telescope is not connected , please do not execute disconnect command"))
            return return_error(_("Telescope is not connected"))
        
        return self.device.disconnect()

    async def reconnect(self,params = {}) -> dict:
        """
            Async reconnect to the device
            Args : None
            Returns : dict
                info : dict # just like connect()
            NOTE : This function is just allowed to be called when the telescope had already connected
        """
        if self.device is None or not self.device.info._is_connected:
            logger.warning(_("Telescope is not connected , please do not execute reconnect command"))
            return return_error(_("Telescope is not connected"))

        return self.device.reconnect()

    async def scanning(self,params = {}) -> dict:
        """
            Async scanning all of the devices available
            Args : None
            Returns : dict
                list : list # a list of telescopes available
        """
        if self.device is not None or self.device.info._is_connected:
            logger.warning(_("Telescope had already been connected , please do not execute scanning command"))
            return return_error(_("Telescope has already been connected"))

        return self.device.scanning()

    async def polling(self,params = {}) -> dict:
        """
            Async polling method to get the newest telescope information
            Args : None
            Returns : dict
                info : dict # usually generated from get_dict() function
        """
        if self.device is not None or self.device.info._is_connected:
            logger.warning(_("Telescope is not connected , please do not execute polling command"))
            return return_error(_("Telescope is not connected"))

        return self.device.polling()

    # #############################################################
    #
    # Following methods are used to control the telescope
    #
    # #############################################################

    # #############################################################
    # Goto
    # #############################################################

    async def goto(self,params = {}) -> dict:
        """
            Async goto operation to let the telescope target at a specific point\n
            Args :
                params : dict
                    ra : str or float
                    dec : str or float
                    az : str or float
                    alt : str or float
                    j2000 : bool
            Returns : dict
            NOTE : This function is non-blocking , it will return the results immediately 
                    and start a thread to watch the operation process.If the goto is finished,
                    it will return a message to connected clients
            NOTE : The parameters contain the coordinates of the target , please just use a single
                    axis format like RA/DEC or AZ/ALT , j2000 means if the coordinates are in the
                    format of J2000 , if true , they need to be converted before send to telescope
        """

    async def abort_goto(self,params = {}) -> dict:
        """
            Async abort goto operation
            Args : None
            Returns : dict
            NOTE : This function must be called before shutting down the main server
        """

    async def get_goto_status(self,params = {}) -> dict:
        """
            Async get the status of the goto operation
            Args : None
            Returns : dict
                status : bool # True if the telescope is still slewing
                ra : float # current ra
                dec : float # current dec
        """

    async def get_goto_result(self,params = {}) -> dict:
        """
            Async get the result of the goto operation
            Args : None
            Returns : dict
                ra : str # current ra
                dec : str # current dec
        """
    
    # #############################################################
    # Park
    # #############################################################

    async def park(self,params = {}) -> dict:
        """
            Async park the telescope and after this operation , we cannot control the telescope
            until we unpark the telescope.
            Args : None
            Returns : dict
        """

    async def unpark(self,params = {}) -> dict:
        """
            Async unpark the parked telescope
            Args : None
            Returns : dict
            NOTE : If a telescope is not parked , please do not execute this function
        """

    async def get_park_position(self,params = {}) -> dict:
        """
            Async get the position of the park operation
            Args : None
            Returns : dict
                ra : str # ra of the parking position
                dec : str # dec of the parking position
        """

    async def set_park_position(self,params = {}) -> dict:
        """
            Async set the position of the park operation
            Args : None
                ra : str or float # ra of the parking position
                dec : str or float # dec of the parking position
            Returns : dict
        """

    # #############################################################
    # Home
    # #############################################################

    async def home(self,params = {}) -> dict:
        """
            Async Let the telescope slew to home position
            Args : None
            Returns : dict
        """

    async def get_home_position(self,params = {}) -> dict:
        """
            Async get the home position
            Args : None
            Returns : dict
                ra : str # ra of the home position
                dec : str # dec of the home position
        """

    # #############################################################
    # Track
    # #############################################################

    async def track(self,params = {}) -> dict:
        """
            Async start tracking mode without any parameters
            Args : None
            Returns : dict
        """

    async def abort_track(self,params = {}) -> dict:
        """
            Async abort the tracking
            Args : None
            Returns : dict
        """

    async def get_track_mode(self,params = {}) -> dict:
        """
            Async get the track mode of the current telescope
            Args : None
            Returns : dict
                mode : str
        """

    async def get_track_rate(self,params = {}) -> dict:
        """
            Async get the track rate of the current telescope
            Args : None
            Returns : dict
                ra_rate : float
                def_rate : float
        """

    async def set_track_mode(self,params = {}) -> dict:
        """
            Async set the track mode of the current telescope
            Args : dict
                mode : str
            Returns : dict
        """

    async def set_track_rate(self,params = {}) -> dict:
        """
            Async set the track rate of the current telescope
            Args : dict
                ra_rate : float
                dec_rate : float
        """

    # #############################################################
    # GPS Location
    # #############################################################

    async def get_gps_location(self,params = {}) -> dict:
        """
            Async get GPS location
            Args : None
            Returns : dict
                lon : str
                lat : str
                elevation : float
        """