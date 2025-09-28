import pygame
import sys
pygame.init()
screen = pygame.display.set_mode((800, 800), pygame.DOUBLEBUF|pygame.OPENGL)
pygame.display.set_caption('Fractals')
font = pygame.font.SysFont("consolas", 20)
running = True

import widgets

import numpy as np
import cupy as cp
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo

res = 300
iterations = 50
last_bounds = None
x = y = None
flat = False

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
    if not flat:
        colours.pop(-1)
    colours.append(Color("black"))
    return cp.array([tuple(i*255 for i in colour.rgb) for colour in colours])

colours = compute_colours(iterations)


def dynamic_iterations(size, base=50):
    return int(base + 20 * math.log2(4 / size))

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

julia_kernel_fast = cp.ElementwiseKernel(
    'float64 zx, float64 zy, float64 x0, float64 y0, int32 maxiter, int8 power',
    'int32 m',
    '''
    double zx_temp = x0;
    double zy_temp = y0;
    double cx = zx;
    double cy = zy;
    for (int i = 0; i < maxiter; i++) {
        double zx_new = zx_temp;
        double zy_new = zy_temp;

        for (int p = 1; p < power; p++) {
            double tmp_x = zx_new * zx_temp - zy_new * zy_temp;
            double tmp_y = zx_new * zy_temp + zy_new * zx_temp;
            zx_new = tmp_x;
            zy_new = tmp_y;
        }

        zx_temp = zx_new + cx;
        zy_temp = zy_new + cy;

        if (zx_temp * zx_temp + zy_temp * zy_temp > 4.0) {
            m = i;
            return;
        }
    }
    m = maxiter;
    ''',
    'julia_kernel'
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


last_iterations = None
def calculate(zx, zy, power):
    global colours, last_iterations, height_map, hm_int
    if iterations != last_iterations:
        colours = compute_colours(iterations)
        last_iterations = iterations

    x, y = make_grid(bounds)

    if set_type:
        M = mandelbrot_kernel_fast(cp.float64(zx), cp.float64(zy), x, y, cp.int32(iterations), power+1)
    else:
        M = julia_kernel_fast(cp.float64(zx), cp.float64(zy), x, y, cp.int32(iterations), power+1)

    if flat:
        surface_array = cp.asnumpy(colours[M])
        return pygame.surfarray.make_surface(np.swapaxes(surface_array, 0, 1))
    else:
        height_map = cp.asnumpy(M)
        hm_int = np.clip(height_map.astype(int), 0, 49)
        return height_map
    

zx_slider = widgets.Slider(620, 10, 150, 30, -1, 1, 0)
zy_slider = widgets.Slider(620, 50, 150, 30, -1, 1, 0)
power_slider = widgets.Slider(620, 90, 150, 30, 1, 10, 1, integer=True)
zx = cp.float64(zx_slider.value)
zy = cp.float64(zy_slider.value)
power = cp.int8(power_slider.value)
set_switch = widgets.ToggleSwitch(610, 130, 170, 30, True, "Julia", "Mandelbrot")
set_type = set_switch.state

def update_sliders(event=None):
    global zx, zy, power, set_type
    zx_slider.handle_event(event)
    zy_slider.handle_event(event)
    set_switch.handle_event(event)
    power_slider.handle_event(event)
    zx = cp.float64(zx_slider.value)
    zy = cp.float64(zy_slider.value)
    power = cp.int8(power_slider.value)
    set_type = set_switch.state


def render(event=None):
    update_sliders(event)
    if flat:
        fractal_surface = calculate(zx, zy, power)
        screen.fill((0,0,0))
        screen.blit(fractal_surface, (0, 0))
        screen.blit(font.render(f"Zoom: {int(4/size)}x", True, (255, 255, 255)), (10, 10))
        screen.blit(font.render(f"Iterations: {iterations}", True, (255, 255, 255)), (10, 35))
        pygame.draw.rect(screen, (0,0,0), pygame.Rect(490,0,310,170))
        screen.blit(font.render("Re(z):", True, (255, 255, 255)), (550, 15))
        screen.blit(font.render("Im(z):", True, (255, 255, 255)), (550, 55))
        screen.blit(font.render("Power:", True, (255, 255, 255)), (530, 95))
        screen.blit(font.render("Set type:", True, (255, 255, 255)), (505, 135))
        zx_slider.draw(screen)
        zy_slider.draw(screen)
        set_switch.draw(screen)
        power_slider.draw(screen)
    else:
        pygame.draw.rect(screen, (0,0,0), pygame.Rect(490,0,310,170))
        screen.blit(font.render("Re(z):", True, (255, 255, 255)), (550, 15))
        screen.blit(font.render("Im(z):", True, (255, 255, 255)), (550, 55))
        screen.blit(font.render("Power:", True, (255, 255, 255)), (530, 95))
        screen.blit(font.render("Set type:", True, (255, 255, 255)), (505, 135))
        zx_slider.draw(screen)
        zy_slider.draw(screen)
        set_switch.draw(screen)
        power_slider.draw(screen)


if __name__ == "__main__":
    if not flat:
        calculate(zx, zy, power)
    else:
        render()

    while running:
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
                exit()
                quit()

            if flat:
                if event.type == pygame.MOUSEWHEEL:
                    if event.y == 1:
                        bounds = ((bounds[0][0]+size/4,bounds[0][1]-size/4),(bounds[1][0]+size/4,bounds[1][1]-size/4))
                    elif event.y == -1:
                        if size < 4:
                            bounds = ((bounds[0][0]-size/2,bounds[0][1]+size/2),(bounds[1][0]-size/2,bounds[1][1]+size/2))
                    size = compute_size(bounds)
                    iterations = dynamic_iterations(size)
                    render()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        bounds = (tuple(i-size*0.1 for i in bounds[0]), bounds[1])
                    elif event.key == pygame.K_RIGHT:
                        bounds = (tuple(i+size*0.1 for i in bounds[0]), bounds[1])
                    elif event.key == pygame.K_UP:
                        bounds = (bounds[0], tuple(i-size*0.1 for i in bounds[1]))
                    elif event.key == pygame.K_DOWN:
                        bounds = (bounds[0], tuple(i+size*0.1 for i in bounds[1]))
                    render()

                elif event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]:
                    render(event)


        if not flat:
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
