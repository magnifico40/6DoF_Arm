"""

          Z (w górę)
           ↑
           |
           |
           O--------→ Y (w lewo)
          /
         /
        X (do przodu, w stronę obserwatora)



"""





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

"""
# Denavit-Hartenberg
a1, a2, a3, a4, a5, a6 = 0, 1, 1, 1, 0, 0
d1, d2, d3, d4, d5, d6 = 1, 0, 0, 0, 0, 0

theta_deg = [angle1, angle2 - 90, angle3 + 180, angle4] #fill in also in display function
theta_table = np.radians(theta_deg)

alpha_deg = [-90, 0, 90, -90]
alpha_table = np.radians(alpha_deg)

d_table = [d1, 0, 0, 0]
a_table = [0, a2, a3, a4]
"""
a_table = [0, 1, 1, 0, 0, 0, 0.5]
d_table = [1, 0, 0, 0, 0, 0, 0]
alpha_table = np.radians([-90, 0, 0, -90, 90, 0, -0])

def get_theta_table():
    theta_deg = [angle1, angle2 - 90, angle3 , angle4, angle5, angle6, 0]
    return np.radians(theta_deg)


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

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    light_position = [5.0, 5.0, 10.0, 1.0]  # [x, y, z, 1.0] – światło punktowe
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])

    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.8, 0.5, 0.2, 1.0])
    glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 50.0)

    glEnable(GL_NORMALIZE)

def draw_text(x, y, text):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 800, 0, 600)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glColor3f(0.0, 0.0, 0.0)

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

    glTranslatef(0, 0, -length / 2.0)
    glRotatef(-90, 0, 0, 1)  # walec wzdłuż osi Y

    # Rysujemy walec wzdłuż osi Z
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
    glDisable(GL_LIGHTING) #wylacza oswietlenie na czas rysowania siatki
    grid_size = 25
    spacing = 0.4
    glPushMatrix()

    # Szara siatka
    glColor3f(0.8, 0.8, 0.8)
    glLineWidth(1.0)
    for i in range(-grid_size, grid_size + 1):
        if i!=0:
            glBegin(GL_LINES)
            glVertex3f(i * spacing, -grid_size * spacing, 0)
            glVertex3f(i * spacing, grid_size * spacing, 0)
            glEnd()

            glBegin(GL_LINES)
            glVertex3f(-grid_size * spacing, i * spacing, 0)
            glVertex3f(grid_size * spacing, i * spacing, 0)
            glEnd()

    glLineWidth(3.0)
    # Zielona oś X = 0
    glColor3f(0.0, 1.0, 0.0)
    glBegin(GL_LINES)
    glVertex3f(0, -grid_size * spacing, 0)
    glVertex3f(0, grid_size * spacing, 0)
    glEnd()

    # Niebieska oś Y = 0
    glColor3f(0.0, 0.0, 1.0)
    glBegin(GL_LINES)
    glVertex3f(-grid_size * spacing, 0, 0)
    glVertex3f(grid_size * spacing, 0, 0)
    glEnd()

    # Czerwona oś Z = 0
    glColor3f(1.0, 0.0, 0.0)
    glBegin(GL_LINES)
    glVertex3f(0, 0, -grid_size * spacing)
    glVertex3f(0, 0, grid_size * spacing)
    glEnd()

    glPopMatrix()
    glEnable(GL_LIGHTING) #przywraca oswietlenie na czas rysowania siatki


def draw_gripper():
    glPushMatrix()

    finger_length = 0.3
    finger_width = 0.05
    spacing = 0.06  # odstęp między palcami

    glColor3f(0.0, 0.0, 0.0)

    # Lewy palec
    glPushMatrix()
    glTranslatef(-spacing, 0.0, 0.0)
    glScalef(finger_width, finger_width, finger_length)
    glutSolidCube(1.0)
    glPopMatrix()

    # Prawy palec
    glPushMatrix()
    glTranslatef(spacing, 0.0, 0.0)
    glScalef(finger_width, finger_width, finger_length)
    glutSolidCube(1.0)
    glPopMatrix()

    glPopMatrix()
