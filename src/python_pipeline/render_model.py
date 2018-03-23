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
import numpy as np
import argparse
import cv2
import moviepy.editor as mpy
import image_processor
import calibration
import random
import math

# import pywavefront

# IMPORT OBJECT LOADER
from objloader import *

pygame.init()
viewport = (800, 600)
hx = viewport[0]/2
hy = viewport[1]/2
surface = pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF)

glLightfv(GL_LIGHT0, GL_POSITION,  (-10, 100, 50, 0.0))
glLightfv(GL_LIGHT0, GL_AMBIENT, (0.5, 0.5, 0.5, 1.0))
glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
glEnable(GL_LIGHT0)
glEnable(GL_LIGHTING)
# Most .obj files expect to be smooth-shaded
glShadeModel(GL_SMOOTH)
glClearDepth(1.0)
glDepthFunc(GL_LESS)

# LOAD OBJECT AFTER PYGAME INIT
obj = None
camera_matrix = None

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

def render_model(tx, ty, ry, rx, zpos):
    glColorMaterial(GL_FRONT, GL_SPECULAR)
    glEnable(GL_COLOR_MATERIAL)
    glColor3f(1.0, 0.0, 0.0)
    glTranslate(tx, ty, -zpos)
    glRotate(ry, 1, 0, 0)
    glRotate(rx, 0, 1, 0)
    glCallList(obj.gl_list)
    glDisable(GL_COLOR_MATERIAL)

def display(image, tx, ty, ry, rx, zpos):
    glLoadIdentity()

    # Background render
    render_background(image)

    # Foreground render
    # Re-enable depth writes and testing
    glEnable(GL_DEPTH_TEST)
    glDepthMask(GL_TRUE)

    glLoadIdentity()
    glMatrixMode(GL_PROJECTION)

    # Compute our Projection Matrix using our calibrated camera.
    near = 1.0
    far = 100.0
    persp = np.zeros((4, 4))
    persp[0, 0] = camera_matrix[0, 0] / camera_matrix[0, 2]
    persp[1, 1] = camera_matrix[1, 1] / camera_matrix[1, 2]
    persp[2, 2] = -(far + near) / (far - near)
    persp[2, 3] = -(2 * far * near) / (far - near)
    persp[3, 2] = -1
    glMultMatrixf(persp)

    render_model(tx, ty, ry, rx, zpos)

    pygame.display.flip()
    # Get a numpy array from the pygame window
    string_image = pygame.image.tostring(surface, 'RGB')
    temp_surf = pygame.image.fromstring(string_image, (width, height), 'RGB' )
    im = pygame.surfarray.array3d(temp_surf)
    return im

def normalize_coordinates(x, y, external_width=800, external_height=600):
    internal_width = 200
    internal_height = 100
    x = (x * internal_width) / external_width
    y = (y * internal_height) / external_height
    x = x - internal_width / 2
    y = -y + internal_height / 2
    return (x, y)

# Returns fov_y on degrees
def camera_field_of_view_y():
    fov_y = 2 * math.atan2(height, (2 * camera_matrix[1, 1]))
    return math.degrees(fov_y)

tracking_keypoint = cv2.KeyPoint(0, 0, 1)
def make_frame(time, tx=0, ty=0, rx=90, ry=135, zpos=40):
    global tracking_keypoint
    # Capture frame-by-frame
    ret, frame = cap.read()

    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

    # RENDER OBJECT
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    matches_keypoints = image_processor.processImage(frame)
    tracking_keypoint = choose_keypoint(tracking_keypoint, matches_keypoints)
    if time != 0:
        tx = time * 10
        ty = time * 10
    # print("keypoint %d, %d" % (tracking_keypoint.pt[0], tracking_keypoint.pt[1]))
    # print("srf %d, %d" % (surface.get_width(), surface.get_height()))
    tx, ty = normalize_coordinates(tracking_keypoint.pt[0], tracking_keypoint.pt[1])
    rx = 160
    ry = 170
    # print("tx: %d, ty: %d, rx: %d, ry: %d, zpos: %d" % (tx, ty, rx, ry, zpos))
    return display(frame, tx, ty, rx, ry, zpos)

def choose_keypoint(old_keypoint, matches_keypoints):
    secure_random = random.SystemRandom()
    closest_distance = float('inf')
    closest_keypoint = old_keypoint
    x = 0
    y = 1
    for current_index, keypoint_no in matches_keypoints[0].iteritems():
        keypoint = matches_keypoints[1][current_index]
        distance = math.sqrt(
                (keypoint.pt[y] - old_keypoint.pt[y]) ** 2 + (keypoint.pt[x] - old_keypoint.pt[x]) ** 2 )
        if distance < closest_distance:
            closest_distance = distance
            closest_keypoint = keypoint
    return closest_keypoint


def game():
    rx, ry = (0, 0)
    tx, ty = (0, 0)
    zpos = 40
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
        make_frame(0, tx, ty, rx, ry, zpos)

def defineFlags():
    parser = argparse.ArgumentParser(description='Feature ketpoint finder')
    parser.add_argument('--obj', help='Pass in the .obj file')
    parser.add_argument('--video', action='store_true')
    return parser.parse_args()

cap = cv2.VideoCapture(0)
# tx: -23, ty: -10, rx: 157, ry: 527, zpos: 17
def main():
    global obj
    global camera_matrix

    args = defineFlags()
    camera_matrix = calibration.calibrate_camera()
    print(camera_matrix)
    if not args.obj:
        raise Exception('Require .obj file path')
    obj = OBJ(args.obj, swapyz=True)
    if args.video:
        output_video = 'pygame_video_output.mp4'
        output_clip = mpy.VideoClip(make_frame, duration=10) # 10 seconds
        output_clip.write_videofile(output_video, audio=False, fps=24)
    else:
        game()

main()
