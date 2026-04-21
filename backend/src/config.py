"""
Configuration file for Smart Urban Transport Demand Forecasting System
Modify these settings to customize the application behavior
"""

# ============================================================================
# DATA CONFIGURATION
# ============================================================================

# Default data file path
DEFAULT_DATA_PATH = "data/yellow_tripdata_2025-01.csv"

# Sample data settings
DEFAULT_SAMPLE_SIZE = 100000
MIN_SAMPLE_SIZE = 10000
MAX_SAMPLE_SIZE = 1000000

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

# ARIMA parameters
ARIMA_ORDER = (5, 1, 2)

# SARIMA parameters
SARIMA_ORDER = (1, 1, 1)
SARIMA_SEASONAL_ORDER = (1, 1, 1, 24)  # 24-hour seasonality

# Prophet parameters
PROPHET_YEARLY_SEASONALITY = False
PROPHET_WEEKLY_SEASONALITY = True
PROPHET_DAILY_SEASONALITY = True
PROPHET_SEASONALITY_MODE = 'multiplicative'

# XGBoost parameters
XGBOOST_N_ESTIMATORS = 100
XGBOOST_MAX_DEPTH = 6
XGBOOST_LEARNING_RATE = 0.1

# ============================================================================
# FEATURE ENGINEERING CONFIGURATION
# ============================================================================

# Lag features (in hours)
LAG_FEATURES = [1, 24, 168]  # 1h, 1d, 1w

# Rolling window sizes (in hours)
ROLLING_WINDOWS = [3, 6, 24]  # 3h, 6h, 1d

# ============================================================================
# TRAIN-TEST SPLIT CONFIGURATION
# ============================================================================

# Train-test split ratio
TRAIN_TEST_SPLIT_RATIO = 0.8

# ============================================================================
# FORECASTING CONFIGURATION
# ============================================================================

# Available forecast horizons
FORECAST_HORIZONS = {
    "24 hours": 24,
    "7 days": 168,
    "14 days": 336,
    "30 days": 720
}

# Default forecast horizon
DEFAULT_FORECAST_HORIZON = "24 hours"

# ============================================================================
# SPATIAL ANALYSIS CONFIGURATION
# ============================================================================

# Number of top zones to display
DEFAULT_TOP_ZONES = 10
MAX_TOP_ZONES = 50

# Number of zones for heatmap
HEATMAP_TOP_ZONES = 20

# ============================================================================
# VISUALIZATION CONFIGURATION
# ============================================================================

# Plot colors
PLOT_COLORS = {
    'ARIMA': '#1f77b4',
    'SARIMA': '#ff7f0e',
    'Prophet': '#2ca02c',
    'XGBoost': '#d62728',
    'Actual': 'black',
    'Historical': 'black',
    'Forecast': '#ff7f0e'
}

# Plot dimensions
PLOT_HEIGHT = 500
HEATMAP_HEIGHT = 600

# ============================================================================
# DATA PREPROCESSING CONFIGURATION
# ============================================================================

# Anomaly detection thresholds
MIN_TRIP_DISTANCE = 0.0
MIN_FARE_AMOUNT = 0.0
MIN_PASSENGER_COUNT = 0
MAX_PASSENGER_COUNT = 10

# ============================================================================
# PERFORMANCE CONFIGURATION
# ============================================================================

# Enable Streamlit caching
ENABLE_CACHING = True

# Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = "INFO"

# Maximum model training iterations
MAX_ARIMA_ITERATIONS = 200
MAX_SARIMA_ITERATIONS = 200

# ============================================================================
# UI CONFIGURATION
# ============================================================================

# Page title and icon
PAGE_TITLE = "Smart Urban Transport Demand Forecasting"
PAGE_ICON = "🚕"

# Available models
AVAILABLE_MODELS = ["ARIMA", "SARIMA", "Prophet", "XGBoost", "All Models"]

# Default selected model
DEFAULT_MODEL = "All Models"

# ============================================================================
# ADVANCED SETTINGS
# ============================================================================

# Enable experimental features
ENABLE_REVENUE_FORECASTING = True
ENABLE_ZONE_FORECASTING = True
ENABLE_FEATURE_IMPORTANCE = True

# Parallel processing
USE_PARALLEL_PROCESSING = True
N_JOBS = -1  # -1 means use all available cores

# ============================================================================
# VALIDATION SETTINGS
# ============================================================================

# Minimum required data points for modeling
MIN_DATA_POINTS = 168  # 1 week of hourly data

# Minimum required data points for SARIMA
MIN_DATA_POINTS_SARIMA = 336  # 2 weeks for seasonal patterns

# ============================================================================
# EXPORT SETTINGS
# ============================================================================

# Enable data export
ENABLE_DATA_EXPORT = True

# Export formats
EXPORT_FORMATS = ["CSV", "Excel", "JSON"]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_model_params(model_name):
    """Get parameters for a specific model"""
    params = {
        'ARIMA': {
            'order': ARIMA_ORDER
        },
        'SARIMA': {
            'order': SARIMA_ORDER,
            'seasonal_order': SARIMA_SEASONAL_ORDER
        },
        'Prophet': {
            'yearly_seasonality': PROPHET_YEARLY_SEASONALITY,
            'weekly_seasonality': PROPHET_WEEKLY_SEASONALITY,
            'daily_seasonality': PROPHET_DAILY_SEASONALITY,
            'seasonality_mode': PROPHET_SEASONALITY_MODE
        },
        'XGBoost': {
            'n_estimators': XGBOOST_N_ESTIMATORS,
            'max_depth': XGBOOST_MAX_DEPTH,
            'learning_rate': XGBOOST_LEARNING_RATE
        }
    }
    return params.get(model_name, {})


def get_forecast_steps(horizon_name):
    """Get number of steps for a forecast horizon"""
    return FORECAST_HORIZONS.get(horizon_name, 24)


def validate_config():
    """Validate configuration settings"""
    assert TRAIN_TEST_SPLIT_RATIO > 0 and TRAIN_TEST_SPLIT_RATIO < 1, \
        "Train-test split ratio must be between 0 and 1"
    
    assert MIN_SAMPLE_SIZE < MAX_SAMPLE_SIZE, \
        "Min sample size must be less than max sample size"
    
    assert all(lag > 0 for lag in LAG_FEATURES), \
        "All lag features must be positive"
    
    assert all(window > 0 for window in ROLLING_WINDOWS), \
        "All rolling windows must be positive"
    
    return True


# Validate configuration on import
validate_config()
