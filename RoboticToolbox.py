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

from RobotArm import RobotArm
   
class RobotOpenGLWidget(QOpenGLWidget):
    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot
        
        self.quadric = None
        self.show_targetToPick = False 
        self.pickTarget = False 

    def draw_cube(self, center, size):
        x, y, z = center
        s = size / 2.0

        vertices = [
            [x - s, y - s, z - s],
            [x + s, y - s, z - s],
            [x + s, y + s, z - s],
            [x - s, y + s, z - s],
            [x - s, y - s, z + s],
            [x + s, y - s, z + s],
            [x + s, y + s, z + s],
            [x - s, y + s, z + s]
        ]

        faces = [
            [0, 1, 2, 3],  # back
            [4, 5, 6, 7],  # front
            [0, 1, 5, 4],  # bottom
            [2, 3, 7, 6],  # top
            [1, 2, 6, 5],  # right
            [0, 3, 7, 4]   # left
        ]

        glBegin(GL_QUADS)
        for face in faces:
            for vertex in face:
                glVertex3fv(vertices[vertex])
        glEnd()

    def draw_targetToPick(self, targetToPickXYZ):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(1.0, 0.4, 0.7, 1)
        self.draw_cube(targetToPickXYZ, size = 0.25)


    def initializeGL(self):
        glClearColor(1, 1, 1, 1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glLightfv(GL_LIGHT0, GL_POSITION, [5.0, 5.0, 10.0, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        glEnable(GL_NORMALIZE)

        self.quadric = gluNewQuadric()

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, w / float(h or 1), 1.0, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        angles = self.robot.get_angles()
        segmentLen = self.robot.get_segments_len()
        targetToPickXYZ = self.robot.get_targetToPick_xyz()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        gluLookAt(5, 1, 8, 0, 0, 0, 0, 0, 1)

        glColor4f(0.9, 0.9, 0.9, 1.0)  # R, G, B, A

        # Wyłącz oświetlenie, jeśli używasz go w scenie
        glDisable(GL_LIGHTING)

        # Rysuj dużą płaszczyznę XY
        glBegin(GL_QUADS)
        size = 100  # rozmiar płaszczyzny w jednostkach
        glVertex3f(-size, -size, 0)
        glVertex3f(size, -size, 0)
        glVertex3f(size, size, 0)
        glVertex3f(-size, size, 0)
        glEnd()

        # (opcjonalnie) Włącz z powrotem oświetlenie
        glEnable(GL_LIGHTING)

        self.draw_grid()

        # Podstawa
        glPushMatrix()
        glTranslatef(0.0, 0.0, segmentLen[0] / 2)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [1.0, 0.5, 0.0, 1.0])
        glRotatef(angles[0], 0, 0, 1)
        self.draw_segment(segmentLen[0])
        glTranslatef(0.0, 0.0, segmentLen[0] / 2)

        # Ramię górne
        glRotatef(angles[1], 1, 0, 0)
        glTranslatef(0.0, 0.0, segmentLen[1] / 2)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.45, 0.65, 0.0, 1.0])
        self.draw_segment(segmentLen[1])
        glTranslatef(0.0, 0.0, segmentLen[1] / 2)

        # nadgarstek
        glRotatef(angles[2], 1, 0, 0)
        glRotatef(90, 1, 0, 0)
        glRotatef(angles[3], 0, 0, 1)  # roll
        glTranslatef(0.0, 0.0, segmentLen[2] / 2)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.6, 0.6, 0.6, 1.0])
        self.draw_segment(segmentLen[2])
        glTranslatef(0.0, 0.0, segmentLen[2] / 2)

        glRotatef(angles[4], 1, 0, 0)
        glRotatef(angles[5], 0, 0, 1)
        glTranslatef(0.0, 0.0, segmentLen[3] / 2)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.3, 0.6, 0.6, 1.0])
        self.draw_segment(segmentLen[3])
        glTranslatef(0.0, 0.0, segmentLen[3] / 2)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [1, 0, 0, 1.0])

        self.draw_gripper()

        #glTranslatef(0.0, 0.0, 0.4)
        #self.draw_targetToPick(targetToPickXYZ)

        if self.pickTarget == True and self.show_targetToPick == True: 
            glTranslatef(0.0, 0.0, 0.0)
            self.draw_targetToPick([0, 0, 0]) #wspolrzedne wzgledem grippera
            
        glPopMatrix()
        
        glPushMatrix()
        if self.pickTarget == False and self.show_targetToPick == True:
           glTranslatef(targetToPickXYZ[0], targetToPickXYZ[1], targetToPickXYZ[2])
           self.draw_targetToPick(targetToPickXYZ)
            
        self.draw_target() 
        

        glPopMatrix()

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

    def draw_grid(self):
        glDisable(GL_LIGHTING)
        grid_size = 25
        spacing = 0.4
        arrow_size = 0.3
        arrow_pos = 5 * spacing 

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

        h = 0.001    #Z offset

        # Oś Y (niebieska)
        glColor3f(0.0, 0.0, 1.0)
        glBegin(GL_LINES)
        glVertex3f(0, -grid_size * spacing, h)
        glVertex3f(0, grid_size * spacing, h)
        glEnd()
        # Strzałka Y
        glBegin(GL_LINES)
        glVertex3f(0, arrow_pos, h)
        glVertex3f(arrow_size, arrow_pos - arrow_size, h)
        glVertex3f(0, arrow_pos, h)
        glVertex3f(-arrow_size, arrow_pos - arrow_size, h)
        glEnd()

        # Oś X (zielona)
        glColor3f(0.0, 1.0, 0.0)
        glBegin(GL_LINES)
        glVertex3f(-grid_size * spacing, 0, h)
        glVertex3f(grid_size * spacing, 0, h)
        glEnd()
        # Strzałka X
        glBegin(GL_LINES)
        glVertex3f(arrow_pos, 0, h)
        glVertex3f(arrow_pos - arrow_size, arrow_size, h)
        glVertex3f(arrow_pos, 0, h)
        glVertex3f(arrow_pos - arrow_size, -arrow_size, h)
        glEnd()

        # Oś Z (czerwona)
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, grid_size * spacing)
        glEnd()

        glPopMatrix()
        glEnable(GL_LIGHTING)

    def draw_target(self):
        #trochę na szybko
        xyz = self.robot.get_target_xyz()

        x, y, z = 0, 0, 0
        #small translation, so we can se target better
        #if xyz[0]>0: x = 0.1
        #elif xyz[0]<0: x = -0.1
        #if xyz[1]>0: y = 0.1
        #elif xyz[1]<0: y = -0.1
        #if xyz[2]>0: z = 0.1
        #elif xyz[2]<0: z = -0.1
        glTranslatef(x, y, z)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glEnable(GL_POINT_SMOOTH)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)

        glPointSize(15.0)
        glColor4f(1.0, 0.7, 0.2, 0.2) 

        glBegin(GL_POINTS)
        glVertex3f(xyz[0], xyz[1], xyz[2])
        glEnd()

    def draw_gripper(self):
        def draw_finger():
            base = 0.2
            height = 1.0

            glBegin(GL_TRIANGLES)
            apex = (0.0, 0.0, height)
            base_pts = [
                (-base/2, -base/2, 0.0),
                ( base/2, -base/2, 0.0),
                ( base/2,  base/2, 0.0),
                (-base/2,  base/2, 0.0)
            ]
            for i in range(4):
                p1 = base_pts[i]
                p2 = base_pts[(i+1) % 4]
                glVertex3f(*p1)
                glVertex3f(*p2)
                glVertex3f(*apex)
            glEnd()

            glBegin(GL_QUADS)
            for pt in base_pts:
                glVertex3f(*pt)
            glEnd()

        glPushMatrix()

        finger_length = 0.3
        finger_width = 0.3
        spacing = 0.06  # odstęp od środka
        angle = 30      # kąt nachylenia palców do środka (stopnie)

        glColor3f(0.1, 0.1, 0.1)

        # Lewy palec - obrót w kierunku środka (+angle)
        glPushMatrix()
        glTranslatef(-spacing, -spacing/2, 0.0)
        glRotatef(angle, 0.0, 0.0, 1.0)  # obrót wokół osi Z
        glScalef(finger_width, finger_width, finger_length)
        draw_finger()
        glPopMatrix()

        # Prawy palec - obrót w kierunku środka (-angle)
        glPushMatrix()
        glTranslatef(spacing, -spacing/2, 0.0)
        glRotatef(-angle, 0.0, 0.0, 1.0) # obrót wokół osi Z
        glScalef(finger_width, finger_width, finger_length)
        draw_finger()
        glPopMatrix()

        # Górny palec (nad środkiem) bez zmiany lub ew. lekki obrót
        glPushMatrix()
        glTranslatef(0.0, spacing, 0.0)
        glRotatef(90, 0.0, 0.0, 1.0)  # pionowo
        # jeśli chcesz, możesz dodać też obrót, np. glRotatef(5, 1, 0, 0)
        glScalef(finger_width, finger_width, finger_length)
        draw_finger()
        glPopMatrix()

        glPopMatrix()
