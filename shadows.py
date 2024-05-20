import glm

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

    def render(self, rendering_cubemap = False):
        self.update_matricies(rendering_cubemap)
        self.cascade_1_fbo.clear()
        self.cascade_1_fbo.use()
        for obj in self.app.scene.objects.values():
            if obj.cast_shadow:
                obj.render_shadow()
    
    def update_matricies(self, rendering_cubemap):
        light_dir = self.app.light.sun.direction

        if rendering_cubemap == False:
            m_view_camera = self.app.camera.m_view
        else:
            m_view_camera = self.app.cube_map_render_data['m_view']

        cascade_data = [
            [1, 0.1, 10]
        ]

        cascade_matricies = []

        for cascade in cascade_data:
            cascade_near = cascade[1]
            cascade_far = cascade[2]

            cascade_m_proj = glm.perspective(glm.radians(self.app.camera.fov), self.app.camera.aspect_ratio, cascade_near, cascade_far)
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

            proj = glm.ortho(min_x, max_x, min_y, max_y, 0.1, 100)
            view = m_view_light
            
            cascade_matricies.append([proj, view])
        
        temp_proj = []
        for cascade in cascade_matricies:
            temp_proj.append(cascade)

        self.app.light.m_c1_proj = temp_proj[0][0]
        self.app.light.m_view_light = temp_proj[0][1]

    def destroy(self):
        self.cascade_1_fbo.release()