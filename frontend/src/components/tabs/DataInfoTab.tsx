import { useEffect, useState } from 'react';
import { Loader2, AlertCircle, Database, TrendingUp, DollarSign, Wrench } from 'lucide-react';
import { getDataInfo } from '../../api';
import type { BaseAnalysisRequest, DataInfo } from '../../types';

interface DataInfoTabProps {
  request: BaseAnalysisRequest;
}

export default function DataInfoTab({ request }: DataInfoTabProps) {
  const [data, setData] = useState<DataInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const result = await getDataInfo(request);
        setData(result);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load data info');
        console.error('Data info error:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [request]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-12 h-12 animate-spin text-primary-600" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="card bg-red-50 border-red-200">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-red-900 mb-1">Error Loading Data Info</h3>
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-neutral-900">Dataset Information</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Data Summary */}
        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-primary-100 p-2 rounded-lg">
              <Database className="w-5 h-5 text-primary-700" />
            </div>
            <h3 className="text-lg font-semibold text-neutral-900">📊 Data Summary</h3>
          </div>
          
          <div className="space-y-3">
            <div className="flex justify-between items-center py-2 border-b border-neutral-100">
              <span className="text-neutral-600">Total Records</span>
              <span className="font-semibold text-neutral-900">
                {data.data_summary.total_records.toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-neutral-100">
              <span className="text-neutral-600">Date Range</span>
              <span className="font-semibold text-neutral-900">
                {new Date(data.data_summary.date_range.start).toLocaleDateString()} to{' '}
                {new Date(data.data_summary.date_range.end).toLocaleDateString()}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-neutral-100">
              <span className="text-neutral-600">Total Hours</span>
              <span className="font-semibold text-neutral-900">
                {data.data_summary.total_hours.toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between items-center py-2">
              <span className="text-neutral-600">Unique Locations</span>
              <span className="font-semibold text-neutral-900">
                {data.data_summary.unique_locations.toLocaleString()}
              </span>
            </div>
          </div>
        </div>

        {/* Demand Statistics */}
        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-accent-100 p-2 rounded-lg">
              <TrendingUp className="w-5 h-5 text-accent-700" />
            </div>
            <h3 className="text-lg font-semibold text-neutral-900">📈 Demand Statistics</h3>
          </div>
          
          <div className="space-y-3">
            <div className="flex justify-between items-center py-2 border-b border-neutral-100">
              <span className="text-neutral-600">Mean</span>
              <span className="font-semibold text-neutral-900">
                {data.demand_statistics.mean.toFixed(2)} trips/hour
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-neutral-100">
              <span className="text-neutral-600">Median</span>
              <span className="font-semibold text-neutral-900">
                {data.demand_statistics.median.toFixed(2)} trips/hour
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-neutral-100">
              <span className="text-neutral-600">Std Dev</span>
              <span className="font-semibold text-neutral-900">
                {data.demand_statistics.std.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-neutral-100">
              <span className="text-neutral-600">Min</span>
              <span className="font-semibold text-neutral-900">
                {data.demand_statistics.min.toFixed(0)}
              </span>
            </div>
            <div className="flex justify-between items-center py-2">
              <span className="text-neutral-600">Max</span>
              <span className="font-semibold text-neutral-900">
                {data.demand_statistics.max.toLocaleString()}
              </span>
            </div>
          </div>
        </div>

        {/* Revenue Statistics */}
        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-emerald-100 p-2 rounded-lg">
              <DollarSign className="w-5 h-5 text-emerald-700" />
            </div>
            <h3 className="text-lg font-semibold text-neutral-900">💰 Revenue Statistics</h3>
          </div>
          
          <div className="space-y-3">
            <div className="flex justify-between items-center py-2 border-b border-neutral-100">
              <span className="text-neutral-600">Total Revenue</span>
              <span className="font-semibold text-neutral-900">
                ${data.revenue_statistics.total_revenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-neutral-100">
              <span className="text-neutral-600">Avg Hourly Revenue</span>
              <span className="font-semibold text-neutral-900">
                ${data.revenue_statistics.avg_hourly_revenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
            </div>
            <div className="flex justify-between items-center py-2">
              <span className="text-neutral-600">Max Hourly Revenue</span>
              <span className="font-semibold text-neutral-900">
                ${data.revenue_statistics.max_hourly_revenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
            </div>
          </div>
        </div>

        {/* Feature Engineering */}
        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-amber-100 p-2 rounded-lg">
              <Wrench className="w-5 h-5 text-amber-700" />
            </div>
            <h3 className="text-lg font-semibold text-neutral-900">🔧 Feature Engineering</h3>
          </div>
          
          <div className="space-y-3">
            <div className="flex justify-between items-center py-2 border-b border-neutral-100">
              <span className="text-neutral-600">Total Features</span>
              <span className="font-semibold text-neutral-900">
                {data.feature_engineering.total_features}
              </span>
            </div>
            <div className="py-2">
              <p className="text-neutral-600 mb-2">Feature Types:</p>
              <ul className="space-y-1">
                {data.feature_engineering.feature_types.map((type, idx) => (
                  <li key={idx} className="text-sm text-neutral-700 ml-4">• {type}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Sample Data */}
      <div className="card">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">📋 Sample Data (First 24 Hours)</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b-2 border-neutral-200">
                <th className="text-left py-3 px-4 font-semibold text-neutral-700">DateTime</th>
                <th className="text-left py-3 px-4 font-semibold text-neutral-700">Demand</th>
              </tr>
            </thead>
            <tbody>
              {data.sample_data.map((row, idx) => (
                <tr key={idx} className="border-b border-neutral-100 hover:bg-neutral-50">
                  <td className="py-2 px-4 text-neutral-900">
                    {new Date(row.datetime).toLocaleString()}
                  </td>
                  <td className="py-2 px-4 text-neutral-900 font-medium">
                    {row.demand.toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
