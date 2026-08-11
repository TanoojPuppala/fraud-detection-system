import React from 'react';
import { LayoutDashboard, Zap, UploadCloud, History, BarChart3, Radio } from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard Overview', icon: LayoutDashboard },
    { id: 'predict', label: 'Single Transaction Scoring', icon: Zap },
    { id: 'batch', label: 'Batch CSV Scoring', icon: UploadCloud },
    { id: 'history', label: 'Transaction Audit Log', icon: History },
    { id: 'analytics', label: 'Model Benchmark & SHAP', icon: BarChart3 },
    { id: 'simulator', label: 'Real-Time Simulator', icon: Radio },
  ];

  return (
    <aside className="w-64 bg-slate-950/60 border-r border-slate-800/80 p-4 space-y-2 min-h-[calc(100vh-61px)]">
      <div className="px-3 py-2 text-xs font-semibold uppercase tracking-wider text-slate-500 font-mono">
        Navigation Menu
      </div>
      <nav className="space-y-1.5">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'bg-gradient-to-r from-cyan-500/20 to-indigo-600/20 text-cyan-400 border border-cyan-500/30 shadow-lg shadow-cyan-500/10'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>
    </aside>
  );
};
