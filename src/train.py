import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / 'data' / 'raw' / 'Churn_Modelling.csv'
MODEL_PATH = BASE_DIR / 'models' / 'best_model.pkl'


def preprocess_data(df):
    columns_to_drop = ['RowNumber', 'CustomerId', 'Surname']
    columns_to_drop = [col for col in columns_to_drop if col in df.columns]
    df = df.drop(columns=columns_to_drop)

    df = pd.get_dummies(
        df,
        columns=['Geography', 'Gender'],
        drop_first=True,
        dtype=int
    )

    X = df.drop('Exited', axis=1)
    y = df['Exited']

    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y,
        test_size=0.3,
        random_state=42,
        stratify=y
    )

    X_valid, X_test, y_valid, y_test = train_test_split(
        X_temp, y_temp,
        test_size=0.5,
        random_state=42,
        stratify=y_temp
    )

    numeric_columns = [
        'CreditScore',
        'Age',
        'Tenure',
        'Balance',
        'NumOfProducts',
        'EstimatedSalary'
    ]

    scaler = StandardScaler()

    X_train = X_train.copy()
    X_valid = X_valid.copy()
    X_test = X_test.copy()

    X_train[numeric_columns] = scaler.fit_transform(X_train[numeric_columns]).astype(float)
    X_valid[numeric_columns] = scaler.transform(X_valid[numeric_columns]).astype(float)
    X_test[numeric_columns] = scaler.transform(X_test[numeric_columns]).astype(float)

    return X_train, X_valid, X_test, y_train, y_valid, y_test, scaler, X.columns.tolist()


def main():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError('Файл data/raw/bank_churn.csv не найден')

    os.makedirs('models', exist_ok=True)

    df = pd.read_csv(DATA_PATH)

    X_train, X_valid, X_test, y_train, y_valid, y_test, scaler, feature_names = preprocess_data(df)

    model = RandomForestClassifier(random_state=42)

    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [5, 7, 10, None],
        'min_samples_split': [2, 5, 10],
        'class_weight': ['balanced']
    }

    grid_search = GridSearchCV(
        estimator=model,
        param_grid=param_grid,
        scoring='roc_auc',
        cv=5,
        n_jobs=-1,
        verbose=1
    )

    grid_search.fit(X_train, y_train)

    best_model = grid_search.best_estimator_

    y_pred = best_model.predict(X_test)
    y_proba = best_model.predict_proba(X_test)[:, 1]

    print('Лучшие параметры:')
    print(grid_search.best_params_)

    print('\nМетрики на test:')
    print('Accuracy:', round(accuracy_score(y_test, y_pred), 4))
    print('Precision:', round(precision_score(y_test, y_pred), 4))
    print('Recall:', round(recall_score(y_test, y_pred), 4))
    print('F1-score:', round(f1_score(y_test, y_pred), 4))
    print('ROC-AUC:', round(roc_auc_score(y_test, y_proba), 4))

    artifact = {
        'model': best_model,
        'scaler': scaler,
        'feature_names': feature_names
    }

    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(artifact, MODEL_PATH)
    print('\nМодель сохранена:', MODEL_PATH)


if __name__ == '__main__':
    main()
