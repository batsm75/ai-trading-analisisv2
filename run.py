#!/usr/bin/env python3
"""Entry point: python run.py"""
from __future__ import annotations

import sys
from pathlib import Path

# Pastikan root proyek ada di sys.path agar import package lokal jalan
sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.menu import main_loop  # noqa: E402

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n\nDiberhentikan oleh user (Ctrl+C).")
        sys.exit(0)
