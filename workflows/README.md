# Workflows

V6 no longer requires a hand-edited workflow JSON for the first inpainting test.

The local bridge in `server.py` builds and submits a standard ComfyUI API workflow automatically:
- LoadImage
- LoadImageMask
- CheckpointLoaderSimple
- CLIPTextEncode (positive/negative)
- VAEEncodeForInpaint
- KSampler
- VAEDecode
- SaveImage

## Required local model

Set the ComfyUI checkpoint filename with:

`COMFY_MODEL=sd-v1-5-inpainting.safetensors`

The file must exist in the ComfyUI `models/checkpoints` directory.

Do not put model files in GitHub.

## Hardware warning

The target PC has Intel UHD integrated graphics with only 128 MB dedicated VRAM and 16 GB system RAM. The shared graphics memory is system RAM. Use a small test image first and expect CPU-heavy generation to be slow.

If the model does not load or generation is impractically slow, stop rather than installing a large 20B-class image editor on this PC.
