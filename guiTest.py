import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QSlider, QLabel, QOpenGLWidget, QPushButton,
    QSplitter, QDoubleSpinBox, QGroupBox
)
from PyQt5.QtCore import Qt
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from RobotArm import RobotArm
import pywavefront
import pywavefront.visualization


class RobotOpenGLWidget(QOpenGLWidget):
    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot
        self.quadric = None
        self.segment_models = [
            pywavefront.Wavefront('Modele3D/J1.obj', collect_faces=True),
            pywavefront.Wavefront('Modele3D/J2.obj', collect_faces=True),
            pywavefront.Wavefront('Modele3D/J3.obj', collect_faces=True),
            pywavefront.Wavefront('Modele3D/J4.obj', collect_faces=True),
            pywavefront.Wavefront('Modele3D/J5.obj', collect_faces=True),
            pywavefront.Wavefront('Modele3D/J6.obj', collect_faces=True)
        ]

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
        # theta_table = get_theta_table()

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


        self.draw_grid()

        # Podstawa
        glPushMatrix()
        glTranslatef(0.0, 0.0, segmentLen[0] / 2)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [1.0, 0.5, 0.0, 1.0])
        glRotatef(angles[0], 0, 0, 1)
        self.draw_segment(0)
        glTranslatef(0.0, 0.0, segmentLen[0] / 2)

        # Ramię górne


        glTranslatef(0.0, 0.0, segmentLen[1] / 2)
        glRotatef(angles[1], 1, 0, 0)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.45, 0.65, 0.0, 1.0])
        self.draw_segment(1)
        glTranslatef(0.0, 0.0, segmentLen[1] / 2)

        # nadgarstek

        glTranslatef(0.15, 0, 0.5)
        glRotatef(angles[2], 1, 0, 0)  # roll
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.6, 0.6, 0.6, 1.0])
        self.draw_segment(2)

        glRotatef(angles[3], 0, 1, 0)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.3, 0.6, 0.6, 1.0])
        self.draw_segment(3)
        glTranslatef(-0.15, -segmentLen[2], 0)

        glRotatef(angles[4], 1, 0, 0)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.3, 0.3, 0.6, 1.0])
        self.draw_segment(4)

        glRotatef(angles[5], 0, 1, 0)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.5, 0, 0, 1.0])
        self.draw_segment(5)

        #self.draw_gripper()
        glPopMatrix()
        glEnable(GL_LIGHTING)

    def draw_segment(self, index):
        glPushMatrix()
        self.draw_model(self.segment_models[index])
        glPopMatrix()

    def draw_model(self, model):
        for mesh in model.mesh_list:
            glBegin(GL_TRIANGLES)
            for face in mesh.faces:
                for vertex_i in face:
                    vertex = model.vertices[vertex_i]
                    glVertex3f(*vertex)
            glEnd()

    def draw_grid(self):
        glDisable(GL_LIGHTING)
        grid_size = 25
        spacing = 0.5
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
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, grid_size * spacing)
        glEnd()

        glPopMatrix()
        glEnable(GL_LIGHTING)

    def draw_gripper(self):
        glPushMatrix()

        finger_length = 0.3
        finger_width = 0.3
        spacing = 0.06  # odstęp od środka

        glColor3f(0.0, 0.0, 0.0)

        # Lewy palec
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [1, 0, 0, 1.0])
        glTranslatef(-spacing, -spacing/2, 0.0)
        glScalef(finger_width, finger_width, finger_length)
        self.draw_segment(1)
        glPopMatrix()

        # Prawy palec
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [1, 0, 0, 1.0])
        glTranslatef(spacing, -spacing/2, 0.0)
        glScalef(finger_width, finger_width, finger_length)
        self.draw_segment(1)
        glPopMatrix()

        # Górny palec (nad środkiem)
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0, 0.55, 0, 1.0])
        glTranslatef(0.0, spacing, 0.0)
        glRotatef(90, 0.0, 0.0, 1.0)  # obrót o 90° żeby palec był pionowy
        glScalef(finger_width, finger_width, finger_length)
        self.draw_segment(1)
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

        splitter = QSplitter(Qt.Horizontal)
        main_widget = splitter  # Use splitter as main widget
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
            #self.labels.append(label)
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

        splitter.addWidget(control_widget)
        splitter.addWidget(self.opengl_widget)
        splitter.setSizes([300, 900])
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
            slider.setValue(0)

    def apply_inverse_kinematics(self):
        target_x = self.x_spinbox.value()
        target_y = self.y_spinbox.value()
        target_z = self.z_spinbox.value()
        target_roll = self.roll_spinbox.value()
        target_pitch = self.pitch_spinbox.value()
        target_yaw = self.yaw_spinbox.value()

        test_angles = [0, 45, -30, 0, 90, 0]
        result = self.robot.kinematics(test_angles)
        x, y, z, yaw, pitch, roll = self.robot.get_gripper_xyz_ypr()

        angles = self.robot.inverse_kinematics_full([target_x, target_y, target_z], [target_yaw, target_pitch, target_roll])
        self.opengl_widget.update()
        for i in range(6):
            try:
                self.sliders[i].setValue(int(angles[i]))
                self.robot.set_angle(i, angles[i])
            except:
                print("cant achieve position")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

