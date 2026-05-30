import pandas as pd
import tkinter as tk
import joblib
from tkinter import messagebox
from tkinter import font as tkFont
from pathlib import Path


root = tk.Tk()
root.title('Прогноз оттока клиентов банка')

window_width = 1000
window_height = 850

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))

root.geometry(f'{window_width}x{window_height}+{x}+{y}')
root.minsize(900, 1050)

root.resizable(False, False)

def only_numbers(value):
    if value == '':
        return True

    allowed = '0123456789.,'

    for char in value:
        if char not in allowed:
            return False

    return True

vcmd = (root.register(only_numbers), '%P')

def check_fields(*args):
    fields = [
        entry_credit_score.get(),
        entry_age.get(),
        entry_tenure.get(),
        entry_balance.get(),
        entry_num_products.get(),
        entry_salary.get()
    ]

    if all(fields):
        btn_predict.config(state=tk.NORMAL)
    else:
        btn_predict.config(state=tk.DISABLED)

        entry_credit_score.bind('<KeyRelease>', check_fields)
        entry_age.bind('<KeyRelease>', check_fields)
        entry_tenure.bind('<KeyRelease>', check_fields)
        entry_balance.bind('<KeyRelease>', check_fields)
        entry_num_products.bind('<KeyRelease>', check_fields)
        entry_salary.bind('<KeyRelease>', check_fields)



def get_float(entry, field_name):
    value = entry.get().replace(',', '.')

    try:
        return float(value)
    except ValueError:
        messagebox.showerror(
            'Ошибка',
            f'Поле "{field_name}" Заполнено неправильно ячейка пустой:\nВведите число!'
        )
        return None

def predict_client(data):
    BASE_DIR = Path(__file__).resolve().parents[1]
    MODEL_PATH = BASE_DIR / "models" / "best_model.pkl"

    artifact = joblib.load(MODEL_PATH)

    model = artifact['model']
    scaler = artifact['scaler']
    feature_names = artifact['feature_names']

    df = pd.DataFrame([data])

    df = pd.get_dummies(
        df,
        columns=['Geography', 'Gender'],
        drop_first=True,
        dtype=int
    )

    for col in feature_names:
        if col not in df.columns:
            df[col] = 0

    df = df[feature_names]

    numeric_columns = [
        'CreditScore',
        'Age',
        'Tenure',
        'Balance',
        'NumOfProducts',
        'EstimatedSalary'
    ]

    df[numeric_columns] = scaler.transform(df[numeric_columns]).astype(float)

    prediction = model.predict(df)[0]
    probability = model.predict_proba(df)[0][1] * 100

    return prediction, probability


def func_predict():
    try:

        # CREDIT SCORE

        credit_score = float(entry_credit_score.get())

        if credit_score < 350 or credit_score > 850:
            messagebox.showerror(
                'Ошибка',
                'Кредитный рейтинг должен быть от 350 до 850'
            )
            return

        # AGE

        age = float(entry_age.get())

        if age < 18 or age > 100:
            messagebox.showerror(
                'Ошибка',
                'Возраст должен быть от 18 до 100'
            )
            return

        # TENURE

        tenure = float(entry_tenure.get())

        if tenure < 0 or tenure > 50:
            messagebox.showerror(
                'Ошибка',
                'Стаж клиента должен быть от 0 до 50 лет'
            )
            return

        # NUM PRODUCTS

        num_products = float(entry_num_products.get())

        if num_products < 1 or num_products > 10:
            messagebox.showerror(
                'Ошибка',
                'Количество продуктов должно быть от 1 до 10'
            )
            return

        # BALANCE

        balance = get_float(entry_balance, 'Баланс')

        # SALARY

        salary = get_float(entry_salary, 'Зарплата клиента')

        if None in [
            credit_score,
            age,
            tenure,
            balance,
            num_products,
            salary
        ]:
            return

        # дальше prediction

    except Exception as error:

        messagebox.showerror(
            'Ошибка',
            f'Произошла ошибка: {error}'
        )

        return

    if None in [credit_score, age, tenure, balance, num_products, salary]:
        return

    country_map = {
        'Франция': 'France',
        'Германия': 'Germany',
        'Испания': 'Spain'
    }

    gender_map = {
        'Мужчина': 'Male',
        'Женщина': 'Female'
    }

    data = {
        'CreditScore': credit_score,
        'Geography': country_map[geography_var.get()],
        'Gender': gender_map[gender_var.get().strip()],
        'Age': age,
        'Tenure': tenure,
        'Balance': balance,
        'NumOfProducts': num_products,
        'HasCrCard': 1 if card_var.get() == 'Да' else 0,
        'IsActiveMember': 1 if active_var.get() == 'Да' else 0,
        'EstimatedSalary': salary
    }

    try:
        prediction, probability = predict_client(data)

        result = 'Клиент уйдёт из банка' if prediction == 1 else 'Клиент останется в банке'
        result_text = f'{result}\nВероятность ухода: {probability:.2f}%'

        label_result.config(
            text=result_text,
            fg='red' if prediction == 1 else 'green'
        )

    except Exception as error:
        messagebox.showerror(
            'Ошибка',
            f'Произошла ошибка:\n{error}'
        )


