"""
Feature engineering module for time series forecasting
"""
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Create features for time series forecasting models"""
    
    def __init__(self):
        self.feature_names = []
        
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create all features for time series forecasting
        
        Args:
            df: DataFrame with datetime index and demand column
            
        Returns:
            DataFrame with engineered features
        """
        logger.info("Creating features...")
        df = df.copy()
        
        # Time-based features
        df = self._create_time_features(df)
        
        # Adaptive lag features based on data size
        df = self._create_adaptive_lag_features(df)
        
        # Adaptive rolling features based on data size
        df = self._create_adaptive_rolling_features(df)
        
        # Drop rows with NaN (from lag/rolling features)
        initial_len = len(df)
        df = df.dropna()
        dropped = initial_len - len(df)
        
        if dropped > 0:
            logger.info(f"Dropped {dropped} rows with NaN values from feature creation")
        
        if len(df) == 0:
            logger.warning("All rows were dropped! Dataset may be too small for feature engineering.")
        else:
            logger.info(f"Created {len(self.feature_names)} features for {len(df)} samples")
        
        return df
    
    def _create_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create time-based features"""
        logger.info("Creating time-based features...")
        
        df['hour'] = df.index.hour
        df['day_of_week'] = df.index.dayofweek
        df['day_of_month'] = df.index.day
        df['month'] = df.index.month
        df['is_weekend'] = (df.index.dayofweek >= 5).astype(int)
        
        # Cyclical encoding for hour (24-hour cycle)
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        
        # Cyclical encoding for day of week (7-day cycle)
        df['dow_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['dow_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        time_features = ['hour', 'day_of_week', 'day_of_month', 'month', 'is_weekend',
                        'hour_sin', 'hour_cos', 'dow_sin', 'dow_cos']
        self.feature_names.extend(time_features)
        
        return df
    
    def _create_lag_features(self, df: pd.DataFrame, lags=[1, 24, 168]) -> pd.DataFrame:
        """
        Create lag features
        
        Args:
            df: Input DataFrame
            lags: List of lag periods (1=1h ago, 24=1d ago, 168=1w ago)
            
        Returns:
            DataFrame with lag features
        """
        logger.info(f"Creating lag features: {lags}...")
        
        for lag in lags:
            col_name = f'demand_lag_{lag}'
            df[col_name] = df['demand'].shift(lag)
            self.feature_names.append(col_name)
        
        return df
    
    def _create_adaptive_lag_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create lag features adaptively based on available data
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with lag features
        """
        data_len = len(df)
        
        # Define possible lags: 1h, 24h (1 day), 168h (1 week)
        possible_lags = [1, 24, 168]
        
        # Only use lags that are less than half the data length
        # This ensures we have enough data after creating lags
        lags = [lag for lag in possible_lags if lag < data_len / 2]
        
        if not lags:
            # If dataset is very small, use minimal lag
            lags = [1]
        
        logger.info(f"Creating adaptive lag features: {lags} (data length: {data_len})...")
        
        for lag in lags:
            col_name = f'demand_lag_{lag}'
            df[col_name] = df['demand'].shift(lag)
            self.feature_names.append(col_name)
        
        return df
    
    def _create_rolling_features(self, df: pd.DataFrame, windows=[3, 6, 24]) -> pd.DataFrame:
        """
        Create rolling window features
        
        Args:
            df: Input DataFrame
            windows: List of window sizes in hours
            
        Returns:
            DataFrame with rolling features
        """
        logger.info(f"Creating rolling features: {windows}...")
        
        for window in windows:
            # Rolling mean
            col_mean = f'demand_rolling_mean_{window}'
            df[col_mean] = df['demand'].shift(1).rolling(window=window).mean()
            self.feature_names.append(col_mean)
            
            # Rolling std
            col_std = f'demand_rolling_std_{window}'
            df[col_std] = df['demand'].shift(1).rolling(window=window).std()
            self.feature_names.append(col_std)
        
        return df
    
    def _create_adaptive_rolling_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create rolling window features adaptively based on available data
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with rolling features
        """
        data_len = len(df)
        
        # Define possible windows: 3h, 6h, 24h
        possible_windows = [3, 6, 24]
        
        # Only use windows that are less than 1/4 of the data length
        windows = [w for w in possible_windows if w < data_len / 4]
        
        if not windows:
            # If dataset is very small, use minimal window
            windows = [3] if data_len >= 6 else []
        
        if windows:
            logger.info(f"Creating adaptive rolling features: {windows} (data length: {data_len})...")
            
            for window in windows:
                # Rolling mean
                col_mean = f'demand_rolling_mean_{window}'
                df[col_mean] = df['demand'].shift(1).rolling(window=window).mean()
                self.feature_names.append(col_mean)
                
                # Rolling std
                col_std = f'demand_rolling_std_{window}'
                df[col_std] = df['demand'].shift(1).rolling(window=window).std()
                self.feature_names.append(col_std)
        else:
            logger.warning("Dataset too small for rolling features")
        
        return df
    
    def get_feature_importance_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare data for feature importance analysis
        
        Args:
            df: DataFrame with features
            
        Returns:
            X (features) and y (target) for modeling
        """
        # Exclude target and non-feature columns
        exclude_cols = ['demand']
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        X = df[feature_cols]
        y = df['demand']
        
        return X, y
