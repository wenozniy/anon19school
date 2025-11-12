from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from collections import deque
from datetime import datetime
import time

ADMINS = {1870435438, 8209990188}

blocked_users = set()
user_last_message_time = {}
usernames_map = {}
message_history = deque(maxlen=100)
CONFIRM_TEXT = "Ваше сообщение отправлено анонимно"

# --- Новый блок для режима ответа ---
admin_reply_mode = {}

def check_user(user_id: int) -> bool:
    if user_id in blocked_users:
        return False
    current_time = time.time()
    last_time = user_last_message_time.get(user_id, 0)
    if current_time - last_time < 3:
        return False
    user_last_message_time[user_id] = current_time
    return True

def build_admin_menu():
    keyboard = [
        [InlineKeyboardButton("Заблокированные", callback_data="menu_blocked")],
        [InlineKeyboardButton("Последние сообщения", callback_data="menu_recent")],
        [InlineKeyboardButton("Массовая рассылка", callback_data="menu_broadcastall")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def send_admin_menu_message(message, bot, text="Выберите действие администратора:"):
    await message.edit_text(text, reply_markup=build_admin_menu())

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Это анонимный бот. Отправляйте свои сообщения.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    username = user.username or "нет"
    usernames_map[user_id] = username
    # Если это админ в режиме ответа
    if user_id in ADMINS and admin_reply_mode.get(user_id):
        to_user_id = admin_reply_mode.pop(user_id, None)
        if to_user_id and to_user_id not in blocked_users:
            try:
                await context.bot.send_message(
                    chat_id=to_user_id,
                    text=f"Вам пришёл анонимный ответ на ваше сообщение:\n{update.message.text}"
                )
                await update.message.reply_text("Ответ отправлен пользователю анонимно.")
            except Exception:
                await update.message.reply_text("Ошибка отправки ответа пользователю.")
            return
        await update.message.reply_text("Ошибка: пользователь заблокирован или не найден.")
        return

    if user_id in blocked_users:
        await update.message.reply_text("Вы заблокированы и не можете отправлять сообщения.")
        return
    current_time = time.time()
    last_time = user_last_message_time.get(user_id, 0)
    if current_time - last_time < 3:
        await update.message.reply_text("Пожалуйста, подождите 3 секунды между сообщениями.")
        return
    user_last_message_time[user_id] = current_time
    await update.message.reply_text(CONFIRM_TEXT)
    message_history.append({
        "user_id": user_id,
        "username": username,
        "text": update.message.text,
        "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    info_text = f"ID: {user_id}\nUsername: @{username}"
    keyboard = [
        [InlineKeyboardButton("Заблокировать", callback_data=f"block_{user_id}")],
        [InlineKeyboardButton("Ответить", callback_data=f"reply_{user_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    for admin_id in ADMINS:
        info_msg = await context.bot.send_message(
            chat_id=admin_id,
            text=info_text,
            reply_markup=reply_markup
        )
        await context.bot.send_message(
            chat_id=admin_id,
            text=update.message.text,
            reply_to_message_id=info_msg.message_id
        )

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    username = user.username or "нет"
    usernames_map[user_id] = username
    if user_id in blocked_users:
        await update.message.reply_text("Вы заблокированы и не можете отправлять сообщения.")
        return
    current_time = time.time()
    last_time = user_last_message_time.get(user_id, 0)
    if current_time - last_time < 3:
        await update.message.reply_text("Пожалуйста, подождите 3 секунды между сообщениями.")
        return
    user_last_message_time[user_id] = current_time
    await update.message.reply_text(CONFIRM_TEXT)
    message_history.append({
        "user_id": user_id,
        "username": username,
        "text": "[Медиа]",
        "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    info_text = f"ID: {user_id}\nUsername: @{username}"
    keyboard = [
        [InlineKeyboardButton("Заблокировать", callback_data=f"block_{user_id}")],
        [InlineKeyboardButton("Ответить", callback_data=f"reply_{user_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    for admin_id in ADMINS:
        info_msg = await context.bot.send_message(
            chat_id=admin_id,
            text=info_text,
            reply_markup=reply_markup
        )
        if update.message.photo:
            await context.bot.send_photo(
                chat_id=admin_id,
                photo=update.message.photo[-1].file_id,
                caption=update.message.caption,
                reply_to_message_id=info_msg.message_id
            )
        elif update.message.video:
            await context.bot.send_video(
                chat_id=admin_id,
                video=update.message.video.file_id,
                caption=update.message.caption,
                reply_to_message_id=info_msg.message_id
            )
        elif update.message.voice:
            await context.bot.send_voice(
                chat_id=admin_id,
                voice=update.message.voice.file_id,
                caption=update.message.caption,
                reply_to_message_id=info_msg.message_id
            )
        elif update.message.audio:
            await context.bot.send_audio(
                chat_id=admin_id,
                audio=update.message.audio.file_id,
                caption=update.message.caption,
                reply_to_message_id=info_msg.message_id
            )
        elif update.message.document:
            await context.bot.send_document(
                chat_id=admin_id,
                document=update.message.document.file_id,
                caption=update.message.caption,
                reply_to_message_id=info_msg.message_id
            )
        elif update.message.video_note:
            await context.bot.send_video_note(
                chat_id=admin_id,
                video_note=update.message.video_note.file_id,
                reply_to_message_id=info_msg.message_id
            )
        elif update.message.sticker:
            await context.bot.send_sticker(
                chat_id=admin_id,
                sticker=update.message.sticker.file_id,
                reply_to_message_id=info_msg.message_id
            )
        else:
            await context.bot.send_message(
                chat_id=admin_id,
                text="[Неизвестный тип медиа]",
                reply_to_message_id=info_msg.message_id
            )

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in ADMINS:
        await update.message.reply_text("У вас нет доступа к этой команде.")
        return
    await update.message.reply_text(
        "Выберите действие администратора:",
        reply_markup=build_admin_menu()
    )

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id not in ADMINS:
        await query.answer(text="Нет доступа", show_alert=True)
        return
    if query.data == "menu_blocked":
        await query.answer()
        if not blocked_users:
            keyboard = [[InlineKeyboardButton("Назад", callback_data="menu_main")]]
            markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Нет заблокированных пользователей.", reply_markup=markup)
            return
        buttons = []
        text = "Заблокированные пользователи:\n"
        for user_id in blocked_users:
            username = usernames_map.get(user_id, "нет")
            text += f"\n{user_id}, @{username}"
            buttons.append([InlineKeyboardButton(f"Разблокировать {user_id}", callback_data=f"unblock_{user_id}")])
        buttons.append([InlineKeyboardButton("Назад", callback_data="menu_main")])
        markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(text, reply_markup=markup)
    elif query.data == "menu_recent":
        await query.answer()
        N = 5
        keyboard = [[InlineKeyboardButton("Назад", callback_data="menu_main")]]
        markup = InlineKeyboardMarkup(keyboard)
        if not message_history:
            await query.edit_message_text("Нет сообщений.", reply_markup=markup)
            return
        lines = []
        for m in list(message_history)[-N:]:
            lines.append(f"ID: {m['user_id']}, Username: @{m['username']}, Время: {m['time']}\nТекст: {m['text']}")
        await query.edit_message_text('\n\n'.join(lines), reply_markup=markup)
    elif query.data == "menu_broadcastall":
        await query.answer()
        keyboard = [[InlineKeyboardButton("Назад", callback_data="menu_main")]]
        markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Используйте команду:\n/broadcastall <текст>", reply_markup=markup)
    elif query.data == "menu_main":
        await send_admin_menu_message(query.message, context.bot)

async def block_user_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = int(query.data.split('_')[1])
    if user_id not in ADMINS:
        blocked_users.add(user_id)
        await query.edit_message_text(text=f"Пользователь {user_id} заблокирован.")
    else:
        await query.edit_message_text(text="Админа нельзя заблокировать!")

async def unblock_user_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = int(query.data.split('_')[1])
    if user_id in blocked_users:
        blocked_users.remove(user_id)
        await query.edit_message_text(text=f"Пользователь {user_id} разблокирован.")
    else:
        await query.edit_message_text(text="Пользователь не найден в списке заблокированных.")

async def block_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ADMINS:
        await update.message.reply_text("У вас нет доступа к этой команде.")
        return
    args = context.args
    if not args or not args[0].isdigit():
        await update.message.reply_text("Используйте: /block <user_id>")
        return
    user_id = int(args[0])
    if user_id not in ADMINS:
        blocked_users.add(user_id)
        await update.message.reply_text(f"Пользователь {user_id} заблокирован.")
    else:
        await update.message.reply_text("Админа нельзя заблокировать!")

async def blocked_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ADMINS:
        await update.message.reply_text("У вас нет доступа к этой команде.")
        return
    if not blocked_users:
        await update.message.reply_text("Нет заблокированных пользователей.")
        return
    for user_id in blocked_users:
        username = usernames_map.get(user_id, "нет")
        text = f"Заблокирован: {user_id}\nUsername: @{username}"
        keyboard = [[InlineKeyboardButton("Разблокировать", callback_data=f"unblock_{user_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup)

async def recent_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ADMINS:
        await update.message.reply_text("Нет доступа.")
        return
    N = int(context.args[0]) if context.args and context.args[0].isdigit() else 5
    if not message_history:
        await update.message.reply_text("Нет сообщений.")
        return
    lines = []
    for m in list(message_history)[-N:]:
        lines.append(f"ID: {m['user_id']}, Username: @{m['username']}, Время: {m['time']}\nТекст: {m['text']}")
    await update.message.reply_text('\n\n'.join(lines))

async def broadcastall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ADMINS:
        await update.message.reply_text("Нет доступа.")
        return
    text = ' '.join(context.args)
    for user_id in usernames_map.keys():
        if user_id not in blocked_users:
            try:
                await context.bot.send_message(chat_id=user_id, text=text)
            except Exception:
                continue
    await update.message.reply_text("Рассылка отправлена всем незаблокированным.")

# --- Новый обработчик: reply_user_callback ---
async def reply_user_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = int(query.data.split('_')[1])
    admin_id = query.from_user.id
    if admin_id in ADMINS:
        admin_reply_mode[admin_id] = user_id
        await query.edit_message_text(
            text=f"Введите ответ для пользователя {user_id}:"
        )
    else:
        await query.edit_message_text(text="Нет доступа.")

if __name__ == '__main__':
    application = ApplicationBuilder().token("8419583158:AAHSlwvz0Incd6QmLJLCbdvzs9219wW-XnQ").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin))
    application.add_handler(CommandHandler("block", block_user_command))
    application.add_handler(CommandHandler("blocked", blocked_list))
    application.add_handler(CommandHandler("recent", recent_messages))
    application.add_handler(CommandHandler("broadcastall", broadcastall_command))

    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))

    application.add_handler(MessageHandler(
        filters.PHOTO | filters.VIDEO | filters.VOICE | filters.AUDIO |
        filters.Document.ALL | filters.Sticker.ALL | filters.VIDEO_NOTE,
        handle_media
    ))

    application.add_handler(CallbackQueryHandler(menu_callback, pattern="^menu_"))
    application.add_handler(CallbackQueryHandler(block_user_callback, pattern="^block_"))
    application.add_handler(CallbackQueryHandler(unblock_user_callback, pattern="^unblock_"))
    application.add_handler(CallbackQueryHandler(reply_user_callback, pattern="^reply_"))

    application.run_polling()
