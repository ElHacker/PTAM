# Framework for an Augmented Reality Application

This work was implemented as project for Stanford class [CS231A: Computer Vision, From 3D Reconstruction to Recognition](https://web.stanford.edu/class/cs231a/), taken in Winter 2018. In this work we attempt to implement a small scale real time detection,
mapping and tracking framework. We take real time video feed as input.
On the first frame we do keypoint detection and evaluate descriptors for
the keypoints. Using keypoint matching we track these points in the
subsequent frames. New points are added as they are detected in the
frame. Such tracking and mapping is useful for augmented reality
applications. We also show basic image augmentation with a virtual
object. More details can be found in the [final project report](https://github.com/beeRitu/Parallel-Tracking-and-Mapping-PTAM/blob/master/Final_Report.pdf).

## Demo video

[Tracking and mapping keypoints across frames](https://youtu.be/tlSAWjjdVRA) 

[Augmented Video Demo](https://youtu.be/0qT57X_Es4A)

## Code File Structure

* src/python_pipeline/ Desktop processing and augmentation pipeline

Takes care of camera calibration, image keypoint detection and
matching, OpenGL rendering of the processed image as a background
texture, OBJ loading and rendering on the image.

* src/java_src/ contains all the Android Java integration with the
  Camera 2 API.

Reads images from the camera on `ARCameraFragment.java` and then
passes it to an interface of `ARCameraImageProcessor` which is
implemented on Python with help of `Pyjnius`.

* src/main.py

Offers an implementation of `ARCameraImageProcessor` which receives
each frame and then transforms it into a Numpy array. This file also
takes care of the Android app single view lifecycle.

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
## Python implementation of keypoint detection and matching

Some relevant files for feature extraction and key point detection are:
- `ofast9.py`: keypoint detector using FAST algorithm, further filtered using Harris corner detection. As ORB uses oriented FAST algorithm, an orientation is calculated corresponding to each keypoint.
- `BRIEF.py`: BRIEF keypoint descriptor
- `proj_utils.py`: Miscellaneous utility functions
- `keypoint_tracking.py`: keypoint tracking across frames
- `ORB.py`: Running a complete  ORB pipeline
- `render_model.py`: Renders the augmentation pipeline

`ORB.ipynb` ipython notebook can be used to follow the step by step output of the ORB keypoint feature detection and matching algorithm implementation. ORB stands for Oriented FAST and rotated BRIEF. Notebook reads the images stored in folder `./data` and generates 3 transformed corresponding images by applying normalization (1st image), rotation (2nd image), affine transformation followed by warping (3rd image). Original image and any of the three corresponding generated images are used for testing of for key point detection and matching. This notebook uses the following:
- Calls `FAST9` function implemented in `ofast9.py` for keypoint detection. FAST stands for (Features from Accelerated Segment Test) algorithm and is used for real time applications such as SLAM (Simultaneous Localization and Mapping). FAST keyppoint algorithm is very sensitive to edges and detects many keypoints along the edges in the image.
- Calls `HARRIS` function from `ofast9.py` to filter out keypoints detected using FAST algorithms to those having maximum corner like properties. 
- Calls `orientation` function from `ofast9.py` to calculate the orientation of keypoints 
- Calls `BRIEF` from `BRIEF.py` for keypoint feature descriptor.
- Uses hamming distance for descriptor matching

### Running the pipeline for keypoint detection and matching
* Download the following files in the run directory:
  - `ORB.ipynb`
  - `ofast9.py`
  - `BRIEF.py`
  - `proj_utils.py`
* Place the image for generating corresponding transformed image and creating keypoints with matching across the two under `./data`
* Add the image filenames in the list parsed by first for loop under the `if __name__ == '__main__':`. The current code uses 1 filename in the list as `['astronaut']`
* Run ORB.ipynb 


