import { useEffect, useState, useMemo } from 'react';
import { Loader2, TrendingUp, AlertCircle } from 'lucide-react';
import { getOptions, loadData } from './api';
import type { AppConfig, BaseAnalysisRequest, LoadSummary } from './types';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import MetricsCards from './components/MetricsCards';
import TabNavigation from './components/TabNavigation';
import EDATab from './components/tabs/EDATab';
import ForecastingTab from './components/tabs/ForecastingTab';
import ModelComparisonTab from './components/tabs/ModelComparisonTab';
import SpatialTab from './components/tabs/SpatialTab';
import DataInfoTab from './components/tabs/DataInfoTab';
import WelcomeScreen from './components/WelcomeScreen';

function App() {
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [loadSummary, setLoadSummary] = useState<LoadSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('eda');
  
  // Sidebar state
  const [dataFile, setDataFile] = useState('data/yellow_tripdata_2025-01_sample.csv');
  const [useSample, setUseSample] = useState(false);
  const [sampleSize, setSampleSize] = useState(100000);
  const [selectedModel, setSelectedModel] = useState('All Models');
  const [forecastHorizon, setForecastHorizon] = useState('24 hours');
  const [analyzeLocation, setAnalyzeLocation] = useState(false);
  const [forceRetrain, setForceRetrain] = useState(false);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const options = await getOptions();
        setConfig(options);
        setDataFile(options.data_file);
        setSelectedModel(options.default_model);
        setForecastHorizon(options.default_forecast_horizon);
        setSampleSize(options.sample_defaults.default_size);
      } catch (err) {
        console.error('Failed to fetch config:', err);
        setError('Failed to connect to the backend. Please ensure the API server is running.');
      }
    };
    fetchConfig();
  }, []);

  const handleLoadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const request: BaseAnalysisRequest = {
        data_file: dataFile,
        use_sample: useSample,
        sample_size: useSample ? sampleSize : undefined,
        force_retrain: forceRetrain,
      };
      const summary = await loadData(request);
      setLoadSummary(summary);
      setForceRetrain(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load data. Please check your configuration.');
      console.error('Load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const baseRequest = useMemo<BaseAnalysisRequest>(() => ({
    data_file: dataFile,
    use_sample: useSample,
    sample_size: useSample ? sampleSize : undefined,
    force_retrain: forceRetrain,
  }), [dataFile, useSample, sampleSize, forceRetrain]);

  if (!config) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-50">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-primary-600 mx-auto mb-4" />
          <p className="text-neutral-600">Connecting to backend...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-50 flex">
      <Sidebar
        config={config}
        dataFile={dataFile}
        setDataFile={setDataFile}
        useSample={useSample}
        setUseSample={setUseSample}
        sampleSize={sampleSize}
        setSampleSize={setSampleSize}
        selectedModel={selectedModel}
        setSelectedModel={setSelectedModel}
        forecastHorizon={forecastHorizon}
        setForecastHorizon={setForecastHorizon}
        analyzeLocation={analyzeLocation}
        setAnalyzeLocation={setAnalyzeLocation}
        onLoadData={handleLoadData}
        loading={loading}
        forceRetrain={forceRetrain}
        setForceRetrain={setForceRetrain}
      />

      <div className="flex-1 ml-80">
        <Header />

        <main className="p-8">
          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-red-900 mb-1">Error</h3>
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            </div>
          )}

          {!loadSummary && !loading && (
            <WelcomeScreen />
          )}

          {loading && (
            <div className="flex items-center justify-center py-20">
              <div className="text-center">
                <Loader2 className="w-16 h-16 animate-spin text-primary-600 mx-auto mb-4" />
                <p className="text-neutral-600 text-lg">Loading and preprocessing data...</p>
                <p className="text-neutral-500 text-sm mt-2">This may take a moment</p>
              </div>
            </div>
          )}

          {loadSummary && (
            <>
              <div className="mb-6 bg-accent-50 border border-accent-200 rounded-lg p-4 flex items-start gap-3">
                <TrendingUp className="w-5 h-5 text-accent-700 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="text-accent-900 font-medium">
                    ✓ Loaded {loadSummary.records_loaded.toLocaleString()} records
                  </p>
                  <p className="text-accent-700 text-sm mt-1">
                    Date range: {new Date(loadSummary.date_range.start).toLocaleDateString()} to{' '}
                    {new Date(loadSummary.date_range.end).toLocaleDateString()}
                  </p>
                </div>
              </div>

              <MetricsCards metrics={loadSummary.summary_metrics} />

              <TabNavigation activeTab={activeTab} setActiveTab={setActiveTab} />

              <div className="mt-6">
                {activeTab === 'eda' && <EDATab request={baseRequest} />}
                {activeTab === 'forecasting' && (
                  <ForecastingTab
                    request={baseRequest}
                    selectedModel={selectedModel}
                    forecastHorizon={forecastHorizon}
                  />
                )}
                {activeTab === 'comparison' && <ModelComparisonTab request={baseRequest} />}
                {activeTab === 'spatial' && (
                  <SpatialTab
                    request={baseRequest}
                    analyzeLocation={analyzeLocation}
                  />
                )}
                {activeTab === 'info' && <DataInfoTab request={baseRequest} />}
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
