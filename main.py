import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Zmienne globalne do przechowywania kątów segmentów
angle1 = 0
angle2 = 0

def draw_arm():
    global angle1, angle2

    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    # Przesunięcie w lewo w celu centrowania rysowania
    glTranslatef(-0.5, -0.5, 0.0)

    # Pierwszy segment ramienia
    glPushMatrix()
    glRotatef(angle1, 0, 0, 1)
    glColor3f(1, 0, 0)  # Czerwony kolor
    glRectf(0.0, -0.05, 0.5, 0.05)

    # Drugi segment ramienia
    glTranslatef(0.5, 0.0, 0.0)
    glRotatef(angle2, 0, 0, 1)
    glColor3f(0, 0, 1)  # Niebieski kolor
    glRectf(0.0, -0.04, 0.4, 0.04)
    glPopMatrix()

    pygame.display.flip()  # Odświeżenie ekranu

def key_pressed(event):
    global angle1, angle2
    if event.key == K_a:
        angle1 += 5  # Zwiększ kąt pierwszego segmentu
    elif event.key == K_d:
        angle1 -= 5  # Zmniejsz kąt pierwszego segmentu
    elif event.key == K_w:
        angle2 += 5  # Zwiększ kąt drugiego segmentu
    elif event.key == K_s:
        angle2 -= 5  # Zmniejsz kąt drugiego segmentu
    elif event.key == K_ESCAPE:
        pygame.quit()  # Zakończ program

def main():
    pygame.init()
    
    # Ustawienia okna i OpenGL
    display = (600, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    
    gluOrtho2D(-1, 1, -1, 1)  # Ustawienia rzutowania 2D

    # Pętla główna
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == KEYDOWN:
                key_pressed(event)
        
        draw_arm()  # Rysowanie ramienia robota

    pygame.quit()

if __name__ == "__main__":
    main()
