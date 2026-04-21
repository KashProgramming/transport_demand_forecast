import { useEffect, useState } from 'react';
import { Loader2, AlertCircle, Award } from 'lucide-react';
import { getModelComparison } from '../../api';
import type { BaseAnalysisRequest, ModelComparisonData } from '../../types';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
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
  Legend
);

interface ModelComparisonTabProps {
  request: BaseAnalysisRequest;
}

export default function ModelComparisonTab({ request }: ModelComparisonTabProps) {
  const [data, setData] = useState<ModelComparisonData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const result = await getModelComparison(request);
        setData(result);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load model comparison data');
        console.error('Model comparison error:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [request]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-primary-600 mx-auto mb-4" />
          <p className="text-neutral-600">Evaluating model performance...</p>
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
            <h3 className="font-semibold text-red-900 mb-1">Error Loading Comparison Data</h3>
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
            <h3 className="font-semibold text-amber-900 mb-1">Comparison Error</h3>
            <p className="text-amber-700 text-sm">{data.error}</p>
          </div>
        </div>
      </div>
    );
  }

  // Prepare comparison chart
  const labels = data.actual_series.map(d => formatDateTime(d.datetime));
  const datasets = [
    {
      label: 'Actual',
      data: data.actual_series.map(d => d.value),
      borderColor: '#000',
      backgroundColor: 'rgba(0, 0, 0, 0.1)',
      borderWidth: 3,
      tension: 0.4,
    },
  ];

  Object.entries(data.predictions).forEach(([modelName, prediction]) => {
    datasets.push({
      label: modelName,
      data: prediction.map(p => p.value),
      borderColor: colorPalette.models[modelName as keyof typeof colorPalette.models] || '#999',
      backgroundColor: 'transparent',
      borderWidth: 2,
      tension: 0.4,
    });
  });

  const chartData = {
    labels,
    datasets,
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-neutral-900">Model Performance Comparison</h2>
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

      {/* Best Model Banner */}
      <div className="card bg-gradient-to-br from-accent-50 to-accent-100 border-accent-200">
        <div className="flex items-center gap-3">
          <div className="bg-accent-600 p-3 rounded-lg">
            <Award className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-accent-900">Best Model</h3>
            <p className="text-accent-700 text-lg font-bold">{data.best_model}</p>
            <p className="text-accent-600 text-sm">Lowest RMSE score</p>
          </div>
        </div>
      </div>

      {/* Performance Metrics Table */}
      <div className="card">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">📊 Performance Metrics</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b-2 border-neutral-200">
                <th className="text-left py-3 px-4 font-semibold text-neutral-700">Model</th>
                <th className="text-left py-3 px-4 font-semibold text-neutral-700">RMSE</th>
                <th className="text-left py-3 px-4 font-semibold text-neutral-700">MAE</th>
                <th className="text-left py-3 px-4 font-semibold text-neutral-700">MAPE (%)</th>
              </tr>
            </thead>
            <tbody>
              {data.comparison_table.map((row, idx) => (
                <tr 
                  key={idx} 
                  className={`border-b border-neutral-100 hover:bg-neutral-50 ${
                    row.model === data.best_model ? 'bg-accent-50' : ''
                  }`}
                >
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2">
                      {row.model === data.best_model && (
                        <Award className="w-4 h-4 text-accent-600" />
                      )}
                      <span className="font-medium text-neutral-900">{row.model}</span>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-neutral-900">{row.RMSE.toFixed(2)}</td>
                  <td className="py-3 px-4 text-neutral-900">{row.MAE.toFixed(2)}</td>
                  <td className="py-3 px-4 text-neutral-900">{row.MAPE.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Comparison Chart */}
      <div className="card">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">Actual vs Predicted Comparison</h3>
        <div className="h-96">
          <Line data={chartData} options={lineChartOptions} />
        </div>
      </div>
    </div>
  );
}
