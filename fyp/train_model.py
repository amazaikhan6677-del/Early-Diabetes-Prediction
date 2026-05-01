"""
Diabetes Prediction Model Trainer
===================================
Run this script ONCE to train the ML model and save it.

Usage:
    python train_model.py

Requirements:
    pip install scikit-learn pandas numpy matplotlib seaborn pickle5

Dataset:
    Uses the PIMA Indians Diabetes Dataset (diabetes.csv)
    Download from: https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database
    Place diabetes.csv in the same folder as this script.
"""

import pandas as pd
import numpy as np
import pickle
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, classification_report,
                              confusion_matrix, roc_auc_score, roc_curve)

# ─── Config ───────────────────────────────────────────────────────────────────
DATA_PATH   = 'diabetes.csv'
MODEL_DIR   = 'model'
MODEL_PATH  = os.path.join(MODEL_DIR, 'diabetes_model.pkl')
SCALER_PATH = os.path.join(MODEL_DIR, 'scaler.pkl')
os.makedirs(MODEL_DIR, exist_ok=True)

# ─── Load Data ────────────────────────────────────────────────────────────────
print("📂 Loading dataset...")
df = pd.read_csv(DATA_PATH)
print(f"   Shape: {df.shape}")
print(df.head())

# ─── Preprocessing ────────────────────────────────────────────────────────────
print("\n🔧 Preprocessing data...")

# Replace zero values in clinical columns with median (zeros are invalid)
zero_invalid_cols = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
for col in zero_invalid_cols:
    df[col] = df[col].replace(0, np.nan)
    df[col] = df[col].fillna(df[col].median())

print("   Zero-value replacement done.")
print(f"   Missing values after fix: {df.isnull().sum().sum()}")

# ─── EDA — Correlation Heatmap ────────────────────────────────────────────────
print("\n📊 Generating correlation heatmap...")
plt.figure(figsize=(10, 8))
sns.heatmap(df.corr(), annot=True, fmt='.2f', cmap='coolwarm', square=True)
plt.title('Feature Correlation Heatmap')
plt.tight_layout()
plt.savefig('model/correlation_heatmap.png', dpi=150)
plt.close()

# ─── Feature / Target Split ───────────────────────────────────────────────────
feature_cols = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
                'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']

X = df[feature_cols]
y = df['Outcome']

print(f"\n   Features: {feature_cols}")
print(f"   Class distribution:\n{y.value_counts()}")

# ─── Train/Test Split ─────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ─── Scaling ──────────────────────────────────────────────────────────────────
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

# ─── Train Models ─────────────────────────────────────────────────────────────
print("\n🤖 Training models...")

rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=8,
    min_samples_split=5,
    random_state=42,
    class_weight='balanced'
)
rf_model.fit(X_train_scaled, y_train)
rf_pred  = rf_model.predict(X_test_scaled)
rf_acc   = accuracy_score(y_test, rf_pred)
rf_auc   = roc_auc_score(y_test, rf_model.predict_proba(X_test_scaled)[:, 1])

lr_model = LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced')
lr_model.fit(X_train_scaled, y_train)
lr_pred  = lr_model.predict(X_test_scaled)
lr_acc   = accuracy_score(y_test, lr_pred)
lr_auc   = roc_auc_score(y_test, lr_model.predict_proba(X_test_scaled)[:, 1])

print(f"\n   Random Forest  — Accuracy: {rf_acc:.4f}  |  AUC: {rf_auc:.4f}")
print(f"   Logistic Reg.  — Accuracy: {lr_acc:.4f}  |  AUC: {lr_auc:.4f}")

# Choose best model
best_model = rf_model if rf_auc >= lr_auc else lr_model
best_name  = "Random Forest" if rf_auc >= lr_auc else "Logistic Regression"
print(f"\n✅ Selected: {best_name}")

# ─── Evaluation ───────────────────────────────────────────────────────────────
print("\n📋 Classification Report:")
best_pred = rf_pred if best_model is rf_model else lr_pred
print(classification_report(y_test, best_pred, target_names=['No Diabetes', 'Diabetes']))

# Confusion Matrix
cm = confusion_matrix(y_test, best_pred)
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['No Diabetes','Diabetes'],
            yticklabels=['No Diabetes','Diabetes'])
plt.title(f'Confusion Matrix — {best_name}')
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.tight_layout()
plt.savefig('model/confusion_matrix.png', dpi=150)
plt.close()

# ROC Curve
fpr, tpr, _ = roc_curve(y_test, best_model.predict_proba(X_test_scaled)[:, 1])
plt.figure(figsize=(7, 5))
plt.plot(fpr, tpr, color='#1D9E75', lw=2, label=f'AUC = {max(rf_auc, lr_auc):.3f}')
plt.plot([0,1],[0,1],'--',color='gray')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve')
plt.legend()
plt.tight_layout()
plt.savefig('model/roc_curve.png', dpi=150)
plt.close()

# Feature Importance (Random Forest)
if best_model is rf_model:
    importance = pd.Series(rf_model.feature_importances_, index=feature_cols).sort_values()
    plt.figure(figsize=(8, 5))
    importance.plot(kind='barh', color='#1D9E75')
    plt.title('Feature Importance — Random Forest')
    plt.tight_layout()
    plt.savefig('model/feature_importance.png', dpi=150)
    plt.close()

# ─── Cross-Validation ─────────────────────────────────────────────────────────
cv_scores = cross_val_score(best_model, scaler.transform(X), y, cv=10, scoring='roc_auc')
print(f"\n📈 10-Fold Cross-Validation AUC: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# ─── Save Model ───────────────────────────────────────────────────────────────
with open(MODEL_PATH, 'wb') as f:
    pickle.dump(best_model, f)
with open(SCALER_PATH, 'wb') as f:
    pickle.dump(scaler, f)

print(f"\n💾 Model saved → {MODEL_PATH}")
print(f"💾 Scaler saved → {SCALER_PATH}")
print("\n🎉 Training complete! Charts saved in model/ folder.")
print("    Now run: python app.py")
