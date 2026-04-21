"""
SARIMA model for time series forecasting with seasonality
"""
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
import logging

logger = logging.getLogger(__name__)


class SARIMAForecaster:
    """SARIMA model for demand forecasting with seasonal patterns"""
    
    def __init__(self, order=(1, 1, 1), seasonal_order=(1, 1, 1, 24)):
        """
        Initialize SARIMA model
        
        Args:
            order: (p, d, q) order for ARIMA component
            seasonal_order: (P, D, Q, s) seasonal order (s=24 for daily seasonality)
        """
        self.order = order
        self.seasonal_order = seasonal_order
        self.model = None
        self.fitted_model = None
        
    def fit(self, train_data: pd.Series):
        """
        Fit SARIMA model
        
        Args:
            train_data: Training time series
        """
        logger.info(f"Fitting SARIMA{self.order}x{self.seasonal_order} model...")
        
        try:
            self.model = SARIMAX(
                train_data,
                order=self.order,
                seasonal_order=self.seasonal_order,
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            self.fitted_model = self.model.fit(disp=False, maxiter=200)
            
            logger.info("SARIMA model fitted successfully")
            logger.info(f"AIC: {self.fitted_model.aic:.2f}")
            logger.info(f"BIC: {self.fitted_model.bic:.2f}")
            
        except Exception as e:
            logger.error(f"Error fitting SARIMA model: {str(e)}")
            raise
    
    def predict(self, steps: int) -> np.ndarray:
        """
        Make predictions
        
        Args:
            steps: Number of steps to forecast
            
        Returns:
            Array of predictions
        """
        if self.fitted_model is None:
            raise ValueError("Model must be fitted before prediction")
        
        logger.info(f"Forecasting {steps} steps ahead...")
        
        forecast = self.fitted_model.forecast(steps=steps)
        
        # Ensure non-negative predictions
        forecast = np.maximum(forecast, 0)
        
        return forecast
    
    def predict_in_sample(self, test_data: pd.Series) -> np.ndarray:
        """
        Make one-step-ahead predictions by refitting on expanding window
        This provides much better accuracy for model evaluation
        
        Args:
            test_data: Test time series to predict
            
        Returns:
            Array of one-step-ahead predictions
        """
        if self.fitted_model is None:
            raise ValueError("Model must be fitted before prediction")
        
        logger.info(f"Making one-step-ahead predictions for {len(test_data)} steps...")
        
        predictions = []
        
        # Get the training data from the fitted model
        train_data = self.fitted_model.model.data.orig_endog
        
        for i in range(len(test_data)):
            try:
                # Make one-step forecast
                forecast = self.fitted_model.forecast(steps=1)[0]
                predictions.append(max(forecast, 0))
                
                # Append actual value and refit (expanding window)
                if i < len(test_data) - 1:
                    new_data = np.append(train_data, test_data.iloc[:i+1].values)
                    try:
                        self.model = SARIMAX(
                            new_data,
                            order=self.order,
                            seasonal_order=self.seasonal_order,
                            enforce_stationarity=False,
                            enforce_invertibility=False
                        )
                        self.fitted_model = self.model.fit(disp=False, maxiter=200, method_kwargs={"warn_convergence": False})
                    except Exception as refit_error:
                        # If refit fails, continue with current model
                        logger.warning(f"Refit failed at step {i}: {refit_error}. Using previous model.")
                        continue
            except Exception as e:
                logger.warning(f"Prediction failed at step {i}: {e}. Using last valid prediction.")
                # Use last prediction or mean if first prediction
                predictions.append(predictions[-1] if predictions else test_data.mean())
        
        return np.array(predictions)
    
    def get_model_summary(self) -> str:
        """Get model summary"""
        if self.fitted_model is None:
            return "Model not fitted yet"
        
        return str(self.fitted_model.summary())
