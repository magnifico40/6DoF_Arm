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
step_size = 3
quadric = gluNewQuadric()


def init():
    glClearColor(1, 1, 1, 1)  # białe tło
    glEnable(GL_DEPTH_TEST)

    # Włączenie oświetlenia
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # Właściwości światła
    light_position = [5.0, 5.0, 10.0, 1.0]  # [x, y, z, 1.0] – światło punktowe
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])  # rozproszone (białe)
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])  # refleksy

    # Właściwości materiału
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.8, 0.5, 0.2, 1.0])  # kolor materiału
    glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])  # odbicia
    glMaterialf(GL_FRONT, GL_SHININESS, 50.0)  # połysk (0–128)

    glEnable(GL_NORMALIZE)


def draw_text(x, y, text):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 800, 0, 600)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glColor3f(0.0, 0.0, 0.0)  # Czarny kolor tekstu

    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_segment(length):
    glPushMatrix()

    radius = 0.1
    slices = 20
    stacks = 20

    # Rysujemy cały element pionowo (Y) — walec + półkule
    glTranslatef(0, -length / 2.0, 0)
    glRotatef(-90, 1, 0, 0)  # walec wzdłuż osi Y

    # Dolna półkula
    glPushMatrix()
    glTranslatef(0, 0, 0)
    gluSphere(quadric, radius, slices, stacks)
    glPopMatrix()

    # Walec
    glPushMatrix()
    glTranslatef(0, 0, 0)
    gluCylinder(quadric, radius, radius, length, slices, 1)
    glPopMatrix()

    # Górna półkula
    glPushMatrix()
    glTranslatef(0, 0, length)
    gluSphere(quadric, radius, slices, stacks)
    glPopMatrix()

    glPopMatrix()


def draw_grid():
    grid_size = 25
    spacing = 0.4  # Odstępy między liniami siatki
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
    glTranslatef(0.0, 0.5, 0.0) #srodek 1 przegubu
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [1.0, 0.5, 0.0, 1.0])
    glRotatef(angle1, 0, 1, 0)
    draw_segment(1.0)

    # Upper Arm
    glTranslatef(0.0, 0.5, 0.0) # 0.5 up
    glRotatef(angle2, 0, 0, 1)  #bending place
    glTranslatef(0.0, 0.5, 0.0)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.45, 0.65, 0.0, 1.0])
    draw_segment(1.0)

    # Forearm
    glTranslatef(0.0, 0.5, 0.0)
    glRotatef(angle3, 0, 0, 1)
    glTranslatef(0.0, 0.5, 0.0)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.6, 0.0, 0.6, 1.0])
    draw_segment(1.0)

    #wrist
    glTranslatef(0.0, 0.5, 0.0)
    glRotatef(angle4, 1, 0, 0)
    glRotatef(angle5, 0, 1, 0)
    glRotatef(angle6, 0, 0, 1)
    glTranslatef(0.0, 0.25, 0.0)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.0, 0.6, 0.6, 1.0])
    draw_segment(0.5)

    # Finger 1
    glPushMatrix()
    glTranslatef(-0.1, 0.25, 0.0) 
    glScalef(0.05, 0.2, 0.05)
    glColor3f(1.0, 1.0, 0.0)
    glutSolidCube(1.0)
    glPopMatrix()

    draw_text(10, 570, f"angle1 (base): {angle1}")
    draw_text(10, 545, f"angle2 (upper arm): {angle2}")
    draw_text(10, 520, f"angle3 (forearm): {angle3}")
    draw_text(10, 495, f"angle4 (wrist x): {angle4}")
    draw_text(10, 470, f"angle5 (wrist y): {angle5}")
    draw_text(10, 445, f"angle6 (wrist z): {angle6}")

    glutSwapBuffers()

def reshape(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width / float(height), 1, 50)
    glMatrixMode(GL_MODELVIEW)

def keyboard(key, x, y):
    global angle1, angle2, angle3, angle4, angle5, angle6
    if key == b'q': angle1 += step_size
    elif key == b'a': angle1 -= step_size
    elif key == b'w': angle2 += step_size
    elif key == b's': angle2 -= step_size
    elif key == b'e': angle3 += step_size
    elif key == b'd': angle3 -= step_size
    elif key == b'r': angle4 += step_size
    elif key == b'f': angle4 -= step_size
    elif key == b't': angle5 += step_size
    elif key == b'g': angle5 -= step_size
    elif key == b'y': angle6 += step_size
    elif key == b'h': angle6 -= step_size
    elif key == b'x': angle1 = angle2 = angle3 = angle4 = angle5 = angle6 = 0
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
