import glfw
import moderngl as mgl
import sys
from model import *
import camera
from light import Light
from mesh import Mesh
import scene
from scene_renderer import SceneRenderer
from config import Config
from texture import Materials
from gui_renderer import imGuiRenderer
import OpenGL

config = Config()
WIREFRAME = config.retrieveConfig('WIREFRAME')

class GraphicsEngine:
    def __init__(self, win_size=(1600, 900)):
        self.WIN_SIZE = (1000, 635)
        self.viewport = (300, 265, 1000, 635)
        # init GLFW
        if not glfw.init():
            raise Exception("GLFW initialization failed")

        # create a GLFW window
        self.window = glfw.create_window(win_size[0], win_size[1], "My OpenGL Window", None, None)
        glfw.set_window_opacity(opacity=0, window=self.window)
        glfw.set_window_pos(self.window, 190, 30)

        if not self.window:
            glfw.terminate()
            raise Exception("GLFW window creation failed")
        
        # set the OpenGL context
        glfw.make_context_current(self.window)
        # turn vsync off
        #glfw.swap_interval(0)        
        # create an moderngl context
        self.ctx = mgl.create_context()
        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)
        OpenGL.GL.glEnable(OpenGL.GL.GL_TEXTURE_CUBE_MAP_SEAMLESS)
        # create an object to help track time
        self.delta_time = 0
        self.time = 0
        # light
        self.light = Light()
        init_lights()
        # camera
        self.camera = camera.Camera(self)
        # mesh
        self.mesh = Mesh(self)
        # materials
        self.material_class = Materials(self)
        self.materials = self.material_class.materials
        # scene
        self.scene = scene.Scene(self)
        # renderer
        self.scene_renderer = SceneRenderer(self)

        if WIREFRAME:
            self.ctx.wireframe = True
        glfw.set_window_opacity(opacity=1, window=self.window)
        #glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        self.cursor_enabled = True
        self.mouse_delta = [0, 0]
        x, y = glfw.get_cursor_pos(self.window)
        self.mouse_pos = [x, y]
        self.imgui_renderer = imGuiRenderer(self)
        
        self.cube_map_render_data = {'rendering' : False,
                                     'camera_pos' : None,
                                     'face' : None,}

    def check_events(self):
        glfw.poll_events()
        if glfw.window_should_close(self.window):
            self.mesh.destroy()
            self.scene_renderer.destroy()
            glfw.terminate() 
            sys.exit()
        
    def render(self):
        # Clear the framebuffer
        self.ctx.clear(color=(0.08, 0.16, 0.18))
        # Set the viewport
        self.ctx.viewport = self.viewport
        # Render the scene
        self.scene_renderer.render()
        # Render ui
        self.imgui_renderer.render()
        glfw.swap_buffers(self.window)

    def get_time(self):
        self.time = glfw.get_time()

    def run(self):
        self.get_time()
        self.rel_mouse()
        self.cursor_hide()
        self.camera.update()
        self.check_events()
        self.render()
        self.delta_time = glfw.get_time() - self.time
        #glfw.set_window_title(self.window, f'FPS: {1/self.delta_time:.2f}, {self.delta_time*1000:.2f}ms')

    def destroy(self):
        self.mesh.destroy()
        self.scene_renderer.destroy()
        
    def get_key_state(self, key):
        if glfw.get_key(self.window, key) == glfw.PRESS:
            return True
        return False
    
    def rel_mouse(self):
        x, y = glfw.get_cursor_pos(self.window)
        self.mouse_delta = [x - self.mouse_pos[0], y - self.mouse_pos[1]] if self.mouse_pos else [0, 0]
        self.mouse_pos = [x, y]

    def cursor_hide(self):
        if self.get_mouse_button_state(glfw.MOUSE_BUTTON_2):
            if self.cursor_enabled:
                self.cursor_enabled = False
                glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        else:
            if not self.cursor_enabled:
                self.cursor_enabled = True
                glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_NORMAL)

    def get_mouse_button_state(self, button):
        if glfw.get_mouse_button(self.window, button) == glfw.PRESS:
            return True
        return False
    
if __name__ == '__main__':
    app = GraphicsEngine()
    
    while not glfw.window_should_close(app.window):
        app.run()

    app.destroy()
    glfw.terminate()    