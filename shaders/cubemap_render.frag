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
    vec3 Ia;
    vec3 Id;
    vec3 Is;
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
uniform vec2 u_resolution;
uniform vec4 norm_rough_metal_height_values;
uniform Material maps;
uniform vec2 mat_values;
uniform samplerCube u_texture_skybox;

const float PI = 3.14159265359;

float lookup(float ox, float oy) {
    vec2 pixelOffset = 1 / u_resolution;
    return textureProj(shadowMap, shadowCoord + vec4(ox * pixelOffset.x * shadowCoord.w,
                                                     oy * pixelOffset.y * shadowCoord.w, 0.0, 0.0));
}

float getSoftShadowX4() {
    float shadow;
    float swidth = 1.5;  // shadow spread
    vec2 offset = mod(floor(gl_FragCoord.xy), 2.0) * swidth;
    shadow += lookup(-1.5 * swidth + offset.x, 1.5 * swidth - offset.y);
    shadow += lookup(-1.5 * swidth + offset.x, -0.5 * swidth - offset.y);
    shadow += lookup( 0.5 * swidth + offset.x, 1.5 * swidth - offset.y);
    shadow += lookup( 0.5 * swidth + offset.x, -0.5 * swidth - offset.y);
    return shadow / 4.0;
}

float getSoftShadowX16() {
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

float getSoftShadowX64() {
    float shadow;
    float swidth = 0.6;
    float endp = swidth * 3.0 + swidth / 2.0;
    for (float y = -endp; y <= endp; y += swidth) {
        for (float x = -endp; x <= endp; x += swidth) {
            shadow += lookup(x, y);
        }
    }
    return shadow / 64;
}

float getShadow() {
    float shadow = textureProj(shadowMap, shadowCoord);
    return shadow;
}

float DistributionGGX(vec3 N, vec3 H, float roughness) {
    float a = roughness * roughness;
    float a2 = a * a;
    float NdotH = max(dot(N, H), 0.0);
    float NdotH2 = NdotH * NdotH;

    float denom = NdotH2 * (a2 - 1.0) + 1.0;
    return a2 / (3.14159 * denom * denom);
}
// Fresnel function using Schlick's approximation
vec3 fresnelSchlick(float cosTheta, vec3 F0) {
    return F0 + (1.0 - F0) * pow(1.0 - cosTheta, 5.0);
}

vec3 getLight(vec3 Normal, float roughness, float metallicness) {
    vec3 viewDir = normalize(camPos - fragPos);

    float specular_range_multiplier = 1.5; // should be a factor of metalicness i think

    // Calculate the reflectance based on the roughness and metallicness
    vec3 reflectance = mix(vec3(0.04), vec3(0.5), metallicness);

    // Calculate the specular contribution using the Cook-Torrance BRDF
    vec3 specular = vec3(0.0);
    for (int i = 0; i < numLights; i++) {
        vec3 lightDir = normalize(static_lights[i].position - fragPos);
        vec3 halfwayDir = normalize(viewDir + lightDir);

        float NdotL = max(0.0, dot(Normal, lightDir));
        float NdotV = max(0.0, dot(Normal, viewDir));
        float NdotH = max(0.0, dot(Normal, halfwayDir));
        float HdotV = max(0.0, dot(halfwayDir, viewDir));

        float D = DistributionGGX(Normal, halfwayDir, roughness);
        vec3 F = fresnelSchlick(HdotV, reflectance);
        float G = min(1.0, min(2.0 * NdotH * NdotV / HdotV, 2.0 * NdotH * NdotL / HdotV));

        float distance = length(static_lights[i].position - fragPos);
        float attenuation = smoothstep(static_lights[i].range * specular_range_multiplier, 0.0, distance);

        vec3 specularContrib = (D * F * G) / (4.0 * NdotL * NdotV + 0.001);
        specular += specularContrib * static_lights[i].colour * static_lights[i].intensity * attenuation;
    }

    // Diffuse light
    vec3 diffuse = vec3(0.0);
    for (int i = 0; i < numLights; i++) {
        vec3 lightDir = normalize(static_lights[i].position - fragPos);
        float diff = max(0.0, dot(lightDir, Normal));

        // Calculate distance between fragment and light source
        float distance = length(static_lights[i].position - fragPos);

        // Apply range-based attenuation
        float attenuation = smoothstep(static_lights[i].range, 0.0, distance);

        // Apply attenuation to diffuse calculation
        vec3 diffuseContrib = diff * static_lights[i].colour * static_lights[i].intensity * attenuation;

        // Mix diffuse and specular based on metallicness
        vec3 finalContrib = mix(diffuseContrib, specular, metallicness);

        diffuse += finalContrib;
    }

    return diffuse + specular;
}

vec3 getSunLight(vec3 Normal, float roughness, float metallicness) {

    vec3 sunAmbient = sun.Ia;

    // diffuse
    vec3 lightDir = normalize(sun.direction);
    float diff = max(0.0, dot(lightDir, Normal));
    vec3 sunDiffuse = diff * sun.Id;

    // reflectance based off metalicness
    vec3 reflectance = mix(vec3(0.04), vec3(0.5), metallicness);

    // specular
    vec3 viewDir = normalize(camPos - fragPos);
    vec3 halfwayDir = normalize(viewDir + lightDir);

    float NdotL = max(0.0, dot(Normal, lightDir));
    float NdotV = max(0.0, dot(Normal, viewDir));
    float NdotH = max(0.0, dot(Normal, halfwayDir));
    float HdotV = max(0.0, dot(halfwayDir, viewDir));

    float D = DistributionGGX(Normal, halfwayDir, roughness);
    vec3 F = fresnelSchlick(HdotV, reflectance);
    float G = min(1.0, min(2.0 * NdotH * NdotV / HdotV, 2.0 * NdotH * NdotL / HdotV));

    vec3 specularContrib = (D * F * G) / (4.0 * NdotL * NdotV + 0.001);
    vec3 sunSpecular = specularContrib * sun.Is;

    // shadow
    float shadow = getSoftShadowX16();

    vec3 sunLight = sunAmbient + (sunDiffuse + sunSpecular) * shadow;

    return sunLight;
}

void main() 
{
    vec3 viewDir = normalize(camPos - fragPos); // valc view direction

    float gamma = 2.2;
    vec3 normal_comp;

    float roughness = mat_values.x;
    float metallicness = mat_values.y;

    if (norm_rough_metal_height_values.x == 0) {
        normal_comp = normalize(normal);
    } else {
        vec3 normal_map = texture(maps.normal_0, uv_0).rgb;
        vec3 tangent_normal = normalize(normal_map * 2.0 - 1.0);
        vec3 tangent_normal_tangent_space = normalize(TBN * tangent_normal);
        normal_comp = normalize(tangent_normal_tangent_space);
    }

    if (roughness < 0.05) {
        roughness = 0.05;    // to see reflection disk
    } 

    vec3 albedo = texture(diff_0, uv_0).rgb;

    vec3 baseReflectivity = vec3(0.04);
    
    albedo = pow(albedo, vec3(gamma)); // un-gamma correct texture

    vec3 sunLight = getSunLight(normal_comp, roughness, metallicness); // sun light contrib
    vec3 pointLights = getLight(normal_comp, roughness, metallicness); // point light contrib

    float NdotV = max(0.0, dot(normal_comp, viewDir));

    vec3 F = fresnelSchlick(NdotV, baseReflectivity);
    vec3 Kd = (1.0 - F) * (metallicness);
    vec3 diffuse = texture(u_texture_skybox, normal_comp).rgb * albedo * Kd;

    //vec3 viewDir_tex = reflect(-viewDir, normal_comp); // reflected view direction around normal
    //vec3 reflectionColor = texture(u_texture_skybox, reflect(-viewDir, normal_comp)).rgb; // for specular
    float shadow = getSoftShadowX16();
    //colour = colour * (sunLight + pointLights) + min(IBLDiffuse, 0);
    vec3 colour = albedo * (sunLight + pointLights) + min((diffuse * (shadow + 0.06)),0); // adding all colours together

    colour = pow(colour, vec3(1.0 / gamma)); // gamma correction
    fragcolour = vec4(colour, 1.0);
}