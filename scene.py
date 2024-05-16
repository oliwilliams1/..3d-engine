from model import *
import yaml
import os
from config import Config

config = Config()

script_path = config.retrieveConfig('script_path')

scene_objects = []

def load_scene_objects():
    script_path = os.path.dirname(os.path.abspath(__file__))
    scene_file_path = os.path.join(script_path, 'config/scene.cfg')

    with open(scene_file_path, 'r') as file:
        data = yaml.safe_load(file)

    scene_objects = []
    for name, attributes in data.items():
        temp_obj = {
            'display_name': name,
            'object_name': str(attributes['object_name']),
            'material': str(attributes['material']),
            'pos': tuple(attributes['position']),
            'rot': tuple(attributes['rotation']),
            'scale': tuple(attributes['scale']),
            'cast_shadow': bool(attributes['cast_shadow'])
        }
        scene_objects.append(temp_obj)

    return scene_objects

class Scene:
    def __init__(self, app):
        self.app = app
        self.objects = {}
        self.scene_objects = load_scene_objects()
        #self.chunk_size = int(config.retrieveConfig('CHUNK_SIZE'))
        #import physics
        #global physics_objects
        #physics_objects = physics.objects
        # load scene
        self.load()
        # skybox
        self.skybox = AdvancedSkyBox(app)
        self.basic_skybox = SkyBox(app)
        self.convoluter = Convolution(app)

    def add_object(self, obj, display_name):
        self.objects[display_name] = obj

    def load(self):
        app = self.app
        add = self.add_object
        #self.physics_objects = {}
        for obj in self.scene_objects:
            display_name = obj['display_name']
            object_name = obj['object_name']
            object_material = obj['material']
            if object_material == '':
                object_material = 'missing_texture'
            object_pos = obj['pos']
            object_rot = obj['rot']
            object_scale = obj['scale']
            cast_shadow = obj['cast_shadow']

            add(models[object_name](app, tex_id=object_material, pos=object_pos, rot=object_rot, scale=object_scale, display_name=display_name, cast_shadow=cast_shadow), display_name)

        add(models['sphere'](app, tex_id='sphere', display_name='cas_1_centre_point', cast_shadow=True, scale=glm.vec3(0.2)), 'cas_1_centre_point')
        #add(models['sphere'](app, tex_id='sphere', display_name='cas_2_centre_point', cast_shadow=True, scale=glm.vec3(1.5)), 'cas_2_centre_point')
        #add(models['sphere'](app, tex_id='sphere', display_name='cas_3_centre_point', cast_shadow=True, scale=glm.vec3(7)), 'cas_3_centre_point')

        #n, s = 10, 2
        #for x in range(-n, n, s):
        #    for z in range(-n, n, s):
        #        add(Cube(app, pos=(x, -s, z)))
            
        """#moving cube
        for i in range(len(physics_objects)):
            self.physics_objects[f'obj_{str(i)}'] = Sphere(app, pos=(i, 1, 0), scale=(0.1, 0.1, 0.1))
                       
        for i in range(len(physics_objects)):
            add(self.physics_objects[f'obj_{str(i)}'])""" 

    def update(self):
        '''# cascade 1 (custum proj)
        for i in range(3):
            match i:
                case 0:
                    near, far = 0.1, 10
                case 1:
                    near, far = 10, 30
                case 2:
                    near, far = 30, 100
    
            m_proj = glm.perspective(glm.radians(self.app.camera.fov), self.app.camera.aspect_ratio, near, far)
            corners = calculate_frustum_corners(self.app.camera.m_view, m_proj)
            center_point = sum(corners) / len(corners)
            radius = calc_bounding_sphere_radius(corners, center_point)
            center_point_obj = self.objects[f'cas_{i+1}_centre_point']
            center_point_obj.pos = glm.vec3(center_point)
            center_point_obj.update_m_model()
            if i == 1:
                print(f'Cascade {i+1} center point: {center_point}, radius: {radius}')
        '''
#################################################################################
#positioning: .pos = glm.vec3(x,y,z)   (x,y,z = float) (default values: 0, 0, 0)#
#rotations:   .rot = .x, .y, .z, .xyz  (x,y,z = float) (default values: 0, 0, 0)#
#scaling:     .scale = glm.vec3(x,y,z) (x,y,z = float) (default values: 1, 1, 1)#
#################################################################################