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

import psutil
import subprocess
from utils.i18n import _
from ...logging import logger

class PHD2Starter(object):
    """
        Start and stop PHD2 server via command line interface
    """

    def __init__(self) -> None:
        """
            Initialize the PHD2Starter object
            Args : None
            Returns : None
        """
        self.process = None

    @property
    def is_running(self) -> bool:
        """
            Check if the server is running using psutil
        """
        pl = psutil.pids()
        for pid in pl:
            if psutil.Process(pid).name() == "phd2":
                return True
        return False

    def start(self , path = "/usr/bin/phd2") -> bool:
        """
            Start the PHD2 server in a subprocess
            Args : path : path to the phd2 executable file
            Returns : bool
        """
        if self.is_running:
            logger.error(_("PHD2 server is already running"))
            return True
        try:
            self.process = subprocess.Popen("phd2", shell=True)
        except Exception as e:
            logger.error(_("Failed to start phd2 server"))
            return False
        logger.info(_("Phd2 server started successfully"))
        return True

    def stop(self) -> bool:
        """
            Stop the phd2 server
            Args : None
            Returns : bool
        """
        if not self.is_running:
            logger.error(_("Phd2 server is not running"))
            return False

        self.process.terminate()

        try:
            self.process.wait(timeout=5)
        except Exception as e:
            logger.error(_("Failed to terminate Phd2 server : {}").format(e))
            return False
        return True
