"""
Model evaluation module for comparing forecasting models
"""
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Evaluate and compare time series forecasting models"""
    
    def __init__(self):
        self.results = []  # Changed to list to avoid persistence issues
        
    def evaluate_model(self, y_true: np.ndarray, y_pred: np.ndarray, 
                      model_name: str) -> dict:
        """
        Evaluate a single model
        
        Args:
            y_true: Actual values
            y_pred: Predicted values
            model_name: Name of the model
            
        Returns:
            Dictionary with evaluation metrics
        """
        logger.info(f"Evaluating {model_name}...")
        
        # Validate inputs
        if len(y_true) == 0 or len(y_pred) == 0:
            logger.warning(f"Cannot evaluate {model_name}: empty arrays")
            return None
        
        if len(y_true) != len(y_pred):
            logger.warning(f"Length mismatch for {model_name}: y_true={len(y_true)}, y_pred={len(y_pred)}")
            return None
        
        # Calculate metrics
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mae = mean_absolute_error(y_true, y_pred)
        
        # Calculate MAPE, avoiding division by zero
        mask = y_true != 0
        if mask.sum() > 0:
            mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
        else:
            mape = np.nan
        
        metrics = {
            'model': model_name,
            'RMSE': rmse,
            'MAE': mae,
            'MAPE': mape
        }
        
        self.results.append(metrics)  # Append to list instead of dict
        
        logger.info(f"{model_name} - RMSE: {rmse:.2f}, MAE: {mae:.2f}, MAPE: {mape:.2f}%")
        
        return metrics
    
    def get_comparison_table(self) -> pd.DataFrame:
        """
        Get comparison table of all evaluated models
        
        Returns:
            DataFrame with model comparison
        """
        if not self.results:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.results)
        df = df.sort_values('RMSE')
        
        return df
    
    def plot_comparison(self, y_true: np.ndarray, predictions: dict, 
                       dates: pd.DatetimeIndex) -> go.Figure:
        """
        Plot actual vs predicted for multiple models
        
        Args:
            y_true: Actual values
            predictions: Dictionary of {model_name: predictions}
            dates: Datetime index for x-axis
            
        Returns:
            Plotly figure
        """
        logger.info("Creating comparison plot...")
        
        fig = go.Figure()
        
        # Plot actual values
        fig.add_trace(go.Scatter(
            x=dates,
            y=y_true,
            mode='lines',
            name='Actual',
            line=dict(color='black', width=2)
        ))
        
        # Plot predictions for each model
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        for i, (model_name, y_pred) in enumerate(predictions.items()):
            fig.add_trace(go.Scatter(
                x=dates,
                y=y_pred,
                mode='lines',
                name=model_name,
                line=dict(color=colors[i % len(colors)], width=1.5, dash='dash')
            ))
        
        fig.update_layout(
            title='Model Comparison: Actual vs Predicted',
            xaxis_title='Date',
            yaxis_title='Demand',
            hovermode='x unified',
            height=500,
            legend=dict(x=0.01, y=0.99)
        )
        
        return fig
    
    def plot_residuals(self, y_true: np.ndarray, y_pred: np.ndarray, 
                      model_name: str) -> go.Figure:
        """
        Plot residuals for a model
        
        Args:
            y_true: Actual values
            y_pred: Predicted values
            model_name: Name of the model
            
        Returns:
            Plotly figure
        """
        residuals = y_true - y_pred
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Residuals Over Time', 'Residuals Distribution')
        )
        
        # Residuals over time
        fig.add_trace(
            go.Scatter(y=residuals, mode='lines', name='Residuals'),
            row=1, col=1
        )
        
        # Residuals histogram
        fig.add_trace(
            go.Histogram(x=residuals, name='Distribution'),
            row=1, col=2
        )
        
        fig.update_layout(
            title=f'Residual Analysis: {model_name}',
            height=400,
            showlegend=False
        )
        
        return fig
