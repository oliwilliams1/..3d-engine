import numpy as np
import math
import glm
from config import Config
config = Config()
import culling_calc
import math


FOV = config.retrieveConfig('FOV')
NEAR = config.retrieveConfig('NEAR')
FAR = config.retrieveConfig('FAR')

class Culling:
    def __init__(self, app):
        self.app = app
        self.aspect = app.WIN_SIZE[0] / app.WIN_SIZE[1]
        self.frustum_vertices = []  
        min_point = glm.vec3(-23.8501, -57.9351, -24.729)
        max_point = glm.vec3(145.233, 8.28434, 43.0882)
        self.bounding_box = (min_point, max_point)
        self.camera = self.app.camera
        self.fov = FOV
        self.near = NEAR
        self.far = FAR
        self.i = 0
    
    def rendering(self, objects):
        position = self.app.camera.position
        yaw_deg = self.app.camera.yaw
        pitch_deg = self.app.camera.pitch
        right = self.app.camera.right
        up = self.app.camera.up
        aspect_ratio = self.app.camera.aspect_ratio
        culling_calc.culling(objects, position, yaw_deg, pitch_deg, right, up, aspect_ratio, FOV, NEAR, FAR)