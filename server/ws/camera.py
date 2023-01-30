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
import threading
from time import sleep
import tornado

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

    def __del__(self) -> None:
        """
            Deinitialize the WSCamera class method
            Args : None
            Returns : None
        """
        if self.device.info._is_connected:
            self.device.disconnect()

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
            self.disconnect()

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

        return self.device.connect(params=params)

    async def disconnect(self,params = {}) -> dict:
        """
            Async disconnect from the device
            Args : None
            Returns : dict
        """
        if self.device is None or not self.device.info._is_connected:
            return return_error(_("Camera is not connected , please do not execute disconnect command"))
        
        return self.device.disconnect()

    async def reconnect(self,params : dict) -> dict:
        """
            Async reconnect to the device
            Args : None
            Returns : dict
            NOTE : This function is just allowed to be called when the camera had already connected
        """
        if self.device is None or not self.device.info._is_connected:
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
        if self.device is None or not self.device.info._is_connected:
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
        if self.device is None or not self.device.info._is_connected:
            return return_error(_("Camera int not connected , please do not execute start exposure command"))

        exposure = params.get('exposure')

        if exposure is None or not 0 <= exposure <= 3600:
            return return_error(_("A reasonable exposure value is required"))
        
        self.blob.clear()
        
        res = self.device.start_exposure(exposure)
        if res.get('status') != 0:
            return res

        self.thread = threading.Thread(target=asyncio.run,args=(self.exposure_thread))
        try:
            self.thread.daemon = True
        except:
            self.thread.setDaemon(True)
        self.thread.start()

        tornado.ioloop.IOLoop.instance().add_callback(self.wait_exposure_result,exposure)

    async def abort_exposure(self,params = {}) -> dict:
        """
            Async abort the exposure operation
            Args : None
            Returns : None
        """
        if self.device is None or not self.device.info._is_connected:
            return return_error(_("Camera is not connected , please do not execute abort exposure command"))

        if not self.device.info._is_exposure:
            return return_error(_("Exposure is not started, please do not execute abort exposure command"))

        return self.device.abort_exposure()

    async def exposure_thread(self) -> None:
        """
            Guard thread during the exposure and read the the status of the camera each second
            Args : None
            Returns : None
        """
        used_time = 0
        while await self.get_exposure_status().get("params").get('status') and used_time <= self.device.info._timeout:
            await asyncio.sleep(0.5)
            used_time += 0.5

    async def get_exposure_status(self,params = {}) -> dict:
        """
            Async get status of the exposure process
            Args : None
            Returns : None
        """
        if self.device is None or not self.device.info._is_connected:
            return (_("Camera is not connected , please do not execute get exposure status command"))

        if not self.device.info._is_exposure:
            return (_("Exposure is not started, please do not execute get exposure status command"))

        res = self.device.get_exposure_status()
        if res.get('status') != 0:
            self.blob.clear()
        
        if res.get('params').get('status') is True:
            self.blob.set()
        else:
            self.blob.clear()
        
        return res

    async def get_exposure_result(self) -> None:
        """
            Get the result of the exposure operation
            Args : None
            Returns : None
        """

    async def wait_exposure_result(self) -> dict:
        """
            Wait for exposure result and return it as a dict with image
            Args : None
            Returns : dict
        """
        r = {
            "status" : 0,
            "message" : "",
            "params" : {}
        }
        try:
            await asyncio.wait_for(self.blob, timeout=self.device.info._timeout)
            logger.info(_("Camera exposure finished"))
            r["message"] = _("Exposure finished successfully")
        except TimeoutError:
            logger.info(_("Camera exposure timed out"))
            r["status"] = 1
            r["message"] = _("Camera exposure timed out")
        finally:
            self.device.info._is_exposure = False
            self.blob.clear()
        
        

        
        

        