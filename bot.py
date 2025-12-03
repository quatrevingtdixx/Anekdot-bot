import asyncio
from telegram import Bot
from datetime import datetime
import os
import sys
import json

# ============================================
# ВНИМАНИЕ: ТОКЕН БЕРЕТСЯ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ!
# НИКОГДА НЕ ПИШИ ТОКЕН ПРЯМО В КОДЕ!
# ============================================

# Получаем секреты из переменных окружения GitHub Actions
BOT_TOKEN = os.environ.get('BOT_TOKEN') or os.environ.get('BOI_TOKEN', '')
CHANNEL_ID = os.environ.get('CHANNEL_ID', '')
MY_CHAT_ID = os.environ.get('MY_CHAT_ID', '')

# Имя файла с анекдотами (теперь TXT формат)
JOKES_FILE = 'anekdots.txt'
PUBLISHED_FILE = 'published.json'  # Для хранения состояния

async def send_telegram_notification(message):
    """Отправляет уведомление в личный Telegram"""
    if not MY_CHAT_ID or not BOT_TOKEN:
        return False
    try:
        bot = Bot(token=BOT_TOKEN)
        await bot.send_message(chat_id=MY_CHAT_ID, text=message)
        return True
    except Exception as e:
        print(f"⚠️ Не удалось отправить уведомление: {e}")
        return False

