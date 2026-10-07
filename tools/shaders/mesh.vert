#version 450
layout(location=0) in vec3 position;
layout(location=1) in vec3 normal;
layout(location=2) in vec2 texcoord;
layout(location=0) out vec3 world_normal;
layout(location=1) out vec2 uv;
layout(push_constant) uniform Push {
    mat4 mvp;
    vec4 rotation_scale;
    vec4 sun;
    vec4 ambient;
    uvec4 colors;
} p;
void main() {
    gl_Position = p.mvp * vec4(position, 1.0);
    vec3 n = normal / p.rotation_scale.yzw;
    float c=cos(p.rotation_scale.x), s=sin(p.rotation_scale.x);
    world_normal=normalize(vec3(c*n.x+s*n.z,n.y,-s*n.x+c*n.z));
    uv=texcoord;
}
