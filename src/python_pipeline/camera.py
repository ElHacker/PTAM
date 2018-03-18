import cv2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import argparse
from moviepy.editor import VideoFileClip

feature_detector = cv2.ORB_create()
matcher = cv2.BFMatcher_create(cv2.NORM_HAMMING, crossCheck=True)
isInitialized = False
current_matches = None
image_number = 0
keypoint_counter = 0

def initProcessImage(image):
    global isInitialized
    global old_descriptors
    global old_keypoints
    global current_matches
    global keypoint_counter

    old_frame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    old_keypoints, old_descriptors = feature_detector.detectAndCompute(old_frame, None)

    keypoint_counter = len(old_keypoints)
    current_matches = dict((i,i) for i in xrange(len(old_keypoints)))

    isInitialized = True
    print(isInitialized)


def processImage(image, plot=False):
    global old_descriptors
    global old_keypoints
    global current_matches
    global image_number
    global keypoint_counter

    if not isInitialized:
        initProcessImage(image)
        return image
    new_frame = image
    new_frame = cv2.cvtColor(new_frame, cv2.COLOR_BGR2GRAY)
    new_keypoints, new_descriptors = feature_detector.detectAndCompute(new_frame, None)

    if new_descriptors is not None and old_descriptors is not None:
        matches = matcher.match(new_descriptors, old_descriptors)
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

    current_matches = next_matches
    old_keypoints, old_descriptors = new_keypoints, new_descriptors


    image_number += 1
    image_frame = drawFeaturePoints(image, current_matches, new_keypoints)

    if plot:
        plt.imshow(image_frame)
        plt.show()

    return image_frame

def drawFeaturePoints(image, matches, keypoints):
    for current_index, keypoint_no in matches.iteritems():
        keypoint = keypoints[current_index]
        cv2.circle(image, (int(keypoint.pt[0]), int(keypoint.pt[1])), 10, (255, 0, 0), 3)
    print("Image Size")
    print(image.shape)
    return image

def defineFlags():
    parser = argparse.ArgumentParser(description='Feature ketpoint finder')
    parser.add_argument('--video', action='store_true')
    return parser.parse_args()

def main():
    args = defineFlags()
    if args.video:
        clip = VideoFileClip('videos/water.mp4')
        print(clip.size)
        output_video = 'project_video_output.mp4'
        # NOTE: this function expects color images!
        output_clip = clip.fl_image(processImage)
        output_clip.write_videofile(output_video, audio=False)
    else:
        image1 = mpimg.imread('test_images/water1.jpg')
        image2 = mpimg.imread('test_images/water2.jpg')
        processImage(image1, plot=True)
        print(isInitialized)
        processImage(image2, plot=True)
        print(isInitialized)

main()
