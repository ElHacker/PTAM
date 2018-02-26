package org.cs231a.ptam;

public interface ARCameraImageProcessor {
    /**
     * Constructs the camera intrinsic transform matrix K.
     * Will receive intrinsic calibration parameters
     * [f_x, f_y, c_x, c_y, s]
     * f_x, f_y are the focal lengths in x and y axis.
     * c_x, c_y represent the coordinates of the center image point.
     * s represents skewness.
     *
     * API reference:
     * https://developer.android.com/reference/android/hardware/camera2/CameraCharacteristics.html#LENS_INTRINSIC_CALIBRATION
     * If API not supported by camera fallback to
     * constructIntrinsicCalibrationMatrixApproximation
     */
  void constructIntrinsicCalibrationMatrix(float[] intrinsicCalibrationParameters);


  /**
   * Contructs an approximation to the intrinsic calibration matrix K
   * This is the fallback to constructIntrinsicCalibrationMatrix in case that the
   * CameraCharacteristics.LENS_INTRINSIC_CALIBRATION is not supported by this
   * device's camera.
   *
   * Uses focal length f, image width, and image height.
   *
   * Assumes that f_x and f_y are equal. f_x == f_y
   * Assumes that c_x and c_y are exactly on the center of the image.
   * Assumes no distortion in camera.
   */
  void constructIntrinsicCalibrationMatrixApproximation(float focalLength, int width, int height);
}
