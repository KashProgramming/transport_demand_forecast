import { ChartOptions } from 'chart.js';

export const defaultChartOptions: ChartOptions<any> = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index',
    intersect: false,
  },
  plugins: {
    legend: {
      display: true,
      position: 'top',
      labels: {
        usePointStyle: true,
        padding: 15,
        font: {
          size: 12,
          family: 'Inter',
        },
      },
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      padding: 12,
      titleFont: {
        size: 13,
        family: 'Inter',
      },
      bodyFont: {
        size: 12,
        family: 'Inter',
      },
      cornerRadius: 8,
    },
  },
};

export const lineChartOptions: ChartOptions<'line'> = {
  ...defaultChartOptions,
  scales: {
    x: {
      grid: {
        display: false,
      },
      ticks: {
        font: {
          size: 11,
          family: 'Inter',
        },
      },
    },
    y: {
      beginAtZero: true,
      grid: {
        color: 'rgba(0, 0, 0, 0.05)',
      },
      ticks: {
        font: {
          size: 11,
          family: 'Inter',
        },
      },
    },
  },
};

export const barChartOptions: ChartOptions<'bar'> = {
  ...defaultChartOptions,
  scales: {
    x: {
      grid: {
        display: false,
      },
      ticks: {
        font: {
          size: 11,
          family: 'Inter',
        },
      },
    },
    y: {
      beginAtZero: true,
      grid: {
        color: 'rgba(0, 0, 0, 0.05)',
      },
      ticks: {
        font: {
          size: 11,
          family: 'Inter',
        },
      },
    },
  },
};

export const colorPalette = {
  primary: '#f0710b',
  primaryLight: '#f38f33',
  accent: '#22c55e',
  accentLight: '#4ade80',
  neutral: '#78716c',
  neutralLight: '#a8a29e',
  models: {
    ARIMA: '#f0710b',
    SARIMA: '#22c55e',
    Prophet: '#f59e0b',
    XGBoost: '#ef4444',
  },
};

export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
};

export const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

export const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toFixed(0);
};
