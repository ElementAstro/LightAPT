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
import socket
import threading
from time import sleep
import time
from server.basic.guider import TcpSocket
from utils.i18n import _
from utils.utility import switch
from ...logging import logger,return_error,return_success,return_warning

class SETTLE(object):
    """
        Settle data structure
    """
    pixels = 0
    time = 10
    timeout = 60

    def get_dict(self) -> dict:
        return {
            "pixels": self.pixels,
            "time": self.time,
            "timeout": self.timeout
        }

class CalibrationModel(object):
    """
        Calibration models for calibration
    """
    xAngle : float
    xRate : float
    xParity : float
    yAngle : float
    yRate : float
    yParity : float
    
    def get_dict(self) -> dict:
        return {
            'xAngle': self.xAngle,
            'xRate': self.xRate,
            'xParity': self.xParity,
            'yAngle': self.yAngle,
            'yRate': self.yRate,
            'yParity': self.yParity,
        }

class CoolingModel(object):
    """
        Cooling models for cooling
    """
    _temperature : float
    _is_cooling : bool
    _target_temperature : float
    _cooling_power : float

    def get_dict(self) -> dict:
        return {
            "temperature": self._temperature,
            "is_cooling": self._is_cooling,
            "target_temperature": self._target_temperature,
            "cooling_power": self._cooling_power,
        }

class EquipmentModel(object):
    """
        Equipment models for equipment
    """
    _camera_name : str
    _is_camera_connected = False

    _mount_name : str
    _is_mount_connected = False

    _aux_mount_name : str
    _is_aux_mount_connected = False

    _ao_name : str
    _is_ao_connected = False

    def get_dict(self) -> dict:
        return {
            "camera" : {
                "name" : self._camera_name,
                "is_connected" : self._is_camera_connected,
            },
            "mount" : {
                "name" : self._mount_name,
                "is_connected" : self._is_mount_connected,
            },
            "aux_mount" : {
                "name" : self._aux_mount_name,
                "is_connected" : self._is_aux_mount_connected,
            },
            "ao" : {
                "name" : self._ao_name,
                "is_connected" : self._is_ao_connected,
            }
        }

class CalibrationStatus(object):
    """
        Calibration status container
    """
    _model = CalibrationModel()
    _direction : str   # calibration direction (phase)
    _distance : float  # distance from starting location
    _dx : float    # x offset from starting position
    _dy : float    # y offset from starting position
    _position = [] # star coordinates
    _step : int # step number
    _state : str   # calibration status message
    _flip : bool # flip calibration data

    def get_dict(self) -> dict:
        return {
            "model": self._model.get_dict(),
            "direction": self._direction,
            "distance": self._distance,
            "dx": self._dx,
            "dy": self._dy,
            "position": self._position,
            "step": self._step,
            "state": self._state,
            "flip": self._flip
        }

class GuidingStatus(object):
    """
        Guiding status container
    """
    _frame : int # The frame number; starts at 1 each time guiding starts
    _time : int # the time in seconds, including fractional seconds, since guiding started
    _last_error = 0 # error code
    _output_enabled : bool # whether output is enabled
    _dec_guide_mode : str # the guide mode of DEC axis

    _dx : float # the X-offset in pixels
    _dy : float # the Y-offset in pixels

    _average_distance : float # a smoothed average of the guide distance in pixels

    _ra_raw_distance : float # the RA distance in pixels of the guide offset vector
    _dec_raw_distance : float # the DEC distance in pixels of the guide offset vector
    _ra_distance : float # the guide algorithm-modified RA distance in pixels of the guide offset vector
    _dec_distance : float # the guide algorithm-modified DEC distance in pixels of the guide offset vector
    
    _ra_duration : float # the RA guide pulse duration in milliseconds
    _dec_duration : float # the DEC guide pulse duration in milliseconds

    _ra_direction : str # "East" or "West"
    _dec_direction : str # "North" or "South"

    _ra_limited : bool # true if step was limited by the Max RA setting (attribute omitted if step was not limited)
    _dec_limited : bool # true if step was limited by the Max DEC setting (attribute omitted if step was not limited)
    
    _pixel_scale : float
    _search_region : float
    _starmass : float # the Star Mass value of the guide star
    _snr : float # the computed Signal-to-noise ratio of the guide star
    _hfd : float # the guide star half-flux diameter (HFD) in pixels
    
    def get_dict(self) -> dict:
        return {
            "frame" : self._frame,
            "time" : time.asctime( time.localtime(time.time()) ),
            "last_error" : self._last_error,
            "output_enabled" : self._output_enabled,
            "dec_guide_mode" : self._dec_guide_mode,
            "dx" : self._dx,
            "dy" : self._dy,
            "average_distance" : self._average_distance,
            "ra" : {
                "raw_distance" : self._ra_raw_distance,
                "distance" : self._ra_distance,
                "duration" : self._ra_duration,
                "direction" : self._ra_direction,
                "limited" : self._ra_limited,
            },
            "dec" : {
                "raw_distance" : self._dec_raw_distance,
                "distance" : self._dec_distance,
                "duration" : self._dec_duration,
                "direction" : self._dec_direction,
                "limited" : self._dec_limited,
            },
            "image" : {
                "starmass" : self._starmass,
                "snr" : self._snr,
                "hfd" : self._hfd,
                "pixel_scale" : self._pixel_scale,
            }
        }

class ImageInfo(object):
    """
        Image information container
    """
    _frame : int
    _height : int
    _width : int
    _star_pos : list
    _image : str

    def get_dict(self) -> dict:
        return {
            "frame" : self._frame,
            "height" : self._height,
            "width" : self._width,
            "star_pos" : self._star_pos,
            "image" : self._image,
        }

