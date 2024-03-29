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
import json
import os

# Tornoda server , provide websocket services
import tornado.web
import tornado.websocket
import tornado.options
import tornado.auth
from tornado.options import options

from .settings import check_encoding_setting, get_host_keys_settings, get_policy_setting, get_server_settings, get_ssl_context

from utils.i18n import _
from .logging import logger,return_error

from .webserver import IndexHtml,ClientHtml,DesktopHtml,DebugHtml,WebSSHHtml
from .webserver import NoVNCHtml,BugReportHtml,SkymapHtml,TestHtml,DeviceHtml
from .webserver import DesktopBrowserHtml,DesktopStoreHtml,DesktopSystemHtml
from .webserver import LoginHandler , RegisterHandler , LockScreenHandler , LicenseHandler , ForgetPasswordHandler

from .ws.indi import (INDIClientWebSocket,INDIDebugWebSocket,INDIDebugHtml,
                        INDIFIFODeviceStartStop,INDIFIFOGetAllDevice,
                        INDIServerConnect,INDIServerDisconnect,INDIServerIsConnected
                        )

import server.api

from .webssh.handler import IndexHandler as webssh_index_handler
from .webssh.handler import WsockHandler as webssh_wsock_handler

import sys
# Check if the system is windows , if true then change asyncio settings
if sys.platform == 'win32' and sys.version_info.major == 3 and \
        sys.version_info.minor >= 8:
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class MainWebsocketServer(tornado.websocket.WebSocketHandler):
    """
        Main websocket server to process all of the commands
        url : /device
    """

    def __init__(self, application, request, **kwargs) -> None:
        """
            Initialize the websocket server with the given application
            Args : 
                application : Tornado application
                request : httputil.request
            Returns : None
        """
        super().__init__(application, request, **kwargs)
        self.worker = None

    def __del__(self) -> None:
        """
            Delete the main websocket server and disconnect all of the devices still connected
            Args: None
            Returns: None
        """

    def check_origin(self, origin: str) -> bool:
        """
            Check if the origin(override)
            Args : origin : str
            Returns : bool
        """
        return True

    def open(self) -> None:
        """
            Event handler for opening the websocket connection
            Args : None
            Returns : None
        """
        logger.debug(_("Opening websocket connection with the client"))

    def on_close(self, code = None, reason = None) -> None:
        """
            Event handler for closing websocket connection
            Args : 
                code : int , status code
                reason : string 
            Returns : None
        """
        logger.debug(_("Closing websocket connection with status code : {} and reason : {}").format(code,reason))

    def on_ping(self, data: bytes) -> None:
        """
            Event handler for ping event
            Args : data : bytes
            Returns : None
            TODO : Will this become a signal to refresh the infomation the client need
        """

    async def on_message(self, message) -> None:
        """
            Event handler for message from the client and need to use asynchronously\n
            Args : message : str
            Returns : None

            Message Example: following format is a dictionary
                device : str
                event : str # Like "connect" or "disconnect"
                params : dict # all of the parameters should be put inside the dict
                    info : dict # this is a example , you can put everything

                {
                    "device" : "camera",
                    "event" : "connect",
                    "params" : {
                        "port" : 11111,
                        "host" : "127.0.0.1",
                        "device_number" : 0,
                        "type" : "ascom",
                        "device_name" : ""
                    }
                }

            ReturnMessage :
                status : int
                type : str # tell the client if this is a pure text message or a binary message
                message : str
                params : dict # the parameters sent to the client

                {
                    "status": 0 , # 0 means success
                    "message": "connected successfully",
                    "params": {
                        "info" : camera information
                    }
                }
        """
        # Parser the message
        command = None
        if isinstance(message,str):
            try:
                command = json.loads(message)
            except json.JSONDecodeError as e:
                logger.error(_("Failed to parse message to a dictionary : {}").format(e))
                await self.write_message(json.dumps(return_error(_("Failed to parse message to a dictionary"))))
                return
        elif isinstance(message,list):
            # TODO : will we add a multi-command message , just like a sequence
            pass
        else:
            await self.write_message(_("Failed to parse message to a dictionary , Unknown message"))
            return
        # Run the command and wait for the response)
        try:
            # NOTE : There the websocket instance will be loaded into the function 
            res = await self.worker.run_command(
                command["device"],
                command["event"],
                command["params"],
                self
            )
        except KeyError as e:
            logger.error(_("Failed to execute command : {}").format(e))
            await self.write_message({"status": 1, "message": "Failed to execute command"})
        # Return the response to client
        await self.write_message(json.dumps(await self.generate_command(res)))
        
    async def generate_command(self, params : dict) -> dict:
        """
            Generates driver responses to the format expected
            Args : params : dict
            Returns : dict
        """
        r = None
        if params.get("params",{}).get('image') is not None:
            r = params.get("params",{}).get('image')
        else:
            r = {"type" : "data"}
            r.update(params)
        return r
    
