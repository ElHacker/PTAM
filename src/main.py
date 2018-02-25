# kivy
import kivy
kivy.require('1.0.9')
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from ui_camera.camera import Camera
from kivy.app import App
from kivy.clock import Clock
from jnius import autoclass, java_method, cast, PythonJavaClass

# kivy3
from kivy3 import Renderer, Scene
from kivy3 import PerspectiveCamera

# geometry
from kivy3.extras.geometries import BoxGeometry
from kivy3 import Material, Mesh

print("WTF")
PythonActivity = autoclass('org.kivy.android.PythonActivity')
LinearLayout = autoclass('android.widget.LinearLayout')
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

class TestCamera(App):

    def on_start(self):
        currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
        fragmentManager = currentActivity.getFragmentManager()
        fragmentTransaction = fragmentManager.beginTransaction()
        linearLayoutId = 12345
        linearLayout = LinearLayout(currentActivity.getContext())
        linearLayout.setOrientation(LinearLayout.HORIZONTAL)
        linearLayout.setId(linearLayoutId)
        cameraFragment = ARCameraFragment.newInstance()
        fragmentTransaction.add(linearLayoutId, cameraFragment, 'ARCameraFragment')
        fragmentTransaction.commit()
        currentActivity.setContentView(linearLayout)


    def build(self):
        processor = PythonMessageProcessor()
        hello = HelloWorld()
        hello.sayHello(processor)
        # return Camera(resolution=(1280, 960), play=True)
        layout = FloatLayout()
        return layout

class ARCameraWidget(Widget):


if __name__ == '__main__':
    # My3D().run()
    TestCamera().run()
