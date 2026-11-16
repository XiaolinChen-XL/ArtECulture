"""Shared, provider-neutral utilities for release scripts."""

import base64
import json
import mimetypes
import os
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

RETRY_STATUS = {408, 409, 429, 500, 502, 503, 504}
_CREATED_OUTPUTS = set()


def iter_jsonl(path):
    """Yield JSON objects from a UTF-8 JSONL file."""
    with open(path, encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def append_jsonl(path, record):
    """Append one UTF-8 JSON record."""
    destination = Path(path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if destination in _CREATED_OUTPUTS else "x"
    with destination.open(mode, encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    _CREATED_OUTPUTS.add(destination)


def image_data_url(path):
    """Encode an image as a data URL without exposing its filesystem path."""
    mime = mimetypes.guess_type(path)[0] or "image/jpeg"
    data = base64.b64encode(Path(path).read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def _message_content(result):
    """Extract text from a chat-completions response across provider variants."""
    choices = result.get("choices") or []
    if not choices:
        raise RuntimeError(f"No choices in response: {json.dumps(result)[:200]}")
    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, list):
        content = "".join(part.get("text", "") for part in content
                          if isinstance(part, dict))
    if not content:
        content = message.get("reasoning_content") or ""
    if not content:
        raise RuntimeError(f"Empty content in response: {json.dumps(result)[:200]}")
    return content.strip()


def call_chat(endpoint, model, prompt, image_path=None, api_key_env=None,
              timeout=180, retries=3, max_tokens=512):
    """Call a user-supplied OpenAI-compatible chat-completions endpoint."""
    content = [{"type": "text", "text": prompt}]
    if image_path:
        content.insert(0, {"type": "image_url", "image_url": {"url": image_data_url(image_path)}})
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "temperature": 0,
        "max_tokens": max_tokens,
    }
    headers = {"Content-Type": "application/json"}
    if api_key_env:
        key = os.environ.get(api_key_env)
        if not key:
            raise RuntimeError(f"Environment variable {api_key_env} is not set")
        headers["Authorization"] = f"Bearer {key}"

    body = json.dumps(payload).encode("utf-8")
    for attempt in range(retries):
        request = Request(endpoint, data=body, headers=headers, method="POST")
        try:
            with urlopen(request, timeout=timeout) as response:
                return _message_content(json.loads(response.read().decode("utf-8")))
        except HTTPError as error:
            if error.code not in RETRY_STATUS or attempt == retries - 1:
                raise
        except (URLError, TimeoutError):
            if attempt == retries - 1:
                raise
        time.sleep(2 ** attempt)
    raise RuntimeError("Unreachable: retry loop exhausted without returning.")
