import pandas as pd
from telegram import Bot
from telegram.constants import ParseMode
from datetime import datetime
import os
import sys

# Получаем секреты из переменных окружения GitHub Actions
BOT_TOKEN = os.environ['BOT_TOKEN']
CHANNEL_ID = os.environ['CHANNEL_ID']
MY_CHAT_ID = os.environ.get('MY_CHAT_ID', '')

def send_telegram_notification(message):
    if not MY_CHAT_ID:
        return False
    try:
        bot = Bot(token=BOT_TOKEN)
        bot.send_message(chat_id=MY_CHAT_ID, text=message, parse_mode=ParseMode.HTML)
        return True
    except Exception as e:
        print(f"Не удалось отправить уведомление: {e}")
        return False

def post_anekdot():
    try:
        print("📖 Читаю файл с анекдотами...")
        df = pd.read_csv('anekdots.csv')
        
        total = len(df)
        published = df['Опубликован?'].fillna('').eq('Да').sum()
        remaining = total - published
        
        print(f"📊 Всего: {total}, Опубликовано: {published}, Осталось: {remaining}")
        
        if 1 <= remaining <= 3:
            send_telegram_notification(f"⚠️ Внимание! Осталось {remaining} анекдотов!")
        
        for i, row in df.iterrows():
            if pd.isna(row.get('Опубликован?')) or row['Опубликован?'] != 'Да':
                joke = str(row['Текст анекдота']).strip()
                if not joke or joke == 'nan':
                    continue
                
                bot = Bot(token=BOT_TOKEN)
                bot.send_message(chat_id=CHANNEL_ID, text=joke)
                
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df.at[i, 'Опубликован?'] = 'Да'
                df.at[i, 'Дата публикации'] = current_time
                df.to_csv('anekdots.csv', index=False)
                
                print(f"✅ Опубликован анекдот #{i+1}: {joke[:50]}...")
                return True
        
        print("📭 Все анекдоты опубликованы!")
        send_telegram_notification("🚨 Все анекдоты закончились! Добавь новые!")
        return False
        
    except FileNotFoundError:
        print("❌ Файл anekdots.csv не найден!")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    success = post_anekdot()
    sys.exit(0 if success else 1)
