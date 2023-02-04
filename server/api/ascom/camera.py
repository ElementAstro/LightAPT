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

from server.basic.camera import BasicCameraAPI,BasicCameraInfo
from libs.alpyca.camera import Camera,CameraStates,SensorType,ImageArrayElementTypes
from libs.alpyca.exceptions import (DriverException,
                                        NotConnectedException,
                                        NotImplementedException,
                                        InvalidValueException,
                                        InvalidOperationException)
from .exception import AscomCameraError as error
from .exception import AscomCameraSuccess as success
from .exception import AscomCameraWarning as warning

from utils.i18n import _
from ...logging import logger,return_error,return_success,return_warning

from time import sleep
from datetime import datetime
from os import path,mkdir,getcwd
from json import dumps,JSONDecodeError
from requests import exceptions
import numpy as np
import astropy.io.fits as fits
from io import BytesIO
from base64 import b64encode

CameraState = {
    CameraStates.cameraIdle : 0 , 
    CameraStates.cameraExposing : 1 , 
    CameraStates.cameraDownload : 2 ,
    CameraStates.cameraReading:3 ,
    CameraStates.cameraWaiting:4 ,
    CameraStates.cameraError : 5
}

Sensor = {
    SensorType.CMYG : "cmyg",
    SensorType.CMYG2 : "cmyg2",
    SensorType.Color : "color",
    SensorType.LRGB : "LRGB",
    SensorType.Monochrome : "monochrome",
    SensorType.RGGB : "rggb",
}

