import time
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
        #self.alpha_val = np.array(np.radians([-90, 0, -90, 90, -90, 0]))
        self.theta_increments = np.radians([0, 90, 0, 0, 0, 0])
        #self.theta_increments = np.radians([-90, -90, 0, 0, 0, 0])
        self.theta_val = np.radians(self.angles) + self.theta_increments
        self.T = np.empty(6, dtype=object)
        self.J = np.empty(6, dtype=object)
        self.Jxyz = np.empty(6, dtype=object)
        self.ypr = np.zeros(3)
        self.targetXYZ = [0, 0, 0]
        self.targetToPickXYZ = [0, 0, 0]
        self.JointLimits = np.array([[-180, 180], [-180, 180], [-180, 180], [-180, 180], [-180, 180], [-180, 180]])
        self._dh_matrix() # inicjalizacja macierzy transformacji

    
    def joint_trajectory(self, startingAngles, endingAngles, TrajetorySteps = 100):
        return [startingAngles + (endingAngles - startingAngles) * t for t in np.linspace(0, 1, TrajetorySteps)]
    
    def set_target_xyz(self, xyz):
        for i in range(3):
            self.targetXYZ[i] = xyz[i]

    def get_target_xyz(self):
        return self.targetXYZ

    def get_targetToPick_xyz(self):
        return self.targetToPickXYZ
    
    def set_angle(self, index, value):
        self.angles[index] = value

    def set_targetToPick_xyz(self, xyz):
        self.targetToPickXYZ = xyz

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
    
    def _joints_xyz(self):
        for i in range(6):
            if i != 0:
                self.J[i] = self.J[i-1] @ self.T[i]
            else:
                self.J[i] = self.T[i]
            self.Jxyz[i] = self.J[i][:3, 3]

        R = self.J[5][:3, :3]

        # Obliczenie YPR z macierzy rotacji
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
        self.angles = np.array(angles)  
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
            
            self.T[i][np.abs(self.T[i]) < 1e-12] = 0.0

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
        
        return self.J[5]
    
    def dhMat(self, theta, d, a, alpha):
        ct, st = np.cos(theta), np.sin(theta)
        ca, sa = np.cos(alpha), np.sin(alpha)
        return np.array([
            [ct, -st * ca,  st * sa, a * ct],
            [st,  ct * ca, -ct * sa, a * st],
            [0,       sa,      ca,      d],
            [0,        0,       0,      1]
            ])
    
    def inverse_kinematics(self, target_xyz, target_ypr):
        #results are in degrees
        yaw, pitch, roll = target_ypr
        x, y, z = target_xyz

        r = Rot.from_euler('zyx', [yaw, pitch, roll], degrees=True)
        R_matrix = r.as_matrix()

        T_target = np.eye(4)
        T_target[:3, :3] = R_matrix
        T_target[:3, 3] = [x, y, z]
        print(self.inverse_kinematics_numeric(T_target))
        return self.inverse_kinematics_numeric(T_target)

    def inverse_kinematics_numeric(self, T_target, max_iters=1000, threshold=1e-3):
        #Pseudo Jacobian inverse
        
        q = np.radians(self.angles) + self.theta_increments
        alpha = 0.1 # Współczynnik uczenia, "skok" między iteracjami
        
        best_error = float('inf')
        best_q = q.copy()

        for iteration in range(max_iters):
            angles_deg = np.degrees(q - self.theta_increments)
            T_curr = self.kinematics(angles_deg)

            # Position error
            dp = T_target[:3, 3] - T_curr[:3, 3]
            position_error = np.linalg.norm(dp)
            
            # Orientation error
            R_err = T_target[:3, :3] @ T_curr[:3, :3].T
            try:
                dR = Rot.from_matrix(R_err).as_rotvec()
                orientation_error = np.linalg.norm(dR)
            except:
                # Fallback jeśli macierz rotacji jest nieprawidłowa
                dR = np.array([0, 0, 0])
                orientation_error = 0
            
            total_error = position_error + orientation_error
            
            # Zapisz najlepsze rozwiązanie
            if total_error < best_error:
                best_error = total_error
                best_q = q.copy()

            # Sprawdź warunek stopu
            if position_error < threshold and orientation_error < threshold:
                print(f"Konwergencja po {iteration} iteracjach")
                break

            # Oblicz Jacobian
            J = self._compute_jacobian(q)
            
            # Sprawdź czy Jacobian nie jest osobliwy
            if np.linalg.det(J @ J.T) < 1e-10:
                print("Jacobian osobliwy - używam najlepszego rozwiązania")
                q = best_q
                break
            
            # Oblicz krok korekcji
            err = np.concatenate((dp, dR))
            try:
                dq = alpha * np.linalg.pinv(J) @ err
            except:
                print("Błąd obliczenia pseudoinverse - przerywam")
                q = best_q
                break

            # Zastosuj krok z ograniczeniami
            q += dq
            
            # Ogranicz kąty do dozwolonych wartości
            q_limited = np.clip(q - self.theta_increments, 
                               np.radians(self.JointLimits[:, 0]), 
                               np.radians(self.JointLimits[:, 1]))
            q = q_limited + self.theta_increments
            
            # Adaptacyjny współczynnik uczenia
            if iteration > 100 and total_error > best_error * 1.1:
                alpha *= 0.9  # Zmniejsz krok jeśli błąd rośnie

        # Użyj najlepszego znalezionego rozwiązania
        q = best_q
        self.angles = np.degrees(q - self.theta_increments)
        
        # Sprawdź ograniczenia stawów
        self.angles = np.clip(self.angles, self.JointLimits[:, 0], self.JointLimits[:, 1])
        
        print(f"Końcowy błąd: {best_error:.6f}")
        return self.angles, best_error

    def _compute_jacobian(self, q):
        J = np.zeros((6, 6))
        
        # Oblicz pozycje i orientacje wszystkich stawów
        T_matrices = []
        for i in range(6):
            T_matrices.append(self.dhMat(q[i], self.d_val[i], self.a_val[i], self.alpha_val[i]))
        
        # Oblicz skumulowane transformacje
        T_cumulative = [T_matrices[0]]
        for i in range(1, 6):
            T_cumulative.append(T_cumulative[-1] @ T_matrices[i])
        
        # Pozycja końcowa
        p_end = T_cumulative[-1][:3, 3]
        
        # Dla każdego stawu oblicz wpływ na pozycję i orientację końcówki
        for i in range(6):
            if i == 0:
                # Pierwszy staw - oś Z bazowa
                z_i = np.array([0, 0, 1])
                p_i = np.array([0, 0, 0])
            else:
                # Pozostałe stawy
                z_i = T_cumulative[i-1][:3, 2]  # Oś Z stawu i-1
                p_i = T_cumulative[i-1][:3, 3]  # Pozycja stawu i-1
            
            # Wkład do prędkości liniowej (iloczyn wektorowy)
            J[:3, i] = np.cross(z_i, p_end - p_i)
            
            # Wkład do prędkości kątowej
            J[3:, i] = z_i

        return J

   
