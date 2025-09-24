import pygame
import sys
import cmath
pygame.init()
screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption('Fractals')
running = True
black = (0,0,0)
white = (255,255,255)

from colour import Color
red = Color("red")
colours = list(red.range_to(Color("green"),50))

def mandelbrot(point, max = 50, count = 0, start=0):
    if abs(start) > 2:
        return count
    count += 1
    if count < max:
        return mandelbrot(point, max, count, (start**2) + point)
    else:
        return -1

bounds = (0,0.5)
def coordinate(x,y):
    return ((x+(0-bounds[0]))*(800/(bounds[1]-bounds[0])), 800-((y+(0-bounds[0]))*(800/(bounds[1]-bounds[0]))))

samples = 800
factor = samples/(bounds[1]-bounds[0])
for x in range(int(bounds[0]*factor),int(bounds[1]*factor)):
    x = x/factor
    for y in range(int(bounds[0]*factor),int(bounds[1]*factor)):
        y = y/factor
        result = mandelbrot(complex(x,0)+complex(0,y))
        if result == -1:
            pygame.draw.circle(screen, black, coordinate(x,y), 1)
        else:
            pygame.draw.circle(screen, tuple((i*255 for i in colours[result].rgb)), coordinate(x,y), 1)

    
while running:
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
            exit()
            quit()
    pygame.display.update()
