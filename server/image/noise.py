# coding=utf-8

"""

Copyright(c) 2022 Max Qian  <astroair.cn>

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

import numpy as np

# #########################################################################
# Some functions about adding noise to image
# #########################################################################

from random import random,randint

def add_salt_pepper_noise(image : np.ndarray, threshold : float) -> np.ndarray:
    """
        Add salt and pepper noise to image
        Args:
            image: np.ndarray # image to add noise
            threshold: float # Salt noise threshold
        Returns:
            np.ndarray
    """
    output = np.zeros(image.shape, np.uint8)
    thres = 1 - threshold
    # Traverse the grayscale of the entire image | 遍历整个图片的灰度级
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            # Generate a random number between 0-1 | 生成一个随机0-1之间的随机数
            randomnum = random()
            # If the random number is greater than the salt noise threshold of 0.1, set the gray level value at this position to 0, that is, add salt noise
            if randomnum < threshold:  # 如果随机数大于盐噪声阈值0.1，则将此位置灰度级的值设为0，即添加盐噪声
                output[i][j] = 0
            # If the random number is greater than the pepper noise threshold of 1-0.1, set the output of the gray level at this position to 255, that is, add pepper noise
            elif randomnum > thres:  # 如果随机数大于胡椒噪声阈值1-0.1，则将此位置灰度级的输出设为255，即添加胡椒噪声
                output[i][j] = 255
            # If the random number is between the two, the gray level value at this position is equal to the gray level value of the original image
            else:  # 如果随机数处于两者之间，则此位置的灰度级的值等于原图的灰度级值
                output[i][j] = image[i][j]
    return output

def add_gaussian_noise(image : np.ndarray, mean : float, var : float) -> np.ndarray:
    """
        Add gaussian noise to image | 为图像添加高斯噪声
        Args:
            image: np.ndarray # image to add noise
            mean: float # mean value 均值
            var: float # variance value 方差
        Returns:
            np.ndarray # image with gaussian noise
    """
    image = np.array(image/255, dtype=float)
    noise = np.normal(mean, var ** 0.5, image.shape)
    output = image + noise
    output_handle = np.array([[[0]*3 for i in range(output.shape[1])] for i in range(output.shape[0])], dtype=float)
    if output.min() < 0:
        low_clip = -1.
    else:
        low_clip = 0.
    for i in range (output.shape[0]):
        for j in range (output.shape[1]):
            for k in range (output.shape[2]):
                if output[i][j][k] < low_clip:
                    output_handle[i][j][k] = low_clip
                elif output[i][j][k] > 1.0:
                    output_handle[i][j][k] = 1.0
                else:
                    output_handle[i][j][k] = output[i][j][k]
    output = np.uint8(output_handle*255)
    return output

def add_random_noise(image : np.ndarray,threshold : float) -> np.ndarray:
    """
        Add random noise to image | 为图像添加随机噪声
        Args:
            image: np.ndarray # image to add noise
            threshold: float # probability to add noise
        Returns:
            np.ndarray # image with random noise
    """
    output = image
    n = randint(1, 1000) + int(threshold*20000)
    for k in range(n-500):
        a = randint(0, 50)
        b = randint(0, 50)
        c = randint(0, 50)
        i = randint(0, image.shape[0]-1)
        j = randint(0, image.shape[1]-1)
        output[i][j][0] = 255-a
        output[i][j][1] = 255-b
        output[i][j][2] = 255-c
    for k in range(n):
        a = randint(0, 50)
        b = randint(0, 50)
        c = randint(0, 50)
        i = randint(0, image.shape[0]-1)
        j = randint(0, image.shape[1]-1)
        output[i][j][0] = a
        output[i][j][1] = b
        output[i][j][2] = c
    return output