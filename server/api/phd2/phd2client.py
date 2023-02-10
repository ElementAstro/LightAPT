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

# #################################################################
# 
# This file is part of LightAPT server , which contains the functionality 
# of the communication between the server and the PHD2 , via asynchronous 
# socket communication
#
# #################################################################

import asyncio
import os
import platform
import subprocess
import socket

from ...logging import phd2_logger as logger

class PHD2ClientWorker(object):
    """
        PHD2 client but alse worker , all of the functions should be asynchronous.
        And do not exist any blocking operations , such as 'while True'
    """

    def __init__(self) -> None:
        """
            Initialize the PHD2 client instance and prepare the connection
            Args : None
            Returns : None
        """
        self.client = None
        self.phd2_instance = None

    def __del__(self) -> None:
        """
            Destructor of the PHD2 client instance
        """

    def __str__(self) -> str:
        """
            Returns a string representation of the client instance
        """
        return "LightAPT PHD2 Client and Network Worker"
    
    # #################################################################
    #
    # Http Request Handler Functions
    #
    # #################################################################
    
    # #################################################################
    # Start or stop the PHD2 server
    # #################################################################
    
    async def start_phd2(self , path = None) -> dict:
        """
            Start the PHD2 server with the specified path
            Args :
                path : str # full path to the PHD2 server executable
            Returns : {
                "message": str # None if the operation was successful
            }
        """
        res = {
            "message": None
        }
        # Check if the instance had already been created
        if self.phd2_instance is not None:
            logger.warning("Phd2 instance had already been created")
            res["message"] = "Phd2 instance had already been created"
            return res
        
        phd2_path = None
        # judge the system type
        if platform.platform() == "Windows":
            if path is None:
                phd2_path = "C:\Program Files (x86)\PHDGuiding2\phd2.exe"
            else:
                phd2_path = path
        elif platform.platform() == "Linux":
            if path is None:
                phd2_path = "/usr/bin/phd2"
            else:
                phd2_path = path
        logger.debug("PHD2 executable path : {}".format(phd2_path))
        
        # Check whether the executable is existing
        if not os.path.exists(phd2_path):
            logger.error("PHD2 executable path does not exist: {}".format(phd2_path))
        
        self.phd2_instance = asyncio.subprocess.create_subprocess_exec(
            program=phd2_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        logger.info("PHD2 server started successfully")
        res["message"] = "PHD2 server started successfully"
        return res
    
    async def stop_phd2(self) -> dict:
        """
            Stop the phd2 server
            Args : None
            Returns : {
                "message" : str
            }
        """
        res = {
            "message" : None
        }
        if self.phd2_instance is None:
            logger.error("No phd2 instance running on this machine")
            res["message"] = "No phd2 instance running on this machine"
            return res
        try:
            self.phd2_instance.close()
        except Exception as e:
            logger.error("Failed to close phd2 instance : {}".format(e))
            res["message"] = "Failed to close phd2 instance"
            return res
        
        logger.info("Phd2 server stopped successfully")
        res["message"] = "Phd2 server stopped successfully"
        return res

    async def scan_server(self, start_port = 4400 , end_port = 4405) -> dict:
        """
            Scan the PHD2 server available in the specified port
            Args:
                start_port : int 
                end_port : int
            Returns:{
                "list" : [] # a list of the ports which servers are listening on
            }
        """
        res = {
            "list" : []
        }
        if start_port > end_port or not isinstance(start_port,int) or not isinstance(end_port,int):
            logger.error("Invalid port was specified")
            return res
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for port in range(start_port,end_port+1):
            try:
                sock.bind(("localhost",port))
                sock.shutdown(2)
                res["list"].append(port)
            except socket.error:
                pass
        logger.debug("Found {} servers".format(len(res["list"])))
        return res
    
    async def connect_server(self , port = 4400) -> dict:
        """
            Connect to the PHD2 server on the specified port
            Args :
                port : int 
            Returns : {
                "message": str # None if the operation is successful
            }
        """

    async def disconnect_server(self) -> dict:
        """
            Disconnects from the PHD2 server
            Args : None
            Returns : {
                "message": str # None if the operation is successful
            }
        """

    async def reconnect_server(self) -> dict:
        """
            Reconnects to the PHD2 server
            Args : None
            Returns : {
                "message": str # None if the operation is successful
            }
        """