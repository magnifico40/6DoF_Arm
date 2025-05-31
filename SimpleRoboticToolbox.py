#kinematics with roboticsToolbox


"""
Instalation
py -3.11 -m venv venv2
venv2\Scripts\activate
pip install numpy==1.24.4
pip install roboticstoolbox-python PyQt5 PyOpenGL PyOpenGL_accelerate
"""

import numpy as np
from roboticstoolbox import DHRobot, RevoluteDH
from spatialmath import SE3

segmentLen = np.array([0.5, 1, 0.5, 0.25])

a_val = np.array([0, segmentLen[1], 0, 0, 0, 0])
dValues = np.array([segmentLen[0], 0, 0, -segmentLen[2], 0, -segmentLen[3]])
theta = np.radians([-90, -90, 0, 0, 0, 0])
alpha = np.radians([-90, 0, -90, 90, -90, 0])

#robot model 

links = [
    RevoluteDH(d=dValues[i], a=a_val[i], alpha=alpha[i], offset=theta[i])
    for i in range(6)
]
robot = DHRobot(links, name="My6DOFRobot")

#inverse kinematics:
xyz = [0.5, 0.1, 0.2]
ypr = [0, 90, 0] #in deg

TargetMatrix = SE3(xyz) * SE3.RPY(ypr, unit='deg')

solution = robot.ikine_LM(TargetMatrix)
if solution.success:
    print("Znaleziono rozwiązanie!")
    print("q =", np.degrees(solution.q))
else:
    print("Nie znaleziono rozwiązania.")
    
"""    
#forward kinematics:

angles = [0, 0, 0, 0, 0, 0]
T = robot.fkine(angles)  # pozycja końcówki przy wszystkich kątach = 0
print("Pozycja końcówki przy q=[0]*6:\n", T)

"""