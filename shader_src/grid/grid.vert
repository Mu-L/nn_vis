#version 410 core

layout (location=0) in vec4 position;
layout (location=1) in int density;

out float vs_density;
flat out float vs_discard;

uniform mat4 projection;
uniform mat4 view;
uniform float scale;

void main()
{
    vs_density = density;
    if (density <= 1.0) {
        vs_discard = 0.0;
    } else {
        vs_discard = 0.0;
    }
	gl_Position = projection * view * vec4(position.xyz * scale, 1.0);
}
