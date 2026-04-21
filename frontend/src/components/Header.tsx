import { Car } from 'lucide-react';

export default function Header() {
  return (
    <header className="bg-white border-b border-neutral-200 px-8 py-6 sticky top-0 z-10 shadow-sm">
      <div className="flex items-center gap-4">
        <div className="bg-gradient-to-br from-primary-500 to-primary-600 p-3 rounded-xl shadow-md">
          <Car className="w-8 h-8 text-white" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">
            Smart Urban Transport Demand Forecasting
          </h1>
          <p className="text-neutral-600 mt-1">
            NYC Yellow Taxi Trip Analysis & Prediction System
          </p>
        </div>
      </div>
    </header>
  );
}
