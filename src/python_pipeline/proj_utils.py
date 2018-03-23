# -*- coding: utf-8 -*-
import numpy as np
import os
import sys
sys.path.append('/Library/Frameworks/Python.framework/\
Versions/2.7/lib/python2.7/site-packages')
from sklearn.svm import LinearSVC
import matplotlib.pyplot as plt
from imageio import imread
from imageio import imwrite

def normalize_img(img):
    img = img.astype(float)
    img_norm= (img - img.min()) / (img.max() - img.min())
    return img_norm

def get_truncated_normal(mean, sd, low, upp):
    return truncnorm((low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)

'''
Matches the keypoints between 2 images
'''

def match_keypoints(descriptors0, descriptors1, thold_hamming):
    #print 'inside match_keypoints...'
    matches=np.zeros([1,2],dtype=int)
    count=0
    for i in range(0,descriptors0.shape[0]):
        desc0_tile=np.tile(descriptors0[i,:],(descriptors1.shape[0],1))
        xor_d0d1=np.bitwise_xor(desc0_tile.astype(int),descriptors1.astype(int))
        hamming_dist=np.sum(xor_d0d1,axis=1)
        if np.any(hamming_dist<64):
            if count==0:
                matches[0,0]=i
                matches[0,1]=np.argmin(hamming_dist)
                count +=1
            else:
                matches=np.append(matches,[[i,np.argmin(hamming_dist)]],axis=0)
    #print 'matches',matches
    return matches
    raise Exception('Not Implemented Error')

def refine_match(keypoints1, keypoints2, matches, reprojection_threshold = 10,
        num_iterations = 1000):
    count=0
    for i in range(0,1000):
        #pick 4 random matched pairs
        arr = np.arange(matches.shape[0])
        np.random.shuffle(arr)
        idx= arr[:4]
        #print idx
        #points 1 correspond to subset of keypoints 1
        #We take first 2 columns corresponding to u and v
        points1=keypoints1[matches[:,0],0:2]
        points2=keypoints2[matches[:,1],0:2]
        #points*_sel correspond to randomly picked keypoints
        points1_sel=keypoints1[matches[idx,0],0:2]
        points2_sel=keypoints2[matches[idx,1],0:2]
        H=homography(points1_sel,points2_sel)
        #Tile H for parallel vector operation
        H_tile=np.tile(H,(points1.shape[0],1,1))
        #print H
        #Make points1 homogenous
        #Reshape points1 for parallel vector operation
        points1_rs=np.column_stack((points1,np.ones((points1.shape[0],1))))
        points1_rs=np.reshape(points1_rs,(points1_rs.shape[0],points1_rs.shape[1],1))
        #Reshape points2 for parallel vector operation
        points2_rs=np.reshape(points2,(points2.shape[0],points2.shape[1],1))
        #Calculate points 2 using H
        points2_cal=np.matmul(H_tile,points1_rs)
        #Reshape the result to 2D array from 3D array
        points2_cal_rs2D=np.reshape(points2_cal,(points2_cal.shape[0],points2_cal.shape[1]))
        #Separate z column for back conversion to non-homogeneous cordinates
        z=points2_cal_rs2D[:,points2_cal_rs2D.shape[1]-1]
        z=np.reshape(z,(points2_cal_rs2D.shape[0],1))
        #Divide by z and drop the 3rd cordinate for non homogeneous conversion
        points2_cal_rs2D_nH=points2_cal_rs2D[:,0:points2_cal_rs2D.shape[1]-1]/z
        #Calculate erro
        error=np.linalg.norm(points2_cal_rs2D_nH-points2,axis=1)
        #print 'error',error
        inlier_count=(error < 10).sum()
        #print 'inlier count',inlier_count
        inliers=np.where(error<10)
        #print 'inliers',inliers
        if (count==0):
            max_inlier_count=inlier_count
            inliers_vector=inliers
            H_out=H
            count +=1
        elif inlier_count>max_inlier_count:
            max_inlier_count=inlier_count
            inliers_vector=inliers
            H_out=H
    #print 'max_inlier_count', max_inlier_count
    inliers_vector=np.reshape(inliers_vector,(max_inlier_count,))
    return inliers_vector, H_out
    raise Exception('Not Implemented Error')

def homography(points1, points2):
    #print points1.shape
    u2=points2[:,0:1]
    v2=points2[:,1:2]
    u1=points1[:,0:1]
    v1=points1[:,1:2]
    u1u2=np.multiply(u1,u2)
    u1v2=np.multiply(u1,v2)
    v1u2=np.multiply(v1,u2)
    v1v2=np.multiply(v1,v2)
    one=np.ones((u2.shape[0],1))
    zero=np.zeros((u2.shape[0],1))
    W1=np.column_stack((-u1,-v1,-one,zero,zero,zero,u1u2,v1u2,u2))
    W2=np.column_stack((zero,zero,zero,-u1,-v1,-one,u1v2,v1v2,v2))
    W=np.vstack((W1,W2))
    u,s,v_transpose=np.linalg.svd(W)
    H=np.reshape(v_transpose[8:9,:],(3,3))
    return H
    raise Exception('Not Implemented Error')

'''
Plots the matched keypoints between 2 images
'''
def plot_matches(im1, im2, keypoints1, keypoints2, matches):
    fig = plt.figure()
    im_new=np.zeros((max(im1.shape[0],im2.shape[0]),im1.shape[1]+im2.shape[1]))
    im_new[:im1.shape[0], :im1.shape[1]] = im1
    im_new[:im2.shape[0], im1.shape[1]:] = im2
    plt.gray()
    plt.imshow(im_new)
    plt.autoscale(False)
    for m in matches:
        ind1, ind2 = m
        plt.plot([keypoints1[ind1,1], im1.shape[1]+keypoints2[ind2,1]],\
                 [keypoints1[ind1,0], keypoints2[ind2,0]], '-x')
    plt.scatter(x=keypoints1[:,1],
                    y=keypoints1[:,0], c='r', s=20)
    plt.scatter(x=im1.shape[1]+keypoints2[:,1],
                    y=keypoints2[:,0], c='r', s=10)
    plt.show()

'''
PLOT_MATCHES: Given two images, plots the matching points between them

Arguments:
    im1 - The first image.

    im2 - The second image

    p1 - The keypoints of the first image.

    p2 - The keypoints of the second image

    matches - An int ndarray of size (N, 2) of indices that for keypoints in
        descriptors1 match which keypoints in descriptors2. For example, [7 5]
        would mean that the keypoint at index 7 of descriptors1 matches the
        keypoint at index 5 of descriptors2. Not every keypoint will necessarily
        have a match, so N is not the same as the number of rows in descriptors1
        or descriptors2.
Returns:
    Nothing; instead generates a figure in which it draws a line between the
        matching points of image 1 and image 2.
'''
