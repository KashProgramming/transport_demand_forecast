"""
XGBoost model for time series forecasting
"""
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
import logging

logger = logging.getLogger(__name__)


class XGBoostForecaster:
    """XGBoost model for demand forecasting"""
    
    def __init__(self, n_estimators=100, max_depth=6, learning_rate=0.1):
        """
        Initialize XGBoost model
        
        Args:
            n_estimators: Number of boosting rounds
            max_depth: Maximum tree depth
            learning_rate: Learning rate
        """
        self.model = xgb.XGBRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            objective='reg:squarederror',
            random_state=42,
            n_jobs=-1
        )
        self.feature_names = None
        self.fitted = False
        
    def fit(self, X_train: pd.DataFrame, y_train: pd.Series):
        """
        Fit XGBoost model
        
        Args:
            X_train: Training features
            y_train: Training target
        """
        logger.info("Fitting XGBoost model...")
        
        self.feature_names = X_train.columns.tolist()
        
        self.model.fit(
            X_train,
            y_train,
            verbose=False
        )
        
        self.fitted = True
        logger.info("XGBoost model fitted successfully")
    
    def predict(self, X_test: pd.DataFrame) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X_test: Test features
            
        Returns:
            Array of predictions
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before prediction")
        
        predictions = self.model.predict(X_test)
        
        # Ensure non-negative predictions
        predictions = np.maximum(predictions, 0)
        
        return predictions
    
    def get_feature_importance(self) -> pd.DataFrame:
        """
        Get feature importance
        
        Returns:
            DataFrame with feature importance scores
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before getting feature importance")
        
        importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return importance
    
    def recursive_forecast(self, X_initial: pd.DataFrame, steps: int) -> np.ndarray:
        """
        Make recursive multi-step forecast
        
        Args:
            X_initial: Initial features for first prediction
            steps: Number of steps to forecast
            
        Returns:
            Array of predictions
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before prediction")
        
        # Validate input
        if X_initial is None or len(X_initial) == 0:
            raise ValueError("X_initial cannot be empty")
        
        logger.info(f"Making recursive forecast for {steps} steps...")
        
        predictions = []
        X_current = X_initial.iloc[[0]].copy()  # Ensure we have exactly one row
        
        for step in range(steps):
            # Predict next step
            pred = self.model.predict(X_current)[0]
            predictions.append(max(pred, 0))  # Ensure non-negative
            
            # Update features for next prediction
            if step < steps - 1:
                X_current = self._update_features(X_current, pred)
        
        return np.array(predictions)
    
    def _update_features(self, X: pd.DataFrame, new_value: float) -> pd.DataFrame:
        """
        Update features with new prediction for recursive forecasting
        
        Args:
            X: Current features
            new_value: New predicted value
            
        Returns:
            Updated features
        """
        X_new = X.copy()
        
        # Update lag features
        if 'demand_lag_1' in X_new.columns:
            X_new['demand_lag_1'] = new_value
        
        # Note: In production, you'd need to properly update all lag and rolling features
        # This is a simplified version
        
        return X_new
