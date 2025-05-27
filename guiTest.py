import sys
import numpy as np

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QSlider, QLabel, QOpenGLWidget
)
from PyQt5.QtCore import Qt

from OpenGL.GL import *
from OpenGL.GLU import *

# -------------------------------------------------------------
# Klasa logiki ramienia robota (Twoja z RobotArm)
# -------------------------------------------------------------
class RobotArm:
    def __init__(self):
        self.angles = np.zeros(6)
        self.segmentLen = np.array([1, 1, 0.5, 0.25])

    def set_angle(self, index, value):
        self.angles[index] = value

    def get_angles(self):
        return self.angles

    def get_segments_len(self):
        return self.segmentLen

# -------------------------------------------------------------
# OpenGL Widget do rysowania ramienia robota
# -------------------------------------------------------------
class RobotOpenGLWidget(QOpenGLWidget):
    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot
        self.quadric = None

    def initializeGL(self):
        glClearColor(1, 1, 1, 1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

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

        gluLookAt(5, 0, 8, 0, 0, 0, 0, 0, 1)


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


# -------------------------------------------------------------
# Główne okno z GUI i OpenGLWidgetem
# -------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Robot Arm Control - PyQt5 + OpenGL")
        self.resize(1000, 600)

        self.robot = RobotArm()

        self.opengl_widget = RobotOpenGLWidget(self.robot)
        self.sliders = []
        self.labels = []

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QHBoxLayout()
        main_widget.setLayout(layout)

        # Panel suwaków
        control_panel = QVBoxLayout()
        for i in range(6):
            label = QLabel(f"Joint {i+1}: 0°")
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(-180)
            slider.setMaximum(180)
            slider.setValue(0)
            slider.valueChanged.connect(self.make_slider_handler(i, label))

            control_panel.addWidget(label)
            control_panel.addWidget(slider)
            self.sliders.append(slider)
            self.labels.append(label)

        layout.addLayout(control_panel, 1)
        layout.addWidget(self.opengl_widget, 4)

    def make_slider_handler(self, index, label):
        def handler(value):
            label.setText(f"Joint {index+1}: {value}°")
            self.robot.set_angle(index, value)
            self.opengl_widget.update()
        return handler

# -------------------------------------------------------------
# Uruchomienie aplikacji
# -------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
