# 🤖 Bot Kuliah AI — Abdul Hamid Maulana (Polije Informatika)

Bot Telegram pribadi yang terhubung ke 5 model AI (Gemini, OpenAI/GPT, Grok, DeepSeek, Kimi)
untuk membantu kuliah: tanya jawab, ringkas materi, bikin soal latihan, kelola jadwal & tugas,
sampai analisis foto soal. Dirancang supaya bisa jalan 24/7 cukup dari **Termux**.

---

## 1. Persiapan sebelum instalasi

### a. Buat Bot Telegram
1. Buka Telegram, cari **@BotFather**.
2. Ketik `/newbot`, ikuti instruksinya (kasih nama & username bot).
3. BotFather akan kasih **token** seperti `123456789:AAExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`. Simpan ini.

### b. Cari ID Telegram kamu sendiri
1. Cari **@userinfobot** di Telegram, chat apa saja ke dia.
2. Dia akan balas dengan ID kamu (angka). Simpan ini — dipakai supaya bot **hanya bisa dipakai kamu**.

### c. Kumpulkan API Key AI yang mau dipakai
Kamu tidak wajib mengisi semuanya — isi saja yang kamu punya, sisanya biarkan kosong di `.env`.

| Provider | Tempat membuat API key |
|---|---|
| Google Gemini | https://aistudio.google.com/apikey |
| OpenAI (GPT) | https://platform.openai.com/api-keys |
| Grok (xAI) | https://console.x.ai |
| DeepSeek | https://platform.deepseek.com/api_keys |
| Kimi (Moonshot AI) | https://platform.moonshot.ai |

> 💡 Saran buat mahasiswa: mulai dari **Gemini** dulu karena punya free tier paling murah hati.
> Tambahkan provider lain belakangan kalau perlu.

---

## 2. Instalasi di Termux (langkah demi langkah)

Buka aplikasi **Termux** di HP kamu, lalu jalankan perintah berikut satu per satu:

```bash
# 1. Update paket Termux
pkg update -y && pkg upgrade -y

# 2. Install Python & git
pkg install python git -y

# 3. (Opsional tapi disarankan) izinkan Termux akses penyimpanan HP
termux-setup-storage
```

### Pindahkan project ke HP kamu
Kalau kamu dapat folder project ini dari Claude (hasil download), pindahkan ke Termux, misalnya:

```bash
# Kalau file ada di folder Download HP
cp -r /sdcard/Download/telegram-ai-bot ~/telegram-ai-bot
cd ~/telegram-ai-bot
```

Atau kalau kamu upload ke GitHub sendiri nanti, tinggal `git clone`.

### Install dependency Python
```bash
pip install -r requirements.txt
```

### Konfigurasi API key
```bash
cp .env.example .env
nano .env
```
Isi `TELEGRAM_BOT_TOKEN`, `OWNER_ID`, dan API key yang kamu punya. Setelah selesai, tekan
`CTRL+X`, lalu `Y`, lalu `Enter` untuk simpan.

### Jalankan bot
```bash
python bot.py
```

Kalau muncul log `Bot mulai berjalan...`, buka Telegram, cari bot kamu, dan ketik `/start`. Selesai! 🎉

---

## 3. Supaya bot tetap jalan meski Termux ditutup

Termux biasa akan mati kalau HP di-lock lama atau aplikasi ditutup. Ada 2 cara mengatasi:

### Cara A — `termux-wake-lock` + jalankan di background (paling simpel)
```bash
termux-wake-lock          # cegah Termux "ditidurkan" Android
nohup python bot.py > bot.log 2>&1 &   # jalankan di background
```
Untuk cek botnya masih hidup: `tail -f bot.log`
Untuk menghentikan: `pkill -f bot.py`

### Cara B — pakai `tmux` (lebih rapi, bisa dibuka-tutup sesi)
```bash
pkg install tmux -y
tmux new -s bot
python bot.py
# tekan CTRL+B lalu D untuk keluar dari sesi tanpa mematikan bot
```
Untuk kembali melihat botnya: `tmux attach -t bot`

> 📌 Catatan jujur: HP Android tetap bisa mematikan proses latar belakang kalau baterai
> hemat daya aktif. Buka pengaturan baterai HP → cari Termux → set ke "Tanpa batasan"/
> "Unrestricted" supaya bot tidak mati sendiri.

---

## 4. Cara memakai bot

