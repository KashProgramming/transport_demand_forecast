"""
Data loading module with memory optimization for large datasets
"""
import pandas as pd
import numpy as np
from typing import Optional
import logging
from src.utils.utils import optimize_dtypes

logger = logging.getLogger(__name__)


class DataLoader:
    """Efficient data loader for NYC Yellow Taxi Trip data"""
    
    def __init__(self, file_path: str):
        """
        Initialize DataLoader
        
        Args:
            file_path: Path to CSV file
        """
        self.file_path = file_path
        
    def load_data(self, nrows: Optional[int] = None) -> pd.DataFrame:
        """
        Load data with optimized dtypes to minimize memory usage
        
        Args:
            nrows: Number of rows to load (None for all)
            
        Returns:
            Loaded DataFrame
        """
        logger.info(f"Loading data from {self.file_path}...")
        
        # Define optimal dtypes for memory efficiency
        dtypes = {
            'VendorID': 'int8',
            'passenger_count': 'float32',
            'trip_distance': 'float32',
            'RatecodeID': 'float32',
            'store_and_fwd_flag': 'category',
            'PULocationID': 'int16',
            'DOLocationID': 'int16',
            'payment_type': 'int8',
            'fare_amount': 'float32',
            'extra': 'float32',
            'mta_tax': 'float32',
            'tip_amount': 'float32',
            'tolls_amount': 'float32',
            'improvement_surcharge': 'float32',
            'total_amount': 'float32',
            'congestion_surcharge': 'float32',
            'Airport_fee': 'float32',
            'cbd_congestion_fee': 'float32'
        }
        
        # Parse dates during loading
        parse_dates = ['tpep_pickup_datetime', 'tpep_dropoff_datetime']
        
        try:
            # Load data with optimized settings
            df = pd.read_csv(
                self.file_path,
                dtype=dtypes,
                parse_dates=parse_dates,
                nrows=nrows,
                low_memory=False
            )
            
            logger.info(f"Loaded {len(df):,} rows with {df.shape[1]} columns")
            logger.info(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def get_data_info(self, df: pd.DataFrame) -> dict:
        """
        Get basic information about the loaded data
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary with data information
        """
        info = {
            'total_rows': len(df),
            'total_columns': df.shape[1],
            'memory_mb': df.memory_usage(deep=True).sum() / 1024**2,
            'date_range': (df['tpep_pickup_datetime'].min(), 
                          df['tpep_pickup_datetime'].max()),
            'missing_values': df.isnull().sum().to_dict()
        }
        
        return info
