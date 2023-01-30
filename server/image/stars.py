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


from math import sqrt
import time
from pathlib import Path
import cv2
import numpy
#from ..logging import #logger ,return_error,return_success,return_warning


class CalcStars(object):

    _distanceThreshold = 10

    def __init__(self, mask=None,detection_threshold = 0.6) -> None:
        """
            Initialize the star calculation object
            Args:
                mask : optional
                detection_threshold : optional
            Returns: None
        """
        self.mask = mask
        self._detection_threshold = detection_threshold
        # Image folder
        self.image_dir = Path(__file__).parent.parent.joinpath('images').absolute()
        # start with a black image
        template = numpy.zeros([15, 15], dtype=numpy.uint8)
        # draw a white circle
        cv2.circle(
            img=template,
            center=(7, 7),
            radius=3,
            color=(255, 255, 255),
            thickness=cv2.FILLED,
        )
        # blur circle to simulate a star
        self.star_template = cv2.blur(
            src=template,
            ksize=(2, 2),
        )
        self.star_template_w, self.star_template_h = self.star_template.shape[::-1]

    def detect_stars(self, original_data : cv2.Mat) -> list:
        """
            Detect stars on the given image
            Args:
                original_data : cv2.Mat
            Returns: list
        """
        if isinstance(self.mask, type(None)):
            # This only needs to be done once if a mask is not provided
            self.generate_mask(original_data)
        masked_img = cv2.bitwise_and(original_data, original_data, mask=self.mask)
        if len(original_data.shape) == 2:
            # gray scale or bayered
            grey_img = masked_img
        else:
            # assume color
            grey_img = cv2.cvtColor(masked_img, cv2.COLOR_BGR2GRAY)
        sep_start = time.time()
        result = cv2.matchTemplate(grey_img, self.star_template, cv2.TM_CCOEFF_NORMED)
        result_filter = numpy.where(result >= self._detection_threshold)
        blobs = list()
        for pt in zip(*result_filter[::-1]):
            for blob in blobs:
                if (abs(pt[0] - blob[0]) < self._distanceThreshold) and (abs(pt[1] - blob[1]) < self._distanceThreshold):
                    break
            else:
                # if none of the points are under the distance threshold, then add it
                blobs.append(pt)
        sep_elapsed_s = time.time() - sep_start
        #logger.info('Star detection in %0.4f s', sep_elapsed_s)
        #logger.info('Found %d objects', len(blobs))
        self.draw_circles(original_data, blobs)
        return blobs

    def generate_mask(self, img : cv2.Mat) -> None:
        """
            Generate a mask
            Args :
                img : cv2.Mat
            Returns : None
        """
        image_height, image_width = img.shape[:2]
        # create a black background
        mask = numpy.zeros((image_height, image_width), dtype=numpy.uint8)
        sqm_roi = []
        try:
            x1 = int(sqm_roi[0] / self.bin_v.value)
            y1 = int(sqm_roi[1] / self.bin_v.value)
            x2 = int(sqm_roi[2] / self.bin_v.value)
            y2 = int(sqm_roi[3] / self.bin_v.value)
        except IndexError:
            #logger.warning('Using central ROI for star detection')
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
        self.mask = mask

    def draw_circles(self, sep_data : cv2.Mat, blob_list ) -> None:
        """
            Draw circles on the image using opencv
            Args :
                sep_data : cv2.Mat
                blob_list : list
            Returns : None
        """
        color_bgr = [39, 117, 182]
        color_bgr.reverse()
        #logger.info('Draw circles around objects')
        for blob in blob_list:
            x, y = blob
            center = (
                int(x + (self.star_template_w / 2)) + 1,
                int(y + (self.star_template_h / 2)) + 1,
            )
            cv2.circle(
                img=sep_data,
                center=center,
                radius=6,
                color=tuple(color_bgr),
                thickness=2,
            )

    def calc_hfd(self,image : numpy.ndarray,outer_diameter : int) -> float:
        """
            Calculate the HFD of an image | 计算图像HFD
            Args:
                image : np.ndarray # image to calculate
                outer_diameter : int # outer diameter of the circle
            Returns:
                float: HFD of the image
        """
        if outer_diameter is None:
            outer_diameter = 60
        output = image
        # Calculate the mean of the image
        # Meanfilter ?
        mean = numpy.mean(image)
        for x in range(image.shape[0]):
            for y in range(image.shape[1]):
                if image[x][y].any() < mean: 
                    output[x][y] = 0
                else:
                    output[x][y] -= mean
        
        out_radius = outer_diameter / 2

        center_x = int(output.shape[0] / 2)
        center_y = int(output.shape[1] / 2)

        _sum,sum_dist = 0,0

        for x in range(image.shape[0]):
            for y in range(image.shape[1]):
                if pow(x - center_x,2) + pow(y - center_y,2) <= pow(out_radius,2):
                    _sum += output[x][y].any()
                    sum_dist = output[x][y] * sqrt(pow(x - center_x,2) + pow(y - center_y,2))
        if _sum != 0:
            return 2 * sum_dist / _sum
        return sqrt(2) * out_radius


if __name__ == '__main__':
    # The following is a simple example of how to use CalcStars
    calc = CalcStars(detection_threshold=0.6)
    img = cv2.imread("test.jpg")
    print(len(calc.detect_stars(img)))
    cv2.imwrite("tes1t.jpg",img)
    print(calc.calc_hfd(img,60))