def make_server(loop, options) -> tornado.web.Application:
    """
        Initialize the tornado websocket server
        Args : None
        Returns : tornado.web.Application
    """
    try:
        host_keys_settings = get_host_keys_settings(options)
    except UserWarning:
        pass
    policy = get_policy_setting(options, host_keys_settings)

    return tornado.web.Application([
            (r"/", IndexHtml),
            (r"/client",ClientHtml),
            (r"/ndesktop",DesktopHtml),
            (r"/ndesktop-system",DesktopSystemHtml),
            (r"/ndesktop-store",DesktopStoreHtml),
            (r"/ndesktop-browser",DesktopBrowserHtml),
            (r"/device", MainWebsocketServer),
            (r"/debug",DebugHtml),
            (r"/webssh",WebSSHHtml),
            (r"/login",LoginHandler),
            (r"/register",RegisterHandler),
            (r"/license",LicenseHandler),
            (r"/forget-password",ForgetPasswordHandler),
            (r"/lockscreen",LockScreenHandler),
            (r"/bugreport",BugReportHtml),
            (r"/novnc",NoVNCHtml),
            (r"/skymap",SkymapHtml),
            (r"/test",TestHtml),
            (r"/devices",DeviceHtml),

            (r"/indi/debug/",INDIDebugHtml),
            (r"/indi/ws/debugging/", INDIDebugWebSocket),
            (r"/indi/ws/indi_client/", INDIClientWebSocket),
            (r"/indi/FIFO/([^/]+)/([^/]+)/([^/]+)/", INDIFIFODeviceStartStop),
            (r"/indi/get/all/devices/", INDIFIFOGetAllDevice),
            (r'/indi/server/connect/', INDIServerConnect),
            (r'/indi/server/disconnect/', INDIServerDisconnect),
            (r'/indi/server/connected/',INDIServerIsConnected),

            (r'/webssh/',webssh_index_handler,dict(loop=loop, policy=policy,
                                  host_keys_settings=host_keys_settings)),
            (r'/webssh/ws',webssh_wsock_handler,dict(loop=loop))
        ],
        template_path=os.path.join(
            os.getcwd(),"client","templates"
        ),
        static_path=os.path.join(
            os.getcwd(),"client","static"
        ),
        debug = True,
        login_url = "/login",
        cookie_secret = "lightapt",
        xsrf_cookies = True,
        autoreload = True
    ) 

async def run_server(host : str = "127.0.0.1", port : str = 8080, debug : bool = False) -> None:
    """
        Run the tornado server
        Args : 
            host : str # host of the server , default is 127.0.0.1
            port : int # port of the server , default is 8080
            debug : bool # whether start debug mode
        Returns : None
        NOTE : There must use asyncio.run to execute
    """
    # Get all of the available options
    options.parse_command_line()
    check_encoding_setting(options.encoding)
    loop = tornado.ioloop.IOLoop.current()
    wsserver = make_server(loop, options)
    # Get the server safety options
    server_settings = get_server_settings(options)
    wsserver.listen(options.port,options.address,**server_settings)
    # Get the SSL context options if available
    ssl_ctx = get_ssl_context(options)
    if ssl_ctx:
        wsserver.listen(options.sslport, options.ssladdress, **server_settings)
    logger.info("Started SSL server on %s:%d" % (options.address,options.port))
    shutdown = asyncio.Event()
    await shutdown.wait()

if __name__ == "__main__":
    # If the server is running in main thread
    asyncio.run(run_server())