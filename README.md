# Rynix

Rynix is the planned official 3D, game, and multimedia library for the Ryn
programming language. It aims for the approachable feel of a small application
library, with 3D as its primary focus. Rynix is a library, not a game engine.

The graphics backend will be Vulkan. Public APIs are intended to describe
renderer-independent concepts; Vulkan setup and handles will remain private to
the backend.

Rynix is in an early development stage. The current foundation contains basic
3D-oriented math types and arithmetic, a native window and input layer for
Windows, an immediate 2D frame, and a depth-tested cube. Audio is not
implemented yet. Both the 2D frame and the cube draw through a private Vulkan
backend.

## Current foundation

- `math::Vec2`, `math::Vec3`, and `math::Vec4` with constructors, vector
  arithmetic, dot products, and lengths; `Vec3` also has a cross product,
  normalization, `try_normalized() -> Option<Vec3>` for the zero-vector case,
  and `from_angles(yaw, pitch)` for a unit direction. Yaw turns around Y and
  pitch rises from the horizontal plane.
- `math::Color` with RGB/RGBA constructors and a few named color constants.
- `window::Window` creates, resizes, titles, pumps, and closes a native Win32
  window. Ryn Guard destroys the HWND and releases the loaded system library
  handles when the `Window` leaves scope.
- `window::KeyCode` and `window::MouseButton` provide basic key/button polling;
  cursor coordinates are reported relative to the client area.
- `math::Mat4` is a column-major 4x4 used for translation, scale, rotation,
  perspective, and `look_at`.
- `three_d::Camera` stores the eye, target, up vector, and vertical field of
  view in degrees. `move_by` shifts the eye and the target together.
  `look_toward` places the target one step from the eye along a direction.
- `graphics::Gpu::open` creates a private Vulkan device for a window handle.
  `begin` acquires a frame; `clear`, `fill_rect`, and `fill_circle` draw with
  `math::Color`. `draw_cube` draws a depth-tested cube from a camera. The frame
  presents when it leaves scope, and the device is released with the `Gpu`.
- Source layout reserved for core, window, graphics, renderer, Vulkan, input,
  audio, and examples.
- A dependency-based quick start that imports Rynix from a Ryn project.

## Quick start

Add Rynix as a local path dependency in `ryn.yaml`:

```yaml
dependencies:
  rynix:
    path: ../Rynix
```

Then use its math module or open a native window:

```ryn
use rynix::math

fun main() {
    position := math::Vec3::new(1.0, 2.0, 3.0)
    offset := math::Vec3::new(0.5, 0.0, -1.0)
    moved := position + offset
    echo moved.length()
}
```

The initial window API is intentionally explicit about its event pump. `open` resolves the Win32 entry points once and keeps them on the window. `poll_events` then passes a null window filter on every `PeekMessage`, so a quit message is not hidden after the first window message:

```ryn
use rynix::window

fun main() {
    window := window::Window::open(1280, 720, "My Ryn game")
    while window.poll_events() {
        when window.key_down(window::KeyCode::ESCAPE) { window.close() }
    }
}
```

The title-bar close button does not destroy the window. `close()` does. The
[window example](examples/window) stays open until Escape. It draws a spinning
cube on a floor and flies the camera: W and S move along the horizontal view
direction, A and D strafe, Space and Control move up and down, Shift moves
faster, and the right mouse button looks around. The first frame does not apply
a mouse delta, so the opening view stays on the cube.

```ryn
use rynix::graphics
use rynix::math
use rynix::three_d
use rynix::window

fun main() {
    mut window := window::Window::open(1280, 720, "Rynix")
    when !window.is_open() { return }
    mut gpu := graphics::Gpu::open(window.native_handle())
    mut camera := three_d::Camera::new(
        math::Vec3::new(3.2, 2.4, 4.2),
        math::Vec3::new(0.0, 0.2, 0.0),
        math::Vec3::new(0.0, 1.0, 0.0),
        45.0
    )
    mut look_yaw: f32 = 0.0 - 2.4905159321453136
    mut look_pitch: f32 = 0.0 - 0.39478093214777676
    pitch_limit: f32 = 1.4
    look_speed: f32 = 0.004
    mut spin: f32 = 0.8
    mut last_x: i32 = 0
    mut last_y: i32 = 0
    mut looking: bool = false
    while window.poll_events_for(16) {
        when window.key_down(window::KeyCode::ESCAPE) { window.close() }
        x := window.mouse_x()
        y := window.mouse_y()
        dx := (x - last_x) as f32
        dy := (y - last_y) as f32
        when window.mouse_down(window::MouseButton::RIGHT) {
            when looking {
                look_yaw = look_yaw - dx * look_speed
                look_pitch = look_pitch - dy * look_speed
                when look_pitch > pitch_limit { look_pitch = pitch_limit }
                when look_pitch < (0.0 as f32) - pitch_limit {
                    look_pitch = (0.0 as f32) - pitch_limit
                }
            }
            looking = true
        } else {
            looking = false
        }
        last_x = x
        last_y = y
        flat := math::Vec3::from_angles(look_yaw, 0.0)
        right := math::Vec3::new(0.0 - flat.z, 0.0, flat.x)
        mut step := math::Vec3::new(0.0, 0.0, 0.0)
        when window.key_down(window::KeyCode::W) { step = step.add(flat) }
        when window.key_down(window::KeyCode::S) { step = step.sub(flat) }
        when window.key_down(window::KeyCode::D) { step = step.add(right) }
        when window.key_down(window::KeyCode::A) { step = step.sub(right) }
        when window.key_down(window::KeyCode::SPACE) { step = step.add(math::Vec3::new(0.0, 1.0, 0.0)) }
        when window.key_down(window::KeyCode::CONTROL) {
            step = step.add(math::Vec3::new(0.0, 0.0 - 1.0, 0.0))
        }
        mut speed: f32 = 0.1
        when window.key_down(window::KeyCode::SHIFT) { speed = 0.3 }
        when step.length_squared() > (0.0 as f32) {
            camera.move_by(step.normalized().mul(speed))
        }
        camera.look_toward(math::Vec3::from_angles(look_yaw, look_pitch))
        frame := gpu.begin()
        frame.clear(math::Color::rgb(18, 22, 34))
        frame.draw_cube(camera, math::Vec3::new(0.0, -0.56, 0.0), math::Vec3::new(5.0, 0.1, 5.0), 0.0)
        frame.draw_cube(camera, math::Vec3::new(0.0, 0.0, 0.0), math::Vec3::new(1.0, 1.0, 1.0), spin)
        spin = spin + (0.02 as f32)
    }
}
```

```powershell
ryn run examples/window
```

The current window backend uses Win32 on Windows. The 2D frame and the cube
draw through Vulkan on that window. Vulkan handles stay inside the graphics
module.
Run the native window lifecycle smoke example on Windows with:

```powershell
ryn run examples/window_smoke
```

Build the example with the current Ryn compiler:

```powershell
ryn run examples/quick_start
```

## License

Rynix is distributed under the Mozilla Public License 2.0. See [LICENSE](LICENSE).
