"""
Time series aggregation module for creating hourly demand data
"""
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class TimeSeriesAggregator:
    """Aggregate taxi trip data into time series format"""
    
    def __init__(self):
        self.aggregated_data = {}
        
    def create_hourly_demand(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate trips per hour to create demand time series
        
        Args:
            df: Preprocessed DataFrame with tpep_pickup_datetime
            
        Returns:
            DataFrame with hourly demand (datetime index, demand column)
        """
        logger.info("Creating hourly demand time series...")
        
        # Set datetime as index and resample to hourly frequency
        df_indexed = df.set_index('tpep_pickup_datetime')
        hourly_demand = df_indexed.resample('H').size()
        
        # Convert to DataFrame
        demand_df = pd.DataFrame({
            'demand': hourly_demand
        })
        
        # Fill missing timestamps with 0
        demand_df = self._fill_missing_hours(demand_df)
        
        logger.info(f"Created hourly demand series: {len(demand_df):,} hours")
        logger.info(f"Date range: {demand_df.index.min()} to {demand_df.index.max()}")
        logger.info(f"Mean demand: {demand_df['demand'].mean():.2f} trips/hour")
        logger.info(f"Max demand: {demand_df['demand'].max():,} trips/hour")
        
        self.aggregated_data['hourly_demand'] = demand_df
        
        return demand_df
    
    def create_location_demand(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate demand per pickup location and hour
        
        Args:
            df: Preprocessed DataFrame
            
        Returns:
            DataFrame with location-level hourly demand
        """
        logger.info("Creating location-level demand time series...")
        
        # Group by location and hour
        df_indexed = df.set_index('tpep_pickup_datetime')
        location_demand = df_indexed.groupby([
            pd.Grouper(freq='H'),
            'PULocationID'
        ]).size().reset_index(name='demand')
        
        location_demand.columns = ['datetime', 'location_id', 'demand']
        
        logger.info(f"Created location demand: {len(location_demand):,} records")
        logger.info(f"Unique locations: {location_demand['location_id'].nunique()}")
        
        self.aggregated_data['location_demand'] = location_demand
        
        return location_demand
    
    def create_hourly_revenue(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate hourly revenue
        
        Args:
            df: Preprocessed DataFrame with total_amount
            
        Returns:
            DataFrame with hourly revenue
        """
        logger.info("Creating hourly revenue time series...")
        
        # Set datetime as index and resample to hourly frequency
        df_indexed = df.set_index('tpep_pickup_datetime')
        hourly_revenue = df_indexed['total_amount'].resample('H').sum()
        
        # Convert to DataFrame
        revenue_df = pd.DataFrame({
            'revenue': hourly_revenue
        })
        
        # Fill missing timestamps with 0
        revenue_df = self._fill_missing_hours(revenue_df)
        
        logger.info(f"Created hourly revenue series: {len(revenue_df):,} hours")
        logger.info(f"Total revenue: ${revenue_df['revenue'].sum():,.2f}")
        logger.info(f"Mean hourly revenue: ${revenue_df['revenue'].mean():,.2f}")
        
        self.aggregated_data['hourly_revenue'] = revenue_df
        
        return revenue_df
    
    def _fill_missing_hours(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create continuous hourly index, filling missing timestamps with 0
        
        Args:
            df: DataFrame with datetime index
            
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
    
    def get_aggregation_summary(self) -> dict:
        """Get summary of aggregated data"""
        summary = {}
        
        for key, df in self.aggregated_data.items():
            if isinstance(df, pd.DataFrame):
                summary[key] = {
                    'records': len(df),
                    'date_range': (df.index.min() if hasattr(df, 'index') else None,
                                  df.index.max() if hasattr(df, 'index') else None)
                }
        
        return summary