root.title('Прогноз оттока клиентов банка')
root.geometry('500x700')
root.minsize(400, 600)

custom_font_label = tkFont.Font(family='Arial', size=12)
custom_font_entry = tkFont.Font(family='Arial', size=12)


def add_label(text):
    label = tk.Label(root, text=text, font=custom_font_label)
    label.pack(pady=(8, 0))


add_label('Кредитный рейтинг клиента от 350 до 850')
entry_credit_score = tk.Entry(
    root,
    font=custom_font_entry,
    width=30,
    validate='key',
    validatecommand=vcmd,
    justify='center'
)
entry_credit_score.pack()

add_label('Страна')
geography_var = tk.StringVar(value='Франция')
geography_menu = tk.OptionMenu(root, geography_var, 'Франция', 'Германия', 'Испания')
geography_menu.pack()

add_label('Пол')
gender_var = tk.StringVar(value='Мужчина')
gender_menu = tk.OptionMenu(root, gender_var, 'Мужчина', 'Женщина')
gender_menu.pack()

add_label('Возраст')
entry_age = tk.Entry(
    root,
    font=custom_font_entry,
    width=30,
    validate='key',
    validatecommand=vcmd,
    justify='center'
)
entry_age.pack()

add_label('Стаж клиента в банке')
entry_tenure = tk.Entry(
    root,
    font=custom_font_entry,
    width=30,
    validate='key',
    validatecommand=vcmd,
    justify='center'
)
entry_tenure.pack()

add_label('Баланс')
entry_balance = tk.Entry(
    root,
    font=custom_font_entry,
    width=30,
    validate='key',
    validatecommand=vcmd,
    justify='center'
)
entry_balance.pack()

add_label('Количество продуктов')
entry_num_products = tk.Entry(
    root,
    font=custom_font_entry,
    width=30,
    validate='key',
    validatecommand=vcmd,
    justify='center'
)
entry_num_products.pack()

add_label('Есть кредитная карта?')
card_var = tk.StringVar(value='Да')
card_menu = tk.OptionMenu(root, card_var, 'Да', 'Нет')
card_menu.pack()

add_label('Активный клиент?')
active_var = tk.StringVar(value='Да')
active_menu = tk.OptionMenu(root, active_var, 'Да', 'Нет')
active_menu.pack()

add_label('Зарплата клиента')
entry_salary = tk.Entry(
    root,
    font=custom_font_entry,
    width=30,
    validate='key',
    validatecommand=vcmd,
    justify='center'
)
entry_salary.pack()

btn_predict = tk.Button(
    root,
    text='Предсказать',
    command=func_predict,
    font=('Arial', 14, 'bold'),
    bg='green',
    fg='black',
    padx=10,
    pady=5
)
btn_predict.pack(pady=5)

label_result = tk.Label(
    root,
    text='Здесь будет результат',
    font=('Arial', 16, 'bold'),
    pady=5,
    wraplength=550,
    justify=tk.CENTER
)

label_result.pack(fill=tk.X, padx=10, pady=(5, 10))


root.mainloop()