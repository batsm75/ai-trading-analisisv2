# AI Trading Terminal

Aplikasi analisis trading berbasis **terminal** (Termux / Linux / macOS / Windows) yang mengambil data market langsung dari **TwelveData** dan **SoSoValue**, lalu dianalisis oleh AI:

- **DeepSeek** → otak & analisis utama
- **Gemini 2.5 Flash** → pembaca chart pattern otomatis (mendukung API key format baru `AQ.xxxxx`)
- **Deatcode (GPT-4o)** → fallback otomatis jika Gemini kena rate limit / quota habis ([console.deatcode.com](https://console.deatcode.com/))

Semua API key disimpan di file **`.env`** (tidak pernah di-commit ke GitHub).

---

## Daftar Isi

1. [Fitur](#fitur)
2. [Tech Stack](#tech-stack)
3. [Struktur Folder](#struktur-folder)
4. [Instalasi di Termux](#instalasi-di-termux)
5. [Setup API Key](#setup-api-key)
6. [Cara Pakai (Menu Utama)](#cara-pakai-menu-utama)
7. [Upload ke GitHub & Clone](#upload-ke-github--clone)
8. [Pengujian](#pengujian)
9. [Catatan Keamanan & Disclaimer](#catatan-keamanan--disclaimer)
10. [Troubleshooting](#troubleshooting)

---

## Fitur

- **Menu 1 — Analisis**: input simbol & timeframe, tampilkan indikator teknis (SMA, RSI, ATR, support/resistance), analisis AI lengkap (sentimen, struktur market, zone kritis, chart pattern, setup trade dengan entry/SL/TP sesuai risk:reward). Ada tombol **Refresh** dan **Kembali ke Menu Utama**.
- **Menu 2 — Pengaturan Trade**: atur **Risk:Reward** dan pilih **metode analisis** dengan mengetik nomor `1-5`:
  1. SND (Supply & Demand)
  2. SNR (Support & Resistance)
  3. SMC (Smart Money Concepts)
  4. ICT (Inner Circle Trader)
  5. Session Killzone
- **Menu 3 — Env**: edit & simpan API key + URL untuk DeepSeek, Gemini, Deatcode, TwelveData, dan SoSoValue. Nilai ditampilkan tersamar. Ada tombol **Save** dan **Kembali ke Menu Utama**.
- **Fallback otomatis**: jika Gemini mengembalikan `429 / quota habis`, analisis chart pattern otomatis dialihkan ke Deatcode (GPT-4o).
- Pengaturan trade dipersistensikan ke `trading_settings.json`.

## Tech Stack

| Komponen | Teknologi | Alasan |
|---|---|---|
| Bahasa | Python 3.8+ | Kompatibel penuh dengan Termux (Android) |
| UI Terminal | `rich` | Tabel/panel berwarna, rapi di layar kecil |
| HTTP | `requests` | Pemanggilan REST API yang simpel & andal |
| Env | `python-dotenv` | Manajemen API key via `.env` |
| Testing | `pytest` | Unit test logika lokal |
| Data market | TwelveData + SoSoValue | OHLC time series + data tambahan |
| AI | DeepSeek (utama), Gemini 2.5 Flash (chart), Deatcode GPT-4o (fallback) | Rantai redundansi |

## Struktur Folder

```
ai-trading-terminal/
├── main.py                  # Entry point (python main.py)
├── requirements.txt
├── .env.example             # Template API key — salin jadi .env
├── .gitignore               # .env TIDAK ikut ter-commit
├── README.md
├── config/
│   ├── __init__.py
│   └── settings.py          # Memuat semua env var + reload()
├── core/
│   ├── __init__.py
│   ├── menu.py              # Menu utama + menu trade settings + menu env
│   ├── analysis.py          # Alur analisis (refresh / kembali)
│   └── trade_settings.py    # Persistensi R:R & metode analisis
├── services/
│   ├── __init__.py
│   ├── market_data.py       # TwelveData + SoSoValue + indikator lokal
│   └── ai_analyzer.py       # DeepSeek + Gemini + Deatcode fallback
├── utils/
│   ├── __init__.py
│   ├── env_manager.py       # Baca/tulis .env (aman, nilai tersamar)
│   └── helpers.py           # Input aman, validasi simbol/timeframe
└── tests/
    ├── __init__.py
    └── test_basic.py        # Unit test (tanpa koneksi internet)
```

---

## Instalasi di Termux

```bash
# 1. Buka Termux, update paket
pkg update && pkg upgrade -y

# 2. Install Python & Git
pkg install python git -y

# 3. Clone repo (ganti dengan username/repo Anda)
git clone https://github.com/USERNAME/ai-trading-terminal.git
cd ai-trading-terminal

# 4. (Opsional tapi disarankan) virtual environment
python -m venv venv
source venv/bin/activate

# 5. Install dependensi
pip install -r requirements.txt

# 6. Salin template env
cp .env.example .env

# 7. Jalankan
python main.py
```

> Di Linux/macOS/Windows langkahnya sama (sesuaikan `pkg` dengan package manager Anda).

## Setup API Key

Edit `.env` secara manual **atau** jalankan aplikasi lalu pilih **Menu 3 (Env)** untuk mengisi lewat terminal.

| Layanan | Dapatkan di | Format key |
|---|---|---|
| DeepSeek | https://platform.deepseek.com/api_keys | `sk_...` |
| Gemini | https://aistudio.google.com/apikey | **`AQ.xxxxx`** (format baru) — tetap pakai endpoint yang sama, aplikasi sudah mendukungnya |
| Deatcode | https://console.deatcode.com/ | `dc_live_...` (fallback GPT-4o) |
| TwelveData | https://twelvedata.com/register | string acak |
| SoSoValue | dashboard SoSoValue Anda | string acak |

> Jika salah satu key kosong, aplikasi tetap jalan dengan sumber yang tersedia dan menampilkan peringatan — tidak crash.

## Cara Pakai (Menu Utama)

```
 1 — Analisis          (input simbol & timeframe → analisis AI → [R]efresh / [M]enu)
 2 — Pengaturan Trade  (R:R + pilih metode 1-5: SND/SNR/SMC/ICT/Killzone)
 3 — Env               (edit API key → [S]impan / [M]enu)
 0 — Keluar
```

Contoh simbol: `EUR/USD`, `GBP/USD`, `XAU/USD`, `BTC/USD`, `AAPL`.
Timeframe yang valid: `1min, 5min, 15min, 30min, 1h, 4h, 1day` (alias `m15`, `h4`, `1d` juga diterima).

## Upload ke GitHub & Clone

```bash
# Di folder proyek lokal:
cd ai-trading-terminal
git init
git add .
git commit -m "Initial commit: AI Trading Terminal"
git branch -M main
# Buat repo kosong di GitHub (jangan centang README), lalu:
git remote add origin https://github.com/USERNAME/ai-trading-terminal.git
git push -u origin main
```

Clone di perangkat lain / Termux:
```bash
git clone https://github.com/USERNAME/ai-trading-terminal.git
```

**Penting:** `.gitignore` sudah mengecualikan `.env` dan `trading_settings.json`, jadi API key Anda **tidak akan** ter-upload. Setelah clone, jalankan `cp .env.example .env` dan isi key Anda (atau lewat Menu 3).

## Pengujian

```bash
pip install pytest
pytest -v
```

Tes mencakup: validasi simbol/timeframe, perhitungan indikator (SMA/RSI/ATR/support-resistance), save/load pengaturan trade, kelengkapan 5 metode analisis, dan pembangunan prompt. Tes ini **tidak** membutuhkan API key atau koneksi internet.

## Catatan Keamanan & Disclaimer

- Semua secret hanya ada di `.env` — tidak ada hardcoded key di kode.
- `.env` masuk `.gitignore`. Verifikasi dengan `git status` sebelum push.
- Aplikasi ini **alat bantu analisis**, bukan saran finansial dan **bukan jaminan profit**. Selalu kelola risiko Anda sendiri. Trading forex/kripto/saham memiliki risiko tinggi.

## Troubleshooting

| Gejala | Solusi |
|---|---|
| `ModuleNotFoundError` | Jalankan `pip install -r requirements.txt` di folder proyek |
| TwelveData error `api_limit` | Upgrade plan TwelveData atau tunggu reset kuota harian |
| Gemini `429 / quota` | Otomatis fallback ke Deatcode — pastikan `DEATCODE_API_KEY` terisi |
| SoSoValue "endpoint tidak cocok" | Sesuaikan `SOSOVALUE_BASE_URL` di `.env` dengan dokumentasi API Anda |
| Termux lambat | Pakai `CANDLE_LIMIT=50` di `.env` untuk mengurangi data |
