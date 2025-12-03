import asyncio
from telegram import Bot
from datetime import datetime
import os
import sys

# ============================================
# ПОЛУЧАЕМ ТОКЕНЫ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ
# ============================================

BOT_TOKEN = os.environ.get('BOT_TOKEN') or os.environ.get('BOI_TOKEN', '')
CHANNEL_ID = os.environ.get('CHANNEL_ID', '')
MY_CHAT_ID = os.environ.get('MY_CHAT_ID', '')

async def post_anekdot():
    """Публикует один анекдот"""
    try:
        print("🤖 БОТ ДЛЯ ПУБЛИКАЦИИ АНЕКДОТОВ")
        print("="*50)
        
        now = datetime.now()
        weekday = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"][now.weekday()]
        print(f"📅 Дата: {now.strftime('%d.%m.%Y')} ({weekday})")
        print(f"⏰ Время запуска: {now.strftime('%H:%M')} МСК")
        print("="*50)
        
        # Проверяем токены
        if not BOT_TOKEN:
            print("❌ ОШИБКА: Не указан BOT_TOKEN!")
            return False
        
        if not CHANNEL_ID:
            print("❌ ОШИБКА: Не указан CHANNEL_ID!")
            return False
        
        print("📖 Читаю файл с анекдотами...")
        
        # Читаем ВЕСЬ файл как ТЕКСТ
        with open('anekdots.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Просто ищем первый анекдот без "Опубликован: Да"
        if "Опубликован: Да" in content:
            # Уже что-то опубликовано, ищем следующий
            print("ℹ️  Уже есть опубликованные анекдоты, ищу следующий...")
            
            # Ищем позицию "Опубликован: " после первого анекдота
            parts = content.split("Опубликован: ")
            if len(parts) > 1:
                # Берем вторую часть (после первого "Опубликован: ")
                second_part = parts[1]
                # Ищем следующий "Опубликован: " без "Да"
                if "Да" not in second_part.split('\n')[0]:
                    # Нашли неопубликованный!
                    print("🎯 Найден неопубликованный анекдот")
                else:
                    # Все опубликовано
                    print("🎉 Все анекдоты уже опубликованы!")
                    return True
            else:
                print("❌ Не могу разобрать файл")
                return False
        else:
            print("🎯 Первый анекдот еще не опубликован")
        
        # ПРОСТОЙ СПОСОБ: публикуем ПЕРВЫЙ анекдот и обновляем файл
        lines = content.split('\n')
        updated_lines = []
        found_joke = False
        joke_text = ""
        
        for i, line in enumerate(lines):
            if not found_joke:
                # Ищем начало первого анекдота
                if line.startswith('Текст:'):
                    joke_text = line.replace('Текст:', '').strip()
                    joke_text = joke_text.replace('\\n', '\n')
                    found_joke = True
                    print(f"📝 Найден текст анекдота: {joke_text[:50]}...")
            
            # Обновляем строки
            if line.startswith('Опубликован:') and not found_joke:
                # Это уже опубликованный, пропускаем
                updated_lines.append(line)
            elif line.startswith('Опубликован:') and found_joke:
                # Нашли наш анекдот - помечаем как опубликованный
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                updated_lines.append('Опубликован: Да')
                # Добавляем дату на следующей строке
                if i+1 < len(lines) and lines[i+1].startswith('Дата:'):
                    # Заменяем существующую дату
                    lines[i+1] = f'Дата: {current_time}'
                else:
                    # Добавляем новую строку с датой
                    updated_lines.append(f'Дата: {current_time}')
            else:
                updated_lines.append(line)
        
        if joke_text:
            print(f"📤 Публикую анекдот в Telegram...")
            
            # Отправляем в Telegram
            bot = Bot(token=BOT_TOKEN)
            await bot.send_message(chat_id=CHANNEL_ID, text=joke_text)
            
            print("✅ Анекдот опубликован!")
            
            # Сохраняем обновленный файл
            with open('anekdots.txt', 'w', encoding='utf-8') as f:
                f.write('\n'.join(updated_lines))
            
            print("💾 anekdots.txt обновлен")
            
            # Обновляем last_id.txt
            with open('last_id.txt', 'w', encoding='utf-8') as f:
                f.write("1")  # Первый анекдот
            
            print("💾 last_id.txt обновлен: 1")
            
            return True
        else:
            print("❌ Не удалось найти текст анекдота")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Главная функция"""
    success = await post_anekdot()
    
    if success:
        print("="*50)
        print("✅ БОТ УСПЕШНО ЗАВЕРШИЛ РАБОТУ")
        print("="*50)
        sys.exit(0)
    else:
        print("="*50)
        print("❌ БОТ ЗАВЕРШИЛСЯ С ОШИБКОЙ")
        print("="*50)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
