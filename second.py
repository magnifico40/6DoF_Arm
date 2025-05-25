

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import sys


class Kinematics:
    def __init__(self):
        self.angles = np.array([0, 0, 0, 0, 0, 0])
        # DH
        self.a_values = np.array([0, 1, 1, 0, 0, 0, 0.5])
        self.d_values = np.array([1, 0, 0, 0, 0, 0, 0])
        self.alfa_values = np.array(np.radians([-90, 0, 0, -90, 90, 0, 0]))
        angles_offset = np.array([0, -90, 0, 0, 0, 0, 0])
        self.theta_values = np.radians(np.append(self.angles, [0]) + angles_offset)
        self.T = np.zeros(7)
        self.Joints = np.zeros(7)
        self.JointsXYZ = np.zeros(7)

    def set_angles(self, angles):
        self.angles = angles

    def dh_matrix(self):
        # notation same as in yt vid
        self.T = np.zeros(7)
        for i in enumerate(self.T):
            ct, st = np.cos(self.theta_values[i]), np.sin(self.theta_values[i])
            ca, sa = np.cos(self.alfa_values[i]), np.sin(self.alfa_values[i])
            self.T[i] = np.array([
                [ct,    -st * ca,   st * sa,    self.a_values[i] * ct],
                [st,    ct * ca,    -ct * sa,   self.a_values[i] * st],
                [0,     sa,         ca,         self.d_values[i]],
                [0,     0,          0,          1]
                ])
    def calculate_xyz(self):
        self.dh_matrix()
        for i in enumerate(self.T):
            if i != 0:
                self.Joints[i] = self.Joints[i-1] @ self.T[i]
            else:
                self.Joints[i] = self.T[i]

            self.JointsXYZ[i] = self.Joints[i][:3, 3]
        R = self.Joints[6][:3, :3]
        roll = np.degrees(np.atan2(R[2, 1], R[2, 2]))  # (r32, r33)
        pitch = np.degrees(np.atan2(-R[2, 0], np.sqrt(R[2, 1] ** 2 + R[2, 2] ** 2)))
        yaw = np.degrees(np.atan2(R[1, 0], R[0, 0]))
        return self.JointsXYZ + [roll, pitch, yaw]



class Robot:
    def __init__(self):
        self.angles = np.array([0, 0, 0, 0, 0, 0])
        self.angle1 = 0
        self.angle2 = 0
        self.angle3 = 0
        self.angle4 = 0
        self.angle5 = 0
        self.angle6 = 0
        self.step_size = 3
        self.radius = 0.5
        self.quadric = gluNewQuadric()
        self.segLen = np.array([5, 5, 5, 2.5])

    def get_angles(self):
        return self.angles

    def reset(self):
        self.angles = np.zeros(6)

    def draw_segment(self, length):
        glPushMatrix()
        r = self.radius
        slices = 20
        stacks = 20
        glTranslatef(0, -length/2, 0)
        glRotatef(-90, 1, 0, 0)

        # Dolna półkula
        glPushMatrix()
        gluSphere(self.quadric, r, slices, stacks)
        glPopMatrix()

        # Walec
        glPushMatrix()
        gluCylinder(self.quadric, r, r, length, slices, 1)
        glPopMatrix()

        # Górna półkula
        glPushMatrix()
        glTranslatef(0, 0, length)
        gluSphere(self.quadric, r, slices, stacks)
        glPopMatrix()

        glPopMatrix()

    def draw_gripper(self, spacing=0.06):
        glPushMatrix()

        finger_length = 0.3
        finger_width = 0.05

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

    def draw(self):
        # Podstawa
        glPushMatrix()
        glTranslatef(0.0, self.segLen[0]/2, 0.0)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [1.0, 0.5, 0.0, 1.0])
        glRotatef(self.angle1, 0, 1, 0)
        glPushMatrix()
        glTranslatef(0.0, -self.segLen[0] / 2, 0.0)
        self.draw_axes()
        glPopMatrix()
        self.draw_segment(self.segLen[0])

        # Ramię
        glTranslatef(0.0, self.segLen[1]/2, 0.0)
        glRotatef(self.angle2, 0, 0, 1)
        glTranslatef(0.0, self.segLen[1]/2, 0.0)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.45, 0.65, 0.0, 1.0])
        glPushMatrix()
        glTranslatef(0.0, -self.segLen[1] / 2, 0.0)
        self.draw_axes()
        glPopMatrix()
        self.draw_segment(self.segLen[1])

        # Przedramię
        glTranslatef(0.0, self.segLen[2]/2, 0.0)
        glRotatef(self.angle3, 0, 0, 1)
        glTranslatef(0.0, self.segLen[2]/2, 0.0)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.6, 0.0, 0.6, 1.0])
        glPushMatrix()
        glTranslatef(0.0, -self.segLen[2] / 2, 0.0)
        self.draw_axes()
        glPopMatrix()
        self.draw_segment(self.segLen[2])

        # Nadgarstek
        glTranslatef(0.0, self.segLen[3], 0.0)
        glRotatef(self.angle4, 1, 0, 0)
        glRotatef(self.angle5, 0, 1, 0)
        glRotatef(self.angle6, 0, 0, 1)
        glTranslatef(0.0, self.segLen[3]/2, 0.0)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.0, 0.6, 0.6, 1.0])
        glPushMatrix()
        glTranslatef(0.0, -self.segLen[3]/2, 0.0)
        self.draw_axes()
        glPopMatrix()
        self.draw_segment(self.segLen[3])

        glPopMatrix()

    def draw_axes(self, length=2):
        glLineWidth(2.0)

        # Wyłącz oświetlenie na czas rysowania osi
        glDisable(GL_LIGHTING)

        glBegin(GL_LINES)

        # X - red
        glColor3f(1, 0, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(length, 0, 0)

        # Y - green
        glColor3f(0, 1, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, length, 0)

        # Z - blue
        glColor3f(0, 0, 1)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, length)

        glEnd()

        # Włącz z powrotem oświetlenie
        glEnable(GL_LIGHTING)


