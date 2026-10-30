
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ["BOT_TOKEN"]
GROUP_ID = os.environ["GROUP_ID"]
REGISTER_URL = "https://redirspinner.com/3fWS?p=%2Fregistration%2F"

WAITING_LINK = 1

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Envia-me o cartaz da aposta e depois o link dessa aposta."
    )


async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        return

    context.user_data["photo"] = update.message.photo[-1].file_id
    await update.message.reply_text("Cartaz recebido! Agora envia o link da aposta.")
    return WAITING_LINK


async def receive_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text.strip()

    if not link.startswith(("https://", "http://")):
        await update.message.reply_text("Envia um link válido, começado por https://")
        return WAITING_LINK

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎯 VER APOSTA", url=link)],
        [InlineKeyboardButton("📝 REGISTAR NA SPINBETTER", url=REGISTER_URL)]
    ])

    try:
        await context.bot.send_photo(
            chat_id=GROUP_ID,
            photo=context.user_data["photo"],
            reply_markup=keyboard
        )
        await update.message.reply_text("Publicado no grupo com sucesso!")
    except Exception:
        logger.exception("Erro ao publicar")
        await update.message.reply_text("Não consegui publicar. Verifica as permissões do bot.")

    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Publicação cancelada.")
    return ConversationHandler.END


def main():
    app = Application.builder().token(TOKEN).build()

    conversation = ConversationHandler(
        entry_points=[MessageHandler(filters.PHOTO, receive_photo)],
        states={
            WAITING_LINK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_link)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        conversation_timeout=600,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conversation)
    app.run_polling()


if __name__ == "__main__":
    main()
