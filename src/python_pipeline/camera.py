import cv2

# Whole point of this script is to output:

# image_no keypoint_no pixel_x pixel_y

feature_detector = cv2.ORB_create()
matcher = cv2.BFMatcher_create(cv2.NORM_HAMMING, crossCheck=True)

#replace web address with video source of your choice, see VideoCapture docs
cap = cv2.VideoCapture('http://10.200.1.58:8080/video')

if cap.isOpened():
    ret, old_frame = cap.read()
    old_frame = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
    old_keypoints, old_descriptors = feature_detector.detectAndCompute(old_frame, None)

    keypoint_counter = len(old_keypoints)
    current_matches = dict((i,i) for i in xrange(len(old_keypoints)))

    image_number = 0
else:
    print "capture didn't open - check the network and the IP address"

while(cap.isOpened()):
    ret, new_frame = cap.read()
    new_frame = cv2.cvtColor(new_frame, cv2.COLOR_BGR2GRAY)
    new_keypoints, new_descriptors = feature_detector.detectAndCompute(new_frame, None)

    if new_descriptors is not None and old_descriptors is not None:
        matches = matcher.match(new_descriptors, old_descriptors)
    else:
        matches = []

    #each match produces:
    #queryIdx - index of keypoint in new_keypoints
    #trainIdx - index of keypoint in old_keypoints

    #two possibilities for each match

    # (1) the match is new

        # meaning: we haven't tracked that keypoint before

    # (2) the match is a continuation

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

    for current_index, keypoint_no in current_matches.iteritems():
        keypoint = new_keypoints[current_index]
        print image_number, keypoint_no, keypoint.pt[0], keypoint.pt[1]

    image_number += 1

cap.release()
