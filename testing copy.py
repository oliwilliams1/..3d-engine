import glm
import pygame as pg
import time

pg.init()

WIDTH, HEIGHT = 800, 600
SCALE = 10
WIN = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Testing")

FONT = pg.font.SysFont("comicsans", 30)

ndc_corners = [glm.vec4(-1, -1, -1, 1),glm.vec4(1, -1, -1, 1),glm.vec4(-1, 1, -1, 1),glm.vec4(1, 1, -1, 1),glm.vec4(-1, -1, 1, 1),glm.vec4(1, -1, 1, 1),glm.vec4(-1, 1, 1, 1),glm.vec4(1, 1, 1, 1)]

def calculate_frustum_corners(view_matrix, proj_matrix):
    combined_matrix = proj_matrix * view_matrix
    inverse_matrix = glm.inverse(combined_matrix)
    world_corners = [inverse_matrix * corner for corner in ndc_corners]
    return [glm.vec3(corner) / corner.w for corner in world_corners]

def find_optimal_bounding_circle(points):
    # Step 1: Find the minimum and maximum x and y coordinates
    min_x = min(p.x for p in points)
    min_y = min(p.y for p in points)
    max_x = max(p.x for p in points)
    max_y = max(p.y for p in points)
    
    # Step 2: Calculate the initial center and radius
    center = glm.vec2((min_x + max_x) / 2, (min_y + max_y) / 2)
    radius = 0
    for p in points:
        radius = max(radius, glm.distance(p, center))
    
    # Step 3: Refine the bounding circle
    for p in points:
        if glm.distance(p, center) > radius:
            new_center = (center * radius + p * (glm.distance(p, center) - radius)) / (radius + glm.distance(p, center))
            radius = glm.distance(p, new_center)
            center = new_center
    
    return center, radius

def conv_coords(pos: glm.vec2):
    pos *= SCALE
    pos.x += WIDTH / 2
    pos.y += HEIGHT / 2
    return pos

def draw_point(pos: glm.vec2):
    pos = conv_coords(pos)
    pg.draw.circle(WIN, "black", (pos), 5)

def draw_circle(pos: glm.vec2, radius: float, width: float=5):
    pos = conv_coords(pos)
    pg.draw.circle(WIN, "black", (pos.x, pos.y), int(radius * SCALE), width) # make a circle, unfilled

def draw_line(pos1: glm.vec2, pos2: glm.vec2, width: float=5):
    pos = conv_coords(pos)
    pg.draw.line(WIN, "black", (pos1), (pos2), width)
    
def draw_text(text: str, pos: glm.vec2, color: tuple=(0, 0, 0)):
    label = FONT.render(text, True, color)
    WIN.blit(label, pos)

def main():
    run = True
    clock = pg.time.Clock()
    
    while run:
        clock.tick(60)
        WIN.fill("white")

        position = glm.vec3(0, 0, 0)
        forward = glm.vec3(0, 0, -1)
        up = glm.vec3(0, 1, 0)
        cascade1_m_proj = glm.perspective(glm.radians(70), 16/9, 5, 15)
        cascade1_m_view = glm.lookAt(position, position + forward, up)
        corners = calculate_frustum_corners(cascade1_m_view, cascade1_m_proj)
        
        for i, corner in enumerate(corners):
            corners[i] = glm.vec2(corner.x, corner.z)

        center, radius = find_optimal_bounding_circle(corners)
        
        for corner in corners:
            draw_point(corner)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
        draw_point(center)
        draw_circle(center, radius)
                
        pg.display.update()
        
    pg.quit()
if __name__ == "__main__":
    main()