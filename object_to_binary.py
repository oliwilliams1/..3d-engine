import os
import yaml
import pyassimp
import numpy as np
import time

script_path = os.path.dirname(os.path.abspath(__file__))
folder_to_save_in = '/obj_bin/'
file_extention = '.bin'

loaded_objects = []

def loadObjects():
    global loaded_objects
    object_file_path = os.path.join(script_path, 'config/objects.cfg')
    with open(object_file_path, 'r') as file:
        data = yaml.safe_load(file)
        loaded_objects = data
    return data

def calculate_attribute_values(vertices, tex_coords, normals, tangents, bitangents):
    vertex_data = []

    for vertex, tex_coord, normal, tangent, bitangent in zip(vertices, tex_coords, normals, tangents, bitangents):
        # Calculate the values for 'in_texcoord_0', 'in_normal', 'in_position', 'in_tangent', and 'in_bitangent'
        texcoord_values = tex_coord[:2]  # Assuming 2D texture coordinates
        normal_values = normal[:3]  # Assuming 3D normals
        position_values = vertex[:3]  # Assuming 3D vertex positions
        tangent_values = tangent[:3]  # Assuming 3D tangent values
        bitangent_values = bitangent[:3]  # Assuming 3D bitangent values

        # Extend the vertex data with the calculated attribute values
        vertex_data.extend(texcoord_values)
        vertex_data.extend(normal_values)
        vertex_data.extend(position_values)
        vertex_data.extend(tangent_values)
        vertex_data.extend(bitangent_values)

    return vertex_data

def get_vertex_data(model_path):
    full_model_path = f'{script_path}{model_path}'
    with pyassimp.load(full_model_path, processing=pyassimp.postprocess.aiProcess_CalcTangentSpace) as scene:
        mesh = scene.meshes[0]
        vertices = mesh.vertices
        tex_coords = mesh.texturecoords[0]
        normals = mesh.normals
        tangents = mesh.tangents
        bitangents = mesh.bitangents
        vertex_data = calculate_attribute_values(vertices, tex_coords, normals, tangents, bitangents)
        vertex_data = np.array(vertex_data, dtype='f4')

        aabb_min = vertices.min(axis=0)
        aabb_max = vertices.max(axis=0)
        print("  AABB Min:", aabb_min)
        print("  AABB Max:", aabb_max)

        return vertex_data

prev_tot_time = time.time()

loadObjects()
for object in loaded_objects:
    prev_time = time.time()
    mesh_name = loaded_objects[object]['label']
    model_path = loaded_objects[object]['model_path']

    mesh_data = get_vertex_data(model_path)
    mesh_data_bytes = mesh_data.tobytes()
    
    with open(f'{script_path}{folder_to_save_in}{mesh_name}{file_extention}', 'bw') as file:
        file.write(mesh_data_bytes)
    
    print(f'Saved: {mesh_name}, Proccessing Time: {round(time.time() - prev_time, 2)}s')

print(f'\nTotal time: {round(time.time() - prev_tot_time, 2)}s')