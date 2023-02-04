# coding=utf-8

"""

Copyright(c) 2023 Gao Le

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

import json
import tornado.web
from ..api.indi.ws import INDIWebsocketWorker

indi_ws_worker = INDIWebsocketWorker()

# #################################################################
# INDI Debug 
# #################################################################

class INDIDebugWebSocket(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin: str) -> bool:
        return True

    def open(self):
        print("Debugging WS opened")

    def on_message(self, message):
        commands = message.split(' ')
        self.write_message(indi_ws_worker.do_debug_command(commands))

    def on_close(self):
        print("Debugging WSclosed")

# #################################################################
# INDI Fifo device (device start or stop)
# #################################################################

class INDIServerConnect(tornado.web.RequestHandler):
    """
        Connect to INDI server if a http request is received
    """
    async def get(self):
        self.write({"status":indi_ws_worker.connect_server()})

class INDIServerDisconnect(tornado.web.RequestHandler):
    """
        Disconnect INDI server 
    """
    async def get(self):
        self.write({"status":indi_ws_worker.disconnect_server()})

class INDIServerIsConnected(tornado.web.RequestHandler):
    """
        Check if the INDI server is connected
    """
    async def get(self):
        self.write(indi_ws_worker.is_connected())

class INDIFIFODeviceStartStop(tornado.web.RequestHandler):
    async def get(self, start_or_stop, device_type, device_name):
        # print(start_or_stop, device_type, device_name)
        if start_or_stop == 'start':
            ret_bool = indi_ws_worker.indi_fifo_start_device(device_type, device_name, True)
        elif start_or_stop == 'stop':
            ret_bool = indi_ws_worker.indi_fifo_start_device(device_type, device_name, False)
        else:
            return self.write('Wrong Command!')
        if ret_bool:
            self.write('Got!')
        else:
            self.write('Wrong device name!')

class INDIFIFOGetAllDevice(tornado.web.RequestHandler):
    async def get(self):
        all_devices = indi_ws_worker.get_all_devices()
        self.write(json.dumps(all_devices))

# #################################################################
# INDI Client
# #################################################################

class INDIClientWebSocket(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin: str) -> bool:
        return True

    def open(self):
        print("Client Instruction WS opened")

    async def on_message(self, message):
        """
        :param message:{
            device_name
            instruction
            params
        }
        :return:
        """
        command_json = json.loads(message)
        return_struct = await indi_ws_worker.accept_instruction(
            command_json['device_name'],
            command_json['instruction'],
            command_json['params'],
            self
        )
        await self.write_message(json.dumps(return_struct))

    def on_close(self):
        print("Client Instruction WS  closed")

class INDIDebugHtml(tornado.web.RequestHandler):
    """
        INDI Debug page container
    """
    def get(self):
        self.render("idebug.html")


import os
import re
import xml.etree.ElementTree as ET
from subprocess import call, check_output, getoutput
from utils.i18n import _

from ..logging import logger

class INDIDeviceContainer(object):
    """
        Device driver container
    """

    def __init__(self, name : str, label : str, version : str , binary, family, skel=None, custom=False) -> None:
        """
            Construct a new INDIDeviceContainer object
            Args :
                name : str # name of the device
                label : str # label of the device
                version : str # version of the device driver
                binary : str # binary of the device
                family : str # family of the device
                skel : str # skel of the device
                custom : bool # whether to use custom device
            Returns : None
        """
        self.name = name
        self.label = label
        self.skeleton = skel
        self.version = version
        self.binary = binary
        self.family = family
        self.custom = custom

class DeviceDriver:
    """Device driver container"""

    def __init__(self, name, label, version, binary, family, skel=None, custom=False):
        self.name = name
        self.label = label
        self.skeleton = skel
        self.version = version
        self.binary = binary
        self.family = family
        self.custom = custom


class INDIDriverCollection:
    """A collection of drivers"""

    def __init__(self, path = "/usr/share/indi") -> None:
        """
            Initialize the driver collection
            Args:
                path : str # The path to the INDi data directory
            Retruns : None
        """
        self.path = path
        self.drivers = []
        self.files = []
        self.parse_drivers()

    def parse_drivers(self) -> None:
        """
            Parse the INDI drivers
            Args:
                None
            Retruns : None
        """
        for fname in os.listdir(self.path):
            # Skip Skeleton files
            if fname.endswith('.xml') and '_sk' not in fname:
                self.files.append(os.path.join(self.path, fname))

        for fname in self.files:
            try:
                tree = ET.parse(fname)
                root = tree.getroot()

                for group in root.findall('devGroup'):
                    family = group.attrib['group']

                    for device in group.findall('device'):
                        label = device.attrib['label']
                        skel = device.attrib.get('skel', None)
                        drv = device.find('driver')
                        name = drv.attrib['name']
                        binary = drv.text
                        version = device.findtext('version', '0.0')

                        skel_file = os.path.join(self.path, skel) if skel else None
                        driver = DeviceDriver(name, label, version,
                                              binary, family, skel_file)
                        self.drivers.append(driver)

            except KeyError as e:
                logger.error("Error in file %s: attribute %s not found" % (fname, e))
            except ET.ParseError as e:
                logger.error("Error in file %s: %s" % (fname, e))

        # Sort all drivers by label
        self.drivers.sort(key=lambda x: x.label)

    def parse_custom_drivers(self, drivers : list) -> None:
        """
            Parse custom drivers
            Args:
                drivers : list of str
            Retruns : None
        """
        for custom in drivers:
            driver = DeviceDriver(custom['name'], custom['label'], custom['version'], custom['exec'],
                                  custom['family'], None, True)
            self.drivers.append(driver)

    def clear_custom_drivers(self) -> None:
        """
            Clear custom drivers
            Args:
                None
            Retruns : None
        """
        self.drivers = list(filter(lambda driver: driver.custom is not True, self.drivers))

    def get_by_label(self, label : str) -> str | None:
        """
            Get the driver by label
            Args:
                label : str
            Retruns : str | None
        """
        for driver in self.drivers:
            if driver.label == label:
                return driver
        return None

    def get_by_name(self, name : str) -> str | None:
        """
            Get the driver by name
            Args:
                name : str
            Retruns : str | None
        """
        for driver in self.drivers:
            if driver.name == name:
                return driver
        return None

    def get_by_binary(self, binary : str) -> str | None:
        """
            Get the driver by binary
            Args:
                binary : str
            Retruns : str | None
        """
        for driver in self.drivers:
            if (driver.binary == binary):
                return driver
        return None

    def get_families(self) -> dict:
        """
            Get the families
            Args:
                None
            Retruns : dict
        """
        families = {}
        for drv in self.drivers:
            if drv.family in families:
                families[drv.family].append(drv.label)
            else:
                families[drv.family] = [drv.label]
        return families

class INDIManager(object):
    """
        INDI Device Manager to replace old INDI Web Manager.
        This is just a class , the interface will be another place
    """

    def __init__(self, host = 'localhost' , port = 7624 , config_path = "" , data_path = "/usr/share/indi" , fifo_path = "/tmp/indiFIFO") -> None:
        """
            Construct a new INDI Device Manager object
            Args :
                host : str # Host of the INDI server , default is 'localhost'
                port : int # Port of the INDI server , default is 7624
                config_path : str # Configuration of the INDI server
                data_path : str # XML file containing device information , default is '/usr/share/indi'
                fifo_path : str # Fifo pipe to the INDI server , default is '/tmp/indiFIFO'
            Returns : None
        """
        self.host = host if host is not None and isinstance(host , str) else 'localhost'
        self.port = port if port is not None and isinstance(port , int) else 7624
        self.config_path = config_path if config_path is not None and isinstance(config_path , str) else ""
        self.data_path = data_path if data_path is not None and isinstance(data_path , str) else "/usr/share/indi"
        self.fifo_path = fifo_path if fifo_path is not None and isinstance(fifo_path , str) else "/tmp/indiFIFO"

        self.running_drivers = {}

    def __del__(self) -> None:
        """
            Delete the INDI Manager object
            Args : None
            Returns : None
        """

    def start_server(self) -> None:
        """
            Start the INDI server without any devices connected
            Args : None
            Returns : None
        """
        # If there is a INDI server running , just kill it
        if self.is_running():
            self.stop_server()
        # Clear the old fifo pipe and create a new one
        logger.info(_("Deleting fifo pipe at : {}").format(self.fifo_path))
        call(['rm', '-f', self.fifo_path])
        call(['mkfifo', self.fifo_path])
        # Just start the server without driver
        cmd = 'indiserver -p {} -m 100 -v -f {} > /tmp/indiserver.log 2>&1 &'.format(self.port, self.fifo_path)
        logger.debug(cmd)
        logger.info(_("Started INDI server on port {}").format(self.port))
        call(cmd, shell=True)

    def stop_server(self) -> None:
        """
            Stop all of the INDI server running
            Args : None
            Returns : None
        """
        cmd = "killall indiserver >/dev/null 2>&1"
        res = call(cmd, shell=True)
        if res == 0:
            logger.info(_("INDI server terminated successfully"))
        else:
            logger.error(_("Failed to terminate indiserver , error code is {}").format(res))

    def is_running(self) -> bool:
        """
            Check if the server is running and return True if it is running
            Args : None
            Returns : bool
        """
        if getoutput("ps -ef | grep indiserver | grep -v grep | wc -l") != "0":
            return True
        return False

    def start_driver(self, driver : INDIDeviceContainer) -> None:
        """
            Start a driver and send the command to the server via FIFO connection
            Args : 
                driver : INDIDeviceContainer object
            Returns : None
        """
        cmd = 'start %s' % driver.binary

        if driver.skeleton:
            cmd += ' -s "%s"' % driver.skeleton

        cmd = cmd.replace('"', '\\"')
        full_cmd = 'echo "%s" > %s' % (cmd, self.fifo_path)
        logger.debug(full_cmd)
        call(full_cmd, shell=True)
        logger.info(_("Started driver : {}").format(driver.name))

        self.running_drivers[driver.label] = driver

    def stop_driver(self, driver : INDIDeviceContainer) -> None:
        """
            Stop a driver and send the command to the server via FIFO connection
            Args : 
                driver : INDIDeviceContainer object
            Returns : None
        """
        cmd = 'stop %s' % driver.binary

        if "@" not in driver.binary:
            cmd += ' -n "%s"' % driver.label
        cmd = cmd.replace('"', '\\"')
        full_cmd = 'echo "%s" > %s' % (cmd, self.fifo_path)
        logger.debug(full_cmd)
        call(full_cmd, shell=True)
        logger.info(_("Stop running driver : {}").format(driver.label))

        del self.running_drivers[driver.label]

    def set_prop(self, dev : str, prop : str, element : str, value : str) -> None:
        """
            Set a property of a device
            Args : 
                dev : str # name of the device
                prop : str # name of the property
                element : str # name of the element
                value : str # value of the property
            Returns : None
        """
        cmd = ['indi_setprop', '%s.%s.%s=%s' % (dev, prop, element, value)]
        call(cmd)

    def get_prop(self, dev : str, prop : str, element : str) -> bytes:
        """
            Get a property of a device
            Args : 
                dev : str # name of the device
                prop : str # name of the property
                element : str # name of the element
            Returns : bytes
        """
        cmd = ['indi_getprop', '%s.%s.%s' % (dev, prop, element)]
        output = check_output(cmd)
        return output.split('=')[1].strip()

    def get_state(self, dev : str, prop : str) -> bytes:
        """
            Get a property of a device
            Args : 
                dev : str # name of the device
                prop : str # name of the property
            Returns : bytes
        """
        return self.get_prop(dev, prop, '_STATE')

    def get_running_drivers(self) -> dict:
        """
            Get all running drivers
            Args : None
            Returns : dict
        """
        return self.running_drivers

    @staticmethod
    def get_devices() -> list:
        """
            Get a list of devices
            Args: None
            Returns:
                list: A list of devices
        """
        cmd = ['indi_getprop', '*.CONNECTION.CONNECT']
        try:
            output = check_output(cmd).decode('utf_8')
            lines = re.split(r'[\n=]', output)
            output = {lines[i]: lines[i + 1] for i in range(0, len(lines) - 1, 2)}
            devices = []
            for key, val in output.items():
                device_name = re.match("[^.]*", key)
                devices.append({"device": device_name.group(), "connected": val == "On"})
            return devices
        except Exception as e:
            logger.error(e)

import json

import server.config as c

from utils.utility import switch

indi_server = INDIManager()
indi_collection = INDIDriverCollection(c.config.get('indiweb',{}).get('data',"/usr/share/indi"))
