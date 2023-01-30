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

import math
import cv2

from ..logging import logger
from utils.i18n import _

class Draw(object):
    def __init__(self, config, bin_v, mask=None) -> cv2.Mat:
        self.config = config
        self.bin_v = bin_v
        self._sqm_mask = mask

    def main(self, sep_data):
        image_height, image_width = sep_data.shape[:2]
        if isinstance(self._sqm_mask, type(None)):
            ### Draw ADU ROI if detection mask is not defined
            ###  Make sure the box calculation matches image.py
            adu_roi = []
            try:
                adu_x1 = int(adu_roi[0] / self.bin_v.value)
                adu_y1 = int(adu_roi[1] / self.bin_v.value)
                adu_x2 = int(adu_roi[2] / self.bin_v.value)
                adu_y2 = int(adu_roi[3] / self.bin_v.value)
            except IndexError:
                adu_x1 = int((image_width / 2) - (image_width / 3))
                adu_y1 = int((image_height / 2) - (image_height / 3))
                adu_x2 = int((image_width / 2) + (image_width / 3))
                adu_y2 = int((image_height / 2) + (image_height / 3))
            logger.info('Draw box around ADU_ROI')
            cv2.rectangle(
                img=sep_data,
                pt1=(adu_x1, adu_y1),
                pt2=(adu_x2, adu_y2),
                color=(128, 128, 128),
                thickness=1,
            )
        else:
            # apply mask to image
            sep_data = cv2.bitwise_and(sep_data, sep_data, mask=self._sqm_mask)
        logger.info('Draw keogram meridian')

        opp_1 = math.tan(math.radians(self.config['KEOGRAM_ANGLE'])) * (image_height / 2)
        m_x1 = int(image_width / 2) + int(opp_1)
        m_y1 = 0
        m_x2 = int(image_width / 2) - int(opp_1)
        m_y2 = image_height
        
        cv2.line(
            sep_data,
            (m_x1, m_y1),
            (m_x2, m_y2),
            (64, 64, 64),
            3,
        )
        return sep_data