class AscomCameraAPI(BasicCameraAPI):
    """
        Ascom Camera API for LightAPT server.
        Communication with ASCOM via Alpyca.
        LightAPT server has already built in alpyca.
        You can use this API to control camera.
        NOTE : To use this , you must run ASCOM Remote too.
        https://github.com/ASCOMInitiative/alpyca
        https://github.com/ASCOMInitiative/ASCOMRemote
    """

    def __init__(self) -> None:
        """
            Initialize the ASCOM Camera object
            Args : None
            Return : None
        """
        self.info = BasicCameraInfo()
        self.device = None

    def __del__(self) -> None:
        """
            Delete the camera object
            Args : None
            Return : None
        """
        if self.info._is_connected:
            self.disconnect()

    def __str__(self) -> str:
        return "LightAPT Ascom API Interface via Alpyca"

    # #################################################################
    #
    # Public methods from BasicCameraAPI
    #
    # #################################################################
    
    def connect(self, params: dict) -> dict:
        """
            Connect to ASCOM camera | 连接ASCOM相机
            Args : 
                host : "127.0.0.1",
                port : 8888,
                device_number : int # default is 0
            Return  : dict
                info : BasicCameraInfo object
        """
        if self.info._is_connected:
            return return_warning(_("Camera is connected"),{})
        if self.device is not None:
            logger.warning(error.OneDevice.value)
            return return_warning(error.OneDevice.value,{"error":error.OneDevice.value})
        host = params.get('host')
        port = params.get('port')
        device_number = params.get('device_number')
        if host is None:
            logger.warning(error.NoHostValue.value)
            host = "127.0.0.1"
        if port is None:
            logger.warning(error.NoPortValue.value)
            port = 11111
        if device_number is None:
            logger.warning(error.NoDeviceNumber.value)
            device_number = 0
        try:
            self.device = Camera(host + ":" + str(port), device_number)
            self.device.Connected = True
        except DriverException as e:
            return return_error(_(f"Failed to connect to device on {host}:{port}"))
        except exceptions.ConnectionError as e:
            return return_error(_("Network error while connecting to camera"),{"error" : e})
        self.info._is_connected = True
        self.info._type = "ascom"
        res = self.get_configration()
        if res.get('status') != 0:
            return return_error(_(f"Failed tp load camera configuration"),{})
        return return_success(_("Connect to camera successfully"),{"info":self.info.get_dict()})

    def disconnect(self) -> dict:
        """
            Disconnect from ASCOM camera
            Args: None
            Return : dict
            NOTE : This function must be called before destory all server
        """
        if not self.info._is_connected or self.device is None:
            return return_warning(_(error.NotConnected.value.value),{})
        try:
            self.device.Connected = False
        except DriverException as e:
            return return_error(error.DriverError.value.value,{"error" : e})
        except exceptions.ConnectionError as e:
            return return_error(error.NetworkError.value.value,{"error" : e})
        self.device = None
        self.info._is_connected = False
        return return_success(_("Disconnect from camera successfully"),{"params":None})

    def reconnect(self) -> dict:
        """
            Reconnect to ASCOM camera | 重连ASCOM相机
            Args: None
            Return : dict
        """
        if self.device is None or not self.info._is_connected:
            return return_warning(_(error.NotConnected.value),{}) 
        try:
            self.device.Connected = False
            sleep(1)
            self.device.Connected = True
        except DriverException as e:
            return return_error(_(f"Failed to reconnect to device"),{"error" : e})
        except ConnectionError as e:
            return return_error(error.NetworkError.value.value,{"error" : e})
        self.info._is_connected = True
        return return_success(success.ReconnectSuccess.value,{})

    def scanning(self) -> dict:
        """
            Scan ASCOM camera | 扫描ASCOM相机
            Args: None
            Return : dict
                camera : list
        """
        if self.device is not None and self.info._is_connected:
            return return_warning(warning.DisconnectBeforeScanning.value,{"warning":warning.DisconnectBeforeScanning})
        camera_list = []
        logger.info(_("Scanning camera : {}").format(camera_list))
        return return_success(success.ScanningSuccess.value,{"camera":camera_list})

    def polling(self) -> dict:
        """
            Polling camera information | 刷新相机信息
            Args: None
            Return : dict
                info : BasicCameraInfo object
        """
        if self.device is None or not self.info._is_connected:
            return return_warning(_(error.NotConnected.value),{})
        return return_success(success.PollingSuccess.value,{"info":self.info.get_dict()})

    def get_configration(self) -> dict:
        """
            Get camera infomation | 获取相机信息
            Args: None
            Return : dict
                info : BasicCameraInfo object
        """
        if self.device is None or not self.info._is_connected:
            return return_warning(_(error.NotConnected.value),{})
        try:
            self.info._name = self.device.Name
            logger.debug(_("Camera name : {}").format(self.info._name))
            self.info._id = self.device._client_id
            logger.debug(_("Camera ID : {}").format(self.info._id))
            self.info._description = self.device.Description
            logger.debug(_("Camera description : {}").format(self.info._description))
            self.info._ipaddress = self.device.address
            logger.debug(_("Camera IP address : {}").format(self.info._ipaddress))
            self.info._api_version = self.device.api_version
            logger.debug(_("Camera API version : {}").format(self.info._api_version))

            self.info._can_binning = self.device.CanAsymmetricBin
            logger.debug(_("Can camera set binning mode : {}").format(self.info._can_binning))
            self.info._binning = [self.device.BinX, self.device.BinY]
            logger.debug(_("Camera current binning mode : {}").format(self.info._binning))

            self.info._can_cooling = self.device.CanSetCCDTemperature
            logger.debug(_("Can camera set cooling : {}").format(self.info._can_cooling))
            self.info._can_get_coolpower = self.device.CanGetCoolerPower
            logger.debug(_("Can camera get cooling power : {}").format(self.info._can_get_coolpower))
            if self.info._can_cooling:
                try:
                    self.info._temperature = self.device.CCDTemperature
                except InvalidValueException as e:
                    logger.debug(error.CanNotGetTemperature)
            if self.info._can_get_coolpower:
                try:
                    self.info._cool_power = self.device.CoolerPower
                except InvalidValueException as e:
                    logger.debug(error.CanNotGetPower)
            try:
                self.info._gain = self.device.Gain
                logger.debug(_("Camera current gain : {}").format(self.info._gain))
                self.info._max_gain = self.device.GainMax
                logger.debug(_("Camera max gain : {}").format(self.info._max_gain))
                self.info._min_gain = self.device.GainMin
                logger.debug(_("Camera min gain : {}").format(self.info._min_gain))
                self.info._can_gain = True
                logger.debug(_("Can camera set gain : {}").format(self.info._can_gain))
            except NotImplementedException:
                self.info._max_gain = 0
                self.info._min_gain = 0
                self.info._can_gain = False
                logger.debug(_("Can camera set gain : {}").format(self.info._can_gain))
            
            self.info._can_guiding = self.device.CanPulseGuide
            logger.debug(_("Can camera guiding : {}").format(self.info._can_guiding))
            self.info._can_has_shutter = self.device.HasShutter
            logger.debug(_("Can camera has shutter : {}").format(self.info._can_has_shutter))
            self.info._can_iso = False
            logger.debug(_("Can camera set iso : {}").format(self.info._can_iso))
            try:
                self.info._offset = self.device.Offset
                logger.debug(_("Camera current offset : {}").format(self.info._offset))
                self.info._max_offset = self.device.OffsetMax
                logger.debug(_("Camera max offset : {}").format(self.info._max_offset))
                self.info._min_offset = self.device.OffsetMin
                logger.debug(_("Camera min offset : {}").format(self.info._min_offset))
                self.info._can_offset = True
                logger.debug(_("Can camera set offset : {}").format(self.info._can_offset))
            except InvalidOperationException:
                self.info._max_offset = 0
                self.info._min_offset = 0
                self.info._can_offset = False
                logger.debug(_("Can camera set offset : {}").format(self.info._can_offset))

            self.info._is_cooling = self.device.CoolerOn
            logger.debug(_("Is camera cooling : {}").format(self.info._is_cooling))
            self.info._is_exposure = CameraState.get(self.device.CameraState)
            logger.debug(_("Is camera exposure : {}").format(self.info._is_exposure))

            self.info._is_imageready = self.device.ImageReady
            logger.debug(_("Is camera image ready : {}").format(self.info._is_imageready))

            self.info._max_exposure = self.device.ExposureMax
            logger.debug(_("Camera max exposure : {}").format(self.info._max_exposure))
            self.info._min_exposure = self.device.ExposureMin
            logger.debug(_("Camera min exposure : {}").format(self.info._min_exposure))
            self.info._min_exposure_increment = self.device.ExposureResolution
            logger.debug(_("Camera min exposure increment : {}").format(self.info._min_exposure_increment))
            self.info._max_binning = [self.device.MaxBinX,self.device.MaxBinY]
            logger.debug(_("Camera max binning : {}").format(self.info._max_binning))

            self.info._height = self.device.CameraYSize
            logger.debug(_("Camera frame height : {}").format(self.info._height))
            self.info._width = self.device.CameraXSize
            logger.debug(_("Camera frame width : {}").format(self.info._width))
            self.info._max_height = self.info._height
            self.info._max_width = self.info._width
            self.info._min_height = self.info._height
            self.info._min_width = self.info._width
            self.info._depth = self.device.ImageArrayInfo
            try:
                self.info._bayer_offset_x = self.device.BayerOffsetX
                logger.debug(_("Camera bayer offset x : {}").format(self.info._bayer_offset_x))
                self.info._bayer_offset_y = self.device.BayerOffsetY
                logger.debug(_("Camera bayer offset y : {}").format(self.info._bayer_offset_y))
                self.info._bayer_pattern = 0
                self.info._is_color = True
            except NotImplementedException:
                self.info._bayer_offset_x = 0
                self.info._bayer_offset_y = 0
                self.info._bayer_pattern = ""
                self.info._is_color = False
            self.info._pixel_height = self.device.PixelSizeY
            logger.debug(_("Camera pixel height : {}").format(self.info._pixel_height))
            self.info._pixel_width = self.device.PixelSizeX
            logger.debug(_("Camera pixel width : {}").format(self.info._pixel_width))
            self.info._max_adu = self.device.MaxADU
            logger.debug(_("Camera max ADU : {}").format(self.info._max_adu))
            self.info._start_x = self.device.StartX
            logger.debug(_("Camera start x : {}").format(self.info._start_x))
            self.info._start_y = self.device.StartY
            logger.debug(_("Camera start y : {}").format(self.info._start_y))
            self.info._subframe_x = self.device.NumX
            logger.debug(_("Camera subframe x : {}").format(self.info._subframe_x))
            self.info._subframe_y = self.device.NumY
            logger.debug(_("Camera subframe y : {}").format(self.info._subframe_y))
            self.info._sensor_name = self.device.SensorName
            logger.debug(_("Camera sensor name : {}").format(self.info._sensor_name))
            self.info._sensor_type = Sensor.get(self.device.SensorType)
            logger.debug(_("Camera sensor type : {}").format(self.info._sensor_type))

        except NotConnectedException as e:
            return return_error(_(error.NotConnected.value,{}))
        except DriverException as e:
            return return_error(_(error.DriverError.value,{"error" : e}))
        except ConnectionError as e:
            return return_error(error.NetworkError.value.value,{"error":e})
        return return_success(success.GetConfigrationSuccess.value,{"info" : self.info.get_dict()})

    def set_configration(self, params: dict) -> dict:
        return super().set_configration(params)

    def load_configration(self) -> dict:
        return super().load_configration()

    def save_configration(self) -> dict:
        """
            Save configration of camera
            Args : None
            Return : dict
        """
        _p = path.join
        _path = _p(getcwd() , "config","camera",self.info._name+".json")
        if not path.exists("config"):
            mkdir("config")
        if not path.exists(_p("config","camera")):
            mkdir(_p("config","camera"))
        self.info._configration = _path
        try:
            with open(_path,mode="w+",encoding="utf-8") as file:
                try:
                    file.write(dumps(self.info.get_dict(),indent=4,ensure_ascii=False))
                except JSONDecodeError as e:
                    return return_error(_("JSON decoder error , error : {}").format(e),{})
        except OSError as e:
            return return_error(_("Failed to write configuration to file , error : {}").format(e),{})
        return return_success(success.SaveConfigrationSuccess.value,{})

    def get_parameter(self, params : dict) -> dict:
        """
            Get the specified parameter and return the value
            Args : 
                params : dict
                    name : str # name of the parameter
        """

    def set_parameter(self, params = {}) -> dict:
        """
            Set the specified parameter of the camera
            Args :
                params : dict
                    name : str
                    value : str
        """

    # #################################################################
    # Camera Control
    # #################################################################

    def start_exposure(self, params : dict) -> dict:
        """
            Start exposure function | 开始曝光
            Args : 
                params : dict
                    exposure : float
                    is_dark : bool
            Returns : dict
            NOTE : This function is a non-blocking function
        """
        if self.device is None or not self.info._is_connected:
            return return_warning(_(error.NotConnected.value),{})

        exposure = params.get("exposure")
        is_dark = params.get("is_dark")

        if exposure is None or not self.info._min_exposure < exposure < self.info._max_exposure:
            return return_error(error.InvalidExposureValue.value,{"error":exposure})
        
        if is_dark:
            logger.debug(_("Prepare to create a dark image"))

        logger.info(_("Start exposure ..."))
        try:
            self.device.StartExposure(exposure,is_dark)
            self.info._is_exposure = True
            sleep(0.1)
            if not self.device.ImageReady and self.device.CameraState == CameraStates.cameraExposing:
                self.info._last_exposure = exposure
            else:
                return return_error(error.StartExposureError.value,{"error" : error.StartExposureError.value})
        except InvalidValueException as e:
            return return_error(error.InvalidExposureValue.value,{"error":e})
        except InvalidOperationException as e:
            return return_error(error.InvalidOperation.value,{"error":e})
        except NotConnectedException as e:
            return return_error(_(error.NotConnected.value),{"error":e})
        except DriverException as e:
            return return_error(error.DriverError.value,{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(error.NetworkError.value,{"error":e})

        return return_success(success.StartExposureSuccess.value,{})

    def abort_exposure(self, params : dict) -> dict:
        """
            Abort exposure operation | 停止曝光
            Args: None
            Return : dict
            NOTE : This function must be called if exposure is still in progress when shutdown server
        """
        if not self.info._is_connected:
            return return_error(_(error.NotConnected.value),{})
        if not self.info._is_exposure:
            return return_warning(_("Exposure not started"),{})
        try:
            self.device.StopExposure()
            sleep(0.5)
            if self.device.CameraState == CameraStates.cameraIdle:
                return return_success(success.AbortExposureSuccess.value,{})
            else:
                return return_error(error.AbortExposureError.value,{"error": error.AbortExposureError.value})
        except NotImplementedException as e:
            return return_error(_("Sorry,exposure is not supported to stop"),{"error":e})
        except NotConnectedException as e:
            return return_error(_(error.NotConnected.value),{"error":e})
        except InvalidOperationException as e:
            return return_error(error.InvalidOperation.value,{"error":e})
        except DriverException as e:
            return return_error(error.DriverError.value,{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(_("Network error while get camera configuration"),{"error":e})
        finally:
            self.info._is_exposure = False
        
    def get_exposure_status(self) -> dict:
        """
            Get exposure status | 获取曝光状态
            Args: None
            Return : dict
                status : int
        """
        if not self.info._is_connected:
            return return_error(error.NotConnected.value,{"error": error.NotConnected.value})
        if not self.info._is_exposure:
            return return_warning(_("Exposure not started"),{})

        try:
            status = CameraState.get(self.device.CameraState)
            self.info._is_exposure = status == CameraStates.cameraExposing
        except NotConnectedException as e:
            return return_error(_(error.NotConnected.value),{"error":e})
        except DriverException as e:
            return return_error(error.DriverError.value,{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(error.NetworkError.value,{"error":e})

        return return_success(_("Get camera exposure status successfully"),{"status":self.info._is_exposure})

    def get_exposure_result(self) -> dict:
        """
            Get exposure result when exposure successful | 曝光成功后获取图像
            Args: None
            Return : dict
                image : binary image
                info : image info
            NOTE : Format!
        """
        if not self.info._is_connected:
            return return_error(error.NotConnected.value,{"error": error.NotConnected.value})
        if self.info._is_exposure:
            return return_error(_("Exposure is still in progress"),{"error": "Exposure is still in progress"})
        try:
            hist = None
            base64_encode_img = None
            info = None

            used_time = 0
            while not self.device.ImageReady and used_time <= self.info._timeout:
                sleep(0.5)
                used_time += 0.5
            imgdata = self.device.ImageArray
            if self.info._depth is None:
                img_format = self.device.ImageArrayInfo
                if img_format.ImageElementType == ImageArrayElementTypes.Int32:
                    if self.info._max_adu <= 65535:
                        self.info._depth = 16
                    else:
                        self.info._depth = 32
                elif img_format.ImageElementType == ImageArrayElementTypes.Double:
                    self.info._depth = 64
                if img_format.Rank == 2:
                    self.info._imgarray = True
                else:
                    self.info._imgarray = False
                logger.debug(_(f"Camera Image Array : {self.info._imgarray}"))
            img = None
            if self.info._depth == 16:
                img = np.uint16
            elif self.info._depth == 32:
                img = np.int32
            else:
                img = np.float64
            
            if self.info._imgarray:
                nda = np.array(imgdata, dtype=img).transpose()
            else:
                nda = np.array(imgdata, dtype=img).transpose(2,1,0)
            # Create a histogram of the image
            if self.info._depth == 16:
                hist , bins= np.histogram(nda,bins=[i for i in range(1,256)])
            elif self.info._depth == 32:
                hist, bins= np.histogram(nda,bins=[i for i in range(1,65536)])
            # Create a base64 encoded image
            bytesio = BytesIO()
            np.savetxt(bytesio, nda)
            base64_encode_img = b64encode(bytesio.getvalue())
            # Create a image information dict
            info = {
                "exposure" : self.info._last_exposure
            }
            if self.info._can_save:
                logger.debug(_("Start saving image data in fits"))
                hdr = fits.Header()
                hdr['COMMENT'] = 'FITS (Flexible Image Transport System) format defined in Astronomy and'
                hdr['COMMENT'] = 'Astrophysics Supplement Series v44/p363, v44/p371, v73/p359, v73/p365.'
                hdr['COMMENT'] = 'Contact the NASA Science Office of Standards and Technology for the'
                hdr['COMMENT'] = 'FITS Definition document #100 and other FITS information.'

                if self.info._depth == 16:
                    hdr['BZERO'] = 32768.0
                    hdr['BSCALE'] = 1.0
                hdr['EXPOSURE'] = self.info._last_exposure
                hdr['TIME'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                hdr['BINX'] = self.info._binning[0]
                hdr['BINY'] = self.info._binning[1]
                hdr['INSTRUME'] = self.info._sensor_type

                if self.info._can_gain:
                    hdr['GAIN'] = self.info._gain
                if self.info._can_offset:
                    hdr['OFFSET'] = self.info._offset
                if self.info._can_iso:
                    hdr['ISO'] = self.info._iso

                hdr["SOFTWARE"] = "LightAPT ASCOM Client"

                hdu = fits.PrimaryHDU(nda, header=hdr)

                _path = "Image_" + "001" + ".fits"
                try:
                    hdu.writeto(_path, overwrite=True)
                except OSError as e:
                    logger.error(_(f"Error writing image , error : {e}"))
        except InvalidOperationException as e:
            return return_error(_("No image data available"),{"error":e})
        except NotConnectedException as e:
            return return_error(_(error.NotConnected.value),{"error":e})
        except DriverException as e:
            return return_error(error.DriverError.value,{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(error.NetworkError.value,{"error":e})
        
        return return_success(_("Save image successfully"),{"image" : nda.tolist(),"histogram" : hist.tolist(),"info" : info})
        
    def cooling(self, params: dict) -> dict:
        """
            Start or stop camera cooling mode
            Args :
                params : dict
                    enable : bool
            Return : dict
        """
        if not self.info._is_connected:
            return return_error(error.NotConnected.value,{"error": error.NotConnected.value})
        if not self.info._can_cooling:
            return return_error(error.CanNotCooling.value,{"error": error.CanNotCooling.value})

        if params is None or not isinstance(params, dict):
            return return_error(error.InvalidCoolingValue.value,{"error": error.InvalidCoolingValue.value})
        enable = params.get('enable')
        if enable is None or not isinstance(enable,bool):
            return return_error(error.InvalidCoolingValue.value,{"error": error.InvalidCoolingValue.value})
        
        try:
            self.device.CoolerOn = enable
        except NotImplementedException as e:
            self.info._can_cooling = False
            return return_error(error.CanNotCooling.value,{"error": e})
        except NotConnectedException as e:
            self.info._is_connected = False
            return return_error(error.NotConnected.value,{"error":e})
        except DriverException as e:
            return return_error(error.DriverError.value,{"error" : e})
        except exceptions.ConnectionError as e:
            return return_error(error.NetworkError.value,{"error": e})

        self.info._is_cooling = True

        return return_success(_("Camera started cooling successfully"),{})

    def cooling_to(self, params: dict) -> dict:
        """
            Cooling camera to the specified temperature
            Args :
                params : dict
                    temperature : float
            Return : dict
        """
        if not self.info._is_connected:
            return return_error(error.NotConnected.value,{"error": error.NotConnected.value})
        if not self.info._can_cooling:
            return return_error(error.CanNotCooling.value,{"error": error.CanNotCooling.value})
        if not self.info._is_cooling:
            return return_error(error.CanNotCooling.value,{"error": error.CanNotCooling.value})

        if params is None or not isinstance(params, dict):
            return return_error(error.InvalidTemperatureValue.value,{"error": error.InvalidTemperatureValue.value})
        temperature = params.get('temperature')
        if temperature is None or not isinstance(temperature,float) or not -60 < temperature < 40:
            return return_error(error.InvalidTemperatureValue.value,{"error": error.InvalidTemperatureValue.value})

        try:
            self.device.CCDTemperature = temperature
        except InvalidValueException as e:
            return return_error(error.InvalidTemperatureValue.value,{"error":e})
        except NotImplementedException as e:
            self.info._can_cooling = False
            return return_error(error.CanNotCooling.value,{"error":e})
        except NotConnectedException as e:
            self.info._is_connected = False
            return return_error(error.NotConnected.value,{"error":e})
        except DriverException as e:
            return return_error(error.DriverError.value,{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(error.NetworkError.value,{"error":e})

        return return_success(success.CoolingToSuccess.value,{})

    def get_cooling_power(self, params: dict) -> dict:
        """
            Get the cooling power of the camera
            Args : None
            Return : dict
                power : float
        """
        if not self.info._is_connected:
            return return_error(error.NotConnected.value,{"error": error.NotConnected.value})
        if not self.info._can_cooling:
            return return_error(error.CanNotCooling.value,{"error": error.CanNotCooling.value})
        if not self.info._can_get_coolpower:
            return return_error(error.CanNotGetCoolingPower.value,{"error": error.CanNotGetCoolingPower.value})
        if not self.info._is_cooling:
            return return_error(error.CanNotCooling.value,{"error": error.CanNotCooling.value})

        try:
            self.info._cool_power = self.device.CoolerPower
        except NotImplementedException as e:
            self.info._can_cooling = False
            self.info._can_get_coolpower = False
            return return_error(error.CanNotGetCoolingPower.value,{"error":e})
        except NotConnectedException as e:
            self.info._is_connected = False
            return return_error(error.NotConnected.value,{"error":e})
        except DriverException as e:
            return return_error(error.DriverError.value,{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(error.NetworkError.value,{"error":e})

        return return_success(success.GetCoolingPowerSuccess.value,{"power":self.info._cool_power})

    def get_cooling_status(self, params: dict) -> dict:
        """
            Get the current status of the cooling
            Args : None
            Return : dict
                status : bool # True if cooling
        """
        if not self.info._is_connected:
            return return_error(error.NotConnected.value,{"error": error.NotConnected.value})
        if not self.info._can_cooling:
            return return_error(error.CanNotCooling.value,{"error": error.CanNotCooling.value})
        
        try:
            self.info._is_cooling = self.device.CoolerOn
        except NotImplementedException as e:
            self.info._can_cooling = False
            return return_error(error.CanNotCooling.value,{"error": e})
        except NotConnectedException as e:
            self.info._is_connected = False
            return return_error(error.NotConnected.value,{"error": e})
        except DriverException as e:
            return return_error(error.DriverError.value,{"error": e})
        except exceptions.ConnectionError as e:
            return return_error(error.NetworkError.value,{"error": e})

        return return_success(success.GetCoolingStatusSuccess.value,{"status" : self.info._is_cooling})

    def get_current_temperature(self, params: dict) -> dict:
        """
            Get the current temperature of the camera
            Args : None
            Return : dict
                temperature : float
        """
        if not self.info._is_connected:
            return return_error(error.NotConnected.value,{"error": error.NotConnected.value})
        if not self.info._can_cooling:
            return return_error(error.CanNotCooling.value,{"error": error.CanNotCooling.value})
        if not self.info._is_cooling:
            return return_error(error.CanNotCooling.value,{"error": error.CanNotCooling.value})

        try:
            self.info._temperature = self.device.CCDTemperature
        except InvalidValueException as e:
            return return_error(error.CanNotGetTemperature.value,{"error":e})
        except NotImplementedException as e:
            self.info._can_cooling = False
            return return_error(error.CanNotCooling.value,{"error":e})
        except NotConnectedException as e:
            self.info._is_connected = False
            return return_error(error.NotConnected.value,{"error":e})
        except DriverException as e:
            return return_error(error.DriverError.value,{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(error.NetworkError.value,{"error":e})
        
        return return_success(success.GetCoolingTemperatureSuccess.value,{'temperature':self.info._temperature})

    # #################################################################
    # Camera Settings
    # #################################################################

    def get_camera_roi(self , params : dict) -> dict:
        """
            Get the current frame settings of the camera
            Args : None
            Return : dict
                roi : dict
                    height : int
                    width : int
                    start_x : int
                    start_y : int
        """
        if not self.info._is_connected:
            return return_error(error.NotConnected.value,{"error": error.NotConnected.value})

        try:
            self.info._height = self.device.NumY
            self.info._width = self.device.NumY
            self.info._start_x = self.device.StartX
            self.info._start_y = self.device.StartY
        except NotConnectedException as e:
            self.info._is_connected = False
            return return_error(error.NotConnected.value,{"error": e})
        except DriverException as e:
            return return_error(error.DriverError.value,{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(error.NetworkError.value,{"error":e})

        return return_success(success.GetROISuccess.value,{
            "height" : self.info._height,
            "width" : self.info._width,
            "start_x" : self.info._start_x,
            "start_y" : self.info._start_y
        })

    def set_camera_roi(self , params : dict) -> dict:
        """
            Set the frame of the current camera
            Args :
                params : dict
                    height : int
                    width : int
                    start_x : int
                    start_y : int
            Return : dict
        """
        if not self.info._is_connected:
            return return_error(error.NotConnected.value,{"error": error.NotConnected.value})

        if self.info._max_height is None or self.info._max_width is None:
            self.get_camera_roi({})

        height = params.get('height',self.info._max_height)
        width = params.get('width',self.info._max_width)
        start_x = params.get('start_x',0)
        start_y = params.get('start_y',0)

        if (not 0 < height <= self.info._max_height / self.info._binning[0] or 
            not 0 < width <= self.info._max_width / self.info._binning[1] or 
            not 0 <= start_x <= self.info._max_width or 
            not 0 <= start_y <= self.info._max_height):
            return return_error(error.InvalidROIValue.value,{"error" : error.InvalidROIValue.value})

        try:
            self.device.StartX = start_x
            self.device.StartY = start_y
            self.device.NumX = width
            self.device.NumY = height
        except NotConnectedException as e:
            self.info._is_connected = False
            return return_error(error.NotConnected.value,{"error": e})
        except DriverException as e:
            return return_error(error.DriverError.value,{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(error.NetworkError.value,{"error":e})

        return return_success(success.SetROISuccess.value,{})

    def get_gain(self , params : dict) -> dict:
        """
            Get the current gain value of the camera
            Args : None
            Return : dict
                gain : int
        """
        if not self.info._is_connected:
            return return_error(error.NotConnected.value,{"error": error.NotConnected.value})
        if not self.info._can_gain:
            return return_error(error.CanNotGetGain.value,{"error": error.CanNotGetGain.value})

        try:
            self.info._gain = self.device.Gain
        except NotImplementedException as e:
            self.info._can_gain = False
            return return_error(error.CanNotGetGain.value,{"error":e})
        except NotConnectedException as e:
            self.info._is_connected = False
            return return_error(error.NotConnected.value,{"error":e})
        except DriverException as e:
            return return_error(error.DriverError.value,{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(error.NetworkError.value,{"error":e})

        return return_success(success.GetGainSuccess.value,{"gain":self.info._gain})


    def set_gain(self , params : dict) -> dict:
        """
            Set the gain of the camera
            Args : 
                params : dict
                    gain : int
            Return : dict
        """
        if not self.info._is_connected:
            return return_error(error.NotConnected.value,{"error": error.NotConnected.value})
        if not self.info._can_gain:
            return return_error(error.CanNotGetGain.value,{"error": error.CanNotGetGain.value})

        gain = params.get('gain', None)
        if gain is None or not 0 <= gain <= self.info._max_gain:
            return return_error(error.InvalidGainValue.value,{"error": error.InvalidGainValue.value})
        
        try:
            self.device.Gain = gain
        except InvalidValueException as e:
            return return_error(error.InvalidGainValue.value,{"error":e})
        except NotImplementedException as e:
            self.info._can_gain = False
            return return_error(error.CanNotGetGain.value,{"error":e})
        except NotConnectedException as e:
            self.info._is_connected = False
            return return_error(error.NotConnected.value,{"error":e})
        except DriverException as e:
            return return_error(error.DriverError.value,{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(error.NetworkError.value,{"error":e})

        return return_success(success.SetGainSuccess.value,{})

    def get_offset(self , params : dict) -> dict:
        """
            Get the current offset value of the camera
            Args : None
            Return : dict
                offset : int
        """
        if not self.info._is_connected:
            return return_error(error.NotConnected.value,{"error": error.NotConnected.value})
        if not self.info._can_offset:
            return return_error(error.CanNotGetOffset.value,{"error": error.CanNotGetOffset.value})

        try:
            self.info._offset = self.device.Offset
        except NotImplementedException as e:
            self.info._can_offset = False
            return return_error(error.CanNotGetOffset.value,{"error": e})
        except NotConnectedException as e:
            self.info._is_connected = False
            return return_error(error.NotConnected.value,{"error":e})
        except DriverException as e:
            return return_error(error.DriverError.value,{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(error.NetworkError.value,{"error":e})

        return return_success(success.GetOffsetSuccess.value,{"offset" : self.info._offset})

    def set_offset(self, params : dict) -> dict:
        """
            Set the offset value of the current camera
            Args : 
                params : dict
                    offset : int
            Return : dict
        """
        if not self.info._is_connected:
            return return_error(error.NotConnected.value,{"error": error.NotConnected.value})
        if not self.info._can_offset:
            return return_error(error.CanNotSetOffset.value,{"error": error.CanNotSetOffset.value})

        offset = params.get('offset', None)
        if offset is None or not 0 <= offset <= self.info._max_offset:
            return return_error(error.InvalidOffsetValue.value,{"error": error.InvalidOffsetValue.value})
        
        try:
            self.device.Offset = offset
        except InvalidValueException as e:
            return return_error(error.InvalidOffsetValue.value,{"error":e})
        except NotImplementedException as e:
            self.info._can_offset = False
            return return_error(error.CanNotSetOffset.value,{"error": e})
        except NotConnectedException as e:
            self.info._is_connected = False
            return return_error(error.NotConnected.value,{"error":e})
        except DriverException as e:
            return return_error(error.DriverError.value,{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(error.NetworkError.value,{"error":e})

        return return_success(success.SetOffsetSuccess.value,{})

    def get_binning(self , params = {}) -> dict:
        """
            Get the current binning mode of the camera
            Args : None
            Returns : dict
                binning : list # [bin_x,bin_y]
        """
        if not self.info._is_connected:
            return return_error(error.NotConnected.value,{"error": error.NotConnected.value})
        if not self.info._can_binning:
            return return_error(error.CanNotGetBinning.value,{"error": error.CanNotSetGinning.value})

        try:
            self.info._binning = [self.device.BinX,self.device.BinY]
        except NotConnectedException as e:
            self.info._is_connected = False
            return return_error(error.NotConnected.value,{"error":e})
        except DriverException as e:
            return return_error(error.DriverError.value,{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(error.NetworkError.value,{"error":e})

        return return_success(success.GetBinningSuccess.value,{"binning":self.info._binning})

    def set_binning(self , params = {}) -> dict:
        """
            Set the binning mode of the camera
            Args :
                params : dict
                    binning : list # [bin_x,bin_y]
            Return : dict
        """
        if not self.info._is_connected:
            return return_error(error.NotConnected.value,{"error": error.NotConnected.value})
        if not self.info._can_binning:
            return return_error(error.CanNotGetBinning.value,{"error": error.CanNotSetGinning.value})

        binning = params.get('binning')
        if binning is None or not isinstance(binning, list):
            return return_error(error.InvalidBinningValue.value,{"error": error.InvalidBinningValue.value})
        try:
            bin_x = binning[0]
            bin_y = binning[1]
        except IndexError as e:
            return return_error(error.InvalidBinningValue.value,{"error":e})
        
        try:
            self.device.BinX = bin_x
            self.device.BinY = bin_y
        except InvalidValueException as e:
            return return_error(error.InvalidBinningValue.value,{"error":e})
        except NotConnectedException as e:
            self.info._is_connected = False
            return return_error(error.NotConnected.value,{"error":e})
        except DriverException as e:
            return return_error(error.DriverError.value,{"error":e})
        except exceptions.ConnectionError as e:
            return return_error(error.NetworkError.value,{"error":e})

        return return_success(_("Set camera binning successfully"))

import asyncio
import tornado
import tornado.ioloop
import tornado.websocket

class WSAscomCamera(object):
    """
        Websocket camera wrapper class for AscomCameraAPI class
    """

    def __init__(self) -> None:
        """
            Initial constructor for WSCamera class methods 
            Args :
                ws : a websocket instance
            Returns : None
        """
        self.device = None
        self.ws = None
        self.blob = asyncio.Event()
        self.thread = None
        self.device = AscomCameraAPI()

    def __str__(self) -> str:
        """
            Returns the name of the WSCamera class
            Args : None
            Returns : None
        """
        return "LightAPT Ascom Websocket Camera API class"

    async def connect(self , params : dict , ws = None) -> dict:
        """
            Async connect to the camera \n
            Args : 
                params : dict
                    type : str # ascom or indi
                    device_name : str
                    host : str # both indi and ascom default is "127.0.0.1"
                    port : int # for indi port is 7624 , for ascom port is 11111
            Returns : dict
        """
        if self.device is not None:
            logger.info(_("Disconnecting from existing camera ..."))
            await self.disconnect()

        _device_name = params.get('device_name')

        if _device_name is None:
            return (_("Device name must be specified"))
        
        return self.device.connect(params=params)

    async def disconnect(self,params = {} , ws = None) -> dict:
        """
            Async disconnect from the device\n
            Args : None
            Returns : dict
        """
        if self.device is None:
            return return_error(_("Camera is not connected , please do not execute disconnect command"))
        
        return self.device.disconnect()

    async def reconnect(self,params = {} , ws = None) -> dict:
        """
            Async reconnect to the device\n
            Args : None
            Returns : dict
            NOTE : This function is just allowed to be called when the camera had already connected
        """
        if self.device is None:
            return return_error(_("Camera is not connected , please do not execute reconnect command"))

        return self.device.reconnect()

    async def scanning(self,params = {} , ws = None) -> dict:
        """
            Async scanning all of the devices available\n
            Args : None
            Returns : dict
        """
        if self.device is not None or self.device.info._is_connected:
            return return_error(_("Camera had already been connected , please do not execute scanning command"))

        return self.device.scanning()

    async def polling(self,params = {} , ws = None) -> dict:
        """
            Async polling method to get the newest camera information\n
            Args : None
            Returns : dict
        """
        if self.device is None:
            return return_error(_("Camera is not connected , please do not execute polling command"))

        return self.device.polling()

    async def get_parameter(self , params = {} , ws = None) -> dict:
        """
            Get the specified parameter value of the camera\n
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
            Set the specified parameter value of the camera\n
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

    async def start_exposure(self, params = {} , ws = None) -> dict:
        """
            Async start exposure event
            Args : 
                params : dict
                    exposure : float
                ws : tornado.websocket.WebsocketHandler
            Returns : dict
        """
        if self.device is None:
            return return_error(_("Camera int not connected , please do not execute start exposure command"))

        exposure = params.get('exposure')

        if exposure is None or not 0 <= exposure <= 3600:
            return return_error(_("A reasonable exposure value is required"))
        
        self.blob.clear()
        
        res = self.device.start_exposure(params)
        if res.get('status') != 0:
            return res

        tornado.ioloop.IOLoop.instance().add_callback(self.exposure_thread)

        return return_success(_("Exposure started successfully"),{})

    async def abort_exposure(self,params = {} , ws = None) -> dict:
        """
            Async abort the exposure operation
            Args : None
            Returns : None
        """
        if self.device is None:
            return return_error(_("Camera is not connected , please do not execute abort exposure command"))

        return self.device.abort_exposure()

    async def exposure_thread(self) -> None:
        """
            Guard thread during the exposure and read the the status of the camera each second
            Args : None
            Returns : None
        """
        used_time = 0
        while used_time <= self.device.info._timeout:
            res = await self.get_exposure_status()
            
            if not res.get("params").get('status'):
                break
            await asyncio.sleep(0.5)
            used_time += 0.5
        await self.get_exposure_result()

    async def get_exposure_status(self,params = {} , ws = None) -> dict:
        """
            Async get status of the exposure process
            Args : None
            Returns : None
        """
        if self.device is None:
            return return_error(_("Camera is not connected , please do not execute get exposure status command"))

        if not self.device.info._is_exposure:
            return return_error(_("Exposure is not started, please do not execute get exposure status command"))

        res = self.device.get_exposure_status()

        await self.ws.write_message(await self.ws.generate_command(res))
        
        if res.get('status') != 0:
                self.blob.clear()
            
        if res.get('params').get('status') is True:
            self.blob.set()
        else:
            self.blob.clear()

        return res

    async def get_exposure_result(self , ws = None) -> dict:
        """
            Get the result of the exposure operation
            Args : None
            Returns : None
            NOTE : I'm not sure that whether this function should be called directly by client
        """
        if self.device is None:
            return return_error(_("Camera is not connected , please do not execute get exposure result command"))
        
        res = self.device.get_exposure_result()
        res["type"] = "data"
        await self.ws.write_message(dumps(res))
        return res

    async def cooling(self , params = {} , ws = None) -> dict:
        """
            Async start or stop cooling mode
            Args :
                params : dict
                    enable : bool
            Return : dict
        """
        if self.device is None:
            return return_error(_("Camera is not connected , please do not execute cooling command"))

        enable = params.get('enable')
        if enable is None or not isinstance(enable, bool):
            return return_error(_("Invalid enable value, please specify a correct value"))

        return self.device.cooling(params=params)

    async def cooling_to(self, params = {} , ws = None) -> dict:
        """
            Async make the camera cool to specified temperature
            Args :
                params : dict
                    temperature : float
            Return : dict
        """
        if self.device is None:
            return (_("Camera is not connected , please do not execute cooling to command"))

        temperature = params.get('temperature')
        if temperature is None or not isinstance(temperature,float):
            return return_error(_("Invalid temperature value provided"))

        res = self.device.cooling_to(params=params)
        if res.get('status') != 0:
            return res

        tornado.ioloop.IOLoop.instance().add_callback(self.cooling_thread)

        return return_success(_("Camera started to cooling to the target temperature started successfully"),{})

    async def cooling_thread(self):
        """
            Thread to monitor temperature while the cooling_to function is running
        """
        used_time = 0
        while used_time <= self.device.info._timeout:
            res = await self.get_cooling_status()
            
            if not res.get("params").get('status'):
                break
            await asyncio.sleep(0.5)
            used_time += 0.5

    async def get_current_temperature(self , params = {} , ws = None) -> dict:
        """
            Async get the current temperature of the camera\n
            Args : None
            Return : dict
                temperature : float
        """
        if self.device is None:
            return (_("Camera is not connected , please do not execute get current temperature command"))

        return self.device.get_current_temperature(params=params)

    async def get_cooling_power(self , params = {} , ws = None) -> dict:
        """
            Async get the cooling power of the camera\n
            Args : None
            Return : dict
                power : float
        """
        if self.device is None:
            return (_("Camera is not connected , please do not execute get current cool power command"))

        return self.device.get_cooling_power(params=params)

    async def get_cooling_status(self , params = {} , ws = None) -> dict:
        """
            Async get the cooling status of the camera\n
            Args : None
            Returns : dict
                status : bool
        """
        if self.device is None:
            return (_("Camera is not connected , please do not execute get cooling status command"))

        return self.device.get_cooling_status(params=params)
    
    async def get_camera_roi(self , params = {} , ws = None) -> dict:
        """
            Async get the roi of the camera frame\n
            Args : None
            Returns : dict
                height : int
                width : int
                start_x : int
                start_y : int
        """
        if self.device is None:
            return (_("Camera is not connected , please do not execute get camera roi command"))
        
        return self.device.get_camera_roi(params=params)
    
    async def set_camera_roi(self , params = {} , ws = None) -> dict:
        """
            Set the roi of the camera frame\n
            Args :
                params : dict
                    height : int
                    width : int
                    start_x : int
                    start_y : int
        """
        if self.device is None:
            return (_("Camera is not connected , please do not execute set camera roi command"))
        
        _height = params.get("height",self.device.info._height)
        _width = params.get("width",self.device.info._width)
        _start_x = params.get("start_x",self.device.info._start_x)
        _start_y = params.get("start_y",self.device.info._start_y)

        if not isinstance(_height,int) or not isinstance(_width,int) or not isinstance (_start_x,int) or not isinstance(_start_y,int):
            logger.error(_("Invalid height or width of the ROI was specified"))
        
        return self.device.set_camera_roi(params=params)
    
    async def get_gain(self , params = {} , ws = None) -> dict:
        """
            Get the gain of the camera\n
            Args : None
            Returns : dict
                gain : int
        """
        if self.device is None:
            return (_("Camera is not connected , please do not execute get camera gain command"))
        
        return self.device.get_gain(params=params)
    
    async def set_gain(self, params = {} , ws = None) -> dict:
        """
            Set the gain value of the current camera\n
            Args :
                params : dict
                    gain : int
            Returns : dict
        """
        if self.device is None:
            return (_("Camera is not connected , please do not execute set camera gain command"))
        
        return self.device.set_gain(params=params)
    
    async def get_offset(self , params = {} , ws = None) -> dict:
        """
            Get the current offset of the camera\n
            Args : None
            Returns : dict
                offset : int
        """
        if self.device is None:
            return (_("Camera is not connected , please do not execute get camera offset command"))
        
        return self.device.get_offset(params=params)
    
    async def set_offset(self, params = {} , ws = None) -> dict:
        """
            Set the offset of the camera\n
            Args :
                params : dict
                    offset : int
            Returns : dict
        """
        if self.device is None:
            return (_("Camera is not connected , please do not execute set camera offset command"))
        
        return self.device.set_offset(params=params)
    
    async def get_binning(self , params = {} , ws = None) -> dict:
        """
            Get the current binning of the camera\n
            Args : None
            Returns : dict
                binning : list
        """
        if self.device is None:
            return (_("Camera is not connected , please do not execute get camera binning mode command"))
        
        return self.device.get_binning(params=params)
    
    async def set_binning(self, params = {} , ws = None) -> dict:
        """
            Set the binning mode of the camera\n
            Args :
                params : dict
                    binning : list
            Returns : dict
        """
        if self.device is None:
            return (_("Camera is not connected , please do not execute set camera binning command"))
        
        _binning = params.get("binning")
        if not _binning or not isinstance(_binning, list):
            logger.error(_("Invalid binning mode specified"))

        return self.device.set_binning(params=params)

    async def call(self, params = {} , ws = None) -> dict:
        """
            This function is inspired by GaoLe , though he just call other functions directly.
            I wanted to cover these additional functions with a simple command.
            Args:
                params: dict
                    command : str # the name of the additional function
                    params : dict # the parameters for the function
            Returns : dict # Returns the function called
        """
        _command = params.get('command')
        if _command is None or not isinstance(_command,str):
            return return_error(_("Invalid command parameter provided"))

        try:
            command = getattr(self.camera,_command)
        except AttributeError as e:
            return return_error(_("Camera command not available"),{"error":e})

        try:
            res = await command(params.get('params',{}))
        except Exception as e:
            return return_error(_("Error executing command"),{"error":e})
        return res
