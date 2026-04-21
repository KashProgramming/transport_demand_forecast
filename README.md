# 🚕 Smart Urban Transport Demand Forecasting System

A production-quality full-stack web application for NYC Yellow Taxi demand forecasting, featuring a FastAPI backend with ML models and a modern React frontend with interactive visualizations.

## 🎯 Project Overview

This system forecasts hourly taxi demand to:
- Identify peak congestion periods
- Optimize fleet allocation
- Generate actionable urban mobility insights
- Analyze spatial demand patterns across pickup zones

**Architecture**: RESTful API backend (FastAPI) + Interactive frontend (React + TypeScript)

## 📊 Features

### Data Processing
- **Efficient large-scale data handling** (~3.4M rows)
- Memory-optimized data types
- Robust preprocessing pipeline
- Anomaly detection and removal
- Configurable sampling for faster testing

### Time Series Analysis
- Hourly demand aggregation
- Trend and seasonality decomposition
- Stationarity testing (ADF test)
- Comprehensive EDA with interactive visualizations

### Forecasting Models
1. **ARIMA** - Baseline autoregressive model
2. **SARIMA** - Seasonal ARIMA with daily/weekly patterns
3. **Prophet** - Facebook's trend + seasonality model
4. **XGBoost** - Gradient boosting with engineered features

### Model Persistence
- **Automatic model saving** - Trained models are saved to disk
- **Smart model loading** - Reuses saved models when configuration matches
- **Configuration-based caching** - Models retrain only when data/parameters change
- **Force retrain option** - Manual model retraining on demand

### Spatial Analysis
- Top pickup zone identification
- Zone-level demand patterns
- Peak hour analysis per location
- Multi-zone comparison
- Interactive location selection

### Interactive Visualizations
- **Chart.js** powered interactive charts
- Real-time data updates
- Demand heatmaps (hour × day)
- Model comparison plots
- Forecast visualizations with historical context
- Responsive design for all screen sizes

### Modern UI/UX
- Clean, intuitive interface with warm color palette
- Card-based layouts with smooth transitions
- Real-time feedback and loading states
- Sidebar configuration panel
- Tab-based navigation
- Mobile-responsive design

## 🏗️ Project Structure

```
.
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
│
├── backend/                    # FastAPI backend
│   ├── main.py                # FastAPI application & routes
│   ├── service.py             # Business logic layer
│   ├── schemas.py             # Pydantic request/response models
│   │
│   ├── src/                   # Core backend modules
│   │   ├── config.py         # Configuration settings
│   │   │
│   │   ├── core/             # Core data processing
│   │   │   ├── data_loader.py    # Data loading with memory optimization
│   │   │   ├── preprocessing.py  # Data cleaning and preprocessing
│   │   │   └── aggregation.py    # Time series aggregation
│   │   │
│   │   ├── analysis/         # Analysis modules
│   │   │   ├── eda.py           # Exploratory data analysis
│   │   │   ├── features.py      # Feature engineering
│   │   │   └── spatial_analysis.py # Location-based analysis
│   │   │
│   │   ├── evaluation/       # Model evaluation
│   │   │   └── evaluation.py    # Model performance metrics
│   │   │
│   │   ├── management/       # Model management
│   │   │   └── model_manager.py # Model persistence & loading
│   │   │
│   │   └── utils/            # Utility functions
│   │       └── utils.py         # Helper functions
│   │
│   ├── models/               # ML models
│   │   ├── arima_model.py       # ARIMA forecaster
│   │   ├── sarima_model.py      # SARIMA forecaster
│   │   ├── prophet_model.py     # Prophet forecaster
│   │   └── xgboost_model.py     # XGBoost forecaster
│   │
│   ├── saved_models/         # Saved models (auto-generated)
│   │   └── metadata.json        # Model configuration tracking
│   │
│   ├── tests/                # Backend tests
│   │   └── test_api.py          # API endpoint tests
│   │
│   └── scripts/              # Utility scripts
│       └── debug_weekday.py     # Debug script for weekday analysis
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── main.tsx           # Application entry point
│   │   ├── App.tsx            # Main application component
│   │   ├── api.ts             # API client functions
│   │   ├── types.ts           # TypeScript type definitions
│   │   ├── index.css          # Global styles & Tailwind
│   │   │
│   │   ├── components/        # React components
│   │   │   ├── Header.tsx        # App header
│   │   │   ├── Sidebar.tsx       # Configuration sidebar
│   │   │   ├── MetricsCards.tsx  # Key metrics display
│   │   │   ├── TabNavigation.tsx # Tab switcher
│   │   │   ├── WelcomeScreen.tsx # Landing page
│   │   │   │
│   │   │   └── tabs/          # Tab components
│   │   │       ├── EDATab.tsx           # Exploratory Data Analysis
│   │   │       ├── ForecastingTab.tsx   # Demand Forecasting
│   │   │       ├── ModelComparisonTab.tsx # Model Performance
│   │   │       ├── SpatialTab.tsx       # Spatial Analysis
│   │   │       └── DataInfoTab.tsx      # Dataset Information
│   │   │
│   │   └── utils/             # Utility functions
│   │       └── chartUtils.ts     # Chart.js configurations
│   │
│   ├── public/                # Static assets
│   │   └── taxi.svg              # Favicon
│   │
│   ├── package.json           # Node.js dependencies
│   ├── tsconfig.json          # TypeScript configuration
│   ├── vite.config.ts         # Vite build configuration
│   ├── tailwind.config.js     # Tailwind CSS configuration
│   ├── README.md              # Frontend documentation
│   └── SETUP.md               # Frontend setup guide
│
└── data/                       # Data files
    └── yellow_tripdata_2025-01.csv
```

