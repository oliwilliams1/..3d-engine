import numpy as np
import os
import object_loader

script_path = os.path.dirname(os.path.abspath(__file__))
obj_loader = object_loader.ObjectLoader()
loaded_objects = obj_loader.retrieveObjects()

class VBO:
    def __init__(self, ctx):
        self.vbos = {}
        self.vbos['skybox']  = SkyBoxVBO(ctx)
        self.vbos['advanced_skybox'] = AdvancedSkyBoxVBO(ctx)
        self.vbos['convolution_vbo'] = ConvolutionVbo(ctx)
        # In form of vbo_name[0], vao_name[1], tex_id[2], tex_path[3], obj_path[4]
        for obj in loaded_objects:
            obj_name = loaded_objects[obj]['label']
            vbo_class = create_VBO_class(obj_name, BaseVBO, obj_name)
            self.vbos[obj_name] = vbo_class(ctx)

    def destroy(self):
        [vbo.destroy() for vbo in self.vbos.values()]

class BaseVBO:
    def __init__(self, ctx):
        self.ctx = ctx
        self.vbo = self.get_vbo()
        self.format: str = None
        self.attrib: list = None
    
    def get_vertex_data(self): ...

    def get_vbo(self):
        vertex_data = self.get_vertex_data()
        vbo = self.ctx.buffer(vertex_data)
        return vbo
    
    def destroy(self):
        self.vbo.release()
    

def create_VBO_class(class_name, base_class, mesh_name):
    class CustomVBOClass(base_class):
        def __init__(self, app):
            super().__init__(app)
            self.format = '2f 3f 3f 3f 3f'  # Updated format to include tangent and bitangent
            self.attribs = ['in_texcoord_0', 'in_normal', 'in_position', 'in_tangent', 'in_bitangent']  # Updated attribs list

        def calculate_attribute_values(self, vertices, tex_coords, normals, tangents, bitangents):
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

        def get_vertex_data(self):
            """full_model_path = f'{script_path}{model_path}'
            with pyassimp.load(full_model_path, processing=pyassimp.postprocess.aiProcess_CalcTangentSpace) as scene:
                mesh = scene.meshes[0]
                vertices = mesh.vertices
                tex_coords = mesh.texturecoords[0]
                normals = mesh.normals
                tangents = mesh.tangents
                bitangents = mesh.bitangents
                vertex_data = self.calculate_attribute_values(vertices, tex_coords, normals, tangents, bitangents)
                vertex_data = np.array(vertex_data, dtype='f4')
                #return vertex_data"""
            
            with open(f'{script_path}/obj_bin/{mesh_name}.bin', 'rb') as file:
                return np.frombuffer(file.read(), dtype='f4')
            
    CustomVBOClass.__name__ = class_name
    return CustomVBOClass
    
class SkyBoxVBO(BaseVBO):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '3f'
        self.attribs = ['in_position']

    @staticmethod
    def get_data(vertices, indices):
        data = [vertices[ind] for triangle in indices for ind in triangle]
        return np.array(data, dtype='f4')
    
    def get_vertex_data(self):
        vertices = [(-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1),
                    (-1, 1, -1), (-1, -1, -1), (1, -1, -1), (1, 1, -1)]
        
        indices = [(0, 2, 3), (0, 1, 2),
                (1, 7, 2), (1, 6, 7),
                (6, 5, 4), (4, 7, 6),
                (3, 4, 5), (3, 5, 0),
                (3, 7, 4), (3, 2, 7),
                (0, 6, 1), (0, 5, 6)]
        
        vertex_data = self.get_data(vertices, indices)
        vertex_data = np.flip(vertex_data, 1).copy(order='C')
        return vertex_data

class ConvolutionVbo(BaseVBO):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '3f'
        self.attribs = ['in_position']
    
    @staticmethod
    def get_data(vertices, indices):
        data = [vertices[ind] for triangle in indices for ind in triangle]
        return np.array(data, dtype='f4')
    
    def get_vertex_data(self):
        vertices = [(-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1),
                    (-1, 1, -1), (-1, -1, -1), (1, -1, -1), (1, 1, -1)]
        
        indices = [(0, 2, 3), (0, 1, 2),
                (1, 7, 2), (1, 6, 7),
                (6, 5, 4), (4, 7, 6),
                (3, 4, 5), (3, 5, 0),
                (3, 7, 4), (3, 2, 7),
                (0, 6, 1), (0, 5, 6)]
        
        vertex_data = self.get_data(vertices, indices)
        vertex_data = np.flip(vertex_data, 1).copy(order='C')
        return vertex_data

class AdvancedSkyBoxVBO(BaseVBO):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '3f'
        self.attribs = ['in_position']
    
    def get_vertex_data(self):
        # in clip space
        z = 0.9999
        vertices = [(-1, -1, z), (3, -1, z), (-1, 3, z)]
        vertex_data = np.array(vertices, dtype='f4')
        return vertex_data