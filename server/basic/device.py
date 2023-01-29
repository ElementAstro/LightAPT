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

class BasicDeviceAPI(object):
    """
        Basic Device API (All of the following methods should be overridden)
    """

    def __init__(self) -> None:
        """
            Constructor | 构造函数\n
            Args : None
            Return : None
            Usage : Initialize info container and device
        """

    def __del__(self) -> None:
        """
            Destructor | 析构函数\n
            Args : None
            Return : None
            Usage : Check if device is still running , and cancel all missions
        """

    def __str__(self) -> str:
        """
            Returns string representation of the device
            Args : None
            Return : str
        """

    async def connect(self, params = {}) -> dict:
        """
            Connect to device | 连接设备\n
            Args:
                params :
                    name : str # name of device
                    ip : str # ip of device , ASCOM and INDI only
                    port : int # port of device , ASCOM and INDI only
            Return : dict
        """

    async def disconnect(self, params = {}) -> dict:
        """
            Disconnect from device | 与设备断开连接\n
            Args : None
            Return: dict
            NOTE : This function must be called when destory self !
        """

    async def reconnect(self , params = {}) -> dict:
        """
            Reconnect to device | 重新连接设备\n
            Args : None
            Return: dict
                info : device information
        """

    async def scanning(self, params = {}) -> dict:
        """
            Scanning of device | 扫描已连接设备\n
            Args : None
            Return : dict
                list : list # list of devices available
            NOTE : This function is suggested to be called before trying to connect devices
        """

    async def polling(self, params = {}) -> dict:
        """
            Polling of device | 获取设备最新信息\n
            Args : None
            Usage:
                Polling of device newest infomation
            Return: dict
                info : device infomation
            NOTE : This function just returns the self.info object in a dictionary
        """

    async def get_configration(self, params = {}) -> dict:
        """
            Get configration of device | 获取设备配置\n
            Args : None
            Return: dict
            NOTE : This function usually is called when initial the device
            NOTE : After this function is called , we should get all of the infomation about the camera we needed
        """

    async def load_configration(self, params = {}) -> dict:
        """
            Load configration of device | 读取设备配置\n
            Args : None
            Usage: Load configration of device
            Return: dict
        """

    async def save_configration(self, params = {}) -> dict:
        """
            Save configration of device | 保存设备配置\n
            Args : None
            Return: dict
        """

    async def get_parameter(self , params = {}) -> dict:
        """
            Get the specified parameter of the device configuration
            Args :
                params : dict
                    name : str # name of the parameter
            Returns : dict
                value : int | str | float
        """

    async def set_parameter(self, params = {}) -> dict:
        """
            Set the specified parameters of the device
            Args : 
                params : dict
                    name : str # name of the parameter
                    value : value of the parameter
            Return : dict
        """