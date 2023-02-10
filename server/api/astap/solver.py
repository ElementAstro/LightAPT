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

import asyncio
import os
import traceback
from pathlib import Path

from ...logging import astap_logger as logger

async def solve(image, ra=None, dec=None, radius=None, fov=None, downsample=None, debug=False, update=False,
                    max_number_star = 500 , tolerance = 0.007 , _wcs=True, timeout=60) -> dict:
    """
        Solve the given image with the parameters\n
        Args:
            image : str # the path to the image or just the image\n
            The following parameters are all optional but can make solver faster
            ra : float # current RA
            dec : float # current dec
            radius : float / str # range to search
            fov : float # FOV of the camera
            downsample : int # downsample , 1 , 2 , 4 , 0 means auto
            debug : bool # debug mode , will have more output
            update : bool # if the image type is not fits , write a new ftis image
            wcs : bool # write a wcs file like astrometry
            timeout : int # timeout in seconds
        Returns : {
            'ra': float
            'dec': float
            'fov': float
            'message': None
            'rota_x' : float
            'rota_y' : float
        }
        if faced error, then message will not be none and display basic error message.
        if correctly executed, message will be none
    """
    ret_struct = {
        'ra': None,
        'dec': None,
        'fov': None,
        'message': None,
        'rota_x' : None,
        "rota_y" : None,
    }
    
    if image is None or not isinstance(image, (str, Path)):  # (, np.ndarray)
        ret_struct['message'] = 'wrong image file type'
        return ret_struct
    if type(image) == str:
        image = Path(image)
    if not image.exists():
        ret_struct['message'] = 'file doesnot exists'
        return ret_struct

    command = ["astap_cli"]
    # check arguments
    if ra is not None:
        command.extend(['-ra', str(ra)])
    if dec is not None:
        command.extend(['-spd', str(dec + 90)])
    if radius is not None:
        command.extend(['-r', str(radius)])
    if fov is not None:
        command.extend(['-fov', str(fov)])
    if downsample is not None:
        command.extend(['-z', str(downsample)])
    if debug:  # simplify if statement
        command.append('-debug')
    if update:
        command.append('-update')
    if _wcs:
        command.append('-wcs')
    
    # Add a limit of the max number of stars
    command.extend(['-s',str(max_number_star)])
    # tolerance
    command.extend(['-t',str(tolerance)])

    # no need to check type here
    command.extend(["-f", str(image)])

    command = ' '.join(command)  # change command as it is called by asyncio subprocess
    logger.debug(f"Command line : {command}")
    try:  # asyncio call
        astap = await asyncio.subprocess.create_subprocess_shell(command, stdin=asyncio.subprocess.PIPE,
                                                                 stdout=asyncio.subprocess.PIPE)
        std_out, std_error = await asyncio.wait_for(astap.communicate(), timeout=timeout)
    except TimeoutError:
        ret_struct['message'] = 'Solve timeout'
        logger.error(f'Solve Timeout with input {image}, {ra}, {dec}, {fov}')
        return ret_struct
    except:
        logger.error(traceback.format_exc())
        ret_struct['message'] = 'unpredictable error'
        return ret_struct
    output_ = std_out.decode().split("\n")
    # same para in input?????????
    for item in output_:
        if item.find("Solution found:") != -1:
            ra_dec = item.replace("Solution found: ", "").replace("  ", " ").replace(":", "")
            ra_h, ra_m, ra_s, dec_h, dec_m, dec_s = ra_dec.split(" ")
            ret_struct['ra'] = ra_h + ":" + ra_m + ":" + ra_s
            ret_struct['dec'] = dec_h + ":" + dec_m + ":" + dec_s
        elif item.find("Set FOV=") != -1:
            tmp = item[item.index("Set FOV=") + 8::]
            ret_struct['fov'] = tmp.split("d")[0]
    if ret_struct['ra'] is None or ret_struct['dec'] is None:
        ret_struct['message'] = 'Solve failed'
        return ret_struct
    
    if _wcs:
        # Read the WCS File to get the rotation information
        def cut(obj, sec):
            return [obj[i:i+sec] for i in range(0,len(obj),sec)]
        # Check if the wcs file is existing
        wcs_path = image.name.split(".")[0] + ".wcs"
        if not os.path.exists(wcs_path):
            ret_struct['message'] = 'No wcs file found'
            return ret_struct
        with open(wcs_path,encoding="utf-8",mode="r") as f:
            wcs = cut(f.read(),80)
            for item in wcs:
                if item.find("CROTA1  =  ") != -1:
                    ret_struct['rota_x'] = item.split("/")[0].split("=")[1].replace(" ","")
                if item.find("CROTA2  =  ") != -1:
                    ret_struct['rota_y'] = item.split("/")[0].split("=")[1].replace(" ","")
                    
    return ret_struct
