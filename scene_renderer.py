from PIL import Image
import numpy as np
import glm

faces = ['right', 'back', 'left', 'front', 'top', 'bottom']

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

def get_view_matrix(position, face):
    match face:
        case 'right':
            m_view = glm.lookAt(position, position + glm.vec3(1, 0, 0) + epsilon, glm.vec3(0, 1, 0))
        case 'back':
            m_view = glm.lookAt(position, position + glm.vec3(0, 0, 1) + epsilon, glm.vec3(0, 1, 0))
        case 'left':
            m_view = glm.lookAt(position, position + glm.vec3(-1, 0, 0) + epsilon, glm.vec3(0, 1, 0))
        case 'front':
            m_view = glm.lookAt(position, position + glm.vec3(0, 0, -1) + epsilon, glm.vec3(0, 1, 0))
        case 'top':
            m_view = glm.lookAt(position, position + glm.vec3(0, 1, 0) + epsilon, glm.vec3(0, 0, 1))
        case 'bottom':
            m_view = glm.lookAt(position, position + glm.vec3(0, -1, 0) + epsilon, glm.vec3(0, 0, -1))
    return m_view

class SceneRenderer:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.mesh = app.mesh
        self.scene = app.scene
        
    def get_texture_cube(self):
        faces = ['right', 'left', 'top', 'bottom'] + ['front', 'back'][::-1]
        textures = []
        for face in faces:
            image = Image.open(f'cubemap_renderer/sharp-{face}.jpg')
            if face in ['right', 'left', 'top', 'bottom']:
                image = image.transpose(Image.FLIP_LEFT_RIGHT)
            else:
                image = image.transpose(Image.FLIP_TOP_BOTTOM)
            textures.append(image)
        
        size = textures[0].size
        texture_cube = self.app.ctx.texture_cube(size, 3)

        for i in range(6):
            texture_data = textures[i].convert("RGB").tobytes()
            texture_cube.write(data=texture_data, face=i)
        
        return texture_cube
    
    def render_cube(self, size):
        cam_pos = self.app.camera.position # make sure center of cubemap is where cam is
        self.app.cube_map_render_data['rendering'] = True
        self.app.cube_map_render_data['camera_pos'] = cam_pos # tell objects states

        for face in faces:
            self.app.cube_map_render_data['face'] = face
            self.app.cube_map_render_data['m_view'] = get_view_matrix(self.app.camera.position, face)
            
            self.app.shadow_renderer.render(True) # True, rendering with custom view matrix

            color_texture = self.app.ctx.texture(size, 3, dtype='f1')
            depth_texture = depth_texture = self.app.ctx.depth_texture(size)
            cube_fbo = self.app.ctx.framebuffer(color_attachments=[color_texture], depth_attachment=depth_texture)
            cube_fbo.clear()
            cube_fbo.use()

            for obj in self.scene.objects.values():
                obj.render_cube()

            self.scene.basic_skybox.render()

            data = np.empty((size[0], size[1], 3), dtype=np.float32)
            data = cube_fbo.read()
            image = Image.frombytes('RGB', size, data=data)
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            image.save(f'cubemap_renderer/sharp-{face}.jpg', 'JPEG')

        self.app.cube_map_render_data['rendering'] = False 

        cubemap_texture = self.get_texture_cube()

        for face in faces:
            self.convolute_cubemap(cam_pos, face, cubemap_texture)

    def convolute_cubemap(self, cam_pos, face, cubemap_texture):
        convoluted_render_size = (512, 512)
        color_texture = self.app.ctx.texture(convoluted_render_size, 3, dtype='f1')
        convolution_fbo = self.app.ctx.framebuffer(color_attachments=[color_texture])
        convolution_fbo.clear(color=(1, 0, 0))
        convolution_fbo.use()

        self.scene.convoluter.update_face(cam_pos, face, cubemap_texture)
        self.scene.convoluter.render()
        
        data = np.empty((convoluted_render_size[0], convoluted_render_size[1], 3), dtype=np.float32)
        data = convolution_fbo.read()
        image = Image.frombytes('RGB', convoluted_render_size, data=data)

        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        image.save(f'cubemap_renderer/convoluted-{face}.jpg', 'JPEG')
        
        #convolution_fbo.release() #cant release, something to do with imgui??

        self.scene.skybox.on_init()       # to fix a bug, doesnt matter performance
        self.scene.basic_skybox.on_init() # wise, as not rendering real-time

    def cull(self, objects):
        m_view = self.app.camera.m_view
        m_proj = self.app.camera.m_proj
        frustum_vertices = calculate_frustum_corners(m_view, m_proj)
        near_plane_normal = glm.cross(frustum_vertices[2] - frustum_vertices[1], frustum_vertices[1] - frustum_vertices[0])
        near_plane_point = frustum_vertices[0]
        for obj in objects:
            obj_pos = glm.vec3(obj.pos)
            bounding_box = obj.bounding_box
            for corner in bounding_box:
                if glm.dot((obj_pos + corner) - near_plane_point, near_plane_normal) > 0:
                    obj.render()
                    break
            


    def render(self):
        self.cull(self.scene.objects.values())
        self.scene.skybox.render()