import telebot
import json
import os
import time
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = "8419583158:AAHSlwvz0Incd6QmLJLCbdvzs9219wW-XnQ"
ADMIN_USER_IDS = [8209990188, 1870435438]

# Файл для хранения заблокированных пользователей
BLOCKED_USERS_FILE = "blocked_users.json"

# Создаем бота
bot = telebot.TeleBot(BOT_TOKEN)


# Загрузка заблокированных пользователей из файла
def load_blocked_users():
    if os.path.exists(BLOCKED_USERS_FILE):
        try:
            with open(BLOCKED_USERS_FILE, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except:
            return set()
    return set()


# Сохранение заблокированных пользователей в файл
def save_blocked_users():
    with open(BLOCKED_USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(blocked_users), f, ensure_ascii=False)


# Загружаем заблокированных пользователей при старте
blocked_users = load_blocked_users()


# Функция для безопасной отправки сообщений
def safe_send_message(chat_id, text, max_retries=1):
    try:
        bot.send_message(chat_id, text)
        return True
    except Exception as e:
        logger.error(f"Ошибка отправки: {e}")
        return False


# Функция для безопасной отправки медиа
def safe_send_media(media_type, chat_id, file_id, caption=None):
    try:
        if media_type == 'photo':
            bot.send_photo(chat_id, file_id, caption=caption)
        elif media_type == 'video':
            bot.send_video(chat_id, file_id, caption=caption)
        elif media_type == 'document':
            bot.send_document(chat_id, file_id, caption=caption)
        elif media_type == 'audio':
            bot.send_audio(chat_id, file_id, caption=caption)
        elif media_type == 'voice':
            bot.send_voice(chat_id, file_id)
        elif media_type == 'sticker':
            bot.send_sticker(chat_id, file_id)
        elif media_type == 'video_note':
            bot.send_video_note(chat_id, file_id)
        return True
    except Exception as e:
        logger.error(f"Ошибка отправки медиа: {e}")
        return False


# Функция для получения информации о пользователе
def get_user_info(user):
    username = f"@{user.username}" if user.username else "не указан"
    first_name = user.first_name or "не указано"
    last_name = user.last_name or "не указана"

    return {
        'id': user.id,
        'first_name': first_name,
        'last_name': last_name,
        'username': username,
        'full_name': f"{first_name} {last_name}".strip()
    }


# Функция для проверки заблокирован ли пользователь
def is_user_blocked(user_id):
    return str(user_id) in blocked_users


# Функция для проверки является ли пользователь администратором
def is_admin(user_id):
    return user_id in ADMIN_USER_IDS


# Функция для блокировки пользователя
def block_user(user_id, admin_id):
    blocked_users.add(str(user_id))
    save_blocked_users()

    # Уведомляем всех администраторов о блокировке
    for admin in ADMIN_USER_IDS:
        safe_send_message(admin, f"🚫 Пользователь {user_id} заблокирован администратором {admin_id}")


# Функция для разблокировки пользователя
def unblock_user(user_id, admin_id):
    if str(user_id) in blocked_users:
        blocked_users.remove(str(user_id))
        save_blocked_users()

        # Уведомляем всех администраторов о разблокировке
        for admin in ADMIN_USER_IDS:
            safe_send_message(admin, f"✅ Пользователь {user_id} разблокирован администратором {admin_id}")
        return True
    return False


# Функция для отправки информации об отправителе всем администраторам
def send_user_info_to_all_admins(user_info, message_type, message_date):
    info_message = (
        f"─── 🔍 НОВОЕ СООБЩЕНИЕ ───\n"
        f"📦 Тип: {message_type}\n"
        f"🆔 ID: {user_info['id']}\n"
        f"👤 Имя: {user_info['full_name']}\n"
        f"📛 Юзернейм: {user_info['username']}\n"
        f"────────────────────"
    )

    for admin_id in ADMIN_USER_IDS:
        safe_send_message(admin_id, info_message)


# Функция для отправки сообщения всем администраторам
def send_message_to_all_admins(message_text):
    for admin_id in ADMIN_USER_IDS:
        safe_send_message(admin_id, message_text)


# Функция для отправки медиа всем администраторам
def send_media_to_all_admins(media_type, file_id, caption=None):
    for admin_id in ADMIN_USER_IDS:
        safe_send_media(media_type, admin_id, file_id, caption)


# Обработчик команд /start и /help
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if is_user_blocked(message.from_user.id):
        safe_send_message(message.chat.id, "🚫 Вы заблокированы и не можете использовать бота.")
        return

    welcome_text = (
        "👋 Привет! Я бот для анонимных сообщений.\n\n"
        "📝 Просто отправь мне любое сообщение (текст, фото, видео, голосовые и т.д.), "
        "и я перешлю его администраторам анонимно.\n\n"
        "⚙️ Команды администраторов:\n"
        "/block <id> - заблокировать пользователя\n"
        "/unblock <id> - разблокировать пользователя\n"
        "/blocked - список заблокированных\n"
        "/stats - статистика бота"
    )

    safe_send_message(message.chat.id, welcome_text)


# Команда для получения ID
@bot.message_handler(commands=['id'])
def get_id(message):
    user_info = get_user_info(message.from_user)

    response_text = (
        f"🆔 Ваш ID: {user_info['id']}\n"
        f"👤 Ваше имя: {user_info['full_name']}\n"
        f"📛 Юзернейм: {user_info['username']}"
    )

    safe_send_message(message.chat.id, response_text)


# Команда для блокировки пользователя
@bot.message_handler(commands=['block'])
def block_user_command(message):
    user_id = message.from_user.id

    if not is_admin(user_id):
        safe_send_message(message.chat.id, "❌ Эта команда только для администраторов")
        return

    if len(message.text.split()) < 2:
        safe_send_message(message.chat.id, "❌ Использование: /block <user_id>")
        return

    try:
        user_id_to_block = message.text.split()[1]
        block_user(user_id_to_block, user_id)
        safe_send_message(message.chat.id, f"✅ Пользователь {user_id_to_block} заблокирован")
    except Exception as e:
        safe_send_message(message.chat.id, f"❌ Ошибка при блокировке: {e}")


# Команда для разблокировки пользователя
@bot.message_handler(commands=['unblock'])
def unblock_user_command(message):
    user_id = message.from_user.id

    if not is_admin(user_id):
        safe_send_message(message.chat.id, "❌ Эта команда только для администраторов")
        return

    if len(message.text.split()) < 2:
        safe_send_message(message.chat.id, "❌ Использование: /unblock <user_id>")
        return

    try:
        user_id_to_unblock = message.text.split()[1]
        if unblock_user(user_id_to_unblock, user_id):
            safe_send_message(message.chat.id, f"✅ Пользователь {user_id_to_unblock} разблокирован")
        else:
            safe_send_message(message.chat.id, f"ℹ️ Пользователь {user_id_to_unblock} не был заблокирован")
    except Exception as e:
        safe_send_message(message.chat.id, f"❌ Ошибка при разблокировке: {e}")


# Команда для просмотра заблокированных пользователей
@bot.message_handler(commands=['blocked'])
def show_blocked_users(message):
    user_id = message.from_user.id

    if not is_admin(user_id):
        safe_send_message(message.chat.id, "❌ Эта команда только для администраторов")
        return

    if not blocked_users:
        safe_send_message(message.chat.id, "📋 Список заблокированных пользователей пуст")
        return

    blocked_list = "\n".join([f"🆔 {user_id}" for user_id in blocked_users])
    safe_send_message(message.chat.id, f"🚫 Заблокированные пользователи:\n\n{blocked_list}")


# Команда для проверки статуса пользователя
@bot.message_handler(commands=['check_user'])
def check_user_status(message):
    user_id = message.from_user.id

    if not is_admin(user_id):
        safe_send_message(message.chat.id, "❌ Эта команда только для администраторов")
        return

    if len(message.text.split()) < 2:
        safe_send_message(message.chat.id, "❌ Использование: /check_user <user_id>")
        return

    user_id_to_check = message.text.split()[1]
    if is_user_blocked(user_id_to_check):
        safe_send_message(message.chat.id, f"🚫 Пользователь {user_id_to_check} ЗАБЛОКИРОВАН")
    else:
        safe_send_message(message.chat.id, f"✅ Пользователь {user_id_to_check} не заблокирован")


# Команда для проверки бота
@bot.message_handler(commands=['check'])
def check_bot(message):
    user_id = message.from_user.id

    if not is_admin(user_id):
        safe_send_message(message.chat.id, "❌ Эта команда только для администраторов")
        return

    safe_send_message(message.chat.id,
                      "✅ Бот работает корректно!\n"
                      f"Сообщения отправляются {len(ADMIN_USER_IDS)} администраторам.\n"
                      f"Заблокировано пользователей: {len(blocked_users)}\n"
                      "Информация об отправителе и сообщения отправляются отдельно.")


# Команда для статистики
@bot.message_handler(commands=['stats'])
def show_stats(message):
    user_id = message.from_user.id

    if not is_admin(user_id):
        safe_send_message(message.chat.id, "❌ Эта команда только для администраторов")
        return

    stats_text = (
        f"📊 Статистика бота:\n"
        f"• Администраторов: {len(ADMIN_USER_IDS)}\n"
        f"• Заблокировано пользователей: {len(blocked_users)}\n"
        f"• Ваш ID: {user_id}\n"
        f"• Администраторы: {', '.join(map(str, ADMIN_USER_IDS))}"
    )
    safe_send_message(message.chat.id, stats_text)


# Обработчик текстовых сообщений
@bot.message_handler(content_types=['text'], func=lambda message: message.chat.type == 'private')
def handle_text(message):
    # Проверка блокировки
    if is_user_blocked(message.from_user.id):
        safe_send_message(message.chat.id, "🚫 Вы заблокированы и не можете отправлять сообщения.")
        return

    # Пропускаем команды
    if message.text.startswith('/'):
        return

    user_info = get_user_info(message.from_user)

    try:
        # Сначала отправляем информацию об отправителе всем администраторам
        send_user_info_to_all_admins(user_info, "📝 Текст", message.date)

        # Затем отправляем само сообщение всем администраторам
        send_message_to_all_admins(f"{message.text}")

        # Подтверждение пользователю
        safe_send_message(message.chat.id, "✅ Ваше сообщение отправлено администраторам анонимно!")

    except Exception as e:
        logger.error(f"Ошибка в handle_text: {e}")
        safe_send_message(message.chat.id, "❌ Произошла ошибка при отправке сообщения")


# Обработчик медиа сообщений
@bot.message_handler(
    content_types=['photo', 'video', 'document', 'audio', 'voice', 'sticker', 'video_note'],
    func=lambda message: message.chat.type == 'private'
)
def handle_media(message):
    # Проверка блокировки
    if is_user_blocked(message.from_user.id):
        safe_send_message(message.chat.id, "🚫 Вы заблокированы и не можете отправлять сообщения.")
        return

    user_info = get_user_info(message.from_user)

    # Типы медиа для русского отображения
    media_types = {
        'photo': ('🖼 Фото', 'фото'),
        'video': ('🎥 Видео', 'видео'),
        'document': ('📄 Документ', 'документ'),
        'audio': ('🎵 Аудио', 'аудио'),
        'voice': ('🎤 Голосовое сообщение', 'голосовое сообщение'),
        'sticker': ('🎨 Стикер', 'стикер'),
        'video_note': ('📹 Видео-заметка', 'видео-заметку')
    }

    media_type, media_type_lower = media_types.get(message.content_type, ('📎 Медиа', 'медиа'))

    try:
        # Сначала отправляем информацию об отправителе всем администраторам
        send_user_info_to_all_admins(user_info, media_type, message.date)

        # Затем отправляем само медиа всем администраторам
        if message.content_type == 'photo':
            send_media_to_all_admins('photo', message.photo[-1].file_id, message.caption)

        elif message.content_type == 'video':
            send_media_to_all_admins('video', message.video.file_id, message.caption)

        elif message.content_type == 'document':
            send_media_to_all_admins('document', message.document.file_id, message.caption)

        elif message.content_type == 'audio':
            send_media_to_all_admins('audio', message.audio.file_id, message.caption)

        elif message.content_type == 'voice':
            send_media_to_all_admins('voice', message.voice.file_id)

        elif message.content_type == 'sticker':
            send_media_to_all_admins('sticker', message.sticker.file_id)

        elif message.content_type == 'video_note':
            send_media_to_all_admins('video_note', message.video_note.file_id)

        # Подтверждение пользователю
        safe_send_message(message.chat.id, f"✅ Ваше {media_type_lower} отправлено администраторам анонимно!")

    except Exception as e:
        logger.error(f"Ошибка отправки медиа: {e}")
        safe_send_message(message.chat.id, f"❌ Произошла ошибка при отправке {media_type_lower}")


# Запуск бота
if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("Бот анонимных сообщений запущен!")
    logger.info("=" * 50)
    logger.info(f"ID бота: {bot.get_me().id}")
    logger.info(f"Администраторы: {', '.join(map(str, ADMIN_USER_IDS))}")
    logger.info(f"Количество администраторов: {len(ADMIN_USER_IDS)}")
    logger.info(f"Заблокировано пользователей: {len(blocked_users)}")
    logger.info("Все сообщения будут приходить всем администраторам")
    logger.info("Информация об отправителе и сообщения отправляются отдельно")
    logger.info("=" * 50)

    try:
        bot.infinity_polling(skip_pending=True, timeout=60)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
