# Bank Customer Churn Prediction

Проект прогнозирует, уйдёт клиент из банка или останется.

## Запуск

1. Установить библиотеки:

```bash
pip install -r requirements.txt
```

2. Положить датасет:

```text
data/raw/bank_churn.csv
```

3. Обучить модель:

```bash
python src/train.py
```

4. Проверить модель:

```bash
python src/evaluate.py
```

5. Запустить веб-приложение:

```bash
streamlit run app/streamlit_app.py
```

6. Запустить Telegram-бот:

Создать файл `.env` и добавить токен:

```text
BOT_TOKEN=your_telegram_bot_token_here
```

Потом запустить:

```bash
python bot/telegram_bot.py
```

## Признаки датасета

- CreditScore
- Geography
- Gender
- Age
- Tenure
- Balance
- NumOfProducts
- HasCrCard
- IsActiveMember
- EstimatedSalary
- Exited
