import { TrendingUp, Activity, Zap, DollarSign } from 'lucide-react';

interface MetricsCardsProps {
  metrics: {
    total_trips: string;
    avg_hourly_demand: number;
    peak_demand: string;
    total_revenue: string;
  };
}

export default function MetricsCards({ metrics }: MetricsCardsProps) {
  const cards = [
    {
      title: 'Total Trips',
      value: metrics.total_trips,
      icon: TrendingUp,
      color: 'from-primary-500 to-primary-600',
      bgColor: 'bg-primary-50',
      textColor: 'text-primary-700',
    },
    {
      title: 'Avg Hourly Demand',
      value: metrics.avg_hourly_demand.toLocaleString(),
      icon: Activity,
      color: 'from-accent-500 to-accent-600',
      bgColor: 'bg-accent-50',
      textColor: 'text-accent-700',
    },
    {
      title: 'Peak Demand',
      value: metrics.peak_demand,
      icon: Zap,
      color: 'from-amber-500 to-amber-600',
      bgColor: 'bg-amber-50',
      textColor: 'text-amber-700',
    },
    {
      title: 'Total Revenue',
      value: metrics.total_revenue,
      icon: DollarSign,
      color: 'from-emerald-500 to-emerald-600',
      bgColor: 'bg-emerald-50',
      textColor: 'text-emerald-700',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <div key={card.title} className="metric-card">
            <div className="flex items-start justify-between mb-3">
              <div className={`${card.bgColor} p-3 rounded-lg`}>
                <Icon className={`w-6 h-6 ${card.textColor}`} />
              </div>
            </div>
            <p className="text-neutral-600 text-sm font-medium mb-1">{card.title}</p>
            <p className="text-3xl font-bold text-neutral-900">{card.value}</p>
          </div>
        );
      })}
    </div>
  );
}