def load_jokes_from_txt():
    """Загружает анекдоты из TXT файла"""
    jokes = []
    
    if not os.path.exists(JOKES_FILE):
        print(f"❌ Файл {JOKES_FILE} не найден!")
        return jokes
    
    try:
        with open(JOKES_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # Разделяем на отдельные анекдоты
        jokes_blocks = content.split('\n\n')
        
        for block in jokes_blocks:
            if not block.strip():
                continue
                
            joke_data = {
                'id': '',
                'text': '',
                'published': '',
                'date': ''
            }
            
            # Парсим строки блока
            for line in block.split('\n'):
                line = line.strip()
                if line.startswith('ID:'):
                    joke_data['id'] = line.replace('ID:', '').strip()
                elif line.startswith('Текст:'):
                    joke_data['text'] = line.replace('Текст:', '').strip()
                elif line.startswith('Опубликован:'):
                    joke_data['published'] = line.replace('Опубликован:', '').strip()
                elif line.startswith('Дата:'):
                    joke_data['date'] = line.replace('Дата:', '').strip()
            
            if joke_data['id'] and joke_data['text']:
                jokes.append(joke_data)
        
        print(f"📖 Загружено анекдотов из TXT: {len(jokes)}")
        return jokes
        
    except Exception as e:
        print(f"❌ Ошибка при чтении TXT файла: {e}")
        return []

def save_jokes_to_txt(jokes):
    """Сохраняет анекдоты обратно в TXT файл"""
    try:
        lines = []
        for joke in jokes:
            lines.append(f"ID: {joke['id']}")
            lines.append(f"Текст: {joke['text']}")
            lines.append(f"Опубликован: {joke['published']}")
            lines.append(f"Дата: {joke['date']}")
            lines.append('')  # Пустая строка между анекдотами
        
        with open(JOKES_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"💾 TXT файл успешно обновлен")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при сохранении TXT файла: {e}")
        return False

def load_published_status():
    """Загружает информацию об опубликованных анекдотах"""
    published_ids = []
    
    if os.path.exists(PUBLISHED_FILE):
        try:
            with open(PUBLISHED_FILE, 'r', encoding='utf-8') as f:
                published_ids = json.load(f)
            print(f"📊 Загружены опубликованные ID: {len(published_ids)}")
        except Exception as e:
            print(f"⚠️ Не удалось загрузить published.json: {e}")
    
    return published_ids

def save_published_status(published_ids):
    """Сохраняет информацию об опубликованных анекдотах"""
    try:
        with open(PUBLISHED_FILE, 'w', encoding='utf-8') as f:
            json.dump(published_ids, f, ensure_ascii=False, indent=2)
        print(f"💾 Сохранен published.json с {len(published_ids)} ID")
        return True
    except Exception as e:
        print(f"❌ Ошибка при сохранении published.json: {e}")
        return False

async def post_anekdot():
    """Основная функция публикации анекдота"""
    try:
        print(f"📖 Читаю файл с анекдотами: {JOKES_FILE}")
        
        # Загружаем анекдоты из TXT
        jokes = load_jokes_from_txt()
        
        if not jokes:
            print("❌ Нет анекдотов для публикации!")
            if MY_CHAT_ID and BOT_TOKEN:
                await send_telegram_notification("❌ ОШИБКА: Файл с анекдотами пустой!")
            return False, "Нет анекдотов"
        
        # Загружаем информацию об уже опубликованных
        published_ids = load_published_status()
        
        # Статистика
        total = len(jokes)
        published_count = len(published_ids)
        remaining = total - published_count
        
        print(f"📊 Статистика: Всего анекдотов: {total}, Опубликовано: {published_count}, Осталось: {remaining}")
        
        # Если все анекдоты уже опубликованы - это УСПЕХ
        if remaining == 0:
            print("🎉 Все анекдоты уже опубликованы!")
            if MY_CHAT_ID and BOT_TOKEN:
                await send_telegram_notification(
                    f"🎉 ВСЕ АНЕКДОТЫ УЖЕ ОПУБЛИКОВАНЫ!\n\n"
                    f"Всего анекдотов: {total}\n"
                    "Добавь новые анекдоты в файл anekdots.txt"
                )
            return True, "Все анекдоты уже опубликованы"
        
        # Предупреждение если мало анекдотов
        if 1 <= remaining <= 3 and MY_CHAT_ID and BOT_TOKEN:
            await send_telegram_notification(f"⚠️ Внимание! Осталось {remaining} анекдотов.")
        
        # Ищем первый неопубликованный анекдот
        for joke in jokes:
            if joke['id'] not in published_ids:
                # Публикуем анекдот в канал
                print(f"📤 Публикую анекдот ID: {joke['id']}...")
                
                try:
                    bot = Bot(token=BOT_TOKEN)
                    await bot.send_message(chat_id=CHANNEL_ID, text=joke['text'])
                except Exception as e:
                    print(f"❌ Ошибка при отправке в Telegram: {e}")
                    return False, f"Ошибка отправки: {e}"
                
                # Обновляем TXT файл
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                joke['published'] = 'Да'
                joke['date'] = current_time
                
                # Сохраняем изменения в TXT
                if not save_jokes_to_txt(jokes):
                    print("⚠️ Не удалось обновить TXT файл, но анекдот опубликован")
                
                # Обновляем список опубликованных
                published_ids.append(joke['id'])
                save_published_status(published_ids)
                
                # Обновляем статистику
                remaining_after = total - len(published_ids)
                
                # Логируем
                joke_preview = joke['text'][:80].replace('\n', ' ')
                print(f"✅ Опубликован анекдот ID: {joke['id']}")
                print(f"   Текст: {joke_preview}...")
                print(f"   Время публикации: {current_time}")
                print(f"   Осталось анекдотов: {remaining_after}")
                
                # Отправляем уведомление
                if MY_CHAT_ID and BOT_TOKEN:
                    await send_telegram_notification(
                        f"📤 Опубликован анекдот ID: {joke['id']}\n"
                        f"📅 {current_time}\n"
                        f"📊 Осталось: {remaining_after}/{total}"
                    )
                
                return True, f"Опубликован анекдот ID: {joke['id']}"
        
        # Если дошли сюда, значит что-то пошло не так
        print("ℹ️ Не удалось найти неопубликованный анекдот")
        return True, "Все анекдоты уже опубликованы"
        
    except Exception as e:
        error_msg = f"❌ Ошибка: {type(e).__name__}: {e}"
        print(error_msg)
        if MY_CHAT_ID and BOT_TOKEN:
            await send_telegram_notification(f"❌ ОШИБКА БОТА: {type(e).__name__}: {e}")
        return False, error_msg

async def main():
    """Главная функция"""
    print("\n" + "="*50)
    print("🤖 БОТ ДЛЯ ПУБЛИКАЦИИ АНЕКДОТОВ")
    print("="*50)
    
    # Проверка обязательных переменных
    if not BOT_TOKEN:
        print("❌ ОШИБКА: Не указан BOT_TOKEN в переменных окружения!")
        print("   Убедитесь, что в GitHub Secrets установлены:")
        print("   - BOT_TOKEN или BOI_TOKEN")
        return False, "Отсутствует BOT_TOKEN"
    
    if not CHANNEL_ID:
        print("❌ ОШИБКА: Не указан CHANNEL_ID в переменных окружения!")
        print("   Убедитесь, что в GitHub Secrets установлен CHANNEL_ID")
        return False, "Отсутствует CHANNEL_ID"
    
    # Выводим информацию (только в логах)
    now = datetime.now()
    weekday = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"][now.weekday()]
    print(f"📅 Дата: {now.strftime('%d.%m.%Y')} ({weekday})")
    print(f"⏰ Время запуска: {now.strftime('%H:%M')} МСК")
    print(f"📢 Канал: {CHANNEL_ID}")
    print(f"📁 Файл анекдотов: {JOKES_FILE}")
    print("="*50)
    
    success, message = await post_anekdot()
    
    print("\n" + "="*50)
    if success:
        print(f"✅ УСПЕШНО: {message}")
        return True, message
    else:
        print(f"❌ ОШИБКА: {message}")
        return False, message

if __name__ == "__main__":
    """
    Главная точка входа.
    Теперь бот завершается с exit code 0, когда все анекдоты опубликованы.
    Exit code 1 только при реальных ошибках.
    """
    try:
