from pyrogram import Client, filters, idle
from gtts import gTTS
import os
import random
from google import genai
import openai
import asyncio
import edge_tts
from pyrogram.types import Message
from pyrogram.raw.functions.channels import GetParticipants
from pyrogram.raw.types import ChannelParticipantsSearch
from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipant, ChannelParticipantAdmin, ChannelParticipantCreator
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
import cairosvg  # Required for `.tgs` to `.png`
import imageio  # Required for GIF handling
from datetime import datetime

# Environment Variables
API_ID = int(os.getenv("API_ID", 7249983))
API_HASH = os.getenv("API_HASH", "be8ea36c220d5e879c91ad9731686642")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7857026606:AAGsLVPXUgPzwNpAeVeo6Fnu7tXE_Nf-uu0")
GEMINI_API_KEY = "AIzaSyDCvXH3OHozEprR_g4k6RHaCyjqfTwKS-s"

# Initialize Pyrogram bot
client = genai.Client(api_key=GEMINI_API_KEY)
app = Client("Harami", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Accept all join requests
@app.on_message(filters.command("acceptall"))
async def accept_all_requests(client, message):
    chat_id = message.chat.id
    approved_count = 0
    try:
        join_requests = await client.get_chat_join_requests(chat_id)
        if not join_requests:
            await message.reply_text("❌ No pending join requests.")
            return
        for request in join_requests:
            await client.approve_chat_join_request(chat_id, request.from_user.id)
            approved_count += 1
        await message.reply_text(f"✅ Approved {approved_count} join requests!")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

# Love Calculator Command
@app.on_message(filters.command("love"))
async def love_calculator(client: Client, message: Message):
    LOVE_MESSAGES = [
        "💔 It's complicated!",
        "💛 You are great friends!",
        "💖 A beautiful bond is forming!",
        "💘 A strong connection!",
        "💞 True love is in the air!"
    ]
    chat_id = message.chat.id
    members = [member.user.id for member in await client.get_chat_members(chat_id)]
    if len(members) < 2:
        await message.reply_text("❌ Not enough users in the group to calculate love.")
        return
    user1_id, user2_id = random.sample(members, 2)
    user1 = await client.get_users(user1_id)
    user2 = await client.get_users(user2_id)
    love_score = random.randint(10, 100)
    love_message = LOVE_MESSAGES[min(love_score // 25, 4)]
    result = f"❤️ **Love Calculator** ❤️\n\n[{user1.first_name}](tg://user?id={user1.id}) + [{user2.first_name}](tg://user?id={user2.id}) "
    result += f"= **{love_score}% Love**\n\n**{love_message}**"
    sent_msg = await message.reply_text(result)
    await asyncio.sleep(5)
    await message.delete()

# AFK System
afk_users = {}
@app.on_message(filters.command("afk"))
async def set_afk(client: Client, message: Message):
    user_id = message.from_user.id
    reason = " ".join(message.command[1:]) if len(message.command) > 1 else "No reason provided"
    afk_users[user_id] = {"reason": reason, "time": datetime.now()}
    await message.reply_text(f"✅ You are now AFK!\n📜 Reason: {reason}")

@app.on_message(filters.private | filters.group)
async def remove_afk_on_message(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in afk_users:
        afk_info = afk_users.pop(user_id)
        afk_time = datetime.now() - afk_info["time"]
        await message.reply_text(f"✅ Welcome back! You were AFK for {afk_time.seconds} seconds.")
    if message.reply_to_message and message.reply_to_message.from_user.id in afk_users:
        afk_user_id = message.reply_to_message.from_user.id
        afk_info = afk_users[afk_user_id]
        afk_time = datetime.now() - afk_info["time"]
        await message.reply_text(f"🤖 {message.reply_to_message.from_user.first_name} is currently AFK!\n\n"
                                 f"🕒 Time Away: {afk_time.seconds} seconds\n📜 Reason: {afk_info['reason']}")

# Text to Speech Command
@app.on_message(filters.command("say"))
async def tts_handler(client, message):
    if len(message.command) < 2:
        await message.reply_text("❌ Usage: /say <text>")
        return
    text = " ".join(message.command[1:])
    file_path = "tts_voice.mp3"
    voice = "hi-IN-SwaraNeural"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(file_path)
    await message.reply_voice(voice=file_path, caption="🎤 Here is your voice message in an Indian female voice!")
    os.remove(file_path)

# Couple Command
@app.on_message(filters.command("couple"))
async def couple_command(client: Client, message: Message):
    chat_id = message.chat.id
    members = [member.user.id for member in await client.get_chat_members(chat_id)]
    if len(members) < 2:
        await message.reply_text("❌ Not enough users in the group.")
        return
    user1_id, user2_id = random.sample(members, 2)
    user1 = await client.get_users(user1_id)
    user2 = await client.get_users(user2_id)
    await message.reply_text(f"💑 Today's couple is: [{user1.first_name}](tg://user?id={user1.id}) ❤️ [{user2.first_name}](tg://user?id={user2.id})")

# Start Command
@app.on_message(filters.command("start"))
async def start_bot(_, message):
    await message.reply_text(f"Hi {message.from_user.mention}, how are you?")

async def main():
    await app.start()
    bot_ = await app.get_me()
    print(f"Bot started as @{bot_.username}!")
    await idle()
    await app.stop()
    print("Bot stopped!")
  

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
