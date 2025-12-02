import pandas as pd
import asyncio
from telegram import Bot
from telegram.constants import ParseMode
from datetime import datetime
import os
import sys

# Получаем секреты
BOT_TOKEN = os.environ['BOT_TOKEN']
CHANNEL_ID = os.environ['CHANNEL_ID']
MY_CHAT_ID = os.environ.get('MY_CHAT_ID', '')

async def send_telegram_notification(message):
    """Асинхронная отправка уведомления в Telegram"""
    if not MY_CHAT_ID:
        return False
    try:
        bot = Bot(token=BOT_TOKEN)
        await bot.send_message(
            chat_id=MY_CHAT_ID,
            text=message,
            parse_mode=ParseMode.HTML
        )
        return True
    except Exception as e:
        print(f"❌ Не удалось отправить уведомление: {e}")
        return False

async def post_anekdot():
    """Основная асинхронная функция"""
    try:
        print("📖 Читаю файл с анекдотами...")
        
        # Читаем CSV с указанием типов данных
        df = pd.read_csv('anekdots.csv', dtype=str)
        
        # Заменяем NaN на пустые строки
        df = df.fillna('')
        
        # Подсчитываем статистику
        total = len(df)
        published = df['Опубликован?'].eq('Да').sum()
        remaining = total - published
        
        print(f"📊 Всего: {total}, Опубликовано: {published}, Осталось: {remaining}")
        
        # Если осталось мало анекдотов
        if 1 <= remaining <= 3 and MY_CHAT_ID:
            warning_msg = f"⚠️ Внимание! Осталось {remaining} анекдотов!"
            await send_telegram_notification(warning_msg)
        
        # Ищем неопубликованный анекдот
        for i, row in df.iterrows():
            if row.get('Опубликован?', '').strip() != 'Да':
                joke = str(row['Текст анекдота']).strip()
                
                if not joke or joke.lower() == 'nan':
                    continue
                
                # Отправляем в канал
                print(f"📤 Публикую анекдот #{i+1}...")
                bot = Bot(token=BOT_TOKEN)
                await bot.send_message(chat_id=CHANNEL_ID, text=joke)
                
                # Обновляем CSV (теперь типы совпадают)
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df.at[i, 'Опубликован?'] = 'Да'
                df.at[i, 'Дата публикации'] = current_time
                
                # Сохраняем
                df.to_csv('anekdots.csv', index=False, encoding='utf-8')
                
                print(f"✅ Опубликован анекдот #{i+1}: {joke[:50]}...")
                return True
        
        # Если все опубликовано
        print("📭 Все анекдоты опубликованы!")
        
        if MY_CHAT_ID:
            await send_telegram_notification("🚨 Все анекдоты закончились! Добавь новые!")
        
        return False
        
    except FileNotFoundError:
        print("❌ Файл anekdots.csv не найден!")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {e}")
        return False

async def main():
    """Главная асинхронная функция"""
    print("\n" + "="*50)
    print("🤖 ЗАПУСК БОТА ДЛЯ ПУБЛИКАЦИИ АНЕКДОТОВ")
    print("="*50)
    
    success = await post_anekdot()
    
    print("\n" + "="*50)
    if success:
        print("✅ ВЫПОЛНЕНИЕ УСПЕШНО ЗАВЕРШЕНО")
        sys.exit(0)
    else:
        print("❌ ВЫПОЛНЕНИЕ ЗАВЕРШЕНО С ОШИБКОЙ")
        sys.exit(1)

if __name__ == "__main__":
    # Запускаем асинхронный код
    asyncio.run(main())
