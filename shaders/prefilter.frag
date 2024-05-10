#version 330 core
out vec4 fragColor;

in vec3 localPos;

uniform samplerCube enviroment_map;

void main() {
    fragColor = texture(enviroment_map, localPos);
}