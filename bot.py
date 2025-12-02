import pandas as pd
import asyncio
from telegram import Bot
from telegram.constants import ParseMode
from datetime import datetime
import os
import sys

# Получаем секреты из переменных окружения GitHub Actions
BOT_TOKEN = os.environ['BOT_TOKEN']
CHANNEL_ID = os.environ['CHANNEL_ID']
MY_CHAT_ID = os.environ.get('MY_CHAT_ID', '')

async def send_telegram_notification(message):
    """Асинхронная отправка уведомления в личный Telegram"""
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
    """Основная асинхронная функция для публикации анекдота"""
    try:
        print("📖 Чтаю файл с анекдотами...")
        
        # Читаем CSV как строки, чтобы избежать проблем с типами данных
        df = pd.read_csv('anekdots.csv', dtype=str)
        
        # Заменяем NaN на пустые строки
        df = df.fillna('')
        
        # Подсчитываем статистику
        total = len(df)
        published = df['Опубликован?'].eq('Да').sum()
        remaining = total - published
        
        print(f"📊 Статистика: Всего анекдотов: {total}, Опубликовано: {published}, Осталось: {remaining}")
        
        # Если осталось мало анекдотов — отправляем предупреждение
        if 1 <= remaining <= 3 and MY_CHAT_ID:
            warning_msg = f"⚠️ <b>Внимание! Заканчиваются анекдоты</b>\n\nОсталось всего <b>{remaining}</b> анекдотов.\n\nДобавь новые в файл anekdots.csv"
            await send_telegram_notification(warning_msg)
            print(f"⚠️ Отправлено предупреждение: осталось {remaining} анекдотов")
        
        # Ищем первый неопубликованный анекдот
        for i, row in df.iterrows():
            if pd.isna(row.get('Опубликован?', '')) or row['Опубликован?'] != 'Да':
                joke = str(row['Текст анекдота']).strip()
                
                if not joke or joke.lower() == 'nan':
                    print(f"⚠️ Пропускаю пустой анекдот в строке {i+1}")
                    continue
                
                # Публикуем анекдот в канал
                print(f"📤 Публикую анекдот #{i+1}...")
                bot = Bot(token=BOT_TOKEN)
                
                # Отправляем с поддержкой HTML-разметки (для тегов <br>)
                try:
                    await bot.send_message(
                        chat_id=CHANNEL_ID, 
                        text=joke, 
                        parse_mode=ParseMode.HTML
                    )
                except Exception as e:
                    # Если ошибка с HTML, пробуем отправить без разметки
                    print(f"⚠️ Ошибка с HTML, пробую без разметки: {e}")
                    await bot.send_message(chat_id=CHANNEL_ID, text=joke)
                
                # Обновляем CSV файл
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df.at[i, 'Опубликован?'] = 'Да'
                df.at[i, 'Дата публикации'] = current_time
                
                # Сохраняем изменения
                df.to_csv('anekdots.csv', index=False, encoding='utf-8')
                
                # Обрезаем текст для логов
                joke_preview = joke.replace('<br>', ' ').replace('\n', ' ')[:60]
                print(f"✅ Опубликован анекдот #{i+1}: {joke_preview}...")
                print(f"   Время: {current_time}")
                print(f"   Осталось анекдотов: {remaining - 1}")
                
                return True  # Успешно нашли и опубликовали анекдот
        
        # Если все анекдоты опубликованы
        print("📭 Все анекдоты уже опубликованы!")
        
        # Отправляем срочное уведомление
        if MY_CHAT_ID:
            emergency_msg = (
                "🚨 <b>СРОЧНОЕ УВЕДОМЛЕНИЕ</b>\n\n"
                "💥 <b>Все анекдоты закончились!</b>\n\n"
                f"📈 Статистика:\n"
                f"• Всего анекдотов: {total}\n"
                f"• Опубликовано: {published}\n"
                f"• Осталось: 0\n\n"
                "🔧 <i>Что делать:</i>\n"
                "1. Открой файл anekdots.csv в репозитории\n"
                "2. Добавь новые анекдоты в конец файла\n"
                "3. Или удали значения 'Да' из столбца 'Опубликован?'\n"
                "4. Запусти workflow вручную для проверки"
            )
            
            if await send_telegram_notification(emergency_msg):
                print("✅ Отправлено уведомление о том, что анекдоты закончились")
        else:
            print("ℹ️ MY_CHAT_ID не установлен, уведомление не отправлено")
        
        # Дополнительно: можно автоматически сбросить все отметки (раскомментируй если нужно)
        # print("🔄 Сбрасываю все отметки о публикации...")
        # df['Опубликован?'] = ''
        # df['Дата публикации'] = ''
        # df.to_csv('anekdots.csv', index=False, encoding='utf-8')
        # print("✅ Все отметки сброшены, начинаю с начала")
        # return True
        
        return False  # Анекдотов не осталось
        
    except FileNotFoundError:
        error_msg = "❌ Файл anekdots.csv не найден!"
        print(error_msg)
        
        if MY_CHAT_ID:
            await send_telegram_notification(
                f"❌ <b>КРИТИЧЕСКАЯ ОШИБКА</b>\n\n{error_msg}"
            )
        return False
        
    except KeyError as e:
        error_msg = f"❌ Ошибка в формате CSV файла: {e}"
        print(error_msg)
        
        if MY_CHAT_ID:
            await send_telegram_notification(
                f"❌ <b>ОШИБКА В ФОРМАТЕ ФАЙЛА</b>\n\n{error_msg}"
            )
        return False
        
    except Exception as e:
        error_msg = f"❌ Неизвестная ошибка: {type(e).__name__}: {str(e)[:200]}"
        print(error_msg)
        
        if MY_CHAT_ID:
            await send_telegram_notification(
                f"❌ <b>НЕИЗВЕСТНАЯ ОШИБКА</b>\n\n{error_msg}"
            )
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
        sys.exit(0)  # Код 0 = успех
    else:
        print("❌ ВЫПОЛНЕНИЕ ЗАВЕРШЕНО С ОШИБКОЙ")
        sys.exit(1)  # Код 1 = ошибка

if __name__ == "__main__":
    # Запускаем асинхронный код
    asyncio.run(main())
