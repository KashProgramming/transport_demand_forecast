import { BarChart3, TrendingUp, Award, Map, Info } from 'lucide-react';
import clsx from 'clsx';

interface TabNavigationProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export default function TabNavigation({ activeTab, setActiveTab }: TabNavigationProps) {
  const tabs = [
    { id: 'eda', label: 'EDA', icon: BarChart3 },
    { id: 'forecasting', label: 'Forecasting', icon: TrendingUp },
    { id: 'comparison', label: 'Model Comparison', icon: Award },
    { id: 'spatial', label: 'Spatial Analysis', icon: Map },
    { id: 'info', label: 'Data Info', icon: Info },
  ];

  return (
    <div className="flex gap-3 overflow-x-auto pb-2">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        return (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={clsx(
              'tab-button flex items-center gap-2 whitespace-nowrap',
              activeTab === tab.id ? 'tab-button-active' : 'tab-button-inactive'
            )}
          >
            <Icon className="w-4 h-4" />
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}
