import random
import time
import numpy as np
import pygame
from noise import snoise4
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from polygon.polygon_vertices import marchingCubesPolygons

# Global scope
screenWidth = 1200 
screenHeight = 800
radius = 20
threshold = 0.5

class Render:
    DISPLAYMODE_POINTS = 0
    DISPLAYMODE_MESH = 1
    
    def __init__(self, worldSize):
        # random number
        random.seed(time.process_time())	
        self.FPS = 30	
        self.seedWorldTimer = self.FPS
        self.displayMode = self.DISPLAYMODE_POINTS
        
        # random world
        self.worldSize = int(worldSize+1)
        self.world = [[[0 for x in range(self.worldSize)] for y in range(self.worldSize)] for z in range(self.worldSize)]
        self.worldThreshold = threshold
        self.getWorldValues()
        
        # initial marching cubes
        self.polygons = [[[[] for x in range(self.worldSize)] for y in range(self.worldSize)] for z in range(self.worldSize)]
        self.findPolygons()
        
        # app window
        pygame.init()
        pygame.display.set_caption('Marching Cubes')
        self.displaySize = (screenWidth, screenHeight)
        pygame.display.set_mode(self.displaySize, DOUBLEBUF | OPENGL)
        self.clock = pygame.time.Clock()
        
        # spehre type
        self.sphere = gluNewQuadric()
        
        # openGL perspective
        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, (screenWidth / screenHeight), 0.1, 50.0)
        
        # view
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glEnable(GL_DEPTH_TEST)

        # camera data
        self.cameraPolar = [radius, 0, 90]	# r, theta, phi
        self.cameraPositionToCartesian()
        self.cameraTarget = [0, 0, 0]
        self.up = [0, 1, 0]
        glLoadIdentity()
        gluLookAt(*self.cameraPosition, *self.cameraTarget, *self.up)

    def loop(self):
        """
        One per frame according to defined FPS until the user
        closes the window
        """
        while True:
            # 30 FPS
            self.dt = self.clock.tick(self.FPS)

            for event in pygame.event.get():
                # quit
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # mouse scroll - threshold
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 5: 
                        self.worldThreshold += 0.01
                        if self.worldThreshold > 1.0: self.worldThreshold = 1
                    if event.button == 4: 
                        self.worldThreshold -= 0.01
                        if self.worldThreshold < 0.0: self.worldThreshold = 0

                    # on threshold change, get all polygons again
                    self.findPolygons()
            
            self.keyboardController()
            
            # draw new scene
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.drawScene()
            
            glLoadIdentity()
            gluLookAt(*self.cameraPosition, *self.cameraTarget, *self.up)
            pygame.display.flip()

    def cameraPositionToCartesian(self):
        """
        Get camera's position to cartesian
        """
        x = self.cameraPolar[0] * np.sin(self.cameraPolar[1] * np.pi / 180) * np.sin(self.cameraPolar[2] * np.pi / 180)
        y = self.cameraPolar[0] * np.cos(self.cameraPolar[2] * np.pi / 180)
        z = self.cameraPolar[0] * np.cos(self.cameraPolar[1] * np.pi / 180) * np.sin(self.cameraPolar[2] * np.pi / 180)
        self.cameraPosition = [x, y, z]

    def keyboardController(self):
        """
        Users input to handle camera and mode
        """
        keypress = pygame.key.get_pressed()

        # recreates world if R is pressed
        if keypress[pygame.K_r]:
            if not self.seedWorldTimer:
                self.seedWorldTimer = int(self.FPS/4)
                self.getWorldValues()
                self.findPolygons()

        # for new randomizations
        if self.seedWorldTimer:
            self.seedWorldTimer -= 1

        # display Mode
        if keypress[pygame.K_p]:
            self.displayMode = self.DISPLAYMODE_POINTS
            glEnable(GL_CULL_FACE)
            glCullFace(GL_BACK)
        elif keypress[pygame.K_o]:
            self.displayMode = self.DISPLAYMODE_MESH
            glDisable(GL_CULL_FACE)

        # keyboard moviment
        if keypress[pygame.K_w]:
            self.cameraPolar[2] -= 0.1 * self.dt
            if self.cameraPolar[2] < 1:
                self.cameraPolar[2] = 1.0
        if keypress[pygame.K_s]:
            self.cameraPolar[2] += 0.1 * self.dt
            if self.cameraPolar[2] > 179:
                self.cameraPolar[2] = 179
        if keypress[pygame.K_d]:
            self.cameraPolar[1] += 0.1 * self.dt
            if self.cameraPolar[1] > 180:
                self.cameraPolar[1] -= 360
        if keypress[pygame.K_a]:
            self.cameraPolar[1] -= 0.1 * self.dt
            if self.cameraPolar[1] <= -180:
                self.cameraPolar[1] += 360


        # update camera cartesian position
        self.cameraPositionToCartesian()


    def drawScene(self):
        """
        Renders scene in OpenGL. The main axes and bounding box of the world are always drawn,
        but the visualization of the world data depends on the current drawing mode selected
        by the user
        # """

        glBegin(GL_LINES)
        # draw axes
        glColor3f(1, 0, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(self.worldSize / 5, 0, 0)
        glColor3f(1, 0, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, self.worldSize / 5, 0)
        glColor3f(1, 0, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, self.worldSize / 5)

        # surrounding box
        glColor3f(0, 0, 0)

        scalar = (self.worldSize - 1) / 2
        for x in [-1, 1]:
            for y in [-1,1]:
                for z in [-1,1]:
                    glVertex3f(scalar * x, scalar * y, scalar * z)
        for z in [-1, 1]:
            for x in [-1,1]:
                for y in [-1,1]:
                    glVertex3f(scalar * x, scalar * y, scalar * z)
        for y in [-1, 1]:
            for z in [-1,1]:
                for x in [-1,1]:
                    glVertex3f(scalar * x, scalar * y, scalar * z)
        glEnd()

        self.pointsMode() 
        self.meshMode()

        # draw background in the distance
        glLoadIdentity()
        glBegin(GL_QUADS)
        glColor3f(30/256, 30/256, 30/256)
        glVertex3f(-30, -23, -49.5)
        glVertex3f(30, -23, -49.5)
        glColor3f(100/256, 100/256, 100/256)
        glVertex3f(30, 23, -49.5)
        glVertex3f(-30, 23, -49.5)
        glEnd()

        # Threshold color
        glColor3f(1,1,0)
        glWindowPos2f(10, 10)
        for ch in 'Threshold: %0.2f' % self.worldThreshold:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(ch))

    def pointsMode(self):
        # Points mode
        if self.displayMode is self.DISPLAYMODE_POINTS:
            prev = (0, 0, 0)
            offset = int(self.worldSize/2)
            for x in range(self.worldSize):
                for y in range(self.worldSize):
                    for z in range(self.worldSize):
                        glTranslatef(x - offset - prev[0], y - offset - prev[1], z - offset - prev[2])
                        # use threshold for black/white coloring
                        if self.world[x][y][z] > self.worldThreshold:
                            
                            glColor3f(0.9, 0.9, 0.9)
                        else:
                            glColor3f(0, 0, 0)
                        gluSphere(self.sphere, 0.1, 8, 4)
                        prev = (x-offset,y-offset,z-offset)

    def meshMode(self):
        # Mesh mode 
        if self.displayMode is self.DISPLAYMODE_MESH:
            offset = int(self.worldSize/2)
            for x in range(self.worldSize-1):
                for y in range(self.worldSize-1):
                    for z in range(self.worldSize-1):
                        if self.polygons[x][y][z]:
                            glBegin(GL_POLYGON)
                            # glColor3f(x/self.worldSize,y/self.worldSize,z/self.worldSize)
                            glColor3f(x / self.worldSize, x / self.worldSize, x / self.worldSize)

                            for vertex in self.polygons[x][y][z]:
                                glVertex3f(x + vertex[0] - offset, y + vertex[1] - offset, z + vertex[2] - offset)
                            glEnd()

    def getWorldValues(self):
        """
        Generate random world
        """
        pNoiseSeed = random.random()
        for x in range(self.worldSize):
            for y in range(self.worldSize):
                for z in range(self.worldSize):
                    self.world[x][y][z] = snoise4(x / self.worldSize, y / self.worldSize, z / self.worldSize, pNoiseSeed)

        # normalize
        worldMax = np.max(self.world)
        worldMin = np.min(self.world)
        for x in range(self.worldSize):
            for y in range(self.worldSize):
                for z in range(self.worldSize):
                    self.world[x][y][z] = (self.world[x][y][z] - worldMin) / (worldMax - worldMin)


    def findPolygons(self):
        """
        Generates an array of polygons to plot across the world
        """
        for x in range(self.worldSize-1):
            for y in range(self.worldSize-1):
                for z in range(self.worldSize-1):

                    # creates edgeTable
                    edgeTable = [
                        self.world[x][y][z],
                        self.world[x + 1][y][z],
                        self.world[x + 1][y + 1][z],
                        self.world[x][y + 1][z],
                        self.world[x][y][z + 1],
                        self.world[x + 1][y][z + 1],
                        self.world[x + 1][y + 1][z + 1],
                        self.world[x][y + 1][z + 1]
                        ]
                    # print(edgeTable)
                    # print(self.world)

                    # define polygons
                    self.polygons[x][y][z] = marchingCubesPolygons(edgeTable, self.worldThreshold)