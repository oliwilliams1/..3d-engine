import glm

class Sun:
    def __init__(self, color=(1, 1, 1)):
        self.color = glm.vec3(color)
        self.direction = glm.vec3(0, 1, 0)
        # intensities
        self.Ia = 0.18 * self.color  # ambient
        self.Id = 1.0 * self.color  # diffuse
        self.Is = 1.5 * self.color  # specular

class Light:
    def __init__(self):
        self.sun = Sun()
        self.position = glm.vec3(1, 50, -1)
        self.direction = glm.vec3(0, 0, 0)
        # view matrix
        self.m_view_light = self.get_view_matrix()

    def get_view_matrix(self):
        return glm.lookAt(self.position, self.direction, glm.vec3(0, 1, 0))