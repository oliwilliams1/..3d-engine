import glm

ortho_1_width = 20 # orhtho width

class Sun:
    def __init__(self, colour=(1, 1, 1)):
        self.colour = glm.vec3(colour)
        self.unormalized_direction = (1, 2, 0.5)
        self.direction = glm.normalize(glm.vec3(self.unormalized_direction))
        # intensities
        self.Ia = glm.vec1(0.18)
        self.Id = glm.vec1(1.5)
        self.Is = glm.vec1(2)

class Light:
    def __init__(self):
        self.sun = Sun()
        self.direction = self.sun.direction
        # matricies
        self.m_proj_light = self.get_proj_matrix()
        self.m_view_light = None
        self.update_view_matrix(glm.vec3(0, 0, 0))

    def get_proj_matrix(self):
        return glm.ortho(-ortho_1_width, ortho_1_width, -ortho_1_width, ortho_1_width, 0.1, 500)
    
    def update_view_matrix(self, campos):
        self.m_view_light = glm.lookAt(campos + 100 * self.direction, campos + glm.vec3(0.001, 0.001, 0.001), glm.vec3(0, 1, 0))