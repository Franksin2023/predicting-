"""
Model training and evaluation module.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import joblib


class TimeSeriesModelTrainer:
    """
    Trains and calibrates walk-forward time series models (LightGBM + IsotonicRegression).
    """

    def __init__(self, n_splits: int = 5):
        self.n_splits = n_splits
        self.models: List[Any] = []
        self.calibrators: List[Any] = []

    def create_labels(self, df: pd.DataFrame, horizon: int = 12, threshold: float = 0.002) -> pd.Series:
        future_return = df['close'].shift(-horizon) / df['close'] - 1.0
        labels = (future_return > threshold).astype(int)
        return labels.dropna()

    def walk_forward_cv(self, X: pd.DataFrame, y: pd.Series) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        train_idx_list = []
        val_idx_list = []

        n_samples = len(X)
        fold_size = n_samples // (self.n_splits + 1)

        for i in range(1, self.n_splits + 1):
            train_end = fold_size * i
            val_end = train_end + fold_size
            if val_end > n_samples:
                val_end = n_samples

            train_indices = np.arange(0, train_end)
            val_indices = np.arange(train_end, val_end)

            train_idx_list.append(train_indices)
            val_idx_list.append(val_indices)

        return train_idx_list, val_idx_list

    def fit_and_calibrate(self, X: pd.DataFrame, y: pd.Series):
        import lightgbm as lgb
        from sklearn.isotonic import IsotonicRegression
        from sklearn.metrics import roc_auc_score

        train_idx_list, val_idx_list = self.walk_forward_cv(X, y)

        for fold, (train_idx, val_idx) in enumerate(zip(train_idx_list, val_idx_list)):
            X_train, y_train = X.iloc[train_idx], y.iloc[train_idx]
            X_val, y_val = X.iloc[val_idx], y.iloc[val_idx]

            model = lgb.LGBMClassifier(
                n_estimators=1000,
                learning_rate=0.03,
                max_depth=5,
                num_leaves=25,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1,
                verbose=-1
            )

            model.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                callbacks=[lgb.early_stopping(stopping_rounds=50, verbose=False)]
            )

            val_probs_raw = model.predict_proba(X_val)[:, 1]

            calibrator = IsotonicRegression(out_of_bounds='clip')
            calibrator.fit(val_probs_raw, y_val)

            val_probs_calibrated = calibrator.predict(val_probs_raw)
            print(f"--- Fold {fold+1} Validation Metrics ---")
            print(f"Raw AUC         : {roc_auc_score(y_val, val_probs_raw):.4f}")
            print(f"Brier Loss (Raw): {np.mean((val_probs_raw - y_val)**2):.4f}")
            print(f"Brier Loss (Cal): {np.mean((val_probs_calibrated - y_val)**2):.4f}")

            self.models.append(model)
            self.calibrators.append(calibrator)

    def predict_calibrated(self, X_new: pd.DataFrame) -> float:
        raw_preds = np.zeros(len(X_new))
        for model in self.models:
            raw_preds += model.predict_proba(X_new)[:, 1]
        raw_preds /= len(self.models)

        calibrated_preds = np.zeros(len(X_new))
        for calibrator in self.calibrators:
            calibrated_preds += calibrator.predict(raw_preds)
        calibrated_preds /= len(self.calibrators)

        return float(calibrated_preds[-1])

    def save(self, path: str):
        joblib.dump({'models': self.models, 'calibrators': self.calibrators}, path)

    def load(self, path: str):
        data = joblib.load(path)
        self.models = data['models']
        self.calibrators = data['calibrators']


class ModelTrainer(TimeSeriesModelTrainer):
    """
    Backward-compatible alias for TimeSeriesModelTrainer.
    """

    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        if X.empty or y.empty:
            return {"status": "error", "message": "Empty dataset"}
        self.fit_and_calibrate(X, y)
        return {"status": "success", "models_count": len(self.models)}

    def predict(self, X: pd.DataFrame) -> pd.Series:
        if X.empty:
            return pd.Series(dtype=float)
        pred = self.predict_calibrated(X)
        return pd.Series(pred, index=X.index[-1:])