def display():
    theta_table = get_theta_table()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    gluLookAt(5, 0, 8, 0, 0, 0, 0, 0, 1)

    draw_grid()
    # Podstawa
    glPushMatrix()
    glTranslatef(0.0, 0.0, 0.5)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [1.0, 0.5, 0.0, 1.0])
    glRotatef(angle1, 0, 0, 1)
    draw_segment(1.0)
    # Ramię górne
    glTranslatef(0.0, 0.0, 0.5)
    glRotatef(angle2, 0, 1, 0)
    glTranslatef(0.0, 0.0, 0.5)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.45, 0.65, 0.0, 1.0])
    draw_segment(1.0)
    # Przedramię
    glTranslatef(0.0, 0.0, 0.5)
    glRotatef(angle3, 0, 1, 0)
    glTranslatef(0.0, 0.0, 0.5)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.6, 0.0, 0.6, 1.0])
    draw_segment(1.0)
    #nadgarstek
    glTranslatef(0.0, 0.0, 0.5)
    glRotatef(angle4, 1, 0, 0)
    glRotatef(angle5, 0, 1, 0)
    glRotatef(angle6, 0, 0, 1)
    glTranslatef(0.0, 0.0, 0.25)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.0, 0.6, 0.6, 1.0])
    draw_segment(0.5)
    #chwytak
    glTranslatef(0.0, 0.0, 0.25)
    draw_gripper()
    glPopMatrix()

    draw_text(10, 570, f"angle1 (base): {angle1}")
    draw_text(10, 545, f"angle2 (upper arm): {angle2}")
    draw_text(10, 520, f"angle3 (forearm): {angle3}")
    draw_text(10, 495, f"angle4 (wrist x): {angle4}")
    draw_text(10, 470, f"angle5 (wrist y): {angle5}")
    draw_text(10, 445, f"angle6 (wrist z): {angle6}")

    T1 = dh_matrix(theta_table[0], alpha_table[0], d_table[0], a_table[0])
    T2 = dh_matrix(theta_table[1], alpha_table[1], d_table[1], a_table[1])
    T3 = dh_matrix(theta_table[2], alpha_table[2], d_table[2], a_table[2])
    T4 = dh_matrix(theta_table[3], alpha_table[3], d_table[3], a_table[3])
    T5 = dh_matrix(theta_table[4], alpha_table[4], d_table[4], a_table[4])
    T6 = dh_matrix(theta_table[5], alpha_table[5], d_table[5], a_table[5])
    T7 = dh_matrix(theta_table[6], alpha_table[6], d_table[6], a_table[6])

    FirstJoint = T1 
    SecondJoint = FirstJoint @ T2
    ThirdJoint = SecondJoint @ T3
    FourthJoint = ThirdJoint @ T4
    FifthJoint = FourthJoint @ T5
    SixthJoint = FifthJoint @ T6
    SeventhJoint = SixthJoint @ T7

    # Współrzędne przegubów
    FirstJointXYZ = FirstJoint[:3, 3]
    SecondJointXYZ = SecondJoint[:3, 3]
    ThirdJointXYZ = ThirdJoint[:3, 3]
    FourthJointXYZ = FourthJoint[:3, 3]
    FifthJointXYZ = FifthJoint[:3, 3]
    SixthJointXYZ = SixthJoint[:3, 3]
    SeventhJointXYZ = SeventhJoint[:3, 3]
    R = SeventhJoint[:3, :3]

    roll  = np.degrees(np.atan2(R[2,1], R[2,2]) )
    pitch = np.degrees(np.arcsin(-R[2,0])       )
    yaw   = np.degrees(np.atan2(R[1,0], R[0,0]) )

    draw_text(600, 570, f"Joint1: {FirstJointXYZ[0]:.2f}, {FirstJointXYZ[1]:.2f}, {FirstJointXYZ[2]:.2f}")
    draw_text(600, 545, f"Joint2: {SecondJointXYZ[0]:.2f}, {SecondJointXYZ[1]:.2f}, {SecondJointXYZ[2]:.2f}")
    draw_text(600, 520, f"Joint3: {ThirdJointXYZ[0]:.2f}, {ThirdJointXYZ[1]:.2f}, {ThirdJointXYZ[2]:.2f}")
    draw_text(600, 495, f"Gripper: {SeventhJointXYZ[0]:.2f}, {SeventhJointXYZ[1]:.2f}, {SeventhJointXYZ[2]:.2f}")
    draw_text(600, 470, f"Y/P/R: {yaw:.2f}, {pitch:.2f}, {roll:.2f}")

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
    angle1 = angle1 % 360
    angle2 = angle2 % 360
    angle3 = angle3 % 360
    angle4 = angle4 % 360
    angle5 = angle5 % 360
    angle6 = angle6 % 360
    glutPostRedisplay()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 600)
    glutCreateWindow(b"3D Robot Arm - OpenGL")
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutMainLoop()

if __name__ == "__main__":
    main()
