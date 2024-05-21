#version 330 core

layout (location = 0) in vec2 in_texcoord_0;
layout (location = 1) in vec3 in_normal;
layout (location = 2) in vec3 in_position;
layout (location = 3) in vec3 in_tangent;
layout (location = 4) in vec3 in_bitangent;

out vec2 uv_0;
out vec3 normal;
out vec3 fragPos;
out vec4 cas1Coord;
out vec4 cas2Coord;
out mat3 TBN;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_proj_light_1;
uniform mat4 m_view_light_1;
uniform mat4 m_proj_light_2;
uniform mat4 m_view_light_2;
uniform mat4 m_model;

mat4 m_shadow_bias = mat4(
    0.5, 0.0, 0.0, 0.0,
    0.0, 0.5, 0.0, 0.0,
    0.0, 0.0, 0.5, 0.0,
    0.5, 0.5, 0.5, 1.0
);

void main() {
    uv_0 = in_texcoord_0;
    fragPos = vec3(m_model * vec4(in_position, 1.0));

    vec3 T = normalize(mat3(m_model) * in_tangent);
    vec3 B = normalize(mat3(m_model) * in_bitangent);
    vec3 N = normalize(mat3(m_model) * in_normal);
    TBN = mat3(-T, -B, N);

    normal = mat3(transpose(inverse(m_model))) * normalize(in_normal);
    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);

    mat4 shadow1MVP = m_proj_light_1 * m_view_light_1 * m_model;
    cas1Coord = m_shadow_bias * shadow1MVP * vec4(in_position, 1.0);
    cas1Coord.z -= 0.0005;

    mat4 shadow2MVP = m_proj_light_2 * m_view_light_2 * m_model;
    cas2Coord = m_shadow_bias * shadow2MVP * vec4(in_position, 1.0);
    cas2Coord.z -= 0.0005;
}