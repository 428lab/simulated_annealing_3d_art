import numpy as np
from PIL import Image, ImageDraw
import random
import math
import cv2

import pygame
from pygame.locals import DOUBLEBUF, OPENGL

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import pickle

# Cube vertices and surfaces
vertices = (
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, -1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, -1, 1),
    (-1, 1, 1)
)

surfaces = (
    (0,1,2,3),
    (3,2,7,6),
    (6,7,5,4),
    (4,5,1,0),
    (1,5,7,2),
    (4,0,3,6)
)


def setup_viewport(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (width / height), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, 10, 0, 0, 0, 0, 1, 0)  # カメラの位置と向きを設定

def draw_cube(size):
    glColor3f(0, 0, 0)  # 黒色の立方体
    glBegin(GL_QUADS)
    for surface in surfaces:
        for vertex in surface:
            glVertex3fv([v * size for v in vertices[vertex]])
    glEnd()


def rendering_image(current_cubes, img_size, cube_size):
    cnt = 40
    # メインループ
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # ここで全体の回転を適用
        glPushMatrix()
        glRotatef(cnt, 1, 1, 1)  # X軸を中心に回転


        for x, y, z, angle in current_cubes:
            glPushMatrix()
            glTranslatef(x, y, z)
            glRotatef(angle, 0, 1, 0)
            #glRotatef(cnt, 1, 0, 0)  # X軸を中心に回転

            draw_cube(cube_size)  # 立方体を描画
            glPopMatrix()
        cnt += 1

        glPopMatrix()

        pygame.display.flip()
        if cnt % 360 == 0:
            pygame.time.wait(1000)

    return 

# 初期配置を生成
img_size = (128, 128)
cube_size= 0.2

pygame.init()
display = (img_size[0], img_size[1])
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

glClearColor(1.0, 1.0, 1.0, 1.0)  # 白色に設定
glEnable(GL_DEPTH_TEST)

# ここでビューポートと投影を設定
setup_viewport(display[0], display[1])

with open("final_cubes.pkl", "rb") as fp:   # Unpickling
    final_cubes =  pickle.load(fp)

# 最終的な画像を生成して保存
final_img = rendering_image(final_cubes, img_size, cube_size)
final_img.show()
