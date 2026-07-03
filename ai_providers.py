"""
Modul ini menangani komunikasi ke 5 provider AI berbeda.
Semua provider kecuali Gemini memakai format OpenAI-compatible (chat/completions),
jadi bisa pakai satu fungsi generik untuk menghemat kode.
"""

import base64
import requests
from config import API_KEYS, MODEL_NAMES

TIMEOUT = 120


class AIError(Exception):
    pass


def _openai_compatible_chat(base_url, api_key, model, messages, image_bytes=None):
    """Dipakai oleh OpenAI, Grok (xAI), DeepSeek, dan Kimi (Moonshot) karena
    keempatnya kompatibel dengan format Chat Completions ala OpenAI."""
    if not api_key:
        raise AIError("API key belum diisi di file .env untuk model ini.")

    final_messages = list(messages)

    # Kalau ada gambar (foto soal dsb), sisipkan ke pesan terakhir sebagai image_url base64
    if image_bytes:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        last = final_messages[-1]
        final_messages[-1] = {
            "role": "user",
            "content": [
                {"type": "text", "text": last["content"]},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
            ],
        }

    resp = requests.post(
        f"{base_url}/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        json={"model": model, "messages": final_messages, "temperature": 0.7},
        timeout=TIMEOUT,
    )

    if resp.status_code != 200:
        raise AIError(f"Error {resp.status_code} dari server: {resp.text[:300]}")

    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise AIError(f"Format respons tidak dikenali: {data}")


def _gemini_chat(api_key, model, messages, image_bytes=None):
    if not api_key:
        raise AIError("API key belum diisi di file .env untuk Gemini.")

    # Gemini memakai format "contents" dengan role user/model, bukan system/user/assistant
    contents = []
    system_instruction = None
    for m in messages:
        if m["role"] == "system":
            system_instruction = m["content"]
            continue
        role = "model" if m["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})

    if image_bytes and contents:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        contents[-1]["parts"].append(
            {"inline_data": {"mime_type": "image/jpeg", "data": b64}}
        )

    body = {"contents": contents}
    if system_instruction:
        body["system_instruction"] = {"parts": [{"text": system_instruction}]}

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    resp = requests.post(url, json=body, timeout=TIMEOUT)

    if resp.status_code != 200:
        raise AIError(f"Error {resp.status_code} dari server: {resp.text[:300]}")

    data = resp.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise AIError(f"Format respons tidak dikenali: {data}")


PROVIDER_BASE_URLS = {
    "openai": "https://api.openai.com/v1",
    "grok": "https://api.x.ai/v1",
    "deepseek": "https://api.deepseek.com",
    "kimi": "https://api.moonshot.ai/v1",
}


def ask_ai(provider: str, messages: list, image_bytes: bytes = None) -> str:
    """Titik masuk tunggal. provider: openai | gemini | grok | deepseek | kimi"""
    model = MODEL_NAMES[provider]
    api_key = API_KEYS[provider]

    if provider == "gemini":
        return _gemini_chat(api_key, model, messages, image_bytes)

    base_url = PROVIDER_BASE_URLS[provider]
    return _openai_compatible_chat(base_url, api_key, model, messages, image_bytes)
