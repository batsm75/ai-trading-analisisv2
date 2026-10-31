# AI Trading Terminal

CLI tool analisis trading berbasis AI yang berjalan di terminal (Termux / Linux / macOS / Windows).
Mengambil data market langsung dari **TwelveData** dan **SoSoValue** via API key, lalu menganalisis
pola chart secara otomatis dengan **Gemini 2.5 Flash** sebagai otak utama. Jika API key Gemini
kena limit/quota habis, otomatis beralih ke **GPT-4o via Deatcode** sebagai cadangan.

> ⚠️ **Disclaimer**: Alat ini hanya untuk edukasi & bantuan analisis. Bukan saran investasi.
> Selalu kelola risiko Anda sendiri.

---

## A. Ringkasan Proyek

| Komponen | Peran |
|---|---|
| TwelveData | Data market utama (forex, saham, crypto, indeks, komoditas) |
| SoSoValue | Data market crypto tambahan (header `x-soso-api-key`) |
| Gemini 2.5 Flash | Otak analisis utama — membaca pola chart dari OHLC |
| Deatcode (gpt-5-mini / dll) | Cadangan otomatis saat Gemini limit (OpenAI-compatible) |
| `.env` | Penyimpanan semua API key (tidak pernah ter-commit) |

**Fitur utama:**
1. **Analisis** — input simbol & timeframe, analisis lengkap (bias, pola chart, level, entry/SL/TP sesuai RR), tombol **Refresh** & **Kembali**.
2. **Pengaturan Trade** — set Risk:Reward + pilih metode analisis (1=SND, 2=SNR, 3=SMC, 4=ICT, 5=SESSION KILLZONE).
3. **Env** — edit & simpan API key/URL (Gemini, Deatcode, TwelveData, SoSoValue) langsung dari menu, plus tombol **[t] Tes koneksi** untuk memverifikasi setiap provider.

---

## B. Tech Stack

- **Python 3.9+** — jalan native di Termux tanpa emulasi.
- `requests` — HTTP client ke semua API.
- `python-dotenv` — memuat `.env`.
- `rich` — tampilan terminal berwarna, tabel, panel.
- Tanpa database — pengaturan disimpan di `storage/config.json` (JSON file).

Pilihan ini sengaja minimal agar instalasi di Termux cepat dan tidak gagal karena dependency native.

---

## C. Arsitektur

```
┌──────────────┐   ambil OHLC   ┌─────────────────┐
│  Menu 1      │ ─────────────► │ TwelveData API  │
│  Analisis    │                └─────────────────┘
│              │   ambil klines ┌─────────────────┐
│              │ ─────────────► │ SoSoValue API   │
└──────┬───────┘                └─────────────────┘
       │ rangkum OHLC + metode + RR
       ▼
┌──────────────────────────┐  utama  ┌──────────────────────┐
│ services/ai_analyzer.py  │ ──────► │ Gemini 2.5 Flash     │
│ (fallback otomatis)      │         │ generateContent      │
│                          │ limit?  └──────────────────────┘
│                          │ ────────┐
└──────────────────────────┘         ▼  cadangan
                          ┌──────────────────────┐
                          │ GPT-4o via Deatcode  │
                          │ /chat/completions    │
                          └──────────────────────┘
```

---

## D. Struktur Folder

```
ai-trading-terminal/
├── run.py                  # entry point: python run.py
├── requirements.txt
├── .env.example            # template (di-commit)
├── .env                    # API key asli (TIDAK di-commit — ada di .gitignore)
├── .gitignore
├── setup_termux.sh         # setup one-command untuk Termux
├── README.md
├── config/
│   └── settings.py         # load .env, reload, daftar field env
├── core/
│   ├── menu.py             # menu utama + loop
│   ├── analysis.py         # submenu 1: alur analisis + prompt
│   ├── trade_settings.py   # submenu 2: RR + metode (config.json)
│   ├── env_manager.py      # submenu 3: edit & simpan .env
│   └── ui.py               # helper rich, daftar metode, input
├── services/
│   ├── market_data.py      # fetch TwelveData + SoSoValue (paralel)
│   └── ai_analyzer.py      # Gemini utama -> Deatcode fallback
├── storage/
│   └── config.json         # pengaturan trade (dibuat otomatis)
└── tests/
    └── test_smoke.py
```

---

## E. Instalasi

### Di Termux (Android)

```bash
# 1. Install Termux dari F-Droid (versi Play Store sudah usang).
# 2. Buka Termux, lalu:
pkg update && pkg install -y python git

# 3. Clone repo (ganti URL dengan repo GitHub Anda):
git clone https://github.com/USERNAME/ai-trading-terminal.git
cd ai-trading-terminal

# 4. Install dependency:
pip install -r requirements.txt

# 5. Salin template env (jika belum ada):
cp .env.example .env

# 6. Jalankan:
python run.py
```

Atau jalankan `bash setup_termux.sh` untuk langkah 2–5 sekaligus.

### Di Linux / macOS / Windows

