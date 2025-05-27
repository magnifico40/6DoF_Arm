from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import numpy as np

class RobotArmApp:
    def __init__(self):
        self.step_size = 2
        self.quadric = gluNewQuadric()
        self.robot = RobotArm()

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

    def draw_text(self, x, y, text):
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

    def draw_grid(self):
        glDisable(GL_LIGHTING)
        grid_size = 25
        spacing = 0.4
        arrow_size = 0.3
        arrow_pos = 5 * spacing  # <--- pozycja grotów osi bliżej środka

        glPushMatrix()

        # Szara siatka
        glColor3f(0.8, 0.8, 0.8)
        glLineWidth(1.0)
        for i in range(-grid_size, grid_size + 1):
            if i != 0:
                glBegin(GL_LINES)
                glVertex3f(i * spacing, -grid_size * spacing, 0)
                glVertex3f(i * spacing, grid_size * spacing, 0)
                glEnd()

                glBegin(GL_LINES)
                glVertex3f(-grid_size * spacing, i * spacing, 0)
                glVertex3f(grid_size * spacing, i * spacing, 0)
                glEnd()

        glLineWidth(3.0)

        # Oś Y (niebieska)
        glColor3f(0.0, 0.0, 1.0)
        glBegin(GL_LINES)
        glVertex3f(0, -grid_size * spacing, 0)
        glVertex3f(0, grid_size * spacing, 0)
        glEnd()
        # Strzałka Y
        glBegin(GL_LINES)
        glVertex3f(0, arrow_pos, 0)
        glVertex3f(arrow_size, arrow_pos - arrow_size, 0)
        glVertex3f(0, arrow_pos, 0)
        glVertex3f(-arrow_size, arrow_pos - arrow_size, 0)
        glEnd()

        # Oś X (zielona)
        glColor3f(0.0, 1.0, 0.0)
        glBegin(GL_LINES)
        glVertex3f(-grid_size * spacing, 0, 0)
        glVertex3f(grid_size * spacing, 0, 0)
        glEnd()
        # Strzałka X
        glBegin(GL_LINES)
        glVertex3f(arrow_pos, 0, 0)
        glVertex3f(arrow_pos - arrow_size, arrow_size, 0)
        glVertex3f(arrow_pos, 0, 0)
        glVertex3f(arrow_pos - arrow_size, -arrow_size, 0)
        glEnd()

        # Oś Z (czerwona)
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, -grid_size * spacing)
        glVertex3f(0, 0, grid_size * spacing)
        glEnd()

        glPopMatrix()
        glEnable(GL_LIGHTING)

    def keyboard(self, key, x, y):
        if key == b'q':
            self.robot.angles[0] += self.step_size
        elif key == b'a':
            self.robot.angles[0] -= self.step_size
        elif key == b'w':
            self.robot.angles[1] += self.step_size
        elif key == b's':
            self.robot.angles[1] -= self.step_size
        elif key == b'e':
            self.robot.angles[2] += self.step_size
        elif key == b'd':
            self.robot.angles[2] -= self.step_size
        elif key == b'r':
            self.robot.angles[3] += self.step_size
        elif key == b'f':
            self.robot.angles[3] -= self.step_size
        elif key == b't':
            self.robot.angles[4] += self.step_size
        elif key == b'g':
            self.robot.angles[4] -= self.step_size
        elif key == b'y':
            self.robot.angles[5] += self.step_size
        elif key == b'h':
            self.robot.angles[5] -= self.step_size
        elif key == b'x':
            self.robot.reset_angles()

        '''
        angle1 = angle1 % 360
        angle2 = angle2 % 360
        angle3 = angle3 % 360
        angle4 = angle4 % 360
        angle5 = angle5 % 360
        angle6 = angle6 % 360
        '''
        glutPostRedisplay()

    def reshape(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / float(height), 1, 50)
        glMatrixMode(GL_MODELVIEW)

    def display(self):
        angles = self.robot.get_angles()
        # theta_table = get_theta_table()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        gluLookAt(5, 0, 8, 0, 0, 0, 0, 0, 1)

        self.draw_grid()
        # Podstawa
        glPushMatrix()
        glTranslatef(0.0, 0.0, 0.5)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [1.0, 0.5, 0.0, 1.0])
        glRotatef(angles[0], 0, 0, 1)
        self.draw_segment(1.0)
        glTranslatef(0.0, 0.0, 0.5)

        # Ramię górne
        glRotatef(angles[1], 1, 0, 0)
        glTranslatef(0.0, 0.0, 0.5)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.45, 0.65, 0.0, 1.0])
        self.draw_segment(1.0)
        glTranslatef(0.0, 0.0, 0.5)

        # nadgarstek
        glRotatef(angles[2], 1, 0, 0)
        glRotatef(90, 1, 0, 0)
        glRotatef(angles[3], 0, 0, 1)  # roll
        glTranslatef(0.0, 0.0, 0.25)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.6, 0.6, 0.6, 1.0])
        self.draw_segment(0.5)
        glTranslatef(0.0, 0.0, 0.25)

        glRotatef(angles[4], 1, 0, 0)
        glRotatef(angles[5], 0, 0, 1)
        glTranslatef(0.0, 0.0, 0.125)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.3, 0.6, 0.6, 1.0])
        self.draw_segment(0.25)
        glTranslatef(0.0, 0.0, 0.125)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [1, 0, 0, 1.0])
        self.draw_gripper()
        glPopMatrix()

        self.draw_text(10, 570, f"angle1 (base): {angles[0]}")
        self.draw_text(10, 545, f"angle2 (upper arm): {angles[1]}")
        self.draw_text(10, 520, f"angle3 (forearm): {angles[2]}")
        self.draw_text(10, 495, f"angle4 (wrist x): {angles[3]}")
        self.draw_text(10, 470, f"angle5 (wrist y): {angles[4]}")
        self.draw_text(10, 445, f"angle6 (wrist z): {angles[5]}")

        T = np.array(self.robot.get_dh_arrays())
        '''
        T1 = dh_matrix(theta_table[0], alpha_table[0], d_table[0], a_table[0])
        T2 = dh_matrix(theta_table[1], alpha_table[1], d_table[1], a_table[1])
        T3 = dh_matrix(theta_table[2], alpha_table[2], d_table[2], a_table[2])
        T4 = dh_matrix(theta_table[3], alpha_table[3], d_table[3], a_table[3])
        T5 = dh_matrix(theta_table[4], alpha_table[4], d_table[4], a_table[4])
        T6 = dh_matrix(theta_table[5], alpha_table[5], d_table[5], a_table[5])
        '''

        J = np.array(np.zeros(6), dtype=object)
        J[0] = T[0]
        J[1] = J[0] @ T[1]
        J[2] = J[1] @ T[2]
        J[3] = J[2] @ T[3]
        J[4] = J[3] @ T[4]
        J[5] = J[4] @ T[5]
        '''
        FirstJoint = T1
        SecondJoint = FirstJoint @ T2
        ThirdJoint = SecondJoint @ T3
        FourthJoint = ThirdJoint @ T4
        FifthJoint = FourthJoint @ T5
        SixthJoint = FifthJoint @ T6
        '''

        Jxyz = np.array(np.zeros(6), dtype=object)
        Jxyz[0] = J[0][:3, 3]
        Jxyz[1] = J[1][:3, 3]
        Jxyz[2] = J[2][:3, 3]
        Jxyz[3] = J[3][:3, 3]
        Jxyz[4] = J[4][:3, 3]
        Jxyz[5] = J[5][:3, 3]
        R = J[5][:3, :3]

        # y,x
        roll = np.degrees(np.atan2(R[2, 1], R[2, 2])) + 135  # (r32, r33)
        pitch = np.degrees(np.atan2(-R[2, 0], np.sqrt(R[2, 1] ** 2 + R[2, 2] ** 2)))
        yaw = np.degrees(np.atan2(R[1, 0], R[0, 0])) - 135

        '''
        # Współrzędne przegubów
        FirstJointXYZ = FirstJoint[:3, 3]
        SecondJointXYZ = SecondJoint[:3, 3]
        ThirdJointXYZ = ThirdJoint[:3, 3]
        FourthJointXYZ = FourthJoint[:3, 3]
        FifthJointXYZ = FifthJoint[:3, 3]
        SixthJointXYZ = SixthJoint[:3, 3]
        R = SixthJoint[:3, :3]
        '''

        self.draw_text(600, 570, f"Joint1: {Jxyz[0][0]:.2f}, {Jxyz[0][1]:.2f}, {Jxyz[0][2]:.2f}")
        self.draw_text(600, 545, f"Joint2: {Jxyz[1][0]:.2f}, {Jxyz[1][1]:.2f}, {Jxyz[1][2]:.2f}")
        self.draw_text(600, 520, f"Joint3: {Jxyz[2][0]:.2f}, {Jxyz[2][1]:.2f}, {Jxyz[2][2]:.2f}")
        self.draw_text(600, 495, f"Gripper: {Jxyz[5][0]:.2f}, {Jxyz[5][1]:.2f}, {Jxyz[5][2] + 2.0:.2f} ")
        self.draw_text(600, 470, f"Y/P/R: {yaw:.2f}, {pitch:.2f}, {roll:.2f}")

        glutSwapBuffers()

    def draw_segment(self, length):
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
        gluSphere(self.quadric, radius, slices, stacks)
        glPopMatrix()

        # Walec
        glPushMatrix()
        glTranslatef(0, 0, 0)
        gluCylinder(self.quadric, radius, radius, length, slices, 1)
        glPopMatrix()

        # Górna półkula
        glPushMatrix()
        glTranslatef(0, 0, length)
        gluSphere(self.quadric, radius, slices, stacks)
        glPopMatrix()

        glPopMatrix()

    def draw_gripper(self):
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


