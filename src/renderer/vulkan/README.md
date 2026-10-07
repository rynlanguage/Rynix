# Vulkan backend

Vulkan is the graphics backend. The implementation currently lives in
`src/graphics.ryn`, with generated entry-point names and SPIR-V words in
`src/vk_data.ryn`. Vulkan handles, enums, and setup details must stay inside the
backend; public APIs expose renderer-independent concepts only.
