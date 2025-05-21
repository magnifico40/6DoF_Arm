from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys

angle1 = 0
angle2 = 0
angle3 = 0

def init():
    glClearColor(0.1, 0.1, 0.1, 0.1)
    glEnable(GL_DEPTH_TEST)
def drawSegment(length):
    glColor3f(0.7, 0.7, 0.7)
    glPushMatrix()
    glScalef(0.2, length, 0.2)
    glutSolidCube(1.0)
    glPopMatrix()

def drawGrid():
    spacing = 1
    gridSize = 20
    glPushMatrix()
    glColor3f(0.1, 0.1, 0.1)
    for i in range (-gridSize, gridSize + 1):
        glBegin(GL_LINES)
        glVertex




