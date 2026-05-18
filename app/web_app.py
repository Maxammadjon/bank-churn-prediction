import joblib
import os
import pandas as pd
from pathlib import Path
from flask import Flask, request, render_template

app = Flask(__name__)


def predict_client(data):
    BASE_DIR = Path(__file__).resolve().parents[1]
    MODEL_PATH = BASE_DIR / 'models' / 'best_model.pkl'

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


@app.route('/', methods=['GET'])
def show_index_page():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def func_predict():
    data = {
        'CreditScore': float(request.form['credit_score']),
        'Geography': request.form['geography'],
        'Gender': request.form['gender'],
        'Age': float(request.form['age']),
        'Tenure': float(request.form['tenure']),
        'Balance': float(request.form['balance']),
        'NumOfProducts': float(request.form['num_products']),
        'HasCrCard': float(request.form['has_card']),
        'IsActiveMember': float(request.form['active_member']),
        'EstimatedSalary': float(request.form['salary'])
    }

    prediction, probability = predict_client(data)

    result = 'Клиент уйдёт из банка' if prediction == 1 else 'Клиент останется в банке'

    result_text = f'{result}<br>Вероятность ухода: {probability:.2f}%'

    return render_template(
        'predict.html',
        prediction=prediction,
        probability=round(probability, 2)
    )

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        debug=True
    )