# Basic OBJ file viewer. needs objloader from:
#  http://www.pygame.org/wiki/OBJFileLoader
# LMB + move: rotate
# RMB + move: pan
# Scroll wheel: zoom in/out
import sys, pygame
from pygame.locals import *
from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
import matplotlib.image as mpimg
import cv2

# import pywavefront

# IMPORT OBJECT LOADER
from objloader import *

pygame.init()
viewport = (800, 600)
hx = viewport[0]/2
hy = viewport[1]/2
srf = pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF)

glLightfv(GL_LIGHT0, GL_POSITION,  (-40, 200, 100, 0.0))
glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
glEnable(GL_LIGHT0)
glEnable(GL_LIGHTING)
# Most .obj files expect to be smooth-shaded
glShadeModel(GL_SMOOTH)
glClearDepth(1.0)
glDepthFunc(GL_LESS)

# LOAD OBJECT AFTER PYGAME INIT
obj = OBJ(sys.argv[1], swapyz=True)

clock = pygame.time.Clock()

width, height = viewport
glMatrixMode(GL_MODELVIEW)

def render_background(image):
    # Convert imge to OpenGL texture format
    bg_image = cv2.flip(image, 0)
    bg_image = Image.fromarray(bg_image)
    ix = bg_image.size[0]
    iy = bg_image.size[1]
    bg_image = bg_image.tobytes('raw', 'RGBX', 0, -1)

    # Use orthographic projection for background image.
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glOrtho(0.0, width, height, 0.0, 0.0, 1.0)

    # Create background texture
    # Assign texture
    texture_background = glGenTextures(1)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_background)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, bg_image)

    # Draw background
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0); glVertex2d(0.0, 0.0)
    glTexCoord2f(1.0, 0.0); glVertex2d(width, 0.0)
    glTexCoord2f(1.0, 1.0); glVertex2d(width, height)
    glTexCoord2f(0.0, 1.0); glVertex2d(0.0, height)
    glEnd()
    glDisable(GL_TEXTURE_2D)

def render_model():
    glColorMaterial(GL_FRONT, GL_SPECULAR)
    glEnable(GL_COLOR_MATERIAL)
    glColor3f(1.0, 0.0, 0.0)
    glTranslate(tx / 20.0, ty / 20.0, -zpos)
    glRotate(ry, 1, 0, 0)
    glRotate(rx, 0, 1, 0)
    glCallList(obj.gl_list)
    glDisable(GL_COLOR_MATERIAL)

def display(image):
    glLoadIdentity()

    # Background render
    render_background(image)

    # Foreground render
    # Re-enable depth writes and testing
    glEnable(GL_DEPTH_TEST)
    glDepthMask(GL_TRUE)

    glLoadIdentity()
    glMatrixMode(GL_PROJECTION)

    gluPerspective(90, width / float(height), 1.0, 100.0)
    # glEnable(GL_BLEND)
    # glBlendFunc(GL_SRC_ALPHA, GL_DST_ALPHA)
    # glEnable(GL_COLOR_LOGIC_OP)
    # glLogicOp(GL_EQUIV)
    glEnable(GL_DEBUG_OUTPUT)
    render_model()

    pygame.display.flip()


rx, ry = (0,0)
tx, ty = (0,0)
zpos = 5
rotate = move = False
image1 = mpimg.imread('test_images/water1.jpg')

cap = cv2.VideoCapture(0)
while 1:
    clock.tick(30)
    for e in pygame.event.get():
        if e.type == QUIT:
            sys.exit()
        elif e.type == KEYDOWN and e.key == K_ESCAPE:
            sys.exit()
        elif e.type == MOUSEBUTTONDOWN:
            if e.button == 4: zpos = max(1, zpos-1)
            elif e.button == 5: zpos += 1
            elif e.button == 1: rotate = True
            elif e.button == 3: move = True
        elif e.type == MOUSEBUTTONUP:
            if e.button == 1: rotate = False
            elif e.button == 3: move = False
        elif e.type == MOUSEMOTION:
            i, j = e.rel
            if rotate:
                rx += i
                ry += j
            if move:
                tx += i
                ty -= j

    # Capture frame-by-frame
    ret, frame = cap.read()

    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

    # RENDER OBJECT
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    display(frame)
