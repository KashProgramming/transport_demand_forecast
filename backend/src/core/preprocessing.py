"""
Data preprocessing module for cleaning and preparing taxi trip data
"""
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Preprocess NYC Yellow Taxi Trip data"""
    
    def __init__(self):
        self.removed_rows = {}
        
    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Complete preprocessing pipeline
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        logger.info("Starting data preprocessing...")
        initial_rows = len(df)
        
        # Convert datetime if not already done
        df = self._ensure_datetime(df)
        
        # Sort chronologically
        df = self._sort_chronologically(df)
        
        # Remove anomalies
        df = self._remove_anomalies(df)
        
        # Handle missing values
        df = self._handle_missing_values(df)
        
        # Keep only necessary columns
        df = self._select_columns(df)
        
        final_rows = len(df)
        logger.info(f"Preprocessing complete: {initial_rows:,} → {final_rows:,} rows "
                   f"({100 * (initial_rows - final_rows) / initial_rows:.2f}% removed)")
        
        return df
    
    def _ensure_datetime(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure datetime columns are properly formatted"""
        if not pd.api.types.is_datetime64_any_dtype(df['tpep_pickup_datetime']):
            df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
        if not pd.api.types.is_datetime64_any_dtype(df['tpep_dropoff_datetime']):
            df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])
        return df
    
    def _sort_chronologically(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sort data by pickup datetime"""
        logger.info("Sorting data chronologically...")
        df = df.sort_values('tpep_pickup_datetime').reset_index(drop=True)
        return df
    
    def _remove_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove anomalous records"""
        logger.info("Removing anomalies...")
        initial_len = len(df)
        
        # Remove invalid trip distances
        mask_distance = df['trip_distance'] > 0
        removed_distance = initial_len - mask_distance.sum()
        self.removed_rows['invalid_distance'] = removed_distance
        
        # Remove invalid fares
        mask_fare = df['fare_amount'] > 0
        removed_fare = initial_len - mask_fare.sum()
        self.removed_rows['invalid_fare'] = removed_fare
        
        # Remove invalid passenger counts
        mask_passengers = (df['passenger_count'] > 0) & (df['passenger_count'] <= 10)
        removed_passengers = initial_len - mask_passengers.sum()
        self.removed_rows['invalid_passengers'] = removed_passengers
        
        # Apply all filters
        df = df[mask_distance & mask_fare & mask_passengers].copy()
        
        logger.info(f"Removed {initial_len - len(df):,} anomalous rows")
        logger.info(f"  - Invalid distance: {removed_distance:,}")
        logger.info(f"  - Invalid fare: {removed_fare:,}")
        logger.info(f"  - Invalid passengers: {removed_passengers:,}")
        
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values appropriately"""
        logger.info("Handling missing values...")
        
        # Fill numeric columns with median
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isnull().any():
                median_val = df[col].median()
                df[col].fillna(median_val, inplace=True)
                logger.info(f"  - Filled {col} with median: {median_val:.2f}")
        
        # Drop rows with missing datetime
        df = df.dropna(subset=['tpep_pickup_datetime'])
        
        return df
    
    def _select_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Keep only necessary columns for modeling"""
        logger.info("Selecting necessary columns...")
        
        # Essential columns for time series analysis
        essential_cols = [
            'tpep_pickup_datetime',
            'PULocationID',
            'total_amount',
            'passenger_count',
            'trip_distance'
        ]
        
        # Keep only columns that exist in the dataframe
        cols_to_keep = [col for col in essential_cols if col in df.columns]
        df = df[cols_to_keep].copy()
        
        logger.info(f"Kept {len(cols_to_keep)} columns: {cols_to_keep}")
        
        return df
    
    def get_preprocessing_report(self) -> dict:
        """Get report of preprocessing operations"""
        return {
            'removed_rows': self.removed_rows,
            'total_removed': sum(self.removed_rows.values())
        }
