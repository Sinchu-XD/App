import os
import asyncio
from pyrogram import Client, filters

# Environment Variables (Use user session, not bot token)
API_ID = int(os.getenv("API_ID", 7249983))  # Replace with your API ID
API_HASH = os.getenv("API_HASH", "be8ea36c220d5e879c91ad9731686642")
SESSION_STRING = os.getenv("SESSION_STRING", "BQBuoD8AUwOve46dl-Ukg7F1uNCBoRBTJC32x7mJirGtGzVOj2tAESQH-yhh2U0mgRUB7QJb7Thit-k1Gazr0kAI7Sqqi2lwcAKzQWwWpWhtRmU9pWRVYTbtqyBsJKb5Ij5dQrnMw1ODtnrpA3UK-T4ULKy6_yNMxJjx0N0kycIpl64oTv09Sw4FfwuSE5kEnGj0-8rQV3vg_sQXJzw8n63RQKNtr7pNxJwcLg6_SsTm59qFzjzEwRUDHGAZliHK6Dkv64zz3m9XNjOauIUr2yBq7_o0QF2hJx5qP0FS_gQZETZuWmNFZ7iWs65Lp1O0hVvuRzyBmhX1oBvCyQJ9NGdXDICMMQAAAAHjq--iAA")  # Generate this using Pyrogram

# Initialize Pyrogram Userbot
app = Client("UserbotSession", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

@app.on_message(filters.command("ping") & filters.me)
async def ping(client, message):
    await message.reply_text("🏓 Pong!")

@app.on_message(filters.command("myadminrights") & filters.me)
async def check_admin_rights(client, message):
    chat_member = await client.get_chat_member(message.chat.id, client.me.id)
    
    if chat_member.status in ["administrator", "creator"]:
        rights = chat_member.privileges
        await message.reply_text(f"✅ You are an admin!\n\n**Your Rights:**\n{rights}")
    else:
        await message.reply_text("❌ You are not an admin in this group.")



@app.on_message(filters.command("acceptall") & filters.me)
async def accept_all_requests(client, message):
    chat_id = message.chat.id
    approved_count = 0

    try:
        async for request in client.get_chat_join_requests(chat_id):  # Works only for userbots
            await client.approve_chat_join_request(chat_id, request.from_user.id)
            approved_count += 1

        if approved_count == 0:
            await message.reply_text("❌ No pending join requests.")
        else:
            await message.reply_text(f"✅ Approved {approved_count} join requests!")

    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

# Start the Userbot
async def main():
    await app.start()
    print("✅ Userbot Started!")
    await asyncio.get_event_loop().create_future()  # Keeps the script running

if __name__ == "__main__":
    asyncio.run(main())
  
