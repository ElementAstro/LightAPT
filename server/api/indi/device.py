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

from PyIndi import BaseDevice
import PyIndi
from .client import IndiClient

from utils.i18n import _
from ...logging import logger

class IndiBaseDevice:
    """
        INDI Basic Device Interface
    """

    def __init__(self, indi_client: IndiClient, indi_device: BaseDevice = None) -> None:
        """
            Initialize a new IndiBaseDevice object
            Args:
                indi_client: IndiClient , a initialized IndiClient
                indi_device: IndiDevice
            Return : None
        """
        self.this_device = indi_device
        self.indi_client = indi_client
        if self.this_device is not None:
            self.this_connection_switch = self.this_device.getSwitch("CONNECTION")
        else:
            self.this_connection_switch = None

    def connect(self) -> None:
        """
            Connect to the device
            Args : None
            Return : None
        """
        if self.this_device is None:
            logger.warning(_("No device specified"))
        elif not (self.this_device.isConnected()):
            # Property vectors are mapped to iterable Python objects
            # Hence we can access each element of the vector using Python indexing
            # each element of the "CONNECTION" vector is a ISwitch
            self.this_connection_switch[0].s = PyIndi.ISS_ON  # the "CONNECT" switch
            # the "DISCONNECT" switch
            self.this_connection_switch[1].s = PyIndi.ISS_OFF  
            # send this new value to the device
            self.indi_client.sendNewSwitch(self.this_connection_switch)
        else:
            logger.info(_("Device had already been connected"))

    def disconnect(self) -> None:
        """
            Disconnects the INDI server
            Args : None
            Return : None
        """
        if self.this_device is None:
            logger.warning(_("No INDI device specified"))
        elif self.this_device.isConnected():
            # Property vectors are mapped to iterable Python objects
            # Hence we can access each element of the vector using Python indexing
            # each element of the "CONNECTION" vector is a ISwitch
            self.this_connection_switch[0].s = PyIndi.ISS_OFF  # the "CONNECT" switch
            self.this_connection_switch[1].s = PyIndi.ISS_ON  # the "DISCONNECT" switch
            self.indi_client.sendNewSwitch(self.this_connection_switch)  # send this new value to the device
        else:
            logger.info(_("Device is not connected"))