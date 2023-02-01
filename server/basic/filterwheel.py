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

from .device import BasicDeviceAPI

class BasicFilterwheelInfo(object):
    """
        Basic filterwheel info container
    """
    _type = "" # type of the camera , must be given
    _name : str # name of the camera
    _id : int # id of the camera
    _description : str
    _timeout = 120
    _configration = "" # path to the configuration file

    _ipaddress : str # IP address only ASCOM and INDI
    _api_version : str # API version only ASCOM and INDI

    _filter_offset : list # list of filter offset
    _filter_name : list # list of filter name

    _current_position : int # current position

    _is_connected = False # Is the filterwheel connected
    _is_slewing = False # Is the filterwheel moving

    def get_dict(self) -> dict:
        """
            Return focuser information in a dictionary
            Args: None
            Return: dict
        """
        return {
            "type": self._type,
            "name": self._name,
            "id": self._id,
            "description": self._description,
            "timeout": self._timeout,
            "configration": self._configration,
            "current" : {
                "position" : self._current_position
            },
            "status" : {
                "is_connected" : self._is_connected,
                "is_slewing" : self._is_slewing
            },
            "properties" : {
                "filter_offset" : self._filter_offset,
                "filter_name" : self._filter_name
            },
            "network" : {
                "ipaddress" : self._ipaddress,
                "api_version" : self._api_version,
            }
        }

class BasicFilterwheelAPI(BasicDeviceAPI):
    """
        Basic filterwheel API Interface
    """

    # #################################################################
    #
    # Filterwheel Basic API (which will be called by client applications)
    #
    # #################################################################

    async def slew_to(self,params = {}) -> dict:
        """
            Let the filterwheel slew to the specified position
            Args :
                params : dict
                    position : int
            Returns : dict
        """

    async def get_filters_list(self,params = {}) -> dict:
        """
            Get a list of filter name and offset
            Args : None
            Retern : dict
                offset : list
                name : list
        """

    async def get_current_position(self,params = {}) -> dict:
        """
            Get the current position of the filterwheel
            Args : None
            Retern : dict
                position : int
        """
