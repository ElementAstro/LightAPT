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

from .indi_switch_operation import turn_on_first_swtich, turn_on_second_swtich
from .device import IndiBaseDevice
from .client import IndiClient
from .basic_indi_state_str import strIPState
from .indi_number_range_validation import indi_number_single_get_value


class INDIFocuserAPI(IndiBaseDevice):
    def __init__(self, indi_client: IndiClient, indi_device: BaseDevice = None):
        """
            Initialize a new INDIFocuser object
            Args:
                indi_client: IndiClient # a initialized IndiClient
                indi_device: IndiDevice
            Returns : None
        """
        super().__init__(indi_client, indi_device)
        self.small_step = 100
        self.large_step = 1000

        # flags
        self.has_speed = False
        self.has_temperature = False

    """
        useful keyword
        FOCUS_MOTION, move in or out
        FOCUS_SPEED, may useless
        REL_FOCUS_POSITION, move relative
        ABS_FOCUS_POSITION, move to position
        FOCUS_MAX, max focus number
        FOCUS_BACKLASH_TOGGLE, backslash setting
        FOCUS_BACKLASH_STEPS, backslash value
    """
    def get_configuration(self) -> None:
        """
            Get all the configuration values of the current focuser
            Args : None
            Returns : None
        """
        # has focus speed?
        t_s = self.this_device.getNumber('FOCUS_SPEED')
        if (t_s):
            self.has_speed = True
        else:
            self.has_speed = False
        # has temperature?
        t_s = self.this_device.getNumber('FOCUS_TEMPERATURE')
        if (t_s):
            self.has_temperature = True
        else:
            self.has_temperature = False

    async def get_params(self, *args, **kwargs):
        """
        move_speed
        absolute position
        ABS_FOCUS_POSITION.state
        in moving
        max_step
        backslash_flag
        backslash
        temperature: if any
        :return:
        """
        ret_struct = {}
        if self.has_speed:
            move_speed = self.this_device.getNumber("FOCUS_SPEED")
            ret_struct['move_speed'] = indi_number_single_get_value(move_speed[0])
        else:
            ret_struct['move_speed'] = None
        if self.has_temperature:
            temp = self.this_device.getNumber("FOCUS_TEMPERATURE")
            ret_struct['temperature'] = indi_number_single_get_value(temp[0])
        else:
            ret_struct['temperature'] = None
        abs_pos = self.this_device.getNumber("ABS_FOCUS_POSITION")
        ret_struct['focus_position'] = abs_pos[0].value
        ret_struct['foucser_state'] = strIPState(abs_pos.getState())
        max_step = self.this_device.getNumber("FOCUS_MAX")
        ret_struct['focus_max'] = max_step[0].value
        backslash_flag = self.this_device.getSwitch("FOCUS_BACKLASH_TOGGLE")
        if backslash_flag[0].s == PyIndi.ISS_ON:
            ret_struct['backslash_switch'] = True
        else:
            ret_struct['backslash_switch'] = False
        backslash = self.this_device.getNumber("FOCUS_BACKLASH_STEPS")
        ret_struct['backslash'] = indi_number_single_get_value(backslash[0])
        return ret_struct

    def __check_in_moving(self):
        abs_position = self.this_device.getNumber("ABS_FOCUS_POSITION")
        if abs_position.getState() == PyIndi.IPS_BUSY:
            return True
        elif abs_position.getState() == PyIndi.IPS_ALERT:
            raise AttributeError('focuser absolute position alert!')
        else:
            return False

    async def set_max_step(self, max_step: int, *args, **kwargs):
        if max_step <= 0:
            raise ValueError("max step must be larger than 0!")
        max_data = self.this_device.getNumber("FOCUS_MAX")
        max_data[0].value = int(max_step)
        self.indi_client.sendNewNumber(max_data)
        return None

    async def set_move_small_step(self, step_value: int, *args, **kwargs):
        if step_value <= 0:
            raise ValueError("step value must be larger than 0!")
        self.small_step = step_value
        return None

    async def set_move_large_step(self, step_value: int, *args, **kwargs):
        if step_value <= 0:
            raise ValueError("step value must be larger than 0!")
        self.large_step = step_value
        return None

    async def move_to_position(self, step_value: int, *args, **kwargs):
        if self.__check_in_moving():
            return "Focuser is in moving! Cannot move!"
        if step_value <= 0:
            raise ValueError("step value must be larger than 0!")
        max_data = self.this_device.getNumber("FOCUS_MAX")
        max_steps = max_data[0].value
        if step_value > max_steps:
            raise ValueError("step value cannot be larger than max step!")
        abs_position = self.this_device.getNumber("ABS_FOCUS_POSITION")
        abs_position[0].value = int(step_value)
        self.indi_client.sendNewNumber(abs_position)
        return None

    async def move_in_small(self, *args, **kwargs):
        if self.__check_in_moving():
            return "Focuser is in moving! Cannot move!"
        move_direction = self.this_device.getSwitch("FOCUS_MOTION")
        rel_move = self.this_device.getNumber("REL_FOCUS_POSITION")
        move_direction = turn_on_first_swtich(move_direction)
        self.indi_client.sendNewSwitch(move_direction)
        rel_move[0].value = self.small_step
        self.indi_client.sendNewNumber(rel_move)
        return None

    async def move_out_small(self, *args, **kwargs):
        if self.__check_in_moving():
            return "Focuser is in moving! Cannot move!"
        move_direction = self.this_device.getSwitch("FOCUS_MOTION")
        rel_move = self.this_device.getNumber("REL_FOCUS_POSITION")
        move_direction = turn_on_second_swtich(move_direction)
        self.indi_client.sendNewSwitch(move_direction)
        rel_move[0].value = self.small_step
        self.indi_client.sendNewNumber(rel_move)
        return None

    async def move_in_large(self, *args, **kwargs):
        if self.__check_in_moving():
            return "Focuser is in moving! Cannot move!"
        move_direction = self.this_device.getSwitch("FOCUS_MOTION")
        rel_move = self.this_device.getNumber("REL_FOCUS_POSITION")
        move_direction = turn_on_first_swtich(move_direction)
        self.indi_client.sendNewSwitch(move_direction)
        rel_move[0].value = self.large_step
        self.indi_client.sendNewNumber(rel_move)
        return None

    async def move_out_large(self, *args, **kwargs):
        if self.__check_in_moving():
            return "Focuser is in moving! Cannot move!"
        move_direction = self.this_device.getSwitch("FOCUS_MOTION")
        rel_move = self.this_device.getNumber("REL_FOCUS_POSITION")
        move_direction = turn_on_second_swtich(move_direction)
        self.indi_client.sendNewSwitch(move_direction)
        rel_move[0].value = self.large_step
        self.indi_client.sendNewNumber(rel_move)
        return None

    async def turn_on_backslash(self, *args, **kwargs):
        if self.__check_in_moving():
            return "Focuser is in moving! Cannot change setting!"
        back_slash = self.this_device.getSwitch("FOCUS_BACKLASH_TOGGLE")
        back_slash = turn_on_first_swtich(back_slash)
        self.indi_client.sendNewSwitch(back_slash)
        return None

    async def turn_off_backslash(self):
        if self.__check_in_moving():
            return "Focuser is in moving! Cannot change setting!"
        back_slash = self.this_device.getSwitch("FOCUS_BACKLASH_TOGGLE")
        back_slash = turn_on_second_swtich(back_slash)
        self.indi_client.sendNewSwitch(back_slash)
        return None

    async def set_backslash(self, step, *args, **kwargs):
        if self.__check_in_moving():
            return "Focuser is in moving! Cannot change setting!"
        if step <= 0:
            raise ValueError("Backslash value cannot smaller than 0")
        backslash_step = self.this_device.getNumber("FOCUS_BACKLASH_STEPS")
        backslash_step[0].value = step
        self.indi_client.sendNewNumber(backslash_step)
        return None
