import traceback
from .misc import *
import sys
from .indi_telescope import IndiTelescopeDevice
from .indi_camera import IndiCameraDevice
from .indi_focuser import IndiFocusDevice
from .indi_filter_wheel import IndiFilterWheelDevice
from .indi_common_printing import *
from .indi_device_driver_name2type import get_driver_type_by_driver_name
"""
todo, need to check how to call function by string
"""


class PyIndiWebSocketWorker:
    def __init__(self):
        self.logger = indi_logger
        self.logger.info('creating an instance of IndiClient')
        self.my_indi_client = IndiClient()
        self.my_indi_client.setServer("localhost", 7624)
        if not (self.my_indi_client.connectServer()):
            self.logger.error(
                "No indiserver running on " + self.my_indi_client.getHost() + ":" + str(self.my_indi_client.getPort()) + " - Try to run")
            self.logger.error("  indiserver ")
            sys.exit(1)
        self.telescope = None
        self.camera = None
        self.focuser = None
        self.filter_wheel = None
        self.phd2 = None

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
                self.logger.warning(traceback.format_exc())
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
            self.logger.warning(f'instruction got wrong device name {device_name}')
            return_struct['message'] = f'!error! wrong device name {device_name}'
            return return_struct

    def indi_fifo_start_device(self, device_type: str, device_name: str, start_or_stop: bool):
        """

        :param device_type:
        :param device_name:
        :param start_or_stop:
        :return: bool, true means connect success. false means connect error
        """
        self.logger.info(f'got FIFO command {start_or_stop}, {device_type}, {device_name}')
        if device_type == 'telescope':
            if start_or_stop:
                if self.telescope is not None:  # close connection if there has an existing device.
                    self.logger.info('disconnecting existing telescope...')
                    self.telescope.disconnect(self.my_indi_client)
                this_indi_device = self.my_indi_client.getDevice(device_name)
                if not (this_indi_device):
                    self.logger.error(f'Got Wrong device name {device_type} / {device_name}')
                    return False
                self.logger.info(f'connecting new device {device_type}, {device_name}')
                self.telescope = IndiTelescopeDevice(self.my_indi_client, this_indi_device)
                self.telescope.connect(self.my_indi_client)
                return True
            else:
                if self.telescope:
                    self.telescope.disconnect(self.my_indi_client)
                    self.telescope = None
                return True
        elif device_type == 'camera':
            if start_or_stop:
                if self.camera:  # close connection if there has an existing device.
                    self.logger.info('disconnecting existing camera...')
                    self.camera.disconnect(self.my_indi_client)
                this_indi_device = self.my_indi_client.getDevice(device_name)
                if not (this_indi_device):
                    self.logger.error(f'Got Wrong device name {device_type} / {device_name}')
                    return False
                self.logger.info(f'connecting new device {device_type}, {device_name}')
                self.camera = IndiCameraDevice(self.my_indi_client, this_indi_device)
                self.camera.connect(self.my_indi_client)
                self.camera.check_camera_params()
                return True
            else:
                if self.camera:
                    self.camera.disconnect(self.my_indi_client)
                    self.camera = None
                return True
        elif device_type == 'focus':
            if start_or_stop:
                if self.focuser:  # close connection if there has an existing device.
                    self.logger.info('disconnecting existing focuser...')
                    self.focuser.disconnect(self.my_indi_client)
                this_indi_device = self.my_indi_client.getDevice(device_name)
                if not (this_indi_device):
                    self.logger.error(f'Got Wrong device name {device_type} / {device_name}')
                    return False
                self.logger.info(f'connecting new device {device_type}, {device_name}')
                self.focuser = IndiFocusDevice(self.my_indi_client, this_indi_device)
                self.focuser.connect(self.my_indi_client)
                self.focuser.check_focus_param()
                return True
            else:
                if self.focuser:
                    self.focuser.disconnect(self.my_indi_client)
                    self.focuser = None
                return True
        elif device_type == 'filter':
            if start_or_stop:
                if self.filter_wheel:  # close connection if there has an existing device.
                    self.logger.info('disconnecting existing filter wheel...')
                    self.filter_wheel.disconnect(self.my_indi_client)
                this_indi_device = self.my_indi_client.getDevice(device_name)
                if not (this_indi_device):
                    self.logger.error(f'Got Wrong device name {device_type} / {device_name}')
                    return False
                self.logger.info(f'connecting new device {device_type}, {device_name}')
                self.filter_wheel = IndiFilterWheelDevice(self.my_indi_client, this_indi_device)
                self.filter_wheel.connect(self.my_indi_client)
                self.filter_wheel.check_filter_param()
                return True
            else:
                if self.filter_wheel:
                    self.filter_wheel.disconnect(self.my_indi_client)
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
