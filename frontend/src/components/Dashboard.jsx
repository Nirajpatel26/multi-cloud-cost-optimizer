import React, { useState, useEffect } from 'react';
import { getCostsSummary, getSavings, getIdleInstances, getUnattachedVolumes } from '../services/api';
import './Dashboard.css';

const Dashboard = () => {
  const [costSummary, setCostSummary] = useState(null);
  const [savings, setSavings] = useState(null);
  const [idleInstances, setIdleInstances] = useState([]);
  const [unattachedVolumes, setUnattachedVolumes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      const [costData, savingsData, idleData, volumeData] = await Promise.all([
        getCostsSummary(),
        getSavings(),
        getIdleInstances(),
        getUnattachedVolumes()
      ]);
      
      setCostSummary(costData);
      setSavings(savingsData);
      setIdleInstances(idleData.idle_instances || []);
      setUnattachedVolumes(volumeData.unattached_volumes || []);
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="dashboard-header glass">
        <div className="header-content">
          <div className="logo-section">
            <svg className="aws-logo" width="40" height="40" viewBox="0 0 40 40">
              <path fill="#FF9900" d="M14.8 18.5c0 .9-.1 1.6-.2 2.1-.1.5-.4 1-.7 1.5-.1.2-.2.3-.2.5 0 .2.1.4.4.4.7-.1 1.4-.6 2-1.3l.6.7c-.9 1.1-2 1.6-3.2 1.6-.8 0-1.5-.2-1.9-.7-.5-.5-.7-1.1-.7-2 0-1.2.4-2.2 1.1-3 .7-.8 1.7-1.2 2.8-1.2.9 0 1.6.3 2.1.8.5.5.7 1.2.7 2.1v.5h-5.1c0 .8.2 1.4.6 1.8.4.4.9.6 1.6.6.9 0 1.7-.3 2.4-1l.6.7c-.9.9-2 1.3-3.3 1.3-1.2 0-2.1-.4-2.8-1.1-.7-.7-1-1.7-1-2.9 0-1.3.4-2.4 1.2-3.2.8-.8 1.8-1.2 3-1.2 1 0 1.8.3 2.4.9.6.6.9 1.4.9 2.4v.4h-5.4z"/>
            </svg>
            <h1>AWS Cost Optimizer</h1>
          </div>
          <button className="refresh-btn" onClick={loadDashboardData}>
            Refresh Data
          </button>
        </div>
      </header>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card glass-card">
          <div className="stat-icon total-cost">$</div>
          <div className="stat-content">
            <h3>Total Monthly Cost</h3>
            <p className="stat-value">
              ${costSummary?.total_cost?.toFixed(2) || '0.00'}
            </p>
          </div>
        </div>

        <div className="stat-card glass-card savings-card">
          <div className="stat-icon savings">💰</div>
          <div className="stat-content">
            <h3>Potential Savings</h3>
            <p className="stat-value savings-value">
              ${savings?.total_potential_savings?.toFixed(2) || '0.00'}
            </p>
          </div>
        </div>

        <div className="stat-card glass-card">
          <div className="stat-icon idle">⚠</div>
          <div className="stat-content">
            <h3>Idle Instances</h3>
            <p className="stat-value">{idleInstances.length}</p>
          </div>
        </div>

        <div className="stat-card glass-card">
          <div className="stat-icon volumes">📦</div>
          <div className="stat-content">
            <h3>Unattached Volumes</h3>
            <p className="stat-value">{unattachedVolumes.length}</p>
          </div>
        </div>
      </div>

      {/* Cost Breakdown */}
      <div className="content-grid">
        <div className="chart-section glass-card">
          <h2>Cost by Service</h2>
          <div className="service-breakdown">
            {costSummary?.by_service?.map((service, index) => (
              <div key={index} className="service-item">
                <div className="service-info">
                  <span className="service-name">{service.service_name}</span>
                  <span className="service-cost">${service.total_cost.toFixed(2)}</span>
                </div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    style={{ width: `${service.percentage}%` }}
                  ></div>
                </div>
                <span className="percentage">{service.percentage.toFixed(1)}%</span>
              </div>
            ))}
          </div>
        </div>

        <div className="chart-section glass-card">
          <h2>Cost by Region</h2>
          <div className="region-breakdown">
            {costSummary?.by_region?.map((region, index) => (
              <div key={index} className="region-item">
                <div className="region-info">
                  <span className="region-name">{region.region}</span>
                  <span className="region-cost">${region.total_cost.toFixed(2)}</span>
                </div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    style={{ width: `${region.percentage}%` }}
                  ></div>
                </div>
                <span className="percentage">{region.percentage.toFixed(1)}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="recommendations-section glass-card">
        <h2>Optimization Recommendations</h2>
        
        {/* Idle Instances */}
        {idleInstances.length > 0 && (
          <div className="recommendation-group">
            <h3 className="group-title">Idle EC2 Instances ({idleInstances.length})</h3>
            <div className="recommendation-table">
              <table>
                <thead>
                  <tr>
                    <th>Instance ID</th>
                    <th>Type</th>
                    <th>Region</th>
                    <th>CPU Usage</th>
                    <th>Monthly Savings</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {idleInstances.map((instance, index) => (
                    <tr key={index}>
                      <td className="instance-id">{instance.instance_id}</td>
                      <td>{instance.instance_type}</td>
                      <td>{instance.region}</td>
                      <td>
                        <span className="cpu-badge">
                          {instance.cpu_utilization.toFixed(1)}%
                        </span>
                      </td>
                      <td className="savings-amount">
                        ${instance.potential_savings.toFixed(2)}
                      </td>
                      <td>
                        <button className="action-btn">Stop Instance</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Unattached Volumes */}
        {unattachedVolumes.length > 0 && (
          <div className="recommendation-group">
            <h3 className="group-title">Unattached EBS Volumes ({unattachedVolumes.length})</h3>
            <div className="recommendation-table">
              <table>
                <thead>
                  <tr>
                    <th>Volume ID</th>
                    <th>Type</th>
                    <th>Size</th>
                    <th>Region</th>
                    <th>Monthly Cost</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {unattachedVolumes.map((volume, index) => (
                    <tr key={index}>
                      <td className="volume-id">{volume.volume_id}</td>
                      <td>{volume.volume_type}</td>
                      <td>{volume.size} GB</td>
                      <td>{volume.region}</td>
                      <td className="savings-amount">
                        ${volume.monthly_cost.toFixed(2)}
                      </td>
                      <td>
                        <button className="action-btn delete-btn">Delete Volume</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
