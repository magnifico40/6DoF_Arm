from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import numpy as np
from scipy.spatial.transform import Rotation as Rot

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
        self._dh_matrix() #inicjalizacja macierzy transformacji

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
        self._dh_matrix()
        self._joints_xyz()
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

    def return16(self):
        for i in range(6):
            if i != 0:
                self.J[i] = self.J[i-1] @ self.T[i]
            else:
                self.J[i] = self.T[i]

        return self.J[5]
    
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

        R = self.J[5][:3, :3]

        pitch = -np.arcsin(R[2, 0])
        roll = np.arctan2(R[2, 1] / np.cos(pitch), R[2, 2] / np.cos(pitch))
        yaw = np.arctan2(R[1, 0] / np.cos(pitch), R[0, 0] / np.cos(pitch))
      
        self.ypr[2] = np.degrees(np.arcsin(R[2, 1]))

        # Handle potential gimbal lock
        if abs(R[2, 1]) < 0.99999:
            # Yaw (Z-axis rotation)
            self.ypr[0] = np.degrees(np.arctan2(-R[0, 1], R[1, 1]))
            # Pitch (Y-axis rotation)
            self.ypr[1] = np.degrees(np.arctan2(-R[2, 0], R[2, 2]))
        else:
            # Gimbal lock: approximate yaw and pitch
            self.ypr[0] = np.degrees(np.arctan2(R[1, 0], R[0, 0]))
            self.ypr[1] = 0  # set pitch to zero or leave as-is


    def inverse_kinematics_full(self, target_xyz, target_ypr):
        yaw, pitch, roll = target_ypr
        x, y, z = target_xyz
        new_theta = np.zeros(6)

        r = Rot.from_euler('zyx', [yaw, pitch, roll], degrees=True)
        R_matrix = r.as_matrix()
        r_zyz = Rot.from_matrix(R_matrix)
        alpha, beta, gamma = r_zyz.as_euler('zyz')

        c1, s1 = np.cos(alpha), np.sin(alpha)
        c2, s2 = np.cos(beta), np.sin(beta)
        c3, s3 = np.cos(gamma), np.sin(gamma)

        T = np.array([[c1*c2*c3-s1*s3,  -c3*s1-c1*c2*s3,    c1*s2,  x],
                      [c1*s3-c2*c3*s1,  c1*c3-c2*s1*s3,     s1*s2,  y],
                      [-c3*s2,          s2*s3,              c2,     z],
                      [0,               0,                  0,      1]
                      ])

        d = self.d_val
        P06 = T[:3, 3]
        d6 = d[5]
        P46 = d6 * T[:3, 2]
        P04 = P06 - P46
         
        #Theta1--------------------------------------------------------------------------------
        new_theta[0] = np.arctan2(P04[1], P04[0])

        d1 = d[0]
        a = self.a_val
        P01 = np.array([a[0] * np.cos(new_theta[0]), a[0] * np.sin(new_theta[0]), d1])

        P14 = P04 - P01

        P14L = np.linalg.norm(P14)

        #fi from -1 to 1 (arccos)
        cos_fi = (np.pow(d[3], 2) + np.pow(a[1], 2) - np.pow(P14L, 2)) / (2 * d[3] * a[1])
        cos_fi = np.clip(cos_fi, -1.0, 1.0)
        fi = np.arccos(cos_fi)
        zeta = np.arctan2(d[3], a[2])
        new_theta[2] = fi - zeta - 2 * np.pi

        #beta1 from -1 to 1 (arccos)
        beta1 = np.arctan2(P14[2], np.sqrt(np.pow(P14[0], 2) + np.pow(P14[1], 2)))
        cos_beta2 = (np.pow(a[1], 2) +np.pow(P14L, 2) - np.pow(d[3], 2)) / (2 * a[1] * P14L)
        cos_beta2 = np.clip(cos_beta2, -1.0, 1.0)
        beta2 = np.arccos(cos_beta2)

        #Theta2--------------------------------------------------------------------------------
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

        #almost
        #new_theta[3] = np.arctan2(A46[1, 2], A46[0, 2])
        #new_theta[5] = np.arctan2(A46[2, 1], A46[2, 0])

        #almost
        new_theta[3] = np.arctan2(A46[1][3], A46[0][3]) #-pi
        new_theta[5] = np.arctan2(A46[2][1], A46[2][0]) #-pi

        new_theta[new_theta < -np.pi] += 2 * np.pi
    
        new_theta = np.degrees(new_theta)
        #new_theta = (new_theta + 180) % 360 - 180  # zakres [-180, 180]
        self.angles = new_theta



