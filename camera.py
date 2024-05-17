import glm
from config import Config
import glfw

config = Config()

FOV = config.retrieveConfig('FOV')
NEAR = config.retrieveConfig('NEAR')
FAR = config.retrieveConfig('FAR')
SPEED = 5
SENSITIVITY = 0.1

is_paused = False

class Camera:
    def __init__(self, app, position=(0, 0, 4), yaw=-90, pitch=0):
        self.app = app
        self.aspect_ratio = app.WIN_SIZE[0] / app.WIN_SIZE[1]
        self.position = glm.vec3(position)
        self.fov = FOV
        self.up = glm.vec3(0, 1, 0)
        self.right = glm.vec3(1, 0, 0)
        self.forward = glm.vec3(0, 0, -1)
        self.yaw = yaw
        self.pitch = pitch
        self.is_jumping = False
        self.is_flying = True
        self.is_falling = False
        self.time_since_last_switch = 0

        # view matrix
        self.m_view = self.get_view_matrix()
        # projection matrix
        self.m_proj = self.get_projection_matrix()


    def rotate(self):
        rel_x, rel_y = self.app.mouse_delta
        self.yaw += rel_x * SENSITIVITY
        self.pitch -= rel_y * SENSITIVITY
        self.pitch = max(-89, min(89, self.pitch))

    def update_camera_vectors(self):
        yaw, pitch = glm.radians(self.yaw), glm.radians(self.pitch)

        cos_pitch = glm.cos(pitch)
        sin_pitch = glm.sin(pitch)
        cos_yaw = glm.cos(yaw)
        sin_yaw = glm.sin(yaw)

        self.forward = glm.vec3(cos_yaw * cos_pitch, sin_pitch, sin_yaw * cos_pitch)

        right_up = glm.cross(self.forward, glm.vec3(0, 1, 0))
        self.right = glm.normalize(right_up)
        self.up = glm.normalize(glm.cross(self.right, self.forward))

    def update(self):
        if not is_paused:
            self.move()
            if self.app.get_mouse_button_state(glfw.MOUSE_BUTTON_2):
                self.rotate()
            self.update_camera_vectors()
            self.m_view = self.get_view_matrix()

    def move(self):
        velocity = SPEED * self.app.delta_time
        
        if self.app.get_key_state(glfw.KEY_W):
            self.position += self.forward * velocity
        if self.app.get_key_state(glfw.KEY_S):
            self.position -= self.forward * velocity
        if self.app.get_key_state(glfw.KEY_A):
            self.position -= self.right * velocity
        if self.app.get_key_state(glfw.KEY_D):
            self.position += self.right * velocity
        if self.app.get_key_state(glfw.KEY_E):
            self.position += self.up * velocity
        if self.app.get_key_state(glfw.KEY_Q):
            self.position -= self.up * velocity
        
    def get_view_matrix(self):
        return glm.lookAt(self.position, self.position + self.forward, self.up)

    def get_projection_matrix(self):
        return glm.perspective(glm.radians(FOV), self.aspect_ratio, NEAR, FAR)
