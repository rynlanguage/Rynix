# Changelog

## 0.3.1 - 2026-10-08

- `physics`: `CharacterController` with gravity, jumping, grounded state, and
  axis-aligned collision against `three_d::Aabb` solids, with sub-stepping.
- `procgen`: seeded `Random`, integer-hash value noise, `fractal_noise`, and a
  `Terrain` height helper. Output is deterministic per seed.
- `text`: built-in 5x7 ASCII bitmap font, `text::width`, and `Frame::draw_text`
  drawn as filled rectangles.
- `audio`: winmm waveOut output with `Sound::tone`, `Sound::silence`, `Output`
  with `play`, `stop`, `is_playing`, and `wait`. The old placeholder is gone.
- `three_d::Fog` and `three_d::PointLight`, set with `Gpu::set_fog` and
  `Gpu::set_point_light`, evaluated per pixel in the mesh fragment shader.
- Mesh shaders are now built in Ryn: `spirv` is a small SPIR-V writer and `shaders`
  describes the vertex and fragment stages. The generated GLSL words,
  `mesh_vertex`/`mesh_fragment`, and the `tools/shaders` naga generator are removed. The mesh push block grew to 224 bytes;
  `Gpu::open` needs `maxPushConstantsSize` of at least 224.
- Examples: `physics_check`, `features_check`, `audio_smoke` (run by the test
  script), and `game_features` (interactive demo, not run unattended).

## 0.3.0

- WM_CLOSE/WM_DESTROY update native window state immediately; explicit close,
  Guard destruction, and independent windows retain safe lifecycles.
- Raw Input mouse deltas, capture/release, cursor hiding, clipping, and focus-loss
  release. Keyboard auto-repeat no longer produces new press edges.
- FPS camera, camera view/projection/near/far/aspect methods, center rays, AABB
  and sphere queries, ray/AABB and ray/plane intersections.
- Shared indexed 3D pipeline for cube, plane, sphere, custom mesh and model;
  vertex/index buffers, per-object color/material, normals/UV, back-face culling.
- PNG loading in Ryn through Windows Imaging Component; optimal Vulkan image
  upload, views, samplers and descriptors with explicit cleanup.
- Minimal glTF 2.0/GLB loader, external or embedded PNG, material fields,
  interleaved attributes, unsigned indices and generated missing normals.
- Ambient/directional Lambert light with inverse-scale/Y-rotation normals.
- graphics facade resource constructors; compatible old draw_cube and new
  colored primitive, mesh, textured mesh and model drawing methods.
- FPS courtyard, CPU camera/assets checks, native lifecycle regression,
  interactive Raw Input regression, shader sources/generator and test script.
- Requires the current Ryn compiler FFI/borrow fixes. See README-VALIDATION.md
  for the distinction from an older installed 0.1.2 compiler.

## 0.2.0

- Resizing the window rebuilds the swapchain, its views, the depth buffer, and
  the framebuffers on the next `Gpu::begin`. A minimized window yields frames
  that draw nothing, and `VK_ERROR_OUT_OF_DATE_KHR` triggers a rebuild instead
  of stopping rendering.
- `Frame::width`, `Frame::height`, `Gpu::width`, and `Gpu::height`.
- Input is sampled once per `poll_events`. `key_pressed`, `key_released`,
  `mouse_pressed`, and `mouse_released` come from the window messages, so short
  taps are not lost and auto-repeat is not a new press. `key_down` and
  `mouse_down` report nothing held while the window is unfocused.
  `Window::is_focused`. `poll_events` and `poll_events_for` now take `mut self`.
- `KeyCode::NUM0`-`NUM9` and `F1`-`F12`.
- `time::Clock` with `tick`, `delta`, `elapsed`, and `fps`.
- Math: `pi`, `radians`, `degrees`, scalar `lerp`; `Vec2`/`Vec3` `neg`,
  `distance`, `lerp`; `Vec2::normalized`; `Vec3::ZERO`, `ONE`, `UP`;
  `Mat4::rotation_x`, `rotation_z`, `transform_point`.
- Colors: `with_alpha`, `YELLOW`, `ORANGE`, `PURPLE`, `SKY_BLUE`, `LIGHT_GRAY`,
  `GRAY`, `DARK_GRAY`, `BLANK`.
- The window example moves and spins by frame time and pauses with P.
- New `math_check` and `graphics_smoke` examples that report failures through
  their exit code.

## 0.1.0

- Win32 window with keyboard and mouse polling.
- Private Vulkan backend: 2D clear, rectangles and circles, and a depth-tested
  cube drawn from a `three_d::Camera`.
- `Vec2`, `Vec3`, `Vec4`, `Color`, and `Mat4`.
