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
glEnable(GL_COLOR_MATERIAL)
glShadeModel(GL_SMOOTH)           # most obj files expect to be smooth-shaded
glClearColor(0.0, 0.0, 0.0, 0.0)
glClearDepth(1.0)
glDepthFunc(GL_LESS)
# Assign texture
glEnable(GL_TEXTURE_2D)
texture_background = glGenTextures(1)

# LOAD OBJECT AFTER PYGAME INIT
obj = OBJ(sys.argv[1], swapyz=True)

clock = pygame.time.Clock()

glMatrixMode(GL_PROJECTION)
glLoadIdentity()
width, height = viewport
gluPerspective(90.0, width/float(height), 1, 100.0)
glEnable(GL_DEPTH_TEST)
glMatrixMode(GL_MODELVIEW)


def render_background(image):
    # Convert imge to OpenGL texture format
    bg_image = cv2.flip(image, 0)
    bg_image = Image.fromarray(bg_image)
    ix = bg_image.size[0]
    iy = bg_image.size[1]
    bg_image = bg_image.tobytes('raw', 'RGBX', 0, -1)

    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 800.0, 600.0, 0.0, 0.0, 1.0)
    glEnable(GL_TEXTURE_2D)
    # Create background texture
    glBindTexture(GL_TEXTURE_2D, texture_background)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, bg_image)

    # Draw background
    # glTranslatef(0.0,0.0,-10.0)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0); glVertex2d(0.0, 0.0)
    glTexCoord2f(1.0, 0.0); glVertex2d(width, 0.0)
    glTexCoord2f(1.0, 1.0); glVertex2d(width, height)
    glTexCoord2f(0.0, 1.0); glVertex2d(0.0, height)
    glEnd()
    glDisable(GL_TEXTURE_2D)

def render_model():
    glTranslate(tx / 20.0, ty / 20.0, -zpos)
    glRotate(ry, 1, 0, 0)
    glRotate(rx, 0, 1, 0)
    glCallList(obj.gl_list)

def display(image):
    # if these lines were still there, i get a black screen
    # glClearColor(0.0, 0.0, 0.0, 1.0)
    # glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Background render
    render_background(image)

    # Foreground render

    # Re-enable depth writes and testing
    # glEnable(GL_DEPTH_TEST)
    # glDepthMask(GL_TRUE)

    # glLoadIdentity()
    # glMatrixMode(GL_PROJECTION)

    # glOrtho(0.0, 800.0, 600.0, 0.0, 0.0, 1.0)

    # render_model()

    # glutSwapBuffers()


rx, ry = (0,0)
tx, ty = (0,0)
zpos = 5
rotate = move = False
image1 = mpimg.imread('test_images/water1.jpg')
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

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # RENDER OBJECT
    display(image1)

    pygame.display.flip()
