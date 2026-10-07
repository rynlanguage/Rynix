#version 450
layout(location=0) in vec3 world_normal;
layout(location=1) in vec2 uv;
layout(location=0) out vec4 output_color;
layout(set=0,binding=0) uniform texture2D image_texture;
layout(set=0,binding=1) uniform sampler image_sampler;
layout(push_constant) uniform Push {
    mat4 mvp;
    vec4 rotation_scale;
    vec4 sun;
    vec4 ambient;
    uvec4 colors;
} p;
void main() {
    vec4 base=unpackUnorm4x8(p.colors.x)*texture(sampler2D(image_texture,image_sampler),uv);
    float lambert=max(dot(normalize(world_normal),-normalize(p.sun.xyz)),0.0);
    vec3 light=p.ambient.rgb*p.ambient.w+unpackUnorm4x8(p.colors.y).rgb*p.sun.w*lambert;
    output_color=vec4(base.rgb*light,base.a);
}
