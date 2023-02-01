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

from .device import IndiBaseDevice
from .client import IndiClient

class SingleFilter:
    def __init__(self, slot_number, filter_name):
        self.slot_number = slot_number
        self.filter_name = filter_name
        self.focus_offset = 0
        self.af_exposure_time = 1

    def set_autofocus_data(self, focus_offset=0, af_exposure_time=1):
        self.focus_offset = focus_offset
        self.af_exposure_time = af_exposure_time


# important note, all slot in index are values larger than 1.
# therefore, indexing will add or minus one.


class IndiFilterWheelDevice(IndiBaseDevice):
    def __init__(self, indi_client: IndiClient, indi_device: BaseDevice = None):
        super().__init__(indi_client, indi_device)
        self.filter_numbers = 0
        self.filter_info = []

    def initial_empty_filter(self):
        for one_count in range(self.filter_numbers):
            self.filter_info.append(SingleFilter(one_count, f"filter_{one_count}"))
    """
    useful keyword
    FILTER_SLOT
    FILTER_NAME
    """
    def check_filter_param(self):
        filter_name = self.this_device.getText("FILTER_NAME")
        filter_number = len(filter_name)
        self.filter_numbers = filter_number
        self.filter_info = []
        self.initial_empty_filter()

    async def get_filter_slot(self, *args, **kwargs):
        filter_slot = self.this_device.getNumber("FILTER_SLOT")
        if self.__check_in_rotating():
            flag = False
        else:
            flag = True
        return {
            'filter_slot': int(filter_slot[0].value),
            'idle': flag
        }

    async def get_all_params(self, *args, **kwargs):
        filter_slot = self.this_device.getNumber("FILTER_SLOT")
        filter_name = self.this_device.getText("FILTER_NAME")
        filters_info = []
        for (index, one_filter_info) in enumerate(self.filter_info):
            filters_info.append({
                'slot': index,
                'filter_name': filter_name[index].text,
                'focus_offset': one_filter_info.focus_offset,
                'af_exposure_time': one_filter_info.af_exposure_time,
            })
        return {
            'filter_slot': int(filter_slot[0].value),
            'filters_info': filters_info,
        }

    async def update_all_slot_data(self, slot_info_struct: list, *args, **kwargs):
        """

        :param slot_number: not used, as the filter number is determined by hardware not software.
        :param slot_info_struct:
        :return:
        """
        filter_name = self.this_device.getText("FILTER_NAME")
        for (filter_index, one_filter_info) in enumerate(slot_info_struct):
            if "filter_name" in one_filter_info.keys():
                self.filter_info[filter_index].filter_name = one_filter_info['filter_name']
                filter_name[filter_index].text = one_filter_info['filter_name']
            if "focus_offset" in one_filter_info.keys():
                focus_offset = one_filter_info["focus_offset"]
            else:
                focus_offset = 0
            if "af_exposure_time" in one_filter_info.keys():
                af_exposure_time = one_filter_info["af_exposure_time"]
            else:
                af_exposure_time = 1
            self.filter_info[filter_index].set_autofocus_data(focus_offset, af_exposure_time)
        self.indi_client.sendNewText(filter_name)

    async def set_one_filter_solt_value(self, slot_index: int, slot_info: dict, *args, **kwargs):
        """

        :param slot_index:
        :param slot_info: dict:
         filter_name, focus_offset, af_exposure_time
        :return:
        """
        real_slot_index = slot_index - 1
        filter_name = self.this_device.getText("FILTER_NAME")
        if "filter_name" in slot_info.keys():
            self.filter_info[real_slot_index].filter_name = slot_info['filter_name']
            filter_name[real_slot_index].text = slot_info['filter_name']
        if "focus_offset" in slot_info.keys():
            focus_offset = slot_info["focus_offset"]
        else:
            focus_offset = 0
        if "af_exposure_time" in slot_info.keys():
            af_exposure_time = slot_info["af_exposure_time"]
        else:
            af_exposure_time = 1
        self.filter_info[real_slot_index].set_autofocus_data(focus_offset, af_exposure_time)
        self.indi_client.sendNewText(filter_name)

    def __check_in_rotating(self):
        filter_slot = self.this_device.getNumber("FILTER_SLOT")
        if filter_slot.getState() == PyIndi.IPS_BUSY:
            return True
        elif filter_slot.getState() == PyIndi.IPS_ALERT:
            raise AttributeError('filter filter slot alert!')
        else:
            return False

    async def switch_filter(self, slot_index, *args, **kwargs):
        if self.__check_in_rotating():
            return 'Filter wheel in rotating!'
        if slot_index < 1 or slot_index > self.filter_numbers:
            raise ValueError("filter slot index value out of range!")
        filter_slot = self.this_device.getNumber("FILTER_SLOT")
        filter_slot[0].value = slot_index
        self.indi_client.sendNewNumber(filter_slot)
        return None
