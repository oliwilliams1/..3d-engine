import config
import os
import yaml
import moderngl as mgl

config = config.Config()

script_path = config.retrieveConfig('script_path')

def get_materials():
    script_path = os.path.dirname(os.path.abspath(__file__))
    material_file_path = os.path.join(script_path, 'config/materials.cfg')
    
    with open(material_file_path, 'r') as file:
        data = yaml.safe_load(file)
        materials = data

    return materials

materials = get_materials()