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
import socket
from time import sleep

from requests import exceptions
from libs.alpyca.telescope import Telescope,EquatorialCoordinateType, TelescopeAxes
from libs.alpyca.exceptions import (DriverException,
                                        ParkedException,
                                        SlavedException,
                                        NotConnectedException,
                                        NotImplementedException,
                                        InvalidValueException,
                                        InvalidOperationException)

from server.basic.telescope import BasicTelescopeAPI,BasicTelescopeInfo

from utils.i18n import _
from ...logging import logger,return_error,return_success

class AscomTelescopeAPI(BasicTelescopeAPI):
    """
        ASCOM Telescope API Interface based on Alpyca.\n
        NOTE : If the return parameters is None , that does not mean there is no error message
    """

    def __init__(self) -> None:
        """
            Initialize a new ASCOM telescope object
            Args : None
            Returns : None
        """
        self.info = BasicTelescopeInfo()
        self.device = None

    def __del__(self) -> None:
        """
            Destory the ASCOM telescope object
            Args : None
            Returns : None
        """
        if self.info._is_connected:
            self.disconnect()

    def __str__(self) -> str:
        """
            Return a string representation of the ASCOM telescope object
            Args : None
            Returns : String
        """
        return """ASCOM Telescope API Interface via Alpyca"""

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
        if self.info._is_connected or self.device is not None:
            return return_error(_("Telescope has already connected"),{"info":self.info.get_dict()})
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

        self.info._is_connected = True
        res = self.get_configration()
        if res.get("status") != 0:
            return return_error(res.get("message"))
        return return_success(_("Connected to telescope successfully"),{"info":self.info.get_dict()})

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
        if not self.info._is_connected or self.device is None:
            return return_error(_("Telescope has not connected"),{})
        # If the telescope is slewing , stop it before disconnecting
        if self.info._is_slewing:
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
        self.info._is_connected = False
        return return_success(_("Disconnected from server successfully"),{})

    def reconnect(self) -> dict:
        """
            Reconnect to the ASCOM telescope
            Args : None
            Returns : dict
                status : int # status of the disconnection
                message : str # message of the disconnection
                params : dict
                    info : dict = self.info.get_dict()
            NOTE : This function is just like a mixing of connect() and disconnect()
        """
        # If the telescope is not connected, do not execute reconnecting command
        if not self.info._is_connected or self.device is None:
            return return_error(_("Telescope has not connected"),{})
        # If the telescope is slewing, stop it before reconnecting
        if self.info._is_slewing:
            logger.warning(_("Telescope is slewing, trying to reconnect"))
            res = self.reconnect_goto()
            if res.get("status")!= 0:
                logger.error(res.get("message"))
                return return_error(res.get("message"),{"error":res.get("params",{}).get("error")})
        # Trying to reconnect the telescope , but we hope that the server is working properly
        self.info._is_connected = False
        try:
            self.device.Connected = False
            sleep(1)
            self.device.Connected = True
        except DriverException as e:
            return return_error(_("Failed to reconnect telescope"),{"error": e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error while reconnecting to telescope"),{"error":e})
        # Do not forget to set the status
        self.info._is_connected = True
        return return_success(_("Reconnected telescope successfully"),{"info": self.info.get_dict()})
    
    def scanning(self) -> dict:
        """
            Scanning the telescope one by one tcp connection
            Args : None
            Returns : dict
                status : int # status of the disconnection
                message : str # message of the disconnection
                params : dict
                    telescope : list # a list of telescope found
        """
        # Though this is a little bit strange that if a telescope had already connected,
        # you can not scanning the other telescopes,this is because too many requests may make the server down
        if self.info._is_connected or self.device is not None:
            return return_error(_("Telescope has already connected"),{})
        # Scanning is just try a few port the server probably running on , the most reliable port is 11111
        telescope_list = []
        for port in range(11111,11116):
            # Trying to bind a socket port , if the port is already uesd it will cause socket.error
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                print(int(port))
                ip = "127.0.0.1:{}".format(str(port))
                s.bind(ip)
                s.shutdown(2)
            except socket.error:
                logger.info(_("{}:{} may have a server listening on").format("127.0.0.1", port))
                # Just try if backend of this port is ASCOM Remote Server
                try:
                    self.device = Telescope("127.0.0.1:"+port,0)
                    self.device.Connected = True
                    # Get the telescope's name
                    telescope_list.append(self.device.Name)
                    sleep(0.1)
                    self.device.Connected = False
                except DriverException as e:
                    logger.error(_("Failed to connect to telescope : {}").format(e))
                except exceptions.ConnectionError as e:
                    logger.error(_("Network error while scanning to telescope : {}").format(e))
        # If no telescope is found,just return an error and a empty list
        if len(telescope_list) == 0:
            return return_error(_("No telescope found"),{})
        logger.info(_("Found {} telescope , list : {}").format(len(telescope_list),telescope_list))
        return return_success(
            _("Found {} telescope").format(len(telescope_list)),
            {"telescope" : telescope_list})

    def polling(self) -> dict:
        """
            Polling the telescope newest infomation
            Args : None
            Returns : dict
                status : int # status of the disconnection
                message : str # message of the disconnection
                params : dict
                    info : dict # just return self.info.get_dict()
            NOTE : This function will not refresh the infomation of the telescope , 
                    because this will cause a huge lag and waste system usage.
        """
        if not self.info._is_connected or self.device is None:
            return return_error(_("Telescope is not connected"),{})
        res = self.info.get_dict()
        return return_success(_("Polling teleescope information"),{"info":res})

    def get_configration(self) -> dict:
        """
            Get all of the configurations needed for further processing
            Args : None
            Returns : dict
                status : int # status of the disconnection
                message : str # message of the disconnection
                params : None
        """
        if not self.info._is_connected or self.device is None:
            return return_error(_("Telescope is not connected"),{})
        logger.info(_("Trying to get telescope configuration"))
        try:
            # Basic information , all of the telescopes have these
            self.info._name = self.device.Name
            logger.debug(_(f"Telescope name : {self.info._name}"))
            # This client number is just a random number , do not have a specific meaning
            self.info._id = self.device._client_id
            logger.debug(_(f"Telescope ID : {self.info._id}"))
            self.info._description = self.device.Description
            logger.debug(_(f"Telescope description : {self.info._description}"))
            self.info._ipaddress = self.device.address
            logger.debug(_(f"Telescope IP address : {self.info._ipaddress}"))
            self.info._api_version = self.device.api_version
            logger.debug(_(f"Telescope API version : {self.info._api_version}"))

            # Get the coordinates system of the current telescope
            self.info.coord_system = self.device.EquatorialSystem

            # Get the telescope abilities , this is very important , though we will try to 
            # avoid error command send to the server if it is not available , but a simple
            # check is better solution
            # NOTE : _can_set_track_ra_rate and _can_set_track_dec_rate are moved to below part staying with rates
            self.info._can_park = self.device.CanPark
            logger.debug(_("Telescope Can Park : {}").format(self.info._can_park))
            self.info._can_set_park_postion = self.device.CanSetPark
            logger.debug(_("Telescope Can Set Parking Position : {}").format(self.info._can_set_park_postion))

            # Check if RA axis is available to goto , I don't know whether a single axis telescope can goto
            self.info._can_goto = self.device.CanMoveAxis(TelescopeAxes.axisPrimary)
            logger.debug(_(f"Telescope Can Slew : {self.info._can_goto}"))

            # I think that every telescope must can abort goto operation ,
            # If not how we to rescue it when error happens
            self.info._can_ahort_goto = True
            logger.debug(_("Telescope Can Abort Slew : {}").format(self.info._can_ahort_goto))
            self.info._can_track = self.device.CanSetTracking
            logger.debug(_("Telescope Can Track : {}").format(self.info._can_track))
            self.info._can_sync = self.device.CanSync
            logger.debug(_("Telescope Can Sync : {}").format(self.info._can_sync))
            # We are very sure about that our telescopes can slewing fast enough to catch the satelite 
            self.info._can_track_satellite = True
            logger.debug(_("Telescope Can Track Satellite : {}").format(self.info._can_track_satellite))
            self.info._can_home = self.device.CanFindHome
            logger.debug(_("Telescope Can Find Home : {}").format(self.info._can_home))

            # Check whether we can get the location of the telescope
            # If there is no location available , it will cause NotImplementedException,
            # so we just need to catch the exception and judge whether having location values
            try:
                self.info.lon = self.device.SiteLongitude
                logger.debug(_("Telescope Longitude : {}").format(self.info.lon))
                self.info.lat = self.device.SiteLatitude
                logger.debug(_("Telescope Latitude : {}").format(self.info.lat))
                self.info._can_get_location = True
            except NotImplementedException as e:
                logger.warning(_("Can not get telescope location : {}").format(e))
                self.info._can_get_location = False
                self.info.lon = ""
                self.info.lat = ""

            # This time we need to get the current status of the telescope , 
            # For example is the telescope is parked , that means we can not execute other commands,
            # before unparked the telescope . Make sure the telescope is safe
            self.info._is_parked = self.device.AtPark
            logger.debug(_("Is Telescope At Park Position : {}").format(self.info._is_parked))
            self.info._is_tracking = self.device.Tracking
            logger.debug(_("Is Telescope Tracking : {}").format(self.info._is_tracking))
            self.info._is_slewing = self.device.Slewing
            logger.debug(_("Is Telescope Slewing : {}").format(self.info._is_slewing))

            # Get telescope targeted RA and DEC values
            self.info.ra = self.device.RightAscension
            self.info.dec = self.device.Declination
            try:
                self.info.az = self.device.Azimuth
                self.info.alt = self.device.Altitude
            except NotImplementedException as e:
                logger.warning(_("Telescope do not have az/alt mode enabled"))
                self.info._can_az_alt = False
                self.info.az = ""
                self.info.alt = ""

            # If the telescope can not track , we will not try to get the settings of the tracking
            if self.info._can_track:
                # Fist we should check if the telescope is enabled to set RA axis tracking rate
                self.info._can_set_track_ra_rate = self.device.CanSetRightAscensionRate
                if self.info._can_set_track_ra_rate:
                    try:
                        # Tracking rate of the RightAscenion axis 
                        self.info.track_ra_rate = self.device.RightAscensionRate
                        self.info._can_ra_track = True
                        logger.debug(_("Telescope Right Ascension Rate : {}").format(self.info.track_ra_rate))
                    except NotImplementedException as e:
                        logger.warning(_("Telescope RA axis track mode can not be set"))
                        self.info._can_set_track_ra_rate = False
                # Just like RA , we need to check first to avoid unexpected errors
                self.info._can_set_track_dec_rate = self.device.CanSetDeclinationRate
                if self.info._can_set_track_dec_rate:
                    try:
                        # Tracking rate of the Declination axis
                        self.info.track_dec_rate = self.device.DeclinationRate
                        self.info._can_dec_track = True
                        logger.debug(_("Telescope Declination Rate : {}").format(self.info.track_dec_rate))
                    except NotImplementedException as e:
                        logger.warning(_("Telescope Dec axis track mode can not be set"))
                        self.info._can_set_track_dec_rate = False

                self.info.track_mode = self.device.TrackingRate
                logger.debug(_("Telescope Tracking Mode : {}").format(self.info.track_mode))
                self.info._can_set_track_mode = True

            # Get the maximum and minimum of the available telescope RA axis rate values
            self.info.slewing_ra_rate = self.device.AxisRates(TelescopeAxes.axisPrimary)
            self.info.max_slewing_ra_rate = self.info.slewing_ra_rate[0].Maximum
            logger.debug(_("Max Right Ascension Rate : {}").format(self.info.max_slewing_ra_rate))
            self.info.min_slewing_ra_rate = self.info.slewing_ra_rate[0].Minimum
            logger.debug(_("Min Right Ascension Rate : {}").format(self.info.min_slewing_ra_rate))

            # Before get the DEC axis, we need to know whether the telescope has DEC axis enabled
            self.info._can_dec_axis = self.device.CanMoveAxis(TelescopeAxes.axisSecondary)
            if self.info._can_dec_axis:
                self.info.slewing_dec_rate = self.device.AxisRates(TelescopeAxes.axisSecondary)
                self.info.max_slewing_dec_rate = self.info.slewing_dec_rate[0].Maximum
                logger.debug(_("Max Declination Rate : {}").format(self.info.max_slewing_dec_rate))
                self.info.min_slewing_dec_rate = self.info.slewing_dec_rate[0].Minimum
                logger.debug(_("Min Declination Rate : {}").format(self.info.min_slewing_dec_rate))
            else:
                self.info.slewing_dec_rate = []
                self.info.max_slewing_dec_rate = -1
                self.info.min_slewing_dec_rate = -1

        except InvalidOperationException as e:
            return return_error(_("Invalid operation"),{"error":e})
        except NotConnectedException as e:
            self.info._is_connected = False
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
        _path = _p(getcwd() , "config","telescope",self.info._name+".json")
        if not path.exists("config"):
            mkdir("config")
        if not path.exists(_p("config","telescope")):
            mkdir(_p("config","telescope"))
        self.info._configration = _path
        try:
            with open(_path,mode="w+",encoding="utf-8") as file:
                try:
                    file.write(dumps(self.info.get_dict(),indent=4,ensure_ascii=False))
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
        if not self.info._is_connected:
            return return_error(_("Telescope is not connected"),{})
        if self.info._is_slewing:
            return return_error(_("Telescope is slewing"),{})
        if self.info._is_parked:
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
            if not self.info._can_az_alt:
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
        if self.info.coord_system == EquatorialCoordinateType.equTopocentric and _j2000:
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
            self.info._is_connected = False
            return return_error(_("Telescope is not connected"),{"error": e})
        except DriverException as e:
            return return_error(_("Telescope driver error"),{"error": e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error": e})

        self.info._is_slewing = True
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
        if self.info._is_parked:
            return return_error(_("Telescope is parked"),{})

        # Trying to abort goto operation
        try:
            self.device.AbortSlew()
        except InvalidOperationException as e:
            return return_error(_("Invalid operation"),{"error": e})
        except NotConnectedException as e:
            self.info._is_connected = False
            return return_error(_("Telescope is not connected"),{"error": e})
        except DriverException as e:
            return return_error(_("Telescope driver error"),{"error": e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error": e})
        
        sleep(0.1)
        if not self.device.Slewing:
            self.info._is_slewing = False
            logger.info(_("Aborting goto operation successfully"))
        else:
            return return_error(_("Aborting goto operation failed"),{})
        
        # Though I don't think after such a few time the telescope will lose connection , just be careful
        try:
            current_ra = self.device.RightAscension
            current_dec = None
            if self.info._can_dec_axis:
                current_dec = self.device.Declination
        except NotConnectedException as e:
            self.info._is_connected = False
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
        if self.info._is_parked:
            return return_error(_("Telescope is parked"),{})
        try:
            status = self.device.Slewing
            ra = self.device.RightAscension
            dec = None
            if self.info._can_dec_axis:
                dec = self.device.Declination
        except NotImplementedException as e:
            self.info._is_slewing = False
            return return_error(_("Telescope is not support slewing"),{"error": e})
        except NotConnectedException as e:
            self.info._is_slewing = False
            self.info._is_connected = False
            return return_error(_("Telescope is not connected"),{"error": e})
        except DriverException as e:
            self.info._is_slewing = False
            return return_error(_("Telescope driver error"),{"error": e})
        except exceptions.ConnectionError as e:
            self.info._is_slewing = False
            return return_error(_("Network error"),{"error": e})
        
        self.info._is_slewing = status 
        
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
        if not self.info._is_connected:
            return return_error(_("Telescope is not connected"),{})
        # Check if the teleescope is parked
        if self.info._is_parked:
            return return_error(_("Telescope is parked"),{})
        # Check if the telescope is slewing
        if self.info._is_slewing:
            return return_error(_("Telescope is slewing"),{})
        try:
            ra = self.device.RightAscension
            dec = None
            if self.info._can_dec_axis:
                dec = self.device.Declination
        except NotConnectedException as e:
            self.info._is_connected = False
            return return_error(_("Telescope is not connected"),{"error":e})
        except DriverException as e:
            return return_error(_("Telescope driver error"),{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error":e})

        logger.info(_("Goto result : RA : {} DEC : {}").format(ra,dec))
        self.info.ra = ra
        self.info.dec = dec
        return return_success(_("Get goto result successfully"),{"ra":self.info.ra, "dec":self.info.dec})

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
        if not self.info._is_connected:
            return logger.error(_("Telescope is not connected"),{})
        if self.info._is_parked:
            return return_success(_("Telescope has already parked"),{})
        if not self.info._can_park:
            return return_error(_("Telescope does not support park function"),{})

        try:
            self.device.Park()
        except NotImplementedException as e:
            return return_error(_("Telescope does not support park function"),{})
        except NotConnectedException as e:
            self.info._is_connected = False
            return return_error(_("Telescope is not connected"),{"error": e})
        except SlavedException as e:
            return return_error(_("Slaved exception: {}"),{"error": e})
        except DriverException as e:
            return return_error(_("Telescope driver error"),{"error": e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error": e})
        except exceptions.ReadTimeout as e:
            return return_error(_("Read timeout: {}"),{"error":e})

        self.info._is_parked = True

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
        if not self.info._is_connected:
            return return_error(_("Telescope is not connected"),{})
        if not self.info._is_parked or not self.device.AtPark:
            return logger.error(_("Telescope is not parked"))
        
        try:
            self.device.Unpark()
        except NotImplementedException as e:
            return return_error(_("Telescope is not supported to unpark"),{"error":e})
        except NotConnectedException as e:
            self.info._is_connected = False
            return return_error(_("Telescope is not connected"),{"error":e})
        except DriverException as e:
            return return_error(_("Telescope driver error"),{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error":e})
        self.info._is_parked = False
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
        if not self.info._is_connected:
            return_error(_("Telescope is not connected"),{})
        if not self.info._can_park:
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
        if not self.info._is_connected:
            return return_error(_("Telescope is not connected"),{})
        if not self.info._can_set_park_postion:
            return return_error(_("Telescope is not support to set parking position"),{})

        # Check if the parameters are valid or just empty string
        ra = params.get('ra')
        dec = params.get('dec')

        if ra is not None and isinstance(ra,str) and re.match("\d{2}:\d{2}:\d{2}",ra):
            ra_h , ra_m , ra_s = map(int,ra.split(":"))
            self.info.park_ra = ra_h + ra_m / 60 + ra_s / 3600
        else:
            logger.warning(_("Unknown type of the RA value are specified , just use the current RA value instead"))
            self.info.park_ra = self.device.RightAscension

        if dec is not None and isinstance(dec,str) and re.match("\d{2}:\d{2}:\d{2}",dec):
            dec_h , dec_m , dec_s = map(int, dec.split(':'))
            self.info.park_dec = dec_h + dec_m / 60 + dec_s / 3600
        else:
            logger.warning(_("Unknown type of the DEC value are specified , just use the current DEC value instead"))
            self.info.park_dec = self.device.Declination

        # Trying to set the position of the park operation
        try:
            # Here is a Alpyca limitation , we can just let the telescope move to the wanted position
            # Then we can set the position of the park operation
            self.device.SlewToCoordinatesAsync(self.info.park_ra,self.info.park_dec)
            used_time = 0
            while used_time <= self.info.timeout:
                if not self.device.Slewing:
                    break
                used_time += 1
                sleep(1)
            
            self.device.SetPark()

        except NotImplementedException as e:
            self.info._can_set_park_postion = False
            return logger.error(_("Telescope is not supported to set parking position"),{"error":e})
        except InvalidValueException as e:
            return return_error(_("Invalid value was specified"),{"error":e})
        except NotConnectedException as e:
            self.info._is_connected = False
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
        if not self.info._is_connected:
            return return_error(_("Telescope is not connected"),{})
        if self.info._is_parked:
            return return_error(_("Telescope had already parked"),{})
        
        if self.info._is_slewing:
            return return_error(_("Telescope is slewing"),{})
        
        try:
            self.device.FindHome()
        except NotImplementedException as e:
            self.info._can_home = False
            return return_error(_("Telescope is not support home function"),{"error": e})
        except NotConnectedException as e:
            return return_error(_("Telescope is not connected : {}").format(e))
        except DriverException as e:
            return return_error(_("Telescope driver error"),{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error":e})

        return return_success(_("Telescope returned home successfully"),{"ra":self.info.ra, "dec":self.info.dec})  

    def get_home_status(self) -> dict:
        """
            Get the realtime home status of the telescope
            Args : None
            Returns : dict
                status : bool
        """
        if not self.info._is_connected:
            return return_error(_("Telescope is not connected"),{})
        if self.info._is_parked:
            return return_error(_("Telescope had already parked"),{})
        if not self.info._can_home:
            return return_error(_("Telescope is not supported to return home position"),{})

        try:
            status = self.device.AtHome
            self.info.ra = self.device.RightAscension
            if self.info._can_dec_axis:
                self.info.dec = self.device.Declination
            logger.debug(_("In returning home processing , RA : {} , DEC : {}").format(self.info.ra,self.info.dec))
        except NotConnectedException as e:
            return return_error(_("Telescope is not connected : {}").format(e))
        except DriverException as e:
            return return_error(_("Telescope driver error"),{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error"),{"error":e})
        
        return return_success(_("Get the home status of the telescope successfully"),{"status":status,"ra":self.info.ra,"dec":self.info.dec})
