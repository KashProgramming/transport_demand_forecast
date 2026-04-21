"""Pydantic schemas for the FastAPI backend."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class BaseAnalysisRequest(BaseModel):
    """Shared request fields across analysis endpoints."""

    data_file: str = "data/yellow_tripdata_2025-01.csv"
    use_sample: bool = False
    sample_size: Optional[int] = Field(default=None, ge=1)
    force_retrain: bool = False

    @model_validator(mode="after")
    def normalize_sample_size(self) -> "BaseAnalysisRequest":
        """Ignore sample size unless sample mode is enabled."""
        if not self.use_sample:
            self.sample_size = None
        return self


class ForecastRequest(BaseAnalysisRequest):
    """Forecast endpoint request."""

    selected_model: str = "All Models"
    forecast_horizon: str = "24 hours"


class SpatialRequest(BaseAnalysisRequest):
    """Spatial analysis endpoint request."""

    analyze_location: bool = False
    selected_location: Optional[int] = None
    compare_zones: Optional[List[int]] = None
