import asyncio
import os
import random
import requests
from pyrogram import Client, filters
from tgvc import VoiceChat
from vimeo import VimeoClient

# Telegram API details
API_ID = 123456  # Ganti dengan API ID Anda
API_HASH = "your_api_hash"  # Ganti dengan API Hash Anda
BOT_TOKEN = "your_bot_token"  # Ganti dengan Bot Token Anda

# Vimeo API setup
VIMEO_CLIENT = VimeoClient(
    token="c2a397ae65dc9e959330e35a59710d19",
    key="e0bcf600712416124ed5a79886b9b1a036dea31c",
    secret="3CbaqJGca7v78sG1+apB+iMO5SSiD+rZs4nCTO5sAGPJVL4o4vdJ1aObUZaSeslu3pt22/ruKle1KEDIPPy/NJ8hCH0zK7RZOwfHha6XQtFRV4IfyPoDbZN3LecId6/n"
)

# API for music
DEEZER_API_URL = "https://api.deezer.com/search"

# Initialize bot and voice chat
app = Client("mvhiro_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
vc = VoiceChat(app)


# Helper functions
async def fetch_music(query):
    """Fetch music using Deezer API."""
    try:
        response = requests.get(DEEZER_API_URL, params={"q": query})
        if response.status_code == 200:
            data = response.json()
            if data["data"]:
                return data["data"][0]["preview"]  # Preview URL
    except Exception as e:
        print(f"Error fetching music: {e}")
    return None


async def fetch_video(query):
    """Fetch video using Vimeo API."""
    try:
        response = VIMEO_CLIENT.get("/videos", params={"query": query, "per_page": 1})
        if response.status_code == 200 and response.json().get("data"):
            return response.json()["data"][0]["link"]
    except Exception as e:
        print(f"Error fetching video from Vimeo: {e}")
    return None


async def mention_members(chat_id, duration=300):
    """Mention 5 random members in a group repeatedly for a specified duration."""
    end_time = asyncio.get_event_loop().time() + duration
    while asyncio.get_event_loop().time() < end_time:
        members = [m.user for m in await app.get_chat_members(chat_id)]
        random_members = random.sample(members, min(5, len(members)))
        mentions = " ".join([f"@{m.username}" for m in random_members if m.username])
        await app.send_message(chat_id, mentions)
        await asyncio.sleep(10)


# Command handlers
@app.on_message(filters.command("start"))
async def start(_, message):
    await message.reply("Hai, saya adalah bot entertain, silahkan tambahkan saya di group kamu, untuk informasi hubungi @hiro_v1")

@app.on_message(filters.command("help"))
async def help_command(_, message):
    help_text = (
        "Perintah yang tersedia:\n"
        "1. /play [judul music/link] - Memainkan musik.\n"
        "2. /vplay [judul video/link] - Memainkan video.\n"
        "3. /stop - Menghentikan pemutaran.\n"
        "4. /start - Informasi bot.\n"
        "5. /help - Bantuan penggunaan bot.\n"
        "6. /admin - Informasi pembuat bot.\n"
        "7. /all - Mention 5 anggota grup secara acak."
    )
    await message.reply(help_text)


@app.on_message(filters.command("admin"))
async def admin(_, message):
    await message.reply("Bot ini dibuat oleh @hiro_v1")


@app.on_message(filters.command("play"))
async def play(_, message):
    query = " ".join(message.command[1:])
    if not query:
        await message.reply("Harap masukkan judul musik atau link.")
        return
    url = await fetch_music(query)
    if url:
        await vc.join(message.chat.id)
        await vc.play(url)
        await message.reply(f"Memainkan musik: {query}")
    else:
        await message.reply("Musik tidak ditemukan.")


@app.on_message(filters.command("vplay"))
async def vplay(_, message):
    query = " ".join(message.command[1:])
    if not query:
        await message.reply("Harap masukkan judul video atau link.")
        return
    url = await fetch_video(query)
    if url:
        await vc.join(message.chat.id)
        await vc.play(url)
        await message.reply(f"Memainkan video: {query}")
    else:
        await message.reply("Video tidak ditemukan.")


@app.on_message(filters.command("stop"))
async def stop(_, message):
    await vc.stop()
    await vc.leave(message.chat.id)
    await message.reply("Pemutaran dihentikan.")


@app.on_message(filters.command("all"))
async def all(_, message):
    chat_id = message.chat.id
    await message.reply("Mention dimulai. Untuk menghentikan, gunakan perintah /stop.")
    asyncio.create_task(mention_members(chat_id))


# Run the bot
if __name__ == "__main__":
    app.run()
