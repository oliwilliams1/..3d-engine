import glm

ndc_corners = [
    glm.vec4(-1, -1, -1, 1),
    glm.vec4(1, -1, -1, 1),
    glm.vec4(-1, 1, -1, 1),
    glm.vec4(1, 1, -1, 1),
    glm.vec4(-1, -1, 1, 1),
    glm.vec4(1, -1, 1, 1),
    glm.vec4(-1, 1, 1, 1),
    glm.vec4(1, 1, 1, 1)
]

def calculate_bounding_sphere(points, center): 
    max_distance = 0
    for point in points:
        distance = glm.distance(point, center)
        max_distance = max(max_distance, distance)
    
    return max_distance

def calculate_frustum_corners(view_matrix, proj_matrix):
    combined_matrix = proj_matrix * view_matrix
    inverse_matrix = glm.inverse(combined_matrix)
    world_corners = [inverse_matrix * corner for corner in ndc_corners]
    return [glm.vec3(corner) / corner.w for corner in world_corners]

class ShadowRenderer():
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.cascade_1_texture = self.app.mesh.texture.textures['cascade_1']
        self.cascade_1_fbo = self.ctx.framebuffer(depth_attachment=self.cascade_1_texture)

    def render(self):
        self.update_matricies()
        self.cascade_1_fbo.clear()
        self.cascade_1_fbo.use()
        for obj in self.app.scene.objects.values():
            if obj.cast_shadow:
                obj.render_shadow()
    
    def update_matricies(self):
        cascade_near, cascade_far = 0.1, 10
        light_dir = self.app.light.sun.direction
        cascade1_m_proj = glm.perspective(glm.radians(self.app.camera.fov), self.app.camera.aspect_ratio, cascade_near, cascade_far)
        corners = calculate_frustum_corners(self.app.camera.m_view, cascade1_m_proj)
        #print(len(corners))
        center = sum(corners) / len(corners)
        radius = calculate_bounding_sphere(corners, center)
        self.app.light.m_proj_light = glm.ortho(-radius, radius, -radius, radius, 0.1, 100)
        self.app.light.m_view_light = glm.lookAt(center + 50 * light_dir, center + glm.vec3(0.001), glm.vec3(0, 1, 0))

        self.app.scene.objects['cas_1_centre_point'].pos = center
        self.app.scene.objects['cas_1_centre_point'].scale = glm.vec3(radius) # m_moodel later updated by imgui

    def destroy(self):
        self.cascade_1_fbo.release()