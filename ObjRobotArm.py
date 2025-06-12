"""
trzeba niestety starszego pythona i numpy

Instalation
py -3.11 -m venv venv2 
venv2\Scripts\activate
pip install numpy==1.24.4
pip install roboticstoolbox-python PyQt5 PyOpenGL PyOpenGL_accelerate

pamiętaj by interpreter jeszcze wybrać z venv2

"""

import time
import sys
import numpy as np
from roboticstoolbox import DHRobot, RevoluteDH
from spatialmath import SE3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QSlider, QLabel, QOpenGLWidget, QPushButton,
    QSplitter, QDoubleSpinBox, QGroupBox, QMessageBox, QScrollArea, 
)
from PyQt5.QtCore import (Qt, QPropertyAnimation, pyqtSlot)
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


class RobotArm:
    def __init__(self):
        self.angles = np.zeros(6)
        self.segmentLen = np.array([0.5, 1, 0.5, 0.25])
        self.a_val = np.array([0, self.segmentLen[1], 0, 0, 0, 0])
        self.d_val = np.array([self.segmentLen[0], 0, 0, self.segmentLen[2], 0, self.segmentLen[3]])
        self.dValues = np.array([self.segmentLen[0], 0, 0, self.segmentLen[2], 0, self.segmentLen[3]])
        self.alpha_val = np.array(np.radians([-90, 0, -90, 90, -90, 0]))
        self.theta_increments = np.radians([-90, -90, 0, 0, 0, 0])
        self.theta_val = np.radians(self.angles) + self.theta_increments
        self.T = np.empty(6, dtype=object)
        self.J = np.empty(6, dtype=object)
        self.Jxyz = np.empty(6, dtype=object)
        self.ypr = np.empty(3, dtype=object)
        self.JointLimits = np.array([[-180, 180], [-180, 180], [-270, 90], [-180, 180], [-180, 180], [-180, 180]])
        self.targetXYZ = [0, 0, 0]
        self.targetToPickXYZ = [0, 0, 0]
        self.links = [
            RevoluteDH(
                d=self.dValues[i],
                a=self.a_val[i],
                alpha=self.alpha_val[i],
                offset=self.theta_increments[i],
                qlim=np.radians(self.JointLimits[i])  # <- Dodane limity w radianach
            )
            for i in range(6)
        ]
        self.robotModel = DHRobot(self.links, name="MyRobot")
    
    def joint_trajectory(self, startingAngles, endingAngles, TrajetorySteps = 100):
        return [startingAngles + (endingAngles - startingAngles) * t for t in np.linspace(0, 1, TrajetorySteps)]
    
    def set_target_xyz(self, xyz):
        for i in range(3):
            self.targetXYZ[i] = xyz[i]

    def get_target_xyz(self):
        return self.targetXYZ

    def get_targetToPick_xyz(self):
        return self.targetToPickXYZ
    
    def set_targetToPick_xyz(self, x, y, z):
        self.targetToPickXYZ[0] = x
        self.targetToPickXYZ[1] = y
        self.targetToPickXYZ[2] = z

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

    def reset_angles(self):
        self.angles = np.zeros(6)
        self.theta_val = np.radians(self.angles) + self.theta_increments
        self.T = np.empty(6, dtype=object)
        self.J = np.empty(6, dtype=object)
        self.Jxyz = np.empty(6, dtype=object)
        self.ypr = np.empty(3, dtype=object)

    def inverse_kinematics(self, xyz, ypr, initial_angles):
        #xyz, ypr - arrays
        try:
            TargetMatrix = SE3(xyz) * SE3.RPY(ypr, unit='deg')
            solution = self.robotModel.ikine_LM(TargetMatrix, q0=initial_angles, ilimit=1000, slimit=1000)

            if solution.success:
                return solution.q, solution.success
            else:
                print("Nie znaleziono rozwiązania.")
                return None, False
        except Exception as e:
            print(f" Błąd podczas obliczania IK: {e}")
            return None, False
