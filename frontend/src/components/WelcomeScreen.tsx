import { BarChart3, Brain, Map, TrendingUp } from 'lucide-react';

export default function WelcomeScreen() {
  const features = [
    {
      icon: TrendingUp,
      title: 'Features',
      items: [
        'Real-time demand forecasting',
        'Multiple ML models',
        'Spatial analysis',
        'Interactive visualizations',
      ],
    },
    {
      icon: Brain,
      title: 'Models',
      items: [
        'ARIMA (baseline)',
        'SARIMA (seasonality)',
        'Prophet (trend + seasonality)',
        'XGBoost (ML features)',
      ],
    },
    {
      icon: Map,
      title: 'Insights',
      items: [
        'Peak hour identification',
        'Zone-level demand',
        'Revenue forecasting',
        'Fleet optimization',
      ],
    },
  ];

  return (
    <div className="max-w-5xl mx-auto">
      <div className="text-center mb-12">
        <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl mb-6 shadow-lg">
          <BarChart3 className="w-10 h-10 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-neutral-900 mb-3">
          About This System
        </h2>
        <p className="text-neutral-600 text-lg max-w-2xl mx-auto">
          Configure settings in the sidebar and click "Load Data & Train Models" to begin your analysis
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {features.map((feature) => {
          const Icon = feature.icon;
          return (
            <div key={feature.title} className="card">
              <div className="flex items-center gap-3 mb-4">
                <div className="bg-primary-100 p-2 rounded-lg">
                  <Icon className="w-5 h-5 text-primary-700" />
                </div>
                <h3 className="font-bold text-neutral-900">{feature.title}</h3>
              </div>
              <ul className="space-y-2">
                {feature.items.map((item) => (
                  <li key={item} className="flex items-start gap-2 text-neutral-700 text-sm">
                    <span className="text-primary-600 mt-1">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
      </div>

      <div className="mt-8 card bg-gradient-to-br from-primary-50 to-accent-50 border-primary-200">
        <h3 className="font-bold text-neutral-900 mb-3">Getting Started</h3>
        <ol className="space-y-2 text-neutral-700">
          <li className="flex gap-3">
            <span className="font-bold text-primary-600">1.</span>
            <span>Configure your data source and sampling options in the sidebar</span>
          </li>
          <li className="flex gap-3">
            <span className="font-bold text-primary-600">2.</span>
            <span>Select your preferred forecasting model and time horizon</span>
          </li>
          <li className="flex gap-3">
            <span className="font-bold text-primary-600">3.</span>
            <span>Click "Load Data & Train Models" to start the analysis</span>
          </li>
          <li className="flex gap-3">
            <span className="font-bold text-primary-600">4.</span>
            <span>Explore the interactive tabs to view insights and predictions</span>
          </li>
        </ol>
      </div>
    </div>
  );
}
