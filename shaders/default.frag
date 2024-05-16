#version 330 core

layout (location = 0) out vec4 fragcolour;

in vec2 uv_0;
in vec3 normal;
in vec3 fragPos;
in vec4 shadowCoord;
in mat3 TBN;

struct Light {
    vec3 position;
    vec3 colour;
    float intensity;
    float range;
};

struct Sun {
    vec3 direction;
    vec3 colour;
    float Ia;
    float Id;
    float Is;
};

struct Material {
    sampler2D normal_0;
    sampler2D rough_metal_diff;
};

uniform int numLights;
uniform Light static_lights[30]; // max number of lights! state this in the engine
uniform Sun sun;
uniform sampler2D diff_0;
uniform vec3 camPos;
uniform sampler2DShadow shadowMap;
uniform vec2 shadow_map_res;
uniform vec4 norm_rough_metal_height_values;
uniform Material maps;
uniform vec2 mat_values;
uniform samplerCube u_irradiance;
uniform samplerCube u_reflection;
uniform sampler2D u_brdf_lut;
const float PI = 3.14159265359;
const float MAX_REFLECTION_LOD = 7;
uniform int IBL_enabled;

float lookup(float ox, float oy) {
    vec2 pixelOffset = 1 / shadow_map_res; // divided by 1.5 for sharper shadows
    return textureProj(shadowMap, shadowCoord + vec4(ox * pixelOffset.x * shadowCoord.w,
                                                     oy * pixelOffset.y * shadowCoord.w, 0.0, 0.0));
}

float getShadow() { // pcf
    if (shadowCoord.x < 0.0 || shadowCoord.x > 1.0 || shadowCoord.y < 0.0 || shadowCoord.y > 1.0 || shadowCoord.z < 0.0 || shadowCoord.z > 1.0) {
        // if sampled point is outside the shadow map, consider it fully lit
        return 1.0;
    }
    float shadow;
    float swidth = 1;
    float endp = swidth * 1.5;
    for (float y = -endp; y <= endp; y += swidth) {
        for (float x = -endp; x <= endp; x += swidth) {
            shadow += lookup(x, y);
        }
    }
    return shadow / 16;
}

float DistributionGGX(vec3 N, vec3 H, float roughness) {
    float a = roughness * roughness;
    float a2 = a * a;
    float NdotH = max(dot(N, H), 0.0);

    float denom = NdotH * NdotH * (a2 - 1.0) + 1.0;
    return a2 / (PI * denom * denom);
}

vec3 fresnelSchlick(float cosTheta, vec3 F0) {
    return F0 + (1.0 - F0) * pow(1.0 - cosTheta, 5.0);
}

vec3 getLight(vec3 Normal, float roughness, float metallicness, vec3 viewDir, float NdotV) {
    // calculate the reflectance based on the roughness and metallicness
    vec3 reflectance = mix(vec3(0.04), vec3(0.5), metallicness);

    vec3 specular = vec3(0.0);
    vec3 diffuse = vec3(0.0);
    for (int i = 0; i < numLights; i++) {
        float distance = length(static_lights[i].position - fragPos);
        if (distance > static_lights[i].range) {continue;} // skip lights that are too far away
        float attenuation = smoothstep(static_lights[i].range, 0.0, distance);
        vec3 light_contrib = static_lights[i].colour * static_lights[i].intensity * attenuation;
        
        vec3 lightDir = normalize(static_lights[i].position - fragPos);
        vec3 halfwayDir = normalize(viewDir + lightDir);

        float NdotL = max(0.0, dot(Normal, lightDir));
        float NdotH = max(0.0, dot(Normal, halfwayDir));
        float HdotV = max(0.0, dot(halfwayDir, viewDir));

        float D = DistributionGGX(Normal, halfwayDir, roughness);
        vec3 F = fresnelSchlick(HdotV, reflectance);
        float G = min(1.0, min(2.0 * NdotH * NdotV / HdotV, 2.0 * NdotH * NdotL / HdotV));
        vec3 specularContrib = (D * F * G) / (4.0 * NdotL * NdotV + 0.001);

        float diff = max(0.0, dot(lightDir, Normal));
        vec3 diffuseContrib = diff * light_contrib;
        vec3 finalContrib = mix(diffuseContrib, vec3(0), metallicness);
        diffuse += finalContrib;

        specular += specularContrib * light_contrib;

    }
    
    return diffuse + specular;
}

