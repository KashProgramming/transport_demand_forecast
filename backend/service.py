"""Service layer that mirrors the Streamlit application's behavior."""
from __future__ import annotations

import json
import logging
import os
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

BACKEND_ROOT = Path(__file__).resolve().parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from models.arima_model import ARIMAForecaster
from models.prophet_model import ProphetForecaster
from models.sarima_model import SARIMAForecaster
from models.xgboost_model import XGBoostForecaster
from src.analysis.eda import TimeSeriesEDA
from src.analysis.features import FeatureEngineer
from src.analysis.spatial_analysis import SpatialAnalyzer
from src.core.aggregation import TimeSeriesAggregator
from src.core.data_loader import DataLoader
from src.core.preprocessing import DataPreprocessor
from src.evaluation.evaluation import ModelEvaluator
from src.management.model_manager import ModelManager
from src.utils.utils import format_large_number

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)


@dataclass
class PreparedData:
    """Precomputed data and derived artifacts for a request configuration."""

    request_key: str
    resolved_data_file: str
    sample_size: Optional[int]
    df_clean: pd.DataFrame
    hourly_demand: pd.DataFrame
    location_demand: pd.DataFrame
    hourly_revenue: pd.DataFrame
    eda: TimeSeriesEDA
    spatial_analyzer: SpatialAnalyzer
    feature_engineer: FeatureEngineer
    demand_with_features: pd.DataFrame
    X: pd.DataFrame
    y: pd.Series
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    train_data: pd.Series
    test_data: pd.Series
    split_idx: int
    model_config: Dict[str, Any]
    config_hash: str


@dataclass
class PreparedModels:
    """Trained or loaded models plus evaluation predictions."""

    models: Dict[str, Any]
    predictions: Dict[str, np.ndarray]
    source: str
    warnings: List[str]


