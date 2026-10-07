# Changelog

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
