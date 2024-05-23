import glm
import pygame

pygame.init()

screen = pygame.display.set_mode((800, 600))

running = True

ndc_corners = [
    glm.vec4(-1, -1, -1, 1),
    glm.vec4(1, -1, -1, 1),
    glm.vec4(-1, 1, -1, 1),
    glm.vec4(1, 1, -1, 1),
    glm.vec4(-1, -1, 1, 1),
    glm.vec4(1, -1, 1, 1),
    glm.vec4(-1, 1, 1, 1),
    glm.vec4(1, 1, 1, 1)
]

def calculate_frustum_corners(view_matrix, proj_matrix):
    combined_matrix = proj_matrix * view_matrix
    inverse_matrix = glm.inverse(combined_matrix)
    world_corners = [inverse_matrix * corner for corner in ndc_corners]
    return [glm.vec3(corner) / corner.w for corner in world_corners]

view_matrix = glm.lookAt(glm.vec3(0, 0, 5), glm.vec3(0, 0, 0) + glm.epsilon(), glm.vec3(0, 1, 0))
proj_matrix = glm.perspective(glm.radians(45.0), 16/9, 5, 20.0)

frustum_verts = calculate_frustum_corners(view_matrix, proj_matrix)

print([list(i) for i in frustum_verts])
ortho_view = glm.lookAt(glm.vec3(0, 0, 10), glm.vec3(0, 0, 0) + glm.epsilon(), glm.vec3(0, 1, 0))
ortho_proj = glm.ortho(-20, 20, -20, 20, 0.1, 50)

font = pygame.font.Font(None, 32)  # Create a font object

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    for i, v in enumerate(frustum_verts):
        old_v = glm.vec4(v, 1) * ortho_proj * ortho_view
        v = old_v * 200
        pygame.draw.circle(screen, (255, 0, 0), (int(v.x + 400), int(v.y + 300)), 5)

        text = font.render(str(i), True, (255, 255, 255))
        text_rect = text.get_rect(center=(int(v.x + 400), int(v.y + 300)))
        screen.blit(text, text_rect)

    pygame.display.flip()

pygame.quit()