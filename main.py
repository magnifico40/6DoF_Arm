# Compatibility profile 
#older, simpler approach, limited possibilities

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys

# Kąty przegubów
angle1 = 0
angle2 = 0
angle3 = 0
angle4 = 0
angle5 = 0
angle6 = 0

def init():
    glClearColor(0.1, 0.1, 0.1, 0.1) #RGB, background
    glEnable(GL_DEPTH_TEST) 

def draw_segment(length):
    glPushMatrix()  #saves matrix on stack
    glScalef(0.2, length, 0.2) #scales length in X,Y,Z draawing in middle of rectangle
    glutSolidCube(1.0) #"original" cube
    glPopMatrix()   #takes from stack

def draw_grid():
    grid_size = 10
    spacing = 1.0  # grid spacing
    glPushMatrix()

    glColor3f(0.2, 0.2, 0.2)  # grey color
    for i in range(-grid_size, grid_size + 1):

        glBegin(GL_LINES)
        glVertex3f(i * spacing, 0, -grid_size * spacing)
        glVertex3f(i * spacing, 0, grid_size * spacing)
        glEnd()
        
        glBegin(GL_LINES)
        glVertex3f(-grid_size * spacing, 0, i * spacing)
        glVertex3f(grid_size * spacing, 0, i * spacing)
        glEnd()

    glPopMatrix()


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) #clears background
    glLoadIdentity()    

    gluLookAt(4, 4, 10, 0, 0, 0, 0, 1, 0) #4,4,10 - camera position , 0,0,0 - camera looking direction, 0,1,0 - "up" 

    draw_grid()

    # Base
    glPushMatrix()
    glTranslatef(0.0, 0.5, 0.0) #middle of 1 joint
    glColor3f(1.0, 0.0, 0.0)
    glRotatef(angle1, 0, 1, 0) #angle, x, y, z
    draw_segment(1.0)

    # Upper Arm
    glTranslatef(0.0, 0.5, 0.0) # 0.5 up
    glRotatef(angle2, 0, 0, 1)  #bending place
    glTranslatef(0.0, 0.5, 0.0)
    glColor3f(0.0, 1.0, 0.0)
    draw_segment(1.0)

    # Forearm
    glTranslatef(0.0, 0.5, 0.0)
    glRotatef(angle3, 0, 0, 1)
    glTranslatef(0.0, 0.5, 0.0)
    glColor3f(0.0, 0.0, 1.0)
    draw_segment(1.0)

    #wrist
    glTranslatef(0.0, 0.5, 0.0)
    glRotatef(angle6, 1, 0, 0)  
    glRotatef(angle5, 0, 1, 0)  
    glRotatef(angle4, 0, 0, 1)  
    glTranslatef(0.0, 0.25, 0.0)
    glColor3f(0.0, 1.0, 1.0)
    draw_segment(0.5)

    # Finger 1
    glPushMatrix()
    glTranslatef(-0.1, 0.25, 0.0) 
    glScalef(0.05, 0.2, 0.05)
    glColor3f(1.0, 1.0, 0.0)
    glutSolidCube(1.0)
    glPopMatrix()

    # Finger 2
    glPushMatrix()
    glTranslatef(0.1, 0.25, 0.0) 
    glScalef(0.05, 0.2, 0.05)
    glColor3f(1.0, 1.0, 0.0)
    glutSolidCube(1.0)
    glPopMatrix()

    glPopMatrix() 

    glutSwapBuffers()

def reshape(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width / float(height), 1, 50)
    glMatrixMode(GL_MODELVIEW)

def keyboard(key, x, y):
    global angle1, angle2, angle3, angle4, angle5, angle6
    if key == b'q': angle1 += 5
    elif key == b'a': angle1 -= 5
    elif key == b'w': angle2 += 5
    elif key == b's': angle2 -= 5
    elif key == b'e': angle3 += 5
    elif key == b'd': angle3 -= 5
    elif key == b'r': angle4 += 5
    elif key == b'f': angle4 -= 5
    elif key == b't': angle5 += 5
    elif key == b'g': angle5 -= 5
    elif key == b'y': angle6 += 5
    elif key == b'h': angle6 -= 5
    elif key == b'x': sys.exit()
    glutPostRedisplay()

def main():
    glutInit(sys.argv) 
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH) 
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"3D Robot Arm - OpenGL")
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutMainLoop()

if __name__ == "__main__":
    main()
