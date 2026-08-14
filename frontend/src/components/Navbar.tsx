import React from 'react';
import { ShieldCheck, Activity, Server } from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  return (
    <header
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 50,
        background: 'rgba(255,255,255,0.92)',
        backdropFilter: 'blur(12px)',
        WebkitBackdropFilter: 'blur(12px)',
        borderBottom: '1px solid var(--border-muted)',
        padding: '0 24px',
        height: 60,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        boxShadow: 'var(--shadow-sm)',
      }}
    >
      {/* Brand */}
      <div
        style={{ display: 'flex', alignItems: 'center', gap: 12, cursor: 'pointer' }}
        onClick={() => setActiveTab('dashboard')}
      >
        <div
          style={{
            width: 36, height: 36,
            borderRadius: 9,
            background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 2px 8px rgba(37,99,235,0.25)',
            flexShrink: 0,
          }}
        >
          <ShieldCheck size={18} color="#fff" />
        </div>
        <div>
          <div style={{ fontWeight: 700, fontSize: 15, color: 'var(--text-primary)', letterSpacing: '-0.02em', lineHeight: 1.2 }}>
            FraudGuard <span style={{ color: 'var(--accent)' }}>AI</span>
          </div>
          <div style={{ fontSize: 10, color: 'var(--text-muted)', letterSpacing: '0.04em', fontWeight: 500 }}>
            Financial Risk Analysis System
          </div>
        </div>
      </div>

      {/* Status Indicators */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
        <div className="status-online">
          <span className="pulse-dot" />
          <span>Model Online</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: 'var(--text-muted)' }}>
          <Server size={13} color="var(--accent)" />
          <span style={{ color: 'var(--text-secondary)', fontWeight: 500 }}>PyTorch DNN</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: 'var(--text-muted)' }}>
          <Activity size={13} color="var(--text-muted)" />
          <span>Threshold: <strong style={{ color: 'var(--text-primary)', fontFamily: 'JetBrains Mono, monospace' }}>0.01</strong></span>
        </div>
      </div>
    </header>
  );
};
