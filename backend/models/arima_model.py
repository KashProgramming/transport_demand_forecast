"""
ARIMA model for time series forecasting
"""
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
import logging

logger = logging.getLogger(__name__)


class ARIMAForecaster:
    """ARIMA model for demand forecasting"""
    
    def __init__(self, order=(5, 1, 2)):
        """
        Initialize ARIMA model
        
        Args:
            order: (p, d, q) order for ARIMA
        """
        self.order = order
        self.model = None
        self.fitted_model = None
        
    def check_stationarity(self, series: pd.Series) -> dict:
        """
        Check stationarity using Augmented Dickey-Fuller test
        
        Args:
            series: Time series data
            
        Returns:
            Dictionary with test results
        """
        logger.info("Performing ADF test for stationarity...")
        
        result = adfuller(series.dropna())
        
        adf_result = {
            'adf_statistic': result[0],
            'p_value': result[1],
            'critical_values': result[4],
            'is_stationary': result[1] < 0.05
        }
        
        logger.info(f"ADF Statistic: {adf_result['adf_statistic']:.4f}")
        logger.info(f"p-value: {adf_result['p_value']:.4f}")
        logger.info(f"Is stationary: {adf_result['is_stationary']}")
        
        return adf_result
    
    def fit(self, train_data: pd.Series):
        """
        Fit ARIMA model
        
        Args:
            train_data: Training time series
        """
        logger.info(f"Fitting ARIMA{self.order} model...")
        
        try:
            self.model = ARIMA(train_data, order=self.order)
            # Use method_kwargs to handle convergence issues and numerical stability
            self.fitted_model = self.model.fit(
                method_kwargs={
                    "warn_convergence": False,
                    "maxiter": 500,
                    "disp": False
                }
            )
            
            logger.info("ARIMA model fitted successfully")
            logger.info(f"AIC: {self.fitted_model.aic:.2f}")
            logger.info(f"BIC: {self.fitted_model.bic:.2f}")
            
        except np.linalg.LinAlgError as e:
            # Handle LU decomposition and other linear algebra errors
            logger.warning(f"Linear algebra error with ARIMA{self.order}: {str(e)}")
            logger.info("Attempting to fit with simpler ARIMA(1,1,1) model...")
            
            try:
                # Fall back to simpler model
                self.order = (1, 1, 1)
                self.model = ARIMA(train_data, order=self.order)
                self.fitted_model = self.model.fit(
                    method_kwargs={
                        "warn_convergence": False,
                        "maxiter": 500,
                        "disp": False
                    }
                )
                logger.info(f"Successfully fitted fallback ARIMA{self.order} model")
            except Exception as fallback_error:
                logger.error(f"Fallback ARIMA model also failed: {str(fallback_error)}")
                raise ValueError(f"ARIMA model fitting failed: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error fitting ARIMA model: {str(e)}")
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
                        self.model = ARIMA(new_data, order=self.order)
                        self.fitted_model = self.model.fit(
                            method_kwargs={
                                "warn_convergence": False,
                                "maxiter": 500,
                                "disp": False
                            }
                        )
                    except (np.linalg.LinAlgError, ValueError) as refit_error:
                        # If refit fails due to numerical issues, continue with current model
                        logger.warning(f"Refit failed at step {i} (numerical instability). Using previous model.")
                        continue
                    except Exception as refit_error:
                        # If refit fails for other reasons, continue with current model
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
