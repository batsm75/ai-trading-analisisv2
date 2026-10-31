"""Tes koneksi ringan ke setiap provider (tanpa menghabiskan kredit).

Dipanggil dari menu Env via opsi [t]. Setiap tes memakai endpoint murah/gratis:
- Gemini     : POST generateContent dengan maxOutputTokens=1 (1 token, hampir gratis)
- Deatcode   : GET /models (gratis, hanya verifikasi key + daftar model)
- TwelveData : GET /api_usage (gratis)
- SoSoValue  : GET /currencies (gratis)
"""
from __future__ import annotations

import requests

from config.settings import Settings

TIMEOUT = 15


def _ok(msg: str) -> tuple[bool, str]:
    return True, msg


def _gagal(msg: str) -> tuple[bool, str]:
    return False, msg


def tes_gemini() -> tuple[bool, str]:
    if not Settings.GEMINI_API_KEY:
        return _gagal("API key kosong")
    url = f"{Settings.GEMINI_BASE_URL.rstrip('/')}/models/{Settings.GEMINI_MODEL}:generateContent"
    try:
        r = requests.post(
            url,
            headers={"Content-Type": "application/json", "x-goog-api-key": Settings.GEMINI_API_KEY},
            json={"contents": [{"parts": [{"text": "hi"}]}],
                  "generationConfig": {"maxOutputTokens": 1}},
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return _ok(f"terhubung ({Settings.GEMINI_MODEL})")
        if r.status_code == 429 or "RESOURCE_EXHAUSTED" in r.text:
            return _gagal("terhubung tapi quota/limit habis (429) — fallback ke Deatcode akan aktif")
        try:
            err = r.json().get("error", {})
            return _gagal(f"HTTP {r.status_code}: {err.get('message', r.text[:100])}")
        except Exception:
            return _gagal(f"HTTP {r.status_code}")
    except Exception as e:
        return _gagal(f"koneksi gagal: {type(e).__name__}")


def tes_deatcode() -> tuple[bool, str]:
    if not Settings.DEATCODE_API_KEY:
        return _gagal("API key kosong")
    url = f"{Settings.DEATCODE_BASE_URL.rstrip('/')}/models"
    try:
        r = requests.get(url, headers={"Authorization": f"Bearer {Settings.DEATCODE_API_KEY}"}, timeout=TIMEOUT)
        if r.status_code == 200:
            models = r.json().get("data", [])
            ids = [m.get("id") for m in models] if isinstance(models, list) else []
            aktif = Settings.DEATCODE_MODEL in ids
            info = f"{len(ids)} model tersedia"
            info += f", '{Settings.DEATCODE_MODEL}' ADA" if aktif else f", '{Settings.DEATCODE_MODEL}' TIDAK ADA (ganti di .env)"
            return _ok(f"terhubung — {info}. Catatan: butuh kredit agar chat completion jalan.")
        if r.status_code == 402:
            return _gagal("key valid tapi saldo kredit kosong (402) — top-up di console.deatcode.com")
        return _gagal(f"HTTP {r.status_code}: {r.text[:100]}")
    except Exception as e:
        return _gagal(f"koneksi gagal: {type(e).__name__}")


def tes_twelvedata() -> tuple[bool, str]:
    if not Settings.TWELVEDATA_API_KEY:
        return _gagal("API key kosong")
    try:
        r = requests.get(
            f"{Settings.TWELVEDATA_BASE_URL.rstrip('/')}/api_usage",
            params={"apikey": Settings.TWELVEDATA_API_KEY},
            timeout=TIMEOUT,
        )
        if r.status_code == 200 and "message" not in r.json():
            d = r.json()
            used = d.get("current_usage", "?")
            limit = d.get("plan_limit", "?")
            return _ok(f"terhubung — pemakaian {used}/{limit} request/hari")
        return _gagal(f"HTTP {r.status_code}: {r.text[:100]}")
    except Exception as e:
        return _gagal(f"koneksi gagal: {type(e).__name__}")


def tes_sosovalue() -> tuple[bool, str]:
    if not Settings.SOSOVALUE_API_KEY:
        return _gagal("API key kosong")
    try:
        r = requests.get(
            f"{Settings.SOSOVALUE_BASE_URL.rstrip('/')}/currencies",
            headers={"Accept": "application/json", "x-soso-api-key": Settings.SOSOVALUE_API_KEY},
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return _ok("terhubung")
        return _gagal(f"HTTP {r.status_code}: {r.text[:100]}")
    except Exception as e:
        return _gagal(f"koneksi gagal: {type(e).__name__}")


def tes_semua() -> list[tuple[str, bool, str]]:
    return [
        ("Gemini", *tes_gemini()),
        ("Deatcode", *tes_deatcode()),
        ("TwelveData", *tes_twelvedata()),
        ("SoSoValue", *tes_sosovalue()),
    ]
