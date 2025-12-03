import asyncio
from telegram import Bot
from datetime import datetime
import os
import sys

BOT_TOKEN = os.environ.get('BOT_TOKEN') or os.environ.get('BOI_TOKEN', '')
CHANNEL_ID = os.environ.get('CHANNEL_ID', '')

async def post_anekdot():
    try:
        print("🚀 ЗАПУСК...")
        
        # Просто берем первый анекдот из файла
        with open('anekdots.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Берем все до первого "Опубликован:"
        parts = content.split('Опубликован:')
        if len(parts) > 1:
            first_joke = parts[0]
            
            # Ищем текст анекдота
            lines = first_joke.split('\n')
            for line in lines:
                if line.startswith('Текст:'):
                    joke_text = line.replace('Текст:', '').strip()
                    joke_text = joke_text.replace('\\n', '\n')
                    
                    # Отправляем
                    bot = Bot(token=BOT_TOKEN)
                    await bot.send_message(chat_id=CHANNEL_ID, text=joke_text)
                    print("✅ ОПУБЛИКОВАНО!")
                    
                    # Создаем ОБНОВЛЕННЫЙ файл
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    new_content = content.replace(
                        'Опубликован: \nДата:',
                        f'Опубликован: Да\nДата: {current_time}',
                        1  # Только первое вхождение
                    )
                    
                    with open('anekdots.txt', 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    print("💾 ФАЙЛ ОБНОВЛЕН!")
                    
                    with open('last_id.txt', 'w', encoding='utf-8') as f:
                        f.write('1')
                    
                    print("💾 last_id.txt ОБНОВЛЕН!")
                    return True
        
        print("❌ НЕ НАЙДЕНО АНЕКДОТОВ")
        return False
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        return False

async def main():
    success = await post_anekdot()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
