import glm
import culling
import time
epsilon = glm.epsilon()

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

def calculate_frustum_corners(view_matrix, proj_matrix):
    combined_matrix = proj_matrix * view_matrix
    inverse_matrix = glm.inverse(combined_matrix)
    world_corners = [inverse_matrix * corner for corner in ndc_corners]
    return [glm.vec3(corner) / corner.w for corner in world_corners]

class ShadowRenderer():
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.c1_texture = self.app.mesh.texture.textures['cascade_1']
        self.c1_fbo = self.ctx.framebuffer(depth_attachment=self.c1_texture)
        self.c2_texture = self.app.mesh.texture.textures['cascade_2']
        self.c2_fbo = self.ctx.framebuffer(depth_attachment=self.c2_texture)
        self.c3_texture = self.app.mesh.texture.textures['cascade_3']
        self.c3_fbo = self.ctx.framebuffer(depth_attachment=self.c3_texture)
        
        self.cascade_fbos = [self.c1_fbo, self.c2_fbo, self.c3_fbo]

    def render(self, rendering_cubemap = False):
        full_cascade_data = [
            [0, 0.1, 7.5, 0.1, 100], # cascade number, subfrusta near
            [1, 7.45, 30, -50, 100],  # subfrasta far, cascade near
            [2, 29.95, 100, -100, 200]  # cascade far
        ]
        for cascade_data in full_cascade_data:
            view, proj = self.update_matricies(rendering_cubemap, cascade_data)
            self.cascade_fbos[cascade_data[0]].clear()
            self.cascade_fbos[cascade_data[0]].use()
            culling.render_culled(self.app.scene.objects.values(), view, proj, cast_shadow_check=True, cascade=cascade_data[0])
    
    def update_matricies(self, rendering_cubemap, cascade_data):
        light_dir = self.app.light.sun.direction

        if rendering_cubemap == False:
            m_view_camera = self.app.camera.m_view
        else:
            m_view_camera = self.app.cube_map_render_data['m_view']

        cascade, sf_near, sf_far, c_near, c_far = cascade_data

        cascade_m_proj = glm.perspective(glm.radians(self.app.camera.fov), self.app.camera.aspect_ratio, sf_near, sf_far)
        frust_verts = calculate_frustum_corners(m_view_camera, cascade_m_proj)
        center = sum(frust_verts) / len(frust_verts)
        m_view_light = glm.lookAt(center + 50 * light_dir, center + epsilon, glm.vec3(0, 1, 0))

        transformed_verts = []
        for vert in frust_verts:
            vert = glm.vec4(vert, 1)
            vert = m_view_light * vert
            transformed_verts.append(vert)  
        
        x_verts = [vert.x for vert in transformed_verts]
        y_verts = [vert.y for vert in transformed_verts]
        min_x = min(x_verts)
        max_x = max(x_verts)
        min_y = min(y_verts)
        max_y = max(y_verts)

        proj = glm.ortho(min_x, max_x, min_y, max_y, c_near, c_far)
        view = m_view_light
                
        self.app.light.proj_matrices[cascade] = proj
        self.app.light.view_matrices[cascade] = view

        return [view, proj]
        
    def destroy(self):
        for fbo in self.cascade_fbos:
            fbo.release()