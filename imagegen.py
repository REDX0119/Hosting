from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
import json
import os

# Your tokens
TOKEN = '7503914601:AAEODGqNNWvd7OVpdxNrXfF8zeo73yYdMpI'  # Replace with your actual bot token
OPENAI_API_KEY = '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'  # Replace with your OpenAI API key

# Define the user ID that can add credits
ADMIN_USER_ID = 5457884198

# Load or initialize user data
user_data_file = 'user_data.json'

if os.path.exists(user_data_file):
    with open(user_data_file, 'r') as file:
        user_data = json.load(file)
else:
    user_data = {}

# Function to save user data to a file
def save_user_data():
    with open(user_data_file, 'w') as file:
        json.dump(user_data, file)

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    last_name = update.message.from_user.last_name

    if user_id not in user_data:
        user_data[user_id] = {
            'first_name': first_name,
            'last_name': last_name,
            'rank': 'FREE',
            'credits': 0  # Initialize with 0 credits
        }
        save_user_data()
        await update.message.reply_text("✅ You have been registered successfully!")
    else:
        await update.message.reply_text("✅ You are already registered.")

async def grant(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id

    # Check if the user is the admin
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("⚠️ You are not authorized to grant ranks.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("⚠️ Usage: /grant {user_id}")
        return

    target_user_id = int(context.args[0])

    if target_user_id in user_data:
        user_data[target_user_id]['rank'] = 'PREMIUM'
        save_user_data()
        await update.message.reply_text(f"✅ User ID {target_user_id} has been upgraded to PREMIUM.")
    else:
        await update.message.reply_text("⚠️ User ID not found.")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id

    if user_id in user_data:
        user_info = user_data[user_id]
        await update.message.reply_text(
            f"🌀 Account Details 🌀\n"
            f"First Name: {user_info['first_name']}\n"
            f"Last Name: {user_info['last_name']}\n"
            f"User ID: {user_id}\n"
            f"Rank: {user_info['rank']}\n"
            f"Credits: {user_info['credits']}"
        )
    else:
        await update.message.reply_text("⚠️ You do not have an account. Please use the /register command first.")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id

    # Check if the user is the admin
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("⚠️ You are not authorized to add credits.")
        return

    if len(context.args) != 2:
        await update.message.reply_text("⚠️ Usage: /add {user_id} {number_of_credits}")
        return

    target_user_id = int(context.args[0])
    credit_amount = int(context.args[1])

    if target_user_id in user_data:
        user_data[target_user_id]['credits'] += credit_amount
        save_user_data()
        await update.message.reply_text(f"✅ Added {credit_amount} credits to user ID {target_user_id}.")
    else:
        await update.message.reply_text("⚠️ User ID not found.")

async def img(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id

    # Check if the user is in the specified group chat
    is_group_chat = (chat_id == -1002250904563)

    # If in the group chat, allow the command without checking for credits
    if is_group_chat:
        if not context.args:
            await update.message.reply_text("⚠️ Please provide a prompt after the /img command.")
            return

        prompt = ' '.join(context.args)

        # Notify the user that the image is being processed
        await update.message.reply_text("WAIT YOUR IMAGE IS PROCESSING ⌛")

        image_url = f"https://imgen.duck.mom/prompt/{prompt}"

        # Fetch the image from the API
        try:
            response = requests.get(image_url)
            if response.status_code == 200:
                # Send the image to the user
                await update.message.reply_photo(photo=response.content)
            else:
                await update.message.reply_text("⚠️ An error occurred while generating the image.")
        except Exception as e:
            await update.message.reply_text("⚠️ An error occurred while fetching the image.")
    else:
        # For users outside the group chat, check if they have enough credits
        if user_id not in user_data:
            user_data[user_id] = {'credits': 0, 'rank': 'FREE'}  # Initialize user data if not exists

        if user_data[user_id]['credits'] < 2:
            await update.message.reply_text("⚠️ You do not have enough credits for this command (2 credits required).")
            return

        if not context.args:
            await update.message.reply_text("⚠️ Please provide a prompt after the /img command.")
            return

        prompt = ' '.join(context.args)

        # Notify the user that the image is being processed
        await update.message.reply_text("WAIT YOUR IMAGE IS PROCESSING ⌛")

        image_url = f"https://imgen.duck.mom/prompt/{prompt}"

        # Fetch the image from the API
        try:
            response = requests.get(image_url)
            if response.status_code == 200:
                # Send the image to the user
                await update.message.reply_photo(photo=response.content)
                user_data[user_id]['credits'] -= 2  # Deduct 2 credits for this command
                save_user_data()  # Save updated user data
            else:
                await update.message.reply_text("⚠️ An error occurred while generating the image.")
        except Exception as e:
            await update.message.reply_text("⚠️ An error occurred while fetching the image.")

def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("register", register))
    application.add_handler(CommandHandler("grant", grant))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(CommandHandler("add", add))  # Adding the /add command
    application.add_handler(CommandHandler("img", img))  # Adding the /img command

    application.run_polling()

if __name__ == '__main__':
    main()