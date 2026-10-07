# 0.3.0 validation and architecture

Rynix extends the existing Win32 window, Vulkan device/swapchain, 2D pipeline,
depth target, math types, and Ryn Guard destructors. It does not introduce a
second renderer or a native companion library.

The 3D pipeline now consumes indexed `Vertex` buffers. Cube, plane, sphere,
custom meshes, and glTF models all use that pipeline. Textures use optimal
Vulkan images, a host staging buffer, explicit transfer/shader barriers,
an image view, a sampler, and descriptor sets. Push constants are 128 bytes,
within Vulkan's required minimum. Normals account for nonuniform scale and
Y rotation. Lighting is ambient plus directional Lambert.

CPU mesh/texture allocations have explicit reference counts. Handles own one
reference. A device cache retains another while GPU resources exist. Device
destruction waits for work, releases Vulkan objects, then releases CPU cache
references. Resources loaded before a device, or surviving a device, remain
valid CPU objects. Rendering and resource operations belong to one thread.

The optional App wrapper is deferred: the existing explicit Window/Gpu/Clock
scope makes the frame/device/window destruction order clear, and needs only
three initializers. No ECS, editor, scene ownership, or physics engine was added.

## Reproduce

From the Rynix root on Windows, using the Ryn executable built from the sibling
compiler tree:

```powershell
./tools/test.ps1 -Native
../Ryn/target/release/ryn.exe run examples/fps_3d
```

The script checks and builds every example, runs CPU regressions, and with
`-Native` also runs short Win32/Vulkan regressions. It stops at the first failed
compiler or program exit. `input_smoke` is interactive and deliberately excluded
from unattended runs. Its 20-second run requires click/capture, mouse movement,
W, Shift+W, Space, Ctrl, F2 for focus loss, another click to capture, and X close.

The sibling compiler's regression command is `cargo test --release`. New
`tests/native_ffi_memory.rs` covers C record field offsets, aggregate copying,
pointer slots, pointer/address round trips, reads through the original addressed
local, preservation of other fields after local assignment, borrowed resource
destruction, and rejection of ownership copies/handle replacement.

## Evidence gates

- Native CPU runs validate yaw/pitch, camera-relative movement, sprint speed,
  movement split across timesteps, diagonal normalization, near/far projection,
  sphere winding, AABB/sphere overlap, and ray hits/misses/parallel/inside cases.
- PNG, external-buffer glTF, and GLB with embedded PNG load actual fixture data.
  Truncated GLB and an out-of-range accessor are rejected.
- `native_3d_smoke` creates Vulkan vertex/index buffers, uploads PNG textures,
  draws models/meshes/primitives, tests keyboard edges/repeat/taps, rebuilds the
  900x600 targets, minimizes/restores, and checks both WM_CLOSE and WM_DESTROY.
- `fps_3d` has been viewed through Windows.Graphics.Capture, including mouse
  look, forward movement, textured objects, lighting, and a resize. Clicking
  the title-bar X exits normally.
- The interactive input regression passed with real injected relative mouse
  movement, W/Shift+W, Space/Ctrl, focus loss, and recapture. Equal-duration
  forward movement measured 2.11 units normally and 4.19 units while sprinting.
- All ten examples pass check/build; CPU and native regressions pass. The
  sibling compiler's full release suite passes 346 tests, including five new
  FFI memory and resource borrowing regressions.

Compilation, CPU execution, Win32/Vulkan execution, and inspection of rendered
frames are separate checks. These results concern Windows on the tested Vulkan
device; no Linux/macOS renderer or hardware matrix is claimed.

## Compiler changes

Rynix 0.3.0 needs the current sibling compiler sources. Its changes are generally
useful FFI operations: reading/writing `#[repr(C)]` pointer fields, copying POD
records through pointers, reading/writing pointer slots, pointer-to-64-bit-address
casts, and borrowing a custom-destructor object without consuming it. Whole
resource dereference and replacement of a borrowed resource's first handle
remain rejected by Ryn Guard. Addressed C records now read their actual stack
memory with C offsets, including array fields, rather than stale SSA values.

The previously installed Ryn release may lack these changes even if its version
string is also 0.1.2. Rebuild/update the compiler before using this package.
