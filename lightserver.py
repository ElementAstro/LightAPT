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
        with open(os.path.join(os.getcwd(),"config","config.json"),mode="r",encoding="utf-8") as f:
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
    parser.add_argument('--threaded', type=bool,help=_("Enable mutiline threading for better performance"))
    # Configuration and version
    parser.add_argument('--config', type=str, help=_("Config file"))
    parser.add_argument('--version', type=bool, help=_("Show current version"))
    # Websocket server options
    parser.add_argument('--wsport', type=int, help=_("Websocket server port"))
    parser.add_argument('--wshost', type=str, help=_("Websocket server host"))
    parser.add_argument('--wsssl',type=bool, help=_("Websocket SSL mode"))
    parser.add_argument('--wskey',type=str,help=_("Websocket SSL key"))
    parser.add_argument('--wscert',type=str,help=_("Websocket SSL certificate"))
    # INDI web manager options
    parser.add_argument('--indiweb' , type=bool,help=_("Start the INDI web manager"))
    parser.add_argument('--indihost',type=str,help=_("INDI server address"))
    parser.add_argument('--indiport', type=int,help=_("The port where the INDI server is running"))
    parser.add_argument('--indiconfig', type=str,help=_("The path of the INDI temp files"))
    parser.add_argument('--indidata', type=str,help=_("The path of the INDI data files"))
    parser.add_argument('--indififo', type=str,help=_("The path of the INDI fifo pipe"))
    parser.add_argument('--indiauto', type=bool,help=_("Connect to the INDI device when server is started"))
    # Webssh settings
    parser.add_argument('--webssh', type=bool,help=_("Start a webssh client"))
    parser.add_argument('--websshport', type=int,help=_("The port the web ssh server is running on"))
    parser.add_argument('--sshport', type=int,help=_("The SSH port to connect to"))
    parser.add_argument('--sshhost', type=str,help=_("The SSH host to connect to"))
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
    # Change the threaded mode if available
    if args.threaded:
        """Threaded mode"""
        c.config["threaded"] = args.threaded
        logger.info(_("Threaded mode is enabled"))
    # Change the INDI web manager options if available
    try:
        if args.indihost:
            c.config["indiweb"]["host"] = args.indihost
            logger.info(_("INDI server host : {}").format(c.config["indiweb"]["host"]))
        if args.indiport:
            c.config["indiweb"]["port"] = args.indiport
            logger.info(_("INDI server port : {}").format(c.config["indiweb"]["port"]))
        if args.indidata:
            c.config["indiweb"]["data"] = args.indidata
            logger.info(_("INDI data path : {}").format(c.config["indiweb"]["data"]))
        if args.indififo:
            c.config["indiweb"]["fifo"] = args.indififo
            logger.info(_("INDI fifo pipe path : {}").format(c.config["indiweb"]["fifo"]))
        try:
            c.config["indiweb"]["config"] = os.path.join(os.environ['HOME'], '.indi')
        except KeyError:
            c.config["indiweb"]["config"] = '/tmp/indi'
    except KeyError as e:
        logger.error(_("Invalid INDI web manager options : {}").format(str(e)))
    # Start the web server
    try:
        """from server.webssh.webssh import start_webssh
        from multiprocessing import Process
        # Start the webssh server
        _webssh_ = Process(target=start_webssh)
        _webssh_.daemon = True
        _webssh_.start()"""
        # Run main web server
        from server.wsapp import async_run_server
        async_run_server()
    except KeyboardInterrupt:
        logger.info(_("Shutdown LightAPT server by user"))

if __name__ == "__main__":
    main()