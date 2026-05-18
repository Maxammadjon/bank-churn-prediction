import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
from src.predict import predict_client


st.set_page_config(
    page_title='Bank Churn Prediction',
    page_icon='🏦',
    layout='centered'
)

st.title('🏦 Прогнозирование оттока клиентов банка')

st.write('Введите данные клиента, чтобы получить прогноз модели.')

credit_score = st.number_input('Credit Score', min_value=300, max_value=900, value=650)
geography = st.selectbox('Страна', ['France', 'Germany', 'Spain'])
gender = st.selectbox('Пол', ['Male', 'Female'])
age = st.number_input('Возраст', min_value=18, max_value=100, value=40)
tenure = st.number_input('Срок обслуживания в банке', min_value=0, max_value=10, value=5)
balance = st.number_input('Баланс на счёте', min_value=0.0, value=100000.0)
num_of_products = st.number_input('Количество продуктов', min_value=1, max_value=4, value=2)
has_cr_card = st.selectbox('Есть кредитная карта?', [1, 0])
is_active_member = st.selectbox('Активный клиент?', [1, 0])
estimated_salary = st.number_input('Примерная зарплата', min_value=0.0, value=90000.0)

if st.button('Получить прогноз'):
    client_data = {
        'CreditScore': credit_score,
        'Geography': geography,
        'Gender': gender,
        'Age': age,
        'Tenure': tenure,
        'Balance': balance,
        'NumOfProducts': num_of_products,
        'HasCrCard': has_cr_card,
        'IsActiveMember': is_active_member,
        'EstimatedSalary': estimated_salary
    }

    result = predict_client(client_data)

    probability_percent = result['probability'] * 100

    st.subheader('Результат прогнозирования')

    if result['prediction'] == 'Exited':
        st.error('Клиент может уйти из банка')
    else:
        st.success('Клиент, скорее всего, останется в банке')

    st.metric('Вероятность ухода', f'{probability_percent:.2f}%')
    st.write('Объяснение:', result['explanation'])
