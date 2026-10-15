# Hardware Profile — Current Test Machine

## Confirmed GPU

- GPU: Intel(R) UHD Graphics
- Dedicated VRAM: 128 MB
- Shared memory: about 8002 MB
- Direct3D: 12
- WDDM: 3.1
- System RAM: 16 GB

## Decision

The machine does **not** have a discrete GPU with usable dedicated VRAM for modern local diffusion image-editing models.

The 8 GB shown as shared GPU memory must not be treated as 8 GB of real VRAM. It is system RAM shared with the integrated GPU.

## Model strategy

Do not install a large Qwen Image Edit / FLUX-class workflow on this machine as the primary local path.

Current plan:

1. Keep the lightweight local editor and ComfyUI bridge.
2. Add ordinary CPU/local image operations immediately.
3. Keep generative AI as an optional backend.
4. Before downloading multi-GB model files, perform a small compatibility test.
5. If local generative inference is too slow or incompatible with Intel UHD, support an optional remote/strong-PC backend without making it mandatory.

## Important

Community low-VRAM Qwen workflows are primarily documented/tested around discrete GPUs. Some GGUF/offloading approaches reduce VRAM requirements, but they do not turn Intel UHD into a high-VRAM accelerator.

The project must therefore avoid promising real-time local generative editing on this PC.

## Target test

Prompt:

> أضف شريكًا يجلس بجانبها بكل حب وود، مع الحفاظ على ملامحها وإضاءة الصورة وتناسق المشهد.

Success means the application can submit an image + prompt to a compatible AI backend and display the returned image. The backend may be local or optional remote depending on hardware capability.
