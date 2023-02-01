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

import PyIndi
from PyIndi import BaseDevice

from .indi_number_range_validation import check_number_range
from .device import IndiBaseDevice
from .client import IndiClient
from .basic_indi_state_str import *
from .indi_switch_operation import turn_on_multiple_switch_by_index, get_multiple_switch_info
from .indi_number_range_validation import indi_number_single_get_value


home_keyword = ["HOME", "HOME_INIT"]
go_home_name_list = ['GoToHome', 'IEQ_GOTO_HOME', 'RETURN_HOME']

class IndiTelescopeDevice(IndiBaseDevice):
    def __init__(self, indi_client: IndiClient, indi_device: BaseDevice = None):
        super().__init__(indi_client, indi_device)
        # telescope basic parameters here, if necessary
        
        self.longitude = None
        self.latitude = None
        self.elevation = None
        self.ha_limit = None  # todo, not available yet.
        self.telescope_aperture = None
        self.telescope_focal_length = None
        self.guider_aperture = None
        self.guider_focal_length = None
        
        # initial after connection
        self.can_park = False
        self.can_home = False
        self.home_word_type = None
        self.can_track_speed = False
        self.can_slew_speed = False
        self.can_guide_speed = False

        # target_information related
        self.target_name = None
        self.target_coord = None
    
    def check_telescope_params(self):
        # check park
        t_s = self.this_device.getSwitch('TELESCOPE_PARK')
        if (t_s):
            self.can_park = True
        else:
            self.can_park = False
        # check home
        self.can_home = False
        for (index, one_keyword) in enumerate(home_keyword):
            t_s = self.this_device.getSwitch(one_keyword)
            if (t_s):
                self.can_home = True
                self.home_word_type = index
        # check track
        t_s = self.this_device.getSwitch('TELESCOPE_TRACK_MODE')
        if (t_s):
            self.can_track_speed=True
        else:
            self.can_track_speed=False
        # check slew
        t_s = self.this_device.getSwitch('SlewRateS')
        if (t_s):
            self.can_slew_speed=True
        else:
            self.can_slew_speed=False
        # check guide speed
        t_s = self.this_device.getSwitch('GuideRateN')
        if (t_s):
            self.can_guide_speed=True
        else:
            self.can_guide_speed=False
    
    async def set_long_lat(self, long: float, lat: float, elev=0, *args, **kwargs):
        geo_coord = self.this_device.getNumber('GEOGRAPHIC_COORD')
        if check_number_range(geo_coord, 1, long):
            raise ValueError('longitude not in range!')
        if check_number_range(geo_coord, 0, lat):
            raise ValueError('latitude not in range!')
        if check_number_range(geo_coord, 2, elev):
            raise ValueError('evelation not in range!')
        self.longitude = long
        self.latitude = lat
        self.elevation = elev
        geo_coord[0].value = lat  # latitude
        geo_coord[1].value = long  # longitude
        geo_coord[2].value = float(elev)  # elevation
        self.indi_client.sendNewNumber(geo_coord)
        return None

    async def get_static_info(self, *args, **kwargs):
        pass
    
    async def get_set_params(self, *args, **kwargs):
        ret_struct = {}
        mount_type = self.this_device.getSwitch("MOUNT_TYPE")
        ret_struct['mount_type'] = get_multiple_switch_info(mount_type)
        on_coord_set = self.this_device.getSwitch("ON_COORD_SET")
        ret_struct['on_coord_set'] = get_multiple_switch_info(on_coord_set)
        track_mode = self.this_device.getSwitch("TELESCOPE_TRACK_MODE")
        ret_struct['track_mode'] = get_multiple_switch_info(track_mode)
        track_state = self.this_device.getSwitch("TELESCOPE_TRACK_STATE")
        ret_struct['track_state'] = get_multiple_switch_info(track_state)
        geo_coord = self.this_device.getNumber("GEOGRAPHIC_COORD")
        ret_struct['longitude'] = indi_number_single_get_value(geo_coord[1])
        ret_struct['latitude'] = indi_number_single_get_value(geo_coord[0])
        ret_struct['elevation'] = indi_number_single_get_value(geo_coord[2])
        return ret_struct

    async def get_real_time_info(self, *args, **kwargs):
        # return ra, dec, in_moving,
        equad_eod_coord = self.this_device.getNumber("EQUATORIAL_EOD_COORD")
        ra = equad_eod_coord[0].value
        dec = equad_eod_coord[1].value
        state_d = equad_eod_coord.getState()
        state = strIPState(state_d)
        if state_d == PyIndi.IPS_BUSY:
            is_moving = True
        else:
            is_moving = False
        return {
            'ra': ra,
            'dec': dec,
            'state': state,
            'is_moving': is_moving
        }

    async def set_telescope_info(self, telescope_aperture: float, telescope_focal_length: float,
                                 guider_aperture: float, guider_focal_length: float,  *args, **kwargs):
        self.telescope_aperture = telescope_aperture
        self.telescope_focal_length = telescope_focal_length
        self.guider_aperture = guider_aperture
        self.guider_focal_length = guider_focal_length
        telescope_info = self.this_device.getNumber('TELESCOPE_INFO')
        t_a = telescope_info.findWidgetByName('TELESCOPE_APERTURE')
        t_a.value = telescope_aperture
        t_f = telescope_info.findWidgetByName('TELESCOPE_FOCAL_LENGTH')
        t_f.value = telescope_focal_length
        g_a = telescope_info.findWidgetByName('GUIDER_APERTURE')
        g_a.value = guider_aperture
        g_f = telescope_info.findWidgetByName('GUIDER_FOCAL_LENGTH')
        g_f.value = guider_focal_length
        self.indi_client.sendNewNumber(telescope_info)
        return None

    async def set_time(self, *args, **kwargs):
        """
        note indi will sync time directly it connected to telescope device.
        so if the machine time is correct, then there is no need to change time.
        :return:
        """
        pass

    async def set_track(self, *args, **kwargs):
        on_coord_set = self.this_device.getSwitch("ON_COORD_SET")
        on_coord_set[0].s = PyIndi.ISS_ON  # TRACK
        on_coord_set[1].s = PyIndi.ISS_OFF  # SLEW
        on_coord_set[2].s = PyIndi.ISS_OFF  # SYNC
        self.indi_client.sendNewSwitch(on_coord_set)
        return None

    async def start_track(self, *args, **kwargs):
        track_state = self.this_device.getSwitch('TELESCOPE_TRACK_STATE')
        track_state[0].s = PyIndi.ISS_ON
        track_state[1].s = PyIndi.ISS_OFF
        self.indi_client.sendNewSwitch(track_state)
        return None

    async def set_track_mode(self, track_mode: str, *args, **kwargs):
        """
        todo need further test. tracking rate doesn't change as track mode change
        :param track_mode: sidereal, solar, lunar
        :return:
        """
        eq_track_mode = self.this_device.getSwitch("TELESCOPE_TRACK_MODE")
        if track_mode == 'sidereal':
            eq_track_mode = turn_on_multiple_switch_by_index(eq_track_mode, 0)
        elif track_mode == 'solar':
            eq_track_mode = turn_on_multiple_switch_by_index(eq_track_mode, 1)
        elif track_mode == 'lunar':
            eq_track_mode = turn_on_multiple_switch_by_index(eq_track_mode, 2)
        else:
            raise TypeError('wrong tracking name!')
        self.indi_client.sendNewSwitch(eq_track_mode)
        return None

    async def stop_track(self, *args, **kwargs):
        track_state = self.this_device.getSwitch('TELESCOPE_TRACK_STATE')
        track_state[0].s = PyIndi.ISS_OFF
        track_state[1].s = PyIndi.ISS_ON
        self.indi_client.sendNewSwitch(track_state)
        return None

    async def goto(self, ra: float, dec: float, target_name=None, *args, **kwargs):
        if self.__is_parked():
            return 'telescope is parked, please unpark first!'
        equad_eod_coord = self.this_device.getNumber("EQUATORIAL_EOD_COORD")
        if not check_number_range(equad_eod_coord, 0, ra):
            return 'RA is not in range!'
        if not check_number_range(equad_eod_coord, 1, dec):
            return 'DEC is not in range!'
        if equad_eod_coord.getState() == PyIndi.IPS_BUSY:
            return 'telescope is moving, please wait!'
        equad_eod_coord[0].value = ra
        equad_eod_coord[1].value = dec
        self.indi_client.sendNewNumber(equad_eod_coord)
        if target_name is not None:
            self.target_name = target_name
            self.target_coord = {
                'ra': ra,
                'dec': dec
            }
        else:
            self.target_name = None
            self.target_coord = None
        return None

    async def goto_ha_dec(self, ha: float, dec: float,  target_name=None):
        pass

    async def got_az_al(self, az: float, al: float,  target_name=None):
        pass

    async def get_fits_file_format_data(self, *args, **kwargs):
        if self.target_name is not None:
            return {
                'name': self.target_name,
                'coord': self.target_coord
            }
        else:
            return None

    async def go_home(self, *args, **kwargs):
        """
        found, if the telescope support home instruction, it will have return_home, at_home property.
        :return:
        """
        if self.can_home:
            # stop track
            await self.stop_track()
            home_switch = self.this_device.getSwitch(home_keyword[self.home_word_type])
            found_switch = False
            for (index, one_switch) in enumerate(home_switch):
                for one_test_gohome_name in go_home_name_list:
                    if one_test_gohome_name == one_switch.name:
                        home_switch = turn_on_multiple_switch_by_index(home_switch, index)
                        found_switch = True
                        break
                if found_switch:
                    break
            self.indi_client.sendNewSwitch(home_switch)
            return None
        else:
            return 'This telescope do not support go home!'

    async def at_home(self, *args, **kwargs):
        pass

    def __is_parked(self, *args, **kwargs):
        park = self.this_device.getSwitch('TELESCOPE_PARK')
        if park[0] == PyIndi.ISS_ON:
            return True
        else:
            return False

    async def park(self, *args, **kwargs):
        if self.can_park:
            park = self.this_device.getSwitch('TELESCOPE_PARK')
            park[0] = PyIndi.ISS_ON
            park[1] = PyIndi.ISS_OFF
            self.indi_client.sendNewSwitch(park)
            return None
        else:
            return 'Telescope cannot park'

    async def unpark(self, *args, **kwargs):
        if self.can_park:
            park = self.this_device.getSwitch('TELESCOPE_PARK')
            park[0] = PyIndi.ISS_OFF
            park[1] = PyIndi.ISS_ON
            self.indi_client.sendNewSwitch(park)
            return None
        else:
            return 'Telescope cannot park'            

    async def set_park(self, ha, dec, *args, **kwargs):
        pass

    async def abort(self, *args, **kwargs):
        abort = self.this_device.getSwitch('TELESCOPE_ABORT_MOTION')
        abort[0] = PyIndi.ISS_ON
        self.indi_client.sendNewSwitch(abort)
        return None
