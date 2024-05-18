import glm
import pygame as pg

# Define NDC corners (normalized device coordinates)
ndc_corners = [
    glm.vec4(-1, -1, -1, 1),
    glm.vec4(1, -1, -1, 1),
    glm.vec4(-1, 1, -1, 1),
    glm.vec4(1, 1, -1, 1),
    glm.vec4(-1, -1, 1, 1),
    glm.vec4(1, -1, 1, 1),
    glm.vec4(-1, 1, 1, 1),
    glm.vec4(1, 1, 1, 1),
]

# View matrix (assuming the camera is at the origin looking towards Z+)
epsilon = glm.epsilon()
m_view = glm.lookAt(glm.vec3(1, 1, 1), glm.vec3(0, 0, 0) + epsilon, glm.vec3(0, 1, 0))

# Define cube vertices
cube_verts = [
    glm.vec3(-1, -1, -1),
    glm.vec3(-1, -1, 1),
    glm.vec3(1, -1, -1),
    glm.vec3(1, -1, 1),
    glm.vec3(-1, 1, -1),
    glm.vec3(-1, 1, 1),
    glm.vec3(1, 1, -1),
    glm.vec3(1, 1, 1),
]

transformed_cube_verts = []
for v in cube_verts:
    mvp = glm.vec4(v, 1.0) * m_view
    transformed_cube_verts.append(mvp)

min_x = min(v.x for v in transformed_cube_verts)
max_x = max(v.x for v in transformed_cube_verts)
min_y = min(v.z for v in transformed_cube_verts)
max_y = max(v.z for v in transformed_cube_verts)

AABB = [glm.vec2(min_x, min_y), glm.vec2(max_x, min_y), glm.vec2(min_x, max_y), glm.vec2(max_x, max_y)]

pg.init()
WIDTH, HEIGHT = 800, 800
SCALE = 10
screen = pg.display.set_mode((WIDTH, HEIGHT))
screen_center = (screen.get_width() // 2, screen.get_height() // 2)

red = pg.Color("red")
black = pg.Color("black")

def draw_point(point):
    x = int(point.x * WIDTH / SCALE + screen_center[0])
    if type(point) == glm.vec4:
        y = int(-point.z * HEIGHT / SCALE + screen_center[1])
        pg.draw.circle(screen, black, (x, y), 5)
    else:
        y = int(-point.y * HEIGHT / SCALE + screen_center[1])
        pg.draw.circle(screen, red, (x, y), 10)

    

running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    screen.fill(pg.Color("white"))

    for point in AABB:
        draw_point(point)

    for point in transformed_cube_verts:
        draw_point(point)


    # Update display
    pg.display.flip()

pg.quit()