```bash
git clone https://github.com/USERNAME/ai-trading-terminal.git
cd ai-trading-terminal
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

---

## F. Upload ke GitHub (untuk pertama kali)

Repo ini sudah di-inisialisasi git dengan commit awal. Cukup:

```bash
cd ai-trading-terminal
git remote add origin https://github.com/USERNAME/ai-trading-terminal.git
git branch -M main
git push -u origin main
```

File `.env` **tidak akan ter-upload** karena sudah masuk `.gitignore`.
Yang ter-upload hanya `.env.example` (placeholder).

---

## G. Konfigurasi API Key

Buka aplikasi → pilih **`3. Env`**, lalu isi field berikut (atau edit langsung file `.env`):

| Field | Keterangan | Dapatkan di |
|---|---|---|
| `GEMINI_API_KEY` | Format baru `AQ.xxxxx` atau lama `AIza...` — keduanya didukung. | https://aistudio.google.com/app/apikey |
| `GEMINI_MODEL` | Default `gemini-2.5-flash`. | — |
| `DEATCODE_API_KEY` | Format `dc_live_...`. Sudah diisi di `.env` lokal Anda. | https://console.deatcode.com/ |
| `DEATCODE_MODEL` | Default `gpt-5-mini`. **`gpt-4o` tidak tersedia** di Deatcode. Alternatif: `gpt-5.4`, `gpt-5.5`, `gpt-6-luna`, `deepseek-flash`, `gemini-2.5-pro`, `claude-sonnet-4.5`. Lihat daftar lengkap via menu `3. Env → [t] Tes koneksi`. | — |
| `DEATCODE_BASE_URL` | **Terkonfirmasi** `https://api.deatcode.com/v1` (OpenAI-compatible). | — |

> ℹ️ **Hasil tes nyata**: base URL & endpoint Deatcode sudah benar, key valid. Namun akun membutuhkan **saldo kredit** (HTTP 402 "model terkunci") agar chat completion berjalan — top-up di console.deatcode.com. Tanpa kredit, fallback tidak akan menghasilkan analisis (pesan error akan tampil jelas).
| `TWELVEDATA_API_KEY` | Wajib agar ada data market. | https://twelvedata.com/ (paket gratis) |
| `SOSOVALUE_API_KEY` | Opsional (data crypto tambahan). | https://sosovalue.com/developer |

**Fallback otomatis:** Jika Gemini mengembalikan HTTP 429 / `RESOURCE_EXHAUSTED` / koneksi gagal,
aplikasi mencetak peringatan dan langsung mengalihkan semua analisis berikutnya ke GPT-4o via Deatcode
untuk sisa sesi.

---

## H. Penggunaan Menu

```
1. Analisis
   → Masukkan simbol (BTC/USD, EUR/USD, AAPL, XAU/USD, ...)
   → Pilih timeframe (1min, 5min, 15min, 30min, 1h, 2h, 4h, 1day, 1week)
   → Data diambil, AI menganalisis, hasil ditampilkan lengkap.
   → [R] Refresh | [U] Ubah instrumen | [B] Kembali ke menu utama

2. Pengaturan Trade
   → Risk:Reward (contoh: 1:2, 1:3)
   → Pilih metode analisis dengan mengetik nomor:
      1 = SND (Supply & Demand)
      2 = SNR (Support & Resistance)
      3 = SMC (Smart Money Concepts)
      4 = ICT (Inner Circle Trader)
      5 = SESSION KILLZONE
   → [S] Simpan & kembali

3. Env
   → Lihat semua field (key di-mask), edit semua atau satu per satu.
   → [t] Tes koneksi semua provider (Gemini, Deatcode, TwelveData, SoSoValue) — pakai endpoint gratis.
   → [S] Simpan → konfigurasi langsung dimuat ulang.
   → [B] Kembali
```

---

## I. Pengujian

```bash
python tests/test_smoke.py
# atau:
python -m pytest tests/ -v
```

Smoke test memverifikasi: semua modul bisa di-import, mapping nomor metode benar,
perhitungan ringkasan OHLC benar, dan tulis-baca `.env` berfungsi.

**Yang belum diuji otomatis:** koneksi API nyata (membutuhkan key valid & jaringan).
Uji manual: jalankan `python run.py`, pastikan key terisi, lalu coba menu `1. Analisis`.

---

## J. Status Proyek

**Selesai:**
- ✅ Menu utama 1/2/3 + tombol kembali di setiap submenu
- ✅ Ambil data market paralel TwelveData + SoSoValue (degradasi graceful jika satu gagal)
- ✅ Analisis AI dengan Gemini 2.5 Flash (mendukung key format `AQ.xxxxx`)
- ✅ Fallback otomatis ke GPT-4o via Deatcode saat Gemini limit
- ✅ Pengaturan RR + 5 metode analisis (pilih nomor 1–5), persist ke `config.json`
- ✅ Editor `.env` in-app (masking, simpan, reload langsung)
- ✅ Tombol **Tes Koneksi** tiap provider (endpoint gratis, tanpa bakar kredit)
- ✅ `.env` di-gitignore + `.env.example` disertakan
- ✅ Setup script Termux + smoke test
- ✅ Base URL Deatcode & model name **diverifikasi langsung via API nyata**

**Catatan / yang bisa disesuaikan:**
- Endpoint kline SoSoValue dibuat toleran terhadap beberapa pola path karena dokumentasi
  versi API dapat berubah. Jika gagal, ubah `SOSOVALUE_KLINE_PATH` di `.env` sesuai docs terbaru.
- `DEATCODE_BASE_URL` default `https://api.deatcode.com/v1` — verifikasi dari dashboard
  https://console.deatcode.com/ dan ubah bila berbeda (formatnya OpenAI-compatible).

**Langkah berikutnya (opsional):** tambahkan riwayat analisis, alert harga, integrasi
webhook ke broker, atau multi-timeframe confirmation.