class Scene:
    def __init__(self):
        self.robot = Robot()
        self.calc = Kinematics()

    def init_gl(self):
        glClearColor(0.1, 0.15, 0.3, 0.7)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_NORMALIZE)

        glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 0.0, 30.0, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 50.0)

    def draw_grid(self):
        glDisable(GL_LIGHTING)
        grid_size = 20
        spacing = 3
        glPushMatrix()
        glColor3f(0.4, 0.4, 0.4)
        for i in range(-grid_size, grid_size + 1):
            glBegin(GL_LINES)
            glVertex3f(i * spacing, 0, -grid_size * spacing)
            glVertex3f(i * spacing, 0, grid_size * spacing)
            glEnd()
            glBegin(GL_LINES)
            glVertex3f(-grid_size * spacing, 0, i * spacing)
            glVertex3f(grid_size * spacing, 0, i * spacing)
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
        glEnable(GL_LIGHTING)

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluLookAt(-30, 30, 30, 0, 10, 0, 0, 1, 0)

        self.draw_grid()
        self.robot.draw()
        self.calc.set_angles(self.robot.get_angles())
        text1 = self.robot.get_angles()
        text2 = self.calc.calculate_xyz()

        # Napisy z kątami
        angles = [
            f"Angle 1: {self.robot.angle1}",
            f"Angle 2: {self.robot.angle2}",
            f"Angle 3: {self.robot.angle3}",
            f"Angle 4: {self.robot.angle4}",
            f"Angle 5: {self.robot.angle5}",
            f"Angle 6: {self.robot.angle6}",
        ]

        for i, angle_text in enumerate(angles):
            self.draw_text(10, 560 - i * 20, angle_text)

        glutSwapBuffers()

    def draw_text(self, x, y, text):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 800, 0, 600)  # Okno 800x600
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_LIGHTING)
        glColor3f(1.0, 1.0, 1.0)
        glRasterPos2f(x, y)
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        glEnable(GL_LIGHTING)

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def reshape(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / float(height), 1, 100)
        glMatrixMode(GL_MODELVIEW)

    def keyboard(self, key, x, y):
        r = self.robot
        if key == b'q':
            r.angle1 += r.step_size
        elif key == b'a':
            r.angle1 -= r.step_size
        elif key == b'w':
            r.angle2 += r.step_size
        elif key == b's':
            r.angle2 -= r.step_size
        elif key == b'e':
            r.angle3 += r.step_size
        elif key == b'd':
            r.angle3 -= r.step_size
        elif key == b'r':
            r.angle4 += r.step_size
        elif key == b'f':
            r.angle4 -= r.step_size
        elif key == b't':
            r.angle5 += r.step_size
        elif key == b'g':
            r.angle5 -= r.step_size
        elif key == b'y':
            r.angle6 += r.step_size
        elif key == b'h':
            r.angle6 -= r.step_size
        elif key == b'x':
            r.reset()
        elif key == b'z':
            sys.exit()
        glutPostRedisplay()


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Robot Arm Scene")

    current_scene = Scene()
    current_scene.init_gl()

    glutDisplayFunc(current_scene.display)
    glutReshapeFunc(current_scene.reshape)
    glutKeyboardFunc(current_scene.keyboard)
    glutMainLoop()


if __name__ == "__main__":
    main()