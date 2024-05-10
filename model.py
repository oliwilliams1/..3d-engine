import moderngl as mgl
import glm
import object_loader
import math
import struct

obj_loader = object_loader.ObjectLoader()
loaded_objects = obj_loader.retrieveObjects()

models = {}

lights = []
num_lights = 0

def init_lights():
    global lights, num_lights

    light1 = {
        'position': glm.vec3(-15, 15, -12),
        'colour': glm.vec3(1.0, 0.0, 0.0),
        'intensity': struct.pack('f', 1.0),
        'range': struct.pack('f', 10.0)
    }
    

    light2 = {
        'position': glm.vec3(0, 15, -12),
        'colour': glm.vec3(0.0, 1.0, 0.0),
        'intensity': struct.pack('f', 1.0),
        'range': struct.pack('f', 10.0)
    }

    light3 = {
        'position': glm.vec3(15, 15, -12),
        'colour': glm.vec3(0.0, 0.0, 1.0),
        'intensity': struct.pack('f', 1.0),
        'range': struct.pack('f', 10.0)
    }
    
    light4 = {
        'position': glm.vec3(0, 2, 4),
        'colour': glm.vec3(1.0, 0.0, 1.0),
        'intensity': struct.pack('f', 6.9),
        'range': struct.pack('f', 5.0)
    }
    # Add the lights to the list
    lights.append(light1)
    lights.append(light2)
    lights.append(light3)
    lights.append(light4)

    num_lights = len(lights)

def min_max_to_bound(bound):
    min = bound[0]
    max = bound[1]
    vertices = []
    minx = min[0]
    miny = min[1]
    minz = min[2]
    maxx = max[0]
    maxy = max[1]
    maxz = max[2]

    vertices.append(glm.vec3(minx, miny, minz))
    vertices.append(glm.vec3(maxx, miny, minz))
    vertices.append(glm.vec3(maxx, miny, maxz))
    vertices.append(glm.vec3(minx, miny, maxz))
    vertices.append(glm.vec3(minx, maxy, minz))
    vertices.append(glm.vec3(maxx, maxy, minz))
    vertices.append(glm.vec3(maxx, maxy, maxz))
    vertices.append(glm.vec3(minx, maxy, maxz))

    return vertices

def get_view_matrix(position, face):
    match face:
        case 'right':
            m_view = glm.lookAt(position, position + glm.vec3(1, 0, 0), glm.vec3(0, 1, 0))
        case 'back':
            m_view = glm.lookAt(position, position + glm.vec3(0, 0, 1), glm.vec3(0, 1, 0))
        case 'left':
            m_view = glm.lookAt(position, position + glm.vec3(-1, 0, 0), glm.vec3(0, 1, 0))
        case 'front':
            m_view = glm.lookAt(position, position + glm.vec3(0, 0, -1), glm.vec3(0, 1, 0))
        case 'top':
            m_view = glm.lookAt(position, position + glm.vec3(0, 1, 0), glm.vec3(0, 0, 1))
        case 'bottom':
            m_view = glm.lookAt(position, position + glm.vec3(0, -1, 0), glm.vec3(0, 0, -1))
    return m_view

class BaseModel:
    def __init__(self, app, vao_name, tex_id, pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), display_name='Untitled Object'):
        self.app = app
        self.pos = pos
        self.vao_name = vao_name
        self.rot = glm.vec3([glm.radians(a) for a in rot])
        self.scale = scale
        self.m_model = self.get_model_matrix()
        self.display_name = display_name
        if 'skybox' in vao_name or vao_name == 'convolution':
            self.bounding_box = None
            self.vao = app.mesh.vao.vaos[vao_name]
        else: 
            self.bounding_box = obj_loader.getAABB(vao_name)
            self.bounding_box = min_max_to_bound(self.bounding_box)
            self.vao = app.mesh.vao.vaos[f'{vao_name}_high']
            self.cube_vao = app.mesh.vao.vaos[f'{vao_name}_low']
        
        self.tex_id = tex_id
        self.program = self.vao.program
        self.camera = self.app.camera

    def update(self): ...

    def get_model_transformations(self):
        return [self.pos, self.rot, self.scale]

    def get_model_matrix(self):
        m_model = glm.mat4()
        # translate
        m_model = glm.translate(m_model, self.pos)
        # rotate
        m_model = glm.rotate(m_model, self.rot.z, glm.vec3(0, 0, 1))
        m_model = glm.rotate(m_model, self.rot.y, glm.vec3(0, 1, 0))
        m_model = glm.rotate(m_model, self.rot.x, glm.vec3(1, 0, 0))
        # scale
        m_model = glm.scale(m_model, self.scale)
        self.m_model_perm = m_model
        return m_model

    def render(self):
        self.update()
        self.vao.render()

