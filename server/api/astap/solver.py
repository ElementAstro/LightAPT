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

import subprocess
import numpy as np

from ...logging import logger , return_error , return_success

class AstapSolveAPI(object):
    """
        Astap solve API via native command line interface
    """

    @staticmethod
    def solve(image, ra = None, dec = None, radius = None, fov = None, downsample = None, debug = False ,update = False , _wcs = True , timeout = 60) -> dict:
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
            Returns : dict

        """
        if image is None or not isinstance(image,(str,np.ndarray)):
            return #return_error("Unknown image type was specified")
        
        command = ["astap_cli"]
        # check arguments
        # TODO : both ra and dec should be converted to str if the format is float
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
        if debug == True:
            command.append('-debug')
        if update == True:
            command.append('-update')
        if _wcs == True:
            command.append('-wcs')

        # if the image path is given
        if isinstance(image , str):
            #if image.find("/") == -1:
                #image = os.path.join(os.getcwd(),"images",image)
            command.extend(["-f",image])

        logger.debug("Command line : {}".format(command))
        try:
            output = subprocess.check_output(command , timeout=timeout).decode()
        except TimeoutError:
            return return_error("Solve timeout")
        except subprocess.CalledProcessError as e:
            return return_error("Command failed",{"error": e})
        output_ = output.split("\n")
        ra = None
        dec = None
        fov = None
        for item in output_:
            if item.find("Solution found:") != -1:
                ra_dec = item.replace("Solution found: ","").replace("  "," ").replace(":","")
                ra_h,ra_m,ra_s,dec_h,dec_m,dec_s = ra_dec.split(" ")
                ra = ra_h + ":" + ra_m + ":" + ra_s
                dec = dec_h + ":" + dec_m + ":" + dec_s
            elif item.find("Set FOV=") != -1:
                tmp = item[item.index("Set FOV=")+8::]
                fov = tmp.split("d")[0]
        if ra is None or dec is None:
            return return_error("Solve failed")
        
        return return_success("Solve succeeded",{"ra": ra, "dec": dec,"fov":fov})
    
# A example:
#print(AstapSolveAPI.solve("test.fits",ra=5.1,dec=88,fov=2.8))