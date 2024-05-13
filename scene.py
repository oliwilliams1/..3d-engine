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
        self.objects = []
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

    def add_object(self, obj):
        self.objects.append(obj)

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

            add(models[object_name](app, tex_id=object_material, pos=object_pos, rot=object_rot, scale=object_scale, display_name=display_name, cast_shadow=cast_shadow))

        #n, s = 10, 2
        #for x in range(-n, n, s):
        #    for z in range(-n, n, s):
        #        add(Cube(app, pos=(x, -s, z)))
            
        """#moving cube
        for i in range(len(physics_objects)):
            self.physics_objects[f'obj_{str(i)}'] = Sphere(app, pos=(i, 1, 0), scale=(0.1, 0.1, 0.1))
                       
        for i in range(len(physics_objects)):
            add(self.physics_objects[f'obj_{str(i)}'])""" 

    def update(self): ...
        #for i in range(len(physics_objects)):
        #    self.physics_objects[f'obj_{str(i)}'].pos = glm.vec3(physics_objects[i][0]/100, physics_objects[i][2]/100 + 5, physics_objects[i][1]/100)


#################################################################################
#positioning: .pos = glm.vec3(x,y,z)   (x,y,z = float) (default values: 0, 0, 0)#
#rotations:   .rot = .x, .y, .z, .xyz  (x,y,z = float) (default values: 0, 0, 0)#
#scaling:     .scale = glm.vec3(x,y,z) (x,y,z = float) (default values: 1, 1, 1)#
#################################################################################