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
    glClearColor(0.1, 0.1, 0.1, 0.1) #kolor tła: RGB,przezroczystość
    glEnable(GL_DEPTH_TEST) #uruchamia głębokość - 3d 

def draw_segment(length):
    glPushMatrix()  #zapisuje macierz na stosie. Robimy push, zmieniamy cos i robimy pop. 
    glScalef(0.2, length, 0.2) #wymiary X,Y,Z prostokąta, rysujemy w "srodku"
    glutSolidCube(1.0)          #oryginalnie sześcian, rozciągniety przez glScalef
    glPopMatrix()   #sciąga ze stosu?

def draw_grid():
    grid_size = 10
    spacing = 1.0  # Odstępy między liniami siatki
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
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) #czyści tło
    glLoadIdentity()    #resetuje macierz transformacji

    gluLookAt(4, 4, 10, 0, 0, 0, 0, 1, 0) #4,4,10 - pozycja kamery, 0,0,0 - punkt na który kamera jest skierowana, 0,1,0 - wektor góra, 

    draw_grid()

    # Podstawa
    glPushMatrix()
    glTranslatef(0.0, 0.5, 0.0) #srodek 1 przegubu
    glColor3f(1.0, 0.0, 0.0)
    glRotatef(angle1, 0, 1, 0)
    draw_segment(1.0)

    # Ramię górne
    glTranslatef(0.0, 0.5, 0.0) #w gore o 0.5 od aktualnego polozenia
    glRotatef(angle2, 0, 0, 1)
    glTranslatef(0.0, 0.5, 0.0)
    glColor3f(0.0, 1.0, 0.0)
    draw_segment(1.0)

    # Przedramię
    glTranslatef(0.0, 0.5, 0.0)
    glRotatef(angle3, 0, 0, 1)
    glTranslatef(0.0, 0.5, 0.0)
    glColor3f(0.0, 0.0, 1.0)
    draw_segment(1.0)

    #nadgarstek
    glTranslatef(0.0, 0.5, 0.0)
    glRotatef(angle4, angle5, angle6, 1)
    glTranslatef(0.0, 0.25, 0.0)
    glColor3f(0.0, 1.0, 1.0)
    draw_segment(0.5)

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
    glutInit(sys.argv) #incicjalizuje glut
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH) # tryb renderowania GLUT_DOUBLE – podwójny bufor (w celu uzyskania płynnej animacji).GLUT_RGB – używa modelu kolorów RGB.GLUT_DEPTH – używa bufora głębokości (potrzebny do rysowania 3D).
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"3D Robot Arm - OpenGL")
    init() #init() – Inicjalizuje ustawienia OpenGL.
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutMainLoop()

if __name__ == "__main__":
    main()
