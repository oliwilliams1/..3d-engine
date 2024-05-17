import culling
from PIL import Image
import numpy as np
import glm

faces = ['right', 'back', 'left', 'front', 'top', 'bottom']

class SceneRenderer:
    def __init__(self, app):
        self.app = app
        self.cull = culling.Culling(self.app)
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
        self.app.cube_map_render_data['rendering'] = True
        cam_pos = self.app.camera.position # change to cubemap centre pos
        self.app.cube_map_render_data['camera_pos'] = cam_pos

        for face in faces:
            self.app.cube_map_render_data['face'] = face
            color_texture = self.app.ctx.texture(size, 3, dtype='f1')
            depth_texture = depth_texture = self.app.ctx.depth_texture(size)
            cube_fbo = self.app.ctx.framebuffer(color_attachments=[color_texture], depth_attachment=depth_texture)
            cube_fbo.clear()
            cube_fbo.use()
            
            for obj in self.scene.objects.values():
                obj.render_cube(cam_pos, face)
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
        convoluted_size = (512, 512)
        color_texture = self.app.ctx.texture(convoluted_size, 3, dtype='f1')
        convolution_fbo = self.app.ctx.framebuffer(color_attachments=[color_texture])
        convolution_fbo.clear(color=(1, 0, 0))
        convolution_fbo.use()

        self.scene.convoluter.update_face(cam_pos, face, cubemap_texture)
        self.scene.convoluter.render()
        
        data = np.empty((convoluted_size[0], convoluted_size[1], 3), dtype=np.float32)
        data = convolution_fbo.read()
        image = Image.frombytes('RGB', convoluted_size, data=data)

        image = image.transpose(Image.FLIP_TOP_BOTTOM)

        image.save(f'cubemap_renderer/convoluted-{face}.jpg', 'JPEG')
        
        #convolution_fbo.release() #cant release, something to do with imgui??

        self.scene.skybox.on_init()       # to fix a bug, doesnt matter performance
        self.scene.basic_skybox.on_init() # wise, as not rendering real-time

    def render(self):
        self.cull.rendering(self.scene.objects.values())
        self.scene.skybox.render()