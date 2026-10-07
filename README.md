# Rynix

Rynix is the 3D/game/multimedia library for Ryn. Version 0.3.0 provides a small
Windows/Vulkan foundation for interactive 3D programs: FPS camera and Raw Input,
indexed meshes, primitives, PNG textures, a glTF/GLB subset, lighting, and CPU
ray/collision queries. Existing immediate 2D drawing and `draw_cube` remain.

The library code, asset readers, geometry generation, and platform/Vulkan
interop are written in Ryn. Windows system libraries provide windowing and PNG
decoding. No companion DLL or Rust build is required by a game using Rynix.
The shader generator under `tools/shaders` is a maintainer tool; generated
SPIR-V words are already shipped in `src/`.

**Compiler requirement:** use the current Ryn source tree with the FFI/borrow
fixes described in [README-VALIDATION.md](README-VALIDATION.md). An older
installed compiler reporting 0.1.2 may lack them. The implementation was checked
and run with the sibling `Ryn/target/release/ryn.exe` built from those sources.

## Dependency

For a released package, Ryn resolves and downloads dependencies from
[pods.ryn-lang.xyz](https://pods.ryn-lang.xyz). Put the release version in your
project's `ryn.yaml`; manual source copying is unnecessary:

```yaml
dependencies:
  rynix: "0.3.0"
```

When developing against this checkout, use a path dependency:

```yaml
dependencies:
  rynix:
    path: ../Rynix
```

## Minimal 3D application

```ryn
use rynix::graphics
use rynix::math
use rynix::three_d
use rynix::time
use rynix::window

fun main() -> i32 {
    mut window := window::Window::open(1280, 720, "My Ryn game")
    when !window.is_open() { return 1 }
    mut gpu := graphics::Gpu::open(window.native_handle())
    when !gpu.is_ready() { return 2 }
    mut camera := three_d::FpsCamera::new(math::Vec3::new(0.0, 2.0, 8.0))
    camera.set_angles(0.0, -10.0)
    mut clock := time::Clock::start()

    while window.poll_events_for(1) {
        dt := clock.tick()
        when window.key_pressed(window::KeyCode::ESCAPE) {
            when window.mouse_captured() { window.release_mouse() }
            else { window.close() break }
        }
        when window.mouse_pressed(window::MouseButton::LEFT) { window.capture_mouse() }
        camera.update(&window, dt)
        view := camera.camera()
        frame := gpu.begin()
        frame.clear(math::Color::rgb(25, 38, 54))
        frame.draw_plane(view, math::Vec3::ZERO, math::Vec2::new(20.0, 20.0), math::Color::GRAY)
        frame.draw_cube_color(view, math::Vec3::new(-1.5, 0.5, 0.0), math::Vec3::ONE, 0.2, math::Color::ORANGE)
        frame.draw_sphere(view, math::Vec3::new(1.5, 1.0, 0.0), 1.0, math::Color::PURPLE)
    }
    return 0
}
```

Click the client area to capture the mouse. WASD moves relative to the camera;
Shift sprints, Space moves up, Ctrl moves down, and the mouse changes yaw/pitch.
Escape first releases the mouse and then closes the window. The title-bar X
also closes it. Losing focus releases capture; regaining focus requires another
click. Raw relative motion continues at the screen edges. The first capture
starts with zero deltas.

Keep each frame scoped inside the loop: its destructor ends recording and
presents. Create Window before Gpu so Gpu is destroyed before the window.
Frames must finish before their Gpu leaves scope. A minimized window yields an
inert frame; a resize recreates the swapchain, depth image and framebuffers.
The renderer computes aspect from the actual frame dimensions.

## Graphics and assets

`graphics` is the public drawing facade. Constructors forward to the CPU
resource modules; Vulkan handles are internal.

| API | Behavior |
| --- | --- |
| `Gpu::open(window.native_handle())`, `is_ready()` | Create and check the Vulkan renderer. |
| `gpu.begin()`, `gpu.width()`, `gpu.height()` | Begin a frame and read the current render extent. |
| `frame.clear(color)`, `fill_rect(x, y, w, h, color)`, `fill_circle(x, y, radius, color)` | Existing 2D operations. Coordinates are pixels. |
| `frame.draw_cube(camera, position, scale, yaw)` | Compatible white cube. |
| `frame.draw_cube_color(camera, position, scale, yaw, color)` | Colored cube. |
| `frame.draw_plane(camera, position, size: Vec2, color)` | XZ plane; size is full X/Z extent. |
| `frame.draw_sphere(camera, position, radius, color)` | Outward-facing indexed sphere. |
| `graphics::Mesh::new(vertices, indices)` | Copy vertex/index slices into an owned CPU mesh. Invalid indices yield an unready mesh. |
| `graphics::Mesh::cube()`, `plane()`, `sphere(segments, rings)` | Reusable generated meshes. Cube/plane have unit extent; sphere has radius one. |
| `graphics::Vertex::new(position, normal, uv)` | Position/normal Vec3 and UV Vec2; 32-byte vertex layout. |
| `graphics::Material::new(color)` | Base color, metallic = 0, roughness = 1. Fields remain editable. |
| `graphics::Texture::load(path)`, `white()` | Decode PNG or create a 1x1 white texture. |
| `graphics::Model::load(path)` | Load the supported glTF 2.0/GLB subset. |
| Mesh/Texture/Model `is_ready()` | Report load/construction success. Mesh and Model also expose vertex/index counts; Texture exposes width/height. |

3D drawing uses vertex/index buffers, a depth buffer with LESS testing/writing,
back-face culling, and dynamic viewport/scissor. Cube yaw and mesh/model yaw are
**radians**. Positive scale components are required. Primitive/color/mesh/model
draw methods return `bool` for successful resource preparation and recording;
the compatible four-argument `draw_cube` has no return value.

Load resources outside the loop and borrow them when drawing:

```ryn
mesh := graphics::Mesh::cube()
texture := graphics::Texture::load("assets/metal.png")
material := graphics::Material::new(math::Color::WHITE)
model := graphics::Model::load("assets/ship.glb")

// Inside a frame, with view := camera.camera():
frame.draw_mesh(&mesh, view, math::Vec3::ZERO, math::Vec3::ONE, 0.0, material)
frame.draw_mesh_textured(&mesh, &texture, view, math::Vec3::new(2.0, 0.0, 0.0), math::Vec3::ONE, 0.0, material)
frame.draw_model(&model, view, math::Vec3::new(-2.0, 0.0, 0.0), math::Vec3::ONE, 0.0)
```

The first draw uploads and caches buffers/images for that device. A device cache
retains CPU allocations until Gpu destruction, so dropping a caller's resource
handle cannot invalidate submitted drawing. CPU handles can outlive a Gpu.
Rendering/resource methods are for one thread. The initial cache supports up to
256 distinct textures per device and does not evict resources early.

PNG decoding preserves RGBA. GPU upload uses a staging buffer, optimal image,
layout transitions, image view, sampler, and descriptor sets. The current 3D
pipeline is opaque: it does not implement alpha blending, mipmaps, or sRGB/PBR.
`metallic` and `roughness` are stored for later shading; the current shader
uses base color, texture, and Lambert lighting.

## Cameras, light, and queries

`three_d::Camera::new(eye, target, up, fov_degrees)` remains available. Public
fields include `aspect`, `near_plane`, and `far_plane` (defaults 16:9, 0.1,
1000). Methods: `move_by`, `look_toward`, `view_matrix`, `projection_matrix`,
`view_projection_matrix`, `view_projection_for(width, height)`, and `center_ray`.
The projection uses Vulkan depth 0..1 and flips clip Y once.

`FpsCamera` exposes `speed`, `sprint_speed`, `sensitivity`, `yaw`, `pitch`,
`fov_degrees`, `near_plane`, and `far_plane`. Defaults are 5 units/s, 10 units/s,
0.12 degrees/pixel, and 60-degree vertical FOV. FPS yaw/pitch are **degrees**;
zero yaw looks along -Z, +90 along +X, and pitch is clamped to -89..89 by
`set_angles`/`look_by`. Methods: `forward`, `right`, `position`, `set_position`,
`set_angles`, `look_by(dx, dy)`, `move_local(forward, right, up, sprint, dt)`,
`update(&window, dt)`, `camera`, and `center_ray`. Combined movement is normalized
so diagonal motion is not faster. Time is seconds.

```ryn
gpu.set_ambient_light(three_d::AmbientLight::new(math::Color::WHITE, 0.25))
gpu.set_directional_light(three_d::DirectionalLight::new(
    math::Vec3::new(-0.4, -1.0, -0.2), math::Color::WHITE, 1.0
))
```

The directional vector points in the direction light travels. Normal inverse
scale and Y rotation are applied before Lambert evaluation. The default device
already has white ambient 0.25 and white directional light 0.8.

`Ray::new(origin, direction)` normalizes nonzero direction. `at(distance)`
evaluates the ray; `intersect_aabb(box)` and `intersect_plane(point, normal)`
return `Option<f32>` distance. An inside AABB hit returns zero. Parallel misses,
hits behind the origin, invalid AABBs, and zero-direction rays are rejected.
Both cameras expose `center_ray()` for interactions.

`Aabb::new(min, max)` has `is_valid`, `contains(point)`, and `intersects(other)`.
`SphereCollider::new(center, radius)` has `contains(point)` and `intersects(other)`.
Touching boundaries count as intersections. These are CPU geometry queries,
independent of Vulkan; they do not add a physics solver.

## Model subset

The loader supports glTF 2.0 JSON with an external binary buffer, or GLB 2.0
with its BIN chunk. It reads the first mesh's first TRIANGLES primitive:
float32 POSITION/NORMAL/TEXCOORD_0, strided buffer views, and unsigned 8/16/32-bit
indices. Missing indices become sequential; missing normals are generated from
triangles; missing UVs become zero. Bounds are checked before reading buffers.

The first primitive's material supplies baseColorFactor, metallicFactor,
roughnessFactor, and a PNG baseColorTexture. PNG may be external or an embedded
bufferView in GLB. Relative file paths resolve against the model file, including
UTF-8 paths. Failure produces an unready Model, with partial allocations freed.

This subset uses mesh-local coordinates. It does not apply the glTF node/scene
hierarchy, node transforms, skins, animations, morph targets, multiple
meshes/primitives/materials, sparse or normalized accessors, data URIs, JPEG,
texture transforms, or required extensions. These limitations are deliberate
and should be considered when exporting a model.
File names may contain literal UTF-8 characters; JSON `\u` escape sequences in
file names are not decoded by this minimal reader.

## Window, math, and time

Window methods retain open/poll/close, width/height, set_size/set_title,
key_down/key_pressed/key_released, mouse_down/mouse_pressed/mouse_released,
mouse_x/mouse_y, and is_focused. New relative input is `mouse_delta_x/y`,
`capture_mouse() -> bool`, `release_mouse()`, and `mouse_captured() -> bool`.
Read input after each poll. Auto-repeat is not a new press; a tap within a poll
records both press and release. Unfocused windows report no held keys.
WM_CLOSE/WM_DESTROY update `is_open()` immediately, without posting a thread-wide
WM_QUIT that would kill a second window. Explicit close and Guard drop are safe
after a native close.

Math includes Vec2/3/4 arithmetic, dot/length, Vec3 cross/normalization,
try_normalized, ZERO/ONE/UP, from_angles (radians), Color RGB/RGBA and named
colors, column-major Mat4 translation/scale/rotations/perspective/look_at/mul/
transform_point, pi/radians/degrees/lerp, and scalar_min/scalar_max/clamp_value.
`time::Clock` has start/tick/delta/elapsed/fps; tick caps long stalls at 0.25 s.

## Examples and verification

Run from this repository's root so sample asset paths resolve:

```powershell
ryn check examples/fps_3d
ryn build examples/fps_3d --release
ryn run examples/fps_3d
./tools/test.ps1 -Native
```

`fps_3d` is a courtyard with stairs, walls, columns, colored primitives,
textured GLB crates, and a ray-based crosshair highlight. It uses the controls
in the minimal example. The original quick_start/window/math_check/window_smoke/
graphics_smoke examples remain. New camera_check and cpu_3d are GPU-free;
native_3d_smoke validates resources, input edges, resize/minimize/restore, and
closing. input_smoke is an interactive Raw Input/focus regression.

See [README-VALIDATION.md](README-VALIDATION.md) for architecture, compiler fixes,
test commands, and the separate compile/CPU/native/image evidence gates.
The backend currently supports Windows/Vulkan. Audio remains unimplemented.

## License

Mozilla Public License 2.0. See [LICENSE](LICENSE).
