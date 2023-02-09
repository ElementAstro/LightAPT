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

from json import JSONDecodeError, dumps
from os import getcwd, mkdir, path
import re
from time import sleep

from requests import exceptions
from ._telescope import Telescope,EquatorialCoordinateType, TelescopeAxes,DriveRates
from ._exceptions import (DriverException,
                                        ParkedException,
                                        SlavedException,
                                        NotConnectedException,
                                        NotImplementedException,
                                        InvalidValueException,
                                        InvalidOperationException)

from utils.i18n import _
from ...logging import ascom_logger as logger
from ...logging import return_error,return_success,return_warning

class AscomTelescopeAPI(object):
    """
        ASCOM Telescope API Interface based on Alpyca.\n
        NOTE : If the return parameters is None , that does not mean there is no error message
    """

    _ipaddress : str # IP address only ASCOM and INDI
    _api_version : str # API version only ASCOM and INDI
    _name : str # name of the camera
    _id : int # id of the camera
    _description : str
    _configration = "" # path to the configuration file

    coord_system : int # the coordinate system . This is also a important parameter , 1 is JNonw ,2 is J2000 , will other type of coordinate system be supported

    # Timeout of all of the commands
    timeout = 60

    # Current telescope target coordinates , I was not sure what is the difference between current coordinates and target coordinates
    ra = ""
    dec = ""
    # The following two parameters need telescope has az/alt mode , most of the GEM do not support this
    az = ""
    alt = ""
    # If the GPS is enabled
    lon = ""
    lat = ""

    # TODO : I don't know what will happen if we connect a single axis telescope like SGP

    # Slewing speed , in iOptron is 1x,2x,4x ...
    # NOTE : Why I use flaot there? Because in Alpaca the return is not the value like 1x or 128x
    #       It returns the degrees per second the telescop will slew , so there must have a convert system
    slewing_ra_rate : list
    slewing_dec_rate : list
    # This is for telescope safety
    max_slewing_ra_rate : float
    max_slewing_dec_rate : float
    min_slewing_ra_rate : float
    min_slewing_dec_rate : float
    # Tracking mode , such as star,sun or moon
    track_mode : int
    # Tracking rate of the RA and DEC axis
    track_ra_rate : float
    track_dec_rate : float

    # RA and DEC axis park settings 
    park_ra = 0
    park_dec = 0

    # Can telescope goto , most of them have this function
    _can_goto = False
    # Can telescope operation been aborted , this is for safety
    _can_ahort_goto = False
    # NOTE : This is add on 2023/1/10 , I think we need to think about if the telescope do not have DEC axis
    _can_dec_axis = False
    # Can telescope sync the current target
    _can_sync = False
    # Can telescope RA axis track
    _can_ra_track = False
    # Can telescope DEC axis track
    _can_dec_track = False
    # Can telescope park , not sure that every telescope supports this
    _can_park = False
    # Can set telescope parking postion
    _can_set_park_postion = False
    # Same as _can_park
    _can_home = False
    # Can set RA axis tracking rate (speed) , this surely need _can_track is True
    _can_set_track_ra_rate = False
    # Can set DEC axis tracking rate (speed), this surely need _can_track is True
    _can_set_track_dec_rate = False
    # Can set traking mode like sun,star or moon , even if the custom tracking mode
    _can_set_track_mode = False
    # Can telescope track a satellite , this means that the telescope can slewing quickly enough
    _can_track_satellite = False
    # Can get telescope location , if we have these attributes , we can better deal with coordinates
    _can_get_location = False
    # Is the telescope have AZ/ALT mode , this is not surely been enabled 
    _can_az_alt = False

    # Is the telescope connected , if not , how we communicate with the telescope
    _is_connected = False
    # Is the telescope slewing such as goto or sync , make sure that the command will not be too many at one time
    _is_slewing = False
    # Is the telescope tracking , this is very important for deepsky photograph
    _is_tracking = False
    # Is the telescope parked, if the status is true , do not do anything until unpark
    _is_parked = False
    # Is the telescope at the home position
    _is_homed = False

    def __init__(self) -> None:
        """
            Initialize a new ASCOM telescope object
            Args : None
            Returns : None
        """
        self.device = None

    def __del__(self) -> None:
        """
            Destory the ASCOM telescope object
            Args : None
            Returns : None
        """
        if self._is_connected:
            self.disconnect()

    def __str__(self) -> str:
        """
            Return a string representation of the ASCOM telescope object
            Args : None
            Returns : String
        """
        return """ASCOM Telescope API Interface via Alpyca"""

    def get_dict(self) -> dict:
        """
            Return a dictionary containing all of the information
        """
        return {
            "ipaddress" : self._ipaddress,
            "api_version" : self._api_version,
            "name" : self._name,
            "id" : self._id,
            "description" : self._description,
            "configration" : self._configration,
            "timeout" : self.timeout,
            "current" : {
                "ra" : self.ra,
                "dec" : self.dec,
                "az" : self.az,
                "alt" : self.alt,
            },
            "location" : {
                "lat" : self.lat,
                "lon" : self.lon,
            },
            "slewing" : {
                "ra" : {
                    "max" : self.max_slewing_ra_rate,
                    "min" : self.min_slewing_ra_rate
                },
                "dec" : {
                    "max" : self.max_slewing_dec_rate,
                    "min" : self.min_slewing_dec_rate
                }
            },
            "tracking" : {
                "mode" : self.track_mode,
                "ra" : self.track_ra_rate,
                "dec" : self.track_dec_rate
            },
            "parking" : {
                "ra" : self.park_ra,
                "dec" : self.park_dec,
            },
            "abilities" : {
                "can_goto" : self._can_goto,
                "can_abort_goto" : self._can_ahort_goto,
                "can_home" : self._can_home,
                "can_park" : self._can_park,
                "can_dec_axis" : self._can_dec_axis,
                "can_sync" : self._can_sync,
                "can_ra_track" : self._can_ra_track,
                "can_dec_track" : self._can_dec_track,
                "can_set_park_position" : self._can_set_park_postion,
                "can_set_track_ra_rate" : self._can_set_track_ra_rate,
                "can_set_track_dec_rate" : self._can_set_track_dec_rate,
                "can_set_track_mode" : self._can_set_track_mode,
                "can_track_satellite" : self._can_track_satellite,
                "can_get_location" : self._can_get_location,
                "can_az_alt" : self._can_az_alt
            }
        }

    def connect(self,params : dict) -> dict:
        """
            Connect to the ASCOM telescope
            Args : 
                params : dict
                    host : str # host of the ASCOM remote server
                    port : int # port of the ASCOM remote server
                    device_number : int # device number of the ASCOM telescope , default is 0
            Returns : dict
                status : int # status of the connection
                message : str # message of the connection
                params : dict
                    info : dict # BasicTelescopeInfo.get_dict()
        """
        if self._is_connected or self.device is not None:
            return return_error(_("Telescope has already connected"),{"info":self.get_dict()})
        # Get the parameters if parameters is not specified , just use the default parameters
        _host = params.get("host","127.0.0.1")
        _port = params.get("port",11111)
        _device_number = params.get("device_number",0)
        # Trying to connect to ASCOM remote server
        try:
            # Establish connection with ASCOM server
            self.device = Telescope(_host + ":" + str(_port), _device_number)
            # Make telescope connected
            self.device.Connected = True
        except DriverException as e:
            return return_error(_("Failed to connect telescope"),{"error": e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error while connecting to telescope"),{"error": e})

        self._is_connected = True
        res = self.get_configration()
        if res.get("status") != 0:
            return return_error(res.get("message"))
        return return_success(_("Connected to telescope successfully"),{"info":self.get_dict()})

    def disconnect(self) -> dict:
        """
            Disconnect from the ASCOM telescope
            Args : None
            Returns : dict
                status : int # status of the disconnection
                message : str # message of the disconnection
                params : None
        """
        # If the telescope is not connected , do not execute disconnecting command
        if not self._is_connected or self.device is None:
            return return_error(_("Telescope has not connected"),{})
        # If the telescope is slewing , stop it before disconnecting
        if self._is_slewing:
            logger.warning(_("Telescope is slewing , trying to abort the operation"))
            res = self.abort_goto()
            if res.get("status") != 0:
                logger.error(res.get("message"))
                return return_error(res.get("message"),{"error":res.get("params",{}).get("error")})
        # Trying to disconnect from the server , however this just destroys the connection not the server
        try:
            self.device.Connected = False
        except DriverException as e:
            return return_error(_("Failed to disconnect telescope"),{"error": e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error while disconnecting from telescope"),{"error":e})
        # If disconnecting from the server succeeded, clear the variables
        self.device = None
        self._is_connected = False
        return return_success(_("Disconnected from server successfully"),{})

    def reconnect(self) -> dict:
        """
            Reconnect to the ASCOM telescope
            Args : None
            Returns : dict
                status : int # status of the disconnection
                message : str # message of the disconnection
                params : dict
                    info : dict = self.get_dict()
            NOTE : This function is just like a mixing of connect() and disconnect()
        """
        # If the telescope is not connected, do not execute reconnecting command
        if not self._is_connected or self.device is None:
            return return_error(_("Telescope has not connected"),{})
        # If the telescope is slewing, stop it before reconnecting
        if self._is_slewing:
            logger.warning(_("Telescope is slewing, trying to reconnect"))
            res = self.reconnect_goto()
            if res.get("status")!= 0:
                logger.error(res.get("message"))
                return return_error(res.get("message"),{"error":res.get("params",{}).get("error")})
        # Trying to reconnect the telescope , but we hope that the server is working properly
        self._is_connected = False
        try:
            self.device.Connected = False
            sleep(1)
            self.device.Connected = True
        except DriverException as e:
            return return_error(_("Failed to reconnect telescope"),{"error": e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error while reconnecting to telescope"),{"error":e})
        # Do not forget to set the status
        self._is_connected = True
        return return_success(_("Reconnected telescope successfully"),{"info": self.get_dict()})

    def polling(self) -> dict:
        """
            Polling the telescope newest infomation
            Args : None
            Returns : dict
                status : int # status of the disconnection
                message : str # message of the disconnection
                params : dict
                    info : dict # just return self.get_dict()
            NOTE : This function will not refresh the infomation of the telescope , 
                    because this will cause a huge lag and waste system usage.
        """
        if not self._is_connected or self.device is None:
            return return_error(_("Telescope is not connected"),{})
        return return_success(_("Polling teleescope information"),{"info":self.get_dict()})

    def get_configration(self) -> dict:
        """
            Get all of the configurations needed for further processing
            Args : None
            Returns : dict
                status : int # status of the disconnection
                message : str # message of the disconnection
                params : None
        """
        if not self._is_connected or self.device is None:
            return return_error(_("Telescope is not connected"),{})
        logger.info(_("Trying to get telescope configuration"))
        try:
            # Basic information , all of the telescopes have these
            self._name = self.device.Name
            logger.debug(_(f"Telescope name : {self._name}"))
            # This client number is just a random number , do not have a specific meaning
            self._id = self.device._client_id
            logger.debug(_(f"Telescope ID : {self._id}"))
            self._description = self.device.Description
            logger.debug(_(f"Telescope description : {self._description}"))
            self._ipaddress = self.device.address
            logger.debug(_(f"Telescope IP address : {self._ipaddress}"))
            self._api_version = self.device.api_version
            logger.debug(_(f"Telescope API version : {self._api_version}"))

            # Get the coordinates system of the current telescope
            self.coord_system = self.device.EquatorialSystem

            # Get the telescope abilities , this is very important , though we will try to 
            # avoid error command send to the server if it is not available , but a simple
            # check is better solution
            # NOTE : _can_set_track_ra_rate and _can_set_track_dec_rate are moved to below part staying with rates
            self._can_park = self.device.CanPark
            logger.debug(_("Telescope Can Park : {}").format(self._can_park))
            self._can_set_park_postion = self.device.CanSetPark
            logger.debug(_("Telescope Can Set Parking Position : {}").format(self._can_set_park_postion))

            # Check if RA axis is available to goto , I don't know whether a single axis telescope can goto
            self._can_goto = self.device.CanMoveAxis(TelescopeAxes.axisPrimary)
            logger.debug(_(f"Telescope Can Slew : {self._can_goto}"))

            # I think that every telescope must can abort goto operation ,
            # If not how we to rescue it when error happens
            self._can_ahort_goto = True
            logger.debug(_("Telescope Can Abort Slew : {}").format(self._can_ahort_goto))
            self._can_track = self.device.CanSetTracking
            logger.debug(_("Telescope Can Track : {}").format(self._can_track))
            self._can_sync = self.device.CanSync
            logger.debug(_("Telescope Can Sync : {}").format(self._can_sync))
            # We are very sure about that our telescopes can slewing fast enough to catch the satelite 
            self._can_track_satellite = True
            logger.debug(_("Telescope Can Track Satellite : {}").format(self._can_track_satellite))
            self._can_home = self.device.CanFindHome
            logger.debug(_("Telescope Can Find Home : {}").format(self._can_home))

            # Check whether we can get the location of the telescope
            # If there is no location available , it will cause NotImplementedException,
            # so we just need to catch the exception and judge whether having location values
            try:
                self.lon = self.device.SiteLongitude
                logger.debug(_("Telescope Longitude : {}").format(self.lon))
                self.lat = self.device.SiteLatitude
                logger.debug(_("Telescope Latitude : {}").format(self.lat))
                self._can_get_location = True
            except NotImplementedException as e:
                logger.warning(_("Can not get telescope location : {}").format(e))
                self._can_get_location = False
                self.lon = ""
                self.lat = ""

            # This time we need to get the current status of the telescope , 
            # For example is the telescope is parked , that means we can not execute other commands,
            # before unparked the telescope . Make sure the telescope is safe
            self._is_parked = self.device.AtPark
            logger.debug(_("Is Telescope At Park Position : {}").format(self._is_parked))
            self._is_tracking = self.device.Tracking
            logger.debug(_("Is Telescope Tracking : {}").format(self._is_tracking))
            self._is_slewing = self.device.Slewing
            logger.debug(_("Is Telescope Slewing : {}").format(self._is_slewing))

            # Get telescope targeted RA and DEC values
            self.ra = self.device.RightAscension
            self.dec = self.device.Declination
            try:
                self.az = self.device.Azimuth
                self.alt = self.device.Altitude
            except NotImplementedException as e:
                logger.warning(_("Telescope do not have az/alt mode enabled"))
                self._can_az_alt = False
                self.az = ""
                self.alt = ""

            # If the telescope can not track , we will not try to get the settings of the tracking
            if self._can_track:
                # Fist we should check if the telescope is enabled to set RA axis tracking rate
                self._can_set_track_ra_rate = self.device.CanSetRightAscensionRate
                if self._can_set_track_ra_rate:
                    try:
                        # Tracking rate of the RightAscenion axis 
                        self.track_ra_rate = self.device.RightAscensionRate
                        self._can_ra_track = True
                        logger.debug(_("Telescope Right Ascension Rate : {}").format(self.track_ra_rate))
                    except NotImplementedException as e:
                        logger.warning(_("Telescope RA axis track mode can not be set"))
                        self._can_set_track_ra_rate = False
                # Just like RA , we need to check first to avoid unexpected errors
                self._can_set_track_dec_rate = self.device.CanSetDeclinationRate
                if self._can_set_track_dec_rate:
                    try:
                        # Tracking rate of the Declination axis
                        self.track_dec_rate = self.device.DeclinationRate
                        self._can_dec_track = True
                        logger.debug(_("Telescope Declination Rate : {}").format(self.track_dec_rate))
                    except NotImplementedException as e:
                        logger.warning(_("Telescope Dec axis track mode can not be set"))
                        self._can_set_track_dec_rate = False

                self.track_mode = self.device.TrackingRate
                logger.debug(_("Telescope Tracking Mode : {}").format(self.track_mode))
                self._can_set_track_mode = True

            # Get the maximum and minimum of the available telescope RA axis rate values
            self.slewing_ra_rate = self.device.AxisRates(TelescopeAxes.axisPrimary)
            self.max_slewing_ra_rate = self.slewing_ra_rate[0].Maximum
            logger.debug(_("Max Right Ascension Rate : {}").format(self.max_slewing_ra_rate))
            self.min_slewing_ra_rate = self.slewing_ra_rate[0].Minimum
            logger.debug(_("Min Right Ascension Rate : {}").format(self.min_slewing_ra_rate))

            # Before get the DEC axis, we need to know whether the telescope has DEC axis enabled
            self._can_dec_axis = self.device.CanMoveAxis(TelescopeAxes.axisSecondary)
            if self._can_dec_axis:
                self.slewing_dec_rate = self.device.AxisRates(TelescopeAxes.axisSecondary)
                self.max_slewing_dec_rate = self.slewing_dec_rate[0].Maximum
                logger.debug(_("Max Declination Rate : {}").format(self.max_slewing_dec_rate))
                self.min_slewing_dec_rate = self.slewing_dec_rate[0].Minimum
                logger.debug(_("Min Declination Rate : {}").format(self.min_slewing_dec_rate))
            else:
                self.slewing_dec_rate = []
                self.max_slewing_dec_rate = -1
                self.min_slewing_dec_rate = -1

        except InvalidOperationException as e:
            return return_error(_("Invalid operation"),{"error":e})
        except NotConnectedException as e:
            self._is_connected = False
            return return_error(_("Telescope is not connected"),{"error":e})
        except InvalidValueException as e:
            return return_error(_("Some invalid value was provided"),{"error":e})
        except NotImplementedException as e:
            return return_error(_("Telescope is not supported"),{"error":e})
        except DriverException as e:
            return return_error(_("Failed to get telescope configuration"),{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error":e})

        return return_success(_("Refresh telescope settings successfully"),{})

    def set_configration(self, params: dict) -> dict:
        return super().set_configration(params)

    def load_configration(self) -> dict:
        return super().load_configration()

    def save_configration(self) -> dict:
        """
            Save configration of telescope into a JSON file
            Args : None
            Returns :
                status : int
                message : str
                params : None
            NOTE : This function will not be automatically called when the __del__ method is called
        """
        _p = path.join
        _path = _p(getcwd() , "config","telescope",self._name+".json")
        if not path.exists("config"):
            mkdir("config")
        if not path.exists(_p("config","telescope")):
            mkdir(_p("config","telescope"))
        self._configration = _path
        try:
            with open(_path,mode="w+",encoding="utf-8") as file:
                try:
                    file.write(dumps(self.get_dict(),indent=4,ensure_ascii=False))
                except JSONDecodeError as e:
                    logger.error(_("JSON decoder error , error : {}").format(e))
        except OSError as e:
            logger.error(_(f"Failed to write configuration to file , error : {e}"))
        return return_success(_("Save telescope configuration to file successfully"),{})

    # #################################################################
    #
    # The following functions are used to control the telescope (all is non-blocking)
    #
    # #################################################################

    def goto(self, params: dict) -> dict:
        """
            Make the telescope target at the specified position of the sky\n
            NOTE : More detail infomation about the arguments are in server.basic.telescope\n
            Args :
                params : dict
                    j2000 : bool
                    ra : str
                    dec : str
            Returns :
                status : int
                message : str
                params : None
            ATTENTION : Though the parameters are checked in wstelescope , I think we still need to check twice
        """
        # Check if the telescope is available to goto
        if not self._is_connected:
            return return_error(_("Telescope is not connected"),{})
        if self._is_slewing:
            return return_error(_("Telescope is slewing"),{})
        if self._is_parked:
            return return_error(_("Telescope is parked"),{})

        _j2000 = params.get('j2000',False)
        _ra = params.get('ra')
        _dec = params.get('dec')
        _az = params.get('az')
        _alt = params.get('alt')

        az_alt_flag = False

        # This is means the user want to make a az/alt telescope goto , so we must make sure az/alt exists
        if not _ra and not _dec and _az and _alt:
            # If the telescope do not support this mode
            if not self._can_az_alt:
                return return_error(_("AZ/ALT mode is not available"),{})
            logger.info(_("Using AzAlt mode"))
            # Check if the coordinates provided are valid
            if not isinstance(_az,str) or not isinstance(_alt,str) or not re.match("\d{2}:\d{2}:\d{2}",_az) or not re.match("\d{2}:\d{2}:\d{2}",_alt):
                return return_error(_("Invalid AZ or Alt coordinate value"),{})
            az_alt_flag = True
        # This means GEM or CEM telescope
        if _ra and _dec:
            logger.info(_("Check the coordinates of the target"))
            if not isinstance(_ra,str) or not isinstance(_dec,str) or not re.match("\d{2}:\d{2}:\d{2}",_ra) or not re.match("\d{2}:\d{2}:\d{2}",_dec):
                return return_error(_("Invalid RA or Dec coordinate value"),{})
        # If all of the parameters are provided , how can we choose , so just return an error
        if _az and _alt and _ra and _dec:
            return return_error(_("Please specify RA/DEC or AZ/ALT mode in one time"),{})

        if az_alt_flag:
            _ra = _az
            _dec = _alt
        # If the telescope is using JNow format of the coordinates system
        # and the coordinates provided are in the J2000 format
        if self.coord_system == EquatorialCoordinateType.equTopocentric and _j2000:
            # TODO There need a coordinate convert
            pass
        
        _ra_h,_ra_m,_ra_s = map(int , _ra.split(":"))
        _dec_h,_dec_m,_dec_s = map(int, _dec.split(":"))

        # Format the RA and DEC values , for 
        _format_ra = _ra_h  + _ra_m / 60 +  _ra_s / 3600
        _format_dec = _dec_h +  _dec_m /60 + _dec_s / 3600
        # CHeck if the current RA and DEC are the same as target RA and DEC
        if self.device.RightAscension == _format_ra and self.device.Declination == _format_dec:
            return return_error(_("Telescope is already targeted the right position"),{})

        # Trying to start goto operation
        try:
            self.device.Tracking = True
            self.device.SlewToCoordinatesAsync(_format_ra,_format_dec)
        except ParkedException as e:
            return return_error(_("Telescope is parked"),{"error": e})
        except NotImplementedException as e:
            return return_error(_("Telescope is not supported"),{"error": e})
        except InvalidValueException as e:
            return return_error(_("Invalid value"),{"error": e})
        except NotConnectedException as e:
            self._is_connected = False
            return return_error(_("Telescope is not connected"),{"error": e})
        except DriverException as e:
            return return_error(_("Telescope driver error"),{"error": e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error": e})

        self._is_slewing = True
        return return_success(_("Telescope is slewing to the target"),{})

    def abort_goto(self) -> dict:
        """
            Abort the current goto operation\n
            Args : None
            Returns : 
                status : int
                message : str
                params : dict
                    ra : str # the current RA when aborting the goto operation
                    dec : str # the current DEC when aborting the goto operation
                    az : str # If is theodolite
                    alt : str # If is theodolite
        """
        # Check if the telescope is connected
        if not self.device.Connected:
            return return_error(_("Telescope is not connected"),{})
        # Check if the telescope is truly slewing
        if not self.device.Slewing:
            return return_error(_("Telescope is not slewing"),{})
        if self._is_parked:
            return return_error(_("Telescope is parked"),{})

        # Trying to abort goto operation
        try:
            self.device.AbortSlew()
        except InvalidOperationException as e:
            return return_error(_("Invalid operation"),{"error": e})
        except NotConnectedException as e:
            self._is_connected = False
            return return_error(_("Telescope is not connected"),{"error": e})
        except DriverException as e:
            return return_error(_("Telescope driver error"),{"error": e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error": e})
        
        sleep(0.1)
        if not self.device.Slewing:
            self._is_slewing = False
            logger.info(_("Aborting goto operation successfully"))
        else:
            return return_error(_("Aborting goto operation failed"),{})
        
        # Though I don't think after such a few time the telescope will lose connection , just be careful
        try:
            current_ra = self.device.RightAscension
            current_dec = None
            if self._can_dec_axis:
                current_dec = self.device.Declination
        except NotConnectedException as e:
            self._is_connected = False
            return return_error(_("Telescope is not connected"),{"error": e})
        except DriverException as e:
            return return_error(_("Telescope driver error"),{"error": e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error": e})

        return return_success(_("Aborted goto operation successfully"),{"ra":current_ra,"dec":current_dec})

    def get_goto_status(self) -> dict:
        """
            Get the status of the goto operation\n
            Args : None
            Returns : 
                status : int
                message : str
                params : dict
                    status : bool # If the telescope is slewing
                    ra : str # the current RA when aborting the goto operation
                    dec : str # the current DEC when aborting the goto operation
        """
        # Check whether the telescope is parked
        if self._is_parked:
            return return_error(_("Telescope is parked"),{})
        try:
            status = self.device.Slewing
            ra = self.device.RightAscension
            dec = None
            if self._can_dec_axis:
                dec = self.device.Declination
        except NotImplementedException as e:
            self._is_slewing = False
            return return_error(_("Telescope is not support slewing"),{"error": e})
        except NotConnectedException as e:
            self._is_slewing = False
            self._is_connected = False
            return return_error(_("Telescope is not connected"),{"error": e})
        except DriverException as e:
            self._is_slewing = False
            return return_error(_("Telescope driver error"),{"error": e})
        except exceptions.ConnectionError as e:
            self._is_slewing = False
            return return_error(_("Network error"),{"error": e})
        
        self._is_slewing = status 
        
        logger.debug(_("Telescope slewing status : {} , Current RA : {} , Current DEC : {}").format(status,ra,dec))
        return return_success(_("Refresh telescope status successfully"),{"status":status,"ra":ra,"dec":dec})

    def get_goto_result(self) -> dict:
        """
            Get the result of the goto operation\n
            Args : None
            Returns : 
                status : int
                message : str
                params : dict
                    ra : str # the final RA
                    dec : str # the final DEC
        """
        # Check if the telescope is connected
        if not self._is_connected:
            return return_error(_("Telescope is not connected"),{})
        # Check if the teleescope is parked
        if self._is_parked:
            return return_error(_("Telescope is parked"),{})
        # Check if the telescope is slewing
        if self._is_slewing:
            return return_error(_("Telescope is slewing"),{})
        try:
            ra = self.device.RightAscension
            dec = None
            if self._can_dec_axis:
                dec = self.device.Declination
        except NotConnectedException as e:
            self._is_connected = False
            return return_error(_("Telescope is not connected"),{"error":e})
        except DriverException as e:
            return return_error(_("Telescope driver error"),{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error":e})

        logger.info(_("Goto result : RA : {} DEC : {}").format(ra,dec))
        self.ra = ra
        self.dec = dec
        return return_success(_("Get goto result successfully"),{"ra":self.ra, "dec":self.dec})
    
    def tracking(self , params = {}) -> dict:
        """
            Start or stop tracking mode of the telescope
            Args:
                params : dict
                    enable : bool
            Returns: dict
        """
        if not self._is_connected:
            return return_error(_("Telescope is not connected"))
        if self._is_parked:
            return return_success(_("Telescope has already parked"),{})
        if not self._can_ra_track and not self._can_dec_track:
            return return_error(_("Telescope is not supported to track"))
        
        enable = params.get('enable')
        if enable is None or not isinstance(enable,bool):
            return return_error(_("Invalid enable value was provided"))
        
        try:
            self.device.Tracking = enable
        except NotImplementedException as e:
            return return_error(_("Telescope does not support track function"),{"error":e})
        except NotConnectedException as e:
            self._is_connected = False
            return return_error(_("Telescope is not connected"),{"error": e})
        except DriverException as e:
            return return_error(_("Telescope driver error"),{"error": e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error": e})
        
        return return_success(_("Set the tracking mode of the telescope successfully"))
    
    def get_tracking_mode(self) -> dict:
        """
            Get the tracking mode of the current telescope
            Args : None
            Returns : dict
                mode : str        
        """
        if not self._is_connected:
            return return_error(_("Telescope is not connected"))
        if not self._can_ra_track and not self._can_dec_track:
            return return_error(_("Telescope is not supported to track"))
        
        try:
            self.track_mode = self.device.TrackingRate
        except NotImplementedException as e:
            return return_error(_("Telescope does not support tracking function"),{"error":e})
        except NotConnectedException as e:
            self._is_connected = False
            return return_error(_("Telescope is not connected"),{"error": e})
        except DriverException as e:
            return return_error(_("Telescope driver error"),{"error": e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error": e})
        
        mode = ""
        if self.track_mode == DriveRates.driveSolar:
            mode = "Solar"
        elif self.track_mode == DriveRates.driveLunar:
            mode = "Lunar"
        elif self.track_mode == DriveRates.driveKing:
            mode = "King"
        elif self.track_mode == DriveRates.driveSidereal:
            mode = "Star"
        
        return return_success(_("Get the tracking mpde successfully"),{"mode":mode})
    
    def set_tracking_rate(self , params = {}) -> dict:
        """
            Set the tracking rate of the current telescope
            Args :
                params : dict
                    rate : int
            Returns : dict
        """
        if not self._is_connected:
            return return_error(_("Telescope is not connected"))
        if not self._can_ra_track and not self._can_dec_track:
            return return_error(_("Telescope is not supported to track"))
        
        _rate = params.get("rate")
        if not _rate or not isinstance(_rate,int):
            return return_error(_("Invalid rate value was specified"))
        
        try:
            self.device.TrackingRate = _rate
        except InvalidValueException as e:
            return return_error(_("Invalid telescope tracking rate was specified"),{"error":e})
        except NotImplementedException as e:
            return return_error(_("Telescope does not support tracking function"),{"error":e})
        except NotConnectedException as e:
            self._is_connected = False
            return return_error(_("Telescope is not connected"),{"error": e})
        except DriverException as e:
            return return_error(_("Telescope driver error"),{"error": e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error": e})

    def park(self) -> dict:
        """
            Park the current telescope to default parking position\n
            Args: None
            Returns: dict
                status : int
                message : str
                params : None
            NOTE : Just like the parent class
        """
        if not self._is_connected:
            return logger.error(_("Telescope is not connected"),{})
        if self._is_parked:
            return return_success(_("Telescope has already parked"),{})
        if not self._can_park:
            return return_error(_("Telescope does not support park function"),{})

        try:
            self.device.Park()
        except NotImplementedException as e:
            return return_error(_("Telescope does not support park function"),{"error":e})
        except NotConnectedException as e:
            self._is_connected = False
            return return_error(_("Telescope is not connected"),{"error": e})
        except SlavedException as e:
            return return_error(_("Slaved exception: {}"),{"error": e})
        except DriverException as e:
            return return_error(_("Telescope driver error"),{"error": e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error": e})
        except exceptions.ReadTimeout as e:
            return return_error(_("Read timeout: {}"),{"error":e})

        self._is_parked = True

        return return_success(_("Telescope parked successfully"),{})

    def unpark(self) -> dict:
        """
            Unpark the telescope to recontrol the telescope\n
            Args : None
            Returns : 
                status : int
                message : str
                params : None
            NOTE : This function must be called if the telescope is parked
        """
        if not self._is_connected:
            return return_error(_("Telescope is not connected"),{})
        if not self._is_parked or not self.device.AtPark:
            return logger.error(_("Telescope is not parked"))
        
        try:
            self.device.Unpark()
        except NotImplementedException as e:
            return return_error(_("Telescope is not supported to unpark"),{"error":e})
        except NotConnectedException as e:
            self._is_connected = False
            return return_error(_("Telescope is not connected"),{"error":e})
        except DriverException as e:
            return return_error(_("Telescope driver error"),{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error":e})
        self._is_parked = False
        return return_success(_("Telescope is unparked successfully"),{})

    def get_park_position(self) -> dict:
        """
            Get the parking position of the current telescope\n
            Args : None
            Returns : 
                ststus : int
                message : str
                params : dict
                    position : int or list
            NOTE : This function needs telescope supported
        """
        if not self._is_connected:
            return_error(_("Telescope is not connected"),{})
        if not self._can_park:
            return return_error(_("Telescope is not supporting park function"),{})

        # TODO : A little bit of embarrassing that it seems that Alpyca doesn't support getting parking position

        return return_error(_("Telescope is not supportingPark function"),{})
        
    def set_park_position(self, params: dict) -> dict:
        """
            Set the position of parking\n
            Args : 
                params : dict
                    ra : str # optional
                    dec : str # optional
                    NOTE : If both ra and dec are not specified , just set the current position as the parking position
            Returns :
                status : int
                message : str
                params : dict
                    ra : str # RA of the parking position
                    dec : str # DEC of the parking position
            NOTE : This function may need telescope supported
        """
        # Regular check the telescope status
        if not self._is_connected:
            return return_error(_("Telescope is not connected"),{})
        if not self._can_set_park_postion:
            return return_error(_("Telescope is not support to set parking position"),{})

        # Check if the parameters are valid or just empty string
        ra = params.get('ra')
        dec = params.get('dec')

        if ra is not None and isinstance(ra,str) and re.match("\d{2}:\d{2}:\d{2}",ra):
            ra_h , ra_m , ra_s = map(int,ra.split(":"))
            self.park_ra = ra_h + ra_m / 60 + ra_s / 3600
        else:
            logger.warning(_("Unknown type of the RA value are specified , just use the current RA value instead"))
            self.park_ra = self.device.RightAscension

        if dec is not None and isinstance(dec,str) and re.match("\d{2}:\d{2}:\d{2}",dec):
            dec_h , dec_m , dec_s = map(int, dec.split(':'))
            self.park_dec = dec_h + dec_m / 60 + dec_s / 3600
        else:
            logger.warning(_("Unknown type of the DEC value are specified , just use the current DEC value instead"))
            self.park_dec = self.device.Declination

        # Trying to set the position of the park operation
        try:
            # Here is a Alpyca limitation , we can just let the telescope move to the wanted position
            # Then we can set the position of the park operation
            self.device.SlewToCoordinatesAsync(self.park_ra,self.park_dec)
            used_time = 0
            while used_time <= self.timeout:
                if not self.device.Slewing:
                    break
                used_time += 1
                sleep(1)
            
            self.device.SetPark()

        except NotImplementedException as e:
            self._can_set_park_postion = False
            return logger.error(_("Telescope is not supported to set parking position"),{"error":e})
        except InvalidValueException as e:
            return return_error(_("Invalid value was specified"),{"error":e})
        except NotConnectedException as e:
            self._is_connected = False
            return return_error(_("Telescope is not connected"),{"error" : e})
        except DriverException as e:
            return return_error(_("Telescope driver error"),{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error" : e})

        return return_success(_("Set park position successfully"),{})

    def home(self) -> dict:
        """
            Let the current telescope slew to home position
            Args : None
            Returns : 
                status : int
                message : str
                params : None
            NOTE : This function may need telescope supported
        """
        if not self._is_connected:
            return return_error(_("Telescope is not connected"),{})
        if self._is_parked:
            return return_error(_("Telescope had already parked"),{})
        
        if self._is_slewing:
            return return_error(_("Telescope is slewing"),{})
        
        try:
            self.device.FindHome()
        except NotImplementedException as e:
            self._can_home = False
            return return_error(_("Telescope is not support home function"),{"error": e})
        except NotConnectedException as e:
            self._is_connected = False
            return return_error(_("Telescope is not connected : {}").format(e))
        except DriverException as e:
            return return_error(_("Telescope driver error"),{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error":e})

        return return_success(_("Telescope returned home successfully"),{"ra":self.ra, "dec":self.dec})  

    def get_home_status(self) -> dict:
        """
            Get the realtime home status of the telescope
            Args : None
            Returns : dict
                status : bool
        """
        if not self._is_connected:
            return return_error(_("Telescope is not connected"),{})
        if self._is_parked:
            return return_error(_("Telescope had already parked"),{})
        if not self._can_home:
            return return_error(_("Telescope is not supported to return home position"),{})

        try:
            status = self.device.AtHome
            self.ra = self.device.RightAscension
            if self._can_dec_axis:
                self.dec = self.device.Declination
            logger.debug(_("In returning home processing , RA : {} , DEC : {}").format(self.ra,self.dec))
        except NotConnectedException as e:
            self._is_connected = False
            return return_error(_("Telescope is not connected : {}").format(e))
        except DriverException as e:
            return return_error(_("Telescope driver error"),{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error":e})
        
        return return_success(_("Get the home status of the telescope successfully"),{"status":status,"ra":self.ra,"dec":self.dec})
    
    def get_gps_location(self) -> dict:
        """
            Get the GPS location of the telescope
            Args : None
            Returns : None
        """
        if not self._is_connected:
            return return_error(_("Telescope is not connected"))
        if not self._can_get_location:
            return return_error(_("Telescope is not supported to get location"))
        
        try:
            self.lon = self.device.SiteLongitude
            self.lat = self.device.SiteLatitude
            self.elevation = self.device.SiteElevation
        except NotImplementedException as e:
            return return_error(_("No location value available"),{'error':e})
        except InvalidOperationException as e:
            self._can_get_location = False
            return return_error(_("Telescope is not supported getting location function"),{"error": e})
        except NotConnectedException as e:
            self._is_connected = False
            return return_error(_("Telescope is not connected : {}").format(e))
        except DriverException as e:
            return return_error(_("Telescope driver error"),{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error":e})
        
        return return_success(_("Get telescope location information successfully"),{"lon":self.lon, "lat":self.lat,"elevation":self.elevation})
    
        
import asyncio
import tornado.ioloop
import tornado.websocket

class WSAscomTelescope(object):
    """
        Websocket telescope interface
    """

    def __init__(self) -> None:
        """
            Initial a new WSTelescope
            Args : None
            Returns : None
        """
        self.thread = None
        self.device = AscomTelescopeAPI()

    def __del__(self) -> None:
        """
            Delete a WSTelescope
            Args : None
            Returns : None
        """

    def __str__(self) -> str:
        """
            Returns the name of the WSTelescope class
            Args : None
            Returns : None
        """
        return "LightAPT Ascom Websocket Telescope Wrapper API "
    
    async def connect(self , params = {} , ws = None) -> dict:
        """
            Async connect to the telescope 
            Args : 
                params : dict
                    device_name : str
                    host : str # both indi and ascom default is "127.0.0.1"
                    port : int # for indi port is 7624 , for ascom port is 11111
            Returns : dict
                info : dict # BasicaTelescopeInfo object
        """
        if self.device is not None:
            logger.info(_("Disconnecting from existing telescope ..."))
            self.disconnect()

        _device_name = params.get('device_name')

        if _device_name is None:
            return return_error(_("Type or device name must be specified"))
        
        return self.device.connect(params=params)

    async def disconnect(self,params = {} , ws = None) -> dict:
        """
            Async disconnect from the device
            Args : None
            Returns : dict
        """
        if self.device is None or not self.device.info._is_connected:
            return return_error(_("Telescope is not connected"))
        
        return self.device.disconnect()

    async def reconnect(self,params = {} , ws = None) -> dict:
        """
            Async reconnect to the device
            Args : None
            Returns : dict
                info : dict # just like connect()
            NOTE : This function is just allowed to be called when the telescope had already connected
        """
        if self.device is None or not self.device.info._is_connected:
            return return_error(_("Telescope is not connected"))

        return self.device.reconnect()

    async def polling(self,params = {} , ws = None) -> dict:
        """
            Async polling method to get the newest telescope information
            Args : None
            Returns : dict
                info : dict # usually generated from get_dict() function
        """
        if self.device is not None:
            return return_error(_("Telescope is not connected"))

        return self.device.polling()
    
    async def get_parameter(self , params = {} , ws = None) -> dict:
        """
            Get the specified parameter value of the telescope\n
            Args :
                params : dict
                    name : str
            Returns : dict
        """
        _name = params.get('name')
        if not _name or not isinstance(_name,str):
            return return_error(_("Invalid parameter name was specified"))

        return self.device.get_parameter(params=params)

    async def set_parameter(self, params = {} , ws = None) -> dict:
        """
            Set the specified parameter value of the telescope\n
            Args :
                params : dict
                    name : str
                    value : str
            Returns : dict
        """
        _name = params.get('name')
        _value = params.get('value')
        if not _name or not _value or not isinstance(_name,str):
            return return_error(_("Invalid name or value were specified"))
        return self.device.set_parameter(params=params)

    # #############################################################
    #
    # Following methods are used to control the telescope
    #
    # #############################################################

    # #############################################################
    # Goto
    # #############################################################

    async def goto(self,params = {} , ws = None) -> dict:
        """
            Async goto operation to let the telescope target at a specific point\n
            Args :
                params : dict
                    ra : str or float
                    dec : str or float
                    j2000 : bool
                ws : tornado.websocket.WebSocketHandler instance
            Returns : dict
            NOTE : This function is non-blocking , it will return the results immediately 
                    and start a thread to watch the operation process.If the goto is finished,
                    it will return a message to connected clients
            NOTE : The parameters contain the coordinates of the target , please just use a single
                    axis format like RA/DEC or AZ/ALT , j2000 means if the coordinates are in the
                    format of J2000 , if true , they need to be converted before send to telescope
        """
        if self.device is None:
            return return_error(_("Telescope is not connected"))

        _ra = params.get('ra')
        _dec = params.get('dec')
        _j2000 = params.get('j2000',False)

        if _ra is None or not isinstance(_ra,(str,float)) or _dec is None or not isinstance(_dec,(str,float)):
            return return_error(_("Invalid coordinates value of the target object"))

        if _j2000:
            pass # There need a convert function

        res = self.device.goto(params=params)
        if res.get("status") != 0:
            return res
        
        tornado.ioloop.IOLoop.instance().add_callback(self.goto_thread,ws)

        return return_success(_("Telescope started goto operation successfully"))

    async def goto_thread(self , ws = None) -> None:
        """
            Goto status monitor thread
        """
        used_time = 0
        while used_time <= self.device.info.timeout:
            res = await self.get_goto_status()
            print(res)
            if not res.get("params").get('status'):
                break
            await asyncio.sleep(0.5)
            used_time += 0.5
        await ws.write_message(await self.get_goto_result()) 

    async def abort_goto(self,params = {} , ws = None) -> dict:
        """
            Async abort goto operation
            Args : None
            Returns : dict
            NOTE : This function must be called before shutting down the main server
        """

    async def get_goto_status(self,params = {} , ws = None) -> dict:
        """
            Async get the status of the goto operation
            Args : 
                params : None
                ws : tornado.websocket.WebSocketHandler
            Returns : dict
                status : bool # True if the telescope is still slewing
                ra : float # current ra
                dec : float # current dec
        """
        if self.device is None:
            return return_error(_("Telescope is not connected"))

        res = self.device.get_goto_status()

        await ws.write_message(res)

        return res

    async def get_goto_result(self,params = {} , ws = None) -> dict:
        """
            Async get the result of the goto operation
            Args : None
            Returns : dict
                ra : str # current ra
                dec : str # current dec
        """
        if self.device is None:
            return return_error(_("Telescope is not connected"))

        return self.device.get_goto_result()
    
    # #############################################################
    # Park
    # #############################################################

    async def park(self,params = {} , ws = None) -> dict:
        """
            Async park the telescope and after this operation , we cannot control the telescope
            until we unpark the telescope.
            Args : None
            Returns : dict
        """
        if self.device is None:
            return return_error(_("Telescope is not connected"))

        return self.device.park()

    async def unpark(self,params = {} , ws = None) -> dict:
        """
            Async unpark the parked telescope
            Args : None
            Returns : dict
            NOTE : If a telescope is not parked , please do not execute this function
        """
        if self.device is None:
            return return_error(_("Telescope is not connected"))

        return self.device.unpark()

    async def get_park_position(self,params = {} , ws = None) -> dict:
        """
            Async get the position of the park operation
            Args : None
            Returns : dict
                ra : str # ra of the parking position
                dec : str # dec of the parking position
        """
        if self.device is None:
            return return_error(_("Telescope is not connected"))

        return self.device.get_park_position()

    async def set_park_position(self,params = {} , ws = None) -> dict:
        """
            Async set the position of the park operation
            Args : None
                ra : str or float # ra of the parking position
                dec : str or float # dec of the parking position
            Returns : dict
        """
        if self.device is None:
            return return_error(_("Telescope is not connected"))

        _ra = params.get('ra')
        _dec = params.get('dec')
        if _ra is None or not isinstance(_ra, (str, float)) or _dec is None or not isinstance(_dec, (str, float)):
            return return_error(_("Invalid parking position values"))

        return self.device.set_park_position(params=params)

    # #############################################################
    # Home
    # #############################################################

    async def home(self,params = {} , ws = None) -> dict:
        """
            Async Let the telescope slew to home position
            Args :
                params : None
                ws : tornado.websocket.WebSocketHandler
            Returns : dict
        """
        if self.device is None:
            return return_error(_("Telescope is not connected"))

        res = self.device.home()
        if res.get("status") != 0:
            return res
        
        tornado.ioloop.IOLoop.instance().add_callback(self.home_thread,ws)

        return return_success(_("Telescope started to move to home successfully"))

    async def home_thread(self , ws = None) -> None:
        """
            Home operation monitor thread
        """
        used_time = 0
        while used_time <= self.device.info.timeout:
            res = await self.get_home_status()
            print(res)
            if res.get("params").get('status'):
                break
            await asyncio.sleep(0.5)
            used_time += 0.5

    async def get_home_status(self,params = {}) -> dict:
        """
            Async get the status of the home 
            Args : None
            Returns : dict
                status : bool # wheather the telescpe is at home position
        """
        if self.device is None:
            return return_error(_("Telescope is not connected"))

        res = self.device.get_home_status()

        await self.ws.write_message(res)

        return res

    async def get_home_position(self,params = {} , ws = None) -> dict:
        """
            Async get the home position
            Args : None
            Returns : dict
                ra : str # ra of the home position
                dec : str # dec of the home position
        """
        return return_error(_("Get home position is not supported"))

    # #############################################################
    # Track
    # #############################################################

    async def track(self,params = {} , ws = None) -> dict:
        """
            Async start tracking mode without any parameters
            Args :
                params : dict
                ws : None
            Returns : dict
        """

        return self.device.tracking(params=params)

    async def abort_track(self,params = {} , ws = None) -> dict:
        """
            Async abort the tracking
            Args : None
            Returns : dict
        """
        if self.device is None:
            logger.error(_("Telescope is not connected"))
        return self.device.tracking(params=params)

    async def get_track_mode(self,params = {} , ws = None) -> dict:
        """
            Async get the track mode of the current telescope
            Args : None
            Returns : dict
                mode : str
        """
        if self.device is None:
            logger.error(_("Telescope is not available"))
        
        return self.device.get_tracking_mode()

    async def set_track_rate(self,params = {} , ws = None) -> dict:
        """
            Async set the track rate of the current telescope
            Args : dict
                ra_rate : float
                dec_rate : float
        """
        if self.device is None:
            logger.error(_("Telescope is not connected"))

        return self.device.set_tracking_rate(params=params)

    # #############################################################
    # GPS Location
    # #############################################################

    async def get_gps_location(self,params = {} , ws = None) -> dict:
        """
            Async get GPS location
            Args : None
            Returns : dict
                lon : str
                lat : str
                elevation : float
        """
        if not self.device:
            return return_error(_("Telescope is not connected"))
        
        return self.device.get_gps_location()