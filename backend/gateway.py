#!/usr/bin/env python3
"""Small dependency-free LAN gateway for the WALL-E prototype.

API keys stay in the local JSON configuration. The gateway never reads
Codex/CC Switch credentials. AI, image, STT and TTS requests are forwarded to
the configured provider, optionally through a local HTTP proxy.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
import base64
import hashlib
import json
import mimetypes
import os
import re
import struct
import time
import urllib.error
import urllib.request
import zlib

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
CONFIG_PATH = ROOT / "gateway-config.json"

DEFAULT_CONFIG = {
    "profiles": [],
    "active_profile": None,
    "proxy_url": "",
    "settings": {"screenshot_enabled": False, "screenshot_interval": 30},
}

DEVICE = {
    "online": True,
    "mode": "演示设备",
    "battery": 87,
    "wifi": -48,
    "camera": True,
    "microphone": True,
    "speaker": True,
    "last_move": "停止",
    "head": "中立",
    "arm": "收回",
    "last_snapshot": None,
    "transcript": "",
    "audio_state": "空闲",
}
EVENTS = []


def load_config():
    if not CONFIG_PATH.exists():
        return json.loads(json.dumps(DEFAULT_CONFIG))
    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        if not isinstance(config, dict):
            raise ValueError("configuration must be an object")
        config.setdefault("profiles", [])
        config.setdefault("active_profile", None)
        config.setdefault("proxy_url", "")
        config.setdefault("settings", {})
        config["settings"].setdefault("screenshot_enabled", False)
        config["settings"].setdefault("screenshot_interval", 30)
        return config
    except (OSError, ValueError, TypeError):
        return json.loads(json.dumps(DEFAULT_CONFIG))


def save_config(config):
    CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")


def emit(kind, payload):
    EVENTS.append({"id": int(time.time() * 1000), "kind": kind, "payload": payload})
    del EVENTS[:-50]


def controller_action(data):
    """Translate UI labels into the ASCII protocol used by the ESP32."""
    event = {key: value for key, value in data.items() if key in ("camera", "mic", "speaker")}
    head = {
        "左看": "left", "中立": "center", "右看": "right",
        "上看": "up", "下看": "down",
    }.get(data.get("head"), data.get("head"))
    arm = {"抬起": "raise", "收回": "stow"}.get(data.get("arm"), data.get("arm"))
    if head:
        event["head"] = head
    if arm:
        event["arm"] = arm
    return event


def json_bytes(value):
    return json.dumps(value, ensure_ascii=False).encode("utf-8")


def websocket_frame(payload):
    raw = payload.encode("utf-8")
    size = len(raw)
    if size < 126:
        header = bytes([0x81, size])
    elif size < 65536:
        header = bytes([0x81, 126]) + struct.pack(">H", size)
    else:
        header = bytes([0x81, 127]) + struct.pack(">Q", size)
    return header + raw


def placeholder_image():
    """Return a low-cost preview until the camera board posts a JPEG."""
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360">
      <rect width="640" height="360" fill="#202522"/><rect x="20" y="20" width="600" height="320" rx="12" fill="#313a35"/>
      <circle cx="270" cy="180" r="54" fill="#e9b949"/><circle cx="370" cy="180" r="54" fill="#e9b949"/>
      <circle cx="270" cy="180" r="22" fill="#101412"/><circle cx="370" cy="180" r="22" fill="#101412"/>
      <text x="320" y="300" text-anchor="middle" fill="#f4eddf" font-family="Arial" font-size="18">ESP32-S3 CAMERA PREVIEW</text>
    </svg>'''
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def placeholder_png():
    width, height = 320, 180
    rows = bytearray()
    for y in range(height):
        rows.append(0)
        for x in range(width):
            if 70 < x < 145 or 175 < x < 250:
                rows.extend((233, 185, 73) if 45 < y < 135 else (48, 57, 52))
            else:
                rows.extend((32, 37, 34))

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(rows), 9))
        + chunk(b"IEND", b"")
    )
    return "data:image/png;base64," + base64.b64encode(png).decode()


def active_profile(config):
    name = config.get("active_profile")
    return next((p for p in config.get("profiles", []) if p.get("name") == name), None)


def proxy_url(config, profile=None):
    """Profile setting wins; otherwise use config or WALLE_PROXY."""
    return (
        (profile or {}).get("proxy_url")
        or config.get("proxy_url")
        or os.environ.get("WALLE_PROXY", "")
    ).strip()


def opener_for(config, profile=None):
    proxy = proxy_url(config, profile)
    if proxy:
        return urllib.request.build_opener(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def extract_text(data):
    if not isinstance(data, dict):
        return ""
    if isinstance(data.get("output_text"), str):
        return data["output_text"]
    chunks = []
    for item in data.get("output", []) or []:
        for part in item.get("content", []) if isinstance(item, dict) else []:
            if isinstance(part, dict) and isinstance(part.get("text"), str):
                chunks.append(part["text"])
    if chunks:
        return "\n".join(chunks)
    choices = data.get("choices", []) or []
    if choices and isinstance(choices[0], dict):
        message = choices[0].get("message", {}) or {}
        content = message.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "\n".join(p.get("text", "") for p in content if isinstance(p, dict))
    return ""


def relay(profile, payload, config, protocol=None):
    if not profile or not profile.get("base_url") or not profile.get("api_key"):
        return {"ok": False, "mock": True, "text": "网关尚未配置中转站，请填写 Base URL、API Key 和模型。"}
    base = profile["base_url"].rstrip("/")
    protocol = protocol or profile.get("protocol", "responses")
    if protocol == "chat_completions":
        url = base if base.endswith("/chat/completions") else base + "/chat/completions"
        body = {"model": profile.get("model", ""), "messages": payload.get("messages", []), "temperature": 0.3}
    else:
        url = base if base.endswith("/responses") else base + "/responses"
        normalized = []
        for message in payload.get("messages", []):
            item = dict(message)
            if isinstance(item.get("content"), str):
                item["content"] = [{"type": "input_text", "text": item["content"]}]
            normalized.append(item)
        body = {"model": profile.get("model", ""), "input": normalized}
    request = urllib.request.Request(
        url,
        data=json_bytes(body),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + profile["api_key"]},
        method="POST",
    )
    started = time.time()
    try:
        with opener_for(config, profile).open(request, timeout=45) as response:
            data = json.loads(response.read().decode("utf-8"))
        return {
            "ok": True,
            "text": extract_text(data) or "中转站返回了空内容。",
            "latency_ms": round((time.time() - started) * 1000),
            "raw": data,
        }
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, OSError) as exc:
        return {"ok": False, "error": str(exc), "text": "中转站请求失败，请检查 Base URL、模型、代理和网络。"}


def relay_audio(profile, config, endpoint, fields, audio=None, content_type="audio/wav"):
    """Call common OpenAI-compatible audio endpoints when configured."""
    if not profile or not profile.get("base_url") or not profile.get("api_key"):
        return None
    boundary = "----WalleGatewayBoundary"
    parts = []
    for key, value in fields.items():
        parts.append((f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n').encode())
    if audio:
        raw = base64.b64decode(audio)
        parts.append(
            (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="recording.wav"\r\nContent-Type: {content_type}\r\n\r\n').encode()
            + raw
            + b"\r\n"
        )
    body = b"".join(parts) + f"--{boundary}--\r\n".encode()
    base = (profile.get("audio_base_url") or profile["base_url"]).rstrip("/")
    for suffix in ("/responses", "/chat/completions"):
        if base.endswith(suffix):
            base = base[: -len(suffix)]
    request = urllib.request.Request(
        base + endpoint,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}", "Authorization": "Bearer " + profile["api_key"]},
        method="POST",
    )
    try:
        with opener_for(config, profile).open(request, timeout=45) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, OSError):
        return None


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "WalleGateway/1.1"

    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))

    def send_json(self, value, status=200):
        raw = json_bytes(value)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(raw)

    def body(self):
        content_type = self.headers.get("Content-Type", "")
        if content_type.startswith("multipart/form-data"):
            result = {}
            size = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(size)
            match = re.search(r'boundary="?([^;\"]+)', content_type)
            if not match:
                return result
            boundary = ("--" + match.group(1)).encode()
            for part in raw_body.split(boundary):
                if b"\r\n\r\n" not in part:
                    continue
                headers, value = part.split(b"\r\n\r\n", 1)
                value = value.rstrip(b"\r\n-")
                disposition = headers.decode("latin1", "ignore")
                name = re.search(r'name="([^"]+)"', disposition)
                if not name:
                    continue
                key = name.group(1)
                filename = re.search(r'filename="([^"]*)"', disposition)
                if filename and filename.group(1):
                    mime_match = re.search(r"Content-Type:\s*([^\r\n]+)", disposition, re.I)
                    mime = mime_match.group(1) if mime_match else "application/octet-stream"
                    result["image" if key == "file" else key] = "data:" + mime + ";base64," + base64.b64encode(value).decode()
                else:
                    result[key] = value.decode("utf-8", "replace")
            return result
        size = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(size)
        if not raw:
            return {}
        try:
            return json.loads(raw.decode("utf-8"))
        except ValueError:
            return {}

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        config = load_config()
        if path == "/api/health":
            self.send_json({"ok": True, "service": "walle-gateway", "version": "1.1", "proxy": bool(proxy_url(config))})
            return
        if path == "/api/device/state":
            self.send_json(DEVICE)
            return
        if path == "/api/providers":
            safe = [
                {k: p.get(k) for k in ("name", "base_url", "model", "protocol", "supports_image", "supports_audio", "proxy_url")}
                for p in config.get("profiles", [])
            ]
            self.send_json({"profiles": safe, "active_profile": config.get("active_profile"), "proxy_url": proxy_url(config)})
            return
        if path == "/api/events":
            self.send_json({"events": EVENTS[-30:]})
            return
        if path == "/ws/events":
            if self.headers.get("Upgrade", "").lower() == "websocket" and self.headers.get("Sec-WebSocket-Key"):
                accept = base64.b64encode(hashlib.sha1((self.headers["Sec-WebSocket-Key"] + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()).decode()
                self.send_response(101, "Switching Protocols")
                self.send_header("Upgrade", "websocket")
                self.send_header("Connection", "Upgrade")
                self.send_header("Sec-WebSocket-Accept", accept)
                self.end_headers()
                try:
                    self.wfile.write(websocket_frame(json.dumps({"kind": "state", "payload": DEVICE}, ensure_ascii=False)))
                    self.wfile.flush()
                    started = time.time()
                    seen = len(EVENTS)
                    while time.time() - started < 30:
                        if len(EVENTS) > seen:
                            for event in EVENTS[seen:]:
                                self.wfile.write(websocket_frame(json.dumps(event, ensure_ascii=False)))
                            self.wfile.flush()
                            seen = len(EVENTS)
                        time.sleep(0.25)
                except (BrokenPipeError, ConnectionResetError, OSError):
                    pass
                return
            self.send_json({"ok": False, "upgrade_required": True, "message": "请使用 WebSocket 客户端连接此地址；普通客户端可轮询 /api/events。"}, 426)
            return
        if path in ("/", "/index.html"):
            self.serve_file(WEB / "index.html")
            return
        if path == "/README.md":
            self.serve_file(ROOT / "README.md")
            return
        if path.startswith("/assets/"):
            self.serve_file(WEB / path.removeprefix("/"))
            return
        self.send_json({"error": "not found"}, 404)

    def serve_file(self, filename):
        try:
            raw = filename.read_bytes()
        except OSError:
            self.send_json({"error": "file not found"}, 404)
            return
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(str(filename))[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self):
        global DEVICE
        path = urlparse(self.path).path
        data = self.body()
        config = load_config()
        if path == "/api/device/move":
            action = data.get("action", "stop")
            labels = {"forward": "前进", "back": "后退", "left": "左转", "right": "右转", "stop": "停止"}
            DEVICE["last_move"] = labels.get(action, action)
            emit("move", {"action": action})
            self.send_json({"ok": True, "state": DEVICE})
            return
        if path == "/api/device/action":
            if "head" in data:
                DEVICE["head"] = data["head"]
            if "arm" in data:
                DEVICE["arm"] = data["arm"]
            if "mic" in data:
                DEVICE["microphone"] = bool(data["mic"])
            for key in ("camera", "speaker"):
                if key in data:
                    DEVICE[key] = bool(data[key])
            emit("action", controller_action(data))
            self.send_json({"ok": True, "state": DEVICE})
            return
        if path == "/api/camera/snapshot":
            image = data.get("image") or placeholder_image()
            ai_image = data.get("image") or placeholder_png()
            DEVICE["last_snapshot"] = image
            emit("snapshot", {"image": image})
            self.send_json({"ok": True, "image": image, "ai_image": ai_image, "source": "esp32_s3" if data.get("image") else "demo"})
            return
        if path == "/api/voice/transcribe":
            profile = active_profile(config)
            remote = relay_audio(profile, config, "/audio/transcriptions", {"model": data.get("model", "gpt-4o-mini-transcribe")}, data.get("audio_base64"), data.get("content_type", "audio/wav")) if data.get("audio_base64") else None
            result = {"text": (remote or {}).get("text") or data.get("text") or "演示转写：你好，瓦力。", "mock": remote is None}
            DEVICE["transcript"] = result["text"]
            DEVICE["audio_state"] = "已转写"
            emit("transcript", result)
            self.send_json(result)
            return
        if path == "/api/voice/speak":
            text = data.get("text", "")
            profile = active_profile(config)
            remote = None
            if profile and profile.get("supports_audio") and text:
                try:
                    base = (profile.get("audio_base_url") or profile["base_url"]).rstrip("/")
                    for suffix in ("/responses", "/chat/completions"):
                        if base.endswith(suffix):
                            base = base[: -len(suffix)]
                    url = base + "/audio/speech"
                    payload = {"model": data.get("model", "gpt-4o-mini-tts"), "voice": data.get("voice", "alloy"), "input": text, "response_format": "mp3"}
                    req = urllib.request.Request(url, data=json_bytes(payload), headers={"Content-Type": "application/json", "Authorization": "Bearer " + profile["api_key"]}, method="POST")
                    with opener_for(config, profile).open(req, timeout=45) as response:
                        remote = base64.b64encode(response.read()).decode()
                except (urllib.error.URLError, urllib.error.HTTPError, OSError):
                    remote = None
            DEVICE["audio_state"] = "播放中"
            emit("speak", {"text": text})
            self.send_json({"ok": True, "mock": remote is None, "text": text, "audio_base64": remote, "message": "已进入播放队列；接入 ESP32-S3 音频板后播放 TTS 音频。"})
            return
        if path in ("/api/ai/chat", "/api/ai/analyze-image"):
            profile = active_profile(config)
            messages = data.get("messages") or [{"role": "user", "content": data.get("text", "请介绍一下你看到的画面。")}]
            if path.endswith("analyze-image") and data.get("image"):
                prompt = data.get("text", "分析这张图片")
                if profile and profile.get("protocol") == "chat_completions":
                    content = [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": data["image"]}}]
                else:
                    content = [{"type": "input_text", "text": prompt}, {"type": "input_image", "image_url": data["image"]}]
                messages = [{"role": "user", "content": content}]
            result = relay(profile, {"messages": messages}, config)
            result["provider"] = profile.get("name") if profile else "演示模式"
            result["model"] = profile.get("model") if profile else "未配置"
            emit("ai", result)
            self.send_json(result)
            return
        if path == "/api/providers":
            profiles = data.get("profiles", [])
            old = {p.get("name"): p for p in config.get("profiles", [])}
            for profile in profiles:
                if not profile.get("api_key") and profile.get("name") in old:
                    profile["api_key"] = old[profile["name"]].get("api_key", "")
            config["profiles"] = profiles
            config["active_profile"] = data.get("active_profile") or (profiles[0].get("name") if profiles else None)
            if "proxy_url" in data:
                config["proxy_url"] = str(data.get("proxy_url") or "").strip()
            save_config(config)
            self.send_json({"ok": True})
            return
        if path == "/api/settings":
            config["settings"].update(data)
            save_config(config)
            self.send_json({"ok": True, "settings": config["settings"]})
            return
        self.send_json({"error": "not found"}, 404)


def main():
    host = os.environ.get("WALLE_HOST", "0.0.0.0")
    port = int(os.environ.get("WALLE_PORT", "8100"))
    print(f"瓦力网关已启动: http://127.0.0.1:{port}  (局域网: http://电脑IP:{port})")
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
