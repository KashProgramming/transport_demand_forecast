import { useEffect, useState } from 'react';
import { Loader2, AlertCircle } from 'lucide-react';
import { getEDA } from '../../api';
import type { BaseAnalysisRequest, EDAData } from '../../types';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import { lineChartOptions, barChartOptions, colorPalette } from '../../utils/chartUtils';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface EDATabProps {
  request: BaseAnalysisRequest;
}

export default function EDATab({ request }: EDATabProps) {
  const [data, setData] = useState<EDAData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const result = await getEDA(request);
        setData(result);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load EDA data');
        console.error('EDA error:', err);
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
            <h3 className="font-semibold text-red-900 mb-1">Error Loading EDA Data</h3>
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  // Convert Plotly data to Chart.js format
  const demandOverTimeData = {
    labels: data.figures.demand_over_time.data[0].x.map((date: string) => {
      const d = new Date(date);
      return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }),
    datasets: [
      {
        label: 'Hourly Demand',
        data: data.figures.demand_over_time.data[0].y,
        borderColor: colorPalette.primary,
        backgroundColor: colorPalette.primary + '20',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const hourlyDistData = {
    labels: data.figures.hourly_distribution.data[0].x.map((h: number) => `${h}:00`),
    datasets: [
      {
        label: 'Average Demand',
        data: data.figures.hourly_distribution.data[0].y,
        backgroundColor: colorPalette.primary,
        borderRadius: 6,
      },
    ],
  };

  // Weekday comparison - line chart with two traces
  const weekdayData = {
    labels: data.figures.weekday_comparison.data[0].x.map((h: number) => `${h}:00`),
    datasets: data.figures.weekday_comparison.data.map((trace: any, idx: number) => ({
      label: trace.name,
      data: trace.y,
      borderColor: idx === 0 ? colorPalette.primary : colorPalette.accent,
      backgroundColor: 'transparent',
      borderWidth: 3,
      pointRadius: 5,
      pointBackgroundColor: idx === 0 ? colorPalette.primary : colorPalette.accent,
      tension: 0.4,
    })),
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-neutral-900">Exploratory Data Analysis</h2>

      {/* Demand Over Time */}
      <div className="card">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">Hourly Demand Over Time</h3>
        <div className="h-96">
          <Line data={demandOverTimeData} options={lineChartOptions} />
        </div>
      </div>

      {/* Hourly Distribution and Weekday Comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Demand by Hour of Day</h3>
          <div className="h-80">
            <Bar data={hourlyDistData} options={barChartOptions} />
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Weekday vs Weekend</h3>
          <div className="h-80">
            <Line data={weekdayData} options={lineChartOptions} />
          </div>
        </div>
      </div>

      {/* Peak Hours Table */}
      <div className="card">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">🔥 Peak Hours</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-neutral-200">
                <th className="text-left py-3 px-4 font-semibold text-neutral-700">Hour</th>
                <th className="text-left py-3 px-4 font-semibold text-neutral-700">Average Demand</th>
              </tr>
            </thead>
            <tbody>
              {data.peak_hours.map((row, idx) => (
                <tr key={idx} className="border-b border-neutral-100 hover:bg-neutral-50">
                  <td className="py-3 px-4 text-neutral-900">{row.Hour}</td>
                  <td className="py-3 px-4 text-neutral-900 font-medium">
                    {row['Average Demand'].toLocaleString()}
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
