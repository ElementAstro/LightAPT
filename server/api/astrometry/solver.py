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
from ...logging import logger , return_error , return_success

class AstrometryOfflineSolver(object):
    """
        Astrometry offline solver via native command line interface

        I do not will we still use this as the default solver.
    """

    @staticmethod
    def solve(image : str , ra = None , dec = None , radius = None , downsample = None,
              depth = None , scale_low = None , scale_high = None , width = None , height = None,
              scale_units = None , overwrite = True , no_plot = True , verify = False,
              debug = False , timeout = 30 , resort = False , _continue = False , no_tweak = False) -> dict:
        """
            Solve the given image by astrometry and return the ra and dec if the solve is successful
            Args:
                image : str # the full path to the image
                ra : str # the ra hour angle
                dec : str # the dec hour angle
                radius : float # the radius of the search region
                downsample : int # the downsample , default is 1
                depth : list # a list of depth , like [20,30,40]
                scale_low : float # lowest of the scale
                scale_high : float # highest of the scale
                width : int # the width of the image
                height : int # the height of the image
                scale_units : str # the scale unit , default is "degwidth"
                overwrite : bool # whether to overwrite the existing image
                no_plot : bool # whether to plot the solve results
                verity : bool # whether to verify the existing wcs file
                debug : bool # whether to print debug information
                timeout : int # the number of seconds to wait before giving up
                resort : bool # whether to resort the brightness of the image
                _continue : bool # whether to continue the old operation
                no_tweak : bool # whether to correct the old wcs file

            Returns : dict
                ra : str
                dec : str
        """
        if image is None or not isinstance(image,str):
            return return_error("Unknown image type was specified")
        
        command = ["solve-field",image]

        if ra is not None and isinstance(ra,str):
            command.extend(["--ra",ra])
        if dec is not None and isinstance(dec,str):
            command.extend(["--dec",dec])
        if radius is not None and isinstance(radius,float):
            command.extend(["--radius",str(radius)])
        if downsample is not None and isinstance(downsample,int):
            command.extend(["--downsample",str(downsample)])
        if depth is not None and isinstance(depth,list):
            command.extend("--depth",str(depth).replace("[","").replace("]","").replace(" ",""))
        if scale_low is not None and isinstance(scale_low,float):
            command.extend("--scale-low",str(scale_low))
        if scale_high is not None and isinstance(scale_high,float):
            command.extend("--scale-high",str(scale_high))
        if width is not None and isinstance(width,int):
            command.extend("--width",str(width))
        if height is not None and isinstance(height,int):
            command.extend("--height",str(height))
        if scale_units is not None and isinstance(scale_units,str):
            command.extend("--scale_units",scale_units)
        if overwrite == True:
            command.append("--overwrite")
        if no_plot == True:
            command.append("--no-plot")
        if verify == True:
            command.append("--verify")
        if resort == True:
            command.append("--resort")
        if _continue == True:
            command.append("--continue")
        if no_tweak == True:
            command.append("--no-tweak")
        logger.debug("Command line : {}".format(command))

        try:
            output = subprocess.check_output(command , timeout=timeout).decode()
        except TimeoutError:
            return return_error("Solve timeout")
        print(output)
        output_ = output.split("\n")
        print(output_)
        ra = None
        dec = None
        for item in output_:
            if item.find("Field center: (RA H:M:S, Dec D:M:S) = ") != -1:
                ra_dec = item.replace("Field center: (RA H:M:S, Dec D:M:S) = ","").replace("(","").replace(").","")
                ra , dec = ra_dec.split(",")
            
            if item.find("Field size: ") != -1:
                fov_ = item.replace("Field size: ","").replace(" ","")
                fov_x  , fov_y = fov_.split("x")
        if ra is None or dec is None:
            return return_error("Solve failed")
        
        return return_success("Solve succeeded",{"ra": ra, "dec": dec,"fov_x" : fov_x, "fov_y" : fov_y})
        