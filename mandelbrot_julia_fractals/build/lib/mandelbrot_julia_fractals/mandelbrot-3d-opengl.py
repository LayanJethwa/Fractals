import pygame
import sys
pygame.init()
screen = pygame.display.set_mode((800, 800), pygame.DOUBLEBUF|pygame.OPENGL)
pygame.display.set_caption('Fractals')
font = pygame.font.SysFont("consolas", 20)
running = True


import numpy as np
import cupy as cp
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo

res = 300
iterations = 50
last_bounds = None
x = y = None

bounds = ((-2,2),(-2,2))
def compute_size(bounds):
    return bounds[0][1]-bounds[0][0]
size = compute_size(bounds)

scale = 2.1
height_scale = 5
offset_x = 400
offset_y = 500
theta = np.radians(180)
height_map = None
hm_int = None
angle_x=angle_y = 30

NEAR_Z = -(res*scale)-5
FAR_Z = (res*scale)+(iterations*height_scale)+5
MAX_Z_WORLD = FAR_Z-NEAR_Z
glClearColor(0.1, 0.1, 0.1, 1.0)
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
glOrtho(0, 800, 800, 0, NEAR_Z, FAR_Z)
glMatrixMode(GL_MODELVIEW)
glLoadIdentity()
glEnable(GL_DEPTH_TEST)
glDepthFunc(GL_LESS)


from colour import Color
def compute_colours(iterations):
    red = Color("red")
    colours = list(red.range_to(Color("purple"),iterations))
    colours.pop(-1)
    colours.append(Color("black"))
    return cp.array([tuple(i*255 for i in colour.rgb) for colour in colours])

colours = compute_colours(iterations)


def make_grid(bounds, dtype=cp.float64, res=res):
    global last_bounds, x, y
    if bounds != last_bounds:
        re = cp.linspace(bounds[0][0], bounds[0][1], res, dtype=dtype)
        im = cp.linspace(bounds[1][0], bounds[1][1], res, dtype=dtype)
        x, y = cp.meshgrid(re, im)
        last_bounds = bounds
    return x, y


mandelbrot_kernel_fast = cp.ElementwiseKernel(
    'float64 zx, float64 zy, float64 cx, float64 cy, int32 maxiter, int8 power',
    'int32 m',
    '''
    double zx_temp = zx;
    double zy_temp = zy;
    double cx_temp = cx;
    double cy_temp = cy;

    for (int i = 0; i < maxiter; i++) {
        double zx_new = zx_temp;
        double zy_new = zy_temp;

        for (int p = 1; p < power; p++) {
            double tmp_x = zx_new * zx_temp - zy_new * zy_temp;
            double tmp_y = zx_new * zy_temp + zy_new * zx_temp;
            zx_new = tmp_x;
            zy_new = tmp_y;
        }

        zx_temp = zx_new + cx_temp;
        zy_temp = zy_new + cy_temp;

        if (zx_temp * zx_temp + zy_temp * zy_temp > 4.0) {
            m = i;
            return;
        }
    }
    m = maxiter;
    ''',
    'mandelbrot_kernel'
)


def project_iso_vec(x, y, z, theta):
    c = (res-1)/2
    x_shift = x - c
    y_shift = y - c
    x_rot = x_shift*np.cos(theta) - y_shift*np.sin(theta)
    y_rot = x_shift*np.sin(theta) + y_shift*np.cos(theta)
    screen_x = offset_x + (x_rot - y_rot) * scale
    screen_y = offset_y + (x_rot + y_rot) * scale / 2 - z * height_scale
    depth = -x_rot - y_rot + z * height_scale
    normalized_z = ((depth - NEAR_Z) / MAX_Z_WORLD) * 2.0 - 1.0
    return np.stack([screen_x, screen_y, normalized_z], axis=-1).astype(np.float32)


def calculate(zx, zy, power):
    global colours, height_map, hm_int

    x, y = make_grid(bounds)

    M = mandelbrot_kernel_fast(cp.float64(zx), cp.float64(zy), x, y, cp.int32(iterations), power+1)
    
    height_map = cp.asnumpy(M)
    hm_int = np.clip(height_map.astype(int), 0, 49)
    return height_map


def main():
    global running, theta, hm_int
    calculate(0, 0, 1)

    while running:
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
                exit()
                quit()

        theta += np.radians(1)
        step = 1

        y0, x0 = np.mgrid[0:res-step, 0:res-step]
        y1, x1 = y0, x0 + step
        y2, x2 = y0 + step, x0 + step
        y3, x3 = y0 + step, x0

        z0, z1 = height_map[y0, x0], height_map[y1, x1]
        z2, z3 = height_map[y2, x2], height_map[y3, x3]
        avg_z = (z0 + z1 + z2 + z3) / 4.0

        avg_h = ((hm_int[y0, x0] + hm_int[y1, x1] + hm_int[y2, x2] + hm_int[y3, x3]) // 4).astype(int)
        colours_arr = cp.asnumpy(colours[avg_h]).astype(np.float32) / 255.0

        mask = avg_z != 0
        z0, z1, z2, z3 = z0[mask], z1[mask], z2[mask], z3[mask]
        x0, x1, x2, x3 = x0[mask], x1[mask], x2[mask], x3[mask]
        y0, y1, y2, y3 = y0[mask], y1[mask], y2[mask], y3[mask]
        colours_arr = colours_arr[mask]

        p0 = project_iso_vec(x0, y0, z0, theta)
        p1 = project_iso_vec(x1, y1, z1, theta)
        p2 = project_iso_vec(x2, y2, z2, theta)
        p3 = project_iso_vec(x3, y3, z3, theta)

        vertices = np.vstack([
            np.stack([p0, p1, p2], axis=1),
            np.stack([p0, p2, p3], axis=1)
        ]).reshape(-1, 3)

        vertex_colours = np.vstack([
            np.repeat(colours_arr[:, None, :], 3, axis=1),
            np.repeat(colours_arr[:, None, :], 3, axis=1)
        ]).reshape(-1, 3)


        vertex_vbo = vbo.VBO(vertices)
        colour_vbo = vbo.VBO(vertex_colours)

        glClearColor(1.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        vertex_vbo.bind()
        glVertexPointer(3, GL_FLOAT, 0, vertex_vbo)
        colour_vbo.bind()
        glColorPointer(3, GL_FLOAT, 0, colour_vbo)
        glDrawArrays(GL_TRIANGLES, 0, len(vertices))
        vertex_vbo.unbind()
        colour_vbo.unbind()
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)


        pygame.display.flip()