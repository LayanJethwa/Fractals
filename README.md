# Fractal visualiser

This project generates fractals in the Mandelbrot and Julia sets, displaying them for the user. It runs on the GPU for speed increases, and I have created a PyPi package so that it can be easily downloaded.

## Features

- Julia/Mandelbrot set toggle
- Change real and imaginary parts of the seed
- Change index of the calculation (for "Multibrot" sets)
- 3D render with polygon mesh

## Usage

Download and run the fractals.py file for the main code, and the fractals_3d_opengl.py file for the 3D render of the Mandelbrot set. I am running it on an Nvidia GeForce RTX 3070 Ti GPU.

I have uploaded it as a package to PyPi, which can be found here: https://pypi.org/project/mandelbrot-julia-fractals/

You can install and run it using the following commands:

``pip install mandelbrot_julia_fractals``

``from mandelbrot_julia_fractals import fractals``

``from mandelbrot_julia_fractals import mandelbrot_3d_opengl``

``fractals.main()`` or ``mandelbrot_3d_opengl.main()``

## Requirements

- colour==0.1.5
- cupy_cuda13x==13.6.0
- numpy==2.1.1
- pygame==2.1.2
- PyOpenGL==3.1.10
- setuptools==63.2.0

## Demo

![Showcase gif](https://github.com/LayanJethwa/Fractals/blob/main/fractals.gif)
