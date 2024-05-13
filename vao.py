from vbo import VBO
from shader_program import ShaderProgram
import object_loader

obj_loader = object_loader.ObjectLoader()
loaded_objects = obj_loader.retrieveObjects()

class VAO:
    def __init__(self, ctx):
        self.ctx = ctx
        self.vbo = VBO(ctx)
        self.program = ShaderProgram(ctx)
        self.vaos = {}

        for obj in loaded_objects:
            object_name = loaded_objects[obj]['label']

            self.vaos[f'{object_name}_high'] = self.get_vao(
                program=self.program.programs['default_high'],
                vbo=self.vbo.vbos[object_name])

            self.vaos[f'shadow_{object_name}'] = self.get_vao(
                program=self.program.programs['shadow_map'],
                vbo=self.vbo.vbos[object_name])

        # skybox vao
        self.vaos['skybox'] = self.get_vao(
            program=self.program.programs['skybox'],
            vbo=self.vbo.vbos['skybox'])

        # advanced_skybox vao
        self.vaos['advanced_skybox'] = self.get_vao(
            program=self.program.programs['advanced_skybox'],
            vbo=self.vbo.vbos['advanced_skybox'])
        
        # convolution vao
        self.vaos['convolution'] = self.get_vao(
            program=self.program.programs['convolution_calc'],
            vbo=self.vbo.vbos['convolution_vbo'])
        
    def get_vao(self, program, vbo):
        vao = self.ctx.vertex_array(program, [(vbo.vbo, vbo.format, *vbo.attribs)], skip_errors=True)
        return vao

    def destroy(self):
        self.vbo.destroy()
        self.program.destroy()