### Ngobrol dengan AI
Tinggal ketik pesan apa saja ke bot, langsung dijawab oleh AI yang sedang aktif.
Riwayat percakapan otomatis diingat sampai kamu ketik `/clear`.

### Ganti AI yang dipakai
`/model` → muncul tombol pilihan Gemini / GPT / Grok / DeepSeek / Kimi.
Cocok untuk membandingkan jawaban antar model untuk tugas yang sama.

### Kirim foto soal/materi
Kirim foto (misalnya foto soal ujian atau slide dosen) dengan caption pertanyaanmu.
Bot akan menganalisis gambarnya. Paling akurat pakai model **Gemini** atau **OpenAI**.

### Perintah bantuan belajar
| Perintah | Fungsi |
|---|---|
| `/ringkas <teks>` atau reply pesan lalu `/ringkas` | Ringkas materi panjang jadi poin-poin |
| `/jelaskan <topik>` | Penjelasan konsep dengan bahasa mudah + contoh |
| `/soal <topik>` | Bikin 5 soal latihan + kunci jawaban |
| `/translate <bahasa>\|<teks>` | Terjemahkan teks |

### Manajemen jadwal kuliah
```
/jadwal_tambah Senin|08:00|Algoritma Pemrograman
/jadwal_lihat
/jadwal_hapus
```

### Manajemen tugas & deadline
```
/tugas_tambah Laporan Praktikum Basis Data|10 Juli 2026
/tugas_lihat
/tugas_selesai 1
```
Bot juga otomatis mengirim pengingat semua tugas yang belum selesai **setiap jam 07:00 pagi**
(asal Termux/bot tetap menyala — lihat bagian 3).

### Catatan kuliah
```
/catatan_tambah Rumus Big-O|O(1) konstan, O(n) linear, O(log n) logaritmik...
/catatan_lihat
```

---

## 5. Fitur-fitur yang sangat membantu (ringkasan)

- ✅ **Multi-AI dalam satu bot** — bandingkan jawaban Gemini vs GPT vs Grok vs DeepSeek vs Kimi tanpa pindah aplikasi.
- ✅ **Riwayat percakapan otomatis** — AI ingat konteks obrolan sebelumnya (mirip ChatGPT).
- ✅ **Analisis foto soal/slide** — foto soal ujian, tinggal tanya ke bot.
- ✅ **Ringkasan materi instan** — paste materi panjang, dapat poin-poin penting.
- ✅ **Generator soal latihan** — bikin bank soal sendiri untuk belajar sebelum ujian.
- ✅ **Manajemen jadwal & tugas kuliah** — pengganti aplikasi to-do terpisah.
- ✅ **Reminder deadline otomatis** — tidak perlu buka bot untuk diingatkan.
- ✅ **Privat & aman** — hanya kamu (lewat `OWNER_ID`) yang bisa memakai bot.
- ✅ **Ringan** — hanya JSON file, tanpa database berat, cocok untuk Termux/HP.

---

## 6. Pengembangan lanjutan (ide kalau mau upgrade nanti)

- Tambah `/summarize_pdf` untuk meringkas file PDF materi kuliah (pakai library `pypdf`).
- Integrasi Google Calendar biar jadwal otomatis sinkron.
- Voice note → transkrip otomatis (pakai Whisper API dari OpenAI).
- Mode grup, supaya bisa dipakai bareng teman satu kelas (hati-hati kuota API kalau ini diaktifkan).
- Ganti penyimpanan JSON ke SQLite kalau datanya makin banyak.

---

## 7. Troubleshooting umum

| Masalah | Solusi |
|---|---|
| `TELEGRAM_BOT_TOKEN belum diisi` | Cek isi file `.env`, pastikan tidak ada spasi ekstra |
| Bot tidak merespon sama sekali | Cek `OWNER_ID` sudah benar & sama dengan ID Telegram kamu |
| `⚠️ API key belum diisi...` | Isi API key provider tsb di `.env`, atau pakai `/model` ganti ke provider lain |
| Bot mati sendiri setelah beberapa jam | Set Termux ke "Unrestricted battery" di pengaturan Android (lihat bagian 3) |
| Error saat `pip install` | Jalankan `pkg install python-dev clang -y` dulu, baru `pip install -r requirements.txt` lagi |

Selamat mencoba, Hamid! Semoga bot ini bener-bener kepake selama kuliah di Polije 🚀
