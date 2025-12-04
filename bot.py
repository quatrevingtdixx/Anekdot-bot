import telebot
import datetime
import os
import pytz

# Получаем переменные окружения
TOKEN = os.getenv('BOT_TOKEN')
CHANNEL = os.getenv('CHANNEL_ID')

# Администратор (для уведомлений)
ADMIN_ID_RAW = os.getenv("ADMIN_ID", "")
ADMIN_ID = int(ADMIN_ID_RAW) if ADMIN_ID_RAW.strip().isdigit() else 0

# Создаём бота
bot = telebot.TeleBot(TOKEN)

# Таймзона Москва
tz = pytz.timezone("Europe/Moscow")


def publish_joke():
    print("=" * 50)
    print("🤖 БОТ ДЛЯ АНЕКДОТОВ")
    print(f"📅 {datetime.datetime.now(tz).strftime('%d.%m.%Y %H:%M')}")
    print("=" * 50)

    try:
        # Читаем файл
        with open('anekdots.txt', 'r', encoding='utf-8') as f:
            text = f.read()

        # Делим на анекдоты
        jokes = text.strip().split('\n\n')

        # Находим неопубликованные
        unpublished = [j for j in jokes if 'Опубликован: Да' not in j]

        # Уведомляем, если осталось 6
        if len(unpublished) == 6 and ADMIN_ID != 0:
            bot.send_message(
                ADMIN_ID,
                "⚠️ Внимание! Осталось всего 6 неопубликованных анекдотов!"
            )
            print("📩 Предупреждение отправлено админу")

        # Ищем первый неопубликованный анекдот
        for joke in jokes:
            if 'Опубликован: Да' not in joke:

                # Ищем текст анекдота
                lines = joke.split('\n')
                joke_text = ""

                for line in lines:
                    if line.startswith('Текст:'):
                        joke_text = line.replace('Текст:', '').strip()
                        joke_text = joke_text.replace('\\n', '\n')

                # Публикуем анекдот
                print("📤 Публикую анекдот...")
                bot.send_message(CHANNEL, joke_text)
                print("✅ Опубликовано в Telegram!")

                # Обновляем блок текста
                now = datetime.datetime.now(tz)
                updated_joke = joke
                updated_joke = updated_joke.replace(
                    'Опубликован:',
                    'Опубликован: Да'
                )
                updated_joke = updated_joke.replace(
                    'Дата:',
                    f'Дата: {now.strftime("%Y-%m-%d %H:%M:%S")}'
                )

                # Перезаписываем в общем тексте
                new_text = text.replace(joke, updated_joke)

                # Сохраняем обновлённый файл
                with open('anekdots.txt', 'w', encoding='utf-8') as f:
                    f.write(new_text)

                print("💾 Файл anekdots.txt обновлён!")

                # Обновляем last_id
                with open('last_id.txt', 'w', encoding='utf-8') as f:
                    f.write('1')

                print("💾 last_id.txt обновлён!")
                return True

        print("🎉 Все анекдоты опубликованы!")
        return True

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


if __name__ == "__main__":
    if publish_joke():
        print("✅ ВСЁ ЗАРАБОТАЛО!")
        exit(0)
    else:
        print("❌ ЧТО-ТО ПОШЛО НЕ ТАК")
        exit(1)
