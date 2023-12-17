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

import argparse

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


def create_initial_cubes(num_cubes, image_size, cube_size, init_cubes=None):
    pygame.init()
    display = (image_size[0], image_size[1])
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    glClearColor(1.0, 1.0, 1.0, 1.0)  # 白色に設定
    glEnable(GL_DEPTH_TEST)

    # ここでビューポートと投影を設定
    setup_viewport(display[0], display[1])

    cubes = []

    if init_cubes == None:

        """ 初期の立方体の配置を生成 """
        for _ in range(num_cubes):
            x, y, z = [random.uniform(-5, 5) for _ in range(3)]
            angle = random.uniform(0, 45)
            cubes.append((x, y, z, angle))
    else:
        for x, y, z, angle in init_cubes:
            cubes.append((x, y, z, angle))

    return cubes

#finds the straight-line distance between two points
def distance(ax, ay, bx, by):
    return math.sqrt((by - ay)**2 + (bx - ax)**2)

#rotates point `A` about point `B` by `angle` radians clockwise.
def rotated_about(ax, ay, bx, by, angle):
    radius = distance(ax,ay,bx,by)
    angle += math.atan2(ay-by, ax-bx)
    return (
        round(bx + radius * math.cos(angle)),
        round(by + radius * math.sin(angle))
    )

def grab_opengl_bitmap(img_size):
    glReadBuffer(GL_FRONT)
    pixels = glReadPixels(0, 0, img_size[0], img_size[1], GL_RGBA, GL_UNSIGNED_BYTE)
    return np.frombuffer(pixels, dtype=np.uint8).reshape(img_size[1], img_size[0], 4)

def numpy_to_pillow_image(np_image):
    return Image.fromarray(np.flip(np_image, axis=0), 'RGBA')

def generate_image(current_cubes, img_size, cube_size):

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    for x, y, z, angle in current_cubes:
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(angle, 0, 1, 0)
        draw_cube(cube_size)  # 立方体を描画
        glPopMatrix()

    #glFinish()  # レンダリングが完了するまで待機
    pygame.display.flip()

    # OpenGLのフレームバッファからビットマップを取得
    bitmap = grab_opengl_bitmap(img_size)

    # NumPy配列をPillow画像に変換
    pillow_image = numpy_to_pillow_image(bitmap)

    return pillow_image.convert('L')

def calculate_error(target_img, generated_img):
    """ RMSEを計算 """
    target_arr = np.array(target_img, dtype=np.float64)
    generated_arr = np.array(generated_img, dtype=np.float64)
    mse = np.mean((target_arr - generated_arr) ** 2)
    rmse = np.sqrt(mse)
    return rmse

def simulated_annealing(cubes, target_img, max_iter, start_temp, end_temp, img_size, cube_size):
    """ シミュレーテッドアニーリングのメインループ """
    temp = start_temp
    current_cubes = cubes
    current_img = generate_image(current_cubes, img_size, cube_size)
    current_error = calculate_error(target_img, current_img)

    for i in range(max_iter):
        new_cubes = current_cubes.copy()
        # ここでランダムに正方形を変更
        cube_index = random.randint(0, len(new_cubes) - 1)
        new_cubes[cube_index] = (
            random.uniform(-5, 5),
            random.uniform(-5, 5),
            random.uniform(-5, 5),
            random.uniform(0, 45)
        )

        new_img = generate_image(new_cubes, img_size, cube_size)
        new_error = calculate_error(target_img, new_img)

        if i % 1000 == 0:
            print('new_error',i,new_error)
            #cv2.imshow('rendering',np.array(new_img, dtype=np.uint8))
            #cv2.waitKey(1)

        # エラーが減少するか、確率で更新を受理
        if new_error < current_error or random.random() < math.exp((current_error - new_error) / temp):
            current_cubes = new_cubes
            current_error = new_error

        # 温度を更新
        temp = start_temp * (end_temp / start_temp) ** (i / max_iter)

    return current_cubes


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--target-img', required=True, type=str, help='target image to create by 3D graphics')
    parser.add_argument('--init-cubes-file', type=str, help='specify initial cubes')
    parser.add_argument('--num-cubes', default=100, type=int, help='num of cubes in 3D space')
    parser.add_argument('--cube-size', default=0.2, type=float, help='num of cubes in 3D space')
    parser.add_argument('--max-iter', default=10000, type=int, help='max iter for simirated annealing')
    parser.add_argument('--start-temp', default=10.0, type=float, help='start temperature for simirated annealing')
    parser.add_argument('--end-temp', default=0.1, type=float, help='end temperature for simirated annealing')
    opt = parser.parse_args()
    print(opt)

    # 目的のモノクロ画像を読み込み
    img = Image.open(opt.target_img).convert('L')

    img_size = (img.size)

    init_cubes_file = opt.init_cubes_file
    initial_cubes = []
    if init_cubes_file == None:
        num_cubes = opt.num_cubes
        cube_size = opt.cube_size
        initial_cubes = create_initial_cubes(num_cubes, img_size, cube_size)
    else:
        with open(init_cubes_file, "rb") as fp:   # Unpickling
            cubes = pickle.load(fp)
        num_cubes = len(cubes)
        cube_size = opt.cube_size
        initial_cubes = create_initial_cubes(num_cubes, img_size, cube_size, init_cubes=cubes)
    print('initial_cubes',initial_cubes)
    print('len(initial_cubes)',len(initial_cubes))

    # シミュレーテッドアニーリングパラメータ
    max_iter = opt.max_iter
    start_temp = opt.start_temp
    end_temp = opt.end_temp

    final_cubes = simulated_annealing(initial_cubes, img, max_iter, start_temp, end_temp, img_size, cube_size)

    # 最終的な画像を生成して保存
    final_img = generate_image(final_cubes, img_size, cube_size)
    basename = os.path.splitext(os.path.basename(opt.target_img))[0]
    final_img.save(basename + '_result.png')

    with open(basename + "_cubes.pkl", "wb") as fp:   #Pickling
        pickle.dump(final_cubes, fp)
    with open(basename + "_cubes.pkl", "rb") as fp:   # Unpickling
        b = pickle.load(fp)
    print(b==final_cubes)

