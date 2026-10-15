# V6 Model Strategy

## Hardware constraint
The target PC has:
- Intel Core i5-13400
- 16 GB system RAM
- Intel UHD integrated graphics
- 128 MB dedicated VRAM
- about 8 GB shared graphics memory

The shared memory is system RAM, not dedicated VRAM. Therefore large modern image-editing models are not the first local target.

## First local test
V6 uses the standard ComfyUI inpainting API bridge and is prepared for a Stable Diffusion v1.5 inpainting checkpoint named:

`sd-v1-5-inpainting.safetensors`

The model is designed for masked image editing/inpainting. It is substantially lighter than current 20B-class image editors, but CPU-only generation on this PC is expected to be slow.

Do not place model files in this repository.

## How the bridge works
1. Browser sends the current image, mask and natural-language prompt to `/api/edit`.
2. `server.py` uploads the image and mask to ComfyUI.
3. It submits a ComfyUI API workflow to `/prompt`.
4. It waits for the job in `/history/{prompt_id}`.
5. It retrieves the generated image through `/view`.
6. The browser displays the result.

This follows ComfyUI's documented local API pattern. See the official ComfyUI API examples and server routes.

## Important quality note
The test prompt asks to add a second person while preserving the original person's identity. SD 1.5 inpainting can perform the addition, but it is not an identity-preserving specialist model. If the first test does not preserve the original face well enough, the next upgrade should be a stronger identity-aware workflow on a machine with a discrete GPU rather than forcing a huge model onto this PC.

## Current default parameters
- Resolution: use a small test image first.
- Steps: 20
- CFG: 7
- Denoise: 0.95
- Mask growth: 8 px
- Sampler: Euler
