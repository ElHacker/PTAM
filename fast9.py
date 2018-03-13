%matplotlib inline
import numpy as np
import os
import sys
sys.path.append('/Library/Frameworks/Python.framework/\
Versions/2.7/lib/python2.7/site-packages')
from sklearn.svm import LinearSVC
import matplotlib.pyplot as plt
from imageio import imread
from imageio import imwrite

'''
FAST Given an image, detects keypoints

Arguments:
    im - the image matrix

    threshold - Threshold used to decide whether the pixels on the 
    circle are brighter, darker or similar w.r.t. the test pixel. 
    Decrease the threshold when more corners are desired and 
    vice-versa.

    n - Minimum number of consecutive pixels out of 16 pixels on the 
    circle that should all be either brighter or darker w.r.t 
    test-pixel. A point c on the circle is darker w.r.t test pixel p 
    if ``Ic < Ip - threshold`` and brighter if 
    ``Ic > Ip + threshold``.Also stands for the n in ``FAST-n`` corner
    detector.


Returns:
    keypoints - N x 2 array of keypoint locations (row,col). 
    Where N is equal to the number of key points.

FAST-9 feature detector is implemented as follows:

1. Select a pixel p in the image which is to be identified as an 
interest point or not. Let its intensity be I_p.
2. Select appropriate threshold value t.
3. Consider a circle of 16 pixels around the pixel under test.
4. Now the pixel p is a corner if there exists a set of n contiguous 
pixels in the circle (of 16 pixels) which are all brighter than 
I_p + t,or all darker than I_p − t. We chose n=9 for FAST-9.
5. A high-speed test was proposed to exclude a large number of 
non-corners. This test examines only the four pixels at 1, 9, 5 and 13
(First 1 and 9 are tested if they are too brighter or darker. If so, 
then checks 5 and 13). If p is a corner, then at least three of these 
must all be brighter than I_p + t or darker than I_p − t. 
If neither of these is the case, then p cannot be a corner. 
6. The full segment test criterion can then be applied to the passed 
candidates by examining all pixels in the circle. 

This detector in itself exhibits high performance, but there are 
several weaknesses:
a) It does not reject as many candidates for n < 12.
b) The choice of pixels is not optimal because its efficiency depends 
on ordering of the questions and distribution of corner appearances.
c) Results of high-speed tests are thrown away.
Multiple features are detected adjacent to one another.

Reference: https://docs.opencv.org/3.0-beta/doc/py_tutorials/ \
py_feature2d/py_fast/py_fast.html
'''
def FAST9(im, threshold, n):
    #can this be done without writing the image?
    #drop 3 rows and 3 columns at the edges 
    #start scanning and checking for corner at each pixel
    count=0
    #initialize the keypoint array
    keypoints=np.zeros((1,2))
    for i in range(3,im.shape[0]-3):
        for j in range(3,im.shape[1]-3):
            #print '[i,j]',i,j
            Imin=im[i,j]-threshold
            Imax=im[i,j]+threshold
            #Test 1 and 9 first
            p1=im[i-3,j]
            #print 'p1',p1
            p9=im[i+3,j]
            if ((p1>Imax) or (p1<Imin)) and ((p9>Imax) or (p9<Imin)):
                    p5=im[i,j+3]
                    p13=im[i,j-3]
                    if ((p5>Imax) or (p5<Imin)) and \
                        ((p13>Imax) or (p13<Imin)):
                            p2=im[i-3,j+1]
                            p3=im[i-2,j+2]
                            p4=im[i-1,j+3]
                            p6=im[i+1,j+3]
                            p7=im[i+2,j+2]
                            p8=im[i+3,j+1]
                            p10=im[i+3,j-1]
                            p11=im[i+2,j-2]
                            p12=im[i+1,j-3]
                            p14=im[i-1,j-3]
                            p15=im[i-2,j-2]
                            p16=im[i-3,j-1]
                            I_grp=np.array([p2,p3,p4,p6,p7,p8,p10,
                                           p11,p12,p14,p15,p16])
                            idx=np.where((I_grp>Imax) | (I_grp<Imin)) 
                            #4 points already >Imax or <Imin
                            #need to have 5 more for 9 pixels
                            if (idx[0].shape[0]>=5):
                                #print 'keypoint',i,j
                                if (count==0):
                                    keypoints=np.array([[i,j]])
                                else:
                                    keypoints=np.row_stack(\
                                        (keypoints,np.array([[i,j]])))
                                count +=1
                    
    #print 'count',count
    #print 'keypoints',keypoints
    return keypoints
    raise Exception('Not Implemented Error')

def normalize_img(img):
    img = img.astype(float)
    img_norm= (img - img.min()) / (img.max() - img.min())
    return img_norm
