"""
Spatial analysis module for location-based demand insights
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import logging

logger = logging.getLogger(__name__)


class SpatialAnalyzer:
    """Analyze demand patterns across different pickup locations"""
    
    def __init__(self, location_demand_df: pd.DataFrame):
        """
        Initialize spatial analyzer
        
        Args:
            location_demand_df: DataFrame with datetime, location_id, demand
        """
        self.location_demand_df = location_demand_df.copy()
        
    def get_top_zones(self, top_n=10) -> pd.DataFrame:
        """
        Identify top pickup zones by total demand
        
        Args:
            top_n: Number of top zones to return
            
        Returns:
            DataFrame with top zones
        """
        logger.info(f"Identifying top {top_n} pickup zones...")
        
        zone_totals = self.location_demand_df.groupby('location_id')['demand'].sum()
        top_zones = zone_totals.sort_values(ascending=False).head(top_n)
        
        top_zones_df = pd.DataFrame({
            'location_id': top_zones.index,
            'total_demand': top_zones.values,
            'avg_demand': top_zones.values / self.location_demand_df['datetime'].nunique()
        })
        
        logger.info(f"Top zone: Location {top_zones_df.iloc[0]['location_id']} "
                   f"with {top_zones_df.iloc[0]['total_demand']:,.0f} trips")
        
        return top_zones_df
    
    def analyze_zone_peak_hours(self, location_id: int) -> pd.DataFrame:
        """
        Analyze peak hours for a specific zone
        
        Args:
            location_id: Location ID to analyze
            
        Returns:
            DataFrame with hourly demand pattern
        """
        logger.info(f"Analyzing peak hours for location {location_id}...")
        
        zone_data = self.location_demand_df[
            self.location_demand_df['location_id'] == location_id
        ].copy()
        
        zone_data['hour'] = pd.to_datetime(zone_data['datetime']).dt.hour
        hourly_pattern = zone_data.groupby('hour')['demand'].mean()
        
        peak_hours_df = pd.DataFrame({
            'hour': hourly_pattern.index,
            'demand': hourly_pattern.values
        }).sort_values('demand', ascending=False)
        
        return peak_hours_df
    
    def compare_zones(self, location_ids: list) -> go.Figure:
        """
        Compare demand patterns across multiple zones
        
        Args:
            location_ids: List of location IDs to compare
            
        Returns:
            Plotly figure
        """
        logger.info(f"Comparing {len(location_ids)} zones...")
        
        fig = go.Figure()
        
        for loc_id in location_ids:
            zone_data = self.location_demand_df[
                self.location_demand_df['location_id'] == loc_id
            ].copy()
            
            zone_data['hour'] = pd.to_datetime(zone_data['datetime']).dt.hour
            hourly_avg = zone_data.groupby('hour')['demand'].mean()
            
            fig.add_trace(go.Scatter(
                x=hourly_avg.index,
                y=hourly_avg.values,
                mode='lines+markers',
                name=f'Zone {loc_id}'
            ))
        
        fig.update_layout(
            title='Demand Pattern Comparison Across Zones',
            xaxis_title='Hour of Day',
            yaxis_title='Average Demand',
            hovermode='x unified',
            height=500
        )
        
        return fig
    
    def plot_zone_heatmap(self, top_n=20) -> go.Figure:
        """
        Create heatmap of demand by zone and hour
        
        Args:
            top_n: Number of top zones to include
            
        Returns:
            Plotly figure
        """
        logger.info(f"Creating zone heatmap for top {top_n} zones...")
        
        # Get top zones
        top_zones = self.get_top_zones(top_n)
        top_zone_ids = top_zones['location_id'].values
        
        # Filter data for top zones
        filtered_data = self.location_demand_df[
            self.location_demand_df['location_id'].isin(top_zone_ids)
        ].copy()
        
        # Add hour column
        filtered_data['hour'] = pd.to_datetime(filtered_data['datetime']).dt.hour
        
        # Create pivot table
        pivot_data = filtered_data.pivot_table(
            values='demand',
            index='location_id',
            columns='hour',
            aggfunc='mean'
        )
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_data.values,
            x=pivot_data.columns,
            y=pivot_data.index,
            colorscale='YlOrRd',
            colorbar=dict(title='Avg Demand')
        ))
        
        fig.update_layout(
            title=f'Demand Heatmap: Top {top_n} Zones by Hour',
            xaxis_title='Hour of Day',
            yaxis_title='Location ID',
            height=600
        )
        
        return fig
    
    def get_zone_statistics(self, location_id: int) -> dict:
        """
        Get detailed statistics for a specific zone
        
        Args:
            location_id: Location ID
            
        Returns:
            Dictionary with zone statistics
        """
        zone_data = self.location_demand_df[
            self.location_demand_df['location_id'] == location_id
        ]
        
        stats = {
            'location_id': location_id,
            'total_demand': zone_data['demand'].sum(),
            'avg_demand': zone_data['demand'].mean(),
            'max_demand': zone_data['demand'].max(),
            'std_demand': zone_data['demand'].std()
        }
        
        return stats
