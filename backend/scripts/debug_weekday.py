"""Debug script to test weekday vs weekend plot"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from src.core.data_loader import DataLoader
from src.core.preprocessing import DataPreprocessor
from src.core.aggregation import TimeSeriesAggregator
from src.analysis.eda import TimeSeriesEDA

# Load data
print("Loading data...")
loader = DataLoader('data/yellow_tripdata_2025-01.csv')
df = loader.load_data()
# Sample if needed
if len(df) > 100000:
    df = df.sample(n=100000, random_state=42)

# Preprocess
print("Preprocessing...")
preprocessor = DataPreprocessor()
df_clean = preprocessor.preprocess(df)

# Aggregate
print("Aggregating...")
aggregator = TimeSeriesAggregator()
hourly_demand = aggregator.create_hourly_demand(df_clean)

print(f"\nHourly demand shape: {hourly_demand.shape}")
print(f"Date range: {hourly_demand.index.min()} to {hourly_demand.index.max()}")

# Create EDA
print("\nCreating EDA...")
eda = TimeSeriesEDA(hourly_demand)

# Check weekday/weekend split
print(f"\nWeekday hours: {(~eda.demand_df['is_weekend']).sum()}")
print(f"Weekend hours: {(eda.demand_df['is_weekend']).sum()}")

# Calculate averages
weekday_avg = eda.demand_df[~eda.demand_df['is_weekend']].groupby('hour')['demand'].mean()
weekend_avg = eda.demand_df[eda.demand_df['is_weekend']].groupby('hour')['demand'].mean()

print(f"\nWeekday avg hours with data: {len(weekday_avg)}")
print(f"Weekend avg hours with data: {len(weekend_avg)}")

print("\nWeekday averages:")
print(weekday_avg)

print("\nWeekend averages:")
print(weekend_avg)

# Generate plot
print("\nGenerating plot...")
fig = eda.plot_weekday_comparison()
print(f"Number of traces in figure: {len(fig.data)}")
for i, trace in enumerate(fig.data):
    print(f"Trace {i}: {trace.name}, points: {len(trace.x)}")
