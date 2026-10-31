"""Otak AI: Gemini (utama) -> GPT-4o via Deatcode (cadangan otomatis).

Fallback otomatis terjadi ketika Gemini mengembalikan HTTP 429 (quota/limit),
error RESOURCE_EXHAUSTED, atau koneksi gagal. Setelah fallback aktif, semua
request berikutnya di sesi ini langsung ke Deatcode (tidak mencoba Gemini lagi).
"""
from __future__ import annotations

import json
from typing import Optional

import requests

from config.settings import Settings

REQUEST_TIMEOUT = 60  # detik


class RateLimitError(Exception):
    """Quota / rate limit habis -> pindah ke provider cadangan."""


class AIServiceError(Exception):
    """Kedua provider gagal dipakai."""


class AIAnalyzer:
    def __init__(self) -> None:
        self.fallback_aktif: bool = False
        self.provider_terakhir: str = "belum ada"

    # ------------------------------------------------------------------ #
    # Gemini (utama) — native generateContent, mendukung key AQ.xxxxx
    # ------------------------------------------------------------------ #
    def _call_gemini(self, prompt: str, system: str) -> str:
        if not Settings.GEMINI_API_KEY:
            raise RateLimitError("GEMINI_API_KEY kosong")

        url = (
            f"{Settings.GEMINI_BASE_URL.rstrip('/')}"
            f"/models/{Settings.GEMINI_MODEL}:generateContent"
        )
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": Settings.GEMINI_API_KEY,
        }
        body = {
            "system_instruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 4096},
        }
        resp = requests.post(url, headers=headers, json=body, timeout=REQUEST_TIMEOUT)

        # Deteksi limit: 429 langsung, atau body error dengan code 429 / RESOURCE_EXHAUSTED
        if resp.status_code == 429:
            raise RateLimitError(f"Gemini HTTP 429: {resp.text[:200]}")

        try:
            data = resp.json()
        except json.JSONDecodeError:
            raise AIServiceError(f"Respons Gemini bukan JSON (HTTP {resp.status_code})")

        if "error" in data:
            err = data["error"]
            code = err.get("code", 0)
            status = str(err.get("status", "")).upper()
            msg = err.get("message", str(err))[:200]
            if code == 429 or status == "RESOURCE_EXHAUSTED":
                raise RateLimitError(f"Gemini quota habis: {msg}")
            raise AIServiceError(f"Gemini error {code} {status}: {msg}")

        if resp.status_code >= 400:
            raise AIServiceError(f"Gemini HTTP {resp.status_code}: {resp.text[:200]}")

        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError):
            raise AIServiceError(f"Format respons Gemini tidak dikenali: {str(data)[:300]}")

    # ------------------------------------------------------------------ #
    # Deatcode (cadangan) — OpenAI-compatible POST /chat/completions
    # ------------------------------------------------------------------ #
    def _call_deatcode(self, prompt: str, system: str) -> str:
        if not Settings.DEATCODE_API_KEY:
            raise AIServiceError("DEATCODE_API_KEY kosong — tidak ada cadangan.")

        url = f"{Settings.DEATCODE_BASE_URL.rstrip('/')}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {Settings.DEATCODE_API_KEY}",
        }
        body = {
            "model": Settings.DEATCODE_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 4096,
        }
        resp = requests.post(url, headers=headers, json=body, timeout=REQUEST_TIMEOUT)

        if resp.status_code == 429:
            raise AIServiceError("Deatcode juga kena rate limit (HTTP 429).")
        if resp.status_code == 402:
            raise AIServiceError(
                "Deatcode: saldo kredit habis / model terkunci (HTTP 402). "
                "Top-up di https://console.deatcode.com/ atau ganti DEATCODE_MODEL ke model yang lebih murah."
            )
        if resp.status_code >= 400:
            raise AIServiceError(f"Deatcode HTTP {resp.status_code}: {resp.text[:200]}")

        try:
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except (json.JSONDecodeError, KeyError, IndexError, TypeError):
            raise AIServiceError(f"Format respons Deatcode tidak dikenali: {resp.text[:300]}")

    # ------------------------------------------------------------------ #
    # Entry point dengan fallback otomatis
    # ------------------------------------------------------------------ #
    def analisis(self, prompt: str, system: str) -> tuple[str, str]:
        """Kembalikan (teks_analisis, nama_provider_yang_dipakai)."""
        if not self.fallback_aktif:
            try:
                hasil = self._call_gemini(prompt, system)
                self.provider_terakhir = f"Gemini {Settings.GEMINI_MODEL}"
                return hasil, self.provider_terakhir
            except RateLimitError as e:
                self.fallback_aktif = True
                print(f"\n[!] Gemini limit/tidak tersedia ({e}).")
                print(f"[!] Beralih otomatis ke cadangan: {Settings.DEATCODE_MODEL} via Deatcode.\n")
            except (requests.ConnectionError, requests.Timeout) as e:
                self.fallback_aktif = True
                print(f"\n[!] Koneksi ke Gemini gagal ({e}). Beralih ke Deatcode.\n")
            except AIServiceError as e:
                # Error non-limit (misal key invalid) — tetap coba cadangan demi usability
                self.fallback_aktif = True
                print(f"\n[!] Gemini error: {e}. Mencoba cadangan Deatcode.\n")

        # Fallback path
        try:
            hasil = self._call_deatcode(prompt, system)
            self.provider_terakhir = f"{Settings.DEATCODE_MODEL} (Deatcode, cadangan)"
            return hasil, self.provider_terakhir
        except (requests.ConnectionError, requests.Timeout) as e:
            raise AIServiceError(f"Koneksi ke Deatcode gagal: {e}")
