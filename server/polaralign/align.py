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
from pathlib import Path
import traceback

from ..logging import polar_align_logger as logger

from astropy.coordinates import FK5, AltAz
from astropy.coordinates import SkyCoord, EarthLocation
from astropy.wcs import WCS

class PolarAlign(object):
    """
         ____       _                 _    _ _             \n
        |  _ \ ___ | | __ _ _ __     / \  | (_) __ _ _ __  \n
        | |_) / _ \| |/ _` | '__|   / _ \ | | |/ _` | '_ \ \n
        |  __/ (_) | | (_| | |     / ___ \| | | (_| | | | |\n
        |_|   \___/|_|\__,_|_|    /_/   \_\_|_|\__, |_| |_|\n
                                            |___/          \n

        Polar calibration completed by platesolve.

        By calculating the center coordinates of the telescope's field of view and 
        comparing them with the polar coordinates, the error can be calculated and 
        adjusted continuously to reduce the error until the calibration is completed.

        For some unknown reasons, the speed of asap parsing in this case is much slower 
        than that of astrometry, and there are often dead cycles.

        So we choose to use astrometry as the platesolve engine.
    """

    def __init__(self , lat : float , lon : float) -> None:
        """
            Args:
                lat : float
                lon : float
        """
        self.lat, self.lon = lat , lon
        self.site = EarthLocation.from_geodetic(lon=lon, lat=lat)

    def __del__(self) -> None:
        """
        
        """

    def __str__(self) -> str:
        return "Polar Aligner by Max Qian via Astrometry.net"
    
    """
        General process:
        First of all, we need to take a picture first. Of course, before that, 
        we need to assume that the telescope is well focused and ready for everything. 
        But these are beyond our control, so we can only do this part well.

        Then we will use astrometry to resolve the coordinates and rotation angle pointed 
        by the center of this photo. Calculate the coordinate difference with the pole and 
        return it to the client for adjustment.

        When users adjust, we still need to shoot continuously to let users know whether
        they adjust correctly.When the error is less than a certain value, the calibration 
        is completed.Before that, there was a cycle
    """

    async def platesolve(self , image : str , downsample : int = 1 , timeout : int = 30) -> dict:
        """
            Call astrometry to solve the picture and obtain the coordinates.\n
            Args :
                image : str # the name of the image 
                downsample : int
            Returns : {
                "ra" : str # RA
                "dec" : str # DEC
                "fov_x" : float,
                "fov_y" : float,
                "ratation" : float,
                "rotation" : float,
            }
            Why don't we directly use the ready-made astrometry-worker?
            Because it doesn't need many parameters to analyze the sky near the polar axis,
            everything is simple
        """
        ret_struct = {
            "ra" : None,
            "dec" : None,
            "fov_x" : None,
            "fov_y" : None,
            "ratation" : None,
            "message" : None
        }

        if image is None or not isinstance(image, (str, Path)):  # (, np.ndarray)
            ret_struct['message'] = 'wrong image file type'
            return ret_struct
        if type(image) == str:
            image = Path(image)
        if not image.exists():
            ret_struct['message'] = 'file doesnot exists'
            return ret_struct
        
        command = ["solve-field",str(image)]
        #command.extend(["--ra",str(90)])
        command.extend(["--dec",str(90)])
        command.extend(["--radius",str(5)])
        if downsample is not None and isinstance(downsample,int):
            command.extend(["--downsample",str(downsample)])
        command.extend(["--depth",str("20,30,40")])
        
        command.extend(["--scale-units","degwidth"])
        command.append("--overwrite")
        command.append("--no-plot")
        command.append("--no-verify")
        command.append("--resort")

        command = ' '.join(command)  # change command as it is called by asyncio subprocess
        logger.debug(f"Command line : {command}")
        try:  # asyncio call
            astap = await asyncio.subprocess.create_subprocess_shell(command, stdin=asyncio.subprocess.PIPE,
                                                                    stdout=asyncio.subprocess.PIPE)
            std_out, std_error = await asyncio.wait_for(astap.communicate(), timeout=timeout)
        except TimeoutError:
            ret_struct['message'] = 'Solve timeout'
            logger.error(f'Solve Timeout')
            return ret_struct
        except:
            logger.error(traceback.format_exc())
            ret_struct['message'] = 'unpredictable error'
            return ret_struct
        
        output_ = std_out.decode().split("\n")
        
        for item in output_:
            if item.find("Field center: (RA H:M:S, Dec D:M:S) = ") != -1:
                ra_dec = item.replace("Field center: (RA H:M:S, Dec D:M:S) = ","").replace("(","").replace(").","")
                ret_struct["ra"] , ret_struct["dec"] = ra_dec.split(",")
                
            if item.find("Field size: ") != -1:
                fov_ = item.replace("Field size: ","").replace(" ","")
                ret_struct["fov_x"]  , ret_struct["fov_y"] = fov_.split("x")
                ret_struct["fov_y"] = ret_struct["fov_y"].replace("arcminutes","")
            
            if item.find("Field rotation angle: up is ") != -1:
                ret_struct["ratation"] = item.replace("Field rotation angle: up is ","").replace(" degrees E of N","")

        if ret_struct['ra'] is None or ret_struct['dec'] is None:
            ret_struct['message'] = 'Solve failed'
            return ret_struct

        return ret_struct
    
    def convert_j2000(self , ra : float, dec : float) -> SkyCoord:
        """
            Convert JNow to J2000
        """
        return SkyCoord(ra=ra, dec=dec, frame='fk5', unit="deg", equinox="J2000")
    
    def convert_altaz(self, ra : float, dec : float) -> SkyCoord:
        """
            Convert RA/DEC to AZ/ALT
        """
        coord = self.convert_j2000(ra,dec)
        # TODO : We need to know when the image was captured
        time = 000
        altaz_frame = AltAz(obstime=time, location=self.site)
        return coord.transform_to(altaz_frame)
    
    async def calc_error(self,info : dict) -> dict:
        """
            Calculate error
            Args:
                info : dict # returned by platesolve
            Returns: {
            
            }
        """

