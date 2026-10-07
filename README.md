# Rynix

Rynix is the planned official 3D, game, and multimedia library for the Ryn
programming language. It aims for the approachable feel of a small application
library, with 3D as its primary focus. Rynix is a library, not a game engine.

The graphics backend is Vulkan. Public APIs describe renderer-independent
concepts; Vulkan setup and handles stay private to the backend.

Rynix is in an early development stage. The current foundation contains
3D-oriented math types, a native window and input layer for Windows, frame
timing, an immediate 2D frame, and a depth-tested cube. Audio is not
implemented yet. Both the 2D frame and the cube draw through a private Vulkan
backend. Rynix 0.2.0 requires Ryn 0.1.0 or newer.

## Current foundation

- `math::Vec2`, `math::Vec3`, and `math::Vec4` with constructors, vector
  arithmetic, dot products, and lengths. `Vec2` and `Vec3` add `neg`,
  `distance`, and `lerp`; `Vec2` adds `normalized`. `Vec3` also has a cross
  product, normalization, `try_normalized() -> Option<Vec3>` for the
  zero-vector case, `from_angles(yaw, pitch)` for a unit direction, and the
  `ZERO`, `ONE`, and `UP` constants. Yaw turns around Y and pitch rises from
  the horizontal plane.
- `math::pi()`, `math::radians`, `math::degrees`, and scalar `math::lerp`.
- `math::Color` with RGB/RGBA constructors, `with_alpha`, and named colors:
  `BLACK`, `WHITE`, `RED`, `GREEN`, `BLUE`, `YELLOW`, `ORANGE`, `PURPLE`,
  `SKY_BLUE`, `LIGHT_GRAY`, `GRAY`, `DARK_GRAY`, and the transparent `BLANK`.
- `math::Mat4` is a column-major 4x4 used for translation, scale, rotation
  around X, Y, and Z, perspective, and `look_at`. `transform_point` applies it
  to a `Vec3`.
- `window::Window` creates, resizes, titles, pumps, and closes a native Win32
  window. Ryn Guard destroys the HWND and releases the loaded system library
  handles when the `Window` leaves scope.
- `window::KeyCode` (letters, digits `NUM0`-`NUM9`, `F1`-`F12`, arrows, and
  common control keys) and `window::MouseButton`. Input is read through the
  window after each `poll_events`:
  - `key_down` / `mouse_down` report what is held. An unfocused window reports
    nothing held, so a key released in another window does not stay stuck.
  - `key_pressed` / `mouse_pressed` and `key_released` / `mouse_released`
    report the transitions that poll saw. They come from the window messages,
    so a tap shorter than one frame is still seen, and keyboard auto-repeat
    does not count as a new press.
  - `mouse_x` / `mouse_y` are relative to the client area; `is_focused` tells
    whether the window has keyboard focus.
- `time::Clock` measures frames on the monotonic clock. `tick()` returns the
  seconds since the previous tick, capped at 0.25 s so one long stall does not
  teleport moving objects. `delta()`, `elapsed()`, and `fps()` read it back.
- `three_d::Camera` stores the eye, target, up vector, and vertical field of
  view in degrees. `move_by` shifts the eye and the target together.
  `look_toward` places the target one step from the eye along a direction.
- `graphics::Gpu::open` creates a private Vulkan device for a window handle.
  `begin` acquires a frame; `clear`, `fill_rect`, and `fill_circle` draw with
  `math::Color`. `draw_cube` draws a depth-tested cube from a camera. The frame
  presents when it leaves scope, and the device is released with the `Gpu`.
  `frame.width()` and `frame.height()` give the drawable size.
- Resizing the window rebuilds the swapchain and depth buffer on the next
  `begin`. While the window is minimized, `begin` returns a frame that draws
  nothing, so the main loop keeps running without special cases.
- Source layout reserved for core, window, graphics, renderer, Vulkan, input,
  audio, and examples.

## Quick start

Add Rynix as a local path dependency in `ryn.yaml`:

```yaml
dependencies:
  rynix:
    path: ../Rynix
```

Then use its math module:

```ryn
use rynix::math

fun main() {
    position := math::Vec3::new(1.0, 2.0, 3.0)
    offset := math::Vec3::new(0.5, 0.0, -1.0)
    moved := position + offset
    echo moved.length()
}
```

Or open a window and draw. `poll_events` pumps the window messages and samples
input; `Clock::tick` gives the frame time, so movement speed does not depend on
the frame rate:

```ryn
use rynix::graphics
use rynix::math
use rynix::three_d
use rynix::time
use rynix::window

fun main() {
    mut window := window::Window::open(1280, 720, "My Ryn game")
    when !window.is_open() { return }
    mut gpu := graphics::Gpu::open(window.native_handle())
    camera := three_d::Camera::new(math::Vec3::new(3.0, 2.0, 4.0), math::Vec3::ZERO, math::Vec3::UP, 45.0)
    mut clock := time::Clock::start()
    mut spin: f32 = 0.0
    mut paused: bool = false
    while window.poll_events_for(1) {
        dt := clock.tick()
        when window.key_down(window::KeyCode::ESCAPE) { window.close() }
        when window.key_pressed(window::KeyCode::P) { paused = !paused }
        when !paused { spin = spin + (1.2 as f32) * dt }
        frame := gpu.begin()
        frame.clear(math::Color::DARK_GRAY)
        frame.draw_cube(camera, math::Vec3::ZERO, math::Vec3::ONE, spin)
        frame.fill_rect(16, 16, 120, 12, math::Color::ORANGE)
    }
}
```

The title-bar close button does not destroy the window. `close()` does.
`poll_events_for(ms)` waits up to `ms` milliseconds for a message before
pumping; a plain sleep would make Windows show the busy cursor.

## Examples

```powershell
ryn run examples/quick_start      # math types printed to the console
ryn run examples/window           # free-fly camera around a spinning cube
ryn run examples/math_check       # exit code 0 when the math helpers agree
ryn run examples/window_smoke     # exit code 0 when the window lifecycle works
ryn run examples/graphics_smoke   # exit code 0 when rendering survives a resize
```

The [window example](examples/window) stays open until Escape. W and S move
along the horizontal view direction, A and D strafe, Space and Control move up
and down, Shift moves faster, the right mouse button looks around, and P pauses
the spinning cube. The first frame does not apply a mouse delta, so the opening
view stays on the cube. The window can be resized freely.

The current window backend uses Win32 on Windows. The 2D frame and the cube
draw through Vulkan on that window; Vulkan handles stay inside the graphics
module.

## License

Rynix is distributed under the Mozilla Public License 2.0. See [LICENSE](LICENSE).
