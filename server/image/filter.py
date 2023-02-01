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

# #################################################################
# Some functions about filter
# #################################################################

def medianfliter(img : np.ndarray, template_size : int) -> np.ndarray:
    """
        Median-fliter function | 中值滤波
        Args:
            img : np.ndarray # image to calculate
            template_size : int # template size , 3 or 5
        Returns:
            np.ndarray: median-fliter image
    """
    output = img
    if template_size == 3 :
        output1 = np.zeros(img.shape, np.uint8)
        # Complete the 9 surrounding squares and templates for bubble sorting
        for i in range(1, output.shape[0]-1):
            for j in range(1, output.shape[1]-1):
                value1 = [output[i-1][j-1], output[i-1][j], output[i-1][j+1], output[i][j-1], output[i][j], output[i][j+1], output[i+1][j-1], output[i+1][j], +output[i+1][j+1]]
                output1[i-1][j-1] = np.sort(value1)[4]
    elif template_size == 5:
        output1 = np.zeros(img.shape, np.uint8)
        # Complete 25 squares around to convolve with the template
        for i in range(2, output.shape[0]-2):
            for j in range(2, output.shape[1]-2):
                value1 = [output[i-2][j-2],output[i-2][j-1],output[i-2][j],output[i-2][j+1],output[i-2][j+2],output[i-1][j-2],output[i-1][j-1],output[i-1][j],output[i-1][j+1],\
                            output[i-1][j+2],output[i][j-2],output[i][j-1],output[i][j],output[i][j+1],output[i][j+2],output[i+1][j-2],output[i+1][j-1],output[i+1][j],output[i+1][j+1],\
                            output[i+1][j+2],output[i+2][j-2],output[i+2][j-1],output[i+2][j],output[i+2][j+1],output[i+2][j+2]]
                output1[i-2][j-2] = value1.sort()[12]
    else :
        print("Unknown template size , choose from 3 or 5")
    return output1

def meanflite(img : np.ndarray, template_size : int) -> np.ndarray:
    """
        Mean-flite function | 中值滤波
        Args:
            a : np.ndarray # image to calculate
            windowsize : int # window size, 3 or 5
        Returns:
            output : np.ndarray # image after mean filter process
    """
    output = img
    if template_size == 3:
        # Generate 3x3 templates
        window = np.ones((3, 3)) / 3 ** 2
        output1 = np.zeros(img.shape, np.uint8)
        # Complete the 9 surrounding squares and templates for bubble sorting
        for i in range(1, output.shape[0] - 1):
            for j in range(1, output.shape[1] - 1):
                value = (output[i - 1][j - 1] * window[0][0] + output[i - 1][j] * window[0][1] + output[i - 1][j + 1] *
                         window[0][2] + \
                         output[i][j - 1] * window[1][0] + output[i][j] * window[1][1] + output[i][j + 1] * window[1][
                             2] +\
                         output[i + 1][j - 1] * window[2][0] + output[i + 1][j] * window[2][1] + output[i + 1][j + 1] *
                         window[2][2])
                output1[i - 1][j - 1] = value
    elif template_size == 5:
        # Generate 5x5 templates
        window = np.ones((5, 5)) / 5 ** 2
        output1 = np.zeros(img.shape, np.uint8)
        # Complete 25 squares around to convolve with the template
        for i in range(2, output.shape[0] - 2):
            for j in range(2, output.shape[1] - 2):
                value = (output[i - 2][j - 2] * window[0][0] + output[i - 2][j - 1] * window[0][1] + output[i - 2][j] *
                         window[0][2] + output[i - 2][j + 1] * window[0][3] + output[i - 2][j + 2] * window[0][4] + \
                         output[i - 1][j - 2] * window[1][0] + output[i - 1][j - 1] * window[1][1] + output[i - 1][j] *
                         window[1][2] + output[i - 1][j + 1] * window[1][3] + output[i - 1][j + 2] * window[1][4] + \
                         output[i][j - 2] * window[2][0] + output[i][j - 1] * window[2][1] + output[i][j] * window[2][
                             2] + output[i][j + 1] * window[2][3] + output[i][j + 2] * window[2][4] + \
                         output[i + 1][j - 2] * window[3][0] + output[i + 1][j - 1] * window[3][1] + output[i + 1][j] *
                         window[3][2] + output[i + 1][j + 1] * window[3][3] + output[i + 1][j + 2] * window[3][4] + \
                         output[i + 2][j - 2] * window[4][0] + output[i + 2][j - 1] * window[4][1] + output[i + 2][j] *
                         window[4][2] + output[i + 2][j + 1] * window[4][3] + output[i + 2][j + 2] * window[4][4])
                output1[i - 2][j - 2] = value
    else:
        print("Invalid template size was given")
    return output1

def gaussianfilter(img : np.ndarray,sigma : float,kernel_size : int) -> np.ndarray:
    """
        Gaussian filter | 高斯滤波
        Args:
            img : np.ndarray # image to filter
            sigma : float # sigma of the Gaussian filter
            kernel_size : int # kernel size of the Gaussian filter
        Returns:
            np.ndarray # filtered image
        Examples:
            gaussianfilter(image,1.5,3)
    """
    h,w,c = img.shape
    # Zero padding | 零填充
    padding = kernel_size//2
    out = np.zeros((h + 2*padding,w + 2*padding,c),dtype=np.float)
    out[padding:padding+h,padding:padding+w] = img.copy().astype(np.float)
    # Define filter kernel | 定义滤波核
    kernel = np.zeros((kernel_size,kernel_size),dtype=np.float)
    
    for x in range(-padding,-padding+kernel_size):
        for y in range(-padding,-padding+kernel_size):
            kernel[y+padding,x+padding] = np.exp(-(x**2+y**2)/(2*(sigma**2)))
    kernel /= (sigma*np.sqrt(2*np.pi))
    kernel /= kernel.sum()
    
    # Convolution process | 卷积过程
    tmp = out.copy()
    for y in range(h):
        for x in range(w):
            for ci in range(c):
                out[padding+y,padding+x,ci] = np.sum(kernel*tmp[y:y+kernel_size,x:x+kernel_size,ci])
    
    return out[padding:padding+h,padding:padding+w].astype(np.uint8)