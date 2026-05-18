import joblib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
    RocCurveDisplay
)


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / 'data' / 'raw' / 'Churn_Modelling.csv'
MODEL_PATH = BASE_DIR / 'models' / 'best_model.pkl'

df = pd.read_csv(DATA_PATH)

best_model = joblib.load(MODEL_PATH)


def main():
    df = pd.read_csv(DATA_PATH)

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

    _, X_temp, _, y_temp = train_test_split(
        X, y,
        test_size=0.3,
        random_state=42,
        stratify=y
    )

    _, X_test, _, y_test = train_test_split(
        X_temp, y_temp,
        test_size=0.5,
        random_state=42,
        stratify=y_temp
    )

    artifact = joblib.load(MODEL_PATH)
    model = artifact['model']
    scaler = artifact['scaler']
    feature_names = artifact['feature_names']

    for col in feature_names:
        if col not in X_test.columns:
            X_test[col] = 0

    X_test = X_test[feature_names]

    numeric_columns = [
        'CreditScore',
        'Age',
        'Tenure',
        'Balance',
        'NumOfProducts',
        'EstimatedSalary'
    ]

    X_test[numeric_columns] = scaler.transform(X_test[numeric_columns]).astype(float)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    print('Accuracy:', round(accuracy_score(y_test, y_pred), 4))
    print('Precision:', round(precision_score(y_test, y_pred), 4))
    print('Recall:', round(recall_score(y_test, y_pred), 4))
    print('F1-score:', round(f1_score(y_test, y_pred), 4))
    print('ROC-AUC:', round(roc_auc_score(y_test, y_proba), 4))

    print('\nClassification Report:')
    print(classification_report(y_test, y_pred))

    cm = confusion_matrix(y_test, y_pred)

    plt.figure(figsize=(6, 4))
    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=['Stayed', 'Exited'],
        yticklabels=['Stayed', 'Exited']
    )
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.show()

    RocCurveDisplay.from_predictions(y_test, y_proba)
    plt.title('ROC Curve')
    plt.show()

    if hasattr(model, 'feature_importances_'):
        feature_importance = pd.DataFrame({
            'Feature': X_test.columns,
            'Importance': model.feature_importances_
        }).sort_values(by='Importance', ascending=False)

        plt.figure(figsize=(10, 6))
        sns.barplot(
            data=feature_importance,
            x='Importance',
            y='Feature'
        )
        plt.title('Feature Importance')
        plt.show()

        print('\nFeature Importance:')
        print(feature_importance)


if __name__ == '__main__':
    main()
