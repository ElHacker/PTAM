from kivy.uix.image import Image
from jnius import autoclass

ARCameraFragment = autoclass('org.cs231a.ptam.ARCameraFragment')

__all__ = ('ARCamera', )


class ARCamera(Image):

    def __init__(self, **kwargs):
        super(ARCamera, self).__init__(**kwargs)
        self.camera = ARCameraFragment.newInstance()
        size = self.camera.getPreviewSize()
        self.texture = Texture(width=size.getWidth(), height=size.getHeight(),
                                       target=GL_TEXTURE_EXTERNAL_OES,
                                       colorfmt='rgba')
        self.texture_size = list(self.texture.size)

