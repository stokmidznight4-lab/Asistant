import asyncio
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import storage
import ai_providers
from config import OWNER_ID, DEFAULT_MODEL, MODEL_LABELS

SYSTEM_PROMPT = (
    "Kamu adalah asisten AI pribadi untuk mahasiswa Politeknik Negeri Jember jurusan "
    "Informatika bernama Abdul Hamid Maulana (Hamid). Jawab dengan bahasa Indonesia yang "
    "jelas, ringkas, dan ramah, kecuali diminta bahasa lain. Kalau menjelaskan materi kuliah, "
    "beri contoh konkret dan mudah dipahami mahasiswa baru."
)


# ---------------- GUARD: hanya owner yang boleh pakai ----------------
def is_owner(update: Update) -> bool:
    if not OWNER_ID:
        return True  # kalau OWNER_ID tidak diisi, bot terbuka untuk siapa saja (tidak disarankan)
    return str(update.effective_user.id) == str(OWNER_ID)


async def guard(update: Update) -> bool:
    if not is_owner(update):
        await update.message.reply_text("Maaf, bot ini bersifat privat. 🔒")
        return False
    return True


# ---------------- HELPER: panggil AI dengan history ----------------
async def chat_with_ai(user_id, provider, user_text, image_bytes=None):
    history = storage.get_history(user_id)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history + [
        {"role": "user", "content": user_text}
    ]
    reply = await asyncio.to_thread(ai_providers.ask_ai, provider, messages, image_bytes)
    storage.add_to_history(user_id, "user", user_text)
    storage.add_to_history(user_id, "assistant", reply)
    return reply


def split_long_message(text, limit=4000):
    return [text[i:i + limit] for i in range(0, len(text), limit)] or [""]


# ---------------- /start & /help ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    nama = update.effective_user.first_name or "Hamid"
    await update.message.reply_text(
        f"Halo {nama}! 👋 Aku bot AI kuliahmu.\n\n"
        "Ketik langsung pesan apapun untuk ngobrol dengan AI, atau pakai /help untuk lihat semua fitur."
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    text = (
        "*📚 Menu Bot Kuliah*\n\n"
        "*Ngobrol dengan AI*\n"
        "Ketik pesan apa saja langsung → dijawab AI yang sedang aktif.\n"
        "Kirim *foto soal/materi* (boleh dikasih caption) → AI akan menganalisis gambarnya.\n"
        "/model — ganti AI aktif (Gemini/OpenAI/Grok/DeepSeek/Kimi)\n"
        "/clear — hapus riwayat percakapan (mulai topik baru)\n\n"
        "*Bantuan Belajar*\n"
        "/ringkas <teks> — ringkas materi panjang\n"
        "/jelaskan <topik> — jelaskan konsep dengan mudah\n"
        "/soal <topik> — buatkan soal latihan + kunci jawaban\n"
        "/translate <bahasa>|<teks> — terjemahkan teks\n\n"
        "*Manajemen Kuliah*\n"
        "/jadwal_tambah <hari>|<jam>|<matkul>\n"
        "/jadwal_lihat — lihat jadwal kuliah\n"
        "/jadwal_hapus — hapus semua jadwal\n\n"
        "/tugas_tambah <judul>|<deadline>\n"
        "/tugas_lihat — lihat daftar tugas\n"
        "/tugas_selesai <nomor> — tandai tugas selesai\n\n"
        "/catatan_tambah <judul>|<isi>\n"
        "/catatan_lihat — lihat semua catatan tersimpan\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


# ---------------- /model ----------------
async def model_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    buttons = [
        [InlineKeyboardButton(label, callback_data=f"setmodel:{key}")]
        for key, label in MODEL_LABELS.items()
    ]
    current = storage.get_active_model(update.effective_user.id, DEFAULT_MODEL)
    await update.message.reply_text(
        f"AI aktif saat ini: *{MODEL_LABELS.get(current, current)}*\n\nPilih AI yang ingin dipakai:",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown",
    )


async def model_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    provider = query.data.split(":", 1)[1]
    storage.set_active_model(query.from_user.id, provider)
    await query.edit_message_text(f"✅ AI aktif diganti ke: {MODEL_LABELS.get(provider, provider)}")


# ---------------- /clear ----------------
async def clear_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    storage.clear_history(update.effective_user.id)
    await update.message.reply_text("🧹 Riwayat percakapan dibersihkan. Mulai topik baru!")


# ---------------- Pesan teks biasa -> chat ----------------
async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    user_id = update.effective_user.id
    provider = storage.get_active_model(user_id, DEFAULT_MODEL)
    await update.message.chat.send_action("typing")
    try:
        reply = await chat_with_ai(user_id, provider, update.message.text)
    except ai_providers.AIError as e:
        await update.message.reply_text(f"⚠️ {e}")
        return
    for chunk in split_long_message(reply):
        await update.message.reply_text(chunk)


# ---------------- Foto -> analisis dengan AI vision ----------------
async def photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    user_id = update.effective_user.id
    provider = storage.get_active_model(user_id, DEFAULT_MODEL)
    caption = update.message.caption or "Tolong jelaskan/bahas isi gambar ini untuk membantu belajarku."

    await update.message.chat.send_action("typing")
    photo_file = await update.message.photo[-1].get_file()
    image_bytes = bytes(await photo_file.download_as_bytearray())

    try:
        reply = await chat_with_ai(user_id, provider, caption, image_bytes=image_bytes)
    except ai_providers.AIError as e:
        await update.message.reply_text(
            f"⚠️ {e}\n\n(Catatan: tidak semua model mendukung gambar dengan baik. "
            f"Coba ganti ke Gemini atau OpenAI lewat /model)"
        )
        return
    for chunk in split_long_message(reply):
        await update.message.reply_text(chunk)


# ---------------- /ringkas ----------------
async def ringkas_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    teks = " ".join(context.args) if context.args else None
    if update.message.reply_to_message and update.message.reply_to_message.text:
        teks = update.message.reply_to_message.text
    if not teks:
        await update.message.reply_text("Gunakan: /ringkas <teks panjang>\natau reply pesan berisi teks lalu ketik /ringkas")
        return

    provider = storage.get_active_model(update.effective_user.id, DEFAULT_MODEL)
    prompt = f"Ringkas teks berikut menjadi poin-poin penting yang mudah dipahami untuk belajar:\n\n{teks}"
    await update.message.chat.send_action("typing")
    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}]
        reply = await asyncio.to_thread(ai_providers.ask_ai, provider, messages)
    except ai_providers.AIError as e:
        await update.message.reply_text(f"⚠️ {e}")
        return
    for chunk in split_long_message(reply):
        await update.message.reply_text(chunk)


