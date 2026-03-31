import React, { useState, useEffect, useCallback } from 'react';
import {
  getCostsSummary, getSavings, getIdleInstances, getUnattachedVolumes,
  getAzureCostsSummary, getAzureSavings, getAzureIdleVMs, getAzureUnattachedDisks,
} from '../services/api';
import './Dashboard.css';

const Dashboard = ({ provider, onBack }) => {
  const [costSummary, setCostSummary] = useState(null);
  const [savings, setSavings] = useState(null);
  const [idleInstances, setIdleInstances] = useState([]);
  const [unattachedVolumes, setUnattachedVolumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dataMode, setDataMode] = useState('mock'); // 'mock' | 'real'
  const [error, setError] = useState(null);
  const [lastRefreshed, setLastRefreshed] = useState(null);

  const loadData = useCallback(async (mode) => {
    try {
      setLoading(true);
      setError(null);
      const isAzure = provider === 'azure';
      const [costData, savingsData, idleData, volumeData] = await Promise.all([
        isAzure ? getAzureCostsSummary({}, mode) : getCostsSummary({}, mode),
        isAzure ? getAzureSavings(mode)           : getSavings(mode),
        isAzure ? getAzureIdleVMs(mode)           : getIdleInstances({}, mode),
        isAzure ? getAzureUnattachedDisks(mode)   : getUnattachedVolumes({}, mode),
      ]);
      const isAzure = provider === 'azure';
      setCostSummary(costData);
      setSavings(savingsData);
      setIdleInstances(isAzure ? (idleData.idle_vms || []) : (idleData.idle_instances || []));
      setUnattachedVolumes(isAzure ? (volumeData.unattached_disks || []) : (volumeData.unattached_volumes || []));
      setLastRefreshed(new Date());
    } catch (err) {
      setError('Could not reach the backend. Make sure the API is running.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData(dataMode);
  }, [dataMode, loadData]);

  const handleModeToggle = () => {
    setDataMode(prev => prev === 'mock' ? 'real' : 'mock');
  };

  if (loading) {
    return (
      <div className="dash-loading">
        <div className="dash-spinner" />
        <p>Fetching AWS data…</p>
      </div>
    );
  }

  return (
    <div className="dash-root">
      {/* Sidebar */}
      <aside className="dash-sidebar">
        <div className="sidebar-brand">
          <div className="brand-icon-sm">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="#FF9900" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <span>MCCO</span>
        </div>

        <button className="sidebar-back" onClick={onBack}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
            <path d="M19 12H5M12 19l-7-7 7-7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          All Providers
        </button>

        <div className="sidebar-section-label">Overview</div>
        <nav className="sidebar-nav">
          <a className="sidebar-item active" href="#costs">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
            Cost Overview
          </a>
          <a className="sidebar-item" href="#recs">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none"><path d="M9 11l3 3L22 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
            Recommendations
          </a>
          <a className="sidebar-item" href="#volumes">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none"><ellipse cx="12" cy="5" rx="9" ry="3" stroke="currentColor" strokeWidth="2"/><path d="M21 12c0 1.66-4.03 3-9 3S3 13.66 3 12" stroke="currentColor" strokeWidth="2"/><path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5" stroke="currentColor" strokeWidth="2"/></svg>
            Volumes
          </a>
        </nav>

        <div className="sidebar-bottom">
          <div className="mode-toggle-wrap">
            <span className="mode-label">Data source</span>
            <button
              className={`mode-toggle ${dataMode === 'live' ? 'mode-live' : 'mode-mock'}`}
              onClick={handleModeToggle}
            >
              <span className="mode-dot" />
              {dataMode === 'mock' ? 'Demo' : 'Real'}
            </button>
          </div>
          {lastRefreshed && (
            <div className="last-refreshed">
              Updated {lastRefreshed.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </div>
          )}
        </div>
      </aside>

      {/* Main */}
      <main className="dash-main">
        {/* Top bar */}
        <div className="dash-topbar">
          <div className="topbar-left">
            <div className="provider-badge">
              {provider === 'azure' ? (
                <>
                  <svg width="16" height="16" viewBox="0 0 48 48" fill="none">
                    <path d="M20 4 L4 36 L16 36 L28 16 Z" fill="#0078D4"/>
                    <path d="M27 14 L38 36 L44 36 L30 4 Z" fill="#50B0F0"/>
                  </svg>
                  Microsoft Azure
                </>
              ) : (
                <>
                  <svg width="16" height="16" viewBox="0 0 40 24" fill="none">
                    <text x="0" y="18" fontFamily="Arial" fontSize="14" fontWeight="bold" fill="#FF9900">AWS</text>
                  </svg>
                  Amazon Web Services
                </>
              )}
            </div>
            <span className={`mock-indicator ${dataMode === 'real' ? 'indicator-real' : ''}`}>
              {dataMode === 'mock' ? 'DEMO DATA' : 'REAL DATA'}
            </span>
          </div>
          <button className="topbar-refresh" onClick={() => loadData(dataMode)}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
              <path d="M23 4v6h-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M1 20v-6h6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Refresh
          </button>
        </div>

        {error && (
          <div className="dash-error">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/><line x1="12" y1="8" x2="12" y2="12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/><line x1="12" y1="16" x2="12.01" y2="16" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/></svg>
            {error}
            <button onClick={() => setError(null)}>✕</button>
          </div>
        )}

        {/* KPI row */}
        <div className="kpi-row" id="costs">
          <div className="kpi-card">
            <div className="kpi-label">Monthly Cost</div>
            <div className="kpi-value">${costSummary?.total_cost?.toFixed(2) ?? '—'}</div>
            <div className="kpi-sub">Total spend this month</div>
          </div>
          <div className="kpi-card kpi-savings">
            <div className="kpi-label">Potential Savings</div>
            <div className="kpi-value kpi-value-green">${savings?.total_potential_savings?.toFixed(2) ?? '—'}</div>
            <div className="kpi-sub">Identified optimizations</div>
          </div>
          <div className="kpi-card">
            <div className="kpi-label">{provider === 'azure' ? 'Idle VMs' : 'Idle Instances'}</div>
            <div className="kpi-value kpi-value-yellow">{idleInstances.length}</div>
            <div className="kpi-sub">{provider === 'azure' ? 'VMs underutilized' : 'EC2 instances underutilized'}</div>
          </div>
          <div className="kpi-card">
            <div className="kpi-label">{provider === 'azure' ? 'Orphan Disks' : 'Orphan Volumes'}</div>
            <div className="kpi-value">{unattachedVolumes.length}</div>
            <div className="kpi-sub">{provider === 'azure' ? 'Unattached managed disks' : 'Unattached EBS volumes'}</div>
          </div>
        </div>

        {/* Breakdown */}
        <div className="breakdown-row">
          <div className="breakdown-card">
            <div className="card-header">
              <h2>By Service</h2>
            </div>
            <div className="breakdown-list">
              {costSummary?.by_service?.map((s, i) => (
                <div key={i} className="breakdown-item">
                  <div className="breakdown-meta">
                    <span className="breakdown-name">{s.service_name}</span>
                    <span className="breakdown-cost">${s.total_cost.toFixed(2)}</span>
                  </div>
                  <div className="bar-track">
                    <div className="bar-fill" style={{ width: `${s.percentage}%` }} />
                  </div>
                  <span className="breakdown-pct">{s.percentage.toFixed(1)}%</span>
                </div>
              ))}
            </div>
          </div>

          <div className="breakdown-card">
            <div className="card-header">
              <h2>By Region</h2>
            </div>
            <div className="breakdown-list">
              {costSummary?.by_region?.map((r, i) => (
                <div key={i} className="breakdown-item">
                  <div className="breakdown-meta">
                    <span className="breakdown-name">{r.region}</span>
                    <span className="breakdown-cost">${r.total_cost.toFixed(2)}</span>
                  </div>
                  <div className="bar-track">
                    <div className="bar-fill bar-fill-region" style={{ width: `${r.percentage}%` }} />
                  </div>
                  <span className="breakdown-pct">{r.percentage.toFixed(1)}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Idle Instances */}
        {idleInstances.length > 0 && (
          <div className="table-card" id="recs">
            <div className="card-header">
              <h2>{provider === 'azure' ? 'Idle Virtual Machines' : 'Idle EC2 Instances'}</h2>
              <span className="count-badge">{idleInstances.length}</span>
            </div>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>{provider === 'azure' ? 'VM Name' : 'Instance'}</th>
                    <th>{provider === 'azure' ? 'VM Size' : 'Type'}</th>
                    <th>Region</th>
                    <th>CPU Avg</th>
                    <th>Savings / mo</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {idleInstances.map((inst, i) => (
                    <tr key={i}>
                      <td><code>{provider === 'azure' ? inst.vm_id : inst.instance_id}</code></td>
                      <td>{provider === 'azure' ? inst.vm_size : inst.instance_type}</td>
                      <td>{inst.region}</td>
                      <td><span className="badge-yellow">{inst.cpu_utilization.toFixed(1)}%</span></td>
                      <td className="text-green">${inst.potential_savings.toFixed(2)}</td>
                      <td><button className="row-btn">{provider === 'azure' ? 'Deallocate' : 'Stop'}</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Unattached Volumes */}
        {unattachedVolumes.length > 0 && (
          <div className="table-card" id="volumes">
            <div className="card-header">
              <h2>{provider === 'azure' ? 'Unattached Managed Disks' : 'Unattached EBS Volumes'}</h2>
              <span className="count-badge">{unattachedVolumes.length}</span>
            </div>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>{provider === 'azure' ? 'Disk Name' : 'Volume'}</th>
                    <th>Type</th>
                    <th>Size</th>
                    <th>Region</th>
                    <th>Cost / mo</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {unattachedVolumes.map((vol, i) => (
                    <tr key={i}>
                      <td><code>{provider === 'azure' ? vol.disk_id : vol.volume_id}</code></td>
                      <td>{provider === 'azure' ? vol.disk_type : vol.volume_type}</td>
                      <td>{vol.size} GB</td>
                      <td>{vol.region}</td>
                      <td className="text-green">${vol.monthly_cost.toFixed(2)}</td>
                      <td><button className="row-btn row-btn-danger">Delete</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;
