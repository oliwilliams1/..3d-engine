cimport cython
cimport numpy as np
import numpy as np
import glm

@cython.boundscheck(False)
@cython.wraparound(False)

def compute_aabb(vertices):
    cdef float inf = float("inf")
    cdef float min_coords[3]
    cdef float max_coords[3]

    for i in range(3):
        min_coords[i] = inf
        max_coords[i] = -inf

    for vertex in vertices:
        for i in range(3):
            min_coords[i] = min(min_coords[i], vertex[i])
            max_coords[i] = max(max_coords[i], vertex[i])

    return min_coords, max_coords

def frustum(position, double yaw_deg, double pitch_deg, right, up, double aspect_ratio, double FOV, double NEAR, double FAR):
    cdef list frustum_vertices = []
    cdef np.ndarray[double, ndim=1] direction = np.array([
        np.cos(np.radians(yaw_deg)) * np.cos(np.radians(pitch_deg)),
        np.sin(np.radians(yaw_deg)) * np.cos(np.radians(pitch_deg)),
        np.sin(np.radians(pitch_deg))
    ])

    # Calculate the frustum box vertices
    cdef double tan_half_fov_x = np.tan(np.radians(FOV / 2))
    cdef double tan_half_fov_y = np.tan(np.radians(FOV / 2))

    cdef double near_x = NEAR * tan_half_fov_x * aspect_ratio
    cdef double near_y = NEAR * tan_half_fov_y

    cdef double far_x = FAR * tan_half_fov_x * aspect_ratio
    cdef double far_y = FAR * tan_half_fov_y

    # Calculate the frustum vertices
    frustum_vertices.append(position + NEAR * direction - near_x * right - near_y * up)
    frustum_vertices.append(position + NEAR * direction + near_x * right - near_y * up)
    frustum_vertices.append(position + NEAR * direction + near_x * right + near_y * up)
    frustum_vertices.append(position + NEAR * direction - near_x * right + near_y * up)

    frustum_vertices.append(position + FAR * direction - far_x * right - far_y * up)
    frustum_vertices.append(position + FAR * direction + far_x * right - far_y * up)
    frustum_vertices.append(position + FAR * direction + far_x * right + far_y * up)
    frustum_vertices.append(position + FAR * direction - far_x * right + far_y * up)

    return frustum_vertices

def culling(objects, position, yaw_deg, pitch_deg, right, up, aspect_ratio, FOV, NEAR, FAR):
    cdef list frustum_vertices = frustum(position, yaw_deg, pitch_deg, right, up, aspect_ratio, FOV, NEAR, FAR)
    near_plane_normal = glm.cross(glm.vec3(frustum_vertices[2] - frustum_vertices[1]), glm.vec3(frustum_vertices[1] - frustum_vertices[0]))
    near_plane_point = glm.vec3(frustum_vertices[0])
    
    for obj in objects:
        obj_pos = glm.vec3(obj.pos)
        bounding_box = obj.bounding_box
        # near plane check
        for corner in bounding_box:
            if glm.dot((obj_pos + corner) - near_plane_point, near_plane_normal) > 0:
                obj.render()
                break

        # cant be bothered doing other planes and problably wouldnt profit that much
            