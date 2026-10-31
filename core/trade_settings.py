"""Pengaturan trade: risk:reward + metode analisis. Disimpan ke storage/config.json."""
from __future__ import annotations

import json
from pathlib import Path

from config.settings import CONFIG_JSON
from core.ui import METODE_ANALISIS, console, tanya


DEFAULT_SETTINGS = {
    "risk_reward": "1:2",
    "metode_kode": "SMC",
    "metode_nama": "Smart Money Concepts",
}


def muat() -> dict:
    if Path(CONFIG_JSON).exists():
        try:
            data = json.loads(Path(CONFIG_JSON).read_text())
            return {**DEFAULT_SETTINGS, **data}
        except (json.JSONDecodeError, OSError):
            pass
    return dict(DEFAULT_SETTINGS)


def simpan(pengaturan: dict) -> None:
    Path(CONFIG_JSON).write_text(json.dumps(pengaturan, indent=2))


def pilih_metode_dari_nomor(nomor: str) -> tuple[str, str] | None:
    """Nomor '1'..'5' -> (kode, nama). Return None jika invalid."""
    try:
        idx = int(nomor) - 1
        if 0 <= idx < len(METODE_ANALISIS):
            return METODE_ANALISIS[idx]
    except ValueError:
        pass
    return None


def menu_pengaturan() -> None:
    """Submenu: 2. Pengaturan Trade."""
    while True:
        cfg = muat()
        console.rule("[bold magenta]2. PENGATURAN TRADE[/bold magenta]")
        console.print(f"  Risk:Reward saat ini : [green]{cfg['risk_reward']}[/green]")
        console.print(f"  Metode analisis      : [green]{cfg['metode_kode']} — {cfg['metode_nama']}[/green]")
        console.print()

        rr = tanya("Risk:Reward (contoh: 1:2, 1:3, 1:5)", cfg["risk_reward"])
        if not rr:
            rr = cfg["risk_reward"]

        from rich.table import Table
        from core.ui import tabel_metode
        console.print(tabel_metode())
        nomor = tanya("Pilih metode (ketik nomor 1-5, atau Enter untuk tetap)", "")
        metode_kode, metode_nama = cfg["metode_kode"], cfg["metode_nama"]
        if nomor:
            hasil = pilih_metode_dari_nomor(nomor)
            if hasil is None:
                console.print("[red]Nomor tidak valid. Metode tidak diubah.[/red]")
            else:
                metode_kode, metode_nama = hasil

        cfg["risk_reward"] = rr
        cfg["metode_kode"] = metode_kode
        cfg["metode_nama"] = metode_nama
        simpan(cfg)
        console.print(f"\n[green]✓ Tersimpan:[/green] RR={rr}, Metode={metode_kode} ({metode_nama})")

        aksi = tanya("\n[s] Simpan & kembali ke menu utama  |  [u] Ubah lagi", "s").lower()
        if aksi in ("s", "0", "b", "back", ""):
            return