vec3 getSunLight(vec3 Normal, float roughness, float metallicness, vec3 viewDir, float NdotV) {
    vec3 sunAmbient = sun.Ia * sun.colour;

    // Diffuse
    vec3 lightDir = normalize(sun.direction);
    float diff = max(0.0, dot(lightDir, Normal));
    vec3 sunDiffuse = diff * (sun.Id * sun.colour);

    // Reflectance based off metalicness
    vec3 reflectance = mix(vec3(0.04), vec3(0.5), metallicness);

    // Specular
    vec3 halfwayDir = normalize(viewDir + lightDir);

    float NdotL = max(0.0, dot(Normal, lightDir));
    float NdotH = max(0.0, dot(Normal, halfwayDir));
    float HdotV = max(0.0, dot(halfwayDir, viewDir));

    float D = DistributionGGX(Normal, halfwayDir, roughness);
    vec3 F = fresnelSchlick(HdotV, reflectance);
    float G = min(1.0, min(2.0 * NdotH * NdotV / HdotV, 2.0 * NdotH * NdotL / HdotV));

    vec3 specularContrib = (D * F * G) / (4.0 * NdotL * NdotV + 0.001);
    vec3 sunSpecular = specularContrib * (sun.Is * sun.colour);

    // Shadow
    float shadow = getShadow();

    vec3 sunLight = sunAmbient + (sunDiffuse + sunSpecular) * shadow;

    return sunLight;
}

vec3 fresnelSchlickRoughness(float cosTheta, vec3 F0, float roughness) {
    return F0 + (max(vec3(1.0 - roughness), F0) - F0) * pow(clamp(1.0 - cosTheta, 0.0, 1.0), 5.0);
}

void main() {
    float gamma = 2.2;
    vec3 albedo = texture(diff_0, uv_0).rgb;
    
    albedo = pow(albedo, vec3(gamma));

    float roughness = mat_values.x;
    float metallicness = mat_values.y;

    vec3 N;

    if (norm_rough_metal_height_values.x == 0) {
        N = normalize(normal);
    } else {
        vec3 normal_map = texture(maps.normal_0, uv_0).rgb;
        vec3 tangent_normal = normalize(normal_map * 2.0 - 1.0);
        vec3 tangent_normal_tangent_space = normalize(TBN * tangent_normal);
        N = normalize(tangent_normal_tangent_space);
    }
    float other_roughness = clamp(roughness, 0.01, 0.99);
    roughness = clamp(other_roughness, 0.05, 0.99);
    
    vec3 viewDir = normalize(camPos - fragPos); // Calc view direction

    vec3 baseReflectivity = vec3(0.04);
    baseReflectivity = mix(baseReflectivity, albedo, metallicness);

    float NdotV = max(0.0, dot(N, viewDir));
    vec3 sunLight = getSunLight(N, roughness, metallicness, viewDir, NdotV); // Sun light contrib
    vec3 pointLights = getLight(N, roughness, metallicness, viewDir, NdotV); // Point light contrib
    vec3 colour;
    if (IBL_enabled == 1) {
        vec3 F = fresnelSchlickRoughness(NdotV, baseReflectivity, roughness);
        vec3 kD = (1.0 - F);
        vec3 diffuse = texture(u_irradiance, N).rgb * albedo * kD;

        vec3 brdf = texture(u_brdf_lut, vec2(clamp(NdotV, 0.01, 0.99), roughness)).rgb;
        vec3 prefilteredColour = textureLod(u_reflection, reflect(-viewDir, N), brdf.b * MAX_REFLECTION_LOD).rgb * F;
        vec3 specular = prefilteredColour * (F * brdf.r + brdf.g);

        colour = (diffuse + specular) * (sunLight + pointLights);
    } else {
        colour = albedo * (sunLight + pointLights);
    }
    
    colour = pow(colour, vec3(1.0 / gamma)); // Gamma correction
    fragcolour = vec4(colour, 1.0);
}