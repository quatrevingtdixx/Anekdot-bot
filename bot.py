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
        
        # Открываем файл с анекдотами
        with open('anekdots.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Делим на анекдоты
        jokes = content.strip().split('\n\n')
        
        print(f"📊 Всего анекдотов: {len(jokes)}")
        
        # Находим первый неопубликованный анекдот
        for i, joke_block in enumerate(jokes):
            lines = joke_block.strip().split('\n')
            
            # Проверяем, опубликован ли уже этот анекдот
            is_published = False
            joke_id = None
            
            for line in lines:
                if line.startswith('Опубликован:') and 'Да' in line:
                    is_published = True
                    break
                elif line.startswith('ID:'):
                    joke_id = line.replace('ID:', '').strip()
            
            if not is_published and joke_id:
                # Находим текст анекдота
                joke_text = ""
                for line in lines:
                    if line.startswith('Текст:'):
                        joke_text = line.replace('Текст:', '').strip()
                        break
                
                if joke_text:
                    print(f"📤 Публикую анекдот ID: {joke_id}...")
                    
                    # Заменяем \n на реальные переносы строк
                    joke_text = joke_text.replace('\\n', '\n')
                    
                    print(f"📝 Длина текста: {len(joke_text)} символов")
                    
                    # Отправляем в Telegram
                    bot = Bot(token=BOT_TOKEN)
                    await bot.send_message(chat_id=CHANNEL_ID, text=joke_text)
                    
                    # Обновляем TXT файл - помечаем как опубликованный
                    updated_lines = []
                    for line in joke_block.strip().split('\n'):
                        if line.startswith('Опубликован:'):
                            updated_lines.append('Опубликован: Да')
                        elif line.startswith('Дата:'):
                            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            updated_lines.append(f'Дата: {current_time}')
                        else:
                            updated_lines.append(line)
                    
                    jokes[i] = '\n'.join(updated_lines)
                    
                    # Сохраняем обновленный файл anekdots.txt
                    with open('anekdots.txt', 'w', encoding='utf-8') as f:
                        f.write('\n\n'.join(jokes))
                    
                    print(f"✅ Опубликован анекдот ID: {joke_id}")
                    
                    # Обновляем last_id.txt
                    with open('last_id.txt', 'w', encoding='utf-8') as f:
                        f.write(joke_id)
                    
                    # Считаем сколько осталось
                    published_count = sum(1 for j in jokes if 'Опубликован: Да' in j)
                    remaining = len(jokes) - published_count
                    
                    print(f"📊 Опубликовано: {published_count}, Осталось: {remaining}")
                    print(f"💾 Обновлен last_id.txt: {joke_id}")
                    
                    return True
        
        print("🎉 Все анекдоты уже опубликованы!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Главная функция"""
    success = await post_anekdot()
    
    if success:
        print("✅ УСПЕШНО ЗАВЕРШЕНО")
        sys.exit(0)
    else:
        print("❌ ЗАВЕРШЕНО С ОШИБКОЙ")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
