from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
import os
import random
import json

# Load .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# JSON file to save boards
DATA_FILE = "data.json"

# Load data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

# Save data
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# Convert list of lists to int (not str) if needed
def fix_board_types(board):
    return [[int(cell) if isinstance(cell, str) and cell != "FREE" else cell for cell in row] for row in board]

# Generate board
def generate_bingo_board():
    board = []
    for i in range(5):
        column = random.sample(range(1 + i * 15, 16 + i * 15), 5)
        board.append(column)
    board[2][2] = 'FREE'
    return list(map(list, zip(*board)))

# Format board
def format_board(board, marks):
    result = "B   I   N   G   O\n"
    for row in board:
        line = ""
        for cell in row:
            if cell == 'FREE':
                line += " F  "
            elif cell in marks:
                line += "❌  "
            else:
                line += str(cell).rjust(2) + "  "
        result += line + "\n"
    return result

# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to Bingo Bot!\nUse /play to get a board.\nUse /mark <number> to mark numbers.")

# Play
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()

    board = generate_bingo_board()
    data[user_id] = {
        "board": board,
        "marks": []
    }

    save_data(data)
    await update.message.reply_text("Here’s your Bingo board:\n" + format_board(board, []))

# Mark
async def mark(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()

    if user_id not in data:
        await update.message.reply_text("Use /play first to get your board.")
        return

    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /mark <number>")
        return

    number = int(context.args[0])
    board = fix_board_types(data[user_id]["board"])
    marks = data[user_id]["marks"]

    flat_board = [cell for row in board for cell in row if cell != 'FREE']

    if number not in flat_board:
        await update.message.reply_text(f"{number} is not on your board.")
        return

    if number in marks:
        await update.message.reply_text(f"{number} is already marked.")
        return

    marks.append(number)
    data[user_id]["marks"] = marks
    save_data(data)

    await update.message.reply_text(f"Marked {number}!\n\n" + format_board(board, marks))

# Bot setup
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("play", play))
app.add_handler(CommandHandler("mark", mark))

app.run_polling()