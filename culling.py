import glm

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

obj_pos = glm.vec3(0)
bounding_box = []
frustum_vertices = []
def calculate_frustum_corners(view_matrix, proj_matrix):
    combined_matrix = proj_matrix * view_matrix
    inverse_matrix = glm.inverse(combined_matrix)
    world_corners = [inverse_matrix * corner for corner in ndc_corners]
    return [glm.vec3(corner) / corner.w for corner in world_corners]

def cull_test():
    vec1 = frustum_vertices[3] - frustum_vertices[1]
    vec2 = frustum_vertices[3] - frustum_vertices[2]
    normal = glm.cross(vec1, vec2)
    point = frustum_vertices[3]

    for v in bounding_box:
        if glm.dot((obj_pos + v) - point, normal) > 0:
            return far_plane_check()
    return False

def far_plane_check():
    vec1 = frustum_vertices[7] - frustum_vertices[6]
    vec2 = frustum_vertices[7] - frustum_vertices[5]
    normal = glm.cross(vec1, vec2)
    point = frustum_vertices[7]

    for v in bounding_box:
        if glm.dot((obj_pos + v) - point, normal) > 0:
            return bottom_plane_check()
    return False

def bottom_plane_check():
    vec1 = frustum_vertices[1] - frustum_vertices[5]
    vec2 = frustum_vertices[1] - frustum_vertices[0]
    normal = glm.cross(vec1, vec2)
    point = frustum_vertices[1]

    for v in bounding_box:
        if glm.dot((obj_pos + v) - point, normal) > 0:
            return top_plane_check()
    return False

def top_plane_check():
    vec1 = frustum_vertices[2] - frustum_vertices[6]
    vec2 = frustum_vertices[2] - frustum_vertices[3]
    normal = glm.cross(vec1, vec2)
    point = frustum_vertices[2]

    for v in bounding_box:
        if glm.dot((obj_pos + v) - point, normal) > 0:
            return right_plane_check()
    return False

def right_plane_check():
    vec1 = frustum_vertices[0] - frustum_vertices[4]
    vec2 = frustum_vertices[0] - frustum_vertices[2]
    normal = glm.cross(vec1, vec2)
    point = frustum_vertices[0]

    for v in bounding_box:
        if glm.dot((obj_pos + v) - point, normal) > 0:
            return left_plane_check()
    return False

def left_plane_check():
    vec1 = frustum_vertices[3] - frustum_vertices[7]
    vec2 = frustum_vertices[3] - frustum_vertices[1]
    normal = glm.cross(vec1, vec2)
    point = frustum_vertices[3]

    for v in bounding_box:
        if glm.dot((obj_pos + v) - point, normal) > 0:
            return True
    return False

def render_culled(objects, m_view, m_proj, cast_shadow_check: bool = False, cascade: int = 0):
    global obj_pos, bounding_box, frustum_vertices
    frustum_vertices = calculate_frustum_corners(m_view, m_proj)
    rendered_objects = 0
    for obj in objects:
        if cast_shadow_check:
            if obj.cast_shadow:
                obj_pos = glm.vec3(obj.pos)
                bounding_box = obj.bounding_box
                if cull_test():
                    obj.render_shadow(cascade)
                    rendered_objects += 1

        obj_pos = glm.vec3(obj.pos)
        bounding_box = obj.bounding_box
        if cull_test():
            rendered_objects += 1
            obj.render()