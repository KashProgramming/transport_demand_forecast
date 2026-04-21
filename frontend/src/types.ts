// API Response Types
export interface LoadSummary {
  records_loaded: number;
  date_range: {
    start: string;
    end: string;
  };
  summary_metrics: {
    total_trips: string;
    avg_hourly_demand: number;
    peak_demand: string;
    total_revenue: string;
  };
  config_hash: string;
  resolved_data_file: string;
}

export interface PlotlyFigure {
  data: any[];
  layout: any;
}

export interface EDAData {
  figures: {
    demand_over_time: PlotlyFigure;
    hourly_distribution: PlotlyFigure;
    weekday_comparison: PlotlyFigure;
    heatmap: PlotlyFigure;
  };
  peak_hours: Array<{
    Hour: string;
    'Average Demand': number;
  }>;
}

export interface TimeSeriesPoint {
  datetime: string;
  value: number;
}

export interface ForecastData {
  model_source: string;
  warnings: string[];
  selected_model: string;
  forecast_horizon: string;
  historical_last_week: Array<{
    datetime: string;
    demand: number;
  }>;
  multi_model_forecasts?: Record<string, TimeSeriesPoint[]>;
  forecast?: TimeSeriesPoint[];
  forecast_stats?: {
    avg_forecast_demand: number;
    peak_forecast_demand: number;
    min_forecast_demand: number;
  };
  figure?: PlotlyFigure;
  error?: string;
}

export interface ModelComparisonData {
  model_source: string;
  warnings: string[];
  comparison_table: Array<{
    model: string;
    RMSE: number;
    MAE: number;
    MAPE: number;
  }>;
  best_model: string;
  comparison_figure: PlotlyFigure;
  actual_series: TimeSeriesPoint[];
  predictions: Record<string, TimeSeriesPoint[]>;
  error?: string;
}

export interface SpatialData {
  top_zones: Array<{
    location_id: number;
    total_demand: number;
    avg_demand: number;
  }>;
  zone_heatmap: PlotlyFigure;
  available_locations: number[];
  selected_location?: number;
  zone_statistics?: {
    total_demand: string;
    avg_demand: number;
    max_demand: number;
    std_demand: number;
  };
  peak_hours_zone?: Array<{
    hour: number;
    demand: number;
  }>;
  compare_zones?: number[];
  comparison_figure?: PlotlyFigure;
  error?: string;
}

export interface DataInfo {
  data_summary: {
    total_records: number;
    date_range: {
      start: string;
      end: string;
    };
    total_hours: number;
    unique_locations: number;
  };
  demand_statistics: {
    mean: number;
    median: number;
    std: number;
    min: number;
    max: number;
  };
  revenue_statistics: {
    total_revenue: number;
    avg_hourly_revenue: number;
    max_hourly_revenue: number;
  };
  feature_engineering: {
    total_features: number;
    feature_names: string[];
    feature_types: string[];
  };
  sample_data: Array<{
    datetime: string;
    demand: number;
  }>;
}

// Request Types
export interface BaseAnalysisRequest {
  data_file: string;
  use_sample: boolean;
  sample_size?: number;
  force_retrain?: boolean;
}

export interface ForecastRequest extends BaseAnalysisRequest {
  selected_model: string;
  forecast_horizon: string;
}

export interface SpatialRequest extends BaseAnalysisRequest {
  analyze_location: boolean;
  selected_location?: number;
  compare_zones?: number[];
}

// UI State Types
export interface AppConfig {
  data_file: string;
  available_models: string[];
  forecast_horizons: Record<string, number>;
  default_model: string;
  default_forecast_horizon: string;
  sample_defaults: {
    enabled: boolean;
    default_size: number;
  };
}