class RobotArm:
    def __init__(self):
        self.angles = np.zeros(6)
        self.a_val = np.array([0, 1, 0, 0, 0, 0])
        self.d_val = np.array([1, 0, 0, 0.5, 0, 0.25])
        self.alpha_val = np.array(np.radians([-90, 0, -90, 90, -90, 0]))
        theta_increments = np.radians([90, 90, 0, 0, 0, 0])
        self.theta_val = np.radians(self.angles) + theta_increments
        self.DH = [0, 0, 0, 0, 0, 0]

    def get_angles(self):
        return self.angles

    def get_dh_arrays(self):
        self.dh_matrix()
        return self.DH

    def dh_matrix(self):
        # notation same as in yt vid
        for i in range(6):
            ct, st = np.cos(self.theta_val[i]), np.sin(self.theta_val[i])
            ca, sa = np.cos(self.alpha_val[i]), np.sin(self.alpha_val[i])

            self.DH[i] = [
                [ct, -st * ca, st * sa, self.a_val[i] * ct],
                [st, ct * ca, -ct * sa, self.a_val[i] * st],
                [0, sa, ca, self.d_val[i]],
                [0, 0, 0, 1]
            ]

    def reset_angles(self):
        self.angles = np.zeros(6)


'''
    def get_theta_table(self):
        theta_deg = [angle1 + 90, angle2 + 90, angle3, angle4, angle5, angle6]
        return np.radians(theta_deg)
'''


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 600)
    glutCreateWindow(b"3D Robot Arm - OpenGL")
    raa = RobotArmApp()
    glutDisplayFunc(raa.display)
    glutReshapeFunc(raa.reshape)
    glutKeyboardFunc(raa.keyboard)
    glutMainLoop()


if __name__ == "__main__":
    main()