class PHD2Info(object):
    """
        PHD2 Guiding Information Container
    """

    _version = ""
    _subversion = ""
    _msgversion = ""

    _is_server_connected = False
    _is_device_connected = False

    _profile_list = [] # list of profiles available
    _current_profile_id = None
    _current_equipments = {}

    _can_cooling = False

    _exposure = 500
    _exposure_durations = []

    _is_calibrated = False
    _is_guiding = False
    _is_calibrating = False
    _is_looping = False
    _is_settling = False
    _is_selected = True
    _is_starlocklost = True

    _cooling_model = CoolingModel()

    _equipment_model = EquipmentModel()

    _g_status = GuidingStatus()

    _c_status = CalibrationStatus()

    _image = ImageInfo()

    _settle_distance : float
    _settle_time : float
    _settle_star_locked : bool
    _settle_total_frame : int
    _settle_drop_frame : int

    _lock_position_x : int
    _lock_position_y : int
    _lock_shift_enabled : bool

    _star_selected_x : int   # lock position X-coordinate
    _star_selected_y : int # lock position Y-coordinate

    _dither_dx : float # the dither X-offset in pixels
    _dither_dy : float # the dither Y-offset in pixels

    _starlost_snr : float
    _starlost_starmass : float
    _starlost_avgdist : float

    def get_dict(self) -> dict:
        """
            Return PHD2 infomation in a dict
        """
        return {
            "version" : self._version,
            "subversion" : self._subversion,
            "msgversion" : self._msgversion,
            "profiles" : self._profile_list,
            "profile_id" : self._current_profile_id,
            "mount" : self._mount,
            "frame" : self._frame,
            "exposure" : self._exposure,
            "subframe" : self._subframe,
            "cooling_model" : self._cooling_model.get_dict(),
            "equipment_model" : self._equipment_model.get_dict(),
            "g_status" : self._g_status.get_dict(),
            "c_status" : self._c_status.get_dict(),
            "image" : self._image.get_dict(),
            "settle_distance" : self._settle_distance,
            "settle_time" : self._settle_time,
            "settle_star_locked" : self._settle_star_locked,
            "settle_total_frame" : self._settle_total_frame,
            "lock_position_x" : self._lock_position_x,
            "lock_position_y" : self._lock_position_y,
            "lock_shift_enabled" : self._lock_shift_enabled,
            "star_selected_x" : self._star_selected_x,
            "star_selected_y" : self._star_selected_y,
            "dither_dx" : self._dither_dx,
            "dither_dy" : self._dither_dy,
            "starlost_snr" : self._starlost_snr,
            "starlost_starmass" : self._starlost_starmass,
            "starlost_avgdist" : self._starlost_avgdist,
        }

