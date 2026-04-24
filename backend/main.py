"""FastAPI application for the transport forecasting backend."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

BACKEND_ROOT = Path(__file__).resolve().parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from schemas import BaseAnalysisRequest, ForecastRequest, SpatialRequest
from service import TransportForecastService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Suppress verbose Prophet/CmdStan logging
logging.getLogger('prophet').setLevel(logging.ERROR)
logging.getLogger('cmdstanpy').setLevel(logging.ERROR)
logging.getLogger('stan').setLevel(logging.ERROR)

app = FastAPI(
    title="Smart Urban Transport Demand Forecasting API",
    version="1.0.0",
    description="FastAPI backend that reproduces the existing Streamlit app's functionality.",
)

# CORS Configuration
# Update the allow_origins list with your actual Vercel deployment URL
ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Local development
    "http://localhost:3000",  # Alternative local port
    "https://transport-demand-forecasting.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=r"https://.*\.vercel\.app",
)

service = TransportForecastService()


@app.get("/health")
def health() -> dict:
    """Basic health check."""
    return {"status": "ok"}


@app.get("/api/options")
def get_options() -> dict:
    """Expose frontend configuration options."""
    return service.get_options()


@app.post("/api/load")
def load_data(request: BaseAnalysisRequest) -> dict:
    """Load and preprocess the dataset, mirroring the Streamlit summary state."""
    return service.get_load_summary(
        data_file=request.data_file,
        use_sample=request.use_sample,
        sample_size=request.sample_size,
    )


@app.post("/api/eda")
def get_eda(request: BaseAnalysisRequest) -> dict:
    """Return EDA charts and tables."""
    return service.get_eda_data(
        data_file=request.data_file,
        use_sample=request.use_sample,
        sample_size=request.sample_size,
    )


@app.post("/api/forecasting")
def get_forecasting(request: ForecastRequest) -> dict:
    """Return model forecasts and plotting payloads."""
    return service.get_forecasting_data(
        data_file=request.data_file,
        use_sample=request.use_sample,
        sample_size=request.sample_size,
        selected_model=request.selected_model,
        forecast_horizon=request.forecast_horizon,
        force_retrain=request.force_retrain,
    )


@app.post("/api/model-comparison")
def get_model_comparison(request: BaseAnalysisRequest) -> dict:
    """Return model-comparison metrics and aligned prediction data."""
    return service.get_model_comparison_data(
        data_file=request.data_file,
        use_sample=request.use_sample,
        sample_size=request.sample_size,
        force_retrain=request.force_retrain,
    )


@app.post("/api/spatial")
def get_spatial(request: SpatialRequest) -> dict:
    """Return spatial-analysis data and optional zone-specific details."""
    return service.get_spatial_data(
        data_file=request.data_file,
        use_sample=request.use_sample,
        sample_size=request.sample_size,
        analyze_location=request.analyze_location,
        selected_location=request.selected_location,
        compare_zones=request.compare_zones,
    )


@app.post("/api/data-info")
def get_data_info(request: BaseAnalysisRequest) -> dict:
    """Return dataset-summary payloads."""
    return service.get_data_info(
        data_file=request.data_file,
        use_sample=request.use_sample,
        sample_size=request.sample_size,
    )
