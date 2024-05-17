import glm
import pygame as pg
import time

pg.init()

WIDTH, HEIGHT = 800, 600
SCALE = 1
WIN = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Testing")

ndc_corners = [glm.vec4(-1, -1, -1, 1),glm.vec4(1, -1, -1, 1),glm.vec4(-1, 1, -1, 1),glm.vec4(1, 1, -1, 1),glm.vec4(-1, -1, 1, 1),glm.vec4(1, -1, 1, 1),glm.vec4(-1, 1, 1, 1),glm.vec4(1, 1, 1, 1)]

edges = [
    (0, 1), (1, 3), (3, 2), (2, 0),  # Bottom quad
    (4, 5), (5, 7), (7, 6), (6, 4),  # Top quad
    (0, 4), (1, 5), (3, 7), (2, 6)   # Connecting edges
]

current_rotation = glm.vec3(0, 0, 0)

def rotation_to_direction(rotation):
    rotation_rad = glm.vec3(glm.radians(rotation.x), glm.radians(rotation.y), glm.radians(rotation.z))
    
    rotation_matrix = glm.mat4(1.0)
    rotation_matrix = glm.rotate(rotation_matrix, rotation_rad.x, glm.vec3(1, 0, 0))
    rotation_matrix = glm.rotate(rotation_matrix, rotation_rad.y, glm.vec3(0, 1, 0))
    rotation_matrix = glm.rotate(rotation_matrix, rotation_rad.z, glm.vec3(0, 0, 1))
    
    direction = glm.vec3(rotation_matrix[2])
    
    return glm.normalize(direction)

def calculate_frustum_corners(view_matrix, proj_matrix):
    combined_matrix = proj_matrix * view_matrix
    inverse_matrix = glm.inverse(combined_matrix)
    world_corners = [inverse_matrix * corner for corner in ndc_corners]
    return [glm.vec3(corner) / corner.w for corner in world_corners]

def draw_point(pos: glm.vec2, colour: str = "black", point_size: int = 5):
    x = int(pos.x * SCALE + (WIDTH / 2))
    y = int(pos.y * SCALE + (HEIGHT / 2))
    pg.draw.circle(WIN, colour, (int(x), int(y)), point_size)

def draw_line(p1: glm.vec2, p2: glm.vec2, colour: str = "black"):
    p1_x = int(p1.x * SCALE + (WIDTH / 2))
    p1_y = int(p1.y * SCALE + (HEIGHT / 2))
    p2_x = int(p2.x * SCALE + (WIDTH / 2))
    p2_y = int(p2.y * SCALE + (HEIGHT / 2))
    pg.draw.line(WIN, colour, (p1_x, p1_y), (p2_x, p2_y))

def main():
    global current_rotation
    run = True
    clock = pg.time.Clock()
    
    while run:
        clock.tick(60)
        WIN.fill("white")

        camera_m_proj = glm.perspective(glm.radians(70), 16/9, 0.1, 15)
        camera_m_view = glm.lookAt(glm.vec3(0, 0, -5), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))
        
        frustum_corners = calculate_frustum_corners(camera_m_view, camera_m_proj)
        
        center_frustum = sum(frustum_corners) / len(frustum_corners)

        current_rotation += glm.vec3(0, 0, 1)
        sun_dir = rotation_to_direction(current_rotation)
        ortho_view = glm.lookAt(center_frustum + 50 * sun_dir, center_frustum + glm.epsilon(), glm.vec3(0, 1, 0))

        cam_space_corner = []

        for corner in frustum_corners:
            corner = glm.vec4(corner, 1)
            cam_space_corner.append(corner * (ortho_view))
    
        for corner in cam_space_corner:
            corner = glm.vec2(corner.x, corner.y)
            draw_point(corner)

        for edge in edges:
            p1 = cam_space_corner[edge[0]]
            p2 = cam_space_corner[edge[1]]
            p1 = glm.vec2(p1.x, p1.y)
            p2 = glm.vec2(p2.x, p2.y)
            draw_line(p1, p2)

        x_verts = [corner.x for corner in cam_space_corner]
        y_verts = [corner.y for corner in cam_space_corner]
        z_verts = [corner.z for corner in cam_space_corner]
        min_x = min(x_verts)
        max_x = max(x_verts)
        min_y = min(y_verts)
        max_y = max(y_verts)
        min_z = min(z_verts)
        max_z = max(z_verts)

        print(f'AABB: ({min_x}, {min_y}, {min_z}) - ({max_x}, {max_y}, {max_z})')

        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False

        pg.display.update()
    pg.quit()

if __name__ == "__main__":
    main()