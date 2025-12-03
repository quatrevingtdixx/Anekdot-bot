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
        
        # Читаем ВЕСЬ файл
        with open('anekdots.txt', 'r', encoding='utf-8') as f:
            all_text = f.read()
        
        # Разделяем на блоки анекдотов
        blocks = all_text.strip().split('\n\n')
        
        print(f"📊 Найдено блоков: {len(blocks)}")
        
        # Ищем первый неопубликованный анекдот
        for i in range(len(blocks)):
            block = blocks[i]
            
            # Проверяем есть ли "Опубликован: Да" в этом блоке
            if 'Опубликован: Да' in block:
                print(f"ℹ️  Блок {i+1} уже опубликован, пропускаю...")
                continue
            
            # Ищем ID
            lines = block.split('\n')
            joke_id = None
            joke_text = None
            
            for line in lines:
                if line.startswith('ID:'):
                    joke_id = line.replace('ID:', '').strip()
                elif line.startswith('Текст:'):
                    joke_text = line.replace('Текст:', '').strip()
            
            if joke_id and joke_text:
                print(f"🎯 Найден неопубликованный анекдот ID: {joke_id}")
                
                # Форматируем текст для Telegram
                formatted_text = joke_text.replace('\\n', '\n')
                print(f"📝 Длина текста: {len(formatted_text)} символов")
                print(f"📝 Превью: {formatted_text[:50]}...")
                
                # Публикуем в Telegram
                print(f"📤 Публикую анекдот ID: {joke_id}...")
                bot = Bot(token=BOT_TOKEN)
                await bot.send_message(chat_id=CHANNEL_ID, text=formatted_text)
                
                # Обновляем блок - добавляем пометку о публикации
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Создаем обновленный блок
                new_lines = []
                for line in lines:
                    if line.startswith('Опубликован:'):
                        new_lines.append('Опубликован: Да')
                    elif line.startswith('Дата:'):
                        new_lines.append(f'Дата: {current_time}')
                    else:
                        new_lines.append(line)
                
                blocks[i] = '\n'.join(new_lines)
                
                # Записываем обновленный файл
                with open('anekdots.txt', 'w', encoding='utf-8') as f:
                    f.write('\n\n'.join(blocks))
                
                print(f"✅ Анекдот ID: {joke_id} опубликован!")
                print(f"🕐 Время публикации: {current_time}")
                
                # Обновляем last_id.txt
                with open('last_id.txt', 'w', encoding='utf-8') as f:
                    f.write(joke_id)
                
                print(f"💾 last_id.txt обновлен: {joke_id}")
                
                # Считаем статистику
                published = sum(1 for b in blocks if 'Опубликован: Да' in b)
                total = len(blocks)
                
                print(f"📊 Статистика: Опубликовано: {published}/{total}")
                print(f"📊 Осталось: {total - published}")
                
                return True
        
        print("🎉 Все анекдоты уже опубликованы!")
        return True
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
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
