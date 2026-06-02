import os
import json
import warnings

import mlflow
import mlflow.sklearn

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier

from sklearn.model_selection import (
    GridSearchCV
)

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

warnings.filterwarnings("ignore")

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "dataset_preprocessing"
)

ARTIFACT_DIR = os.path.join(
    BASE_DIR,
    "artifacts"
)

os.makedirs(
    ARTIFACT_DIR,
    exist_ok=True
)

train_df = pd.read_csv(
    os.path.join(
        DATA_DIR,
        "train.csv"
    )
)

test_df = pd.read_csv(
    os.path.join(
        DATA_DIR,
        "test.csv"
    )
)

X_train = train_df.drop(
    "Quality",
    axis=1
)

y_train = train_df["Quality"]

X_test = test_df.drop(
    "Quality",
    axis=1
)

y_test = test_df["Quality"]

print(f"Train Shape : {X_train.shape}")
print(f"Test Shape  : {X_test.shape}")

param_grid = {

    "n_estimators": [
        100,
        200,
        300
    ],

    "max_depth": [
        5,
        10,
        15,
        None
    ],

    "min_samples_split": [
        2,
        5,
        10
    ],

    "min_samples_leaf": [
        1,
        2,
        4
    ]
}

with mlflow.start_run():

    print("Starting Hyperparameter Tuning...")

    grid_search = GridSearchCV(

        estimator=
        RandomForestClassifier(
            random_state=42
        ),

        param_grid=param_grid,

        cv=5,

        scoring="accuracy",

        n_jobs=-1,

        verbose=1
    )

    grid_search.fit(
        X_train,
        y_train
    )

    best_model = (
        grid_search.best_estimator_
    )

    y_train_pred = best_model.predict(
        X_train
    )

    y_test_pred = best_model.predict(
        X_test
    )

    train_accuracy = accuracy_score(
        y_train,
        y_train_pred
    )

    train_precision = precision_score(
        y_train,
        y_train_pred
    )

    train_recall = recall_score(
        y_train,
        y_train_pred
    )

    train_f1 = f1_score(
        y_train,
        y_train_pred
    )

    test_accuracy = accuracy_score(
        y_test,
        y_test_pred
    )

    test_precision = precision_score(
        y_test,
        y_test_pred
    )

    test_recall = recall_score(
        y_test,
        y_test_pred
    )

    test_f1 = f1_score(
        y_test,
        y_test_pred
    )

    mlflow.log_params(
        grid_search.best_params_
    )

    metrics = {

        "train_accuracy": train_accuracy,
        "train_precision": train_precision,
        "train_recall": train_recall,
        "train_f1": train_f1,

        "test_accuracy": test_accuracy,
        "test_precision": test_precision,
        "test_recall": test_recall,
        "test_f1": test_f1
    }

    mlflow.log_metrics(
        metrics
    )

    mlflow.sklearn.log_model(
        best_model,
        artifact_path="model"
    )

    cm_train = confusion_matrix(
        y_train,
        y_train_pred
    )

    plt.figure(figsize=(6,5))

    sns.heatmap(
        cm_train,
        annot=True,
        fmt="d"
    )

    plt.title(
        "Confusion Matrix Train"
    )

    train_cm_path = os.path.join(
        ARTIFACT_DIR,
        "confusion_matrix_train.png"
    )

    plt.savefig(train_cm_path)

    plt.close()

    mlflow.log_artifact(
        train_cm_path
    )

    cm_test = confusion_matrix(
        y_test,
        y_test_pred
    )

    plt.figure(figsize=(6,5))

    sns.heatmap(
        cm_test,
        annot=True,
        fmt="d"
    )

    plt.title(
        "Confusion Matrix Test"
    )

    test_cm_path = os.path.join(
        ARTIFACT_DIR,
        "confusion_matrix_test.png"
    )

    plt.savefig(test_cm_path)

    plt.close()

    mlflow.log_artifact(
        test_cm_path
    )

    train_report = classification_report(
        y_train,
        y_train_pred
    )

    train_report_path = os.path.join(
        ARTIFACT_DIR,
        "classification_report_train.txt"
    )

    with open(
        train_report_path,
        "w"
    ) as f:
        f.write(train_report)

    mlflow.log_artifact(
        train_report_path
    )

    test_report = classification_report(
        y_test,
        y_test_pred
    )

    test_report_path = os.path.join(
        ARTIFACT_DIR,
        "classification_report_test.txt"
    )

    with open(
        test_report_path,
        "w"
    ) as f:
        f.write(test_report)

    mlflow.log_artifact(
        test_report_path
    )

    feature_importance = pd.DataFrame({

        "feature":
        X_train.columns,

        "importance":
        best_model.feature_importances_
    })

    feature_importance = (
        feature_importance
        .sort_values(
            by="importance",
            ascending=False
        )
    )

    feature_path = os.path.join(
        ARTIFACT_DIR,
        "feature_importance.csv"
    )

    feature_importance.to_csv(
        feature_path,
        index=False
    )

    mlflow.log_artifact(
        feature_path
    )

    best_param_path = os.path.join(
        ARTIFACT_DIR,
        "best_params.json"
    )

    with open(
        best_param_path,
        "w"
    ) as f:

        json.dump(
            grid_search.best_params_,
            f,
            indent=4
        )

    mlflow.log_artifact(
        best_param_path
    )

    metrics_path = os.path.join(
        ARTIFACT_DIR,
        "metrics.json"
    )

    with open(
        metrics_path,
        "w"
    ) as f:

        json.dump(
            metrics,
            f,
            indent=4
        )

    mlflow.log_artifact(
        metrics_path
    )

    print("\nBest Parameters")
    print(grid_search.best_params_)

    print("\nTrain Accuracy")
    print(train_accuracy)

    print("\nTest Accuracy")
    print(test_accuracy)

    print(
        "\nRun successfully logged to DagsHub MLflow"
    )