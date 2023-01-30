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

import cv2
import numpy

from ..logging import logger


class SQM(object):

    def __init__(self, config, bin_v, mask=None) -> None:
        self.config = config
        self.bin_v = bin_v
        # both masks will be combined
        self._external_mask = mask
        self._sqm_mask = None

    def calculate(self, img, exposure, gain) -> float:
        if isinstance(self._sqm_mask, type(None)):
            # This only needs to be done once if a mask is not provided
            self._generateSqmMask(img)
        if len(img.shape) == 2:
            # mono
            img_gray = img
        else:
            # color
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        sqm_avg = cv2.mean(src=img_gray, mask=self._sqm_mask)[0]
        logger.info('Raw SQM average: %0.2f', sqm_avg)
        # offset the sqm based on the exposure and gain
        weighted_sqm_avg = (((self.config['CCD_EXPOSURE_MAX'] - exposure) / 10) + 1) * (sqm_avg * (((self.config['CCD_CONFIG']['NIGHT']['GAIN'] - gain) / 10) + 1))
        logger.info('Weighted SQM average: %0.2f', weighted_sqm_avg)
        return weighted_sqm_avg

    def _generateSqmMask(self, img):
        logger.info('Generating mask based on SQM_ROI')
        image_height, image_width = img.shape[:2]
        # create a black background
        mask = numpy.zeros((image_height, image_width), dtype=numpy.uint8)
        sqm_roi = self.config.get('SQM_ROI', [])
        try:
            x1 = int(sqm_roi[0] / self.bin_v.value)
            y1 = int(sqm_roi[1] / self.bin_v.value)
            x2 = int(sqm_roi[2] / self.bin_v.value)
            y2 = int(sqm_roi[3] / self.bin_v.value)
        except IndexError:
            logger.warning('Using central 20% ROI for SQM calculations')
            x1 = int((image_width / 2) - (image_width / 5))
            y1 = int((image_height / 2) - (image_height / 5))
            x2 = int((image_width / 2) + (image_width / 5))
            y2 = int((image_height / 2) + (image_height / 5))
        # The white area is what we keep
        cv2.rectangle(
            img=mask,
            pt1=(x1, y1),
            pt2=(x2, y2),
            color=(255),  # mono
            thickness=cv2.FILLED,
        )
        # combine masks in case there is overlapping regions
        if not isinstance(self._external_mask, type(None)):
            self._sqm_mask = cv2.bitwise_and(mask, mask, mask=self._external_mask)
            return
        self._sqm_mask = mask