class MyButton(QPushButton):
    def __init__(self, text=""):
        super().__init__(text)
        self.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50; /* Green */
                        border: none;
                        color: white;
                        padding: 15px 32px;
                        text-align: center;
                        text-decoration: none;
                        display: inline-block;
                        font-size: 16px;
                    }
                    QPushButton:hover {
                        background-color: #45a049; /* Darker green */
                    }
                """)


class MySlider(QSlider):
    def __init__(self, orientation=None):
        super().__init__(orientation)
        self.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999;
                border-radius: 4px;
                height: 10px;
                margin: 2px 0;
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 red, stop:0.1667 orange, stop:0.3333 yellow, stop:0.5 green, stop:0.6667 cyan, stop:0.8333 blue, stop:1 violet);
            }
            }
            QSlider::handle:horizontal {
                width: 16px;
                margin-top: -4px;
                margin-bottom: -4px;
                border-radius: 8px;
                background-color: qradialgradient(cx:0.5, cy:0.5, fx:0.5, fy:0.5, radius:1, stop:0 #3daee9, stop:0.4 #2f5bb7);
            }
        """)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Robot Arm Control - PyQt5 + OpenGL")
        self.resize(1200, 900)

        self.robot = RobotArm()

        self.opengl_widget = RobotOpenGLWidget(self.robot)
        self.sliders = []
        self.labels = []
        self.animations = []

        splitter = QSplitter(Qt.Horizontal)
        main_widget = splitter  
        self.setCentralWidget(main_widget)

        # Panel suwaków
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)

        kin_group = QGroupBox("Forward Kinematics")
        kin_group.setStyleSheet("QGroupBox {background-color: #ADD8E6;}")
        kin_layout = QVBoxLayout(kin_group)

        # Create sliders with improvements
        limits = self.robot.get_joints_limits()
        for i in range(6):
            slider_layout = QVBoxLayout()
            label_layout = QHBoxLayout()
            label1 = QLabel(f"Joint {i + 1}: ")
            label1.setStyleSheet("min-width: 100px; font-size: 12px")
            label2 = QLabel(f"0°")
            label2.setStyleSheet("min-width: 15px; font-size: 12px")
            label_layout.addWidget(label1)
            label_layout.addWidget(label2)

            slider_layout.addLayout(label_layout)

            slider = MySlider(Qt.Horizontal)
            slider.setMinimum(limits[i][0])
            slider.setMaximum(limits[i][1])
            slider.setValue(0)
            slider.setTickPosition(QSlider.TicksBelow)
            slider.setTickInterval(30)
            slider.valueChanged.connect(self.make_slider_handler(i, label2))

            slider_layout.addWidget(slider)

            slider_layout.addSpacing(5)
            self.sliders.append(slider)
            kin_layout.addLayout(slider_layout)

        control_layout.addWidget(kin_group)


        coord_group = QGroupBox("Inverse Kinematics")
        coord_group.setStyleSheet("QGroupBox {background-color: #ADD8E6;}")
        coord_layout = QVBoxLayout(coord_group)

        # Position coordinates
        pos_label = QLabel("Position:")
        pos_label.setStyleSheet("font-weight: bold; font-size: 13px")
        coord_layout.addWidget(pos_label)

        # X coordinate
        x_layout = QHBoxLayout()
        x_label = QLabel("X:")
        x_label.setStyleSheet("font-size: 12px")
        x_label.setMinimumWidth(20)
        self.x_spinbox = QDoubleSpinBox()
        self.x_spinbox.setRange(-10.0, 10.0)
        self.x_spinbox.setSingleStep(0.1)
        self.x_spinbox.setDecimals(2)
        self.x_spinbox.setValue(0.0)
        x_layout.addWidget(x_label)
        x_layout.addWidget(self.x_spinbox)

        # Y coordinate
        y_layout = QHBoxLayout()
        y_label = QLabel("Y:")
        y_label.setStyleSheet("font-size: 12px")
        y_label.setMinimumWidth(20)
        self.y_spinbox = QDoubleSpinBox()
        self.y_spinbox.setRange(-10.0, 10.0)
        self.y_spinbox.setSingleStep(0.1)
        self.y_spinbox.setDecimals(2)
        self.y_spinbox.setValue(0.0)
        y_layout.addWidget(y_label)
        y_layout.addWidget(self.y_spinbox)

        # Z coordinate
        z_layout = QHBoxLayout()
        z_label = QLabel("Z:")
        z_label.setStyleSheet("font-size: 12px")
        z_label.setMinimumWidth(20)
        self.z_spinbox = QDoubleSpinBox()
        self.z_spinbox.setRange(-10.0, 10.0)
        self.z_spinbox.setSingleStep(0.1)
        self.z_spinbox.setDecimals(2)
        self.z_spinbox.setValue(2.0)
        z_layout.addWidget(z_label)
        z_layout.addWidget(self.z_spinbox)

        # Orientation coordinates
        orient_label = QLabel("Orientation:")
        orient_label.setStyleSheet("font-weight: bold; font-size: 13px")
        coord_layout.addWidget(orient_label)

        # Roll
        roll_layout = QHBoxLayout()
        roll_label = QLabel("Roll:")
        roll_label.setStyleSheet("font-size: 12px")
        roll_label.setMinimumWidth(20)
        self.roll_spinbox = QDoubleSpinBox()
        self.roll_spinbox.setRange(-180.0, 180.0)
        self.roll_spinbox.setSingleStep(1.0)
        self.roll_spinbox.setDecimals(1)
        self.roll_spinbox.setValue(0.0)
        self.roll_spinbox.setSuffix("°")
        roll_layout.addWidget(roll_label)
        roll_layout.addWidget(self.roll_spinbox)

        # Pitch
        pitch_layout = QHBoxLayout()
        pitch_label = QLabel("Pitch:")
        pitch_label.setStyleSheet("font-size: 12px")
        pitch_label.setMinimumWidth(20)
        self.pitch_spinbox = QDoubleSpinBox()
        self.pitch_spinbox.setRange(-180.0, 180.0)
        self.pitch_spinbox.setSingleStep(1.0)
        self.pitch_spinbox.setDecimals(1)
        self.pitch_spinbox.setValue(0.0)
        self.pitch_spinbox.setSuffix("°")
        pitch_layout.addWidget(pitch_label)
        pitch_layout.addWidget(self.pitch_spinbox)

        # Yaw
        yaw_layout = QHBoxLayout()
        yaw_label = QLabel("Yaw:")
        yaw_label.setStyleSheet("font-size: 12px")
        yaw_label.setMinimumWidth(20)
        self.yaw_spinbox = QDoubleSpinBox()
        self.yaw_spinbox.setRange(-180.0, 180.0)
        self.yaw_spinbox.setSingleStep(1.0)
        self.yaw_spinbox.setDecimals(1)
        self.yaw_spinbox.setValue(0.0)
        self.yaw_spinbox.setSuffix("°")
        yaw_layout.addWidget(yaw_label)
        yaw_layout.addWidget(self.yaw_spinbox)

        # Apply button
        apply_ik_btn = MyButton("Apply IK")

        apply_ik_btn.clicked.connect(self.apply_inverse_kinematics)

        # Add all to coordinate group
        coord_layout.addLayout(x_layout)
        coord_layout.addSpacing(5)
        coord_layout.addLayout(y_layout)
        coord_layout.addSpacing(5)
        coord_layout.addLayout(z_layout)
        coord_layout.addSpacing(10)  # Add space between position and orientation
        coord_layout.addWidget(orient_label)
        coord_layout.addLayout(roll_layout)
        coord_layout.addSpacing(5)
        coord_layout.addLayout(pitch_layout)
        coord_layout.addSpacing(5)
        coord_layout.addLayout(yaw_layout)
        coord_layout.addSpacing(5)
        coord_layout.addWidget(apply_ik_btn)

        # Add the group to main control layout
        control_layout.addWidget(coord_group)

        # Add reset button
        reset_btn = MyButton("Reset All Joints")

        reset_btn.clicked.connect(self.reset_all_joints)
        control_layout.addWidget(reset_btn)

        control_layout.addStretch()

        #target section
        target_group = QGroupBox("Object to pick")
        target_group.setStyleSheet("QGroupBox {background-color: #ADD8E6;}")
        target_layout = QVBoxLayout(target_group)
        
        
        # target coordinates
        pos_label_targ = QLabel("Position:")
        pos_label_targ.setStyleSheet("font-weight: bold; font-size: 13px")
        target_layout.addWidget(pos_label_targ)

        # X coordinate
        x_layout_targ = QHBoxLayout()
        x_label_targ = QLabel("X:")
        x_label_targ.setStyleSheet("font-size: 12px")
        x_label_targ.setMinimumWidth(20)
        self.x_spinbox_targ = QDoubleSpinBox()
        self.x_spinbox_targ.setRange(-10.0, 10.0)
        self.x_spinbox_targ.setSingleStep(0.1)
        self.x_spinbox_targ.setDecimals(2)
        self.x_spinbox_targ.setValue(0.0)
        x_layout_targ.addWidget(x_label_targ)
        x_layout_targ.addWidget(self.x_spinbox_targ)

        # Y coordinate
        y_layout_targ = QHBoxLayout()
        y_label_targ = QLabel("Y:")
        y_label_targ.setStyleSheet("font-size: 12px")
        y_label_targ.setMinimumWidth(20)
        self.y_spinbox_targ = QDoubleSpinBox()
        self.y_spinbox_targ.setRange(-10.0, 10.0)
        self.y_spinbox_targ.setSingleStep(0.1)
        self.y_spinbox_targ.setDecimals(2)
        self.y_spinbox_targ.setValue(0.0)
        y_layout_targ.addWidget(y_label_targ)
        y_layout_targ.addWidget(self.y_spinbox_targ)

        # Z coordinate
        z_layout_targ = QHBoxLayout()
        z_label_targ = QLabel("Z:")
        z_label_targ.setStyleSheet("font-size: 12px")
        z_label_targ.setMinimumWidth(20)
        self.z_spinbox_targ = QDoubleSpinBox()
        self.z_spinbox_targ.setRange(-10.0, 10.0)
        self.z_spinbox_targ.setSingleStep(0.1)
        self.z_spinbox_targ.setDecimals(2)
        self.z_spinbox_targ.setValue(0.0)
        z_layout_targ.addWidget(z_label_targ)
        z_layout_targ.addWidget(self.z_spinbox_targ)
        
        self.draw_target_btn = MyButton("Draw Target")
        self.draw_target_btn.setCheckable(True)
        self.draw_target_btn.clicked.connect(self.draw_targetToPick) #referencja do funckji, bez naw - nie jest wykonywana natychmist

        self.PickTarget_btn = MyButton("Pick Target")
        self.PickTarget_btn.setCheckable(True)
        self.PickTarget_btn.clicked.connect(self.PickTarget)


        target_layout.addLayout(x_layout_targ)
        target_layout.addSpacing(5)
        target_layout.addLayout(y_layout_targ)
        target_layout.addSpacing(5)
        target_layout.addLayout(z_layout_targ)
        target_layout.addSpacing(5)
        target_layout.addWidget(self.draw_target_btn)
        target_layout.addSpacing(5)
        target_layout.addWidget(self.PickTarget_btn)

        control_layout.addWidget(target_group)

        # scroll_area z pionowym suwakiem
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(control_widget)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Dodaj tylko scroll_area i OpenGL widget do splitter
        splitter.addWidget(scroll_area)
        splitter.addWidget(self.opengl_widget)

        splitter.setSizes([300, 700])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)


        self.opengl_widget.setMinimumWidth(300)
        control_widget.setMinimumWidth(300)

    def make_slider_handler(self, index, label):
        def handler(value):
            # Joint {index + 1}:
            label.setText(f"{value}°")
            self.robot.set_angle(index, value)
            self.opengl_widget.update()
            x, y, z, yaw, pitch, roll = self.robot.get_gripper_xyz_ypr()
            self.x_spinbox.setValue(x)
            self.y_spinbox.setValue(y)
            self.z_spinbox.setValue(z)
            self.roll_spinbox.setValue(roll)
            self.pitch_spinbox.setValue(pitch)
            self.yaw_spinbox.setValue(yaw)

            label.setStyleSheet("color: black; min-width: 100px;")

        return handler

    def reset_all_joints(self):
        for slider in self.sliders:
            animation = QPropertyAnimation(slider, b"value")
            animation.setDuration(500)  # Czas trwania animacji w milisekundach (np. 0.5 sekundy)
            animation.setStartValue(slider.value())
            animation.setEndValue(0)
            animation.start()
            self.animations.append(animation)
    
    def PickTarget(self):
        
        if self.PickTarget_btn.isChecked():
            self.opengl_widget.pickTarget = True

            targetToPick_x = self.x_spinbox_targ.value()
            targetToPick_y = self.y_spinbox_targ.value()
            targetToPick_z = self.z_spinbox_targ.value()
            targetToPickXYZ = [targetToPick_x, targetToPick_y, targetToPick_z]

            initial_angles = self.robot.get_angles()
            yaw = np.degrees(np.arctan2(targetToPick_y, targetToPick_x))

            rpy = [0, 90, yaw]
            Targetangles, success = self.robot.inverse_kinematics(targetToPickXYZ, rpy, initial_angles)
            if success:
                print("sukces")
                self.move_pointToPoint(Targetangles, initial_angles)
            else: QMessageBox.warning(self, "Inverse Kinematics", "Cel poza zasięgiem.")
        else:  self.opengl_widget.pickTarget = False
        self.opengl_widget.update()

    def draw_targetToPick(self):
        if self.draw_target_btn.isChecked():
            targetToPick_x = self.x_spinbox_targ.value()
            targetToPick_y = self.y_spinbox_targ.value()
            targetToPick_z = self.z_spinbox_targ.value()
            targetToPickXYZ = [targetToPick_x, targetToPick_y, targetToPick_z]

            
            self.robot.set_targetToPick_xyz(targetToPick_x, targetToPick_y, targetToPick_z)
            self.opengl_widget.show_targetToPick = True
        else:
            self.opengl_widget.show_targetToPick = False

        self.opengl_widget.update()

    def move_pointToPoint(self, endingAngles, initialAngles):
        angles_deg = np.degrees(endingAngles)
        angles_deg_int = np.rint(angles_deg).astype(int)
        print(angles_deg)
        trajectory = self.robot.joint_trajectory(initialAngles, angles_deg)
        for q in trajectory:
            transitional_angles = q
            transitional_angles_int = np.rint(transitional_angles).astype(int)
            for i in range(6):
                self.sliders[i].setValue(transitional_angles_int[i])
                self.robot.set_angle(i, transitional_angles[i])
            time.sleep(0.001)    
            QApplication.processEvents()    #odswierzenie GUI

    def apply_inverse_kinematics(self):
        # Get target coordinates
        target_x = self.x_spinbox.value()
        target_y = self.y_spinbox.value()
        target_z = self.z_spinbox.value()

        # Get target orientation
        target_roll = self.roll_spinbox.value()
        target_pitch = self.pitch_spinbox.value()
        target_yaw = self.yaw_spinbox.value()

        xyz = [target_x, target_y, target_z]
        rpy = [target_roll, target_pitch, target_yaw]  

        self.robot.set_target_xyz(xyz)

        initial_angles = self.robot.get_angles()

        angles, success = self.robot.inverse_kinematics(xyz, rpy, initial_angles)

        if success:
            self.move_pointToPoint(angles, initial_angles)
        else:
            #print("Inverse Kinematics Impossible")
            QMessageBox.warning(self, "Inverse Kinematics", "Nie udało się znaleźć rozwiązania IK.")


       
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
        
          
        
        
        
        
        
        
        
        
        
       
        