# ---------------- /jelaskan ----------------
async def jelaskan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    if not context.args:
        await update.message.reply_text("Gunakan: /jelaskan <topik>\nContoh: /jelaskan rekursi dalam pemrograman")
        return
    topik = " ".join(context.args)
    provider = storage.get_active_model(update.effective_user.id, DEFAULT_MODEL)
    prompt = f"Jelaskan konsep '{topik}' untuk mahasiswa baru jurusan Informatika, pakai bahasa sederhana dan contoh nyata/kode singkat kalau relevan."
    await update.message.chat.send_action("typing")
    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}]
        reply = await asyncio.to_thread(ai_providers.ask_ai, provider, messages)
    except ai_providers.AIError as e:
        await update.message.reply_text(f"⚠️ {e}")
        return
    for chunk in split_long_message(reply):
        await update.message.reply_text(chunk)


# ---------------- /soal ----------------
async def soal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    if not context.args:
        await update.message.reply_text("Gunakan: /soal <topik>\nContoh: /soal struktur data linked list")
        return
    topik = " ".join(context.args)
    provider = storage.get_active_model(update.effective_user.id, DEFAULT_MODEL)
    prompt = (
        f"Buatkan 5 soal latihan (campuran pilihan ganda dan essay singkat) tentang '{topik}' "
        f"untuk mahasiswa Informatika, lengkap dengan kunci jawaban dan penjelasan singkat di akhir."
    )
    await update.message.chat.send_action("typing")
    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}]
        reply = await asyncio.to_thread(ai_providers.ask_ai, provider, messages)
    except ai_providers.AIError as e:
        await update.message.reply_text(f"⚠️ {e}")
        return
    for chunk in split_long_message(reply):
        await update.message.reply_text(chunk)


# ---------------- /translate ----------------
async def translate_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    raw = " ".join(context.args)
    if "|" not in raw:
        await update.message.reply_text("Gunakan: /translate <bahasa tujuan>|<teks>\nContoh: /translate inggris|Saya sedang mengerjakan tugas")
        return
    bahasa, teks = raw.split("|", 1)
    provider = storage.get_active_model(update.effective_user.id, DEFAULT_MODEL)
    prompt = f"Terjemahkan teks berikut ke bahasa {bahasa.strip()}, tanpa penjelasan tambahan:\n\n{teks.strip()}"
    await update.message.chat.send_action("typing")
    try:
        messages = [{"role": "user", "content": prompt}]
        reply = await asyncio.to_thread(ai_providers.ask_ai, provider, messages)
    except ai_providers.AIError as e:
        await update.message.reply_text(f"⚠️ {e}")
        return
    await update.message.reply_text(reply)


