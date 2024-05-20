import moderngl as mgl
from config import Config
import object_loader
import material_loader
import glm
from PIL import Image

obj_loader = object_loader.ObjectLoader()
loaded_objects = obj_loader.retrieveObjects()

config = Config()

script_path = config.retrieveConfig('script_path')
materials = material_loader.get_materials()

class Material:
    def __init__(self, ctx, diffuse_tex, flip_y, normal_tex, roughness_metal_height_tex, roughness_value, metalicness_value):
        self.ctx = ctx
        self.flip_y = bool(flip_y)
        self.diffuse_tex = self.get_texture(diffuse_tex, self.flip_y)

        self.has_normal = normal_tex != ''

        if self.has_normal:
            self.normal_tex = self.get_texture(normal_tex, self.flip_y)
        else: 
            self.normal_tex = None

        self.has_roughness_metal_height_tex = roughness_metal_height_tex != ''

        if self.has_roughness_metal_height_tex:
            self.roughness_metal_height_tex = self.get_texture(roughness_metal_height_tex, self.flip_y)
        else:
            self.roughness_metal_height_tex = None

        self.roughness_value = roughness_value
        self.metalicness_value = metalicness_value

        # 1 = has the texutre, 0 = doesnt have the texture
        self.norm_rough_metal_height_values = glm.vec4(int(self.has_normal), int(self.has_roughness_metal_height_tex), 0, 0)

    def update_values(self, roughness, metalicness):
        self.roughness_value = roughness
        self.metalicness_value = metalicness
        print([self.roughness_value, self.metalicness_value])

    def get_texture(self, path, x):
        path = f'{script_path}{path}'
        image = Image.open(path)
        if x:
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
        image_data = image.convert("RGB").tobytes()

        width, height = image.size

        texture = self.ctx.texture((width, height), 3, image_data)
        texture.filter = (mgl.LINEAR_MIPMAP_LINEAR, mgl.LINEAR)
        texture.build_mipmaps()
        texture.anisotropy = 32.0

        return texture

class Materials:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        
        self.materials = {}

        for material in materials:
            material_attributes = materials[material]

            self.materials[material] = Material(
                                        ctx=self.ctx,
                                        diffuse_tex=material_attributes['diffuse_tex'],
                                        flip_y=material_attributes['flip_y'],
                                        normal_tex=material_attributes['normal_tex'],
                                        roughness_metal_height_tex=material_attributes['roughness_metal_height_tex'],
                                        roughness_value=material_attributes['roughness_value'],
                                        metalicness_value=material_attributes['metalicness_value'])
        def add_material(): ...
        def edit_material(): ...    

# Legacy loader (still used for skybox)
class Texture:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.shadow_res = 1024
        self.textures = {}
        self.textures[0] = self.get_texture(path=f'{script_path}/textures/img.png')
        self.textures[1] = self.get_texture(path=f'{script_path}/textures/img_1.png')
        self.textures[2] = self.get_texture(path=f'{script_path}/textures/img_2.png')
        self.textures['skybox'] = self.get_texture_cube(dir_path=f'{script_path}/textures/skybox1/', ext='png')
        self.textures['cascade_1'] = self.get_depth_texture()
        self.textures['cascade_2'] = self.get_depth_texture()
        self.textures['cascade_3'] = self.get_depth_texture()
        self.textures['irradiance'] = self.get_texture_cube(dir_path=f'{script_path}/cubemap_renderer/convoluted-', ext='jpg')
        self.textures['reflection'] = self.get_texture_cube(dir_path=f'{script_path}/cubemap_renderer/sharp-', ext='jpg')
        self.textures['brdf_lut'] = self.get_texture(path=f'{script_path}/textures/brdf_lut.png')
        # In form of vbo_name[0], vao_name[1], tex_id[2], tex_path[3], obj_path[4]
        
        
    def get_depth_texture(self):
        depth_texture = self.ctx.depth_texture((self.shadow_res, self.shadow_res))
        depth_texture.repeat_x = False
        depth_texture.repeat_y = False
        return depth_texture

    def get_texture_cube(self, dir_path, ext='png'):
        faces = ['right', 'left', 'top', 'bottom'] + ['front', 'back'][::-1]
        textures = []
        for face in faces:
            image = Image.open(dir_path + f'{face}.{ext}')
            if face in ['right', 'left', 'front', 'back']:
                image = image.transpose(Image.FLIP_LEFT_RIGHT)
            else:
                image = image.transpose(Image.FLIP_TOP_BOTTOM)
            textures.append(image)

        size = textures[0].size
        texture_cube = self.ctx.texture_cube(size, 3)

        for i in range(6):
            texture_data = textures[i].convert("RGB").tobytes()
            texture_cube.write(data=texture_data, face=i)

        texture_cube.build_mipmaps()
        texture_cube.anisotropy = 32.0
        return texture_cube

    def get_texture(self, path):
        image = Image.open(path)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        image_data = image.convert("RGB").tobytes()

        width, height = image.size

        texture = self.ctx.texture((width, height), 3, image_data)
        texture.filter = (mgl.LINEAR_MIPMAP_LINEAR, mgl.LINEAR)
        texture.build_mipmaps()
        texture.anisotropy = 32.0

        return texture
    
    def get_normal_texture(self, path):
        image = Image.open(path)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        image_data = image.convert("RGB").tobytes()

        width, height = image.size

        texture = self.ctx.texture((width, height), 3, image_data)
        texture.filter = (mgl.LINEAR_MIPMAP_LINEAR, mgl.LINEAR)
        texture.build_mipmaps()
        texture.anisotropy = 32.0

        return texture
    
    def destroy(self):
        [tex.release() for tex in self.textures.values()]