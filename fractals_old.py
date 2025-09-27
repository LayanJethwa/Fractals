import pygame
import numpy as np
from numba import njit, prange
iterations = 0
size = 0
bounds = 0
colours = []

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

def coordinate(x,y):
    return ((x+(0-bounds[0][0]))*(800/size), 800-((y+(0-bounds[1][0]))*(800/size)))

@njit(parallel=True, fastmath=True)
def mandelbrot_kernel(bounds, max, zx, zy):
    re = np.linspace(bounds[0][0], bounds[0][1], 800).astype(np.longdouble)
    im = np.linspace(bounds[1][0], bounds[1][1], 800).astype(np.longdouble)
    M = np.full((800,800), max, dtype=np.int32)

    for ix in prange(800):
        for iy in prange(800):
            c = re[ix]+1j*im[iy]
            z = zx+zy*1j
            for n in range(max):
                if ((z.real*z.real)+(z.imag*z.imag)) > 4:
                    M[iy,ix] = n
                    break
                z = (z*z) + c
    return M

@njit(parallel=True, fastmath=True)
def julia_kernel(bounds, max, zx, zy):
    re = np.linspace(bounds[0][0], bounds[0][1], 800).astype(np.longdouble)
    im = np.linspace(bounds[1][0], bounds[1][1], 800).astype(np.longdouble)
    M = np.full((800,800), max, dtype=np.int32)
    c = zx+zy*1j

    for ix in prange(800):
        for iy in prange(800):
            z = re[ix] + 1j * im[iy]
            for n in range(max):
                if ((z.real*z.real)+(z.imag*z.imag)) > 4:
                    M[iy,ix] = n
                    break
                z = (z*z) + c
    return M