class TransportForecastService:
    """Backend facade that reproduces the Streamlit app logic."""

    def __init__(self, project_root: Optional[Path] = None):
        self.backend_root = BACKEND_ROOT
        self.project_root = project_root or self.backend_root.parent
        self.saved_models_dir = self.backend_root / "saved_models"
        self.model_manager = ModelManager(models_dir=str(self.saved_models_dir))
        self._context_cache: Dict[str, PreparedData] = {}
        self._model_cache: Dict[str, PreparedModels] = {}

    def get_options(self) -> Dict[str, Any]:
        """Return UI-style options that mirror the Streamlit sidebar."""
        return {
            "data_file": "data/yellow_tripdata_2025-01_sample.csv",
            "available_models": ["ARIMA", "SARIMA", "Prophet", "XGBoost", "All Models"],
            "forecast_horizons": {
                "24 hours": 24,
                "7 days": 168,
            },
            "default_model": "All Models",
            "default_forecast_horizon": "24 hours",
            "sample_defaults": {
                "enabled": False,
                "default_size": 100000,
            },
        }

    def get_load_summary(
        self,
        data_file: str,
        use_sample: bool = False,
        sample_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Return the top-level post-load summary shown in Streamlit."""
        context = self.prepare_context(
            data_file=data_file,
            use_sample=use_sample,
            sample_size=sample_size,
        )

        return {
            "records_loaded": int(len(context.df_clean)),
            "date_range": {
                "start": context.hourly_demand.index.min().isoformat(),
                "end": context.hourly_demand.index.max().isoformat(),
            },
            "summary_metrics": {
                "total_trips": format_large_number(context.hourly_demand["demand"].sum()),
                "avg_hourly_demand": round(float(context.hourly_demand["demand"].mean())),
                "peak_demand": format_large_number(context.hourly_demand["demand"].max()),
                "total_revenue": f"${format_large_number(context.hourly_revenue['revenue'].sum())}",
            },
            "config_hash": context.config_hash,
            "resolved_data_file": context.resolved_data_file,
        }

    def get_eda_data(
        self,
        data_file: str,
        use_sample: bool = False,
        sample_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Return the EDA tab payload."""
        context = self.prepare_context(
            data_file=data_file,
            use_sample=use_sample,
            sample_size=sample_size,
        )

        peak_hours = context.eda.get_peak_hours(top_n=5)
        peak_df = pd.DataFrame(
            {
                "Hour": [f"{hour:02d}:00" for hour in peak_hours.index],
                "Average Demand": peak_hours.values.astype(int),
            }
        )

        return {
            "figures": {
                "demand_over_time": self._figure_to_json(context.eda.plot_demand_over_time(interactive=True)),
                "hourly_distribution": self._figure_to_json(context.eda.plot_hourly_distribution()),
                "weekday_comparison": self._figure_to_json(context.eda.plot_weekday_comparison()),
                "heatmap": self._figure_to_json(context.eda.plot_heatmap()),
            },
            "peak_hours": self._dataframe_to_records(peak_df),
        }

    def get_forecasting_data(
        self,
        data_file: str,
        use_sample: bool = False,
        sample_size: Optional[int] = None,
        selected_model: str = "All Models",
        forecast_horizon: str = "24 hours",
        force_retrain: bool = False,
    ) -> Dict[str, Any]:
        """Return the forecasting tab payload."""
        context = self.prepare_context(
            data_file=data_file,
            use_sample=use_sample,
            sample_size=sample_size,
        )
        prepared_models = self.prepare_models(context, force_retrain=force_retrain)

        forecast_steps = 24 if forecast_horizon == "24 hours" else 168
        last_week = context.hourly_demand.tail(168)
        last_date = context.hourly_demand.index[-1]
        future_dates = pd.date_range(
            start=last_date + pd.Timedelta(hours=1),
            periods=forecast_steps,
            freq="H",
        )

        response: Dict[str, Any] = {
            "model_source": prepared_models.source,
            "warnings": prepared_models.warnings,
            "selected_model": selected_model,
            "forecast_horizon": forecast_horizon,
            "historical_last_week": self._indexed_dataframe_to_records(
                last_week, index_name="datetime"
            ),
        }

        if selected_model == "All Models":
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=last_week.index,
                    y=last_week["demand"],
                    mode="lines",
                    name="Historical",
                    line=dict(color="black", width=2),
                )
            )

            colors = {
                "ARIMA": "#1f77b4",
                "SARIMA": "#ff7f0e",
                "Prophet": "#2ca02c",
                "XGBoost": "#d62728",
            }

            forecasts: Dict[str, List[Dict[str, Any]]] = {}
            for model_name, model in prepared_models.models.items():
                try:
                    if model_name == "XGBoost":
                        if len(context.X) == 0:
                            warning = f"Cannot forecast with {model_name}: no features available"
                            prepared_models.warnings.append(warning)
                            continue
                        last_features = context.X.tail(1)
                        forecast = model.recursive_forecast(last_features, forecast_steps)
                    else:
                        forecast = model.predict(forecast_steps)

                    fig.add_trace(
                        go.Scatter(
                            x=future_dates,
                            y=forecast,
                            mode="lines",
                            name=model_name,
                            line=dict(
                                color=colors.get(model_name, "#999"),
                                width=2,
                                dash="dash",
                            ),
                        )
                    )

                    forecasts[model_name] = self._series_points(future_dates, forecast)
                except Exception as exc:  # pragma: no cover - mirrors UI fallback path
                    prepared_models.warnings.append(
                        f"Forecast failed for {model_name}: {str(exc)}"
                    )

            fig.update_layout(
                title=f"Multi-Model Forecast: Next {forecast_horizon}",
                xaxis_title="Date",
                yaxis_title="Demand",
                hovermode="x unified",
                height=500,
            )

            response["multi_model_forecasts"] = forecasts
            response["figure"] = self._figure_to_json(fig)
            return response

        if selected_model not in prepared_models.models:
            return {
                **response,
                "error": f"Model '{selected_model}' is not available.",
            }

        model = prepared_models.models[selected_model]
        try:
            if selected_model == "XGBoost":
                if len(context.X) == 0:
                    return {
                        **response,
                        "error": "Cannot forecast with XGBoost: no features available. The dataset may be too small.",
                    }
                last_features = context.X.tail(1)
                forecast = model.recursive_forecast(last_features, forecast_steps)
            else:
                forecast = model.predict(forecast_steps)
        except Exception as exc:
            return {
                **response,
                "error": f"Forecast failed: {str(exc)}",
            }

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=last_week.index,
                y=last_week["demand"],
                mode="lines",
                name="Historical",
                line=dict(color="black", width=2),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=future_dates,
                y=forecast,
                mode="lines",
                name="Forecast",
                line=dict(color="#ff7f0e", width=2, dash="dash"),
            )
        )
        fig.update_layout(
            title=f"{selected_model} Forecast: Next {forecast_horizon}",
            xaxis_title="Date",
            yaxis_title="Demand",
            hovermode="x unified",
            height=500,
        )

        response["forecast"] = self._series_points(future_dates, forecast)
        response["forecast_stats"] = {
            "avg_forecast_demand": round(float(np.mean(forecast))),
            "peak_forecast_demand": round(float(np.max(forecast))),
            "min_forecast_demand": round(float(np.min(forecast))),
        }
        response["figure"] = self._figure_to_json(fig)
        return response

    def get_model_comparison_data(
        self,
        data_file: str,
        use_sample: bool = False,
        sample_size: Optional[int] = None,
        force_retrain: bool = False,
    ) -> Dict[str, Any]:
        """Return the model-comparison tab payload."""
        context = self.prepare_context(
            data_file=data_file,
            use_sample=use_sample,
            sample_size=sample_size,
        )
        prepared_models = self.prepare_models(context, force_retrain=force_retrain)

        if len(context.test_data) == 0:
            return {
                "error": "No test data available. The dataset may be too small.",
                "warnings": prepared_models.warnings,
            }

        if (not prepared_models.predictions) or all(
            len(prediction) == 0 for prediction in prepared_models.predictions.values()
        ):
            return {
                "error": "No predictions available. All models failed to train.",
                "warnings": prepared_models.warnings,
            }

        non_empty_predictions = [
            prediction
            for prediction in prepared_models.predictions.values()
            if len(prediction) > 0
        ]
        min_len = min(len(context.test_data), min(len(prediction) for prediction in non_empty_predictions))

        if min_len == 0:
            return {
                "error": "Cannot evaluate models: insufficient data for comparison.",
                "warnings": prepared_models.warnings,
            }

        y_true = context.test_data.values[:min_len]
        evaluator = ModelEvaluator()

        for model_name, y_pred in prepared_models.predictions.items():
            if len(y_pred) > 0:
                evaluator.evaluate_model(y_true, y_pred[:min_len], model_name)

        comparison_df = evaluator.get_comparison_table()
        if comparison_df.empty:
            return {
                "error": "No model evaluation results available.",
                "warnings": prepared_models.warnings,
            }

        comparison_df["RMSE"] = comparison_df["RMSE"].round(2)
        comparison_df["MAE"] = comparison_df["MAE"].round(2)
        comparison_df["MAPE"] = comparison_df["MAPE"].round(2)

        best_model = comparison_df.iloc[0]["model"]
        test_dates = context.hourly_demand.index[
            context.split_idx : context.split_idx + min_len
        ]
        aligned_predictions = {
            name: prediction[:min_len]
            for name, prediction in prepared_models.predictions.items()
            if len(prediction) > 0
        }
        comparison_fig = evaluator.plot_comparison(y_true, aligned_predictions, test_dates)

        return {
            "model_source": prepared_models.source,
            "warnings": prepared_models.warnings,
            "comparison_table": self._dataframe_to_records(comparison_df),
            "best_model": best_model,
            "comparison_figure": self._figure_to_json(comparison_fig),
            "actual_series": self._series_points(test_dates, y_true),
            "predictions": {
                name: self._series_points(test_dates, prediction)
                for name, prediction in aligned_predictions.items()
            },
        }

    def get_spatial_data(
        self,
        data_file: str,
        use_sample: bool = False,
        sample_size: Optional[int] = None,
        analyze_location: bool = False,
        selected_location: Optional[int] = None,
        compare_zones: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """Return the spatial-analysis tab payload."""
        context = self.prepare_context(
            data_file=data_file,
            use_sample=use_sample,
            sample_size=sample_size,
        )

        top_zones = context.spatial_analyzer.get_top_zones(top_n=10)
        zone_heatmap = context.spatial_analyzer.plot_zone_heatmap(top_n=20)
        available_locations = sorted(context.location_demand["location_id"].unique().tolist())

        response: Dict[str, Any] = {
            "top_zones": self._dataframe_to_records(top_zones),
            "zone_heatmap": self._figure_to_json(zone_heatmap),
            "available_locations": available_locations,
        }

        if not analyze_location:
            return response

        if not available_locations:
            response["error"] = "No locations are available for spatial analysis."
            return response

        location = selected_location if selected_location is not None else available_locations[0]
        zone_stats = context.spatial_analyzer.get_zone_statistics(location)
        peak_hours_zone = context.spatial_analyzer.analyze_zone_peak_hours(location)

        zones_to_compare = compare_zones
        if zones_to_compare is None:
            zones_to_compare = available_locations[:3]

        response["selected_location"] = int(location)
        response["zone_statistics"] = self._coerce_scalars(zone_stats)
        response["peak_hours_zone"] = self._dataframe_to_records(peak_hours_zone.head(10))
        response["compare_zones"] = zones_to_compare

        if zones_to_compare:
            response["comparison_figure"] = self._figure_to_json(
                context.spatial_analyzer.compare_zones(zones_to_compare)
            )

        return response

    def get_data_info(
        self,
        data_file: str,
        use_sample: bool = False,
        sample_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Return the dataset-info tab payload."""
        context = self.prepare_context(
            data_file=data_file,
            use_sample=use_sample,
            sample_size=sample_size,
        )
        stats = context.eda.get_summary_statistics()

        return {
            "data_summary": {
                "total_records": int(len(context.df_clean)),
                "date_range": {
                    "start": context.hourly_demand.index.min().date().isoformat(),
                    "end": context.hourly_demand.index.max().date().isoformat(),
                },
                "total_hours": int(len(context.hourly_demand)),
                "unique_locations": int(context.location_demand["location_id"].nunique()),
            },
            "demand_statistics": self._coerce_scalars(
                {
                    "mean": round(float(stats["mean"]), 2),
                    "median": round(float(stats["median"]), 2),
                    "std": round(float(stats["std"]), 2),
                    "min": round(float(stats["min"])),
                    "max": int(stats["max"]),
                }
            ),
            "revenue_statistics": {
                "total_revenue": round(float(context.hourly_revenue["revenue"].sum()), 2),
                "avg_hourly_revenue": round(float(context.hourly_revenue["revenue"].mean()), 2),
                "max_hourly_revenue": round(float(context.hourly_revenue["revenue"].max()), 2),
            },
            "feature_engineering": {
                "total_features": len(context.feature_engineer.feature_names),
                "feature_names": context.feature_engineer.feature_names,
                "feature_types": [
                    "Time-based features (9)",
                    "Lag features (adaptive from [1, 24, 168])",
                    "Rolling features (adaptive from [3, 6, 24])",
                ],
            },
            "sample_data": self._indexed_dataframe_to_records(
                context.hourly_demand.head(24), index_name="datetime"
            ),
        }

    def prepare_context(
        self,
        data_file: str,
        use_sample: bool = False,
        sample_size: Optional[int] = None,
    ) -> PreparedData:
        """Load, preprocess, and derive the same data artifacts as Streamlit."""
        effective_sample_size = sample_size if use_sample else None
        request_key = self._request_key(data_file, effective_sample_size)

        if request_key in self._context_cache:
            return self._context_cache[request_key]

        resolved_data_file = self._resolve_data_file(data_file)
        df_clean = self._load_and_preprocess_data(resolved_data_file, effective_sample_size)
        hourly_demand, location_demand, hourly_revenue = self._create_time_series(df_clean)

        eda = TimeSeriesEDA(hourly_demand)
        spatial_analyzer = SpatialAnalyzer(location_demand)
        feature_engineer = FeatureEngineer()
        demand_with_features = feature_engineer.create_features(hourly_demand)

        split_idx = int(len(hourly_demand) * 0.8)
        train_data = hourly_demand["demand"][:split_idx]
        test_data = hourly_demand["demand"][split_idx:]

        if len(demand_with_features) == 0:
            X = pd.DataFrame()
            y = pd.Series(dtype=float)
            X_train = pd.DataFrame()
            X_test = pd.DataFrame()
            y_train = pd.Series(dtype=float)
            y_test = pd.Series(dtype=float)
        else:
            X, y = feature_engineer.get_feature_importance_data(demand_with_features)
            if len(X) == 0:
                X_train = X
                X_test = X
                y_train = y
                y_test = y
            else:
                split_idx_features = int(len(X) * 0.8)
                X_train = X[:split_idx_features]
                X_test = X[split_idx_features : split_idx_features + len(test_data)]
                y_train = y[:split_idx_features]
                y_test = y[split_idx_features : split_idx_features + len(test_data)]

        # In production, we want to reuse models trained on larger datasets
        # Set USE_SAMPLE_IN_HASH=false in environment to allow this
        use_sample_in_hash = os.getenv('USE_SAMPLE_IN_HASH', 'true').lower() == 'true'
        model_config = self.model_manager.get_config_from_params(
            data_file, effective_sample_size, use_sample_in_hash=use_sample_in_hash
        )
        _, config_hash = self.model_manager.models_exist(model_config)

        prepared = PreparedData(
            request_key=request_key,
            resolved_data_file=resolved_data_file,
            sample_size=effective_sample_size,
            df_clean=df_clean,
            hourly_demand=hourly_demand,
            location_demand=location_demand,
            hourly_revenue=hourly_revenue,
            eda=eda,
            spatial_analyzer=spatial_analyzer,
            feature_engineer=feature_engineer,
            demand_with_features=demand_with_features,
            X=X,
            y=y,
            X_train=X_train,
            X_test=X_test,
            y_train=y_train,
            y_test=y_test,
            train_data=train_data,
            test_data=test_data,
            split_idx=split_idx,
            model_config=model_config,
            config_hash=config_hash,
        )
        self._context_cache[request_key] = prepared
        return prepared

    def prepare_models(
        self, context: PreparedData, force_retrain: bool = False
    ) -> PreparedModels:
        """Load or train models using the Streamlit app's exact logic."""
        if force_retrain:
            self._model_cache.pop(context.config_hash, None)
            self._delete_saved_model_files(context.config_hash)

        if context.config_hash in self._model_cache:
            return self._model_cache[context.config_hash]

        warnings_list: List[str] = []

        models_exist, _ = self.model_manager.models_exist(context.model_config)
        if models_exist:
            models = self.model_manager.load_models(context.model_config)
            if models:
                predictions = self._generate_predictions(
                    models, context.test_data, context.X_test
                )
                prepared = PreparedModels(
                    models=models,
                    predictions=predictions,
                    source="disk",
                    warnings=warnings_list,
                )
                self._model_cache[context.config_hash] = prepared
                return prepared

            warnings_list.append("Failed to load saved models, training new ones...")

        models, predictions = self._train_models(
            context.train_data,
            context.test_data,
            context.X_train,
            context.X_test,
            context.y_train,
            context.y_test,
            warnings_list,
        )

        try:
            self.model_manager.save_models(models, context.model_config)
            self.model_manager.clear_old_models(keep_latest=3)
        except Exception as exc:  # pragma: no cover - persistence is best-effort
            warnings_list.append(f"Models trained but failed to save: {exc}")

        prepared = PreparedModels(
            models=models,
            predictions=predictions,
            source="trained",
            warnings=warnings_list,
        )
        self._model_cache[context.config_hash] = prepared
        return prepared

    def _load_and_preprocess_data(
        self, file_path: str, sample_size: Optional[int] = None
    ) -> pd.DataFrame:
        """Mirror the Streamlit cached data-loading function."""
        loader = DataLoader(file_path)

        if sample_size:
            df = loader.load_data(nrows=min(sample_size * 3, 1_000_000))
            if len(df) > sample_size:
                df = (
                    df.sample(n=sample_size, random_state=42)
                    .sort_values("tpep_pickup_datetime")
                    .reset_index(drop=True)
                )
        else:
            df = loader.load_data(nrows=sample_size)

        preprocessor = DataPreprocessor()
        return preprocessor.preprocess(df)

    def _create_time_series(
        self, df_clean: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Mirror the Streamlit cached time-series creation function."""
        aggregator = TimeSeriesAggregator()
        hourly_demand = aggregator.create_hourly_demand(df_clean)
        location_demand = aggregator.create_location_demand(df_clean)
        hourly_revenue = aggregator.create_hourly_revenue(df_clean)
        return hourly_demand, location_demand, hourly_revenue

    def _train_models(
        self,
        train_data: pd.Series,
        test_data: pd.Series,
        X_train: pd.DataFrame,
        X_test: pd.DataFrame,
        y_train: pd.Series,
        y_test: pd.Series,
        warnings_list: List[str],
    ) -> Tuple[Dict[str, Any], Dict[str, np.ndarray]]:
        """Mirror the Streamlit train_models helper."""
        del y_test  # kept for parity with the original function signature

        models: Dict[str, Any] = {}
        predictions: Dict[str, np.ndarray] = {}

        try:
            arima = ARIMAForecaster(order=(5, 1, 2))
            arima.fit(train_data)
            predictions["ARIMA"] = arima.predict_in_sample(test_data)
            models["ARIMA"] = arima
        except Exception as exc:
            warnings_list.append(f"ARIMA training failed: {str(exc)}")
            predictions["ARIMA"] = np.zeros(len(test_data))

        try:
            sarima = SARIMAForecaster(order=(1, 1, 1), seasonal_order=(1, 1, 1, 24))
            sarima.fit(train_data)
            predictions["SARIMA"] = sarima.predict_in_sample(test_data)
            models["SARIMA"] = sarima
        except Exception as exc:
            warnings_list.append(f"SARIMA training failed: {str(exc)}")
            predictions["SARIMA"] = np.zeros(len(test_data))

        try:
            prophet = ProphetForecaster()
            prophet.fit(train_data)
            predictions["Prophet"] = prophet.predict_in_sample(test_data)
            models["Prophet"] = prophet
        except Exception as exc:
            warnings_list.append(f"Prophet training failed: {str(exc)}")
            predictions["Prophet"] = np.zeros(len(test_data))

        try:
            xgb_model = XGBoostForecaster(
                n_estimators=100, max_depth=6, learning_rate=0.1
            )
            xgb_model.fit(X_train, y_train)
            predictions["XGBoost"] = xgb_model.predict(X_test)
            models["XGBoost"] = xgb_model
        except Exception as exc:
            warnings_list.append(f"XGBoost training failed: {str(exc)}")
            predictions["XGBoost"] = np.zeros(len(test_data))

        return models, predictions

    def _generate_predictions(
        self,
        models: Dict[str, Any],
        test_data: pd.Series,
        X_test: pd.DataFrame,
    ) -> Dict[str, np.ndarray]:
        """Mirror the Streamlit generate_predictions helper."""
        predictions: Dict[str, np.ndarray] = {}

        for model_name, model in models.items():
            try:
                if model_name == "XGBoost":
                    predictions[model_name] = model.predict(X_test)
                else:
                    predictions[model_name] = model.predict_in_sample(test_data)
            except Exception as exc:
                logger.warning("Prediction failed for %s: %s", model_name, exc)
                predictions[model_name] = np.zeros(len(test_data))

        return predictions

    def _request_key(self, data_file: str, sample_size: Optional[int]) -> str:
        """Build a stable in-memory cache key."""
        return json.dumps(
            {"data_file": data_file, "sample_size": sample_size},
            sort_keys=True,
        )

    def _resolve_data_file(self, data_file: str) -> str:
        """Resolve relative data paths from the project root first."""
        candidate = Path(data_file)
        if candidate.is_absolute():
            return str(candidate)

        project_path = (self.project_root / candidate).resolve()
        if project_path.exists():
            return str(project_path)

        backend_path = (self.backend_root / candidate).resolve()
        return str(backend_path)

    def _delete_saved_model_files(self, config_hash: str) -> None:
        """Delete generated backend model artifacts for a specific config."""
        for path in [
            self.saved_models_dir / f"arima_{config_hash}.pkl",
            self.saved_models_dir / f"sarima_{config_hash}.pkl",
            self.saved_models_dir / f"xgboost_{config_hash}.pkl",
            self.saved_models_dir / f"prophet_{config_hash}.json",
        ]:
            if path.exists():
                path.unlink()

    def _figure_to_json(self, figure: go.Figure) -> Dict[str, Any]:
        """Convert a Plotly figure into plain JSON data."""
        return json.loads(pio.to_json(figure))

    def _indexed_dataframe_to_records(
        self, df: pd.DataFrame, index_name: str = "index"
    ) -> List[Dict[str, Any]]:
        """Serialize a DataFrame with its index preserved."""
        serialized = df.reset_index()
        serialized = serialized.rename(columns={serialized.columns[0]: index_name})
        return self._dataframe_to_records(serialized)

    def _dataframe_to_records(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Serialize a DataFrame into JSON-friendly records."""
        serialized = df.copy()
        for column in serialized.columns:
            if pd.api.types.is_datetime64_any_dtype(serialized[column]):
                serialized[column] = serialized[column].dt.strftime("%Y-%m-%dT%H:%M:%S")
            elif pd.api.types.is_integer_dtype(serialized[column]):
                serialized[column] = serialized[column].astype(int)
            elif pd.api.types.is_float_dtype(serialized[column]):
                serialized[column] = serialized[column].astype(float)

        records = serialized.to_dict(orient="records")
        return [self._coerce_scalars(record) for record in records]

    def _series_points(
        self, index: pd.Index, values: np.ndarray | pd.Series
    ) -> List[Dict[str, Any]]:
        """Serialize aligned time series into [{datetime, value}] points."""
        points: List[Dict[str, Any]] = []
        for timestamp, value in zip(index, values):
            if isinstance(timestamp, pd.Timestamp):
                ts_value = timestamp.isoformat()
            else:
                ts_value = str(timestamp)
            points.append({"datetime": ts_value, "value": float(value)})
        return points

    def _coerce_scalars(self, value: Any) -> Any:
        """Convert pandas/numpy scalar types into builtin Python types."""
        if isinstance(value, dict):
            return {key: self._coerce_scalars(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._coerce_scalars(item) for item in value]
        if isinstance(value, tuple):
            return [self._coerce_scalars(item) for item in value]
        if isinstance(value, np.integer):
            return int(value)
        if isinstance(value, np.floating):
            return float(value)
        if isinstance(value, np.bool_):
            return bool(value)
        if isinstance(value, pd.Timestamp):
            return value.isoformat()
        return value