## 🚀 Installation

### Prerequisites
- **Python 3.8+** with pip
- **Node.js 18+** with npm
- 4GB+ RAM recommended for full dataset

### Quick Start

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd transport_forecast
```

#### 2. Backend Setup

**Install Python dependencies:**
```bash
pip install -r requirements.txt
```

**Start the FastAPI backend:**
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

#### 3. Frontend Setup

**Install Node.js dependencies:**
```bash
cd frontend
npm install
```

**Configure environment:**
```bash
cp .env.example .env
```

**Start the React development server:**
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

#### 4. Prepare Data
Place your NYC Yellow Taxi Trip CSV file in the `data/` folder:
- Default path: `data/yellow_tripdata_2025-01.csv`
- Or configure a custom path in the frontend sidebar

## 💻 Usage

### Accessing the Application

1. **Open your browser** to `http://localhost:3000`
2. **Configure settings** in the left sidebar:
   - Data file path
   - Sample data options (for faster testing)
   - Model selection
   - Forecast horizon (24 hours or 7 days)
   - Spatial analysis options
3. **Click "Load Data & Train Models"** to begin
4. **Explore the tabs**:
   - **EDA**: Demand patterns, hourly distributions, peak hours
   - **Forecasting**: Generate predictions with selected models
   - **Model Comparison**: Compare performance metrics
   - **Spatial Analysis**: Zone-level demand patterns
   - **Data Info**: Dataset statistics and sample data

### Configuration Options

**Data Options:**
- **Data File Path**: Specify CSV file location
- **Use Sample Data**: Enable for faster testing (10K-1M rows)
- **Sample Size**: Configurable sample size

**Model Selection:**
- ARIMA, SARIMA, Prophet, XGBoost, or All Models

**Forecast Settings:**
- **Forecast Horizon**: 24 hours or 7 days
- **Force Retrain**: Clear cached models and retrain

**Spatial Analysis:**
- **Analyze Specific Location**: Enable zone-specific analysis
- **Location Selection**: Choose from available zones
- **Zone Comparison**: Compare multiple zones

## 🔌 API Endpoints

### Backend API (FastAPI)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/options` | GET | Get configuration options |
| `/api/load` | POST | Load and preprocess data |
| `/api/eda` | POST | Get EDA visualizations |
| `/api/forecasting` | POST | Generate forecasts |
| `/api/model-comparison` | POST | Compare model performance |
| `/api/spatial` | POST | Get spatial analysis data |
| `/api/data-info` | POST | Get dataset information |

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/load" \
  -H "Content-Type: application/json" \
  -d '{
    "data_file": "data/yellow_tripdata_2025-01.csv",
    "use_sample": true,
    "sample_size": 100000
  }'
