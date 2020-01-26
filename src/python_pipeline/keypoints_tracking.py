'''
This script shows the comparison between cv2 ORB keypoint feature_detector
and matching compared to our custom implementation.
All variables named starting with my_* are used to excecute our custom
implementation. Usually these correspond to the variable with same name
without prefix 'my_' which track the implementation using cv2 library.
'''
import cv2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import argparse
from moviepy.editor import VideoFileClip
from proj_utils import *
# import our implementation of FAST keypoint detector
# import our implementation of BRIEF keypoint descriptor
from ofast9 import *
from BRIEF import *

feature_detector = cv2.ORB_create()
matcher = cv2.BFMatcher_create(cv2.NORM_HAMMING, crossCheck=True)
# isInitialized: is used to assign variables for the first frame.
# *current_matches: dictionary of matching keypoints between the
# query frame and reference frame.
# image_number: counts the number of frames
# *keypoint_counter: keeps a count of total number of keypoints detected.
# This includes matching and unmatched points.
isInitialized = False
current_matches = None
my_currentMatches=None
image_number = 0
keypoint_counter = 0
my_keypointCounter=0

# *old_descriptors: Is the descriptors from the reference frame
# *old_keypoints: Are the keypoints from the reference frame
# my_oldKeypoints_wHarris: Are the keypoints from our custom implementation
# obtained by FAST keypoint detector followed by harris corner filtering.
# old_frame: is the reference frame
# initProcessImage() takes the first frame and assigns it as the reference
# frame (old_frame). Keypoints (old_keypoints) and descriptor (old_descriptors)
# are computed. At the first frame, the total number of keypoints
# (keypoint_counter) is the keypoints detected in the frame. Similarly each
# point is its own matching in (current_matches).
def initProcessImage(image):
    global isInitialized
    global old_descriptors
    global my_oldDescriptors
    global old_keypoints
    global my_oldKeypoints_wHarris
    global current_matches
    global my_currentMatches
    global keypoint_counter
    global my_keypointCounter

    old_frame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    old_keypoints, old_descriptors = feature_detector.detectAndCompute(old_frame, None)
    my_oldKeypoints=FAST9(old_frame, threshold=40, n=9)

    old_harrisMeasures=HARRIS(old_frame,my_oldKeypoints,k=0.04,offset=3)
    my_oldKeypoints_wHarris=np.column_stack((my_oldKeypoints,\
                                                old_harrisMeasures))
    my_oldKeypoints_wHarris=my_oldKeypoints_wHarris[\
                        my_oldKeypoints_wHarris[:,2].argsort()[::-1]]
    my_oldKeypoints_wHarris=my_oldKeypoints_wHarris[0:80,:]
    my_oldDescriptors=BRIEF(old_frame,my_oldKeypoints_wHarris,kernel=2,l=256,S=31)
    keypoint_counter = len(old_keypoints)
    my_keypointCounter=my_oldKeypoints_wHarris.shape[0]
    current_matches = dict((i,i) for i in xrange(len(old_keypoints)))
    my_currentMatches=dict((i,i) for i in xrange(my_oldKeypoints_wHarris.shape[0]))

    isInitialized = True
    print 'Initializing frame 1'

    print 'my_keypointCounter',my_keypointCounter
    print 'my_currentMatches',my_currentMatches
    print 'my_oldKeypoints_wHarris',my_oldKeypoints_wHarris
    '''
    plt.gray()
    implot = plt.imshow(old_frame)
    plt.scatter(x=my_oldKeypoints[0:,1],
                    y=my_oldKeypoints[0:,0], c='g', s=10)
    plt.scatter(x=my_oldKeypoints_wHarris[0:,1],
                    y=my_oldKeypoints_wHarris[0:,0], c='r', s=10)
    plt.show()
    '''
    #print(isInitialized)
