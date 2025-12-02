import pandas as pd
import asyncio
from telegram import Bot
from datetime import datetime
import os
import sys

# Получаем секреты
BOT_TOKEN = os.environ['BOT_TOKEN']
CHANNEL_ID = os.environ['CHANNEL_ID']
MY_CHAT_ID = os.environ.get('MY_CHAT_ID', '')

async def send_telegram_notification(message):
    """Отправляет уведомление в личный Telegram"""
    if not MY_CHAT_ID:
        return False
    try:
        bot = Bot(token=BOT_TOKEN)
        await bot.send_message(chat_id=MY_CHAT_ID, text=message)
        return True
    except Exception as e:
        print(f"Не удалось отправить уведомление: {e}")
        return False

def check_start_date():
    """Проверяет, можно ли начинать публикацию"""
    today = datetime.now().date()
    
    # Дата начала - завтра от сегодня
    # Если запускаешь сегодня, то завтра = старт
    start_date = datetime.now().date()  # Сегодня для теста
    
    # Для реального запуска с завтрашнего дня:
    # from datetime import timedelta
    # start_date = datetime.now().date() + timedelta(days=1)
    
    if today < start_date:
        print(f"⏸️ Бот еще не начал работу. Стартуем с {start_date}")
        return False
    return True

async def post_anekdot():
    """Основная функция публикации анекдота"""
    
    # Проверяем дату начала
    if not check_start_date():
        return False
    
    try:
        print("📖 Читаю файл с анекдотами...")
        
        # Читаем CSV, сохраняя переносы строк
        df = pd.read_csv('anekdots.csv', dtype=str, keep_default_na=False)
        
        # Статистика
        total = len(df)
        published = df['Опубликован?'].eq('Да').sum()
        remaining = total - published
        
        print(f"📊 Статистика: Всего анекдотов: {total}, Опубликовано: {published}, Осталось: {remaining}")
        
        # Предупреждение если мало анекдотов
        if 1 <= remaining <= 3 and MY_CHAT_ID:
            await send_telegram_notification(f"⚠️ Внимание! Осталось {remaining} анекдотов.")
        
        # Ищем неопубликованный анекдот
        for i, row in df.iterrows():
            if row.get('Опубликован?', '').strip() != 'Да':
                joke = str(row['Текст анекдота']).strip()
                
                if not joke or joke.lower() == 'nan':
                    continue
                
                # Публикуем анекдот в канал (БЕЗ времени и даты!)
                print(f"📤 Публикую анекдот #{i+1}...")
                bot = Bot(token=BOT_TOKEN)
                
                # Отправляем просто текст анекдота без добавлений
                await bot.send_message(chat_id=CHANNEL_ID, text=joke)
                
                # Обновляем CSV
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df.at[i, 'Опубликован?'] = 'Да'
                df.at[i, 'Дата публикации'] = current_time
                df.to_csv('anekdots.csv', index=False, encoding='utf-8')
                
                # Логируем (в логах оставляем время для отладки)
                joke_preview = joke.replace('\n', ' ')[:80]
                print(f"✅ Опубликован анекдот #{i+1}")
                print(f"   Текст: {joke_preview}...")
                print(f"   Время публикации: {current_time}")
                print(f"   Осталось анекдотов: {remaining - 1}")
                
                return True
        
        # Все анекдоты опубликованы
        print("📭 Все анекдоты опубликованы!")
        if MY_CHAT_ID:
            await send_telegram_notification(
                "🚨 ВСЕ АНЕКДОТЫ ЗАКОНЧИЛИСЬ!\n\n"
                "Добавь новые анекдоты в файл anekdots.csv\n"
                "или удали отметки 'Да' из столбца 'Опубликован?'"
            )
        
        return False
        
    except FileNotFoundError:
        print("❌ Файл anekdots.csv не найден!")
        return False
    except KeyError as e:
        print(f"❌ Ошибка в CSV: нет столбца {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {e}")
        return False

async def main():
    """Главная функция"""
    print("\n" + "="*50)
    print("🤖 БОТ ДЛЯ ПУБЛИКАЦИИ АНЕКДОТОВ")
    print("="*50)
    
    # Выводим информацию о расписании (только в логах)
    now = datetime.now()
    weekday = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"][now.weekday()]
    print(f"📅 Сегодня: {now.strftime('%d.%m.%Y')} ({weekday})")
    print(f"⏰ Время запуска: {now.strftime('%H:%M')}")
    print("="*50)
    
    success = await post_anekdot()
    
    print("\n" + "="*50)
    if success:
        print("✅ УСПЕШНО ЗАВЕРШЕНО")
        sys.exit(0)
    else:
        print("❌ ЗАВЕРШЕНО С ОШИБКОЙ")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
