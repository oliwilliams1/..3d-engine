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

# Transform cube vertices using view matrix
transformed_cube_verts = []
for v in cube_verts:
    mvp = glm.vec4(v, 1.0) * m_view
    transformed_cube_verts.append(mvp)

# Initialize Pygame
pg.init()
WIDTH, HEIGHT = 800, 800
SCALE = 10
screen = pg.display.set_mode((WIDTH, HEIGHT))
screen_center = (screen.get_width() // 2, screen.get_height() // 2)

# Set color for points
point_color = pg.Color("red")

# Function to draw a point on the screen (ignoring perspective)
def draw_point(point):
    # Offset point to center of the screen
    x = int(point.x * WIDTH / SCALE + screen_center[0])
    y = int(-point.y * HEIGHT / SCALE + screen_center[1])  # Invert Y for screen coordinates
    pg.draw.circle(screen, point_color, (x, y), 5)

running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    # Clear screen
    screen.fill(pg.Color("white"))

    # Draw all transformed points (ignoring perspective)
    for point in transformed_cube_verts:
        draw_point(point)

    # Update display
    pg.display.flip()

pg.quit()