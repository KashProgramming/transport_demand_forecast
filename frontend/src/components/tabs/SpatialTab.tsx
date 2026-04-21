import { useEffect, useState } from 'react';
import { Loader2, AlertCircle, MapPin } from 'lucide-react';
import { getSpatial } from '../../api';
import type { BaseAnalysisRequest, SpatialData } from '../../types';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';
import { barChartOptions, colorPalette } from '../../utils/chartUtils';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
);

interface SpatialTabProps {
  request: BaseAnalysisRequest;
  analyzeLocation: boolean;
}

export default function SpatialTab({ request, analyzeLocation }: SpatialTabProps) {
  const [data, setData] = useState<SpatialData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedLocation, setSelectedLocation] = useState<number | undefined>();
  const [compareZones, setCompareZones] = useState<number[]>([]);
  const [initialLoad, setInitialLoad] = useState(true);

  // Initial data fetch
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const result = await getSpatial({
          ...request,
          analyze_location: analyzeLocation,
          selected_location: undefined,
          compare_zones: undefined,
        });
        setData(result);
        
        // Set default selected location if not set
        if (initialLoad && result.available_locations.length > 0) {
          setSelectedLocation(result.available_locations[0]);
          if (result.available_locations.length >= 3) {
            setCompareZones(result.available_locations.slice(0, 3));
          }
          setInitialLoad(false);
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load spatial data');
        console.error('Spatial error:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [request, analyzeLocation]);

  // Fetch location-specific data when location or compareZones changes
  useEffect(() => {
    if (!initialLoad && analyzeLocation && (selectedLocation || compareZones.length > 0)) {
      const fetchLocationData = async () => {
        try {
          const result = await getSpatial({
            ...request,
            analyze_location: true,
            selected_location: selectedLocation,
            compare_zones: compareZones.length > 0 ? compareZones : undefined,
          });
          setData(result);
        } catch (err: any) {
          console.error('Failed to fetch location data:', err);
        }
      };
      fetchLocationData();
    }
  }, [selectedLocation, compareZones]);

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
            <h3 className="font-semibold text-red-900 mb-1">Error Loading Spatial Data</h3>
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  // Prepare top zones chart
  const topZonesData = {
    labels: data.top_zones.map(z => `Zone ${z.location_id}`),
    datasets: [
      {
        label: 'Total Demand',
        data: data.top_zones.map(z => z.total_demand),
        backgroundColor: colorPalette.primary,
        borderRadius: 6,
      },
    ],
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-neutral-900">Spatial Demand Analysis</h2>

      {/* Top Zones Chart */}
      <div className="card">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">🔝 Top Pickup Zones</h3>
        <div className="h-80 mb-6">
          <Bar data={topZonesData} options={barChartOptions} />
        </div>
        
        {/* Top Zones Table */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b-2 border-neutral-200">
                <th className="text-left py-3 px-4 font-semibold text-neutral-700">Location ID</th>
                <th className="text-left py-3 px-4 font-semibold text-neutral-700">Total Demand</th>
                <th className="text-left py-3 px-4 font-semibold text-neutral-700">Avg Demand</th>
              </tr>
            </thead>
            <tbody>
              {data.top_zones.map((zone, idx) => (
                <tr key={idx} className="border-b border-neutral-100 hover:bg-neutral-50">
                  <td className="py-3 px-4 text-neutral-900 font-medium">{zone.location_id}</td>
                  <td className="py-3 px-4 text-neutral-900">{zone.total_demand.toLocaleString()}</td>
                  <td className="py-3 px-4 text-neutral-900">{zone.avg_demand.toFixed(1)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Location-Specific Analysis */}
      {analyzeLocation && data.available_locations.length > 0 && (
        <>
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <MapPin className="w-5 h-5 text-primary-600" />
              <h3 className="text-lg font-semibold text-neutral-900">📍 Location-Specific Analysis</h3>
            </div>
            
            <div className="mb-6">
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                Select Location ID
              </label>
              <select
                value={selectedLocation}
                onChange={(e) => setSelectedLocation(Number(e.target.value))}
                className="w-full max-w-xs px-3 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                {data.available_locations.slice(0, 50).map((loc) => (
                  <option key={loc} value={loc}>
                    Zone {loc}
                  </option>
                ))}
              </select>
            </div>

            {/* Zone Statistics */}
            {data.zone_statistics && (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-primary-50 rounded-lg p-4 border border-primary-200">
                  <p className="text-sm text-primary-700 font-medium mb-1">Total Demand</p>
                  <p className="text-2xl font-bold text-primary-900">{data.zone_statistics.total_demand}</p>
                </div>
                <div className="bg-accent-50 rounded-lg p-4 border border-accent-200">
                  <p className="text-sm text-accent-700 font-medium mb-1">Avg Demand</p>
                  <p className="text-2xl font-bold text-accent-900">{data.zone_statistics.avg_demand.toFixed(1)}</p>
                </div>
                <div className="bg-amber-50 rounded-lg p-4 border border-amber-200">
                  <p className="text-sm text-amber-700 font-medium mb-1">Max Demand</p>
                  <p className="text-2xl font-bold text-amber-900">{data.zone_statistics.max_demand.toFixed(0)}</p>
                </div>
                <div className="bg-emerald-50 rounded-lg p-4 border border-emerald-200">
                  <p className="text-sm text-emerald-700 font-medium mb-1">Std Dev</p>
                  <p className="text-2xl font-bold text-emerald-900">{data.zone_statistics.std_demand.toFixed(1)}</p>
                </div>
              </div>
            )}

            {/* Peak Hours for Zone */}
            {data.peak_hours_zone && (
              <div>
                <h4 className="font-semibold text-neutral-900 mb-3">Peak Hours for Zone {selectedLocation}</h4>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-neutral-200">
                        <th className="text-left py-2 px-4 font-semibold text-neutral-700">Hour</th>
                        <th className="text-left py-2 px-4 font-semibold text-neutral-700">Demand</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.peak_hours_zone.slice(0, 10).map((row, idx) => (
                        <tr key={idx} className="border-b border-neutral-100 hover:bg-neutral-50">
                          <td className="py-2 px-4 text-neutral-900">{row.hour}:00</td>
                          <td className="py-2 px-4 text-neutral-900 font-medium">{row.demand.toFixed(0)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>

          {/* Zone Comparison */}
          <div className="card">
            <h3 className="text-lg font-semibold text-neutral-900 mb-4">Compare with Other Zones</h3>
            
            <div className="mb-6">
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                Select zones to compare
              </label>
              <div className="flex flex-wrap gap-2 mb-3">
                {compareZones.map((zone) => (
                  <button
                    key={zone}
                    onClick={() => setCompareZones(compareZones.filter(z => z !== zone))}
                    className="inline-flex items-center gap-1 px-3 py-1.5 bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors text-sm font-medium"
                  >
                    {zone}
                    <span className="text-white">×</span>
                  </button>
                ))}
              </div>
              
              <div className="flex gap-2">
                <select
                  onChange={(e) => {
                    const newZone = Number(e.target.value);
                    if (newZone && !compareZones.includes(newZone)) {
                      setCompareZones([...compareZones, newZone]);
                    }
                    e.target.value = '';
                  }}
                  className="flex-1 px-3 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  defaultValue=""
                >
                  <option value="" disabled>Add a zone...</option>
                  {data.available_locations.slice(0, 50).map((loc) => (
                    <option key={loc} value={loc} disabled={compareZones.includes(loc)}>
                      Zone {loc}
                    </option>
                  ))}
                </select>
                {compareZones.length > 0 && (
                  <button
                    onClick={() => setCompareZones([])}
                    className="px-4 py-2 text-neutral-600 hover:text-neutral-900 border border-neutral-300 rounded-lg hover:bg-neutral-50 transition-colors"
                  >
                    Clear All
                  </button>
                )}
              </div>
            </div>

            {compareZones.length > 0 && data.comparison_figure && (
              <div>
                <h4 className="font-semibold text-neutral-900 mb-3">Demand Pattern Comparison Across Zones</h4>
                <div className="h-80">
                  <Line 
                    data={{
                      labels: Array.from({ length: 24 }, (_, i) => i),
                      datasets: data.comparison_figure.data.map((trace: any, idx: number) => ({
                        label: trace.name,
                        data: trace.y,
                        borderColor: [
                          colorPalette.primary,
                          colorPalette.accent,
                          colorPalette.primaryLight,
                          '#f59e0b',
                          '#10b981',
                          '#8b5cf6',
                        ][idx % 6],
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        pointRadius: 3,
                        pointHoverRadius: 5,
                        tension: 0.4,
                      })),
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      scales: {
                        x: {
                          title: {
                            display: true,
                            text: 'Hour of Day',
                          },
                        },
                        y: {
                          title: {
                            display: true,
                            text: 'Average Demand',
                          },
                          beginAtZero: true,
                        },
                      },
                    }}
                  />
                </div>
              </div>
            )}
            
            {compareZones.length === 0 && (
              <p className="text-neutral-500 text-center py-10">
                Select zones above to compare their demand patterns
              </p>
            )}
          </div>
        </>
      )}
    </div>
  );
}
