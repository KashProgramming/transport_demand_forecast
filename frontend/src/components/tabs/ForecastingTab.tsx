import { useEffect, useState } from 'react';
import { Loader2, AlertCircle, TrendingUp, Activity, TrendingDown } from 'lucide-react';
import { getForecasting } from '../../api';
import type { BaseAnalysisRequest, ForecastData } from '../../types';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { lineChartOptions, colorPalette, formatDateTime } from '../../utils/chartUtils';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface ForecastingTabProps {
  request: BaseAnalysisRequest;
  selectedModel: string;
  forecastHorizon: string;
}

export default function ForecastingTab({ request, selectedModel, forecastHorizon }: ForecastingTabProps) {
  const [data, setData] = useState<ForecastData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const result = await getForecasting({
          ...request,
          selected_model: selectedModel,
          forecast_horizon: forecastHorizon,
        });
        setData(result);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load forecasting data');
        console.error('Forecasting error:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [request, selectedModel, forecastHorizon]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-primary-600 mx-auto mb-4" />
          <p className="text-neutral-600">Training models and generating forecasts...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="card bg-red-50 border-red-200">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-red-900 mb-1">Error Loading Forecast Data</h3>
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (data.error) {
    return (
      <div className="card bg-amber-50 border-amber-200">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-amber-900 mb-1">Forecast Error</h3>
            <p className="text-amber-700 text-sm">{data.error}</p>
          </div>
        </div>
      </div>
    );
  }

  // Prepare chart data
  let chartData;
  
  if (selectedModel === 'All Models' && data.multi_model_forecasts) {
    const historicalLabels = data.historical_last_week.map(d => formatDateTime(d.datetime));
    const historicalData = data.historical_last_week.map(d => d.demand);
    
    const datasets = [
      {
        label: 'Historical',
        data: historicalData,
        borderColor: '#000',
        backgroundColor: 'rgba(0, 0, 0, 0.1)',
        borderWidth: 2,
        fill: false,
        tension: 0.4,
      },
    ];

    // Add forecast datasets for each model
    Object.entries(data.multi_model_forecasts).forEach(([modelName, forecast]) => {
      datasets.push({
        label: modelName,
        data: [...Array(historicalData.length).fill(null), ...forecast.map(f => f.value)] as any,
        borderColor: colorPalette.models[modelName as keyof typeof colorPalette.models] || '#999',
        backgroundColor: 'transparent',
        borderWidth: 2,
        borderDash: [5, 5] as any,
        fill: false,
        tension: 0.4,
      } as any);
    });

    const forecastLabels = Object.values(data.multi_model_forecasts)[0]?.map(f => formatDateTime(f.datetime)) || [];
    
    chartData = {
      labels: [...historicalLabels, ...forecastLabels],
      datasets,
    };
  } else if (data.forecast) {
    const historicalLabels = data.historical_last_week.map(d => formatDateTime(d.datetime));
    const historicalData = data.historical_last_week.map(d => d.demand);
    const forecastLabels = data.forecast.map(f => formatDateTime(f.datetime));
    const forecastData = data.forecast.map(f => f.value);

    chartData = {
      labels: [...historicalLabels, ...forecastLabels],
      datasets: [
        {
          label: 'Historical',
          data: historicalData,
          borderColor: '#000',
          backgroundColor: 'rgba(0, 0, 0, 0.1)',
          borderWidth: 2,
          fill: false,
          tension: 0.4,
        },
        {
          label: 'Forecast',
          data: [...Array(historicalData.length).fill(null), ...forecastData] as any,
          borderColor: colorPalette.primary,
          backgroundColor: 'transparent',
          borderWidth: 2,
          borderDash: [5, 5] as any,
          fill: false,
          tension: 0.4,
        } as any,
      ],
    };
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-neutral-900">Demand Forecasting</h2>
        {data.model_source && (
          <span className="px-3 py-1 bg-accent-100 text-accent-700 rounded-full text-sm font-medium">
            Models: {data.model_source}
          </span>
        )}
      </div>

      {/* Warnings */}
      {data.warnings && data.warnings.length > 0 && (
        <div className="card bg-amber-50 border-amber-200">
          <h3 className="font-semibold text-amber-900 mb-2">Warnings</h3>
          <ul className="space-y-1">
            {data.warnings.map((warning, idx) => (
              <li key={idx} className="text-amber-700 text-sm">• {warning}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Forecast Chart */}
      {chartData && (
        <div className="card">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">
            {selectedModel === 'All Models' 
              ? `Multi-Model Forecast: Next ${forecastHorizon}`
              : `${selectedModel} Forecast: Next ${forecastHorizon}`
            }
          </h3>
          <div className="h-96">
            <Line data={chartData} options={lineChartOptions} />
          </div>
        </div>
      )}

      {/* Forecast Statistics */}
      {data.forecast_stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card bg-gradient-to-br from-primary-50 to-white">
            <div className="flex items-center gap-3 mb-2">
              <div className="bg-primary-100 p-2 rounded-lg">
                <Activity className="w-5 h-5 text-primary-700" />
              </div>
              <h3 className="font-semibold text-neutral-700">Avg Forecast Demand</h3>
            </div>
            <p className="text-3xl font-bold text-neutral-900">
              {data.forecast_stats.avg_forecast_demand.toLocaleString()}
            </p>
          </div>

          <div className="card bg-gradient-to-br from-accent-50 to-white">
            <div className="flex items-center gap-3 mb-2">
              <div className="bg-accent-100 p-2 rounded-lg">
                <TrendingUp className="w-5 h-5 text-accent-700" />
              </div>
              <h3 className="font-semibold text-neutral-700">Peak Forecast Demand</h3>
            </div>
            <p className="text-3xl font-bold text-neutral-900">
              {data.forecast_stats.peak_forecast_demand.toLocaleString()}
            </p>
          </div>

          <div className="card bg-gradient-to-br from-amber-50 to-white">
            <div className="flex items-center gap-3 mb-2">
              <div className="bg-amber-100 p-2 rounded-lg">
                <TrendingDown className="w-5 h-5 text-amber-700" />
              </div>
              <h3 className="font-semibold text-neutral-700">Min Forecast Demand</h3>
            </div>
            <p className="text-3xl font-bold text-neutral-900">
              {data.forecast_stats.min_forecast_demand.toLocaleString()}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
