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
        background: 'rgba(14,17,23,0.92)',
        backdropFilter: 'blur(12px)',
        WebkitBackdropFilter: 'blur(12px)',
        borderBottom: '1px solid rgba(255,255,255,0.07)',
        padding: '0 24px',
        height: 60,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
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
            boxShadow: '0 2px 10px rgba(37,99,235,0.30)',
            flexShrink: 0,
          }}
        >
          <ShieldCheck size={18} color="#fff" />
        </div>
        <div>
          <div style={{ fontWeight: 700, fontSize: 15, color: '#e8edf5', letterSpacing: '-0.02em', lineHeight: 1.2 }}>
            FraudGuard <span style={{ color: '#93c5fd' }}>AI</span>
          </div>
          <div style={{ fontSize: 10, color: '#64748b', letterSpacing: '0.04em', fontWeight: 500 }}>
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

        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: '#64748b' }}>
          <Server size={12} color="#93c5fd" />
          <span style={{ color: '#94a3b8' }}>PyTorch DNN</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: '#64748b' }}>
          <Activity size={12} color="#94a3b8" />
          <span>Threshold: <strong style={{ color: '#e8edf5', fontFamily: 'JetBrains Mono, monospace' }}>0.01</strong></span>
        </div>
      </div>
    </header>
  );
};
