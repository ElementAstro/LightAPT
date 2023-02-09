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

import os
import logging
import time

# Initialize logger object
logger = logging.getLogger("logger")

# logger parameters | 控制台日志参数
console_font = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handle = logging.StreamHandler()
console_handle.setFormatter(console_font)

# if the log folder is not exist, create it
if not os.path.exists("./logs"):
    os.mkdir("./logs")

# logger for astap
astap_logger = logging.getLogger("logger")
astap_logger.name = 'astap'
astap_logger.setLevel(logging.DEBUG)
f_astap_logger = logging.FileHandler("logs/astap.log")
f_astap_logger.setFormatter(console_font)
astap_logger.addHandler(f_astap_logger)
# logger for astrometry
astrometry_logger = logging.getLogger("logger")
astrometry_logger.name = "astrometry"
astrometry_logger.setLevel(logging.DEBUG)
f_astrometry_logger = logging.FileHandler("logs/astrometry.log")
f_astrometry_logger.setFormatter(console_font)
astrometry_logger.addHandler(f_astrometry_logger)
# logger for ascom devices
ascom_logger = logging.getLogger("logger")
ascom_logger.name = "ascom"
ascom_logger.setLevel(logging.DEBUG)
f_ascom_logger = logging.FileHandler("logs/ascom.log")
f_ascom_logger.setFormatter(console_font)
ascom_logger.addHandler(f_ascom_logger)
# logger for webssh
webssh_logger = logging.getLogger("logger")
webssh_logger.name = "webssh"
webssh_logger.setLevel(logging.DEBUG)
f_webssh_logger = logging.FileHandler("logs/webssh.log")
f_webssh_logger.setFormatter(console_font)
webssh_logger.addHandler(f_webssh_logger)

# Output log into a file | 文件日志
file_font = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handle = logging.FileHandler(filename=f"logs/{time.strftime('%Y-%m-%d#%H%M%S')}.log",encoding="utf-8",mode="w+")
file_handle.setFormatter(file_font)

logger.addHandler(console_handle)
logger.addHandler(file_handle)

# Set logger level | 设置日志级别
logger.setLevel(logging.DEBUG)

def return_success(message : str , params = {}) -> dict:
    """
        Return success message | 返回信息
        Args :
            message : str
            params : dict
        Returns : dict
    """
    logger.info(message)
    return {
        "status" : 0,
        "message" : message if message is not None else None,
        "params" :  params if params is not None else {}
    }

def return_error(message : str,params = {}) -> dict :
    """
        Return error message | 返回错误
        Args:
            message: str # Info message
            params : dict # Container
        Return : dict
    """
    logger.error(message)
    return {
        "status" : 1,
        "message" : message if message is not None else None,
        "params" : params if params is not None else {} 
    }

def return_warning(message : str,params = {}) -> dict:
    """
        Return warning message | 返回警告
        Args:
            message: str # Info message
            params : dict # Container
        Return : dict
    """
    logger.warning(message)
    return {
        "status" : 2,
        "message" : message if message is not None else None,
        "params" : params if params is not None else {}
    }