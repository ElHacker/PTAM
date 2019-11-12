# Framework for an Augmented Reality Application

This work was implemented as project for Stanford class [CS231A: Computer Vision, From 3D Reconstruction to Recognition](https://web.stanford.edu/class/cs231a/), taken in Winter 2018. In this work we attempt to implement a small scale real time detection,
mapping and tracking framework. We take real time video feed as input.
On the first frame we do keypoint detection and evaluate descriptors for
the keypoints. Using keypoint matching we track these points in the
subsequent frames. New points are added as they are detected in the
frame. Such tracking and mapping is useful for augmented reality
applications. We also show basic image augmentation with a virtual
object.

## Demo video

[Tracking and mapping keypoints across frames](https://youtu.be/tlSAWjjdVRA) 

[Augmented Video Demo](https://youtu.be/0qT57X_Es4A)

## Code File Structure

* src/java_src/ contains all the Android Java integration with the
  Camera 2 API.

Reads images from the camera on `ARCameraFragment.java` and then
passes it to an interface of `ARCameraImageProcessor` which is
implemented on Python with help of `Pyjnius`.

* src/main.py

Offers an implementation of `ARCameraImageProcessor` which receives
each frame and then transforms it into a Numpy array. This file also
takes care of the Android app single view lifecycle.

* src/python_pipeline/ Desktop processing and augmentation pipeline

Takes care of camera calibration, image keypoint detection and
matching, OpenGL rendering of the processed image as a background
texture, OBJ loading and rendering on the image.

Some relevant files:
- `ofast9.py`: keypoint detector using FAST
- `BRIEF.py`: BRIEF keypoint descriptor
- `proj_utils.py`: Miscellaneous utility functions
- `keypoint_tracking.py`: keypoint tracking across frames
- `ORB.py`: Running a complete  ORB pipeline
- `render_model.py`: Renders the augmentation pipeline

It supports live video from a web camera and do the full
processing there. To run it use command:
```
python render_model.py --obj CartoonRocket.obj
```

If you want to store it on 10 seconds video file append the --video option
flag

```
python render_model.py --obj CartoonRocket.obj --video
```
