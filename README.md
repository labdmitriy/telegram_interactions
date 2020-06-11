# Библиотека для Домашнего задания 3 ("Обработка событий в Telegram") по курсу Airflow  
## Файлы
- telegram_interactions/ 
  - bot.py - Telegram-бот для отправки, изменения и ответа на сообщения
  - operators.py - Airflow operators
    - TelegramSendMessageOperator - отправка сообщений
    - TelegramEventSaveOperator - сохранение событий в Airtable
  - sensors.py - Airflow sensors
    - TelegramActionsIncrementSensor - мониторинг действий пользователей
