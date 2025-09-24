import pygame
import sys
pygame.init()
screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption('Fractals')
running = True
import numpy as np

iterations = 50

from colour import Color
red = Color("red")
colours = list(red.range_to(Color("purple"),iterations))
colours.append(Color("black"))
colours = np.array([tuple(i*255 for i in colour.rgb) for colour in colours])

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

def mandelbrot(bounds, max = iterations, start = 0):
    re = np.linspace(bounds[0], bounds[1], 800)
    im = np.linspace(bounds[0], bounds[1], 800)
    x, y = np.meshgrid(re, im)
    points = x + 1j*y

    Z = np.zeros_like(points, dtype=np.complex128)
    M = np.full(points.shape, max, dtype=np.int32)

    mask = np.ones(points.shape, dtype=bool)
    for i in range(max):
        Z[mask] = Z[mask] * Z[mask] + points[mask]
        mask = (np.abs(Z) <= 2)
        M[np.logical_not(mask) & (M == max)] = i

    return M


bounds = (-2,2)
def coordinate(x,y):
    return ((x+(0-bounds[0]))*(800/(bounds[1]-bounds[0])), 800-((y+(0-bounds[0]))*(800/(bounds[1]-bounds[0]))))

def basic_compute():
    samples = 800
    surface_array = np.zeros((800, 800, 3))
    factor = samples/(bounds[1]-bounds[0])
    for x in range(int(bounds[0]*factor),int(bounds[1]*factor)):
        x = x/factor
        for y in range(int(bounds[0]*factor),int(bounds[1]*factor)):
            y = y/factor
            coordinates = tuple(int(i) for i in coordinate(x,y))
            try: surface_array[coordinates] = colours[mandelbrot_basic(complex(x,0)+complex(0,y))]
            except: continue
    fractal_surface = pygame.surfarray.make_surface(surface_array)
    return fractal_surface

#fractal_surface = basic_compute()

M = mandelbrot(bounds)
surface_array = colours[M]

fractal_surface = pygame.surfarray.make_surface(np.swapaxes(surface_array, 0, 1))

while running:
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
            exit()
            quit()
    screen.blit(fractal_surface, (0, 0))
    pygame.display.update()