class PHD2API(object):
    """
        PHD2 Guider API for LightAPT
    """

    def __init__(self) -> None:
        """
            Initialize the PHD2 API object
            Args : None
            Returns : None
        """
        self.conn = TcpSocket()
        self.terminate = False
        self._background_task = None
        self.info = PHD2Info()
        self.response = None
        self.lock = threading.Lock()
        self.cond = threading.Condition()

    def __del__(self) -> None:
        """
            Delete the PHD2 API object
            Args : None
            Returns : None
        """

    async def connect_server(self , host = "127.0.0.1" , port = 4400) -> dict:
        """
            Connect to the PHD2 server without connecting to the devices
            Args :
                host : str # default host is '127.0.0.1'
                port : int # default port is 4400
            Returns : dict
        """
        # TODO : Use a decorator to replace such a stupid way
        if self.info._is_server_connected:
            return return_error(_("PHD2 server is connected"))

        # Check if the parameters are valid
        if not isinstance(host, str) or not isinstance(port, int):
            return return_error(_("Invalid host or port specified"))

        try:
            self.conn.connect(host, port)
            self.terminate = False
            self.info._is_server_connected = True
            # Start a standalone thread to listen to the PHD2 server
            self._background_task = threading.Thread(target=self.background_task)
            self._background_task.start()
        except OSError as e:
            return return_error(_("Failed to connect to PHD2 server"),{"error" :e})

        return return_success(_("Connected to PHD2 server successfully"),{})

    async def disconnect_server(self) -> dict:
        """
            Disconnects from PHD2 server and do not disconnect the devices
            Args : None
            Returns : dict
        """
        if not self.info._is_server_connected:
            return return_warning(_("PHD2 server is not connected"))
        # Close the socket connection
        self.conn.disconnect()
        self.info._is_server_connected = False
        # Terminate the background thread
        self.terminate = True

        return return_success(_("Disconnect from PHD2 successfully"),{})

    async def reconnect(self) -> dict:
        """
            Reconnect to PHD server and will not change the devices
            Args : None
            Returns : None
            This function is more like a wrapper around the connect() method and disconnect() method
        """
        if not self.info._is_server_connected:
            return return_warning(_("PHD2 server is not connected"))
        # Terminate the background thread first
        self.terminate = True
        # Close the socket connection
        self.conn.disconnect()
        # Wait for a moment
        sleep(1)
        # Then reconnect to the server
        self.conn.connect()
        self.info._is_server_connected = True
        # Restart the background thread
        self.terminate = False
        self._background_task = threading.Thread(target=self.background_task)
        self._background_task.start()
        
        return return_success(_("Reconnecting to PHD2 successfully"),{})

    async def scanning_server(self , host = "127.0.0.1" , start_port = 4400 , end_port = 4406) -> dict:
        """
            Scan the server listening on the given port range , and return a list of the available servers if found.
            Args :
                host : str # default host is "127.0.0.1"
                start_port : int # start of the range
                end_port : int # end of the range
            Returns : dict
                list : list of servers port
        """
        if not isinstance(start_port, int) or not isinstance(end_port, int):
            return return_error(_("Invalid start_port or end_port specified"))
        logger.info(_("Start scanning PHD2 server on port from {} to {} ...").format(start_port, end_port))
        guider_list = []
        for port in range(start_port,end_port+1):
            # Try to connect to the specified port
            try:
                connSkt = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
                connSkt.connect((host,port))
                logger.info(_("Found socket port open on {}").format(port))
                guider_list.append(port)
            except socket.error:
                pass
        if len(guider_list) == 0:
            return return_error(_("No PHD2 server found"),{})

        return return_success(_("Found PHD2 server"),{"list" : guider_list})

    async def shutdown_server(self) -> dict:
        """
            Shutdown the server
            Args : None
            Returns : dict
            NOTE : After this command , we will stop all of the guiding processes
        """
        if not self.info._is_server_connected:
            return return_error(_("PHD2 server is not connected"))

        command = await self.generate_command("shutdown",{})
        try:
            res = await self.send_command(command)
        except socket.error as e:
            return return_error(_("Failed to send shutdown command to PHD2 server"),{"error":e})

        if "error" in res:
            return return_error(_("Shutdown PHD2 server error"),{"error":res.get('error')})

        return return_success(_("Shutdown PHD2 server successfully"),{})

    # #################################################################
    # Listen and progress messages from PHD2 server
    # #################################################################

    def background_task(self) -> None:
        """
            Background task listen server message | 获取PHD2信息
            Args : None
            Returns : None
        """
        while not self.terminate:
            line = self.conn.read()
            if not line and not self.terminate:
                break
            try:
                j = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "jsonrpc" in j:
                with self.cond:
                    self.response = j
                    self.cond.notify()
            else:
                asyncio.run(self.parser_json(j))

    async def generate_command(self, command : str, params : dict) -> dict:
        """
            Generate command to send to the PHD2 server
            Args:
                command : str
                params : dict
            Returns : dict
        """
        res = {
            "method": command,
            "id" : 1
        }
        if params is not None:
            if isinstance(params, (list, dict)):
                res["params"] = params
            else:
                res["params"] = [ params ]
        return res

    async def send_command(self, command : dict) -> dict:
        """
            Send command to the PHD2 server
            Args:
                command : dict
            Returns : bool
        """
        r = json.dumps(command,separators=(',', ':'))
        self.conn.send(r + "\r\n")
        # wait for response
        with self.cond:
            while not self.response:
                self.cond.wait()
            response = self.response
            self.response = None
        if "error" in response:
            logger.error(_("Guiding Error : {})").format(response.get('error').get('message')))
        return response

    async def parser_json(self,message) -> None:
        """
            Parser the JSON message received from the server
            Args : message : JSON message
            Returns : None
        """
        if message is None:
            return

        event = message.get('Event')

        for case in switch(event):
            if case("Version"):
                await self._version(message)
                break
            if case("LockPositionSet"):
                await self._lock_position_set(message)
                break
            if case("Calibrating"):
                await self._calibrating(message)
                break
            if case("CalibrationComplete"):
                await self._calibration_completed(message)
                break
            if case("StarSelected"):
                await self._star_selected(message)
                break
            if case("StartGuiding"):
                await self._start_guiding()
                break
            if case("Paused"):
                self._paused()
                break
            if case("StartCalibration"):
                await self._start_calibration(message)
                break
            if case("AppState"):
                await self._app_state(message)
                break
            if case("CalibrationFailed"):
                await self._calibration_failed(message)
                break
            if case("CalibrationDataFlipped"):
                await self._calibration_data_flipped(message)
                break
            if case("LockPositionShiftLimitReached"):
                await self._lock_position_shift_limit_reached()
                break
            if case("LoopingExposures"):
                await self._looping_exposures(message)
                break
            if case("LoopingExposuresStopped"):
                await self._looping_exposures_stopped()
                break
            if case("SettleBegin"):
                await self._settle_begin()
                break
            if case("Settling"):
                await self._settling(message)
                break
            if case("SettleDone"):
                await self._settle_done(message)
                break
            if case("StarLost"):
                await self._star_lost(message)
                break
            if case("GuidingStopped"):
                await self._guiding_stopped()
                break
            if case("Resumed"):
                await self._resumed()
                break
            if case("GuideStep"):
                await self._guide_step(message)
                break
            if case("GuidingDithered"):
                await self._guiding_dithered(message)
                break
            if case("LockPositionLost"):
                await self._lock_position_lost()
                break
            if case("Alert"):
                await self._alert(message)
                break
            if case("GuideParamChange"):
                await self._guide_param_change(message)
                break
            if case("ConfigurationChange"):
                await self._configuration_change()
                break
            logger.error(_(f"Unknown event : {event}"))
            break

    # #################################################################
    # Get the profiles in server and set one of them to connect to
    # #################################################################

    async def get_profiles(self) -> dict:
        """
            Get all of the profiles in the server and return a list of the profiles names
            Args : None
            Returns : dict
                list : list # a list of profiles name
        """
        if not self.info._is_server_connected:
            return return_error(_("PHD2 server is not connected"))

        command = await self.generate_command("get_profiles",{})
        try:
            res = await self.send_command(command)
        except socket.error as e:
            return return_error(_("Failed to send command to PHD2 server"),{"error":e})

        if "error" in res:
            return return_error(_("Get PHD2 profile error"),{"error":res.get('error')})

        self.info._profile_list = res.get("result")
        logger.debug(_("All of the profile : {}").format(res.get('result')))
        return return_success(_("Get profiles successfully"),{"list":res.get('result')})

    async def get_current_profile(self) -> dict:
        """
            Get the current profile selected
            Args : None
            Returns : None
                profile : dict
                    id : int
                    name : str
        """
        command = await self.generate_command("get_profile",{})
        try:
            res = await self.send_command(command)
        except socket.error as e:
            return return_error(_("Failed to send command to PHD2 server"),{"error":e})

        if "error" in res:
            return return_error(_("Get PHD2 profile error"),{"error":res.get('error')})

        self.info._profile_list = res.get("result")
        self.info._current_profile_id = res.get('result').get('id')
        logger.debug(_("Current profile : {}").format(res.get('result')))
        return return_success(_("Get current profiles successfully"),{"list":res.get('result')})

    async def set_profile(self, profile_id = 1) -> dict:
        """
            Set the profile id , the same as what we get from the server
            Args :
                profile_id : int # the profile id 
            Returns : dict
        """
        if not isinstance(profile_id, int):
            return return_error(_("Profile id must be an integer"))

        command = await self.generate_command("set_profile",[profile_id])
        try:
            res = await self.send_command(command)
        except socket.error as e:
            return return_error(_("Failed to send set_profile command to server"),{"error":e})
        if "error" in res:
            return return_error(_("Failed to set the server profile"),{"error":res.get("error")})

        self.info._current_profile_id = profile_id
        return return_success(_("Set profile successfully"),{"profile_id":profile_id})

    async def connect_device(self) -> dict:
        """
            Connect to the device in current profile
            Args : None
            Returns : dict
            NOTE : This function is not required any parameters , so you need to set the profile you want 
                    before calling this function
        """
        if self.info._current_profile_id is None:
            return_error(_("No profile specified"),{})

        command = await self.generate_command("set_connected",True)
        try:
            res = await self.send_command(command)
        except socket.error as e:
            return return_error(_("Failed to send set device connect command to server"),{"error":e})
        if "error" in res:
            return return_error(_("PHD2 connect to device failed"),{"error":res.get('error')})
        self.info._is_device_connected = True
        return return_success(_("PHD2 connected to devices successfully"))

    async def disconnect_device(self) -> dict:
        """
            Let PHD2 server disconnect the device
            Args : None
            Returns : dict
        """
        if not self.info._is_device_connected:
            return return_error(_("PHD2 device is not connected"))

        command = await self.generate_command("set_connected",False)
        try:
            res = await self.send_command(command)
        except socket.error as e:
            return return_error(_("Failed to send set device disconnect command to server"),{"error":e})
        if "error" in res:
            return return_error(_("PHD2 disconnect with device failed"),{"error":res.get('error')})
        self.info._is_device_connected = True
        return return_success(_("PHD2 disconnected with devices successfully"))

    async def get_connected(self) -> dict:
        """
            Get the connected status of the device
            Args : None
            Returns : dict
                "status" : bool
        """
        if not self.info._is_device_connected:
            return return_error(_("PHD2 device is not connected"))

        command = await self.generate_command("get_connected",{})
        try:
            res = await self.send_command(command)
        except socket.error as e:
            return return_error(_("Failed to send get connected status of the device command to server"),{"error":e})
        if "error" in res:
            return return_error(_("Get connected status of the device failed"),{"error":res.get('error')})
        result = res.get('result')
        return return_success(_("Get connected status of the device"),{"status":result})

    # #################################################################
    # Get/Set the parameters about the exposure
    # #################################################################

    async def get_exposure(self) -> dict:
        """
            Get the current exposure value
            Args : None
            Returns : dict
        """
        if not self.info._is_device_connected:
            return return_error(_("PHD2 device is not connected"))

        command = await self.generate_command("get_exposure",{})
        try:
            res = await self.send_command(command)
        except socket.error as e:
            return return_error(_("Failed to send get exposure command to server"),{"error":e})

        exposure = res.get('result')
        self.info._exposure = exposure

        return return_success(_("Current exposure : {}").format(exposure),{"exposure":exposure})

    async def get_exposure_durations(self) -> dict:
        """
            Get the available exposure durations
            Args : None
            Returns : dict
                durations : list
        """
        if not self.info._is_device_connected:
            return return_error(_("PHD2 device is not connected"))

        command = await self.generate_command("get_exposure_durations",{})
        try:
            res = await self.send_command(command)
        except socket.error as e:
            return return_error(_("Failed to send get exposure durations command to server"),{"error":e})

        exposure_durations = res.get('result')
        self.info._exposure_durations = exposure_durations

        return return_success(_("Exposure durations : {}").format(exposure_durations),{"durations":exposure_durations})


    async def set_exposure(self , exposure : int) -> dict:
        """
            Set the exposure value of the guiding camera
            Args :
                exposure : int # milliseconds
            Returns : dict
        """
        if not self.info._is_device_connected:
            return return_error(_("PHD2 device is not connected"))

        if exposure is None or not isinstance(exposure,int):
            return return_error(_("Invalid exposure value is specified"))

        command = await self.generate_command("set_exposure",exposure)
        try:
            await self.send_command(command)
        except socket.error as e:
            return return_error(_("Failed to send set exposure command to server"),{"error":e})

        await asyncio.sleep(0.5)

        res = await self.get_exposure()
        if res.get('status') == 0 and res.get('params',{}).get('exposure') == exposure:
            return return_success(_("Set exposure value successfully"))
        return return_error(_("Failed to set exposure value"),{"error" : res.get('params',{}).get('error')})

    # #################################################################
    # Get the current equipments
    # #################################################################

    async def get_current_equipment(self) -> dict:
        """
            Get the current equipments and just return them in a dictionary
            Args : None
            Returns : dict
                info : equipment infomation
            Data example:
                example: {
                    "camera":{
                        "name":"Simulator",
                        "connected":true
                    },
                    "mount":{
                        "name":"On Camera",
                        "connected":true
                    },
                    "aux_mount":{
                        "name":"Simulator",
                        "connected":true
                    },
                    "AO":{
                        "name":"AO-Simulator",
                        "connected":false
                    },
                    "rotator":{
                        "name":"Rotator Simulator .NET (ASCOM)",
                        "connected":false
                    }
                }
        """
        if not self.info._is_device_connected:
            return return_error(_("PHD2 device is not connected"))

        command = await self.generate_command("get_current_equipment",{})
        try:
            res = await self.send_command(command)
        except socket.error as e:
            return return_error(_("Failed to send get current equipment command to server"),{"error":e})

        equipments = res.get('result')
        self.get_current_equipment = equipments
        return return_success(_("Get current equipment successfully"),{"result":equipments})

    # #################################################################
    # Get the current camera information
    # #################################################################

    async def get_camera_frame_size(self) -> dict:
        """
            Get the current camera frame size
            Args : None
            Returns : None
        """
        if not self.info._is_device_connected:
            return return_error(_("PHD2 device is not connected"))

        command = await self.generate_command("get_camera_frame_size",{})
        try:
            res = await self.send_command(command)
        except socket.error as e:
            return return_error(_("Failed to send get camera frame size to server"),{"error":e})
        if "error" in res:
            return return_error(_("PHD2 get_camera_frame_size error"),{"error":res.get('error')})
        result = res.get('result')
        logger.debug(_(f"Current camera frame : [{result[0]},{result[1]}]"))
        return return_success(_("PHD2 get_camera_frame_size successfully"),{"width":result[0],"height":result[1]})
    
    async def get_camera_cooler_status(self) -> dict:
        """
            Get the status of the camera cooling
            Args : None
            Returns : dict
            NOTE : This function needs camera supported
            Data structure:	
                "temperature": sensor temperature in degrees C (number), 
                "coolerOn": boolean, 
                "setpoint": cooler set-point temperature (number, degrees C), 
                "power": cooler power (number, percent)
        """
        if not self.info._is_device_connected:
            return return_error(_("PHD2 device is not connected"))

        command = await self.generate_command("get_cooler_status",{})
        try:
            res = await self.send_command(command)
        except socket.error as e:
            return return_error(_("Failed to send get cooler status command to server"),{"error":e})
        if "error" in res:
            logger.error(_(f"Get cooler status error : {res.get('error')}"))
            self.info._can_cooling = False
            return return_error(_("Get cooler status error"),{"error":res.get('error')})
        result = res.get("result")
        self.info._can_cooling = True
        return return_success(_("Get cooler status successfully"),{"result":result})

    async def get_camera_pixel_size(self) -> dict:
        """
            Get the pixel size of the camera
            Args : None
            Returns : dict
                pixel_size : float
        """
        if not self.info._is_device_connected:
            return return_error(_("PHD2 device is not connected"))

        command = await self.generate_command("get_pixel_scale",{})
        try:
            res = await self.send_command(command)
        except socket.error as e:
            return return_error(_("Failed to send get pixel size command to server"),{"error":e})
        if "error" in res:
            return return_error(_("Get pixel size error"),{"error":res.get('error')})
        result = res.get("result")
        return return_success(_("Get pixel size successfully"),{"result":result})

    async def get_camera_temperature(self) -> dict:
        """
            Get the temperature of the camera
            Args : None
            Returns : dict
                temperature : float
        """
        if not self.info._is_device_connected:
            return return_error(_("PHD2 device is not connected"))

        command = await self.generate_command("get_ccd_temperature",{})
        try:
            res = await self.send_command(command)
        except socket.error as e:
            return return_error(_("Failed to send get temperature command to server"),{"error":e})
        if "error" in res:
            return return_error(_("Get temperature error"),{"error":res.get('error')})
        result = res.get("result")
        return return_success(_("Get temperature successfully"),{"result":result})

    async def get_camera_subframe(self) -> dict:
        """
            Get the camera subframe
            Args : None
            Returns : dict
                enable : bool
        """
        if not self.info._is_device_connected:
            return return_error(_("PHD2 device is not connected"))

        command = await self.generate_command("get_use_subframes",{})
        try:
            res = await self.send_command(command)
        except socket.error as e:
            return return_error(_("Failed to send get camera subframe command to server"),{"error":e})
        if "error" in res:
            return return_error(_("Get if the camera use subframe error"),{"error":res.get('error')})
        result = res.get("result")
        return return_success(_("Get if the camera use subframe successfully"),{"enable":result})

    # #################################################################
    # Calibration
    # #################################################################

    async def get_calibration_data(self) -> dict:
        """
            Get the calibration data of the telescope
            Args : None
            Returns : dict
                data : dict
            Data example:
                "calibrated":true,
                "xAngle":-167.1,
                "xRate":39.124,
                "xParity":"-",
                "yAngle":106.1,
                "yRate":39.330,
                "yParity":"+"
        """
        if not self.info._is_device_connected:
            return return_error(_("PHD2 device is not connected"))

        command = await self.generate_command("get_calibration_data",{})
        try:
            res = await self.send_command(command)
        except socket.error as e:
            return return_error(_("Failed to send get calibration data command to server"),{"error":e})
        if "error" in res:
            return return_error(_("Get calibration data error"),{"error":res.get('error')})
        result = res.get("result")
        return return_success(_("Get calibration data successfully"),{"data":result})

    async def clear_calibration_data(self) -> dict:
        """
            Clear calibration data of the current calibration
            Args : None
            Returns : dict
        """
        if not self.info._is_device_connected:
            return return_error(_("PHD2 device is not connected"))

        command = await self.generate_command("clear_calibration",{})
        try:
            res = await self.send_command(command)
        except socket.error as e:
            return return_error(_("Failed to send clear calibration data command to server"),{"error":e})
        if "error" in res:
            return return_error(_("Clear calibration data error"),{"error":res.get('error')})
        return return_success(_("Clear calibration data successfully"),{})

    async def flip_calibration_data(self) -> dict:
        """
            Flip the calibration data
            Args : None
            Returns : dict
        """
        if not self.info._is_device_connected:
            return return_error(_("PHD2 device is not connected"))

        command = await self.generate_command("flip_calibration",{})
        try:
            res = await self.send_command(command)
        except socket.error as e:
            return return_error(_("Failed to send flip calibration data command to server"),{"error":e})
        if "error" in res:
            return return_error(_("Flip calibration data error"),{"error":res.get('error')})
        return return_success(_("Flip calibration data successfully"),{})

    async def get_calibrated(self) -> dict:
        """
            Get if the calibration had already done
            Args : None
            Returns : dict
                "status" : bool
        """
        if not self.info._is_device_connected:
            return return_error(_("PHD2 device is not connected"))

        command = await self.generate_command("get_calibrated",{})
        try:
            res = await self.send_command(command)
        except socket.error as e:
            return return_error(_("Failed to send get calibratid command to server"),{"error":e})
        if "error" in res:
            return return_error(_("Get calibration status error"),{"error":res.get('error')})
        return return_success(_("Get calibration status successfully"),{"status" : res.get("result")})

    # #################################################################
    # Guiding
    # #################################################################

    async def start_guiding(self,settle : SETTLE,recalibrate : bool,roi : list) -> dict:
        """
            Start guiding 
            Args :
                settle : SETTLE
                recalibrate : bool # whether to recalibrate the telescope before starting guiding
                roi : list # [x,y,width,height],default is full roi
            Returns : dict
        """
        if not self.info._is_device_connected:
            return return_error(_("PHD2 device is not connected"))
        
        if not isinstance(recalibrate,bool) or not isinstance(roi,list):
            return return_error(_("Invalid guiding parameters"))

        command = await self.generate_command("guide",{"settle" : settle.get_dict(),"recalibrate": recalibrate})
        try:
            res = await self.send_command(command)
        except socket.error as e:
            return return_error(_("Failed to send start guiding command to server"),{"error":e})
        if "error" in res:
            return return_error(_("Started guiding error"),{"error":res.get('error')})
        return return_success(_("Started guiding successfully"),{})

    async def stop_guiding(self) -> dict:
        """
            Stop guiding process but keep looping
            Args : None
            Returns : dict
        """
        if not self.info._is_device_connected:
            return return_error(_("PHD2 device is not connected"))

        command = await self.generate_command("set_paused",[True])
        try:
            res = await self.send_command(command)
        except socket.error as e:
            return return_error(_("Failed to send stop guiding command to server"),{"error":e})
        if "error" in res:
            return return_error(_("Stopped guiding error"),{"error":res.get('error')})
        return return_success(_("Stopped guiding successfully"),{})

    async def start_looping(self) -> dict:
        """
            Start looping
            Args : None
            Returns : dict
        """
        if not self.info._is_device_connected:
            return return_error(_("PHD2 device is not connected"))

        command = await self.generate_command("loop",[True])
        try:
            res = await self.send_command(command)
        except socket.error as e:
            return return_error(_("Failed to send start looping command to server"),{"error":e})
        if "error" in res:
            return return_error(_("Started looping error"),{"error":res.get('error')})
        return return_success(_("Started looping successfully"),{})

    async def stop_looping(self) -> dict:
        """
            Stop looping capture
            Args : None
            Returns : dict
        """
        if not self.info._is_device_connected:
            return return_error(_("PHD2 device is not connected"))

        command = await self.generate_command("set_paused",[True,"full"])
        try:
            res = await self.send_command(command)
        except socket.error as e:
            return return_error(_("Failed to send stop looping command to server"),{"error":e})
        if "error" in res:
            return return_error(_("Stopped looping error"),{"error":res.get('error')})
        return return_success(_("Stopped looping successfully"),{})

    async def start_dither(self,settle : SETTLE,raonly : bool,amount : float) -> dict:
        """
            Start dither
            Args : 
                settle : SETTLE
                raonly : bool # default is False
                amount : float # amount in pixels
            Returns : dict
        """
        if not self.info._is_device_connected:
            return return_error(_("PHD2 device is not connected"))

        if self.info._is_settling:
            return return_error(_("PHD2 device is settling"))
        
        if not isinstance(amount,float) or not isinstance(raonly,bool):
            return return_error(_("Invalid amount or raonly parameter is specified"))

        command = await self.generate_command("dither",{"settle":settle.get_dict(),"amount":amount,"raOnly":raonly})
        try:
            res = await self.send_command(command)
        except socket.error as e:
            return return_error(_("Failed to send dither command to server"),{"error":e})
        if "error" in res:
            return return_error(_("Dither error"),{"error":res.get('error')})
        return return_success(_("Started dither successfully"),{})

    async def get_image(self) -> dict:
        """
            Get the latest image
            Args : None
            Returns : dict
            	frame : int # frame number
                width : int # width of the image
                height : int # height of the image
                image : str # base64 encoded image
                star_position : list # star position
        """
        if not self.info._is_device_connected:
            return return_error(_("PHD2 device is not connected"))

        command = await self.generate_command("get_star_image",{})
        try:
            res = await self.send_command(command)
        except socket.error as e:
            return return_error(_("Failed to send get image data command to server"),{"error":e})
        if "error" in res:
            return return_error(_("Get image data error"),{"error":res.get('error')})
        result = res.get("result")
        return return_success(_("Get image data successfully"),{"data":result})

    async def save_image(self) -> dict:
        """
            Save the current image to a specified location
            Args : None
            Returns : dict
        """
        if not self.info._is_device_connected:
            return return_error(_("PHD2 device is not connected"))

        command = await self.generate_command("save_image",{})
        try:
            res = await self.send_command(command)
        except socket.error as e:
            return return_error(_("Failed to send save image command to server"),{"error":e})
        if "error" in res:
            return return_error(_("Save image error"),{"error":res.get('error')})
        result = res.get('result')
        return return_success(_("Save image successfully"),{"path":result})

    # #################################################################
    #
    # Event handlers from the server
    #
    # #################################################################

    async def _version(self,message : dict) -> None:
        """
            Get PHD2 version
            Args : None
            Returns : None
        """
        self.info._version = message.get("PHDVersion")
        self.info._subversion = message.get("PHDSubver")
        self.info._msgversion = message.get("MsgVersion")

    async def _lock_position_set(self, message : dict) -> None:
        """
            Get lock position set
            Args:
                message : dict
            Returns : None
        """
        self.info._lock_position_x = message.get("X")
        self.info._lock_position_y = message.get("Y")
        logger.debug(_("Star lock position : {} {}").format(self.info._lock_position_x,self.info._lock_position_y))

    async def _calibrating(self,message : dict) -> None:
        """
            Get calibrating state
            Args:
                message : dict
            Returns : None
        """
        self.info.c_status._direction = message.get("dir")
        logger.debug(_(f"Star calibrating direction : {self.info._is_calibrating}"))
        self.info.c_status._distance = message.get("dist")
        logger.debug(_(f"Star calibrating distance : {self.info.c_status._distance}"))
        self.info.c_status._dx = message.get("dx")
        logger.debug(_(f"Star calibrating dx : {self.info.c_status._dx}"))
        self.info.c_status._dy = message.get("dy")
        logger.debug(_(f"Star calibrating dy : {self.info.c_status._dy}"))
        self.info.c_status._position = message.get("pos")
        logger.debug(_(f"Star calibrating position : {self.info.c_status._position}"))
        self.info.c_status._step = message.get("step")
        logger.debug(_(f"Star calibrating step : {self.info.c_status._step}"))
        self.info.c_status._state = message.get("State")
        logger.debug(_(f"Star calibrating state : {self.info.c_status._state}"))

    async def _calibration_completed(self,message : dict) -> None:
        """
            Get calibration completed state
            Args:
                message : dict
            Returns : None
        """
        self.info.mount = message.get("Mount")
        logger.debug(_(f"Mount : {self.info.mount}"))

    async def _star_selected(self,message : dict) -> None:
        """
            Get star selected state
            Args:
                message : dict
            Returns : None
        """
        self.info.star_selected_x = message.get("X")
        self.info.star_selected_y = message.get("Y")
        logger.debug(_(f"Star selected position : [{self.info.star_selected_x},{self.info.star_selected_y}]"))
    
    async def _start_guiding(self) -> None:
        """
            Get start guiding state
            Args:
                message : dict
            Returns : None
        """
        self.info._is_guiding = True
        logger.debug(_(f"Start guiding"))

    async def _paused(self) -> None:
        """
            Get paused state
            Args : None
            Returns : None
        """
        self.info._is_guiding = False
        self.info._is_calibrating = False

    async def _start_calibration(self, message : dict) -> None:
        """
            Get start calibration state
            Args:
                message : dict
            Returns : None
        """
        self.info.mount = message.get("Mount")
        self.info._is_calibrating = True
        self.info._is_guiding = False
        logger.info(_("Start calibration"))

    async def _app_state(self, message : dict) -> None:
        """
            Get app state
            Args:
                message : dict
            Returns : None
        """
        state = message.get("State")
        for case in switch(state):
            if case("Stopped"):
                self.info._is_calibrating = False
                self.info._is_looping = False
                self.info._is_guiding = False
                self.info._is_settling = False
                break
            if case("Selected"):
                self.info._is_selected = True
                self.info._is_looping = False
                self.info._is_guiding = False
                self.info._is_settling = False
                self.info._is_calibrating = False
                break
            if case("Calibrating"):
                self.info._is_calibrating = True
                self.info._is_guiding = False
                break
            if case("Guiding"):
                self.info._is_guiding = True
                self.info._is_calibrating = False
                break
            if case("LostLock"):
                self.info._is_guiding = True
                self.info._is_starlocklost = True
                break
            if case("Paused"):
                self.info._is_guiding = False
                self.info._is_calibrating = False
                break
            if case("Looping"):
                self.info._is_looping = True
        logger.debug(_(f"App state : {state}"))

    async def _calibration_failed(self, message : dict) -> None:
        """
            Get calibration failed state
            Args:
                message : dict
            Returns : None
        """
        self.info.last_error = message.get("Reason")
        self.info._is_calibrating = False
        self.info._is_calibrated = False
        logger.error(_(f"Calibration failed , error : {self.info.last_error}"))

    async def _calibration_data_flipped(self, message : dict) -> None:
        """
            Get calibration data flipping state
            Args:
                message : dict
            Returns : None
        """
        self.info.c_status._flip = True
        logger.info(_("Calibration data flipped"))

    async def _lock_position_shift_limit_reached(self) -> None:
        """
            Get lock position shift limit reached state
            Args : None
            Returns : None
        """
        logger.warning(_("Star locked position reached the edge of the camera frame"))

    async def _looping_exposures(self, message : dict) -> None:
        """
            Get looping exposures state
            Args:
                message : dict
            Returns : None
        """
        self.info._is_looping = True
        self.info.frame = message.get("Frame")

    async def _looping_exposures_stopped(self) -> None:
        """
            Get looping exposures stopped state
            Args : None
            Returns : None
        """
        self.info._is_looping = False
        logger.info(_("Stop looping exposure"))

    async def _settle_begin(self) -> None:
        """
            Get settle begin state
            Args : None
            Returns : None
        """
        self.info._is_settling = True
        logger.info(_("Star settle begin ..."))

    async def _settling(self , message : dict) -> None:
        """
            Get settling state
            Args:
                message : dict
            Returns : None
        """
        self.info._settle_distance = message.get("Distance")
        self.info._settle_time = message.get("SettleTime")
        self.info._settle_star_locked = message.get("StarLocked")
        self.info._is_settling = True
        logger.debug(_("Settling status : distance {} time {} star_locked {}").format(self.info._settle_distance,self.info._settle_time,self.info._settle_star_locked))

    async def _settle_done(self, message : dict) -> None:
        """
            Get settle done state
            Args:
                message : dict
            Returns : None
        """
        status = message.get("Status")
        if status == 0:
            logger.info(_("Settle succeeded"))
            self.info._is_settled = True
        else:
            logger.info(_(f"Settle failed , error : {message.get('Error')}"))
            self.info._is_settled = False
        self.info._is_settling = False

    async def _star_lost(self, message : dict) -> None:
        """
            Get star lost state
            Args:
                message : dict
            Returns : None
        """
        self.info.frame = message.get('Frame')
        self.info.starlost_snr = message.get('SNR')
        self.info.starlost_starmass = message.get('StarMass')
        self.info.starlost_avgdist = message.get('AvgDist')
        logger.error(_(f"Star Lost , Frame : {self.info.frame} , SNR : {self.info.starlost_snr} , StarMass : {self.info.starlost_starmass} , AvgDist : {self.info.starlost_avgdist}"))
        self.info._is_starlost = True

    async def _guiding_stopped(self) -> None:
        """
            Get guiding stopped state
            Args : None
            Returns : None
        """
        self.info._is_guiding = False
        logger.info(_("Guiding Stopped"))

    async def _resumed(self) -> None:
        """
            Get guiding resumed state
            Args : None
            Returns : None
        """
        logger.info(_("Guiding Resumed"))
        self.info._is_guiding = True

    async def _guide_step(self , message : dict) -> None:
        """
            Get guide step state
            Args:
                message : dict
            Returns : None
        """
        self.info.g_status._frame = message.get("Frame")
        logger.debug(_("Guide step frame : {}").format(self.info.g_status._frame))
        self.info.mount = message.get("Mount")
        logger.debug(_("Guide step mount : {}").format(self.info.mount))
        self.info.g_status._error = message.get("ErrorCode")
        logger.debug(_("Guide step error : {}").format(self.info.g_status._error))

        self.info.g_status._average_distance = message.get("AvgDist")
        logger.debug(_("Guide step average distance : {}").format(self.info.g_status._average_distance))

        self.info.g_status._dx = message.get("dx")
        logger.debug(_("Guide step dx : {}").format(self.info.g_status._dx))
        self.info.g_status._dy = message.get("dy")
        logger.debug(_("Guide step dy : {}").format(self.info.g_status._dy))

        self.info.g_status._ra_raw_distance = message.get("RADistanceRaw")
        logger.debug(_("Guide step RADistanceRaw : {}").format(self.info.g_status._ra_raw_distance))
        self.info.g_status._dec_raw_distance = message.get("DECDistanceRaw")
        logger.debug(_("Guide step DECDistanceRaw : {}").format(self.info.g_status._dec_raw_distance))

        self.info.g_status._ra_distance = message.get("RADistanceGuide")
        logger.debug(_("Guide step RADistanceGuide : {}").format(self.info.g_status._ra_distance))
        self.info.g_status._dec_distance = message.get("DECDistanceGuide")
        logger.debug(_("Guide step DECDistanceGuide : {}").format(self.info.g_status._dec_distance))

        self.info.g_status._ra_duration = message.get("RADuration")
        logger.debug(_("Guide step RADuration : {}").format(self.info.g_status._ra_duration))
        self.info.g_status._dec_duration = message.get("DECDuration")
        logger.debug(_("Guide step DECDuration : {}").format(self.info.g_status._dec_duration))

        self.info.g_status._ra_direction = message.get("RADirection")
        logger.debug(_("Guide step RADirection : {}").format(self.info.g_status._ra_direction))
        self.info.g_status._dec_direction = message.get("DECDirection")    
        logger.debug(_("Guide step DECDirection : {}").format(self.info.g_status._dec_direction))

        self.info.g_status._snr = message.get("SNR")
        logger.debug(_("Guide step SNR : {}").format(self.info.g_status._snr))
        self.info.g_status._starmass = message.get("StarMass")
        logger.debug(_("Guide step StarMass : {}").format(self.info.g_status._starmass))
        self.info.g_status._hfd = message.get("HFD")
        logger.debug(_("Guide step HFD : {}").format(self.info.g_status._hfd))
        
    async def _guiding_dithered(self, message : dict) -> None:
        """
            Get guiding dithered state
            Args:
                message : dict
            Returns : None
        """
        self.info.dither_dx = message.get("dx")
        self.info.dither_dy = message.get("dy")

    async def _lock_position_lost(self) -> None:
        """
            Get lock position lost state
            Args : None
            Returns : None
        """
        self.info._is_starlocklost = True
        logger.error(_(f"Lock Position Lost"))

    async def _alert(self, message : dict) -> None:
        """
            Get alert state
            Args:
                message : dict
            Returns : None
        """
        logger.error(_(f"Alert : {message.get('Msg')}"))

    async def _guide_param_change(self, message : dict) -> None:
        """
            Get guide param change state
            Args:
                message : dict
            Returns : None
        """
    
    async def _configuration_change(self) -> None:
        """
            Get configuration change state
            Args : None
            Returns : None
        """
