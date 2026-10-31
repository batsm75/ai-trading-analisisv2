"""Submenu: 1. Analisis — ambil data market, kirim ke AI, tampilkan hasil.

Tombol: [R] Refresh (ambil data ulang + analisis ulang), [B] Kembali ke menu utama.
"""
from __future__ import annotations

from rich.panel import Panel

from config.settings import Settings
from core.trade_settings import muat
from core.ui import TIMEFRAME_VALID, console, tanya, tanya_pilhan
from services.ai_analyzer import AIAnalyzer, AIServiceError
from services.market_data import ambil_data_market, format_untuk_ai


SYSTEM_PROMPT = """Anda adalah analis teknikal profesional. Tugas Anda membaca pola chart
dari data OHLC yang diberikan, lalu menghasilkan setup trading yang jelas.
Gunakan bahasa Indonesia yang ringkas dan terstruktur.

WAJIB ada di laporan:
1. BIAAS (Bullish/Bearish/Netral) + alasan berdasarkan struktur harga.
2. POLA CHART yang terdeteksi (misal: double top, head & shoulders, flag,
   break of structure, order block, supply/demand zone, dll) — sebut level harganya.
3. LEVEL PENTING: support, resistance, zona supply/demand, order block, FVG bila ada.
4. SETUP: zona entry (E), stop loss (SL), take profit (TP).
   Hitung TP berdasarkan risk:reward yang ditentukan user (jika RR=1:R, maka
   jarak TP = R x jarak entry-SL, searah bias).
5. INVALIDASI: kondisi yang membatalkan setup.
6. MANAJEMEN RISIKO: catatan singkat.

Jika data tidak cukup atau tidak ada candle, katakan secara jujur — jangan mengarang harga.
Format dengan heading dan bullet agar mudah dibaca di terminal."""


def _bangun_prompt(data_teks: str, cfg: dict) -> str:
    return (
        f"METODE ANALISIS YANG WAJIB DIGUNAKAN: {cfg['metode_kode']} ({cfg['metode_nama']}).\n"
        f"RISK:REWARD yang dipakai: {cfg['risk_reward']}.\n\n"
        f"DATA MARKET:\n{data_teks}\n\n"
        "Berdasarkan data di atas, lakukan analisis lengkap sesuai format yang diminta."
    )


def _jalankan_analisis(symbol: str, interval: str, ai: AIAnalyzer) -> None:
    cfg = muat()
    console.print(f"\n[dim]→ Mengambil data market untuk {symbol} ({interval})...[/dim]")
    data = ambil_data_market(symbol, interval)

    if not data.get("candles") and not data.get("ringkasan"):
        console.print(Panel(
            "[red]Tidak ada data market yang berhasil diambil.[/red]\n"
            "Kemungkinan: API key TwelveData/SoSoValue belum diisi, simbol tidak dikenal, "
            "atau koneksi gagal.\n"
            f"Error: {' | '.join(data.get('error', ['-']))}",
            title="Gagal Ambil Data", border_style="red",
        ))
        return

    data_teks = format_untuk_ai(data)
    prompt = _bangun_prompt(data_teks, cfg)

    console.print(f"[dim]→ Menganalisis dengan AI (metode {cfg['metode_kode']}, RR {cfg['risk_reward']})...[/dim]")
    try:
        hasil, provider = ai.analisis(prompt, SYSTEM_PROMPT)
    except AIServiceError as e:
        console.print(Panel(f"[red]Kedua provider AI gagal:[/red]\n{e}",
                            title="Error AI", border_style="red"))
        return

    console.rule(f"[bold green]HASIL ANALISIS — {symbol} ({interval})[/bold green]")
    console.print(f"[dim]Provider AI: {provider} | Metode: {cfg['metode_kode']} | RR: {cfg['risk_reward']}[/dim]\n")
    console.print(hasil)
    console.print(f"\n[dim]Sumber data: {', '.join(data.get('sumber_berhasil', ['-']))}[/dim]")


def menu_analisis() -> None:
    """Loop submenu analisis dengan tombol refresh & kembali."""
    ai = AIAnalyzer()
    symbol = ""
    interval = ""

    while True:
        console.rule("[bold blue]1. ANALISIS[/bold blue]")
        if symbol:
            console.print(f"  Instrumen : [green]{symbol}[/green]  |  Timeframe: [green]{interval}[/green]")
            console.print()

        symbol = tanya("Instrumen (contoh: BTC/USD, EUR/USD, AAPL, XAU/USD, GBP/USD)", symbol or "BTC/USD")
        if symbol.lower() in ("b", "back", "0"):
            return
        interval = tanya_pilhan(
            "Timeframe",
            TIMEFRAME_VALID,
            default=interval or "1h",
        )
        if not interval:
            return

        _jalankan_analisis(symbol, interval, ai)

        aksi = tanya(
            "\n[R] Refresh analisis  |  [U] Ubah instrumen/timeframe  |  [B] Kembali ke menu utama",
            "b",
        ).lower()
        if aksi in ("b", "back", "0"):
            return
        if aksi in ("r", "refresh"):
            continue  # pakai symbol & interval yang sama
        # else: ubah -> loop ulang tanya symbol
