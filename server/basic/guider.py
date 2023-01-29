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

import selectors
import socket

class TcpSocket(object):
    """
        TCP socket client interface
    """

    def __init__(self):
        self.lines = []
        self.buf = b''
        self.sock = None
        self.sel = None
        self.terminate = False

    def __del__(self):
        self.disconnect()

    def connect(self, hostname, port):
        self.sock = socket.socket()
        try:
            self.sock.connect((hostname, port))
            self.sock.setblocking(False)  # non-blocking
            self.sel = selectors.DefaultSelector()
            self.sel.register(self.sock, selectors.EVENT_READ)
        except Exception:
            self.sel = None
            self.sock = None
            raise

    def disconnect(self):
        if self.sel is not None:
            self.sel.unregister(self.sock)
            self.sel = None
        if self.sock is not None:
            self.sock.close()
            self.sock = None

    def terminate(self):
        self.terminate = True

    def read(self):
        while not self.lines:
            while True:
                if self.terminate:
                    return ''
                events = self.sel.select(0.5)
                if events:
                    break
            s = self.sock.recv(4096)
            i0 = 0
            i = i0
            while i < len(s):
                if s[i] == b'\r'[0] or s[i] == b'\n'[0]:
                    self.buf += s[i0 : i]
                    if self.buf:
                        self.lines.append(self.buf)
                        self.buf = b''
                    i += 1
                    i0 = i
                else:
                    i += 1
            self.buf += s[i0 : i]
        return self.lines.pop(0)

    def send(self, s):
        b = s.encode()
        totsent = 0
        while totsent < len(b):
            sent = self.sock.send(b[totsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totsent += sent

class BasicGuiderInfo(object):
    """
        Basic Guider Information container
    """

    _is_connected = False
    _is_device_connected = False
    _is_looping = False
    _is_calibrating = False
    _is_dithering = False
    _is_guiding = False
    _is_settling = False

    _is_calibrated = False
    _is_selected = False
    _is_settled = False
    _is_starlost = False
    _is_starlocklost = False

    _can_cooling = False

    def get_dict(self) -> dict:
        """
            Return Guider Information in the dictionary format
        """

class BasicGuiderAPI(BasicDeviceAPI):
    """
        Basic Guider API Interface
    """

    def start_looping(self,params = {}) -> dict:
        """
            Start looping to get image | 循环曝光
            Args: 
                params :

            Return :  dict
        """

    async def stop_looping(self,params = {}) -> dict:
        """
            Stop the looping process | 停止循环曝光
            Args : None
            Return :  dict
        """

    async def get_looping_status(self,params = {}) -> dict:
        """
            Get the looping status | 循环曝光
            Return :  {
                "status" : int,
                "message" : str,
                "params" : dict
            }
        """
    
    async def get_looping_result(self,params = {}) -> dict:
        """
            Get the looping result | 循环曝光结果
            Return :  {
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE : This function should get the image of the looping
        """

    async def start_guiding(self, params = {}) -> dict:
        """
            Start guiding | 开始导星
            Args:
                params:{

                }
            Return : {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """

    async def abort_guiding(self,params = {}) -> dict:
        """
            Abort guiding | 停止导星
            Return : {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """

    async def get_guiding_status(self,params = {}) -> dict:
        """
            Get guiding status | 获取导星状态
            Return : {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """

    async def get_guiding_result(self,params = {}) -> dict:
        """
            Get the result of the current guiding result | 获取导星结果
            Return : {
                "status" : int,
                "message" : str,
                "params" : None
            }
            NOTE : This function usually be called after canceling the guiding
        """

    async def start_calibration(self, params = {}) -> dict:
        """
            Start calibration | 开始校准
            Args:
                params:{

                }
            Return : dict
        """
    
    async def abort_calibration(self,params = {}) -> dict:
        """
            Abort the calibration | 停止校准
            Args: None
            Return : {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """

    async def get_calibration_status(self,params = {}) -> dict:
        """
            Get the status of the calibration | 获取校准状态
            Return : {
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : str
                }
            }
        """

    async def get_calibration_result(self,params = {}) -> dict:
        """
            Get the result of the calibration | 获取校准结果
            Return : {
                "status" : int,
                "message" : str,
                "params" : {
                    "result" : str
                }
            }
        """

    async def start_dither(self, params = {}) -> dict:
        """
            Start dithering | 开始抖动
            Args:
                params:{

                }
            Return :  dict
        """

    def abort_dither(self,params = {}) -> dict:
        """
            Abort dither | 停止抖动
            Args: None
            Return : dict
        """

    def get_dither_status(self,params = {}) -> dict:
        """
            Get the status of the dither process | 获取抖动状态
            Return : {
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : str
                }
            }
        """

    def get_dither_result(self,params = {}) -> dict:
        """
            Get the result of the dither process | 获取抖动结果
            Return : {
                "status" : int,
                "message" : str,
                "params" : {
                    "result" : str
                }
            }
        """
