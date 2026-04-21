"""
Prophet model for time series forecasting
"""
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class ProphetForecaster:
    """Prophet model for demand forecasting"""
    
    def __init__(self, yearly_seasonality=False, weekly_seasonality=True, 
                 daily_seasonality=True):
        """
        Initialize Prophet model
        
        Args:
            yearly_seasonality: Include yearly seasonality
            weekly_seasonality: Include weekly seasonality
            daily_seasonality: Include daily seasonality
        """
        try:
            from prophet import Prophet
            
            # Initialize Prophet with simple configuration
            self.model = Prophet(
                yearly_seasonality=yearly_seasonality,
                weekly_seasonality=weekly_seasonality,
                daily_seasonality=daily_seasonality,
                seasonality_mode='additive'
            )
            logger.info("Prophet initialized successfully")
                    
        except ImportError as e:
            logger.error(f"Prophet not installed: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Prophet: {e}")
            raise
            
        self.fitted = False
        
    def fit(self, train_data: pd.Series):
        """
        Fit Prophet model
        
        Args:
            train_data: Training time series with datetime index
        """
        logger.info("Fitting Prophet model...")
        
        # Prepare data in Prophet format
        df = pd.DataFrame({
            'ds': train_data.index,
            'y': train_data.values
        })
        
        # Suppress Prophet's verbose output and fit
        import warnings
        
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                # Let Prophet handle its own output suppression
                # Don't manually redirect stdout/stderr as it conflicts with CmdStan
                self.model.fit(df)
            
            self.fitted = True
            logger.info("Prophet model fitted successfully")
            
        except AttributeError as e:
            if 'stan_backend' in str(e):
                logger.error("Prophet backend error. CmdStan may not be properly installed.")
                logger.info("To fix: Run 'python -m cmdstanpy.install_cmdstan' in your terminal")
                raise RuntimeError("Prophet requires CmdStan to be installed. Run: python -m cmdstanpy.install_cmdstan")
            else:
                raise
        except Exception as e:
            logger.error(f"Prophet fitting failed: {e}")
            raise
    
    def predict(self, steps: int, freq='H') -> np.ndarray:
        """
        Make predictions
        
        Args:
            steps: Number of steps to forecast
            freq: Frequency of predictions ('H' for hourly)
            
        Returns:
            Array of predictions
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before prediction")
        
        logger.info(f"Forecasting {steps} steps ahead...")
        
        # Create future dataframe
        future = self.model.make_future_dataframe(periods=steps, freq=freq)
        
        # Make predictions
        forecast = self.model.predict(future)
        
        # Extract predictions for future periods only
        predictions = forecast['yhat'].tail(steps).values
        
        # Ensure non-negative predictions
        predictions = np.maximum(predictions, 0)
        
        return predictions
    
    def predict_in_sample(self, test_data: pd.Series, freq='H') -> np.ndarray:
        """
        Make one-step-ahead predictions by refitting on expanding window
        This provides much better accuracy for model evaluation
        
        Args:
            test_data: Test time series to predict
            freq: Frequency of predictions ('H' for hourly)
            
        Returns:
            Array of one-step-ahead predictions
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before prediction")
        
        logger.info(f"Making one-step-ahead predictions for {len(test_data)} steps...")
        
        predictions = []
        
        # Get original training data
        train_df = self.model.history.copy()
        
        import warnings
        from prophet import Prophet
        
        for i in range(len(test_data)):
            try:
                # Make one-step forecast
                future = self.model.make_future_dataframe(periods=1, freq=freq)
                
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    forecast = self.model.predict(future)
                    pred = forecast['yhat'].iloc[-1]
                    predictions.append(max(pred, 0))
                    
                    # Refit with new data point (expanding window)
                    if i < len(test_data) - 1:
                        new_row = pd.DataFrame({
                            'ds': [test_data.index[i]],
                            'y': [test_data.iloc[i]]
                        })
                        train_df = pd.concat([train_df, new_row], ignore_index=True)
                        
                        # Create NEW Prophet instance for refitting
                        try:
                            self.model = Prophet(
                                yearly_seasonality=False,
                                weekly_seasonality=True,
                                daily_seasonality=True,
                                seasonality_mode='additive'
                            )
                            self.model.fit(train_df)
                        except Exception as refit_error:
                            logger.warning(f"Refit failed at step {i}: {refit_error}. Using previous model.")
                            # Keep the previous model if refit fails
                            
            except Exception as e:
                logger.warning(f"Prediction failed at step {i}: {e}. Using last valid prediction.")
                # Use last prediction or mean if first prediction
                predictions.append(predictions[-1] if predictions else test_data.mean())
        
        return np.array(predictions)
    
    def get_forecast_components(self, steps: int, freq='H') -> pd.DataFrame:
        """
        Get forecast with components (trend, seasonality)
        
        Args:
            steps: Number of steps to forecast
            freq: Frequency of predictions
            
        Returns:
            DataFrame with forecast components
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before prediction")
        
        future = self.model.make_future_dataframe(periods=steps, freq=freq)
        forecast = self.model.predict(future)
        
        return forecast

