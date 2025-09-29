
# Fractal visualiser

This project generates fractals in the Mandelbrot and Julia sets, displaying them for the user.

## Features

- Julia/Mandelbrot set toggle
- Change real and imaginary parts of the seed
- Change index of the calculation (for "Multibrot" sets)
- 3D render with polygon mesh
- Up to 2^54 times zoom


## Usage

``pip install mandelbrot_julia_fractals``

``from mandelbrot_julia_fractals import fractals``

``from mandelbrot_julia_fractals import mandelbrot_3d_opengl``

``fractals.main()`` or ``mandelbrot_3d_opengl.main()``

