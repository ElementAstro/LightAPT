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

import asyncio
import functools
import json
import threading
from time import sleep
import tornado
import tornado.ioloop

from utils.i18n import _
from ..logging import logger , return_error,return_success,return_warning

class WSCamera(object):
    """
        Websocket camera wrapper class
    """

    def __init__(self,ws) -> None:
        """
            Initial constructor for WSCamera class methods 
            Args : None
            Returns : None
        """
        self.device = None
        self.ws = ws
        self.blob = asyncio.Event()
        self.thread = None

    def __str__(self) -> str:
        """
            Returns the name of the WSCamera class
            Args : None
            Returns : None
        """
        return self.__class__.__name__

    async def connect(self , params : dict) -> None:
        """
            Async connect to the camera 
            Args : 
                params : dict
                    type : str # ascom or indi
                    device_name : str
                    host : str # both indi and ascom default is "127.0.0.1"
                    port : int # for indi port is 7624 , for ascom port is 11111
            Returns : dict
        """
        if self.device is not None:
            logger.info(_("Disconnecting from existing camera ..."))
            await self.disconnect()

        _type = params.get('type')
        _device_name = params.get('device_name')

        if _type is None or _device_name is None:
            return (_("Type or device name must be specified"))
        
        if _type == "indi":
            """from server.api.indi.camera import INDICameraAPI
            self.device = INDICameraAPI()"""
        elif _type == "ascom":
            from server.api.ascom.camera import AscomCameraAPI
            self.device = AscomCameraAPI()
        else:
            return return_error(_("Unknown device type"))
        res = self.device.connect(params=params)
        print(res)
        return res

    async def disconnect(self,params = {}) -> dict:
        """
            Async disconnect from the device
            Args : None
            Returns : dict
        """
        if self.device is None:
            return return_error(_("Camera is not connected , please do not execute disconnect command"))
        
        return self.device.disconnect()

    async def reconnect(self,params : dict) -> dict:
        """
            Async reconnect to the device
            Args : None
            Returns : dict
            NOTE : This function is just allowed to be called when the camera had already connected
        """
        if self.device is None:
            return return_error(_("Camera is not connected , please do not execute reconnect command"))

        return self.device.reconnect()

    async def scanning(self,params = {}) -> dict:
        """
            Async scanning all of the devices available
            Args : None
            Returns : dict
        """
        if self.device is not None or self.device.info._is_connected:
            return return_error(_("Camera had already been connected , please do not execute scanning command"))

        return self.device.scanning()

    async def polling(self,params = {}) -> dict:
        """
            Async polling method to get the newest camera information
            Args : None
            Returns : dict
        """
        if self.device is None:
            return return_error(_("Camera is not connected , please do not execute polling command"))

        return self.device.polling()

    async def start_exposure(self, params = {}) -> dict:
        """
            Async start exposure event
            Args : 
                params : dict
                    exposure : float
            Returns : dict
        """
        if self.device is None:
            return return_error(_("Camera int not connected , please do not execute start exposure command"))

        exposure = params.get('exposure')

        if exposure is None or not 0 <= exposure <= 3600:
            return return_error(_("A reasonable exposure value is required"))
        
        self.blob.clear()
        
        res = self.device.start_exposure(params)
        if res.get('status') != 0:
            return res

        tornado.ioloop.IOLoop.instance().add_callback(self.exposure_thread)

        return return_success(_("Exposure started successfully"),{})

    async def abort_exposure(self,params = {}) -> dict:
        """
            Async abort the exposure operation
            Args : None
            Returns : None
        """
        if self.device is None:
            return return_error(_("Camera is not connected , please do not execute abort exposure command"))

        return self.device.abort_exposure()

    async def exposure_thread(self) -> None:
        """
            Guard thread during the exposure and read the the status of the camera each second
            Args : None
            Returns : None
        """
        used_time = 0
        while used_time <= self.device.info._timeout:
            res = await self.get_exposure_status()
            
            if not res.get("params").get('status'):
                break
            await asyncio.sleep(0.5)
            used_time += 0.5
        await self.get_exposure_result()

    async def get_exposure_status(self,params = {}) -> dict:
        """
            Async get status of the exposure process
            Args : None
            Returns : None
        """
        if self.device is None:
            return (_("Camera is not connected , please do not execute get exposure status command"))

        if not self.device.info._is_exposure:
            return (_("Exposure is not started, please do not execute get exposure status command"))

        res = self.device.get_exposure_status()

        await self.ws.write_message(res)
        
        if res.get('status') != 0:
                self.blob.clear()
            
        if res.get('params').get('status') is True:
            self.blob.set()
        else:
            self.blob.clear()

        return res

    async def get_exposure_result(self) -> dict:
        """
            Get the result of the exposure operation
            Args : None
            Returns : None
            NOTE : I'm not sure that whether this function should be called directly by client
        """
        if self.device is None:
            return (_("Camera is not connected , please do not execute get exposure result command"))
        
        res = self.device.get_exposure_result()
        res["type"] = "data"
        await self.ws.write_message(json.dumps(res))
        return res

    async def cooling(self , params = {}) -> dict:
        """
            Async start or stop cooling mode
            Args :
                params : dict
                    enable : bool
            Return : dict
        """
        if self.device is None:
            return (_("Camera is not connected , please do not execute cooling command"))
        
        return self.device.cooling(params=params)

    async def cooling_to(self, params = {}) -> dict:
        """
            Async make the camera cool to specified temperature
            Args :
                params : dict
                    temperature : float
            Return : dict
        """
        if self.device is None:
            return (_("Camera is not connected , please do not execute cooling to command"))

        return self.device.cooling_to(params=params)

    async def get_current_temperature(self , params = {}) -> dict:
        """
            Async get the current temperature of the camera
            Args : None
            Return : dict
                temperature : float
        """
        if self.device is None:
            return (_("Camera is not connected , please do not execute get current temperature command"))

        return self.device.get_current_temperature(params=params)

    async def get_cooling_power(self , params = {}) -> dict:
        """
            Async get the cooling power of the camera
            Args : None
            Return : dict
                power : float
        """
        if self.device is None:
            return (_("Camera is not connected , please do not execute get current cool power command"))

        return self.device.get_cooling_power(params=params)

    async def get_cooling_status(self , params = {}) -> dict:
        """
            Async get the cooling status of the camera
            Args : None
            Returns : dict
                status : bool
        """
        if self.device is None:
            return (_("Camera is not connected , please do not execute get cooling status command"))

        return self.device.get_cooling_status(params=params)

    async def start_fan(self, params = {}) -> dict:
        """
            Async start fan of the camera (only for INDI and ToupCam)
            Args : None
            Return : dict
        """
        if self.device is None:
            return (_("Camera is not connected , please do not execute start fan command"))

        return self.device.start_fan(params=params)

    async def stop_fan(self, params = {}) -> dict:
        """
            Async stop fan of the camera (only for INDI and ToupCam)
            Args : None
            Return : dict
        """
        if self.device is None:
            return (_("Camera is not connected , please do not execute stop fan command"))

        return self.device.stop_fan(params=params)

    async def start_heat(self, params = {}) -> dict:
        """
            Async start heating camera (only for INDI and ToupCam)
            Args : None
            Return : dict
        """
        if self.device is None:
            return (_("Camera is not connected , please do not execute start heating command"))

        return self.device.start_heat(params=params)

    async def stop_heat(self, params = {}) -> dict:
        """
            Async stop heating of the camera (only for INDI and ToupCam)
            Args : None
            Return : dict
        """
        if self.device is None:
            return (_("Camera is not connected , please do not execute stop heat command"))

        return self.device.stop_heat(params=params)