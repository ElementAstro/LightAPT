# coding=utf-8

"""

Copyright(c) 2022 Max Qian  <astroair.cn>

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

"""
  _      _       _     _            _____ _______ 
 | |    (_)     | |   | |     /\   |  __ \__   __|
 | |     _  __ _| |__ | |_   /  \  | |__) | | |   
 | |    | |/ _` | '_ \| __| / /\ \ |  ___/  | |   
 | |____| | (_| | | | | |_ / ____ \| |      | |   
 |______|_|\__, |_| |_|\__/_/    \_\_|      |_|   
            __/ |                                 
           |___/                                  
"""

import argparse,os,json
import asyncio
import sys

import server.config as c
from utils.i18n import _
from server.logging import logger

def main():
    """
        Main function | 主函数
        Args : None
        Return : None
    """
    # Load configuration from file
    try:
        with open(os.path.join(os.getcwd(),"server","config","config.json"),mode="r",encoding="utf-8") as f:
            c.config = json.load(f)
    except FileNotFoundError as e:
        logger.error(_("Config file not found : {}").format(str(e)))
    except json.JSONDecodeError as e:
        logger.error(_("Config file is not valid : {}").format(str(e)))
    except:
        logger.error(_("Unknown error while reading config file : {}").format(str(e)))

    # Command line arguments
    parser = argparse.ArgumentParser()
    # Server options
    parser.add_argument('--port', type=int,help=_("Port the server is listening on"))
    parser.add_argument('--host', type=str,help=_("Host the server is listening on"))
    parser.add_argument('--debug', type=bool,help=_("Enable debug output for better debug"))
    # Configuration and version
    parser.add_argument('--config', type=str, help=_("Config file"))
    parser.add_argument('--version', type=bool, help=_("Show current version"))
    # Webssh settings
    parser.add_argument('--sshport', type=int,help=_("The SSH port to connect to"))
    parser.add_argument('--sshhost', type=str,help=_("The SSH host to connect to"))
    # TUI
    parser.add_argument('--tui',type=bool,default=False,help=_("Start a terminal ui for debugging"))
    args = parser.parse_args()
    # Change the host if the command line argument is specified
    if args.host:
        _host = args.host
        if not isinstance(_host,str):
            logger.error(_("Invalid host"))
        c.config["host"] = _host
        logger.info(_("Server host : {}").format(_host))
    # Change the port if the command line argument is specified
    if args.port:
        _port = int(args.port)
        if not isinstance(_port,int):
            logger.error(_("Invalid port"))
        c.config["port"] = _port
        logger.info(_("Server port : {}").format(_port))
    # Change the debug mode if available
    if args.debug:
        """Debug mode"""
        c.config["debug"] = False
        logger.info(_("DEBUG mode is enabled"))
    # TUI
    if args.tui:
        from server.tui.main import LightAPTTui
        app = LightAPTTui()
        app.run()
    else:
        try:
            # Run script server
            import server.script
            from multiprocessing import Process
            script_server = Process(target=server.script.run_scriptserver,daemon=True).start()
            # Run main web server
            from server.wsapp import run_server
            asyncio.run(run_server())
        except KeyboardInterrupt:
            logger.info(_("Shutdown LightAPT server by user"))

if __name__ == "__main__":
    main()