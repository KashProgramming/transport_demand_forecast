import { Settings, Database, Brain, MapPin, Loader2, RefreshCw } from 'lucide-react';
import type { AppConfig } from '../types';

interface SidebarProps {
  config: AppConfig;
  dataFile: string;
  setDataFile: (value: string) => void;
  useSample: boolean;
  setUseSample: (value: boolean) => void;
  sampleSize: number;
  setSampleSize: (value: number) => void;
  selectedModel: string;
  setSelectedModel: (value: string) => void;
  forecastHorizon: string;
  setForecastHorizon: (value: string) => void;
  analyzeLocation: boolean;
  setAnalyzeLocation: (value: boolean) => void;
  onLoadData: () => void;
  loading: boolean;
  forceRetrain: boolean;
  setForceRetrain: (value: boolean) => void;
}

export default function Sidebar({
  config,
  dataFile,
  setDataFile,
  useSample,
  setUseSample,
  sampleSize,
  setSampleSize,
  selectedModel,
  setSelectedModel,
  forecastHorizon,
  setForecastHorizon,
  analyzeLocation,
  setAnalyzeLocation,
  onLoadData,
  loading,
  forceRetrain,
  setForceRetrain,
}: SidebarProps) {
  return (
    <aside className="w-80 bg-white border-r border-neutral-200 h-screen overflow-y-auto fixed left-0 top-0 shadow-lg">
      <div className="p-6">
        <div className="flex items-center gap-3 mb-8">
          <div className="bg-primary-100 p-2 rounded-lg">
            <Settings className="w-6 h-6 text-primary-700" />
          </div>
          <h2 className="text-xl font-bold text-neutral-900">Configuration</h2>
        </div>

        {/* Data Options */}
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-3">
            <Database className="w-4 h-4 text-primary-600" />
            <h3 className="font-semibold text-neutral-800">Data Options</h3>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                Data File Path
              </label>
              <input
                type="text"
                value={dataFile}
                onChange={(e) => setDataFile(e.target.value)}
                className="w-full px-3 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
              />
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="useSample"
                checked={useSample}
                onChange={(e) => setUseSample(e.target.checked)}
                className="w-4 h-4 text-primary-600 border-neutral-300 rounded focus:ring-primary-500"
              />
              <label htmlFor="useSample" className="text-sm font-medium text-neutral-700">
                Use Sample Data (faster)
              </label>
            </div>

            {useSample && (
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Sample Size
                </label>
                <input
                  type="number"
                  value={sampleSize}
                  onChange={(e) => setSampleSize(Number(e.target.value))}
                  min={10000}
                  max={1000000}
                  step={10000}
                  className="w-full px-3 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
                />
              </div>
            )}
          </div>
        </div>

        {/* Model Selection */}
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-3">
            <Brain className="w-4 h-4 text-primary-600" />
            <h3 className="font-semibold text-neutral-800">Model Selection</h3>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">
              Choose Model
            </label>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="w-full px-3 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
            >
              {config.available_models.map((model) => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Forecast Settings */}
        <div className="mb-6">
          <h3 className="font-semibold text-neutral-800 mb-3">Forecast Settings</h3>
          
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">
              Forecast Horizon
            </label>
            <select
              value={forecastHorizon}
              onChange={(e) => setForecastHorizon(e.target.value)}
              className="w-full px-3 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
            >
              {Object.keys(config.forecast_horizons).map((horizon) => (
                <option key={horizon} value={horizon}>
                  {horizon}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Spatial Analysis */}
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-3">
            <MapPin className="w-4 h-4 text-primary-600" />
            <h3 className="font-semibold text-neutral-800">Spatial Analysis</h3>
          </div>
          
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="analyzeLocation"
              checked={analyzeLocation}
              onChange={(e) => setAnalyzeLocation(e.target.checked)}
              className="w-4 h-4 text-primary-600 border-neutral-300 rounded focus:ring-primary-500"
            />
            <label htmlFor="analyzeLocation" className="text-sm font-medium text-neutral-700">
              Analyze Specific Location
            </label>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="space-y-3">
          <button
            onClick={onLoadData}
            disabled={loading}
            className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Loading...
              </>
            ) : (
              <>
                <Database className="w-5 h-5" />
                Load Data & Train Models
              </>
            )}
          </button>

          <button
            onClick={() => setForceRetrain(!forceRetrain)}
            className={`w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
              forceRetrain
                ? 'bg-accent-600 text-white hover:bg-accent-700'
                : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200'
            }`}
          >
            <RefreshCw className="w-4 h-4" />
            {forceRetrain ? 'Will Retrain Models' : 'Force Retrain Models'}
          </button>
        </div>

        {forceRetrain && (
          <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-lg">
            <p className="text-xs text-amber-800">
              Models will be retrained on next data load
            </p>
          </div>
        )}
      </div>
    </aside>
  );
}
