# Rynix

Rynix is the planned official 3D, game, and multimedia library for the Ryn
programming language. It aims for the approachable feel of a small application
library, with 3D as its primary focus. Rynix is a library, not a game engine.

The graphics backend will be Vulkan. Public APIs are intended to describe
renderer-independent concepts; Vulkan setup and handles will remain private to
the backend.

Rynix is in an early development stage. The current foundation contains basic
3D-oriented math types and arithmetic. Windowing, input, audio, rendering, mesh
and camera APIs, and the Vulkan backend are not implemented yet.

## Current foundation

- `math::Vec2`, `math::Vec3`, and `math::Vec4` with constructors, vector
  arithmetic, dot products, and lengths; `Vec3` also has a cross product and
  normalization.
- `math::Color` with RGB/RGBA constructors and a few named color constants.
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

Build the example with the current Ryn compiler:

```powershell
ryn run examples/quick_start
```

## License

Rynix is distributed under the Mozilla Public License 2.0. See [LICENSE](LICENSE).
