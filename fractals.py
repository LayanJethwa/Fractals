import pygame
import sys
pygame.init()
screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption('Fractals')
font = pygame.font.SysFont("consolas", 20)
running = True

import numpy as np
from numba import njit, prange

iterations = 50

from colour import Color
def compute_colours(iterations):
    red = Color("red")
    colours = list(red.range_to(Color("purple"),iterations))
    colours.append(Color("black"))
    colours = np.array([tuple(i*255 for i in colour.rgb) for colour in colours])
    return colours

colours = compute_colours(iterations)

def dynamic_iterations(size, base=50):
    import math
    return int(base + 20 * math.log2(4 / size))

def mandelbrot_recursive(point, max = iterations, count = 0, start = 0):
    if abs(start) > 2:
        return count
    count += 1
    if count < max:
        return mandelbrot_recursive(point, max, count, (start**2) + point)
    else:
        return max

def mandelbrot_basic(point, max = iterations, start = 0):
    for count in range(max):
        if abs(start) > 2:
            return count
        start = (start**2) + point
    return max

@njit(parallel=True, fastmath=True)
def mandelbrot(bounds, max):
    re = np.linspace(bounds[0][0], bounds[0][1], 800).astype(np.longdouble)
    im = np.linspace(bounds[1][0], bounds[1][1], 800).astype(np.longdouble)
    M = np.full((800,800), max, dtype=np.int32)

    for ix in prange(800):
        for iy in prange(800):
            c = re[ix]+1j*im[iy]
            z = 0.0j
            for n in range(max):
                if ((z.real*z.real)+(z.imag*z.imag)) > 4:
                    M[iy,ix] = n
                    break
                z = (z*z) + c
    return M


bounds = ((-2,2),(-2,2))

def compute_size(bounds):
    return bounds[0][1]-bounds[0][0]

size = compute_size(bounds)

def coordinate(x,y):
    return ((x+(0-bounds[0][0]))*(800/size), 800-((y+(0-bounds[1][0]))*(800/size)))

def basic_compute():
    samples = 800
    surface_array = np.zeros((800, 800, 3))
    factor = samples/size
    for x in range(int(bounds[0][0]*factor),int(bounds[0][1]*factor)):
        x = x/factor
        for y in range(int(bounds[1][0]*factor),int(bounds[1][1]*factor)):
            y = y/factor
            coordinates = tuple(int(i) for i in coordinate(x,y))
            try: surface_array[coordinates] = colours[mandelbrot_basic(complex(x,0)+complex(0,y))]
            except: continue
    fractal_surface = pygame.surfarray.make_surface(surface_array)
    return fractal_surface

def vectorisation():
    global colours
    colours = compute_colours(iterations)
    M = mandelbrot(bounds, iterations)
    surface_array = colours[M]

    return pygame.surfarray.make_surface(np.swapaxes(surface_array, 0, 1))

def calculate():
    #fractal_surface = basic_compute()
    fractal_surface = vectorisation()
    return fractal_surface
    
def render():
    fractal_surface = calculate()
    screen.fill((0,0,0))
    screen.blit(fractal_surface, (0, 0))
    screen.blit(font.render(f"Zoom: {int(4/size)}x", True, (255, 255, 255)), (10, 10))
    screen.blit(font.render(f"Iterations: {iterations}", True, (255, 255, 255)), (10, 35))
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

    pygame.display.update()
