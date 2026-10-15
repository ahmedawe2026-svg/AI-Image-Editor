import base64
import json
import os
import time
import uuid
from email import policy
from email.parser import BytesParser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen
import urllib.error

ROOT = os.path.dirname(os.path.abspath(__file__))
COMFY = os.environ.get("COMFY_URL", "http://127.0.0.1:8188")
MODEL = os.environ.get("COMFY_MODEL", "sd-v1-5-inpainting.safetensors")
TIMEOUT = int(os.environ.get("COMFY_TIMEOUT", "900"))

def http_json(url, payload=None, method="GET", timeout=10):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, method=method, headers={"Content-Type": "application/json"} if data else {})
    with urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def multipart_upload(filename, content, mime="image/png"):
    boundary = "----AIImageEditor" + uuid.uuid4().hex
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'
        f"Content-Type: {mime}\r\n\r\n"
    ).encode("utf-8") + content + f"\r\n--{boundary}--\r\n".encode("utf-8")
    req = Request(
        COMFY + "/upload/image",
        data=body,
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    with urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def build_workflow(image_name, mask_name, prompt):
    negative = os.environ.get(
        "COMFY_NEGATIVE",
        "deformed, distorted, duplicate person, extra limbs, bad anatomy, "
        "bad hands, blurry, low quality, text, watermark"
    )
    return {
        "1": {
            "class_type": "LoadImage",
            "inputs": {"image": image_name}
        },
        "2": {
            "class_type": "LoadImageMask",
            "inputs": {"image": mask_name, "channel": "red"}
        },
        "3": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": MODEL}
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["3", 1], "text": prompt}
        },
        "5": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["3", 1], "text": negative}
        },
        "6": {
            "class_type": "VAEEncodeForInpaint",
            "inputs": {
                "pixels": ["1", 0],
                "vae": ["3", 2],
                "mask": ["2", 0],
                "grow_mask_by": 8
            }
        },
        "7": {
            "class_type": "KSampler",
            "inputs": {
                "seed": int.from_bytes(os.urandom(4), "big"),
                "steps": int(os.environ.get("COMFY_STEPS", "20")),
                "cfg": float(os.environ.get("COMFY_CFG", "7.0")),
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": float(os.environ.get("COMFY_DENOISE", "0.95")),
                "model": ["3", 0],
                "positive": ["4", 0],
                "negative": ["5", 0],
                "latent_image": ["6", 0]
            }
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["7", 0], "vae": ["3", 2]}
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": "AIImageEditor", "images": ["8", 0]}
        }
    }

def wait_for_result(prompt_id):
    deadline = time.time() + TIMEOUT
    while time.time() < deadline:
        try:
            history = http_json(f"{COMFY}/history/{prompt_id}", timeout=10)
            item = history.get(prompt_id)
            if item:
                status = item.get("status", {})
                if status.get("status_str") == "error":
                    messages = status.get("messages", [])
                    raise RuntimeError("ComfyUI execution error: " + json.dumps(messages, ensure_ascii=False))
                outputs = item.get("outputs", {})
                for node in outputs.values():
                    for image in node.get("images", []):
                        params = urlencode({
                            "filename": image["filename"],
                            "subfolder": image.get("subfolder", ""),
                            "type": image.get("type", "output")
                        })
                        with urlopen(f"{COMFY}/view?{params}", timeout=30) as r:
                            return r.read()
        except urllib.error.HTTPError as e:
            if e.code not in (404,):
                raise
        time.sleep(1)
    raise TimeoutError("ComfyUI did not finish before the configured timeout.")

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def send_json(self, obj, code=200):
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == "/api/comfy/status":
            try:
                stats = http_json(COMFY + "/system_stats", timeout=3)
                self.send_json({"ok": True, "url": COMFY, "model": MODEL, "stats": stats})
            except Exception as e:
                self.send_json({"ok": False, "url": COMFY, "model": MODEL, "message": str(e)})
            return
        super().do_GET()

    def do_POST(self):
        if self.path != "/api/edit":
            self.send_json({"message": "Not found"}, 404)
            return

        try:
            content_type = self.headers.get("Content-Type", "")
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            msg = BytesParser(policy=policy.default).parsebytes(
                b"Content-Type: " + content_type.encode() + b"\r\n\r\n" + raw
            )

            fields = {}
            files = {}
            for part in msg.iter_parts():
                name = part.get_param("name", header="content-disposition")
                filename = part.get_filename()
                data = part.get_payload(decode=True) or b""
                if filename:
                    files[name] = (filename, data, part.get_content_type())
                else:
                    fields[name] = data.decode("utf-8", "replace")

            if "image" not in files or "mask" not in files:
                self.send_json({"ok": False, "message": "الصورة والقناع مطلوبان."}, 400)
                return

            prompt = (fields.get("prompt") or "").strip()
            if not prompt:
                self.send_json({"ok": False, "message": "اكتب وصف التعديل أولًا."}, 400)
                return

            image_info = multipart_upload(*files["image"])
            mask_info = multipart_upload(*files["mask"])
            workflow = build_workflow(image_info["name"], mask_info["name"], prompt)

            queued = http_json(COMFY + "/prompt", {"prompt": workflow}, method="POST", timeout=30)
            if "error" in queued:
                self.send_json({
                    "ok": False,
                    "message": "ComfyUI رفض الـWorkflow.",
                    "error": queued
                }, 400)
                return

            prompt_id = queued.get("prompt_id")
            if not prompt_id:
                self.send_json({"ok": False, "message": "لم يرجع ComfyUI رقم المهمة.", "data": queued}, 502)
                return

            output = wait_for_result(prompt_id)
            data_url = "data:image/png;base64," + base64.b64encode(output).decode("ascii")
            self.send_json({"ok": True, "image": data_url, "prompt_id": prompt_id})

        except urllib.error.URLError as e:
            self.send_json({
                "ok": False,
                "message": "تعذر الاتصال بـComfyUI. تأكد أنه يعمل على المنفذ 8188.",
                "error": str(e)
            }, 503)
        except Exception as e:
            self.send_json({"ok": False, "message": str(e)}, 500)

    def log_message(self, fmt, *args):
        print(fmt % args)

if __name__ == "__main__":
    print("AI Image Editor V6 — http://127.0.0.1:8765")
    print("ComfyUI:", COMFY)
    print("Model:", MODEL)
    ThreadingHTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
