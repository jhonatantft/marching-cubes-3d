import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import sys
from OpenGL.GLUT import *
from visualize.marching_cubes import Render

def main():
    glutInit()
    cubeSize = 10
    # start app
    App = Render(cubeSize)
    App.loop()

if __name__ == '__main__':
    main()