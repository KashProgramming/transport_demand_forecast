"""
Utility functions for the Smart Urban Transport Demand Forecasting System
"""
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimize DataFrame memory usage by downcasting numeric types
    
    Args:
        df: Input DataFrame
        
    Returns:
        Memory-optimized DataFrame
    """
    logger.info("Optimizing data types...")
    initial_memory = df.memory_usage(deep=True).sum() / 1024**2
    
    # Optimize integers
    int_cols = df.select_dtypes(include=['int']).columns
    for col in int_cols:
        df[col] = pd.to_numeric(df[col], downcast='integer')
    
    # Optimize floats
    float_cols = df.select_dtypes(include=['float']).columns
    for col in float_cols:
        df[col] = pd.to_numeric(df[col], downcast='float')
    
    final_memory = df.memory_usage(deep=True).sum() / 1024**2
    logger.info(f"Memory reduced from {initial_memory:.2f} MB to {final_memory:.2f} MB "
                f"({100 * (initial_memory - final_memory) / initial_memory:.1f}% reduction)")
    
    return df


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Calculate evaluation metrics for time series forecasting
    
    Args:
        y_true: Actual values
        y_pred: Predicted values
        
    Returns:
        Dictionary containing RMSE, MAE, and MAPE
    """
    from sklearn.metrics import mean_squared_error, mean_absolute_error
    
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    
    # Calculate MAPE, avoiding division by zero
    mask = y_true != 0
    mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    
    return {
        'RMSE': rmse,
        'MAE': mae,
        'MAPE': mape
    }


def create_continuous_hourly_index(df: pd.DataFrame, datetime_col: str) -> pd.DataFrame:
    """
    Create a continuous hourly index, filling missing timestamps with 0
    
    Args:
        df: DataFrame with datetime index
        datetime_col: Name of datetime column
        
    Returns:
        DataFrame with continuous hourly index
    """
    # Create complete hourly range
    full_range = pd.date_range(
        start=df.index.min(),
        end=df.index.max(),
        freq='H'
    )
    
    # Reindex and fill missing values with 0
    df = df.reindex(full_range, fill_value=0)
    
    return df


def format_large_number(num: float) -> str:
    """
    Format large numbers with K, M suffixes
    
    Args:
        num: Number to format
        
    Returns:
        Formatted string
    """
    if num >= 1_000_000:
        return f"{num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num/1_000:.2f}K"
    else:
        return f"{num:.0f}"


def get_date_range_info(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get information about the date range in the dataset
    
    Args:
        df: DataFrame with datetime index
        
    Returns:
        Dictionary with date range information
    """
    return {
        'start_date': df.index.min(),
        'end_date': df.index.max(),
        'total_hours': len(df),
        'total_days': len(df) / 24
    }
