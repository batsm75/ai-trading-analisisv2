"""Manajemen konfigurasi: memuat .env dan menyediakan akses terpusat."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR: Path = Path(__file__).resolve().parent.parent
ENV_PATH: Path = ROOT_DIR / ".env"
STORAGE_DIR: Path = ROOT_DIR / "storage"
CONFIG_JSON: Path = STORAGE_DIR / "config.json"

STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Daftar field yang bisa diedit lewat menu "Env" (urutan tampil).
ENV_FIELDS: list[tuple[str, str, str]] = [
    # (key env, label tampilan, default bila kosong)
    ("GEMINI_API_KEY",     "Gemini API Key (otak utama)",          ""),
    ("GEMINI_MODEL",       "Gemini Model",                         "gemini-2.5-flash"),
    ("GEMINI_BASE_URL",    "Gemini Base URL",                      "https://generativelanguage.googleapis.com/v1beta"),
    ("DEATCODE_API_KEY",   "Deatcode API Key (cadangan)",          ""),
    ("DEATCODE_MODEL",     "Deatcode Model (mis. gpt-5-mini)",     "gpt-5-mini"),
    ("DEATCODE_BASE_URL",  "Deatcode Base URL (OpenAI-compatible)","https://api.deatcode.com/v1"),
    ("TWELVEDATA_API_KEY", "TwelveData API Key",                   ""),
    ("TWELVEDATA_BASE_URL","TwelveData Base URL",                  "https://api.twelvedata.com"),
    ("SOSOVALUE_API_KEY",  "SoSoValue API Key",                    ""),
    ("SOSOVALUE_BASE_URL", "SoSoValue Base URL",                   "https://openapi.sosovalue.com/openapi/v1"),
    ("SOSOVALUE_KLINE_PATH","SoSoValue Kline Path",                "/currency/historical-klines"),
]


class Settings:
    """Akses konfigurasi runtime. Panggil Settings.reload() setelah .env diubah."""

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta"
    DEATCODE_API_KEY: str = ""
    DEATCODE_MODEL: str = "gpt-5-mini"
    DEATCODE_BASE_URL: str = "https://api.deatcode.com/v1"
    TWELVEDATA_API_KEY: str = ""
    TWELVEDATA_BASE_URL: str = "https://api.twelvedata.com"
    SOSOVALUE_API_KEY: str = ""
    SOSOVALUE_BASE_URL: str = "https://openapi.sosovalue.com/openapi/v1"
    SOSOVALUE_KLINE_PATH: str = "/currency/historical-klines"

    @classmethod
    def reload(cls) -> None:
        load_dotenv(ENV_PATH, override=True)
        for key, _label, default in ENV_FIELDS:
            setattr(cls, key, os.getenv(key, default))

    @classmethod
    def as_dict(cls) -> dict[str, str]:
        return {key: getattr(cls, key) for key, _l, _d in ENV_FIELDS}


Settings.reload()
