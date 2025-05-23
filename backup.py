from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import numpy as np

# Kąty przegubów
angle1 = 0
angle2 = 0
angle3 = 0
angle4 = 0
angle5 = 0
angle6 = 0
step_size = 3
quadric = gluNewQuadric()


#Denavit - Hartenberg
a1, a2, a3, a4, a5, a6 = 0, 1, 1, 1, 0, 0
d1, d2, d3, d4, d5, d6 = 1, 0, 0, 0, 0, 0

theta_deg = [angle1, angle2 - 90, angle3 + 180, angle4]
theta_table = np.radians(theta_deg)

alpha_deg = [-90, 0, 90, -90]
alpha_table = np.radians(alpha_deg)

d_table = [d1, 0, 0, 0]
a_table = [0, a2, a3, a4]

def dh_matrix(theta, alpha, d, a):
    #notation same as in yt vid
    ct, st = np.cos(theta), np.sin(theta)
    ca, sa = np.cos(alpha), np.sin(alpha)

    return np.array([
        [ct, -st*ca,  st*sa, a*ct],
        [st,  ct*ca, -ct*sa, a*st],
        [0,     sa,     ca,    d],
        [0,      0,      0,    1]
    ])



def init():
    glClearColor(1, 1, 1, 1)  
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
    # Rysowanie siatki w płaszczyźnie XZ
    glColor3f(0.2, 0.2, 0.2)  # Kolor linii siatki (ciemnoszary)
    for i in range(-grid_size, grid_size + 1):
        # Linie poziome (X)
        glBegin(GL_LINES) # rysowanie odcinkow
        glVertex3f(i * spacing, 0, -grid_size * spacing)
        glVertex3f(i * spacing, 0, grid_size * spacing)
        glEnd()
        
        # Linie pionowe (Z)
        glBegin(GL_LINES)
        glVertex3f(-grid_size * spacing, 0, i * spacing)
        glVertex3f(grid_size * spacing, 0, i * spacing)
        glEnd()

    glPopMatrix()


def display():
    #table update
    theta_deg = [angle1, angle2 - 90, angle3 + 180, angle4]
    theta_table = np.radians(theta_deg)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) #czyści tło
    glLoadIdentity()    #resetuje macierz transformacji

    gluLookAt(4, 4, 10, 0, 0, 0, 0, 1, 0) #4,4,10 - pozycja kamery, 0,0,0 - punkt na który kamera jest skierowana, 0,1,0 - wektor góra, 

    draw_grid()

    # Podstawa
    glPushMatrix()
    glTranslatef(0.0, 0.5, 0.0) #srodek 1 przegubu
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [1.0, 0.5, 0.0, 1.0])
    glRotatef(angle1, 0, 1, 0)
    draw_segment(1.0)

    # Ramię górne
    glTranslatef(0.0, 0.5, 0.0) #w gore o 0.5 od aktualnego polozenia
    glRotatef(angle2, 0, 0, 1)
    glTranslatef(0.0, 0.5, 0.0)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.45, 0.65, 0.0, 1.0])
    draw_segment(1.0)

    # Przedramię
    glTranslatef(0.0, 0.5, 0.0)
    glRotatef(angle3, 0, 0, 1)
    glTranslatef(0.0, 0.5, 0.0)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.6, 0.0, 0.6, 1.0])
    draw_segment(1.0)

    #nadgarstek
    glTranslatef(0.0, 0.5, 0.0)
    glRotatef(angle4, 1, 0, 0)
    glRotatef(angle5, 0, 1, 0)
    glRotatef(angle6, 0, 0, 1)
    glTranslatef(0.0, 0.25, 0.0)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.0, 0.6, 0.6, 1.0])
    draw_segment(0.5)

    glPopMatrix()

    draw_text(10, 570, f"angle1 (base): {angle1}")
    draw_text(10, 545, f"angle2 (upper arm): {angle2}")
    draw_text(10, 520, f"angle3 (forearm): {angle3}")
    draw_text(10, 495, f"angle4 (wrist x): {angle4}")
    draw_text(10, 470, f"angle5 (wrist y): {angle5}")
    draw_text(10, 445, f"angle6 (wrist z): {angle6}")


    
    #def dh_matrix(theta, alpha, d, a):
    T1 = dh_matrix(theta_table[0], alpha_table[0], d1, a1)
    T2 = dh_matrix(theta_table[1], alpha_table[1], d2, a2)
    T3 = dh_matrix(theta_table[2], alpha_table[2], d3, a3)
    T4 = dh_matrix(theta_table[3], alpha_table[3], d4, a4)
    FirstJoint = T1 @ T2
    SecondJoint = FirstJoint @ T3
    ThirdJoint = SecondJoint @ T4
    FirstJointXYZ = [FirstJoint[0, 3], FirstJoint[1,3], FirstJoint[2, 3] ]
    SecondJointXYZ = [SecondJoint[0, 3], SecondJoint[1,3], SecondJoint[2, 3] ]
    ThirdJointXYZ = [ThirdJoint[0, 3], ThirdJoint[1,3], ThirdJoint[2, 3] ]
    draw_text(300, 570, f"XYZ1: {FirstJointXYZ[0]:.2f}, {FirstJointXYZ[1]:.2f}, {FirstJointXYZ[2]:.2f}")
    draw_text(300, 545, f"XYZ2: {SecondJointXYZ[0]:.2f}, {SecondJointXYZ[1]:.2f}, {SecondJointXYZ[2]:.2f}")
    draw_text(300, 520, f"XYZ3: {ThirdJointXYZ[0]:.2f}, {ThirdJointXYZ[1]:.2f}, {ThirdJointXYZ[2]:.2f}")



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
    angle1 = degreesLimit(angle1) 
    angle2 = degreesLimit(angle2)
    angle3 = degreesLimit(angle3)
    angle4 = degreesLimit(angle4)
    angle5 = degreesLimit(angle5) 
    angle6 = degreesLimit(angle6) 
    glutPostRedisplay()

    

def degreesLimit(deg):
    return deg%360

def main():
    glutInit(sys.argv) #incicjalizuje glut
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