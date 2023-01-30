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


import copy
import functools
import os
from pathlib import Path

from astropy.io import fits
import cv2
import numpy

from utils.i18n import _
from ..logging import logger,return_error,return_success,return_warning

class ImageProcessor(object):
    """
        Image processing API Interface
    """

    def __init__(self) -> None:
        """
            Initialize ImageProcessor object
            Args : None
            Returns : None
        """
        self.image_list = []
        self._adu_mask = None

    def load_new_image(self , path : str) -> dict:
        """
            Loaded a new image from the given path
            Args :
                path : str
            Returns : dict
        """
        if not os.path.isfile(path):
            return return_error(_("Could not load new image from given path"))
        _file = Path(path)
        indi_rgb = True
        # Load Fits Image
        if path.suffix in ['.fit']:
            hdulist = fits.open(_file)
            depth = hdulist[0].header['BITPIX']
            image_bayerpat = hdulist[0].header.get('BAYERPAT')
            data = hdulist[0].data
        # Load JPG Image
        elif path.suffix in ['.jpg', '.jpeg']:
            indi_rgb = False
            data = cv2.imread(str(_file), cv2.IMREAD_UNCHANGED)
            depth = 8
            image_bayerpat = None
        # Load PNG Image
        elif path.suffix in ['.png']:
            indi_rgb = False
            data = cv2.imread(str(_file), cv2.IMREAD_UNCHANGED)
            depth = 8
            image_bayerpat = None
        
        hdulist[0].header['OBJECT'] = 'LightAPT'
        hdulist[0].header['TELESCOP'] = 'LightAPT Server'
        # Releasing the original image
        _file.unlink()

        if not len(hdulist[0].data.shape) == 2:
            # color data
            if indi_rgb:
                # INDI returns array in the wrong order for cv2
                hdulist[0].data = numpy.swapaxes(hdulist[0].data, 0, 2)
                hdulist[0].data = numpy.swapaxes(hdulist[0].data, 0, 1)
                hdulist[0].data = cv2.cvtColor(hdulist[0].data, cv2.COLOR_RGB2BGR)
            else:
                # normal rgb data
                pass

        image_bit_depth = self._detectBitDepth(hdulist)
        

        image_data = {
            'hdulist'          : hdulist,
            'calibrated'       : False,
            'depth'     : depth,
            'image_bayerpat'   : image_bayerpat,
            'image_bit_depth'  : image_bit_depth,
            'indi_rgb'         : indi_rgb,
            'sqm_value'        : None,    # populated later
            'lines'            : list(),  # populated later
            'stars'            : list(),  # populated later
        }

        self.image_list.insert(0, image_data)  # new image is first in list

    def detect_depth(self , hdulist : fits.HDUList) -> int:
        """
            Detect the depth of the image
            Args :
                hdulist : fits image data
            Returns : int
        """
        max_val = numpy.amax(hdulist[0].data)
        if max_val > 32768:
            image_bit_depth = 16
        elif max_val > 16384:
            image_bit_depth = 15
        elif max_val > 8192:
            image_bit_depth = 14
        elif max_val > 4096:
            image_bit_depth = 13
        elif max_val > 2096:
            image_bit_depth = 12
        elif max_val > 1024:
            image_bit_depth = 11
        elif max_val > 512:
            image_bit_depth = 10
        elif max_val > 256:
            image_bit_depth = 9
        else:
            image_bit_depth = 8
        return image_bit_depth

    def calculate_histogram(self, data : cv2.Mat , exposure : float) -> float:
        """
            Calculates the histogram of the image
            Args : 
                data : cv2.Mat
                exposure : float
        """
        if self._adu_mask is None:
            # This only needs to be done once if a mask is not provided
            self._generateAduMask(data)
        if len(data.shape) == 2:
            # mono
            m_avg = cv2.mean(src=data, mask=self._adu_mask)[0]
            adu = m_avg
        else:
            data_mono = cv2.cvtColor(data, cv2.COLOR_BGR2GRAY)
            m_avg = cv2.mean(src=data_mono, mask=self._adu_mask)[0]
            adu = m_avg
        if adu <= 0.0:
            # ensure we do not divide by zero
            logger.warning('Zero average, setting a default of 0.1')
            adu = 0.1
        logger.info('Brightness average: %0.2f', adu)
        
        adu_dev = float(10)
        self.current_adu_target = 0
        self.target_adu_found = False
        self.target_adu = 75
        self.hist_adu = []

        target_adu_min = self.target_adu - adu_dev
        target_adu_max = self.target_adu + adu_dev
        current_adu_target_min = self.current_adu_target - adu_dev
        current_adu_target_max = self.current_adu_target + adu_dev
        exp_scale_factor = 1.0  # scale exposure calculation
        history_max_vals = 6    # number of entries to use to calculate average

        if not self.target_adu_found:
            self.recalculate_exposure(exposure , adu, target_adu_min, target_adu_max, exp_scale_factor)

        self.hist_adu.append(adu)
        self.hist_adu = self.hist_adu[(history_max_vals * -1):]  # remove oldest values, up to history_max_vals
        logger.info('Current target ADU: %0.2f (%0.2f/%0.2f)', self.current_adu_target, current_adu_target_min, current_adu_target_max)
        logger.info('Current ADU history: (%d) [%s]', len(self.hist_adu), ', '.join(['{0:0.2f}'.format(x) for x in self.hist_adu]))

        adu_average = functools.reduce(lambda a, b: a + b, self.hist_adu) / len(self.hist_adu)
        logger.info('ADU average: %0.2f', adu_average)

        hist = cv2.calcHist(data, [0], None, [256], [0, 256])
        logger.info(hist)

        # Need at least x values to continue
        if len(self.hist_adu) < history_max_vals:
            return adu, 0.0

        # only change exposure when 70% of the values exceed the max or minimum
        if adu_average > current_adu_target_max:
            logger.warning('ADU increasing beyond limits, recalculating next exposure')
            self.target_adu_found = False
        elif adu_average < current_adu_target_min:
            logger.warning('ADU decreasing beyond limits, recalculating next exposure')
            self.target_adu_found = False

        

        return adu, adu_average

    def _generateAduMask(self, img):
        logger.info('Generating mask based on ADU_ROI')

        image_height, image_width = img.shape[:2]

        # create a black background
        mask = numpy.zeros((image_height, image_width), dtype=numpy.uint8)

        adu_roi = []

        try:
            x1 = int(adu_roi[0] / self.bin_v.value)
            y1 = int(adu_roi[1] / self.bin_v.value)
            x2 = int(adu_roi[2] / self.bin_v.value)
            y2 = int(adu_roi[3] / self.bin_v.value)
        except IndexError:
            logger.warning('Using central ROI for ADU calculations')
            x1 = int((image_width / 2) - (image_width / 3))
            y1 = int((image_height / 2) - (image_height / 3))
            x2 = int((image_width / 2) + (image_width / 3))
            y2 = int((image_height / 2) + (image_height / 3))

        # The white area is what we keep
        cv2.rectangle(
            img=mask,
            pt1=(x1, y1),
            pt2=(x2, y2),
            color=(255),  # mono
            thickness=cv2.FILLED,
        )

        self._adu_mask = mask

    def recalculate_exposure(self, exposure : float, adu, target_adu_min, target_adu_max, exp_scale_factor):
        """
            Recalculates the exposure value of the given image
            Args:
                adu : image
                target_adu_min :
                target_adu_max :
                exp_scale_factor : float # scale exposure calculation
        """
        # Until we reach a good starting point, do not calculate a moving average
        if adu <= target_adu_max and adu >= target_adu_min:
            logger.warning('Found target value for exposure')
            self.current_adu_target = copy.copy(adu)
            self.target_adu_found = True
            self.hist_adu = []
            return
        # Scale the exposure up and down based on targets
        if adu > target_adu_max:
            new_exposure = exposure - ((exposure - (exposure * (self.target_adu / adu))) * exp_scale_factor)
        elif adu < target_adu_min:
            new_exposure = exposure - ((exposure - (exposure * (self.target_adu / adu))) * exp_scale_factor)
        else:
            new_exposure = exposure

        logger.warning('New calculated exposure: %0.6f', new_exposure)
        return new_exposure
