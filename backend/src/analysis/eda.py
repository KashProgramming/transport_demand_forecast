"""
Exploratory Data Analysis module for time series visualization
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import logging

logger = logging.getLogger(__name__)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


class TimeSeriesEDA:
    """Exploratory Data Analysis for time series demand data"""
    
    def __init__(self, demand_df: pd.DataFrame):
        """
        Initialize EDA with demand data
        
        Args:
            demand_df: DataFrame with datetime index and demand column
        """
        self.demand_df = demand_df.copy()
        self._add_time_features()
        
    def _add_time_features(self):
        """Add time-based features for analysis"""
        self.demand_df['hour'] = self.demand_df.index.hour
        self.demand_df['day_of_week'] = self.demand_df.index.dayofweek
        self.demand_df['day_name'] = self.demand_df.index.day_name()
        self.demand_df['date'] = self.demand_df.index.date
        self.demand_df['is_weekend'] = self.demand_df['day_of_week'].isin([5, 6])
        
    def plot_demand_over_time(self, interactive=True):
        """
        Plot hourly demand over time
        
        Args:
            interactive: Use plotly (True) or matplotlib (False)
            
        Returns:
            Plotly figure or None
        """
        logger.info("Plotting demand over time...")
        
        if interactive:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=self.demand_df.index,
                y=self.demand_df['demand'],
                mode='lines',
                name='Hourly Demand',
                line=dict(color='#1f77b4', width=1)
            ))
            
            fig.update_layout(
                title='Hourly Taxi Demand Over Time',
                xaxis_title='Date',
                yaxis_title='Number of Trips',
                hovermode='x unified',
                height=500
            )
            
            return fig
        else:
            fig, ax = plt.subplots(figsize=(14, 6))
            ax.plot(self.demand_df.index, self.demand_df['demand'], linewidth=0.8)
            ax.set_title('Hourly Taxi Demand Over Time', fontsize=14, fontweight='bold')
            ax.set_xlabel('Date')
            ax.set_ylabel('Number of Trips')
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            return fig
    
    def plot_hourly_distribution(self):
        """Plot demand distribution by hour of day"""
        logger.info("Plotting hourly distribution...")
        
        hourly_avg = self.demand_df.groupby('hour')['demand'].mean()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=hourly_avg.index,
            y=hourly_avg.values,
            marker_color='#2ca02c',
            name='Average Demand'
        ))
        
        fig.update_layout(
            title='Average Demand by Hour of Day',
            xaxis_title='Hour of Day',
            yaxis_title='Average Number of Trips',
            xaxis=dict(tickmode='linear', tick0=0, dtick=1),
            height=400
        )
        
        return fig
    
    def plot_weekday_comparison(self):
        """Plot weekday vs weekend demand comparison"""
        logger.info("Plotting weekday vs weekend comparison...")
        
        # Calculate averages
        weekday_data = self.demand_df[~self.demand_df['is_weekend']]
        weekend_data = self.demand_df[self.demand_df['is_weekend']]
        
        logger.info(f"Weekday records: {len(weekday_data)}, Weekend records: {len(weekend_data)}")
        
        weekday_avg = weekday_data.groupby('hour')['demand'].mean().reset_index()
        weekend_avg = weekend_data.groupby('hour')['demand'].mean().reset_index()
        
        logger.info(f"Weekday hours: {len(weekday_avg)}, Weekend hours: {len(weekend_avg)}")
        
        # Create figure with both traces
        fig = go.Figure()
        
        # Weekday trace
        fig.add_trace(go.Scatter(
            x=weekday_avg['hour'],
            y=weekday_avg['demand'],
            mode='lines+markers',
            name='Weekday',
            line=dict(color='blue', width=3),
            marker=dict(size=10, color='blue'),
            legendgroup='weekday',
            showlegend=True
        ))
        
        # Weekend trace  
        fig.add_trace(go.Scatter(
            x=weekend_avg['hour'],
            y=weekend_avg['demand'],
            mode='lines+markers',
            name='Weekend',
            line=dict(color='red', width=3, dash='dash'),
            marker=dict(size=10, color='red', symbol='square'),
            legendgroup='weekend',
            showlegend=True
        ))
        
        fig.update_layout(
            title='Weekday vs Weekend Demand Pattern',
            xaxis_title='Hour of Day',
            yaxis_title='Average Number of Trips',
            xaxis=dict(
                tickmode='linear',
                tick0=0,
                dtick=2,
                range=[-0.5, 23.5]
            ),
            yaxis=dict(rangemode='tozero'),
            height=450,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode='x unified'
        )
        
        logger.info(f"Created figure with {len(fig.data)} traces")
        for i, trace in enumerate(fig.data):
            logger.info(f"  Trace {i}: {trace.name}, {len(trace.x)} points")
        
        return fig
    
    def plot_heatmap(self):
        """Plot heatmap of demand by hour and day of week"""
        logger.info("Plotting demand heatmap...")
        
        # Create pivot table
        pivot_data = self.demand_df.pivot_table(
            values='demand',
            index='hour',
            columns='day_of_week',
            aggfunc='mean'
        )
        
        # Rename columns to day names (only for days that exist in the data)
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        pivot_data.columns = [day_names[int(col)] for col in pivot_data.columns]
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_data.values,
            x=pivot_data.columns,
            y=pivot_data.index,
            colorscale='YlOrRd',
            colorbar=dict(title='Avg Trips')
        ))
        
        fig.update_layout(
            title='Demand Heatmap: Hour vs Day of Week',
            xaxis_title='Day of Week',
            yaxis_title='Hour of Day',
            height=600
        )
        
        return fig
    
    def get_peak_hours(self, top_n=5):
        """
        Identify peak demand hours
        
        Args:
            top_n: Number of top hours to return
            
        Returns:
            DataFrame with peak hours
        """
        hourly_avg = self.demand_df.groupby('hour')['demand'].mean().sort_values(ascending=False)
        peak_hours = hourly_avg.head(top_n)
        
        logger.info(f"Top {top_n} peak hours:")
        for hour, demand in peak_hours.items():
            logger.info(f"  - Hour {hour:02d}:00: {demand:.0f} trips")
        
        return peak_hours
    
    def get_summary_statistics(self):
        """Get summary statistics of demand"""
        stats = {
            'mean': self.demand_df['demand'].mean(),
            'median': self.demand_df['demand'].median(),
            'std': self.demand_df['demand'].std(),
            'min': self.demand_df['demand'].min(),
            'max': self.demand_df['demand'].max(),
            'total_trips': self.demand_df['demand'].sum()
        }
        
        return stats
