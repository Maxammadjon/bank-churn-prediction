import joblib
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / 'models' / 'best_model.pkl'


def prepare_input(data, feature_names, scaler):
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

    return df


def predict_client(data):
    artifact = joblib.load(MODEL_PATH)

    model = artifact['model']
    scaler = artifact['scaler']
    feature_names = artifact['feature_names']

    X = prepare_input(data, feature_names, scaler)

    probability = model.predict_proba(X)[0][1]
    prediction = model.predict(X)[0]

    result = 'Exited' if prediction == 1 else 'Stayed'

    if prediction == 1:
        explanation = 'Клиент имеет высокий риск ухода из банка.'
    else:
        explanation = 'Клиент с высокой вероятностью останется в банке.'

    return {
        'prediction': result,
        'probability': probability,
        'explanation': explanation
    }
