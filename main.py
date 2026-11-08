import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from gtts import gTTS
from pydub import AudioSegment
from pydub.generators import Sine

TOKEN = os.environ.get("BOT_TOKEN")

def make_beat(duration_ms=15000):
    beat = AudioSegment.silent(duration=duration_ms)
    for i in range(0, duration_ms, 500):
        kick = Sine(60).to_audio_segment(duration=150).apply_gain(-10)
        beat = beat.overlay(kick, position=i)
        if i % 1000 == 0:
            hat = Sine(8000).to_audio_segment(duration=50).apply_gain(-25)
            beat = beat.overlay(hat, position=i+250)
    return beat

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎤 Bienvenue dans SongBot !\n\n"
        "Envoie : /song Je mange mon wrap fait maison à Lomé"
    )

async def song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Écris : /song ton texte ici")
        return
    texte = " ".join(context.args)
    await update.message.reply_text(f"🎵 Je crée ton son pour : '{texte}'... attends 10 sec...")
    try:
        tts = gTTS(text=texte, lang='fr', slow=False)
        tts.save("voix.mp3")
        voix = AudioSegment.from_mp3("voix.mp3")
        voix = voix.speedup(playback_speed=1.1)
        beat = make_beat(duration_ms=len(voix)+2000)
        beat = beat - 12
        final = beat.overlay(voix, position=1000)
        final.export("song_final.mp3", format="mp3")
        await update.message.reply_audio(
            audio=open("song_final.mp3", "rb"),
            caption=f"🎤 Ton son : {texte}"
        )
    except Exception as e:
        await update.message.reply_text(f"Erreur : {e}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("song", song))
print("Bot lancé...")
app.run_polling()
