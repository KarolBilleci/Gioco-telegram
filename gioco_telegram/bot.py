import html
import os
import re
import time
import asyncio
import threading
from urllib.parse import quote_plus
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)

print("--- AVVIO SCRIPT BOT.PY ---")

# Il token del bot
TOKEN = "8900259703:AAEejIefSjZRQJ1zSXzjXcpvM7MHra1JD1c"
CARTELLA = os.path.dirname(os.path.abspath(__file__))

# ===============================================================
# INTEGRAZIONE FLASK PER RENDER
# ===============================================================
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot ARG a Trapani è attivo e operativo!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)

# ===============================================================
# PARTE 1 - AUDIO (QR "audio1", "audio2", ...)
# ===============================================================
AUDIO = {
    1: ("tappa1.ogg", 41),
    2: ("tappa2.ogg", 37),
    3: ("tappa3.ogg", 36),
    4: ("tappa4.ogg", 36),
}

# ===============================================================
# PARTE 2 - I 9 PUNTI DELLA MISSIONE
# ===============================================================
PUNTI = [
    (
        "PUNTO 01 // Iniezione di Frequenza",
        "Via Garibaldi",
        "38.01813, 12.51334",
        [
            "⚠️ [ATTENZIONE: CANALE VULNERABILE]",
            "«Se state leggendo questo, la mia coscienza temporale si è frammentata. Hanno iniziato a sovrascrivere i miei ricordi sui ripetitori in Via Garibaldi... L'aria qui sa di ozono bruciato.»",
            "📍 <b>INDICAZIONE:</b> Muovetevi lungo <b>Via Garibaldi</b>. Agganciate il primo ripetitore alla base della struttura prima che la memoria svanisca.",
        ],
    ),
    (
        "PUNTO 02 // Il Labirinto di Pietra",
        "Salita S. Domenico",
        "38.017389, 12.511531",
        [
            "«Sento i vostri passi rimbombare dentro la mia testa... Le pietre di questa salita sono state mappate otticamente. Non guardate le finestre.»",
            "📍 <b>INDICAZIONE:</b> Infilatevi su <b>Salita S. Domenico</b>. Salite i gradini con circospezione e stringetevi contro i muri antichi.",
        ],
    ),
    (
        "PUNTO 03 // Eco Sintetico",
        "Chiesa Sant'Agostino (Fronte Tuttessenze)",
        "38.0147, 12.5100",
        [
            "«Continuano a mandarmi repliche digitali della mia voce che vi chiamano per nome. Non rispondete! Se vi voltate adesso, vedrete solo il riflesso del cielo che si spegne.»",
            "📍 <b>INDICAZIONE:</b> Raggiungete la zona della <b>Chiesa di Sant'Agostino</b>, proprio di fronte a Tuttessenze. Bonificate il settore al buio.",
        ],
    ),
    (
        "PUNTO 04 // Il Nodo Centrale",
        "Statua di Garibaldi",
        "38.01437, 12.50809",
        [
            "🚨 [ALLARME: OVERLOAD SENSORIALE]",
            "«I miei pensieri stanno colando nei vostri terminali! C'è un nodo di trasmissione impazzito che pulsa a ritmo con le vostre tempie.»",
            "📍 <b>INDICAZIONE:</b> Spostatevi verso la <b>Statua di Garibaldi</b>. Individuate la base del monumento e rinforzate il firewall umano.",
        ],
    ),
    (
        "PUNTO 05 // Corridoio di Corso Vittorio",
        "Corso Vittorio Emanuele",
        "38.015829, 12.507024",
        [
            "«I palazzi alti qui dentro stringono il segnale... La rete sta tentando di formattarvi la memoria lungo la strada.»",
            "📍 <b>INDICAZIONE:</b> Imboccate <b>Corso Vittorio Emanuele</b>. Percorrete il rettilineo tenendovi radenti ai muri e alle vetrine dei negozi.",
        ],
    ),
    (
        "PUNTO 06 // Sfiato di Maestrale",
        "Mura di Tramontana (Vicino Bastione)",
        "38.01574, 12.55788",
        [
            "⚠️ [ATTENZIONE: RILEVATA ENTITÀ OSTILE]",
            "«Hanno staccato la corrente alla realtà in questo settore a picco sul mare. C'è un vuoto di tre secondi tra un battito di ciglia e l'altro... Nascondetevi!»",
            "📍 <b>INDICAZIONE:</b> Salite verso le <b>Mura di Tramontana</b>, nei pressi del Bastione. Camminate lungo la ringhiera e cercate riparo.",
        ],
    ),
    (
        "PUNTO 07 // Il Porto Fantasma",
        "Pescheria vicino al Lazzaretto",
        "38.016088, 12.499428",
        [
            "«Le barche ormeggiate qui non galleggiano sull'acqua, ma su stringhe di codice binario stagnante. Hanno svuotato la zona per far posto ai server.»",
            "📍 <b>INDICAZIONE:</b> Scendete verso la zona della <b>Pescheria vicino al Lazzaretto</b>. Costeggiate la banchina tenendovi vicini alle barche.",
        ],
    ),
    (
        "PUNTO 08 // Il Confine del Mondo",
        "Via Torre di Ligny (Avvicinamento)",
        "38.019625, 12.496938",
        [
            "🔴 [PERIMETRO LIMITROFO // COLLASSO IMMINENTE]",
            "«La terra finisce qui, ma la rete continua sotto il mare. Sento i cavi sottomarini che vibrano tra i denti.»",
            "📍 <b>INDICAZIONE:</b> Imboccate l'ultima lingua d'asfalto in direzione della torre. La strada è stretta tra le onde: non potete sbagliare.",
        ],
    ),
    (
        "PUNTO 09 // Estrazione Totale",
        "Torre di Ligny (Punta Estrema)",
        None,
        [
            "⚡ [SINCRONIZZAZIONE COMPLETATA AL 100%]",
            "«Avete pulito i settori. Avete tenuto aperta la frequenza fino all'ultimo respiro... La realtà torna a respirare.»",
            "📍 <b>INDICAZIONE:</b> Siete arrivati in fondo alla punta estrema di <b>Torre di Ligny</b>. È la fine del percorso a piedi: recuperate l'oggetto nascosto e preparatevi alla fuga in moto.",
        ],
    ),
]

