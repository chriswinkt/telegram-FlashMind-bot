import os
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

load_dotenv("hello.env")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Groq Chat Function
async def ask_gpt(prompt):
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "llama3-70b-8192",  # Use only valid models
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1024
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload
            )

            print("Response Status:", response.status_code)
            print("Response Body:", response.text)

            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

    except Exception as e:
        print("Groq API error:", e)
        return "⚠️ Sorry, I couldn't respond due to a system error."


# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I'm a ChatGPT bot powered by Groq. Ask me anything!")

# Handle Messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return  # Ignore messages without text (e.g., stickers, contacts, etc.)

    user_input = update.message.text
    reply = await ask_gpt(user_input)
    await update.message.reply_text(reply)


# Main function
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("🤖 Bot is running...")
    app.run_polling()