'''
processImage() takes a frame from the video as input. First itchecks if
the image is initialized or not.
If not initialized, initProcessImage() is called to initialize the image.
Initialized image is returned.
new_frame is the query frame. Keypoints and descriptors are evaluated on
the query frame.
Matching is performed between the reference frame and the query frame.
'''
def processImage(image, plot=False):
    global old_descriptors
    global my_oldDescriptors
    global old_keypoints
    global my_oldKeypoints_wHarris
    global current_matches
    global my_currentMatches
    global image_number
    global keypoint_counter
    global my_keypointCounter

    print 'image number',image_number
    if not isInitialized:
        initProcessImage(image)
        return image
    new_frame = image
    new_frame = cv2.cvtColor(new_frame, cv2.COLOR_BGR2GRAY)
    new_keypoints, new_descriptors = feature_detector.detectAndCompute(new_frame, None)
    my_newKeypoints=FAST9(new_frame, threshold=40, n=9)

    new_harrisMeasures=HARRIS(new_frame,my_newKeypoints,k=0.04,offset=3)
    my_newKeypoints_wHarris=np.column_stack((my_newKeypoints,\
                                                new_harrisMeasures))
    my_newKeypoints_wHarris=my_newKeypoints_wHarris[\
                        my_newKeypoints_wHarris[:,2].argsort()[::-1]]
    my_newKeypoints_wHarris=my_newKeypoints_wHarris[0:80,:]
    my_newDescriptors=BRIEF(new_frame,my_newKeypoints_wHarris,kernel=2,l=256,S=31)
    print 'old keypoints',my_oldKeypoints_wHarris[0:5,:]
    print 'new keypoints',my_newKeypoints_wHarris[0:5,:]
    '''
    plt.gray()
    implot = plt.imshow(new_frame)
    plt.scatter(x=my_newKeypoints[0:,1],
                    y=my_newKeypoints[0:,0], c='g', s=10)
    plt.scatter(x=my_newKeypoints_wHarris[0:,1],
                    y=my_newKeypoints_wHarris[0:,0], c='r', s=10)
    plt.show()
    '''
    if new_descriptors is not None and old_descriptors is not None:
        matches = matcher.match(new_descriptors, old_descriptors)
        my_matches=match_keypoints(my_oldDescriptors, my_newDescriptors,\
                                                            thold_hamming = 64)
        #print 'my_matches',my_matches
        inliers, model = refine_match(my_oldKeypoints_wHarris,\
                                        my_newKeypoints_wHarris,\
                                         my_matches)
        my_matches=my_matches[inliers,:]
        print 'my_matches',my_matches

    else:
        matches = []

    # Each match produces:
    # queryIdx - index of keypoint in new_keypoints
    # trainIdx - index of keypoint in old_keypoints

    # Two possibilities for each match

    # (1) The match is new

        # Meaning: we haven't tracked that keypoint before

    # (2) The match is a continuation

        # meaning: we've tracked that keypoint before

    next_matches = {}
    my_nextMatches= {}

    for match in matches:
        if match.trainIdx in current_matches:
            keypoint_no = current_matches[match.trainIdx]
            current_index = match.queryIdx
            next_matches[current_index] = keypoint_no
        else:
            keypoint_no = keypoint_counter
            keypoint_counter += 1
            current_index = match.queryIdx
            next_matches[current_index] = keypoint_no

    for k in range(0,my_matches.shape[0]):
        if my_matches[k,0] in my_currentMatches:
            #print 'my_matches[k,0]',my_matches[k,0]
            my_keypointNo = my_currentMatches[my_matches[k,0]]
            #print 'my_keypointNo',my_keypointNo
            my_currentIndex = my_matches[k,1]
            #print 'my_currentIndex',my_currentIndex
            my_nextMatches[my_currentIndex] = my_keypointNo
            #print 'my_nextMatches[my_currentIndex]',my_nextMatches[my_currentIndex]
        else:
            my_keypointNo = my_keypointCounter
            my_keypointCounter += 1
            my_currentIndex = my_matches[k,1]
            my_nextMatches[my_currentIndex] = my_keypointNo

    current_matches = next_matches
    old_keypoints, old_descriptors = new_keypoints, new_descriptors
    my_currentMatches = my_nextMatches
    my_oldKeypoints_wHarris, my_oldDescriptors = my_newKeypoints_wHarris,\
                                                            my_newDescriptors

    image_number += 1
    #print 'image_number',image_number
    image_frame = drawFeaturePoints(image, current_matches, new_keypoints)
    image_frame = my_drawFeaturePoints(image_frame, my_matches,\
                                                my_newKeypoints_wHarris)
    if image_number==1:
        imwrite('frame1.jpg', image_frame)
    if image_number==100:
        imwrite('frame100.jpg', image_frame)
    if image_number==200:
        imwrite('frame200.jpg', image_frame)
    if image_number==300:
        imwrite('frame300.jpg', image_frame)

    #print 'my current_matches',my_currentMatches
    #print 'my_currentIndex',my_currentIndex
    #image_frame = my_drawFeaturePoints(image_frame, my_currentMatches,\
    #                                            my_newKeypoints_wHarris)

    if plot:
        plt.imshow(image_frame)
        plt.show()

    return image_frame

def drawFeaturePoints(image, matches, keypoints):
    for current_index, keypoint_no in matches.iteritems():
        keypoint = keypoints[current_index]
        cv2.circle(image, (int(keypoint.pt[0]), int(keypoint.pt[1])), 5, (255, 0, 0), 3)
    #print("Image Size")
    #print(image.shape)
    return image

def my_drawFeaturePoints(image, matches, keypoints):
    for j in range(0,matches.shape[0]):
        #keypoint = keypoints[current_index]
        cv2.circle(image, (int(keypoints[matches[j,1],1]),\
                            int(keypoints[matches[j,1],0])),\
                             5, (0, 255, 255), 3)
    return image

def defineFlags():
    parser = argparse.ArgumentParser(description='Feature ketpoint finder')
    parser.add_argument('--video', action='store_true')
    return parser.parse_args()

def main():
    args = defineFlags()
    if args.video:
        clip = VideoFileClip('Desk_comp.mp4')
        print(clip.size)
        output_video = 'project_video_output.mp4'
        # NOTE: this function expects color images!
        output_clip = clip.fl_image(processImage)
        output_clip.write_videofile(output_video, audio=False)
    else:
        image1 = mpimg.imread('im-gray.jpg')
        image2 = mpimg.imread('im-gray2.jpg')
        processImage(image1, plot=True)
        print(isInitialized)
        processImage(image2, plot=True)
        print(isInitialized)

main()