COORD_RE = re.compile(r"-?\d+(\.\d+)?\s*,\s*-?\d+(\.\d+)?")


def testo_punto(indice):
    titolo, luogo, mappa, righe = PUNTI[indice]
    corpo = "\n".join(r for r in righe)
    testo = (
        f"<b>📍 {html.escape(titolo)}</b>\n"
        f"🧭 <b>Destinazione:</b> {html.escape(luogo)}\n"
    )
    if mappa and COORD_RE.fullmatch(mappa.strip()):
        testo += f"📌 <b>Coordinate:</b> <code>{html.escape(mappa.strip())}</code>\n"
    return testo + f"\n{corpo}"


def genera_tastiera(indice):
    bottoni = []
    mappa = PUNTI[indice][2]
    if mappa:
        mappa = mappa.strip()
        if COORD_RE.fullmatch(mappa):
            mappa = mappa.replace(" ", "")
        url = (
            "https://www.google.com/maps/dir/?api=1"
            f"&destination={quote_plus(mappa, safe=',')}&travelmode=walking"
        )
        bottoni.append([InlineKeyboardButton("🧭 Portami lì (mappa)", url=url)])

    if indice < len(PUNTI) - 1:
        bottoni.append([InlineKeyboardButton("🔓 Abbiamo fatto, procedi oltre", callback_data=f"next_{indice + 1}")])

    return InlineKeyboardMarkup(bottoni) if bottoni else None


async def invia_punto(bot, chat_id, indice):
    await bot.send_message(
        chat_id,
        testo_punto(indice),
        parse_mode=ParseMode.HTML,
        reply_markup=genera_tastiera(indice),
    )


# ---------------- GESTIONE INTERATTIVA, MANOVRA EVASIVA E INTRUSIONE ----------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "safe_8":
        msg_attesa = await query.message.reply_text(
            "🔄 <i>Verifica frequenze radio e bonifica area in corso...</i>", 
            parse_mode=ParseMode.HTML
        )
        await asyncio.sleep(5)
        await msg_attesa.delete()
        
        await query.message.reply_text(
            "<i>«Ok... sembra che se ne siano andati. La via a piedi è libera verso Cala Venezia, ma... un momento. Il terminale sta ricevendo un flusso di dati anomalo...»</i>",
            parse_mode=ParseMode.HTML
        )
        await asyncio.sleep(4)

        url_intruso = "https://t.me/SoggettoIntrusoBot?start=intercettazione"
        tastiera_intruso = InlineKeyboardMarkup([
            [InlineKeyboardButton("⚠️ CANALE INTERCETTATO - ISPEZIONA", url=url_intruso)]
        ])

        await query.message.reply_text(
            "🔴 <b>[ALLARME: SEGNALE DIROTTATO]</b>\n\n"
            "<code>[ERRORE 0x889 - FREQUENZA COMPROMESSA]</code>\n"
            "<i>Il protocollo Valenti è stato bloccato da una sorgente esterna. Cliccate sul pulsante sotto per analizzare l'intrusione.</i>",
            parse_mode=ParseMode.HTML,
            reply_markup=tastiera_intruso
        )
        return

    if data.startswith("next_"):
        indice = int(data.split("_")[1])
        
        resta = context.chat_data.get("audio_fino", 0) - time.time()
        if resta > 0:
            await query.message.reply_text("⚠️ Interferenza radio in corso! Aspetta la fine dell'audio.")
            return

        msg_attesa = await query.message.reply_text("🔄 <i>Decifrazione coordinate in corso... Sincronizzazione frequenza...</i>", parse_mode=ParseMode.HTML)
        await asyncio.sleep(10)
        await msg_attesa.delete()

        if indice == 7: 
            await query.message.reply_text(
                "🚨 <b>ATTENZIONE: UNITÀ OSTILE IN AVVICINAMENTO</b> 🚨\n\n"
                "<code>[ALLARME PROSSIMITÀ: TRACCIAMENTO ATTIVO]</code>\n"
                "<i>«Non muovetevi! Vi stanno passando accanto. Spegnete la torcia del telefono!»</i>",
                parse_mode=ParseMode.HTML
            )
            await asyncio.sleep(4)
            
            percorso_foto = os.path.join(CARTELLA, "minaccia.jpg")
            if os.path.exists(percorso_foto):
                with open(percorso_foto, "rb") as foto_file:
                    await context.bot.send_photo(
                        query.message.chat_id,
                        photo=foto_file,
                        caption="🔴 <b>NON GIRATEVI. Lasciateli sfilare lungo il muro opposto.</b>",
                        parse_mode=ParseMode.HTML
                    )
            await asyncio.sleep(3)

            tastiera_fuga = InlineKeyboardMarkup([
                [InlineKeyboardButton("🛡️ La costa è pulita, conferma la sicurezza", callback_data="safe_8")]
            ])
            
            await query.message.reply_text(
                "🏃‍♂️ <b>MANOVRA EVASIVA IN CORSO:</b>\n\n"
                "<i>Intrufolatevi nel vicolo cieco sulla destra, premete le spalle contro la pietra e attendete trenta secondi in silenzio.</i>\n\n"
                "Appena il pericolo si è allontanato, confermate la vostra posizione qui sotto.",
                parse_mode=ParseMode.HTML,
                reply_markup=tastiera_fuga
            )
            return 

        await invia_punto(context.bot, query.message.chat_id, indice)


