# -*- coding: utf-8 -*-
import numpy as np
import random
import os
import sys
sys.path.append('/Library/Frameworks/Python.framework/\
Versions/2.7/lib/python2.7/site-packages')
from skimage import transform as tf
from sklearn.svm import LinearSVC
import matplotlib.pyplot as plt
import scipy.ndimage
from scipy.stats import truncnorm
from imageio import imread
from imageio import imwrite
from ofast9 import *
from proj_utils import *


'''
BRIEF Given an image, detects keypoints

Arguments:
    im- image

    kernel-Gaussian smoothing kernal for the image

    l-feature length for BRIEF

    S-Window size for BRIEF is SxS

    keypoints - array of Nx2. N rows, each corresponding to a keypoint.
    2 columns representing (x,y)

Returns:
    descriptors - N x l array of descriptors. N (rows) is the number of
    keypoints. l (cloumns) is the length of each feature.

BRIEF feature detector is implemented as follows:

1. Implemented on smoothed image.
2. Choose kernels used to smooth the patches before intensity differencing.
Default use gaussian kernel of 2 with patch size of 9x9.
3. Choose the spatial arrangement of the (x, y)-pairs.

BRIEF provides a shortcut to find the binary strings directly without
finding descriptors.It takes smoothened image patch and selects a set of
n_d (x,y) location pairs in an unique way (explained in paper).
Then some pixel intensity comparisons are done on these location pairs.
For eg, let first location pairs be p and q. If I(p) < I(q), then its
result is 1, else it is 0. This is applied for all the n_d location pairs
to get a n_d-dimensional bitstring. This n_d can be 128, 256 or 512.
By default, it would be 256 (OpenCV represents it in bytes.So the values
will be 16, 32 and 64). So once you get this, you can use Hamming Distance
to match these descriptors.

One important point is that BRIEF is a feature descriptor, it doesn’t provide
any method to find the features. So you will have to use any other feature
detectors like SIFT, SURF etc. The paper recommends to use CenSurE which is
a fast detector and BRIEF works even slightly better for CenSurE points than
for SURF points.

In short, BRIEF is a faster method feature descriptor calculation and matching.
It also provides high recognition rate unless there is large in-plane rotation.

https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_feature2d/py_brief/
py_brief.html#brief
'''

def BRIEF(im,keypoints,kernel,l,S):
    #Smoothen the image using gaussian filter
    im_smooth=scipy.ndimage.filters.gaussian_filter(im, kernel)
    #Assign zeros to descriptor array
    descriptors=np.zeros((keypoints.shape[0],l))
    #We loop over each keypoint to find BRIEF descriptor for the same
    for i in range(0,keypoints.shape[0]):
        #print 'i am here'
        #print 'i',i
        #choose l(=256 default) pairs of pixel locations
        #We define 2 groups n1 and n2 and make corresponding coordinates
        #from each group a pair.
        n1=np.empty((l,2))
        n2=np.empty((l,2))
        #Finding row for 1st set of points
        #Choose random numbers with mean around keypoint row, SD=S/5 as
        #used in the BRIEF paper and we restrict the random number selection
        #to be within the image row numbers
        n=get_truncated_normal(keypoints[i,0],S/5,0,im.shape[0])
        n1[:,0]=n.rvs(l,random_state=5)
        n=get_truncated_normal(keypoints[i,1],S/5,0,im.shape[1])
        #Similarly we pick columns
        n1[:,1]=n.rvs(l,random_state=10)
        n=get_truncated_normal(keypoints[i,0],S/5,0,im.shape[0])
        #Choose second set of points in the same manner as set 1
        n2[:,0]=n.rvs(l,random_state=15)
        n=get_truncated_normal(keypoints[i,1],S/5,0,im.shape[1])
        n2[:,1]=n.rvs(l,random_state=20)
        n1=n1.astype(np.int16)
        n2=n2.astype(np.int16)
        #print 'n1',n1
        #print 'n2',n2
        #We choose pixel intensity value corresponding to each location
        I_n1=im[n1[:,0],n1[:,1]]
        I_n2=im[n2[:,0],n2[:,1]]
        #Calculate BRIEF feature
        descriptors[i,np.where(I_n1>I_n2)[0]]=1
        #print 'BRIEF descriptor',descriptors[i,:]
        #find the BRIEF feature
    return descriptors
    raise Exception('Not Implemented Error')

def get_truncated_normal(mean, sd, low, upp):
    return truncnorm((low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)
