"""Smoke test: pastikan semua modul bisa di-import dan fungsi dasar berjalan.

Jalankan:  python -m pytest tests/ -v
atau tanpa pytest:  python tests/test_smoke.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def test_imports():
    import config.settings  # noqa
    import services.ai_analyzer  # noqa
    import services.market_data  # noqa
    import core.ui  # noqa
    import core.trade_settings  # noqa
    import core.env_manager  # noqa
    import core.analysis  # noqa
    import core.menu  # noqa


def test_metode_nomor():
    from core.trade_settings import pilih_metode_dari_nomor
    assert pilih_metode_dari_nomor("1") == ("SND", "Supply & Demand")
    assert pilih_metode_dari_nomor("5") == ("SESSION KILLZONE", "Session Killzone (London/New York killzone)")
    assert pilih_metode_dari_nomor("0") is None
    assert pilih_metode_dari_nomor("6") is None
    assert pilih_metode_dari_nomor("abc") is None


def test_ringkas_ohlc():
    from services.market_data import _ringkas_ohlc
    candles = [
        {"open": 100, "high": 110, "low": 95, "close": 105},
        {"open": 105, "high": 115, "low": 100, "close": 112},
    ]
    r = _ringkas_ohlc(candles)
    assert r["highest"] == 115
    assert r["lowest"] == 95
    assert r["current"] == 112
    assert r["jumlah_candle"] == 2


def test_env_tulis_baca():
    import tempfile
    from pathlib import Path
    import core.env_manager as em
    import config.settings as cfg

    # Uji tulis-baca di file temporary agar .env asli tidak tertimpa
    with tempfile.TemporaryDirectory() as tmp:
        tmp_env = Path(tmp) / ".env"
        asli = em.ENV_PATH
        try:
            em.ENV_PATH = tmp_env  # type: ignore[attr-defined]
            data = {"GEMINI_API_KEY": "AQ.test123", "DEATCODE_API_KEY": "dc_live_abc",
                    "GEMINI_MODEL": "gemini-2.5-flash", "GEMINI_BASE_URL": "https://x",
                    "DEATCODE_MODEL": "gpt-4o", "DEATCODE_BASE_URL": "https://y",
                    "TWELVEDATA_API_KEY": "", "TWELVEDATA_BASE_URL": "https://z",
                    "SOSOVALUE_API_KEY": "", "SOSOVALUE_BASE_URL": "https://w",
                    "SOSOVALUE_KLINE_PATH": "/k"}
            em._tulis_env(data)
            terbaca = em._baca_env_saat_ini()
            assert terbaca["GEMINI_API_KEY"] == "AQ.test123"
            assert terbaca["DEATCODE_API_KEY"] == "dc_live_abc"
        finally:
            em.ENV_PATH = asli  # type: ignore[attr-defined]
            cfg.Settings.reload()


if __name__ == "__main__":
    test_imports()
    test_metode_nomor()
    test_ringkas_ohlc()
    test_env_tulis_baca()
    print("SEMUA SMOKE TEST LULUS ✓")
