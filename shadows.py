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
        m_view = self.app.camera.m_view
        m_proj = glm.perspective(glm.radians(self.app.camera.fov), self.app.camera.aspect_ratio, 0.1, 15)

        corners = calculate_frustum_corners(m_view, m_proj)

        center = sum(corners) / len(corners)

        light_dir = self.app.light.sun.direction
        m_view_light = glm.lookAt(center + 50 * light_dir, center + glm.epsilon(), glm.vec3(0, 1, 0))

        cam_space_corners = [glm.vec4(corner, 1) * m_view_light for corner in corners]

        x_verts = [corner.y for corner in cam_space_corners]
        y_verts = [corner.z for corner in cam_space_corners]
        z_verts = [corner.x for corner in cam_space_corners]
        min_x, max_x = min(x_verts), max(x_verts)
        min_y, max_y = min(y_verts), max(y_verts)
        min_z, max_z = min(z_verts), max(z_verts)

        z_mult = 10
        if min_z < 0:
            min_z *= z_mult
        else:
            min_z /= z_mult
        if max_z < 0:
            max_z /= z_mult
        else:
            max_z *= z_mult


        self.app.light.m_proj_light = glm.ortho(min_x, max_x, min_y, max_y, min_z, max_z)
        self.app.light.m_view_light = m_view_light

    def destroy(self):
        self.cascade_1_fbo.release()