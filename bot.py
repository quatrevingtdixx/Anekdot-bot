import telebot
import datetime
import os
import pytz

# ⬇️ Настрой: сюда вставь свой личный Telegram ID
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))  # можно через Secret или заменить цифрой

TOKEN = os.getenv('BOT_TOKEN')
CHANNEL = os.getenv('CHANNEL_ID')

bot = telebot.TeleBot(TOKEN)

# Таймзона (Москва как пример)
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

        # Считаем неопубликованные
        unpublished = [j for j in jokes if 'Опубликован: Да' not in j]

        # ⛔ Уведомление если осталось 6
        if len(unpublished) == 6 and ADMIN_ID != 0:
            bot.send_message(
                ADMIN_ID,
                "⚠️ Внимание! Осталось всего 6 неопубликованных анекдотов!"
            )
            print("📩 Отправлено предупреждение админу")

        # Ищем первый неопубликованный
        for joke in jokes:
            if 'Опубликован: Да' not in joke:

                # Находим текст анекдота
                lines = joke.split('\n')
                joke_text = ""

                for line in lines:
                    if line.startswith('Текст:'):
                        joke_text = line.replace('Текст:', '').strip()
                        joke_text = joke_text.replace('\\n', '\n')

                # Публикуем
                print(f"📤 Публикую анекдот...")
                bot.send_message(CHANNEL, joke_text)
                print("✅ Опубликовано в Telegram!")

                # Формируем новую версию блока
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

                # Обновляем текст целиком
                new_text = text.replace(joke, updated_joke)

                # Сохраняем файл
                with open('anekdots.txt', 'w', encoding='utf-8') as f:
                    f.write(new_text)

                print("💾 Файл anekdots.txt обновлен!")

                # Обновляем last_id
                with open('last_id.txt', 'w', encoding='utf-8') as f:
                    f.write('1')

                print("💾 last_id.txt обновлен!")
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
