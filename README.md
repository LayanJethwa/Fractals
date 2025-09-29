
# Fractal visualiser

This project generates fractals in the Mandelbrot and Julia sets, displaying them for the user. As it runs on the GPU for speed increases, I cannot publish to a website for a demo unfortunately.

## Features

- Julia/Mandelbrot set toggle
- Change real and imaginary parts of the seed
- Change index of the calculation (for "Multibrot" sets)
- 3D render with polygon mesh


## Usage

Download and run the fractals.py file for the main code, and the fractals_3d_opengl.py file for the 3D render of the Mandelbrot set. I am running it on an Nvidia GeForce RTX 3070 Ti GPU.

I have uploaded it as a package to PyPi, which can be found here: https://pypi.org/project/mandelbrot-julia-fractals/1.0.0/

You can install and run it using the following commands:

``pip install mandelbrot_julia_fractals``

``from mandelbrot_julia_fractals import fractals``

``from mandelbrot_julia_fractals import mandelbrot_3d_opengl``

``fractals.main()`` or ``mandelbrot_3d_opengl.main()``

## Demo

![Showcase gif](https://github.com/LayanJethwa/Fractals/blob/main/fractals.gif)

