"""
Model Evaluation Script
=======================
Load the trained model and evaluate its performance on the test set.

Usage:
    python evaluate_model.py

This script loads the saved model and scaler, then evaluates performance
using various metrics including accuracy, precision, recall, F1-score, and AUC.
"""

import pandas as pd
import numpy as np
import pickle
import os
from sklearn.metrics import (accuracy_score, classification_report,
                              confusion_matrix, roc_auc_score, roc_curve,
                              precision_recall_fscore_support)

# ─── Config ───────────────────────────────────────────────────────────────────
DATA_PATH   = 'diabetes.csv'
MODEL_DIR   = 'model'
MODEL_PATH  = os.path.join(MODEL_DIR, 'diabetes_model.pkl')
SCALER_PATH = os.path.join(MODEL_DIR, 'scaler.pkl')

# ─── Load Model and Scaler ────────────────────────────────────────────────────
print("🔄 Loading model and scaler...")
with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)
with open(SCALER_PATH, 'rb') as f:
    scaler = pickle.load(f)
print("✅ Model loaded successfully!")

# ─── Load and Preprocess Data ─────────────────────────────────────────────────
print("\n📂 Loading dataset...")
df = pd.read_csv(DATA_PATH)

# Same preprocessing as training
zero_invalid_cols = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
for col in zero_invalid_cols:
    df[col] = df[col].replace(0, np.nan)
    df[col] = df[col].fillna(df[col].median())

feature_cols = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
                'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']

X = df[feature_cols]
y = df['Outcome']

# ─── Evaluate on Full Dataset ─────────────────────────────────────────────────
print("\n📊 Evaluating model performance...")

# Scale the features
X_scaled = scaler.transform(X)

# Make predictions
y_pred = model.predict(X_scaled)
y_pred_proba = model.predict_proba(X_scaled)[:, 1]

# Calculate metrics
accuracy = accuracy_score(y, y_pred)
auc_score = roc_auc_score(y, y_pred_proba)

print(f"\n🎯 Model Performance Metrics:")
print(f"   Accuracy: {accuracy:.4f}")
print(f"   AUC Score: {auc_score:.4f}")

# Detailed classification report
print(f"\n📋 Detailed Classification Report:")
print(classification_report(y, y_pred, target_names=['No Diabetes', 'Diabetes']))

# Confusion Matrix
cm = confusion_matrix(y, y_pred)
print(f"\n🔢 Confusion Matrix:")
print(f"   True Negatives:  {cm[0,0]}")
print(f"   False Positives: {cm[0,1]}")
print(f"   False Negatives: {cm[1,0]}")
print(f"   True Positives:  {cm[1,1]}")

# Additional metrics
precision, recall, f1, support = precision_recall_fscore_support(y, y_pred, average='weighted')
print(f"\n📈 Weighted Metrics:")
print(f"   Precision: {precision:.4f}")
print(f"   Recall:    {recall:.4f}")
print(f"   F1-Score:  {f1:.4f}")

print(f"\n✅ Evaluation complete!")