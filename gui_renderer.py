import imgui
from imgui.integrations.glfw import GlfwRenderer
from numpy import rad2deg, radians
from PIL import Image
import glm
from glfw import get_time
image = Image.open('objects/cat/20430_cat_diff_v1.jpg')
image.resize((128, 128))
image_data = image.convert('RGB').tobytes()

def from_vec3(vec):
    return [round(rad2deg(vec.x), 3), round(rad2deg(vec.y), 3), round(rad2deg(vec.z), 3)]

def to_vec3(rot):
    return glm.vec3(radians(rot[0]), radians(rot[1]), radians(rot[2]))

pos_step = 0.1
rot_step = 1
scale_step = 0.1

cam_yaw = 0
cam_pitch = 0

def update_camera_vectors():
    global cam_yaw, cam_pitch
    y_drag = imgui.drag_float('Yaw', cam_yaw, 1, -180, 180)
    p_drag = imgui.drag_float('Pitch', cam_pitch, 1, -89, 89)

    if y_drag[0] or p_drag[0]:
        cam_yaw, cam_pitch = y_drag[1], p_drag[1]

    yaw, pitch = glm.radians(cam_yaw), glm.radians(cam_pitch)

    cos_pitch = glm.cos(pitch)
    sin_pitch = glm.sin(pitch)
    cos_yaw = glm.cos(yaw)
    sin_yaw = glm.sin(yaw)

    forward = glm.vec3(cos_yaw * cos_pitch, sin_pitch, sin_yaw * cos_pitch)

    right_up = glm.cross(forward, glm.vec3(0, 1, 0))
    right = glm.normalize(right_up)
    up = glm.normalize(glm.cross(right, forward))

    imgui.text(f'forward = {forward}')
    imgui.text(f'up = {up}')


