"""Submenu: 3. Env — lihat & edit API key, simpan ke file .env.

File .env ditulis ulang dengan mempertahankan komentar dan urutan field.
Setelah simpan, Settings.reload() dipanggil agar perubahan langsung aktif.
"""
from __future__ import annotations

from pathlib import Path

from config.settings import ENV_FIELDS, ENV_PATH, Settings
from core.ui import console, tanya


def _baca_env_saat_ini() -> dict[str, str]:
    """Parse .env saat ini menjadi dict (key=value). Abaikan komentar/baris kosong."""
    hasil: dict[str, str] = {}
    if not Path(ENV_PATH).exists():
        return hasil
    for baris in Path(ENV_PATH).read_text().splitlines():
        baris = baris.strip()
        if not baris or baris.startswith("#") or "=" not in baris:
            continue
        key, _, val = baris.partition("=")
        hasil[key.strip()] = val.strip().strip('"').strip("'")
    return hasil


def _tulis_env(data: dict[str, str]) -> None:
    """Tulis ulang .env dengan header komentar + semua field terurut."""
    grup = [
        ("# --- Gemini (otak AI utama) ---", ["GEMINI_API_KEY", "GEMINI_MODEL", "GEMINI_BASE_URL"]),
        ("# --- Deatcode (cadangan GPT-4o) ---", ["DEATCODE_API_KEY", "DEATCODE_MODEL", "DEATCODE_BASE_URL"]),
        ("# --- TwelveData (market data) ---", ["TWELVEDATA_API_KEY", "TWELVEDATA_BASE_URL"]),
        ("# --- SoSoValue (market data crypto) ---", ["SOSOVALUE_API_KEY", "SOSOVALUE_BASE_URL", "SOSOVALUE_KLINE_PATH"]),
    ]
    baris = [
        "# File .env — berisi kredensial asli. JANGAN di-commit ke GitHub.",
        "# Diedit melalui menu '3. Env' atau langsung dengan teks editor.",
        "",
    ]
    for komentar, keys in grup:
        baris.append(komentar)
        for k in keys:
            baris.append(f"{k}={data.get(k, '')}")
        baris.append("")
    Path(ENV_PATH).write_text("\n".join(baris) + "\n")


def _mask(nilai: str) -> str:
    if not nilai:
        return "[dim](kosong)[/dim]"
    if len(nilai) <= 8:
        return nilai[:2] + "***"
    return nilai[:6] + "..." + nilai[-4:]


def menu_env() -> None:
    while True:
        Settings.reload()
        env_saat_ini = _baca_env_saat_ini()

        console.rule("[bold yellow]3. ENV — API KEY & URL[/bold yellow]")
        console.print("[dim]Kosongkan input (Enter) untuk mempertahankan nilai saat ini.[/dim]\n")

        for i, (key, label, _default) in enumerate(ENV_FIELDS, 1):
            console.print(f"  [cyan]{i:>2}.[/cyan] {label:<42} [green]{_mask(env_saat_ini.get(key, ''))}[/green]")

        console.print()
        aksi = tanya(
            "[e] Edit semua field  |  [n] Edit satu field  |  [t] Tes koneksi semua provider  |  [s/b] Kembali",
            "e",
        ).lower()

        if aksi in ("s", "b", "0", "back", ""):
            return

        if aksi in ("t", "tes", "test"):
            from rich.table import Table
            from services.healthcheck import tes_semua
            console.print("\n[dim]→ Mengetes koneksi ke semua provider (maks ~15 detik)...[/dim]\n")
            t = Table(title="Hasil Tes Koneksi", header_style="bold cyan")
            t.add_column("Provider", style="cyan")
            t.add_column("Status")
            t.add_column("Keterangan")
            for nama, ok, msg in tes_semua():
                status = "[green]OK[/green]" if ok else "[red]GAGAL[/red]"
                t.add_row(nama, status, msg)
            console.print(t)
            console.input("\n[dim]Tekan [Enter] untuk kembali...[/dim]")
            continue

        if aksi in ("n", "nomor"):
            nomor = tanya("Nomor field yang ingin diedit", "")
            try:
                idx = int(nomor) - 1
                key, label, default = ENV_FIELDS[idx]
                baru = tanya(f"{label} (sekarang: {_mask(env_saat_ini.get(key, ''))})",
                             env_saat_ini.get(key, default))
                env_saat_ini[key] = baru
            except (ValueError, IndexError):
                console.print("[red]Nomor tidak valid.[/red]")
                continue
        else:
            # Edit semua field satu per satu
            console.print("\n[dim]--- Isi ulang setiap field (Enter = tetap) ---[/dim]")
            for key, label, default in ENV_FIELDS:
                baru = tanya(f"{label}", env_saat_ini.get(key, default))
                env_saat_ini[key] = baru

        _tulis_env(env_saat_ini)
        Settings.reload()
        console.print("\n[green]✓ .env tersimpan dan konfigurasi dimuat ulang.[/green]")
        console.print("[dim]Catatan: .env masuk .gitignore — tidak akan ter-upload ke GitHub.[/dim]")

        lanjut = tanya("\n[s] Kembali ke menu utama  |  [e] Edit lagi", "s").lower()
        if lanjut in ("s", "0", "b", "back", ""):
            return
