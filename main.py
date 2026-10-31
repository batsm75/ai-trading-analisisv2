#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI TRADING TERMINAL
===================
Aplikasi analisis trading berbasis terminal (Termux / Linux / macOS / Windows).
Data market  : TwelveData + SoSoValue (via API key di .env)
Otak AI      : DeepSeek (analisis utama)
Chart pattern: Gemini 2.5 Flash — otomatis fallback ke Deatcode (GPT-4o) jika limit.

Jalankan:  python main.py
"""
import sys
import os

# Pastikan root proyek ada di sys.path agar import package berjalan di Termux
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from utils import env_manager
from core.menu import main_menu

console = Console()

BANNER = r"""
   ___    _____   _____ _____ ___  _   _  ____   ___
  / _ \  |_ _\ \ / /_ _|_   _/ _ \| \ | |/ ___| / _ \
 | | | |  | | \ V / | |  | || | | |  \| | |  _ | | | |
 | |_| |  | |  | |  | |  | || |_| | |\  | |_| || |_| |
  \__\_\ |___| |_| |___| |_| \___/|_| \_|\____(_)___/
        TERMINAL  ·  AI-POWERED MARKET ANALYSIS
"""


def check_python_version() -> bool:
    if sys.version_info < (3, 8):
        console.print("[red]Python 3.8+ dibutuhkan. Versi Anda: "
                      f"{sys.version_info.major}.{sys.version_info.minor}[/red]")
        return False
    return True


def main():
    console.print(f"[cyan bold]{BANNER}[/cyan bold]")
    if not check_python_version():
        sys.exit(1)

    # Pastikan file .env ada (salin dari .env.example bila perlu)
    env_manager.ensure_env_exists()

    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Dibatalkan dengan Ctrl+C. Keluar.[/bold yellow]")
        sys.exit(0)


if __name__ == "__main__":
    main()
