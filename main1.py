import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

angle1 = 0
angle2 = 0

def draw_arm():
    global angle1, angle2

    glClear(GL_COLOR_BUFFER_BIT) #czyszczenie sceny przed rysowaniem
    glLoadIdentity() #zerowanie macierzy

    glTranslatef(-0.5, -0.5, 0) #przesuwa układ współrzędnych

    glPushMatrix() #zapisuje macierz na stosie
    glRotatef(angle1, 0, 0, 1) #obraca wzg OZ o angle1
    glColor3f(1, 0, 0) #kolor RGB
    glRectf(0, -0.05, 0.5, 0.05) #wsp. rogów prostokąta

    glTranslatef(0.5, 0.0, 0.0)
    glRotatef(angle2, 0, 0, 1) #obraca wzg OZ o angle1
    glColor3f(1, 0, 0) #kolor RGB
    glRectf(0, -0.05, 0.5, 0.05) #wsp. rogów prostokąta
    glPopMatrix() #Przywraca macierz modelowania ze szczytu stosu.


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
