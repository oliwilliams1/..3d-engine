import os
import yaml
from config import Config

config = Config()

script_path = config.retrieveConfig('script_path')

loaded_objects = []

def loadObjects():
    global loaded_objects
    object_file_path = os.path.join(script_path, 'config/objects.cfg')
    objects = []
    with open(object_file_path, 'r') as file:
        data = yaml.safe_load(file)
    loaded_objects = data
    return objects

loadObjects()

class ObjectLoader:
    def retrieveObjects(self):
        global loaded_objects
        return loaded_objects
        
    def getAABB(self, desired_obj):
        desired_obj = desired_obj.strip()
        if 'skybox' in desired_obj or desired_obj == 'convolution':
            return None
        return loaded_objects[desired_obj]['aabb']