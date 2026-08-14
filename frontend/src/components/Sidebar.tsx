import React from 'react';
import { LayoutDashboard, UploadCloud, History, BarChart3, Radio } from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const menuItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'batch',     label: 'Batch CSV',        icon: UploadCloud },
  { id: 'history',   label: 'Audit Log',        icon: History },
  { id: 'analytics', label: 'Model Benchmark',  icon: BarChart3 },
  { id: 'simulator', label: 'Live Simulator',   icon: Radio },
];

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  return (
    <aside
      style={{
        width: 220,
        minHeight: 'calc(100vh - 60px)',
        background: 'var(--bg-surface)',
        borderRight: '1px solid var(--border-muted)',
        padding: '20px 12px',
        flexShrink: 0,
      }}
    >
      <div
        style={{
          fontSize: 10,
          fontWeight: 600,
          color: 'var(--text-faint)',
          textTransform: 'uppercase',
          letterSpacing: '0.09em',
          padding: '0 10px',
          marginBottom: 12,
        }}
      >
        Navigation
      </div>

      <nav style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                padding: '8px 10px',
                borderRadius: 8,
                border: isActive ? '1px solid var(--accent-border)' : '1px solid transparent',
                background: isActive ? 'var(--accent-subtle)' : 'transparent',
                color: isActive ? '#93c5fd' : 'var(--text-secondary)',
                fontSize: 13,
                fontWeight: isActive ? 600 : 400,
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.15s ease',
              }}
              onMouseEnter={(e) => {
                if (!isActive) {
                  (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.04)';
                  (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-primary)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isActive) {
                  (e.currentTarget as HTMLButtonElement).style.background = 'transparent';
                  (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-secondary)';
                }
              }}
            >
              <Icon
                size={15}
                style={{ color: isActive ? '#93c5fd' : 'var(--text-faint)', flexShrink: 0 }}
              />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>
    </aside>
  );
};