# ---------------- AUDIO ----------------
async def manda_audio(update: Update, context: ContextTypes.DEFAULT_TYPE, n: int):
    chat_id = update.effective_chat.id
    voce = AUDIO.get(n)
    percorso = os.path.join(CARTELLA, "audio", voce[0]) if voce else None
    if not percorso or not os.path.exists(percorso):
        await update.message.reply_text("Codice non riconosciuto.")
        return
    with open(percorso, "rb") as f:
        await context.bot.send_voice(chat_id, voice=f)
    context.chat_data["audio_fino"] = time.time() + voce[1] + 2


# ---------------- COMANDI PRINCIPALI ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if context.args:
        codice = context.args[0]
        if codice.isdigit():
            punto_indice = int(codice)
            if 0 <= punto_indice < len(PUNTI):
                context.chat_data["punto_attuale"] = punto_indice
                await context.bot.send_message(
                    chat_id, 
                    "⚡ <i>Riconnessione al canale di Valenti stabilita. Ripresa protocollo in corso...</i>", 
                    parse_mode=ParseMode.HTML
                )
                await asyncio.sleep(2)
                await invia_punto(context.bot, chat_id, punto_indice)
                return
        elif codice.startswith("audio") and codice[5:].isdigit():
            numero_audio = int(codice[5:])
            await manda_audio(update, context, numero_audio)
            punto_indice = numero_audio - 1
            if 0 <= punto_indice < len(PUNTI):
                context.chat_data["punto_attuale"] = punto_indice
                await context.bot.send_message(
                    chat_id, 
                    "⚡ <i>Riconnessione al canale di Valenti stabilita. Ripresa protocollo in corso...</i>", 
                    parse_mode=ParseMode.HTML
                )
                await asyncio.sleep(2)
                await invia_punto(context.bot, chat_id, punto_indice)
            return

    testo_intro = (
        "🔴 <b>[CANALE DI EMERGENZA ATTIVATO]</b>\n\n"
        "<i>«Hanno preso Valenti. Il segnale si sta disperdendo nei vicoli... "
        "Se leggete questo messaggio, siete l'unica speranza per recuperare i file prima che il blocco diventi permanente.»</i>\n\n"
        "📍 <b>OBIETTIVO PRELIMINARE:</b>\n"
        "Raggiungete la <b>Statua di Garibaldi</b> in centro a Trapani. "
        "Lì troverete il primo marcatore nascosto: scannerizzate il QR code per sbloccare il protocollo e iniziare la ricerca dell'investigatore."
    )
    await context.bot.send_message(chat_id, testo_intro, parse_mode=ParseMode.HTML)


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data.pop("audio_fino", None)
    context.chat_data.pop("punto_attuale", None)
    await update.message.reply_text("Missione azzerata. Usa /start per ricominciare.")


async def punto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args and context.args[0].isdigit() and 1 <= int(context.args[0]) <= len(PUNTI):
        await invia_punto(context.bot, update.effective_chat.id, int(context.args[0]) - 1)
    else:
        await update.message.reply_text(f"Scrivi /punto seguito da un numero da 1 a {len(PUNTI)}.")


def main():
    # Avvia Flask in un thread in background per la porta web di Render
    threading.Thread(target=run_flask, daemon=True).start()

    # Avvia il bot Telegram nel thread principale
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("punto", punto))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("Bot Telegram attivo tramite polling.")
    app.run_polling()


if __name__ == "__main__":
    main()
