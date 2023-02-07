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

import importlib
import json
import requests

from camera import WSAscomCamera
from telescope import WSAscomTelescope
from focuser import WSAscomFocuser
from filterwheel import WSAscomFilterwheel

from utils.i18n import _
from ...logging import logger , return_error

class ASCOMWebsocketWorker(object):
    """
        ASCOM websocket worker , no need to what the source code like , just call the API method
    """

    def __init__(self) -> None:
        """
            Just initialize the worker , no device connection
            Args : None
            Returns : None
        """
        self.telescope = WSAscomTelescope()
        self.camera = WSAscomCamera()
        self.focuser = WSAscomFocuser()
        self.filterhweel = WSAscomFilterwheel()

        self.win32api = None
        self.can_win32api = True

    def __del__(self) -> None:
        """"""

    def __str__(self) -> str:
        return "LightAPT ASCOM Websocket Worker"
    
    def scan_devices(self , host : str, port : int,protocol = "http", timeout = 100 , version = 1) -> dict:
        """
            Scan the devices under the specified IP\n
            Args :
                host : str # host of the alpaca server
                port : int # port of the alpaca server
                protocol : str # default is http , if you use SSL mode , please specify https
                version : int # default is 1 , this is depending on Alpyca , no need to specify
            Returns : dict
                devices : dict
                    name : str # name of the device
                    description : str # description of the device
                    connected : bool # whether the device is connected
                    driver_info : str # driver information
                    driver_version : str # driver version
            If the device dictionary returns null, it means that the server is not connected to 
            any device or the server is not existing.
        """
        base_url = protocol + "://" + host + ":" + str(port) + "/api/v" + str(version) + "/"
        devices = {}
        for device_type in ["camera", "telescope", "focuser","filterwheel"]:
            device_id = 0
            devices[device_type] = {}
            while True:
                try:
                    devices[device_type][device_id] = {}
                    for label in ["name","description","connected","driverinfo","driverversion"]:
                        url = base_url + device_type + "/" + str(device_id) + "/" + label
                        try:
                            devices[device_type][device_id][label] = requests.get(url).json()["Value"]
                        except json.JSONDecodeError:
                            devices[device_type].pop(device_id)
                            raise requests.exceptions.ConnectionError
                    device_id += 1
                except (requests.exceptions.ConnectionError,requests.exceptions.Timeout):
                    try:
                        if not devices[device_type][device_id]:
                            devices[device_type].pop(device_id)
                    except KeyError:
                        pass
                    break
            if not devices[device_type]:
                devices.pop(device_type)
        return devices
    
    def scan_server_exe(self) -> str | None:
        """
            Get the path of the server executable\n
            Args : None
            Returns : str | None
        """
        # Try to import win32api module
        if self.can_win32api:
            if self.win32api is None:
                try:
                    self.win32api = importlib.import_module("win32api")
                    self.win32con = importlib.import_module("win32con")
                except ImportError:
                    self.can_win32api = False
        else:
            return return_error(_("No win32 API available"))
        # Try to find ASCOM Remote Server
        name = "ASCOM.RemoteServer.exe"
        path = None
        key = rf'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{name}'
        # Find the software by getting the Windows registry
        key = self.win32api.RegOpenKey(self.win32con.HKEY_LOCAL_MACHINE, key, 0, self.win32con.KEY_READ)
        info2 = self.win32api.RegQueryInfoKey(key)
        for j in range(0, info2[1]):
            key_value = self.win32api.RegEnumValue(key, j)[1]
            if key_value.upper().endswith(name.upper()):
                path = key_value
                break
        self.win32api.RegCloseKey(key)
        return path
    
    def scan_device_exe(self , device_binary : str) -> str:
        """
            Search for device-driven executable files\n
            Args :
                device_binary : str
            Returns : str
        """
        
    def get_device_by_type(self , device_type : str):
        """
            Get the device instance by type
            Args : 
                device_type : str 
            Returns : device instance
        """
        if device_type == "camera":
            return self.camera
        elif device_type == "telescope":
            return self.telescope
        elif device_type == "filterwheel":
            return self.filterwheel
        elif device_type == "focuser":
            return self.focuser
        return None
    
    def get_device_info_by_type(self, device_type : str) -> dict | None:
        """
            Get the device information by device type . All of the information is in a dictionary\n
            Args :
                device_type : str
            Returns : dict
        """
        if device_type == "camera":
            return self.camera.info.get_dict()
        elif device_type == "telescope":
            return self.telescope.info.get_dict()
        elif device_type == "focuser":
            return self.focuser.info.get_dict()
        elif device_type == "filterwheel":
            return self.filterwheel.info.get_dict()
        return None
    
    async def run_command(self, device : str, command : str , params : dict , ws) -> dict:
        """
            Execute the command asynchronously and return the response\n
            Args : 
                device : str # device type like "cameras" or "telescope"
                command : str # command to execute
                params : dict # parameters
            Returns : dict
                status : int # status code
                message : str # message
                params : dict # parameters to return to client
        """
        _command = None
        if device == "camera":
            # Pay attention to if the camera command is available , the following devices are the same
            try:
                _command = getattr(self.camera,command)
            except AttributeError as e:
                return return_error(_("Camera command not available"),{"error":e})
        elif device == "telescope":
            try:
                _command = getattr(self.telescope,command)
            except AttributeError as e:
                return return_error(_("Telescope command not available"),{"error":e})
        elif device == "focuser":
            try:
                _command = getattr(self.focuser,command)
            except AttributeError as e:
                return return_error(_("Focuser command not available"),{"error":e})
        elif device == "filterwheel":
            try:
                _command = getattr(self.filterwheel,command)
            except AttributeError as e:
                return return_error(_("Filterwheel command not available"),{"error":e})
        elif device == "guider":
            try:
                _command = getattr(self.guider,command)
            except AttributeError as e:
                return return_error(_("Guider command not available"),{"error":e})
        elif device == "sovler":
            try:
                _command = getattr(self.sovler,command)
            except AttributeError as e:
                return return_error(_("Solver command not available"),{"error":e})
        else:
            return return_error(_("Unknown device type"))

        res = {
            "status": 0,
            "message": "",
            "params": {}
        }
        try:
            res = await _command(params)
        except Exception as e:
            logger.error(_("Error executing command : {}").format(e))
            return return_error(_("Error executing command"),{"error":e})
        return res
    
    


                
