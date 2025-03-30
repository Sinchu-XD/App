from pyrogram import Client, filters, idle
from gtts import gTTS
import os
import random
from google import genai
import openai
import asyncio
import edge_tts
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.raw.functions.channels import GetParticipants
from pyrogram.raw.types import ChannelParticipantsSearch
from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import (
    ChannelParticipantsSearch,
    ChannelParticipant,
    ChannelParticipantAdmin,
    ChannelParticipantCreator,
    MessageEntityMentionName
)
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
import cairosvg  # ✅ Required for `.tgs` to `.png`
import imageio  # ✅ Required for GIF handling
from datetime import datetime

# Replace with your API details
API_ID = int(os.getenv("API_ID", 7249983))
API_HASH = os.getenv("API_HASH", "be8ea36c220d5e879c91ad9731686642")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7857026606:AAGsLVPXUgPzwNpAeVeo6Fnu7tXE_Nf-uu0")
GEMINI_API_KEY = "AIzaSyDCvXH3OHozEprR_g4k6RHaCyjqfTwKS-s"

# Initialize Pyrogram bot
client = genai.Client(api_key=GEMINI_API_KEY)

app = Client("Harami", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest



@app.on_message(filters.command("acceptall") & filters.chat("your_channel_or_group_username"))
def accept_all_requests(client, message):
    chat_id = message.chat.id
    approved_count = 0
    
    try:
        for request in client.get_chat_join_requests(chat_id):
            client.approve_chat_join_request(chat_id, request.from_user.id)
            approved_count += 1
    except Exception as e:
        message.reply_text(f"Error: {str(e)}")
        return
    
    message.reply_text(f"Approved {approved_count} join requests!")



LOVE_MESSAGES = [
    "💔 It's complicated!",
    "💛 You are great friends!",
    "💖 A beautiful bond is forming!",
    "💘 A strong connection!",
    "💞 True love is in the air!"
]

@app.on_message(filters.command("love"))
async def love_calculator(client: Client, message: Message):
    chat_id = message.chat.id
    users = []

    # Check if users were mentioned
    if message.entities:
        for entity in message.entities:
            if entity.user:
                users.append(entity.user)

    # If two users are mentioned, use them
    if len(users) == 2:
        user1, user2 = users
    else:
        # Fetch group participants
        participants = await client.invoke(
            GetParticipants(channel=chat_id, filter=ChannelParticipantsSearch(""), offset=0, limit=100, hash=0)
        )

        members = [user.user_id for user in participants.participants]

        if len(members) < 2:
            await message.reply_text("❌ Not enough users in the group to calculate love.")
            return
        
        user1_id, user2_id = random.sample(members, 2)
        user1 = await client.get_users(user1_id)
        user2 = await client.get_users(user2_id)

    # Generate love score
    love_score = random.randint(10, 100)
    love_message = LOVE_MESSAGES[min(love_score // 25, 4)]

    result = f"❤️ **Love Calculator** ❤️\n\n" \
             f"[{user1.first_name}](tg://user?id={user1.id}) + [{user2.first_name}](tg://user?id={user2.id}) " \
             f"= **{love_score}% Love**\n\n**{love_message}**"
    
    sent_msg = await message.reply_text(result)

    # Auto-delete the command message after 5 seconds
    await asyncio.sleep(5)
    await message.delete()


afk_users = {}

# 🔹 AFK Command
@app.on_message(filters.command("afk"))
async def set_afk(client: Client, message: Message):
    user_id = message.from_user.id
    reason = " ".join(message.command[1:]) if len(message.command) > 1 else "No reason provided"
    
    afk_users[user_id] = {"reason": reason, "time": datetime.now()}
    
    await message.reply_text(f"✅ You are now AFK!\n📜 Reason: {reason}")


# 🔹 Auto AFK Removal when AFK user sends a message
@app.on_message(filters.private | filters.group)
async def remove_afk_on_message(client: Client, message: Message):
    user_id = message.from_user.id

    # If the user was AFK, remove AFK status
    if user_id in afk_users:
        afk_info = afk_users.pop(user_id)
        afk_time = datetime.now() - afk_info["time"]
        await message.reply_text(f"✅ Welcome back! You were AFK for {afk_time.seconds} seconds.")
    
    # If replying to an AFK user, notify the sender
    if message.reply_to_message and message.reply_to_message.from_user.id in afk_users:
        afk_user_id = message.reply_to_message.from_user.id
        afk_info = afk_users[afk_user_id]
        afk_time = datetime.now() - afk_info["time"]
        
        await message.reply_text(
            f"🤖 {message.reply_to_message.from_user.first_name} is currently AFK!\n\n"
            f"🕒 Time Away: {afk_time.seconds} seconds\n"
            f"📜 Reason: {afk_info['reason']}"
        )


@app.on_message(filters.command(["tts"]))  # Exclude command messages
def text_to_speech(client, message):
    text = message.text
    tts = gTTS(text=text, lang='hi',  tld="co.in")  # Convert text to speech
    file_path = "speech.mp3"
    tts.save(file_path)

    message.reply_voice(voice=file_path)
    os.remove(file_path)  # Remove the file after sending

@app.on_message(filters.command("say"))
async def tts_handler(client, message):
    if len(message.command) < 2:
        await message.reply_text("❌ Usage: /say <text>")
        return

    text = " ".join(message.command[1:])
    file_path = "tts_voice.mp3"

    # Use an Indian female voice from Microsoft TTS
    voice = "hi-IN-SwaraNeural"  # Change this for other Indian voices

    # Convert text to speech
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(file_path)

    await message.reply_voice(voice=file_path, caption="🎤 Here is your voice message in an Indian female voice!")

    os.remove(file_path)  # Delete after sending


HINDI_VOICES = ["hi-IN-NeerjaNeural", "hi-IN-MadhurNeural", "hi-IN-PrabhatNeural"]

# Function to generate TTS audio
async def generate_tts(text, output_file):
    try:
        # Ensure text is not empty
        if not text.strip():
            raise ValueError("Text cannot be empty!")

        for voice in HINDI_VOICES:  # Try multiple voices
            tts = edge_tts.Communicate(text, voice)
            await tts.save(output_file)

            # Check if file exists and is not empty
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                return output_file

        raise RuntimeError("TTS failed with all available voices!")

    except Exception as e:
        raise RuntimeError(f"TTS Generation Error: {e}")

@app.on_message(filters.command("says"))
async def tts_handlerr(client, message):
    if len(message.command) < 2:
        await message.reply_text("⚠️ Please provide text! Example: `/tts Hello World`")
        return

    text = message.text.split(" ", 1)[1]  # Extract text after /tts
    output_file = "tts_output.mp3"

    try:
        await generate_tts(text, output_file)
        await message.reply_voice(output_file, caption="🎤 Here is your generated speech!")
        os.remove(output_file)  # Delete file after sending
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@app.on_message(filters.command("couple") & filters.group)
def choose_couple(client, message):
    chat_id = message.chat.id
    members = [member.user for member in client.get_chat_members(chat_id) if not member.user.is_bot]
    
    if len(members) < 2:
        message.reply_text("Not enough members to make a couple!")
        return
    
    couple = random.sample(members, 2)  # Select two random users
    message.reply_text(f"💞 Today's lucky couple: \n\n{couple[0].mention} ❤️ {couple[1].mention} 💞")

@app.on_message(filters.command("clean_deleted") & filters.group)
def remove_deleted_accounts(client, message):
    chat_id = message.chat.id
    deleted_users = []
    
    for member in client.get_chat_members(chat_id):
        if member.user.is_deleted:
            deleted_users.append(member.user.id)
            client.kick_chat_member(chat_id, member.user.id)
    
    if deleted_users:
        message.reply_text(f"Removed {len(deleted_users)} deleted accounts!")
    else:
        message.reply_text("No deleted accounts found!")

"""
@app.on_message(filters.text)
def ai_chat(client, message):
    user_input = message.text
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use latest OpenAI model
            messages=[{"role": "user", "content": user_input}],
            temperature=0.7
        )
        ai_reply = response["choices"][0]["message"]["content"]
        message.reply_text(ai_reply)
    except Exception as e:
        message.reply_text(f"Error: {e}")
        """


# Function to generate AI response
async def ask_gemini(question, msg):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=question,
        )

        return response.text
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Handle /ask command
@app.on_message(filters.command("ask"))
async def chat_handler(client, message):
    if len(message.command) < 2:
        await message.reply_text("❌ Usage: /ask <your question>")
        return
    
    question = message.text.split(None, maxsplit=1)[-1]
    msg = await message.reply_text("🤖 Thinking...")
    response = await ask_gemini(question, msg)
    await msg.edit_text(f" **Hi {message.from_user.mention}**\n\n **Abhi Gemini Ai Says** :\n\n**{response}**")


@app.on_message(filters.command("start"))
async def start_bot(_, message):
    await message.reply_text(f"Hi {message.from_user.mention}, how are you?")


def get_available_font():
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
        "arial.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            return path
    raise OSError("No valid font found. Install a TrueType font.")


# 🔹 Function to add text to image
def convert_sticker_to_image(input_path):
    output_path = input_path.replace(".webp", ".jpg").replace(".tgs", ".png")

    if input_path.endswith(".webp"):
        try:
            img = Image.open(input_path).convert("RGB")
            img.save(output_path, "JPEG")
            return output_path
        except Exception:
            return None

    elif input_path.endswith(".tgs"):
        try:
            cairosvg.svg2png(url=input_path, write_to=output_path)
            return output_path
        except Exception:
            return None

    return None


# 🔹 Convert GIFs to Images (Extract First Frame)
def convert_gif_to_image(gif_path):
    output_path = gif_path.replace(".gif", ".jpg").replace(".mp4", ".jpg")
    try:
        gif = imageio.mimread(gif_path)
        first_frame = Image.fromarray(gif[0]).convert("RGB")
        first_frame.save(output_path, "JPEG")
        return output_path
    except Exception:
        return None


# 🔹 Add Text to Image
def add_text_to_image(image_path, top_text=None, bottom_text=None, output_path="output_meme.jpg"):
    try:
        img = Image.open(image_path).convert("RGBA")
        draw = ImageDraw.Draw(img)
        font_path = get_available_font()
        font_size = int(img.width / 10)
        font = ImageFont.truetype(font_path, font_size)

        def draw_text(text, position):
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            x = (img.width - text_width) / 2
            y = position if position >= 0 else (img.height - text_height + position)
            draw.text((x, y), text, font=font, fill="white", stroke_width=4, stroke_fill="black")

        if top_text:
            draw_text(top_text, 10)
        if bottom_text:
            draw_text(bottom_text, img.height - font_size - 10)

        if img.mode == "RGBA":
            rgb_image = Image.new("RGB", img.size, (255, 255, 255))
            rgb_image.paste(img, mask=img.split()[3])
            rgb_image.save(output_path, "JPEG")
        else:
            img.save(output_path, "JPEG")

        return output_path
    except UnidentifiedImageError:
        return None


# 🟢 Command Handler: Generate Meme
@app.on_message(filters.command("mmf") & filters.reply)
async def mmf_handler(client: Client, message: Message):
    try:
        if not message.text or " " not in message.text:
            return await message.reply("⚠️ Usage: `/mmf top_text | bottom_text` or `/mmf top_text`")

        requested_text = message.text.split(" ", 1)[1]
        texts = requested_text.split("|")
        top_text = texts[0].strip() if texts[0] else None
        bottom_text = texts[1].strip() if len(texts) > 1 else None

        # Download Media
        media = message.reply_to_message.photo or message.reply_to_message.sticker or message.reply_to_message.animation
        if not media:
            return await message.reply("❌ Please reply to an image, sticker, or GIF with `/mmf top_text | bottom_text`")

        image_path = await client.download_media(media, file_name="temp")

        # ✅ **Ensure file downloaded correctly**
        if not os.path.exists(image_path) or os.path.getsize(image_path) == 0:
            return await message.reply("❌ Failed to download media. Try again.")

        # ✅ **Convert Stickers (if necessary)**
        if image_path.endswith((".webp", ".tgs")):
            converted_path = convert_sticker_to_image(image_path)
            if not converted_path:
                return await message.reply("⚠️ Failed to process sticker.")
            image_path = converted_path

        # ✅ **Convert GIFs to Images (Extract First Frame)**
        elif image_path.endswith((".mp4", ".gif")):
            converted_path = convert_gif_to_image(image_path)
            if not converted_path:
                return await message.reply("⚠️ Failed to process GIF.")
            image_path = converted_path

        # ✅ **Ensure the downloaded file is a valid image**
        try:
            img = Image.open(image_path)
        except UnidentifiedImageError:
            return await message.reply("⚠️ The downloaded file is not a valid image.")

        # ✅ **Generate Meme**
        meme_path = add_text_to_image(image_path, top_text, bottom_text)

        # ✅ **Ensure meme creation was successful**
        if not meme_path or not os.path.exists(meme_path):
            return await message.reply("⚠️ Failed to create the meme.")

        # ✅ **Send Meme**
        await message.reply_photo(meme_path, caption="🔥 Your meme is ready!")

        # ✅ **Cleanup**
        os.remove(image_path)
        os.remove(meme_path)

    except Exception as e:
        await message.reply(f"⚠️ Error: {e}")


async def main():
    await app.start()
    bot_ = await app.get_me()
    print(f"Bot started as @{bot_.username}!")
    await idle()
    await app.stop()
    print("Bot stoped!")



if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
