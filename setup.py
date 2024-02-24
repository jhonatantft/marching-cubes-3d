# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE.md') as f:
    license = f.read()

setup(
    name='Marching Cubes',
    version='0.0.1',
    description='Marching Cubes in 3d',
    keywords='marching cubes 3d python opengl',
    long_description=readme,
    author='Jhonatan Tomimatsu',
    author_email='jhonatan.tft@gmail.com',
    url='https://github.com/jhonatantft/marching-cubes-3d',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)