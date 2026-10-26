import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN_INTRUSO = os.environ.get("BOT_TOKEN_INTRUSO", "8840678686:AAG5ovl312PXd9T3H4APBrYtYqBbot6yP2o")
CARTELLA = os.path.dirname(os.path.abspath(__file__))

async def start_intruso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    url_netlify = "https://luxury-babka-5f8bbe.netlify.app/"
    
    # Sostituisci "NOME_DEL_TUO_FIRST_BOT" con l'username esatto del tuo primo bot (quello principale di Valenti)
    url_ritorno = "https://t.me/InvestigatorAssistant_Bot?start=7"  # 7 corrisponde all'indice del Punto 08 (Cala Venezia)
    
    tastiera_miniapp = InlineKeyboardMarkup([
        [InlineKeyboardButton("📡 VERIFICA POSIZIONE TARGET", web_app=WebAppInfo(url=url_netlify))],
        [InlineKeyboardButton("🚨 FORZA IL BLOCCO E RIPRENDI LA FUGA", url=url_ritorno)]
    ])

    # Messaggio di minaccia e aggancio immediato della posizione
    testo_intruso = (
        "🔴 <b>[TERMINALE DI CONTROLLO N.4]</b>\n\n"
        "<i>Abbiamo tracciato il vostro dispositivo nei vicoli. State seguendo un soggetto non autorizzato (Valenti) in una zona interdetta.</i>\n\n"
        "<code>[PROTOCOLLO DI TRACCIAMENTO ATTIVO]</code>\n"
        "Il sistema richiede l'estrazione delle coordinate GPS in tempo reale del dispositivo per confermare il perimetro."
    )
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=testo_intruso,
        parse_mode=ParseMode.HTML,
        reply_markup=tastiera_miniapp
    )
    
    # Invia anche la foto della sorveglianza (se presente nella cartella)
    percorso_foto = os.path.join(CARTELLA, "sorveglianza.jpg")
    if os.path.exists(percorso_foto):
        with open(percorso_foto, "rb") as foto_file:
            await context.bot.send_photo(
                chat_id,
                photo=foto_file,
                caption="⚠️ <b>TARGET AGGANCIATI DAL SISTEMA DI SORVEGLIANZA.</b>",
                parse_mode=ParseMode.HTML
            )

async def ricevi_prove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Manteniamo il comando manuale come backup
    await start_intruso(update, context)

def main():
    app = Application.builder().token(TOKEN_INTRUSO).build()
    app.add_handler(CommandHandler("start", start_intruso))
    app.add_handler(CommandHandler("ricevi_prove", ricevi_prove))
    
    print("Bot Intruso (@SoggettoIntrusoBot) attivo.")
    app.run_polling()

if __name__ == "__main__":
    main()