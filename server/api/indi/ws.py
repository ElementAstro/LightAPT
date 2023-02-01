import traceback
from .misc import *
import sys
from .indi_telescope import IndiTelescopeDevice
from .camera import INDICameraAPI
from .focuser import INDIFocuserAPI
from .filterwheel import IndiFilterWheelDevice
from .indi_common_printing import *
from .indi_device_driver_name2type import get_driver_type_by_driver_name
from ...logging import logger

"""
todo, need to check how to call function by string
"""


class INDIWebsocketWorker(object):
    """
        INDI Websocket Worker
    """

    def __init__(self) -> None:
        """
            Initialize a new Indi WebSocket Worker
            Args : None
            Returns : None
        """
        # Initialize the INDI CLient
        self.my_indi_client = IndiClient()

        self.camera = None
        self.telescope = None
        self.focuser = None
        self.filter_wheel = None
        self.phd2 = None

    def __del__(self) -> None:
        """
            Destroy the INDI client when the server is went down.
            Args : None
            Returns : None
        """
        if self.my_indi_client.isServerConnected():
            self.my_indi_client.disconnectServer()

    def __str__(self) -> str:
        """
            Just return a string representation of the INDI client API
        """
        return "INDI Client API"

    def connect_server(self , host = "127.0.0.1" , port = 7624) -> bool:
        """
            Connect to the INDI server using PyINDI
            Args :
                host : str # the hostname of the INDI server
                port : int # the port number of the INDI server
            Returns : None
        """
        # Bind the INDI host and port
        self.my_indi_client.setServer("localhost", 7624)
        # Connect to the INDI server
        if self.my_indi_client.isServerConnected():
            logger.warning("Server is already connected")
            return True
        if not self.my_indi_client.connectServer():
            logger.error(
                "No indiserver running on " + self.my_indi_client.getHost() + ":" + str(self.my_indi_client.getPort()) + " - Try to run")
            return False
        return True

    def disconnect_server(self) -> bool:
        """
            Disconnect INDI server and should close the device connection too?
            Args : None
            Returns : None
        """
        if not self.my_indi_client.isServerConnected():
            logger.warning("Server is not connected")
            return False
        self.my_indi_client.disconnectServer()
        logger.info("Server is disconnected successfully")
        return True

    def is_connected(self) -> bool:
        """
            Returns True if the server is connected
        """
        return {"status":self.my_indi_client.isServerConnected()}

    def do_debug_command(self, commands):
        if commands[0] == 'print':
            return self.__print_indi_command(*commands[1:])
        elif commands[0] == 'list':
            return self.__print_indi_command(*commands[1:])
        else:
            return 'wrong command! only support:\n' \
                   'print ' \
                   'list '

    def get_indi_device_by_name(self, device_type: str):
        try:
            if device_type == 'telescope':
                return self.telescope.this_device
            elif device_type == 'camera':
                return self.camera.this_device
            elif device_type == 'focus':
                return self.focuser.this_device
            elif device_type == 'filter':
                return self.filter_wheel.this_device
            else:
                return None
        except:
            raise ConnectionError

    def get_ws_device_by_name(self, device_type: str):
        if device_type == 'telescope':
            return self.telescope
        elif device_type == 'camera':
            return self.camera
        elif device_type == 'focus':
            return self.focuser
        elif device_type == 'filter':
            return self.filter_wheel
        else:
            return None

    def __print_indi_command(self, *args):
        try:
            if len(args) == 0:
                return get_str_all_device(self.my_indi_client)
            elif len(args) == 1:
                return get_str_one_device(self.my_indi_client, self.get_indi_device_by_name(args[0]))
            elif len(args) == 2:
                return get_str_one_property(self.my_indi_client, self.get_indi_device_by_name(args[0]), *args[1:])
        except ConnectionError:
            return f'wrong connection! check your input {args}'
        except:
            return traceback.format_exc()

    def __list_indi_command(self, *args):
        # list property
        pass

    async def accept_instruction(self, device_name: str, instruction: str, params: list, ws_instance=None):
        params = tuple(params)
        print(device_name, instruction, params)
        kwargs = {
            'ws_instance': ws_instance,
        }
        # todo build target info and other data structure here.
        if self.telescope:
            targe_info = await self.telescope.get_fits_file_format_data()
            if targe_info is not None:
                kwargs['target_info'] = targe_info
        return_struct = {
            'type': 'message',
            'message': '',
            'data': None,
        }
        device_accepting_command = self.get_ws_device_by_name(device_name)
        if device_accepting_command is not None:
            func = getattr(device_accepting_command, instruction)
            try:
                # do the instruction
                data = await func(*params, **kwargs)
            except Exception as e:
                # catch errors
                logger.warning(traceback.format_exc())
                return_struct['type'] = 'error'
                if len(e.args) >= 1:
                    return_struct['message'] = e.args[0]
                return return_struct
            if data is not None:
                if type(data) == dict or type(data) == list:
                    return_struct['type'] = 'data'
                    return_struct['message'] = 'see data'
                    return_struct['data'] = data
                    return return_struct
                elif type(data) == str:
                    return_struct['message'] = data
                    return return_struct
                else:
                    # if it is binary, directly return.
                    return data
            else:
                return_struct['message'] = 'success'
                return return_struct
        else:
            logger.warning(f'instruction got wrong device name {device_name}')
            return_struct['message'] = f'!error! wrong device name {device_name}'
            return return_struct

    def indi_fifo_start_device(self, device_type: str, device_name: str, start_or_stop: bool) -> bool:
        """
            Connect to the given device type and device name and return flag
            :param device_type:
            :param device_name:
            :param start_or_stop:
            :return: bool, true means connect success. false means connect error
        """
        logger.info(f'got FIFO command {start_or_stop}, {device_type}, {device_name}')
        if device_type == 'telescope':
            if start_or_stop:
                if self.telescope is not None:  # close connection if there has an existing device.
                    logger.info('disconnecting existing telescope...')
                    self.telescope.disconnect()
                this_indi_device = self.my_indi_client.getDevice(device_name)
                if not (this_indi_device):
                    logger.error(f'Got Wrong device name {device_type} / {device_name}')
                    return False
                logger.info(f'connecting new device {device_type}, {device_name}')
                self.telescope = IndiTelescopeDevice(self.my_indi_client, this_indi_device)
                self.telescope.connect()
                return True
            else:
                if self.telescope:
                    self.telescope.disconnect()
                    self.telescope = None
                return True
        elif device_type == 'camera':
            if start_or_stop:
                if self.camera:  # close connection if there has an existing device.
                    logger.info('disconnecting existing camera...')
                    self.camera.disconnect()
                this_indi_device = self.my_indi_client.getDevice(device_name)
                if not (this_indi_device):
                    logger.error(f'Got Wrong device name {device_type} / {device_name}')
                    return False
                logger.info(f'connecting new device {device_type}, {device_name}')
                self.camera = INDICameraAPI(self.my_indi_client, this_indi_device)
                self.camera.connect()
                self.camera.get_configuration()
                return True
            else:
                if self.camera:
                    self.camera.disconnect()
                    self.camera = None
                return True
        elif device_type == 'focus':
            if start_or_stop:
                if self.focuser:  # close connection if there has an existing device.
                    logger.info('disconnecting existing focuser...')
                    self.focuser.disconnect()
                this_indi_device = self.my_indi_client.getDevice(device_name)
                if not (this_indi_device):
                    logger.error(f'Got Wrong device name {device_type} / {device_name}')
                    return False
                logger.info(f'connecting new device {device_type}, {device_name}')
                self.focuser = INDIFocuserAPI(self.my_indi_client, this_indi_device)
                self.focuser.connect()
                self.focuser.check_focus_param()
                return True
            else:
                if self.focuser:
                    self.focuser.disconnect()
                    self.focuser = None
                return True
        elif device_type == 'filter':
            if start_or_stop:
                if self.filter_wheel:  # close connection if there has an existing device.
                    logger.info('disconnecting existing filter wheel...')
                    self.filter_wheel.disconnect()
                this_indi_device = self.my_indi_client.getDevice(device_name)
                if not (this_indi_device):
                    logger.error(f'Got Wrong device name {device_type} / {device_name}')
                    return False
                logger.info(f'connecting new device {device_type}, {device_name}')
                self.filter_wheel = IndiFilterWheelDevice(self.my_indi_client, this_indi_device)
                self.filter_wheel.connect()
                self.filter_wheel.check_filter_param()
                return True
            else:
                if self.filter_wheel:
                    self.filter_wheel.disconnect()
                    self.filter_wheel = None
                return True
        elif device_type == 'phd2':
            pass
        else:
            pass

    def get_all_devices(self):
        all_devices = self.my_indi_client.getDevices()
        ret_struct = []
        for one_device in all_devices:
            ret_struct.append({
                'device_name': one_device.getDeviceName(),
                'device_driver': one_device.getDriverName(),
                'device_type': get_driver_type_by_driver_name(one_device.getDriverName()),
            })
        return ret_struct
