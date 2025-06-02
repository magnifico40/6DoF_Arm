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
            self.robot.reset_state()

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
        segmentLen = self.robot.get_segments_len()
        # theta_table = get_theta_table()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        gluLookAt(5, 1, 6, 0, 0, 0, 0, 0, 1)

        self.draw_grid()
        # Podstawa
        glPushMatrix()
        glTranslatef(0.0, 0.0, segmentLen[0]/2)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [1.0, 0.5, 0.0, 1.0])
        glRotatef(angles[0], 0, 0, 1)
        self.draw_segment(segmentLen[0])
        glTranslatef(0.0, 0.0, segmentLen[0]/2)

        # Ramię górne
        glRotatef(angles[1], 1, 0, 0)
        glTranslatef(0.0, 0.0, segmentLen[1]/2)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.45, 0.65, 0.0, 1.0])
        self.draw_segment(segmentLen[1])
        glTranslatef(0.0, 0.0, segmentLen[1]/2)

        # nadgarstek
        glRotatef(angles[2], 1, 0, 0)
        glRotatef(-90, 1, 0, 0)
        glRotatef(angles[3], 0, 0, 1)  # roll
        glTranslatef(0.0, 0.0, segmentLen[2]/2)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.6, 0.6, 0.6, 1.0])
        self.draw_segment(segmentLen[2])
        glTranslatef(0.0, 0.0, segmentLen[2]/2)

        glRotatef(angles[4], 1, 0, 0)
        glRotatef(angles[5], 0, 0, 1)
        glTranslatef(0.0, 0.0, segmentLen[3]/2)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.3, 0.6, 0.6, 1.0])
        self.draw_segment(segmentLen[3])
        glTranslatef(0.0, 0.0, segmentLen[3]/2)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [1, 0, 0, 1.0])
        self.draw_gripper()
        glPopMatrix()

        self.draw_text(10, 570, f"angle1 (base): {angles[0]}")
        self.draw_text(10, 545, f"angle2 (upper arm): {angles[1]}")
        self.draw_text(10, 520, f"angle3 (forearm): {angles[2]}")
        self.draw_text(10, 495, f"angle4 (wrist x): {angles[3]}")
        self.draw_text(10, 470, f"angle5 (wrist y): {angles[4]}")
        self.draw_text(10, 445, f"angle6 (wrist z): {angles[5]}")

        xyz, ypr = self.robot.get_joints_xyz_ypr()

        self.draw_text(600, 570, f"Joint1: {xyz[0][0]:.2f}, {xyz[0][1]:.2f}, {xyz[0][2]:.2f}")
        self.draw_text(600, 545, f"Joint2: {xyz[1][0]:.2f}, {xyz[1][1]:.2f}, {xyz[1][2]:.2f}")
        self.draw_text(600, 520, f"Joint3: {xyz[3][0]:.2f}, {xyz[3][1]:.2f}, {xyz[3][2]:.2f}")
        self.draw_text(600, 495, f"Gripper: {xyz[5][0]:.2f}, {xyz[5][1]:.2f}, {xyz[5][2]:.2f} ")
        self.draw_text(600, 470, f"Y/P/R: {ypr[0]:.2f}, {ypr[1]:.2f}, {ypr[2]:.2f}")

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
        self.segmentLen = np.array([0.5, 1, 0.5, 0.25])
        self.a_val = np.array([0, self.segmentLen[1], 0, 0, 0, 0])
        self.d_val = np.array([self.segmentLen[0], 0, 0, self.segmentLen[2], 0, self.segmentLen[3]])
        self.alpha_val = np.array(np.radians([90, 0, 90, -90, 90, 0]))
        self.theta_increments = np.radians([0, 90, 0, 0, 0, 0])
        self.theta_val = np.radians(self.angles) + self.theta_increments
        self.T = np.empty(6, dtype=object)
        self.J = np.empty(6, dtype=object)
        self.Jxyz = np.empty(6, dtype=object)
        self.ypr = np.zeros(3)
        self.JointLimits = np.array([[-180, 180], [-180, 180], [-180, 180], [-180, 180], [-180, 180], [-180, 180]])

    def set_angle(self, index, value):
        self.angles[index] = value

    def get_angles(self):
        return self.angles

    def get_segments_len(self):
        return self.segmentLen

    def get_joints_limits(self):
        return self.JointLimits

    def get_gripper_xyz_ypr(self):
        Jxyz, ypr = self.get_joints_xyz_ypr()
        return Jxyz[5][0], Jxyz[5][1], Jxyz[5][2], ypr[0], ypr[1], ypr[2]

    def get_joints_xyz_ypr(self):
        # self._dh_matrix()
        # self._joints_xyz()
        self.kinematics(self.angles)
        return self.Jxyz, self.ypr

    def _dh_matrix(self):
        # notation same as in yt vid
        self.theta_val = np.radians(self.angles) + self.theta_increments
        for i in range(6):
            ct, st = np.cos(self.theta_val[i]), np.sin(self.theta_val[i])
            ca, sa = np.cos(self.alpha_val[i]), np.sin(self.alpha_val[i])

            self.T[i] = np.array([
                [ct, -st * ca, st * sa, self.a_val[i] * ct],
                [st, ct * ca, -ct * sa, self.a_val[i] * st],
                [0, sa, ca, self.d_val[i]],
                [0, 0, 0, 1]
            ])

            self.T[i][np.abs(self.T[i]) < 1e-12] = 0.0

    def _joints_xyz(self):
        for i in range(6):
            if i != 0:
                self.J[i] = self.J[i-1] @ self.T[i]
            else:
                self.J[i] = self.T[i]
            self.Jxyz[i] = self.J[i][:3, 3]

        R = self.J[5][:3, :3]

        # y,x
        self.ypr[0] = np.degrees(np.atan2(R[1, 2], R[0, 2]))
        self.ypr[1] = np.degrees(np.atan2(np.sqrt(1-np.pow(R[2, 2], 2)), R[2, 2]))
        self.ypr[2] = np.degrees(np.atan2(R[2, 1], -R[2, 0]))

    def reset_angles(self):
        self.angles = np.zeros(6)
        self.theta_val = np.radians(self.angles) + self.theta_increments
        self.T = np.empty(6, dtype=object)
        self.J = np.empty(6, dtype=object)
        self.Jxyz = np.empty(6, dtype=object)
        self.ypr = np.zeros(3)
        self._dh_matrix()

    def kinematics(self, angles):
        self.theta_val = np.radians(angles) + self.theta_increments

        for i in range(6):
            ct, st = np.cos(self.theta_val[i]), np.sin(self.theta_val[i])
            ca, sa = np.cos(self.alpha_val[i]), np.sin(self.alpha_val[i])

            self.T[i] = np.array([
                [ct,    -st * ca,   st * sa,    self.a_val[i] * ct],
                [st,    ct * ca,    -ct * sa,   self.a_val[i] * st],
                [0,     sa,         ca,         self.d_val[i]],
                [0,     0,          0,          1]
            ])

        for j in range(6):
            if j != 0:
                self.J[j] = self.J[j-1] @ self.T[j]
            else:
                self.J[j] = self.T[j]
            self.Jxyz[j] = self.J[j][:3, 3]



        R = Tip = self.J[5][:3, :3]
        # Euler
        Z_e = np.arctan2(Tip[1][2], Tip[0][2])
        Yp_e = np.arctan2(np.sqrt(1 - np.pow(Tip[2][2], 2)), Tip[2][2])
        Zpp_e = np.arctan2(Tip[2][1], -Tip[2][0])

        # pitch = -np.arcsin(R[2, 0])
        # roll = np.arctan2(R[2, 1] / np.cos(pitch), R[2, 2] / np.cos(pitch))
        # yaw = np.arctan2(R[1, 0] / np.cos(pitch), R[0, 0] / np.cos(pitch))
        #
        # # Tait-bryan
        # X_t = np.degrees(np.arctan2(-Tip[1][2], Tip[2][2])) # roll
        # Yp_t = np.degrees(np.arctan2(Tip[0][2], np.sqrt(1 - np.pow(Tip[0][2], 2)))) # pitch
        # Zpp_t = np.degrees(np.arctan2(-Tip[0][1], Tip[0][0])) # yaw

        self.ypr[0] = np.degrees(Zpp_e)
        self.ypr[1] = np.degrees(Yp_e)
        self.ypr[2] = np.degrees(Z_e)


    def inverse_kinematics_full(self, target_xyz, target_ypr):
        yaw, pitch, roll = target_ypr
        x, y, z = target_xyz
        new_theta = np.zeros(6)

        c1, s1 = np.cos(np.radians(roll)), np.sin(np.radians(roll))
        c2, s2 = np.cos(np.radians(pitch)), np.sin(np.radians(pitch))
        c3, s3 = np.cos(np.radians(yaw)), np.sin(np.radians(yaw))

        T = np.array([[c1*c2*c3-s1*s3,  -c3*s1-c1*c2*s3,    c1*s2,  x],
                      [c1*s3-c2*c3*s1,  c1*c3-c2*s1*s3,     s1*s2,  y],
                      [-c3*s2,          s2*s3,              c2,     z],
                      [0,               0,                  0,      1]
                      ])

        T[np.abs(T) < 1e-12] = 0.0

        d = self.d_val
        P06 = T[:3, 3]
        d6 = d[5]
        P46 = d6 * T[:3, 2]
        P04 = P06 - P46

        new_theta[0] = np.arctan2(P04[1], P04[0])

        d1 = d[0]
        a = self.a_val
        P01 = np.array([a[0] * np.cos(new_theta[0]), a[0] * np.sin(new_theta[0]), d1])

        P14 = P04 - P01

        P14L = np.linalg.norm(P14)

        fi = np.arccos((np.pow(d[3], 2) + np.pow(a[1], 2) - np.pow(P14L, 2)) / (2 * d[3] * a[1]))
        new_theta[2] = np.pi - fi

        beta1 = np.arctan2(P14[2], np.sqrt(np.pow(P14[0], 2) + np.pow(P14[1], 2)))
        beta2 = np.arccos((np.pow(a[1], 2) + np.pow(P14L, 2) - np.pow(d[3], 2)) / (2 * a[1] * P14L))

        new_theta[1] = beta1 + beta2 - np.pi/2

        ct1, st1 = np.cos(new_theta[0]), np.sin(new_theta[0])
        ct2, st2 = np.cos(new_theta[1]), np.sin(new_theta[1])
        ct3, st3 = np.cos(new_theta[2]), np.sin(new_theta[2])
        c12 = ct1*ct2 - st1*st2
        s12 = ct1*st2 + st1*ct2
        c23 = ct2 * ct3 - st2 * st3
        s23 = ct2 * st3 + st2 * ct3

        A14 = np.array([
            [ct1 * c23,     st1,    ct1 * s23,  ct1 * (a[0] + a[1] * ct2 + a[2] * c23)],
            [st1 * c23,     -ct1,   st1 * s23,  st1 * (a[0] + a[1] * ct2 + a[2] * c23)],
            [s23,           0,      -c23,       a[1] * st2 + d[0] + a[2] * s23],
            [0,             0,      0,          1]
        ])

        R6z = T[:3, 2]
        R4z = A14[:3, 2]

        new_theta[4] = np.arccos(R6z @ R4z.T) - np.pi/2
        new_theta[np.abs(new_theta) < 1e-12] = 0.0

        A16 = T
        A13 = A14
        A13_inv = np.linalg.inv(A13)
        A46 = A13_inv @ A16

        new_theta[3] = np.arctan2(A46[1][3], A46[0][3]) - np.pi
        new_theta[5] = np.arctan2(A46[2][1], A46[2][0]) - np.pi

        new_theta[new_theta < -np.pi] += 2 * np.pi
        new_theta = np.round(new_theta, decimals=1)

        self.angles = np.degrees(new_theta)
        print(np.degrees(new_theta))





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