class ExtendedBaseModel(BaseModel):
    def __init__(self, app, vao_name, tex_id, pos, rot, scale, display_name):
        super().__init__(app, vao_name, tex_id, pos, rot, scale, display_name)
        self.cube_program = self.cube_vao.program # only for editor
        self.init_cubemap() # only for editor
        self.on_init()
        self.light1pos = 15
        self.iteras = 0

    def update(self):
        self.update_pbr_values()
        self.depth_texture.use(location=0) #-- fixes a weird bug with imgui, dont keep in final version?
        self.diffuse.use(location=1)
        
        self.program['norm_rough_metal_height_values'].write(self.norm_rough_metal_height_values)
        self.program['mat_values'].write(self.mat_values)

        if self.uses_normal:
            self.normal.use(location=2)

        self.program['camPos'].write(self.camera.position)
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)
        self.program['static_lights[0].position'].write(glm.vec3(-15, self.light1pos + math.sin(self.iteras/100)*3, -12))
        self.program['static_lights[1].position'].write(glm.vec3(0, self.light1pos + math.sin(self.iteras/100+1)*3, -12))
        self.program['static_lights[2].position'].write(glm.vec3(15, self.light1pos + math.sin(self.iteras/100+2)*3, -12))
        self.program['static_lights[3].position'].write(glm.vec3(0, 2 + math.sin(self.iteras/100) * 2, 2))
        self.iteras += 1

    def render_cube(self, cam_pos, face):
        self.update_cubemap(cam_pos, face)
        self.cube_vao.render()

    def update_shadow(self):
        self.shadow_program['m_model'].write(self.m_model)

    def render_shadow(self):
        self.update_shadow()
        self.shadow_vao.render()

    def update_pbr_values(self):
        self.norm_rough_metal_height_values = self.app.materials[self.tex_id].norm_rough_metal_height_values
        self.mat_values = glm.vec2(self.app.materials[self.tex_id].roughness_value, self.app.materials[self.tex_id].metalicness_value)
        self.uses_normal = self.app.materials[self.tex_id].norm_rough_metal_height_values.x
    
    def update_cubemap(self, cam_pos, face):
        self.update_pbr_values()
        self.depth_texture.use(location=0)
        self.diffuse.use(location=1)

        self.cube_program['norm_rough_metal_height_values'].write(self.norm_rough_metal_height_values)
        self.cube_program['mat_values'].write(self.mat_values)

        if self.uses_normal:
            self.normal.use(location=2)

        self.cube_program['camPos'].write(cam_pos)
        self.cube_program['m_view'].write(get_view_matrix(self.app.camera.position, face))
        self.cube_program['m_model'].write(self.m_model)

    def init_cubemap(self):
        self.update_pbr_values()
        # number of lights
        self.cube_program['numLights'].value = num_lights

        self.cube_program['m_view_light'].write(self.app.light.m_view_light)
        # resolution
        self.cube_program['u_resolution'].write(glm.vec2(self.app.WIN_SIZE))
        # depth texture
        self.depth_texture = self.app.mesh.texture.textures['depth_texture']
        self.cube_program['shadowMap'] = 0
        self.depth_texture.use(location=0)
        # shadow
        self.shadow_vao = self.app.mesh.vao.vaos['shadow_' + self.vao_name]
        self.shadow_program = self.shadow_vao.program
        self.shadow_program['m_proj'].write(self.camera.m_proj)
        self.shadow_program['m_view_light'].write(self.app.light.m_view_light)
        self.shadow_program['m_model'].write(self.m_model)

        # textures
        self.diffuse = self.app.materials[self.tex_id].diffuse_tex
        self.cube_program['diff_0'] = 1
        self.diffuse.use(location=1)

        #pbr values
        self.cube_program['mat_values'].write(glm.vec2(self.app.materials[self.tex_id].roughness_value, self.app.materials[self.tex_id].metalicness_value))

        #self.program['maps.is_normal_loaded'].value = 1

        if self.app.materials[self.tex_id].has_normal:
            self.normal = self.app.materials[self.tex_id].normal_tex
            self.cube_program['maps.normal_0'] = 2
            self.normal.use(location=2)

        self.cube_program['norm_rough_metal_height_values'].write(self.app.materials[self.tex_id].norm_rough_metal_height_values)
        # skybox
        self.irradiance = self.app.mesh.texture.textures['irradiance']
        self.cube_program['u_texture_skybox'] = 3
        self.irradiance.use(location=3)       

        # mvp
        self.cube_program['m_shadow_proj'].write(self.app.camera.m_proj)
        self.cube_program['m_proj'].write(glm.perspective(glm.radians(90), 1, 0.1, 100)) # cubemap projection
        self.cube_program['m_view'].write(self.camera.m_view)
        self.cube_program['m_model'].write(self.m_model)
        # sun
        self.cube_program['sun.direction'].write(self.app.light.sun.direction)
        self.cube_program['sun.Ia'].write(self.app.light.sun.Ia)
        self.cube_program['sun.Id'].write(self.app.light.sun.Id)
        self.cube_program['sun.Is'].write(self.app.light.sun.Is)

        # lights
        for i, light in enumerate(lights):
            self.cube_program[f'static_lights[{i}].position'].write(bytes(light['position']))
            self.cube_program[f'static_lights[{i}].colour'].write(light['colour'])
            self.cube_program[f'static_lights[{i}].intensity'].write(light['intensity'])
            self.cube_program[f'static_lights[{i}].range'].write(light['range'])
    
    def on_init(self):
        self.update_pbr_values()
        # number of lights
        self.program['numLights'].value = num_lights

        self.program['m_view_light'].write(self.app.light.m_view_light)
        # resolution
        self.program['u_resolution'].write(glm.vec2(self.app.WIN_SIZE))
        # depth texture
        self.depth_texture = self.app.mesh.texture.textures['depth_texture']
        self.program['shadowMap'] = 0
        self.depth_texture.use(location=0)
        # shadow
        self.shadow_vao = self.app.mesh.vao.vaos['shadow_' + self.vao_name]
        self.shadow_program = self.shadow_vao.program
        self.shadow_program['m_proj'].write(self.camera.m_proj)
        self.shadow_program['m_view_light'].write(self.app.light.m_view_light)
        self.shadow_program['m_model'].write(self.m_model)

        # textures
        self.diffuse = self.app.materials[self.tex_id].diffuse_tex
        self.program['diff_0'] = 1
        self.diffuse.use(location=1)

        #pbr values
        self.program['mat_values'].write(glm.vec2(self.app.materials[self.tex_id].roughness_value, self.app.materials[self.tex_id].metalicness_value))

        #self.program['maps.is_normal_loaded'].value = 1

        if self.app.materials[self.tex_id].has_normal:
            self.normal = self.app.materials[self.tex_id].normal_tex
            self.program['maps.normal_0'] = 2
            self.normal.use(location=2)

        self.program['norm_rough_metal_height_values'].write(self.app.materials[self.tex_id].norm_rough_metal_height_values)
        
        # skybox
        self.cubemap = self.app.mesh.texture.textures['irradiance']
        self.program['u_irradiance'] = 3
        self.cubemap.use(location=3)

        self.reflection = self.app.mesh.texture.textures['reflection']
        self.program['u_reflection'] = 4
        self.reflection.use(location=4)

        self.brdf_lut = self.app.mesh.texture.textures['brdf_lut']
        self.program['u_brdf_lut'] = 5
        self.brdf_lut.use(location=5)

        # mvp
        self.program['m_proj'].write(self.camera.m_proj)
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)
        # sun
        #self.program['sun.position'].write(self.app.light.position)
        self.program['sun.direction'].write(self.app.light.sun.direction)
        self.program['sun.Ia'].write(self.app.light.sun.Ia)
        self.program['sun.Id'].write(self.app.light.sun.Id)
        self.program['sun.Is'].write(self.app.light.sun.Is)

        # lights
        for i, light in enumerate(lights):
            self.program[f'static_lights[{i}].position'].write(bytes(light['position']))
            self.program[f'static_lights[{i}].colour'].write(light['colour'])
            self.program[f'static_lights[{i}].intensity'].write(light['intensity'])
            self.program[f'static_lights[{i}].range'].write(light['range'])


