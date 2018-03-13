# kivy
import kivy
kivy.require('1.0.9')
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from jnius import autoclass, java_method, cast, PythonJavaClass
from android.runnable import run_on_ui_thread

# kivy3
from kivy3 import Renderer, Scene
from kivy3 import PerspectiveCamera

# geometry
from kivy3.extras.geometries import BoxGeometry
from kivy3 import Material, Mesh

# numpy
import numpy as np


PythonActivity = autoclass('org.kivy.android.PythonActivity')
LinearLayout = autoclass('android.widget.LinearLayout')
AugmentationLinearLayout = autoclass('org.cs231a.ptam.AugmentationLinearLayout')
ARCameraFragment = autoclass('org.cs231a.ptam.ARCameraFragment')
HelloWorld = autoclass('org.cs231a.ptam.HelloWorld')

# Renders a simple cube.
class My3D(App):

    def _adjust_aspect(self, *args):
        rsize = self.renderer.size
        aspect = rsize[0] / float(rsize[1])
        self.renderer.camera.aspect = aspect

    def rotate_cube(self, *dt):
        self.cube.rotation.y  += 1

    def build(self):
        layout = FloatLayout()

        # Create renderer.
        self.renderer = Renderer()

        # Create scene.
        scene = Scene()

        # Create default cube for scene.
        cube_geo = BoxGeometry(1, 1, 1)
        cube_mat = Material()
        self.cube = Mesh(
                geometry=cube_geo,
                material=cube_mat
        )
        self.cube.pos.z = -5

        # Create camera for scene.
        self.camera = PerspectiveCamera(
                fov=75, # distance from the screen
                aspect=0, # "screen" ratio
                near=1, #nearest rendered point
                far=10 # farthest rendered point
        )

        # Start rendering the scene and camera.
        scene.add(self.cube)
        self.renderer.render(scene, self.camera)

        # Set renderer ratio if its size changes.
        # e.g. when added to parent
        self.renderer.bind(size=self._adjust_aspect)

        layout.add_widget(self.renderer)
        Clock.schedule_interval(self.rotate_cube, 0.01)
        return layout

class PythonMessageProcessor(PythonJavaClass):
    __javainterfaces__ = ('org.cs231a.ptam.HelloWorld$MessageProcessor', )
    __javacontext__ = 'app'

    def __init__(self):
        super(PythonMessageProcessor, self).__init__()

    @java_method('(Ljava/lang/String;)Ljava/lang/String;')
    def processMessage(self, message):
        return message + " Python"

class PythonARCameraImageProcessor(PythonJavaClass):
    __javainterfaces__ = ('org.cs231a.ptam.ARCameraImageProcessor', )
    __javacontext__ = 'app'

    def __init_(self):
        super(PythonARCameraImageProcessor, self).__init__()

    @java_method('([F)V')
    def constructIntrinsicCalibrationMatrix(self, intrinsicCalibrationParameters):
        f_x = 0
        f_y = 1
        c_x = 2
        c_y = 3
        s = 4
        c_params = intrinsicCalibrationParameters
        if c_params is None:
            # If the intrinsic calibration parameters are null it means that the
            # camera doesn't have support for that API.
            Logger.info("Camera doesn't support native Internal Calibration Parameters")
            return
        K = np.array([
            [c_params[f_x], c_params[s], c_params[c_x]],
            [0, c_params[f_y], c_params[c_y]],
            [0, 0, 1]
        ])
        Logger.info("The Internal Calibration Matrix:")
        Logger.info(K)

    @java_method('(FII)V')
    def constructIntrinsicCalibrationMatrixApproximation(self, focalLength, image_width, image_height):
        c_x = image_width / 2
        c_y = image_height / 2
        f_x = f_y = focalLength
        K = np.array([
            [f_x, 0, c_x],
            [0, f_y, c_y],
            [0, 0, 1]
        ])
        Logger.info("The approximated Internal Calibration Matrix:")
        Logger.info(K)

class TestCamera(App):

    def on_start(self):
        Clock.schedule_once(self.create_view, 0)

    @run_on_ui_thread
    def create_view(self, *args):
        currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
        fragmentManager = currentActivity.getFragmentManager()
        fragmentTransaction = fragmentManager.beginTransaction()
        linearLayoutId = 12345
        linearLayout = AugmentationLinearLayout(currentActivity.getApplicationContext())
        linearLayout.setOrientation(LinearLayout.HORIZONTAL)
        linearLayout.setId(linearLayoutId)
        # Pass in the camera image processor to the camera fragment.
        imageProcessor = PythonARCameraImageProcessor()
        self.cameraFragment = ARCameraFragment.newInstance(imageProcessor)
        fragmentTransaction.add(linearLayoutId, self.cameraFragment, 'ARCameraFragment')
        fragmentTransaction.commit()
        currentActivity.setContentView(linearLayout)

    def build(self):
        processor = PythonMessageProcessor()
        hello = HelloWorld()
        hello.sayHello(processor)
        layout = FloatLayout()
        return layout


if __name__ == '__main__':
    # My3D().run()
    TestCamera().run()
