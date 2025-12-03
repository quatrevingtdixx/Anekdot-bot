import telebot
import datetime
import os

# Получаем токены
TOKEN = os.getenv('BOT_TOKEN')
CHANNEL = os.getenv('CHANNEL_ID')

# Создаем бота
bot = telebot.TeleBot(TOKEN)

def publish_joke():
    print("="*50)
    print("🤖 БОТ ДЛЯ АНЕКДОТОВ")
    print(f"📅 {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print("="*50)
    
    try:
        # Читаем файл
        with open('anekdots.txt', 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Делим на анекдоты
        jokes = text.strip().split('\n\n')
        
        for joke in jokes:
            # Ищем неопубликованный
            if 'Опубликован: Да' not in joke:
                # Нашли! Ищем текст
                lines = joke.split('\n')
                for line in lines:
                    if line.startswith('Текст:'):
                        joke_text = line.replace('Текст:', '').strip()
                        joke_text = joke_text.replace('\\n', '\n')
                        
                        # Публикуем
                        print(f"📤 Публикую анекдот...")
                        bot.send_message(CHANNEL, joke_text)
                        print("✅ Опубликовано в Telegram!")
                        
                        # Обновляем файл
                        updated_joke = joke.replace('Опубликован:', 'Опубликован: Да')
                        updated_joke = updated_joke.replace('Дата:', f'Дата: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
                        
                        # Заменяем в основном тексте
                        new_text = text.replace(joke, updated_joke)
                        
                        # Сохраняем
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
