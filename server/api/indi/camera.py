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
import time
import datetime
import asyncio
from pathlib import Path
import tornado.ioloop

import PyIndi
from PyIndi import BaseDevice

from .device import IndiBaseDevice
from .client import IndiClient
from .indi_switch_operation import turn_on_second_swtich, turn_on_first_swtich, \
    turn_on_multiple_switch_by_index,\
    get_multiple_switch_info
from .indi_property_2_json import indi_property_2_json
from .indi_number_range_validation import check_number_range, indi_number_single_get_value

from .misc import blob_event2, blob_event1

from utils.i18n import _
from ...logging import logger

GAIN_Keywords = ["CCD_GAIN", "CCD_CONTROLS"]

class INDICameraAPI(IndiBaseDevice):
    """
        INDI Camera API Interface
    """

    def __init__(self, indi_client: IndiClient, indi_device: BaseDevice = None) -> None:
        """
            Initialize IndiCamera object
            Args:
                indi_client: IndiClient
                indi_device: IndiDevice
            Return : None
        """
        super().__init__(indi_client, indi_device)
        # telescope basic parameters here, if necessary
        self.can_cool = False
        self.can_binning = False
        self.can_gain = False
        self.can_offset = False
        self.can_abort = False
        self.can_subframe = False
        self.can_rotation = False

        self.has_shutter = False
        self.has_fan = False
        self.has_heater = False
        self.has_hcg = False
        self.has_low_noise = False
        self.gain_type = 0

        self._is_connected = False

        self.fits_save_path = Path.home() / 'Pictures'
        self.subframe_counting = 0
        self.save_file_name_pattern = '{date}/{target_name}_{filter}_{exposure}_{date_time}_{HFR}_{guiding_RMS}_{count}.fits'

        self.indi_client.setBLOBMode(
            PyIndi.B_ALSO, self.this_device.getDeviceName(), "CCD1")
        # important flag
        self.in_exposure = False  # flag for camera is working

    def __del__(self) -> None:
        """
            Destructor method
            Args : None
            Returns : None
        """
        if self._is_connected:
            self.disconnect()

    def __str__(self) -> str:
        """
            Just a string representation
            Args : None
            Returns : str
        """
        return "INDI Camera API Interface written by GaoLe"

    def get_configuration(self) -> None:
        """
            Get the configuration of the camera after connection established
            Args : None
            Returns : None
        """
        # check gain
        res = self.this_device.getNumber("CCD_GAIN")
        if (res):
            self.can_gain = True
        else:
            self.can_gain = False
        # check offset
        res = self.this_device.getNumber("CCD_OFFSET")
        if (res):
            self.can_offset = True
        else:
            self.can_offset = False
        # check binning
        res = self.this_device.getNumber("CCD_BINNING")
        if (res):
            self.can_binning = True
        else:
            self.can_binning = False
        # check cool
        time.sleep(1)
        res = self.this_device.getSwitch('CCD_COOLER')
        if (res):
            self.can_cool = True
        else:
            self.can_cool = False
        # check abort
        res = self.this_device.getSwitch('CCD_ABORT')
        if (res):
            self.can_abort = True
        else:
            self.can_abort = False
        # check subframe
        res = self.this_device.getSwitch('CCD_SUBFRAME')
        if (res):
            self.can_subframe = True
        else:
            self.can_subframe = False
        # check rotation
        res = self.this_device.getNumber('CCD_ROTATION')
        if (res):
            self.can_rotation = True
        else:
            self.can_rotation = False

        # #################################################################
        # Following parameters are for toupcam
        # #################################################################

        # check fan
        res = self.this_device.getSwitch('TC_FAN_CONTROL')
        if (res):
            self.has_fan = True
        else:
            self.has_fan = False

        # check heat
        res = self.this_device.getSwitch('TC_HEAT_CONTROL')
        if (res):
            self.has_heater = True
        else:
            self.has_heater = False
        # check gain keyword type
        for (index, one_keyword) in enumerate(GAIN_Keywords):
            res = self.this_device.getNumber(one_keyword)
            if (res):
                self.gain_type = index
        
        # check hcg
        res = self.this_device.getSwitch("TC_HCG_CONTROL")
        if (res):
            self.has_hcg = True
        else:
            self.has_hcg = False
        res = self.this_device.getSwitch("TC_LOW_NOISE_CONTROL")
        if (res):
            self.has_low_noise = True
        else:
            self.has_low_noise = False

    async def start_exposure(self, exposure: float, *args, **kwargs) -> None:
        """
            Start a single exposure
            :param exposure: must have
            :param args:  args[0] is subframe count, if no subframe count is given, system will use self_increase count
            :param kwargs:
            :return:
        """
        if self.in_exposure:
            return 'Exposure is in progress. Cannot start exposure now!'

        ccd_exposure = self.this_device.getNumber("CCD_EXPOSURE")
        ccd_exposure[0].value = exposure
        blob_event1.clear()
        self.indi_client.sendNewNumber(ccd_exposure)
        self.in_exposure = True
        logger.info(f'device camera, start exposure {exposure} seconds')
        ccd_ccd1 = self.this_device.getBLOB('CCD1')

        if len(args) >= 1:
            kwargs['count'] = args[0]
        kwargs['exposure'] = exposure
        kwargs['ccd1'] = ccd_ccd1
        tornado.ioloop.IOLoop.instance().add_callback(
            self.after_exposure_finish, *args, **kwargs)

    async def after_exposure_finish(self, *args, **kwargs):
        try:
            await asyncio.wait_for(blob_event1.wait(), timeout=kwargs['exposure']+2)
            self.in_exposure = False
            logger.info(
                f'device camera, ended exposure {kwargs["exposure"]} seconds')
            for blob in kwargs['ccd1']:
                fits = blob.getblobdata()
                kwargs['HFR'] = 0  # to detect HFR value
                to_save_file_path = self.__translate_parameters_formatting(
                    **kwargs)
                with open(str(to_save_file_path), 'wb') as f:
                    f.write(fits)
            kwargs['ws_instance'].write_message(json.dumps({
                'type': 'signal',
                'message': 'Exposure Finished!',
                'data': None,
            }))
        except TimeoutError:
            blob_event1.clear()
            self.in_exposure = False
            kwargs['ws_instance'].write_message(json.dumps({
                'type': 'signal',
                'message': 'ERROR! Exposure Time Out Error!',
                'data': None,
            }))

    async def abort_exposure(self, **kwargs):
        """
            Async abort the exposure operation
            Args : None
            Returns : None
        """
        if not self.in_exposure:
            return 'No exposure in progress!'
        else:
            abort_exposure = self.this_device.getSwitch('CCD_ABORT_EXPOSURE')
            abort_exposure = turn_on_multiple_switch_by_index(
                abort_exposure, 0)
            self.indi_client.sendNewSwitch(abort_exposure)
            self.in_exposure = False
            return 'Exposure aborted!'

    async def cooling_to(self, target_temperature: float, **kwargs):
        """
            Let the camera cool to the target temperature
            Args :
                target_temperature : float
            Returns : None
        """
        temperature = self.this_device.getNumber("CCD_TEMPERATURE")
        if check_number_range(temperature, 0, target_temperature):
            temperature[0].value = target_temperature
            self.indi_client.sendNewNumber(temperature)
            return None
        else:
            raise ValueError("Temperature is out of range!")

    async def gerestatic_info(self, **kwargs):
        # pixel size,
        ccd_info = self.this_device.getNumber("CCD_INFO")
        return indi_property_2_json(ccd_info)

    async def gereset_params(self, **kwargs):
        # gain offset, binning
        ret_json = {}
        gain = self.this_device.getNumber(GAIN_Keywords[self.gain_type])
        ret_json['gain'] = indi_number_single_get_value(gain[0])
        offset = self.this_device.getNumber("CCD_OFFSET")
        ret_json['offset'] = indi_number_single_get_value(offset[0])
        if self.can_binning:
            binning = self.this_device.getNumber("CCD_BINNING")
            ret_json['binning'] = indi_number_single_get_value(binning[0])
        else:
            ret_json['binning'] = None
        if self.can_cool:
            ccd_cooler = self.this_device.getSwitch('CCD_COOLER')
            if ccd_cooler[0].s == PyIndi.ISS_ON:
                ret_json['cooler'] = True
            else:
                ret_json['cooler'] = False
        else:
            ret_json['cooler'] = None
        if self.has_fan:
            ccd_cooler = self.this_device.getSwitch('TC_FAN_CONTROL')
            if ccd_cooler[0].s == PyIndi.ISS_ON:
                ret_json['fan'] = True
            else:
                ret_json['fan'] = False
        else:
            ret_json['fan'] = None
        if self.has_heater:
            ccd_cooler = self.this_device.getSwitch('TC_HEAT_CONTROL')
            if ccd_cooler[0].s == PyIndi.ISS_ON:
                ret_json['heater'] = True
            else:
                ret_json['heater'] = False
        else:
            ret_json['heater'] = None
        if self.has_hcg:
            hcg = self.this_device.getSwitch("TC_HCG_CONTROL")
            ret_json['hcg'] = get_multiple_switch_info(hcg)
        else:
            ret_json['hcg'] = None
        if self.has_low_noise:
            low_n = self.this_device.getSwitch("TC_LOW_NOISE_CONTROL")
            if low_n[0].s == PyIndi.ISS_ON:
                ret_json['low_noise_mode'] = True
            else:
                ret_json['low_noise_mode'] = False
        else:
            ret_json['low_noise_mode'] = None
        return ret_json

    async def get_real_time_info(self, **kwargs):
        temperature = self.this_device.getNumber("CCD_TEMPERATURE")
        return {
            "temperature": temperature[0].value,
            "in_exposure": self.in_exposure,
        }

    async def start_cool_camera(self, **kwargs):
        """
           > CCD_COOLER type switch
               COOLER_ON(ON)= On
               COOLER_OFF(OFF)= Off
        :return:
        """
        if self.can_cool:
            ccd_cooler = self.this_device.getSwitch('CCD_COOLER')
            ccd_cooler = turn_on_first_swtich(ccd_cooler)
            self.indi_client.sendNewSwitch(ccd_cooler)
            return None
        else:
            return 'No Cooler Available!'

    async def stop_cool_camera(self, **kwargs):
        if self.can_cool:
            ccd_cooler = self.this_device.getSwitch('CCD_COOLER')
            ccd_cooler = turn_on_second_swtich(ccd_cooler)
            self.indi_client.sendNewSwitch(ccd_cooler)
            return None
        else:
            return 'No Cooler Available!'

    async def start_fan(self, **kwargs):
        """
           > TC_FAN_CONTROL type switch
               TC_FAN_ON(On)= On
               TC_FAN_OFF(Off)= Off
        :return:
        """
        if self.has_fan:
            ccd_cooler = self.this_device.getSwitch('TC_FAN_CONTROL')
            ccd_cooler = turn_on_first_swtich(ccd_cooler)
            self.indi_client.sendNewSwitch(ccd_cooler)
        else:
            return 'No Fan Available'

    async def stop_fan(self, **kwargs):
        if self.has_fan:
            ccd_cooler = self.this_device.getSwitch('TC_FAN_CONTROL')
            ccd_cooler = turn_on_second_swtich(ccd_cooler)
            self.indi_client.sendNewSwitch(ccd_cooler)
        else:
            return 'No Fan Available'

    async def start_tc_heat(self, **kwargs):
        """
           > TC_HEAT_CONTROL type switch
               TC_HEAT_OFF(Off)= On
               TC_HEAT_ON(On)= Off
        :return:
        """
        if self.has_heater:
            ccd_cooler = self.this_device.getSwitch('TC_HEAT_CONTROL')
            ccd_cooler = turn_on_first_swtich(ccd_cooler)
            self.indi_client.sendNewSwitch(ccd_cooler)
        else:
            return 'No Heater Available'

    async def stop_tc_heat(self, **kwargs):
        if self.has_heater:
            ccd_cooler = self.this_device.getSwitch('TC_HEAT_CONTROL')
            ccd_cooler = turn_on_second_swtich(ccd_cooler)
            self.indi_client.sendNewSwitch(ccd_cooler)
        else:
            return 'No Heater Available'

    """
    kwargs define for file name formatting.
    target_info: obj, the name of target. countain name, coord
    filter_info: object, the filter basic information given by the indi_filter_wheel
    phd2_object: TBD, how to get the realtime guiding rmse.   
    
    keywords for generating format
    target_name:        str, target name
    count:              int, default by 0, sequence subframe number.
    other automatically generated parameters
    exposure    given directly by parameter
    HFR         calculated by ??? TBD
    guiding_rms phd2 guiding accuracy
    date        the date when this fits file is generated.
    date_time   the date time when this fits file is generated. format %Y-%m-%d-%H-%M
    
    note: if the file name is already exists, extra _1 will be added.
    
    '{date}/{target_name}_{filter}_{exposure}_{date_time}_{HFR}_{guiding_RMS}_{count}.fits'
    """

    def __translate_parameters_formatting(self, **kwargs):
        if 'target_info' in kwargs.keys():
            target_name = kwargs['target_info']['name']
        else:
            target_name = ''
        if 'count' in kwargs.keys():
            count = kwargs['count']
        else:
            count = self.subframe_counting
            self.subframe_counting += 1
        if 'filter_info' in kwargs.keys():
            filter = None
        else:
            filter = 'none'
        if 'phd2_object' in kwargs.keys():
            guiding_RMS = None
        else:
            guiding_RMS = ''
        now = datetime.datetime.now()
        now_str = now.strftime('%Y-%m-%d-%H-%M-%S')
        date_str = now.strftime('%Y-%m-%d')
        file_name = self.save_file_name_pattern.format(
            target_name=target_name, count=count, filter=filter, guiding_RMS=guiding_RMS, HFR=kwargs[
                'HFR'],
            date=date_str, date_time=now_str, exposure=kwargs['exposure']
        )
        file_path = self.fits_save_path / file_name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if file_path.exists():
            new_file_path = file_path.parent / \
                file_name.replace('.fits', '_1.fits')
            file_path = new_file_path
        return file_path

    async def set_number_parameters(self, param_name: str, param_value, *args, **kwargs):
        """
            Set the number of the specified parameter
            Args :
                param_name : str # the name of the parameter
                param_value : str # the value of the parameter
            Returns : None
        """
        if param_name == 'gain':
            gain = self.this_device.getNumber(GAIN_Keywords[self.gain_type])
            if self.gain_type == 0:
                if check_number_range(gain, 0, param_value):
                    gain[0].value = param_value
                else:
                    raise ValueError("gain value is out of range!")
            elif self.gain_type == 1:
                if check_number_range(gain, 0, param_value):
                    gain[0].value = param_value
                else:
                    raise ValueError("gain value is out of range!")
            self.indi_client.sendNewNumber(gain)
        elif param_name == 'offset':
            offset = self.this_device.getNumber("CCD_OFFSET")
            if check_number_range(offset, 0, param_value):
                offset[0].value = param_value
            else:
                raise ValueError("offset value is out of range!")
            self.indi_client.sendNewNumber(offset)
        elif param_name == 'binning':
            if self.can_binning:
                binning = self.this_device.getNumber("CCD_BINNING")
                if check_number_range(binning, 0, param_value):
                    binning[0].value = param_value
                    binning[1].value = param_value
                else:
                    raise ValueError("binning value is out of range!")
                self.indi_client.sendNewNumber(binning)
        elif param_name == "hcg":
            if self.has_hcg:
                hcg = self.this_device.getSwitch("TC_HCG_CONTROL")
                found = False
                for (index, one_switch) in enumerate(hcg):
                    if param_value == one_switch.name:
                        turn_on_multiple_switch_by_index(hcg, index)
                        found = True
                        break
                if not found:
                    raise ValueError("hcg setting name is incorrect!")
                else:
                    self.indi_client.sendNewSwitch(hcg)
        elif param_name == "low_noise_mode":
            if self.has_low_noise:
                low_n = self.this_device.getSwitch("TC_LOW_NOISE_CONTROL")
                if param_value == 1:
                    turn_on_first_swtich(low_n)
                else:
                    turn_on_second_swtich(low_n)
                self.indi_client.sendNewSwitch(low_n)
        else:
            pass
        return None

    async def get_parameter(self, **kwargs):
        pass
