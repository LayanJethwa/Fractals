import pygame
import sys
pygame.init()
screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption('Fractals')
font = pygame.font.SysFont("consolas", 20)
running = True

import widgets

import numpy as np
import cupy as cp
import math

iterations = 50
last_bounds = None
x = y = None


from colour import Color
def compute_colours(iterations):
    red = Color("red")
    colours = list(red.range_to(Color("purple"),iterations))
    colours.append(Color("black"))
    return cp.array([tuple(i*255 for i in colour.rgb) for colour in colours])

colours = compute_colours(iterations)


def dynamic_iterations(size, base=50):
    return int(base + 20 * math.log2(4 / size))

def make_grid(bounds, dtype=cp.float64):
    global last_bounds, x, y
    if bounds != last_bounds:
        re = cp.linspace(bounds[0][0], bounds[0][1], 800, dtype=dtype)
        im = cp.linspace(bounds[1][0], bounds[1][1], 800, dtype=dtype)
        x, y = cp.meshgrid(re, im)
        last_bounds = bounds
    return x, y


mandelbrot_kernel_fast = cp.ElementwiseKernel(
    'float64 zx, float64 zy, float64 cx, float64 cy, int32 maxiter',
    'int32 m',
    '''
    double zx_temp = zx;
    double zy_temp = zy;
    double cx_temp = cx;
    double cy_temp = cy;
    for (int i = 0; i < maxiter; i++) {
        double zx2 = zx_temp * zx_temp - zy_temp * zy_temp + cx_temp;
        double zy2 = 2 * zx_temp * zy_temp + cy_temp;
        zx_temp = zx2;
        zy_temp = zy2;
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
    'float64 zx, float64 zy, float64 x0, float64 y0, int32 maxiter',
    'int32 m',
    '''
    double zx_temp = x0;
    double zy_temp = y0;
    double cx = zx;
    double cy = zy;
    for (int i = 0; i < maxiter; i++) {
        double zx2 = zx_temp * zx_temp - zy_temp * zy_temp + cx;
        double zy2 = 2 * zx_temp * zy_temp + cy;
        zx_temp = zx2;
        zy_temp = zy2;
        if (zx_temp * zx_temp + zy_temp * zy_temp > 4.0) {
            m = i;
            return;
        }
    }
    m = maxiter;
    ''',
    'julia_kernel'
)


bounds = ((-2,2),(-2,2))
def compute_size(bounds):
    return bounds[0][1]-bounds[0][0]
size = compute_size(bounds)


last_iterations = None
def calculate(zx, zy):
    global colours, last_iterations
    if iterations != last_iterations:
        colours = compute_colours(iterations)
        last_iterations = iterations

    x, y = make_grid(bounds)

    if set_type:
        M = mandelbrot_kernel_fast(cp.float64(zx), cp.float64(zy), x, y, cp.int32(iterations))
    else:
        M = julia_kernel_fast(cp.float64(zx), cp.float64(zy), x, y, cp.int32(iterations))

    surface_array = cp.asnumpy(colours[M])
    return pygame.surfarray.make_surface(np.swapaxes(surface_array, 0, 1))
    

zx_slider = widgets.Slider(620, 10, 150, 30, -1, 1, 0, False)
zy_slider = widgets.Slider(620, 50, 150, 30, -1, 1, 0, False)
zx = cp.float64(zx_slider.value)
zy = cp.float64(zy_slider.value)
set_switch = widgets.ToggleSwitch(610, 90, 170, 30, True, "Julia", "Mandelbrot")
set_type = set_switch.state

def update_sliders(event=None):
    global zx, zy, set_type
    zx_slider.handle_event(event)
    zy_slider.handle_event(event)
    set_switch.handle_event(event)
    zx = cp.float64(zx_slider.value)
    zy = cp.float64(zy_slider.value)
    set_type = set_switch.state


def render(event=None):
    update_sliders(event)
    fractal_surface = calculate(zx, zy)
    screen.fill((0,0,0))
    screen.blit(fractal_surface, (0, 0))
    screen.blit(font.render(f"Zoom: {int(4/size)}x", True, (255, 255, 255)), (10, 10))
    screen.blit(font.render(f"Iterations: {iterations}", True, (255, 255, 255)), (10, 35))
    pygame.draw.rect(screen, (0,0,0), pygame.Rect(490,0,310,130))
    screen.blit(font.render("Re(z):", True, (255, 255, 255)), (550, 15))
    screen.blit(font.render("Im(z):", True, (255, 255, 255)), (550, 55))
    screen.blit(font.render("Set type:", True, (255, 255, 255)), (505, 95))
    zx_slider.draw(screen)
    zy_slider.draw(screen)
    set_switch.draw(screen)

render()


while running:
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
            exit()
            quit()

        elif event.type == pygame.MOUSEWHEEL:
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

    pygame.display.update()