class Cube(ExtendedBaseModel):
    def __init__(self, app, vao_name='cube', tex_id=0, pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
        super().__init__(app, vao_name, tex_id, pos, rot, scale)

class MovingCube(Cube):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update(self):
        self.m_model = self.get_model_matrix()
        super().update()

def create_static_custom_class(class_name, base_class, custom_attrs):
    class CustomClass(base_class):
        def __init__(self, app, pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), **kwargs):
            super().__init__(app, **custom_attrs, pos=pos, rot=rot, scale=scale, **kwargs)

        def update_m_model(self):
            self.m_model = self.get_model_matrix()
            super().update()

    CustomClass.__name__ = class_name
    return CustomClass

for obj in loaded_objects:
    obj_name = loaded_objects[obj]["label"]
    attrs = {'vao_name': obj_name}
    models[obj_name] = create_static_custom_class(obj_name, ExtendedBaseModel, attrs)

"""class Sphere(ExtendedBaseModel):
    def __init__(self, app, vao_name='sphere', tex_id='sphere',
                 pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
        super().__init__(app, vao_name, tex_id, pos, rot, scale)
    
    def update(self):
        self.m_model = self.get_model_matrix()
        super().update()"""

class SkyBox(BaseModel):
    def __init__(self, app, vao_name='skybox', tex_id='skybox',
                 pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1),
                 display_name='skybox'):
        super().__init__(app, vao_name, tex_id, pos, rot, scale, display_name)
        self.on_init()

    def update(self):
        if self.app.cube_map_render_data['rendering']: # rendeirng the cubemap
            cam_pos = self.app.cube_map_render_data['camera_pos']
            face = self.app.cube_map_render_data['face']
            self.program['m_view'].write(glm.mat4(glm.mat3(get_view_matrix(cam_pos, face))))
        else:
            self.program['m_view'].write(glm.mat4(glm.mat3(self.camera.m_view)))

    def on_init(self):
        # texture
        self.texture = self.app.mesh.texture.textures[self.tex_id]
        self.program['u_texture_skybox'] = 0
        self.texture.use(location=0)
        # mvp
        self.program['m_proj'].write(glm.perspective(glm.radians(90), 1, 0.1, 100))
        self.program['m_view'].write(glm.mat4(glm.mat3(self.camera.m_view)))