class imGuiRenderer:
    def __init__(self, app):
        self.app = app
        self.window = app.window
        imgui.create_context()
        self.imgui_renderer = GlfwRenderer(self.window)
        self.scene_handler = app.scene
        self.selected_object = ['None', 'grr']
        self.scene_objects = None
        self.material_handler = app.material_class
        self.loaded_materials = [i for i in self.material_handler.materials]
        self.selected_albedo_tex = None
        self.selected_normal_tex = None
        self.selected_roughness_value = None
        self.selected_metallic_value = None
        self.material_or_cubemap = 0
        self.selected_material = 0
        self.texture_handler = app.mesh.texture
        self.light_handler = app.light

        self.cube_renderer = app.scene_renderer.render_cube

        self.tab_names = ['Materials', 'Cubemap Editor']
        self.current_tab = 0

    def render(self):
        self.imgui_renderer.process_inputs()
        imgui.new_frame()
        self.scene_objects = self.scene_handler.objects
        imgui.set_next_window_position(0, 0)
        imgui.set_next_window_size(300, 350)
        imgui.begin('Scene Hierarchy', flags=imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_COLLAPSE)
        self.render_hierarchy()
        imgui.end()

        imgui.set_next_window_position(0, 350)
        imgui.set_next_window_size(300, 550)
        imgui.begin('Properties', flags=imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_COLLAPSE)
        self.render_object_properties()
        imgui.end()

        imgui.show_demo_window()

        imgui.set_next_window_position(1300, 425)
        imgui.set_next_window_size(300, 475)
        
        imgui.begin('Material Editor', flags=imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_COLLAPSE)
        self.render_materials()
        imgui.end()

        imgui.begin('Cubemap Editor')
        self.render_cubemap_editor()
        imgui.end()

        imgui.begin('Shadow Viewer')
        imgui.text('Cascade 1')
        imgui.image(self.texture_handler.textures['cascade_1'].glo, 275, 275)
        imgui.image(self.texture_handler.textures['cascade_2'].glo, 275, 275)
        imgui.image(self.texture_handler.textures['cascade_3'].glo, 275, 275)
        imgui.end()

        imgui.set_next_window_position(1300, 0)
        imgui.set_next_window_size(300, 110)
        imgui.begin('Performance Graph')
        update_time = self.app.update_time * 1000
        shadow_time = self.app.shadow_time * 1000
        render_time = self.app.render_time * 1000
        skybox_time = self.app.skybox_time * 1000
        event_time  = self.app.event_time  * 1000
        imgui_time  = (get_time() - self.app.pre_imgui_time) * 1000
        buffer_time = self.app.past_swap_buffer * 1000
        imgui.text(f'''Update time: {update_time:.4f} ms
Shadow time: {shadow_time:.4f} ms
Render time: {render_time:.4f} ms
Skybox time: {skybox_time:.4f} ms
Event time: {event_time:.4f} ms
Imgui time: {imgui_time:.4f} ms
Buffer swap time: {buffer_time:.2f} ms
Delta time: {self.app.delta_time * 1000:.2f} ms''')
        imgui.end()

        imgui.render()
        self.imgui_renderer.render(imgui.get_draw_data())

    def destroy(self):
        self.imgui_renderer.shutdown()
    
    def render_hierarchy(self):
        selected, _ = imgui.selectable('Sun', selected=self.selected_object[0] == '#1457Sun')
        if selected:
            self.selected_object = ['#1457Sun', None]
            print(f'Selected object: {self.selected_object} index: None')
    
        for obj in self.scene_objects.values():
            selected, _ = imgui.selectable(obj.display_name, selected=obj.display_name == self.selected_object[0])
            if selected:
                self.selected_object = [obj.display_name, obj.display_name]
    
    def render_object_properties(self):
        if self.selected_object[0] == '#1457Sun':
            imgui.columns(2)
            imgui.set_column_width(0, imgui.get_window_width() * 0.4)
            imgui.text('Colour:')
            imgui.next_column()
            imgui.push_item_width(-1)
            sun_rgb = self.light_handler.sun.colour
            sun_colour_picker = imgui.color_edit3("  Colour Picker", sun_rgb[0], sun_rgb[1], sun_rgb[2])
            if sun_colour_picker[0]:
                self.light_handler.sun.colour = glm.vec3(sun_colour_picker[1])
            
            imgui.next_column()

            imgui.text('Direction:')
            imgui.next_column()
            imgui.push_item_width(-1)
            sun_dir = self.light_handler.sun.unormalized_direction
            sun_direction = imgui.drag_float3('   Direction', sun_dir[0], sun_dir[1], sun_dir[2], 0.05, format='%.1f')
            if sun_direction[0]:
                self.light_handler.sun.unormalized_direction = sun_direction[1]
                norm_sun_dir = glm.normalize(glm.vec3(sun_direction[1]))
                self.light_handler.sun.direction = norm_sun_dir
                self.light_handler.direction = norm_sun_dir
            

        elif self.selected_object[1] != 'grr':
            obj = self.scene_objects[self.selected_object[1]]

            obj_pos = [obj.pos[0], obj.pos[1], obj.pos[2]]
            obj_rot = from_vec3(obj.rot)
            obj_scale = [obj.scale[0], obj.scale[1], obj.scale[2]]

            imgui.columns(2)
            imgui.set_column_width(0, imgui.get_window_width() * 0.4)

            imgui.text('Position:')
            imgui.next_column() 
            imgui.push_item_width(-1)  # has to be unique for data, not displayed
            pos_drag = imgui.drag_float3('  Position', obj_pos[0], obj_pos[1], obj_pos[2], pos_step, format='%.1f')
            slider_obj_pos = pos_drag[1]

            imgui.pop_item_width()
            imgui.next_column()

            imgui.text('Rotation:')
            imgui.next_column()
            imgui.push_item_width(-1)
            rot_drag = imgui.drag_float3('  Rotation', obj_rot[0], obj_rot[1], obj_rot[2], rot_step, format='%.1f')
            slider_obj_rot = to_vec3(rot_drag[1])

            imgui.pop_item_width()
            imgui.next_column()

            imgui.text('Scale:')
            imgui.next_column()
            imgui.push_item_width(-1)
            scale_drag = imgui.drag_float3('  Scale', obj_scale[0], obj_scale[1], obj_scale[2], scale_step, format='%.1f')
            slider_obj_scale = scale_drag[1]
            imgui.pop_item_width()

            imgui.next_column()
            imgui.text('Cast shadow: ')
            imgui.next_column()
            cast_shadow = imgui.checkbox('', obj.cast_shadow)

            imgui.columns(1)

            if cast_shadow[0]:
                obj.cast_shadow = cast_shadow[1]
                
            if pos_drag[0] or rot_drag[0] or scale_drag[0]:
                obj.pos = (slider_obj_pos[0], slider_obj_pos[1], slider_obj_pos[2])
                obj.rot = slider_obj_rot
                obj.scale = slider_obj_scale
                obj.update_m_model()
        else:
            imgui.text('No object selected')

    def render_materials(self):
        materials = ['Select a material'] + self.loaded_materials
        imgui.push_item_width(imgui.get_window_width() * 0.8)
        material_box = imgui.combo('', self.selected_material, materials)
        imgui.same_line()
        imgui.text('+/-')

        if material_box[0]:
            self.selected_material = material_box[1]
            temp_alb = self.material_handler.materials[materials[self.selected_material]].diffuse_tex
            temp_nor = self.material_handler.materials[materials[self.selected_material]].normal_tex
            self.selected_roughness_value = self.material_handler.materials[materials[self.selected_material]].roughness_value
            self.selected_metallic_value = self.material_handler.materials[materials[self.selected_material]].metalicness_value
            
            if temp_alb != None:
                self.selected_albedo_tex = temp_alb.glo
            else:
                self.selected_albedo_tex = None
            
            if temp_nor != None:
                self.selected_normal_tex = temp_nor.glo
            else:
                self.selected_normal_tex = None
            
        if self.selected_material == 0:
            return
        
        imgui.columns(2)
        column_width = imgui.get_window_width() * 0.7
        imgui.set_column_width(0, column_width)
        imgui.text('Albedo Texture')
        imgui.next_column()
        if self.selected_albedo_tex is not None:
            imgui.image(self.selected_albedo_tex, 64, 64)
            if imgui.is_item_hovered(): ... # do something here
        else:
            imgui.text('Select\nAlbedo Map')

        imgui.next_column()

        imgui.text('Normal Texture')
        imgui.next_column()
        if self.selected_normal_tex is not None:
            imgui.image(self.selected_normal_tex, 64, 64)
            if imgui.is_item_hovered(): ... # do something here
        else:
            imgui.text('Select\nNormal Map')

        imgui.columns(1)
        imgui.text('\n\n')

        if self.selected_roughness_value != None:
            rough_value = self.selected_roughness_value
            roughness_slider = imgui.drag_float('Roughness', rough_value, 0.005, 0, 1)
            if roughness_slider[0]:
                self.selected_roughness_value = roughness_slider[1]
                self.material_handler.materials[materials[self.selected_material]].roughness_value = roughness_slider[1]

        if self.selected_metallic_value != None:
            metallic_value = self.selected_metallic_value
            metallic_slider = imgui.drag_float('Metallic', metallic_value, 0.005, 0, 1)
            if metallic_slider[0]:
                self.selected_metallic_value = metallic_slider[1]
                self.material_handler.materials[materials[self.selected_material]].metalicness_value = metallic_slider[1]

    def render_mat_cube_tab(self): ...
        
    def render_cubemap_editor(self):
        if imgui.button('512x'):
            self.cube_renderer((512, 512))
        if imgui.button('update cascades'):
            self.app.scene.objects['cas_1_centre_point'].update_m_model()