# ---------------- JADWAL ----------------
async def jadwal_tambah_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    raw = " ".join(context.args)
    parts = raw.split("|")
    if len(parts) != 3:
        await update.message.reply_text("Gunakan: /jadwal_tambah <hari>|<jam>|<mata kuliah>\nContoh: /jadwal_tambah Senin|08:00|Algoritma Pemrograman")
        return
    hari, jam, matkul = [p.strip() for p in parts]
    storage.add_jadwal(update.effective_user.id, hari, jam, matkul)
    await update.message.reply_text(f"✅ Jadwal ditambahkan: {hari}, {jam} - {matkul}")


async def jadwal_lihat_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    jadwal = storage.get_jadwal(update.effective_user.id)
    if not jadwal:
        await update.message.reply_text("Belum ada jadwal tersimpan. Tambahkan dengan /jadwal_tambah")
        return
    urutan_hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    jadwal_sorted = sorted(jadwal, key=lambda x: (urutan_hari.index(x["hari"]) if x["hari"] in urutan_hari else 99, x["jam"]))
    text = "*🗓 Jadwal Kuliahmu*\n\n"
    for j in jadwal_sorted:
        text += f"• {j['hari']}, {j['jam']} — {j['matkul']}\n"
    await update.message.reply_text(text, parse_mode="Markdown")


async def jadwal_hapus_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    storage.clear_jadwal(update.effective_user.id)
    await update.message.reply_text("🗑 Semua jadwal dihapus.")


# ---------------- TUGAS ----------------
async def tugas_tambah_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    raw = " ".join(context.args)
    parts = raw.split("|")
    if len(parts) != 2:
        await update.message.reply_text("Gunakan: /tugas_tambah <judul>|<deadline>\nContoh: /tugas_tambah Laporan Praktikum Basis Data|10 Juli 2026")
        return
    judul, deadline = [p.strip() for p in parts]
    storage.add_tugas(update.effective_user.id, judul, deadline)
    await update.message.reply_text(f"✅ Tugas ditambahkan: {judul} (deadline: {deadline})")


async def tugas_lihat_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    tugas = storage.get_tugas(update.effective_user.id)
    if not tugas:
        await update.message.reply_text("Tidak ada tugas yang belum selesai. 🎉")
        return
    text = "*📝 Daftar Tugas Belum Selesai*\n\n"
    for i, t in enumerate(tugas, 1):
        text += f"{i}. {t['judul']} — _deadline: {t['deadline']}_\n"
    text += "\nTandai selesai dengan: /tugas_selesai <nomor>"
    await update.message.reply_text(text, parse_mode="Markdown")


async def tugas_selesai_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Gunakan: /tugas_selesai <nomor>\nLihat nomornya lewat /tugas_lihat")
        return
    idx = int(context.args[0]) - 1
    ok = storage.selesaikan_tugas(update.effective_user.id, idx)
    if ok:
        await update.message.reply_text("✅ Tugas ditandai selesai!")
    else:
        await update.message.reply_text("Nomor tugas tidak ditemukan.")


# ---------------- CATATAN ----------------
async def catatan_tambah_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    raw = " ".join(context.args)
    parts = raw.split("|", 1)
    if len(parts) != 2:
        await update.message.reply_text("Gunakan: /catatan_tambah <judul>|<isi catatan>")
        return
    judul, isi = parts[0].strip(), parts[1].strip()
    storage.add_catatan(update.effective_user.id, judul, isi)
    await update.message.reply_text(f"✅ Catatan '{judul}' disimpan.")


async def catatan_lihat_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    catatan = storage.get_catatan(update.effective_user.id)
    if not catatan:
        await update.message.reply_text("Belum ada catatan tersimpan.")
        return
    text = "*🗒 Catatanmu*\n\n"
    for c in catatan:
        text += f"*{c['judul']}*\n{c['isi']}\n\n"
    for chunk in split_long_message(text):
        await update.message.reply_text(chunk, parse_mode="Markdown")


# ---------------- Reminder harian otomatis (tugas mendekati deadline) ----------------
async def daily_reminder(context: ContextTypes.DEFAULT_TYPE):
    if not OWNER_ID:
        return
    tugas = storage.get_tugas(OWNER_ID)
    if not tugas:
        return
    text = "⏰ *Pengingat Tugas Harian*\n\n" + "\n".join(
        f"• {t['judul']} — deadline: {t['deadline']}" for t in tugas
    )
    await context.bot.send_message(chat_id=OWNER_ID, text=text, parse_mode="Markdown")
