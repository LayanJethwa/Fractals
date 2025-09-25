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

def mandelbrot(bounds, max = iterations):
    re = np.linspace(bounds[0][0], bounds[0][1], 800)
    im = np.linspace(bounds[1][0], bounds[1][1], 800)
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
    M = mandelbrot(bounds)
    surface_array = colours[M]

    return pygame.surfarray.make_surface(np.swapaxes(surface_array, 0, 1))

def calculate():
    #fractal_surface = basic_compute()
    fractal_surface = vectorisation()
    return fractal_surface

fractal_surface = calculate()

while running:
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
            exit()
            quit()

        elif event.type == pygame.MOUSEWHEEL:
            print(bounds)
            if event.y == 1:
                bounds = ((bounds[0][0]+size/4,bounds[0][1]-size/4),(bounds[1][0]+size/4,bounds[1][1]-size/4))
            elif event.y == -1:
                bounds = ((bounds[0][0]-size/2,bounds[0][1]+size/2),(bounds[1][0]-size/2,bounds[1][1]+size/2))
            size = compute_size(bounds)
            print(bounds)
            fractal_surface = calculate()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                bounds = (tuple(i-size*0.1 for i in bounds[0]), bounds[1])
            elif event.key == pygame.K_RIGHT:
                bounds = (tuple(i+size*0.1 for i in bounds[0]), bounds[1])
            elif event.key == pygame.K_UP:
                bounds = (bounds[0], tuple(i-size*0.1 for i in bounds[1]))
            elif event.key == pygame.K_DOWN:
                bounds = (bounds[0], tuple(i+size*0.1 for i in bounds[1]))
            size = compute_size(bounds)
            fractal_surface = calculate()

    screen.blit(fractal_surface, (0, 0))
    pygame.display.update()
