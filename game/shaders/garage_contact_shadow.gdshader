shader_type spatial;
render_mode unshaded, blend_mix, depth_draw_never, cull_disabled;

uniform float strength : hint_range(0.0, 1.0) = 0.32;

void fragment() {
    vec2 p = (UV - vec2(0.5)) * vec2(1.0, 1.20);
    float radius = length(p);
    float falloff = 1.0 - smoothstep(0.07, 0.49, radius);
    ALBEDO = vec3(0.008, 0.014, 0.023);
    ALPHA = strength * falloff;
}