```

## 📈 Models & Methodology

### Data Preprocessing
- Remove invalid records (distance ≤ 0, fare ≤ 0, passengers ≤ 0 or > 10)
- Handle missing values
- Sort chronologically
- Memory optimization with dtype downcasting

### Feature Engineering
**Time-based features:**
- Hour, day of week, day of month, month
- Weekend flag
- Cyclical encoding (sin/cos for hour and day)

**Lag features:**
- demand(t-1), demand(t-24), demand(t-168)

**Rolling features:**
- Rolling mean and std (3h, 6h, 24h windows)

### Model Training
- **Train-test split**: 80-20 time-based split
- **Evaluation metrics**: RMSE, MAE, MAPE
- **Validation**: No data leakage, proper time series cross-validation
- **Model persistence**: Automatic saving and loading based on configuration hash

### Forecasting
- Multi-step ahead forecasting
- Recursive prediction for XGBoost
- Confidence intervals (where applicable)
- Non-negative constraint enforcement

## 📊 Performance Optimization

### Backend
- **Memory efficiency**: Optimized dtypes reduce memory by ~50%
- **Vectorized operations**: No row-by-row loops
- **Data caching**: In-memory caching for repeated requests
- **Model persistence**: Trained models saved to disk and reused
  - First run: ~2-5 minutes (training)
  - Subsequent runs: ~5-10 seconds (loading)
- **Batch processing**: Efficient aggregation with pandas groupby
- **Handles 3M+ rows** without performance issues

### Frontend
- **Code splitting**: Lazy loading of chart components
- **Efficient re-renders**: React hooks with proper dependencies
- **Tailwind CSS**: Purged unused styles in production
- **Vite optimization**: Fast HMR and optimized builds
- **Chart.js**: Hardware-accelerated canvas rendering

## 🛠️ Technology Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance REST API framework |
| **Pydantic** | Data validation and serialization |
| **Pandas** | Data manipulation and analysis |
| **NumPy** | Numerical computing |
| **Scikit-learn** | ML utilities and metrics |
| **Statsmodels** | ARIMA/SARIMA models |
| **Prophet** | Facebook's forecasting library |
| **XGBoost** | Gradient boosting |
| **Plotly** | Data visualization (converted to JSON) |
| **Uvicorn** | ASGI server |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18** | UI framework with hooks |
| **TypeScript** | Type safety and better DX |
| **Vite** | Fast build tool and dev server |
| **Chart.js** | Interactive chart library |
| **react-chartjs-2** | React wrapper for Chart.js |
| **Tailwind CSS** | Utility-first styling |
| **Axios** | HTTP client for API calls |
| **Lucide React** | Modern icon library |

## 🔍 Key Insights Generated

1. **Peak Hours**: Identify busiest hours for fleet allocation
2. **Demand Patterns**: Weekday vs weekend differences
3. **Seasonal Trends**: Daily and weekly seasonality
4. **Zone Hotspots**: Top pickup locations
5. **Revenue Forecasting**: Predict hourly revenue
6. **Model Performance**: Compare forecasting accuracy across models

## 📝 Dataset Schema

Expected CSV columns:
- `VendorID` (int)
- `tpep_pickup_datetime` (datetime)
- `tpep_dropoff_datetime` (datetime)
- `passenger_count` (float)
- `trip_distance` (float)
- `RatecodeID` (float)
- `store_and_fwd_flag` (object)
- `PULocationID` (int)
- `DOLocationID` (int)
- `payment_type` (int)
- `fare_amount` (float)
- `extra` (float)
- `mta_tax` (float)
- `tip_amount` (float)
- `tolls_amount` (float)
- `improvement_surcharge` (float)
- `total_amount` (float)
- `congestion_surcharge` (float)
- `Airport_fee` (float)
- `cbd_congestion_fee` (float)

## 🚢 Production Deployment

### Backend Deployment
```bash
# Install production dependencies
pip install -r requirements.txt

# Run with production server
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend Deployment
```bash
cd frontend

# Build for production
npm run build

# Serve the dist/ folder with any static file server
# Example with Python:
python -m http.server 3000 --directory dist

# Or with nginx, Apache, etc.
```

### Environment Variables
**Frontend (.env):**
```bash
VITE_API_URL=https://your-api-domain.com
```

## 🎓 Use Cases

- **Urban Planning**: Understand transportation demand patterns
- **Fleet Management**: Optimize taxi/rideshare allocation
- **Traffic Management**: Predict congestion hotspots
- **Business Intelligence**: Revenue forecasting and optimization
- **Research**: Time series analysis methodology
- **Smart Cities**: Data-driven transportation decisions

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request