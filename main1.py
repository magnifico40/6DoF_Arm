#core approach - more professional, more opportunities


#----------------------------------------------------------------------------------
#not ready yet - needs improvements
#in theory we can use stl files, would be nice to do something like this:
#https://youtu.be/jJZ30hhS2Rk
#----------------------------------------------------------------------------------


import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import sys
import ctypes

angle1 = 0
angle2 = 0
angle3 = 0
angle4 = 0
angle5 = 0
angle6 = 0

#geometry shader
vertex_shader_source = """
#version 330 core
layout (location = 0) in vec3 aPos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform vec3 color;

out vec3 fragColor;

void main()
{
    gl_Position = projection * view * model * vec4(aPos, 1.0);
    fragColor = color;
}
"""

#color shader
fragment_shader_source = """
#version 330 core
in vec3 fragColor;
out vec4 FragColor;

void main()
{
    FragColor = vec4(fragColor, 1.0);
}
"""

class RobotArm:
    def __init__(self):
        self.shader_program = None
        self.cube_vao = None
        self.line_vao = None
        self.view_matrix = None
        self.projection_matrix = None
        self.setup_shaders()
        self.setup_geometry()

    def setup_shaders(self):
        vertex_shader = compileShader(vertex_shader_source, GL_VERTEX_SHADER)
        fragment_shader = compileShader(fragment_shader_source, GL_FRAGMENT_SHADER)
        self.shader_program = compileProgram(vertex_shader, fragment_shader)

    def setup_geometry(self):
        # Vertices dla sześcianu
        cube_vertices = np.array([
            -0.5, -0.5,  0.5,
             0.5, -0.5,  0.5,
             0.5,  0.5,  0.5,
            -0.5,  0.5,  0.5,
            -0.5, -0.5, -0.5,
             0.5, -0.5, -0.5,
             0.5,  0.5, -0.5,
            -0.5,  0.5, -0.5,
        ], dtype=np.float32)

        cube_indices = np.array([
            0, 1, 2, 2, 3, 0,  # front
            4, 5, 6, 6, 7, 4,  # back
            7, 3, 0, 0, 4, 7,  # left
            1, 5, 6, 6, 2, 1,  # right
            3, 2, 6, 6, 7, 3,  # top
            0, 1, 5, 5, 4, 0,  # bottom
        ], dtype=np.uint32)

        # Setup cube VAO
        self.cube_vao = glGenVertexArrays(1)
        cube_vbo = glGenBuffers(1)
        cube_ebo = glGenBuffers(1)

        glBindVertexArray(self.cube_vao)
        glBindBuffer(GL_ARRAY_BUFFER, cube_vbo)
        glBufferData(GL_ARRAY_BUFFER, cube_vertices.nbytes, cube_vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, cube_ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, cube_indices.nbytes, cube_indices, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * 4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        glBindVertexArray(0)

        # Setup grid
        grid_vertices = []
        grid_size = 10
        spacing = 1.0
        for i in range(-grid_size, grid_size + 1):
            # Horizontal lines
            grid_vertices.extend([i * spacing, 0, -grid_size * spacing])
            grid_vertices.extend([i * spacing, 0, grid_size * spacing])
            # Vertical lines
            grid_vertices.extend([-grid_size * spacing, 0, i * spacing])
            grid_vertices.extend([grid_size * spacing, 0, i * spacing])

        grid_vertices = np.array(grid_vertices, dtype=np.float32)

        self.line_vao = glGenVertexArrays(1)
        line_vbo = glGenBuffers(1)

        glBindVertexArray(self.line_vao)
        glBindBuffer(GL_ARRAY_BUFFER, line_vbo)
        glBufferData(GL_ARRAY_BUFFER, grid_vertices.nbytes, grid_vertices, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * 4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        glBindVertexArray(0)

    def create_transformation_matrix(self, translation, rotation, scale):
        # Translation matrix
        T = np.eye(4, dtype=np.float32)
        T[0, 3] = translation[0]
        T[1, 3] = translation[1]
        T[2, 3] = translation[2]
        
        # Rotation matrices (w radianach)
        rx, ry, rz = np.radians(rotation)
        
        # X rotation
        Rx = np.array([
            [1, 0, 0, 0],
            [0, np.cos(rx), -np.sin(rx), 0],
            [0, np.sin(rx), np.cos(rx), 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        # Y rotation
        Ry = np.array([
            [np.cos(ry), 0, np.sin(ry), 0],
            [0, 1, 0, 0],
            [-np.sin(ry), 0, np.cos(ry), 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        # Z rotation
        Rz = np.array([
            [np.cos(rz), -np.sin(rz), 0, 0],
            [np.sin(rz), np.cos(rz), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        # Scale matrix
        S = np.array([
            [scale[0], 0, 0, 0],
            [0, scale[1], 0, 0],
            [0, 0, scale[2], 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        # Combine: T * Rz * Ry * Rx * S
        return T @ Rz @ Ry @ Rx @ S

    def create_view_matrix(self, eye, center, up):
        eye = np.array(eye, dtype=np.float32)
        center = np.array(center, dtype=np.float32)
        up = np.array(up, dtype=np.float32)
        
        f = center - eye
        f = f / np.linalg.norm(f)
        
        s = np.cross(f, up)
        s = s / np.linalg.norm(s)
        
        u = np.cross(s, f)
        
        view = np.array([
            [s[0], s[1], s[2], -np.dot(s, eye)],
            [u[0], u[1], u[2], -np.dot(u, eye)],
            [-f[0], -f[1], -f[2], np.dot(f, eye)],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        return view

    def create_perspective_matrix(self, fovy, aspect, near, far):
        f = 1.0 / np.tan(np.radians(fovy) / 2.0)
        return np.array([
            [f/aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far+near)/(near-far), (2*far*near)/(near-far)],
            [0, 0, -1, 0]
        ], dtype=np.float32)

    def draw_segment(self, model_matrix, color):
        glUseProgram(self.shader_program)
        
        # Transpose matrices for OpenGL (column-major)
        model_t = model_matrix.T
        view_t = self.view_matrix.T
        proj_t = self.projection_matrix.T
        
        glUniformMatrix4fv(glGetUniformLocation(self.shader_program, "model"), 1, GL_FALSE, model_t)
        glUniformMatrix4fv(glGetUniformLocation(self.shader_program, "view"), 1, GL_FALSE, view_t)
        glUniformMatrix4fv(glGetUniformLocation(self.shader_program, "projection"), 1, GL_FALSE, proj_t)
        glUniform3f(glGetUniformLocation(self.shader_program, "color"), color[0], color[1], color[2])
        
        glBindVertexArray(self.cube_vao)
        glDrawElements(GL_TRIANGLES, 36, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

    def draw_grid(self):
        glUseProgram(self.shader_program)
        
        model = np.eye(4, dtype=np.float32)
        view_t = self.view_matrix.T
        proj_t = self.projection_matrix.T
        
        glUniformMatrix4fv(glGetUniformLocation(self.shader_program, "model"), 1, GL_FALSE, model)
        glUniformMatrix4fv(glGetUniformLocation(self.shader_program, "view"), 1, GL_FALSE, view_t)
        glUniformMatrix4fv(glGetUniformLocation(self.shader_program, "projection"), 1, GL_FALSE, proj_t)
        glUniform3f(glGetUniformLocation(self.shader_program, "color"), 0.3, 0.3, 0.3)
        
        glBindVertexArray(self.line_vao)
        glDrawArrays(GL_LINES, 0, 168)  # 21*4*2 = 168 vertices
        glBindVertexArray(0)

    def render(self, width, height):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Setup view and projection matrices
        self.view_matrix = self.create_view_matrix([4, 4, 10], [0, 0, 0], [0, 1, 0])
        self.projection_matrix = self.create_perspective_matrix(45.0, width/height, 0.1, 100.0)
        
        # Draw grid
        self.draw_grid()
        
        # Robotic arm rendering with proper hierarchical transformations
        
        # Base (czerwony)
        base_matrix = self.create_transformation_matrix([0.0, 0.5, 0.0], [0, angle1, 0], [0.2, 1.0, 0.2])
        self.draw_segment(base_matrix, [1.0, 0.0, 0.0])
        
        # Upper arm (zielony)
        upper_arm_matrix = base_matrix @ self.create_transformation_matrix([0.0, 0.5, 0.0], [0, 0, angle2], [1.0, 1.0, 1.0])
        upper_segment_matrix = upper_arm_matrix @ self.create_transformation_matrix([0.0, 0.5, 0.0], [0, 0, 0], [0.2, 1.0, 0.2])
        self.draw_segment(upper_segment_matrix, [0.0, 1.0, 0.0])
        
        # Forearm (niebieski)
        forearm_matrix = upper_arm_matrix @ self.create_transformation_matrix([0.0, 1.0, 0.0], [0, 0, angle3], [1.0, 1.0, 1.0])
        forearm_segment_matrix = forearm_matrix @ self.create_transformation_matrix([0.0, 0.5, 0.0], [0, 0, 0], [0.2, 1.0, 0.2])
        self.draw_segment(forearm_segment_matrix, [0.0, 0.0, 1.0])
        
        # Wrist (cyan)
        wrist_matrix = forearm_matrix @ self.create_transformation_matrix([0.0, 1.0, 0.0], [angle6, angle5, angle4], [1.0, 1.0, 1.0])
        wrist_segment_matrix = wrist_matrix @ self.create_transformation_matrix([0.0, 0.25, 0.0], [0, 0, 0], [0.2, 0.5, 0.2])
        self.draw_segment(wrist_segment_matrix, [0.0, 1.0, 1.0])
        
        # Left gripper finger (żółty)
        left_finger_matrix = wrist_matrix @ self.create_transformation_matrix([-0.1, 0.5, 0.0], [0, 0, 0], [0.05, 0.2, 0.05])
        self.draw_segment(left_finger_matrix, [1.0, 1.0, 0.0])
        
        # Right gripper finger (żółty)
        right_finger_matrix = wrist_matrix @ self.create_transformation_matrix([0.1, 0.5, 0.0], [0, 0, 0], [0.05, 0.2, 0.05])
        self.draw_segment(right_finger_matrix, [1.0, 1.0, 0.0])

def main():
    pygame.init()
    width, height = 800, 600
    
    # Setup OpenGL context
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
    pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
    pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)

    screen = pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("3D Robot Arm - Core Profile")
    
    # OpenGL settings
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1.0)
    
    print("OpenGL Version:", glGetString(GL_VERSION).decode())
    print("GLSL Version:", glGetString(GL_SHADING_LANGUAGE_VERSION).decode())

    robot = RobotArm()
    clock = pygame.time.Clock()
    
    global angle1, angle2, angle3, angle4, angle5, angle6
    running = True
    
    print("Controls:")
    print("Q/A - Base rotation")
    print("W/S - Upper arm")
    print("E/D - Forearm")
    print("R/F - Wrist roll")
    print("T/G - Wrist pitch") 
    print("Y/H - Wrist yaw")
    print("X - Exit")
    
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_q: angle1 += 5
                elif event.key == K_a: angle1 -= 5
                elif event.key == K_w: angle2 += 5
                elif event.key == K_s: angle2 -= 5
                elif event.key == K_e: angle3 += 5
                elif event.key == K_d: angle3 -= 5
                elif event.key == K_r: angle4 += 5
                elif event.key == K_f: angle4 -= 5
                elif event.key == K_t: angle5 += 5
                elif event.key == K_g: angle5 -= 5
                elif event.key == K_y: angle6 += 5
                elif event.key == K_h: angle6 -= 5
                elif event.key == K_x: running = False
        
        robot.render(width, height)
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()