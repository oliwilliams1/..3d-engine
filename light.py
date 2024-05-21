import glm

ortho_1_width = 20 # orhtho width
epsilon = glm.epsilon()

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
        # matrices
        self.proj_matrices = []
        self.view_matrices = []
        self.dummy_matrices()

    def dummy_matrices(self):
        self.proj_matrices.append(glm.ortho(-ortho_1_width, ortho_1_width, -ortho_1_width, ortho_1_width, 0.1, 100))
        self.view_matrices.append(glm.lookAt(self.sun.direction, glm.vec3(0), glm.vec3(0, 1, 0)))
