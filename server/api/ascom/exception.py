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

from enum import Enum

from utils.i18n import _

class AscomCameraError(Enum):
    """
        Regular ASCOM camera error
    """
    OneDevice = _("Each server can only connect to one device at a time")
    NotConnected = _("Camera is not connected")
    NetworkError = _("Network error occurred")
    DriverError = _("Driver error occurred")
    InvalidOperation = _("Invalid operation")
    NotSupported = _("Not supported function")

    NoHostValue = _("No host value provided")
    NoPortValue = _("No port value provided")
    NoDeviceNumber = _("No device number provided")
    NoExposureValue = _("No exposure value provided")
    NoGainValue = _("No gain value provided")
    NoOffsetValue = _("No offset value provided")
    NoISOValue = _("No ISO value provided")

    InvalidExposureValue = _("Invalid exposure value provided")
    InvalidGainValue = _("Invaild gain value provided , default is 20")
    InvalidOffsetValue = _("Invalid offsets value provided , default is 20")
    InvalidBinningValue = _("Invalid binding mode value provided , default is 1")
    InvalidCoolingValue = _("Invalid cooling status value provided")
    InvalidTemperatureValue = _("Invalid temperature value provided")
    InvalidROIValue = _("Invalid ROI value provided")

    CanNotCooling = _("Camera is not supported to cool")
    CanNotGetTemperature = _("Could not get camera current temperature")
    CanNotGetCoolingPower = _("Could not get camera current power")
    CanNotGetPower = _("Could not get camera current cooling power")
    CanNotGetGain = _("Could not get the gain value of the current camera")
    CanNotGetOffset = _("Could not get the offset value of the current camera")
    CanNotSetGain = _("Could not set the gain value of the current camera")
    CanNotSetOffset = _("Could not set the offset value of the current camera")
    CanNotGetBinning = _("Could not get binning mode of the current camera")
    CanNotSetBinning = _("Could not set binning mode of the current camera")

    StartExposureError = _("Start exposure failed")
    AbortExposureError = _("Abort exposure failed")

    CameraNotCooling = _("Camera is not started cooling mode")

class AscomCameraSuccess(Enum):
    """
        Regular ASCOM camera success
    """

    ScanningSuccess = _("Scanning camera successfully")
    ReconnectSuccess = _("Reconnect camera successfully")
    PollingSuccess = _("Camera's information is refreshed successfully")
    GetConfigrationSuccess = _("Get camera configuration successfully")
    SaveConfigrationSuccess = _("Save camera configuration successfully")

    StartExposureSuccess = _("Start exposure successfully")
    AbortExposureSuccess = _("Abort exposure successfully")
    CoolingToSuccess = _("Camera started cooling to specified temperature successfully")
    GetCoolingPowerSuccess = _("Get camera current cooling power successfully")
    GetCoolingStatusSuccess = _("Get camera current cooling status successfully")
    GetCoolingTemperatureSuccess = _("Get camera current Cooling temperature successfully")
    GetROISuccess = _("Get camera ROI successfully")
    SetROISuccess = _("Set camera ROI successfully")
    GetGainSuccess = _("Get camera gain value successfully")
    SetGainSuccess = _("Set camera gain value successfully")
    GetOffsetSuccess = _("Get camera offset value successfully")
    SetOffsetSuccess = _("Set camera offset value successfully")
    GetBinningSuccess = _("Get camera binning mode successfully")
    SetBinningSuccess = _("Set camera binning mode successfully")

class AscomCameraWarning(Enum):
    """
        Regular ASCOM camera warning
    """
    DisconnectBeforeScanning = _("Please disconnect your camera before scanning")