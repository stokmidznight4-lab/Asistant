import datetime
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

import handlers
from config import TELEGRAM_BOT_TOKEN

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    if not TELEGRAM_BOT_TOKEN:
        raise SystemExit(
            "TELEGRAM_BOT_TOKEN belum diisi di file .env! "
            "Buat bot lewat @BotFather dulu, lalu isi tokennya di .env"
        )

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Perintah dasar
    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CommandHandler("help", handlers.help_cmd))
    app.add_handler(CommandHandler("model", handlers.model_cmd))
    app.add_handler(CommandHandler("clear", handlers.clear_cmd))
    app.add_handler(CallbackQueryHandler(handlers.model_callback, pattern="^setmodel:"))

    # Bantuan belajar
    app.add_handler(CommandHandler("ringkas", handlers.ringkas_cmd))
    app.add_handler(CommandHandler("jelaskan", handlers.jelaskan_cmd))
    app.add_handler(CommandHandler("soal", handlers.soal_cmd))
    app.add_handler(CommandHandler("translate", handlers.translate_cmd))

    # Jadwal
    app.add_handler(CommandHandler("jadwal_tambah", handlers.jadwal_tambah_cmd))
    app.add_handler(CommandHandler("jadwal_lihat", handlers.jadwal_lihat_cmd))
    app.add_handler(CommandHandler("jadwal_hapus", handlers.jadwal_hapus_cmd))

    # Tugas
    app.add_handler(CommandHandler("tugas_tambah", handlers.tugas_tambah_cmd))
    app.add_handler(CommandHandler("tugas_lihat", handlers.tugas_lihat_cmd))
    app.add_handler(CommandHandler("tugas_selesai", handlers.tugas_selesai_cmd))

    # Catatan
    app.add_handler(CommandHandler("catatan_tambah", handlers.catatan_tambah_cmd))
    app.add_handler(CommandHandler("catatan_lihat", handlers.catatan_lihat_cmd))

    # Pesan biasa (teks & foto) -> chat dengan AI
    app.add_handler(MessageHandler(filters.PHOTO, handlers.photo_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.text_message))

    # Reminder tugas otomatis tiap jam 7 pagi
    if app.job_queue:
        app.job_queue.run_daily(
            handlers.daily_reminder,
            time=datetime.time(hour=7, minute=0),
        )

    logger.info("Bot mulai berjalan... Tekan CTRL+C untuk berhenti.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
