import os
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
from telegram.ext import ContextTypes
from telegram import MessageEntity

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
    await update.message.reply_text("👋 Welcome to FlashMind Bot!. Ask me anything!")

# Handle Messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return  # Ignore non-text messages

    # Only respond in groups if bot is mentioned
    if update.message.chat.type in ['group', 'supergroup']:
        entities = update.message.entities or []
        bot_username = (await context.bot.get_me()).username

        # Check if bot was mentioned
        mentioned = any(
            e.type == MessageEntity.MENTION and 
            update.message.text[e.offset:e.offset + e.length] == f"@{bot_username}"
            for e in entities
        )

        if not mentioned:
            return  # Exit if bot was not mentioned

    # Proceed to respond
    user_input = update.message.text
    reply = await ask_gpt(user_input)
    await update.message.reply_text(reply)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = "🤖 *FlashMind Bot Help*\n\n" \
                "/ask <question> – Ask anything.\n" \
                "@BotName <message> – Mention to get replies in group.\n" \
                "/help – Show this message."
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = ' '.join(context.args)
    if not question:
        await update.message.reply_text("❓ Please provide a question. Example: `/ask What is Python?`", parse_mode="Markdown")
        return
    await update.message.reply_text("💭 Thinking...")
    
    # Your AI response logic here (e.g., OpenAI API or custom model)
    response = await ask_gpt(question)
    
    await update.message.reply_text(f"🤖 {response}")



# Main function
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ask", ask_command))


    print("🤖 Bot is running...")
    app.run_polling()
