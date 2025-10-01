import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mandelbrot_julia_fractals",
    version="1.0.2",
    author="Layan Jethwa",
    author_email="lrsjethwa3.14@gmail.com",
    description="A fractal visualisation for the Mandelbrot and Julia sets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LayanJethwa/fractals",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "colour==0.1.5",
        "cupy_cuda13x==13.6.0",
        "numpy==2.1.1",
        "pygame==2.1.2",
        "PyOpenGL==3.1.10"
    ],
)