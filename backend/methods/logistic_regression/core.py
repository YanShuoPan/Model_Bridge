"""
Logistic Regression Core Algorithms

Provides binary classification utilities and model evaluation functions.
"""

import numpy as np
from sklearn.linear_model import LogisticRegression as SklearnLogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve, accuracy_score, confusion_matrix


def train_logistic_model(X, y, max_iter=200):
    """
    Train a logistic regression model.

    Args:
        X: Feature matrix (n x p)
        y: Binary target (n,)
        max_iter: Maximum iterations for optimization

    Returns:
        Trained sklearn LogisticRegression model
    """
    model = SklearnLogisticRegression(max_iter=max_iter)
    model.fit(X, y)
    return model


def predict_probabilities(model, X):
    """
    Get predicted probabilities for positive class.

    Args:
        model: Trained logistic regression model
        X: Feature matrix

    Returns:
        Array of probabilities for class 1
    """
    return model.predict_proba(X)[:, 1]


def calculate_metrics(y_true, y_pred_proba, threshold=0.5):
    """
    Calculate classification metrics.

    Args:
        y_true: True labels
        y_pred_proba: Predicted probabilities
        threshold: Decision threshold

    Returns:
        dict with accuracy, auc, precision, recall, f1
    """
    y_pred = (y_pred_proba >= threshold).astype(int)

    # Confusion matrix
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

    # Metrics
    accuracy = accuracy_score(y_true, y_pred)
    auc = roc_auc_score(y_true, y_pred_proba)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "accuracy": float(accuracy),
        "auc": float(auc),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "true_positives": int(tp),
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn)
    }


def get_roc_curve_data(y_true, y_pred_proba):
    """
    Calculate ROC curve data.

    Args:
        y_true: True labels
        y_pred_proba: Predicted probabilities

    Returns:
        Tuple of (fpr, tpr, thresholds)
    """
    return roc_curve(y_true, y_pred_proba)
