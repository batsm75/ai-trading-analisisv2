"""Menu utama aplikasi."""
from __future__ import annotations

from rich.table import Table

from core.analysis import menu_analisis
from core.env_manager import menu_env
from core.trade_settings import menu_pengaturan, muat
from core.ui import banner, console, tanya


def _tabel_menu() -> Table:
    t = Table(show_header=False, box=None, padding=(0, 2))
    t.add_column(style="cyan", justify="center")
    t.add_column()
    t.add_row("1", "[bold]Analisis[/bold] — input timeframe, analisis lengkap, refresh & kembali")
    t.add_row("2", "[bold]Pengaturan Trade[/bold] — risk:reward + pilih metode (SND/SNR/SMC/ICT/Killzone)")
    t.add_row("3", "[bold]Env[/bold] — API key & URL (Gemini, Deatcode, TwelveData, SoSoValue)")
    t.add_row("0", "[bold]Keluar[/bold]")
    return t


def _cek_kunci() -> None:
    """Peringatan di awal jika ada key penting yang kosong."""
    from config.settings import Settings
    kosong = []
    if not Settings.GEMINI_API_KEY and not Settings.DEATCODE_API_KEY:
        kosong.append("Gemini & Deatcode (analisis AI tidak akan jalan)")
    if not Settings.TWELVEDATA_API_KEY and not Settings.SOSOVALUE_API_KEY:
        kosong.append("TwelveData & SoSoValue (tidak ada data market)")
    if kosong:
        console.print("[yellow]⚠ Perhatian:[/yellow]")
        for k in kosong:
            console.print(f"  [yellow]• {k}[/yellow]")
        console.print("  Silakan isi melalui menu [bold]3. Env[/bold] atau edit file .env\n")


def main_loop() -> None:
    banner()
    _cek_kunci()
    cfg = muat()
    console.print(f"[dim]Pengaturan aktif: RR={cfg['risk_reward']}, Metode={cfg['metode_kode']}[/dim]\n")

    while True:
        console.print(_tabel_menu())
        pilihan = tanya("Pilih menu", "")
        if pilihan == "1":
            menu_analisis()
        elif pilihan == "2":
            menu_pengaturan()
        elif pilihan == "3":
            menu_env()
        elif pilihan in ("0", "q", "exit", "keluar"):
            console.print("[cyan]Sampai jumpa. Ingat: kelola risiko Anda.[/cyan]")
            return
        else:
            console.print("[red]Pilihan tidak dikenal. Ketik 1, 2, 3, atau 0.[/red]\n")
