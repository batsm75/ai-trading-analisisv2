"""Helper UI terminal (rich) + fungsi input yang aman."""
from __future__ import annotations

import sys

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# Lima metode analisis — urutan nomor tetap 1..5 sesuai permintaan.
METODE_ANALISIS: list[tuple[str, str]] = [
    ("SND", "Supply & Demand"),
    ("SNR", "Support & Resistance"),
    ("SMC", "Smart Money Concepts"),
    ("ICT", "Inner Circle Trader"),
    ("SESSION KILLZONE", "Session Killzone (London/New York killzone)"),
]

TIMEFRAME_VALID = ["1min", "5min", "15min", "30min", "1h", "2h", "4h", "1day", "1week"]


def banner() -> None:
    console.print(Panel.fit(
        "[bold cyan]AI TRADING TERMINAL[/bold cyan]\n"
        "[dim]Data: TwelveData + SoSoValue  |  Otak: Gemini 2.5 Flash (fallback GPT-4o via Deatcode)[/dim]",
        border_style="cyan",
    ))


def tanya(prompt: str, default: str = "") -> str:
    """Input dengan default. Enter kosong -> pakai default."""
    suffix = f" [dim](default: {default})[/dim]" if default else ""
    val = console.input(f"[yellow]?[/yellow] {prompt}{suffix}: ").strip()
    return val if val else default


def tanya_pilhan(prompt: str, pilihan_valid: list[str], default: str = "") -> str:
    """Loop sampai input valid atau user batal (ketik 'b'/'back')."""
    while True:
        val = tanya(prompt + f" [dim](salah satu: {', '.join(pilihan_valid)})[/dim]", default)
        if val.lower() in ("b", "back", "0"):
            return ""
        if val in pilihan_valid:
            return val
        console.print("[red]  Input tidak valid. Coba lagi (atau ketik b untuk batal).[/red]")


def tekan_enter() -> None:
    console.input("\n[dim]Tekan [Enter] untuk melanjutkan...[/dim]")


def tabel_metode() -> Table:
    t = Table(title="Pilih Metode Analisis (ketik nomor 1-5)", show_header=True, header_style="bold magenta")
    t.add_column("No", style="cyan", justify="center")
    t.add_column("Kode", style="green")
    t.add_column("Keterangan")
    for i, (kode, nama) in enumerate(METODE_ANALISIS, 1):
        t.add_row(str(i), kode, nama)
    return t