class Convolution(BaseModel):
    def __init__(self, app, vao_name='convolution', tex_id='convolution',
                 pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1),
                 display_name='convolution'):
        super().__init__(app, vao_name, tex_id, pos, rot, scale, display_name)
        self.on_init()

    def update_face(self, cam_pos, face, cubemap):
        self.texture = cubemap
        self.program['enviroment_map'] = 0
        self.texture.use(location=0)
        self.program['m_view'].write(glm.mat4(glm.mat3(get_view_matrix(cam_pos, face))))

    def on_init(self):
        self.program['m_proj'].write(glm.perspective(glm.radians(90), 1, 0.1, 100))

    def on_init(self):
        self.program['m_proj'].write(glm.perspective(glm.radians(90), 1, 0.1, 100)) 

class AdvancedSkyBox(BaseModel):
    def __init__(self, app, vao_name='advanced_skybox', tex_id='skybox',
                 pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1),
                 display_name='skybox'):
        super().__init__(app, vao_name, tex_id, pos, rot, scale, display_name)
        self.on_init()
        self.cube_proj = glm.perspective(glm.radians(90), 1, 0.1, 100)

    def update(self):
        m_view = glm.mat4(glm.mat3(self.camera.m_view))
        self.program['m_invProjView'].write(glm.inverse(self.camera.m_proj * m_view))

    def on_init(self):
        m_view = glm.mat4(glm.mat3(self.camera.m_view))
        self.program['m_invProjView'].write(glm.inverse(self.camera.m_proj * m_view))
        # texture
        self.texture = self.app.mesh.texture.textures[self.tex_id]
        self.program['u_texture_skybox'] = 0
        self.texture.use(location=0)