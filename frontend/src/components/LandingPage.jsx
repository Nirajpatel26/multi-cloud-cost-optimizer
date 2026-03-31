import React from 'react';
import './LandingPage.css';

/* ── Proper cloud provider SVG logos ── */

const AwsLogo = () => (
  <svg width="64" height="40" viewBox="0 0 64 40" fill="none">
    {/* "aws" wordmark */}
    <text
      x="2" y="26"
      fontFamily="'Amazon Ember', Arial Black, Arial, sans-serif"
      fontSize="26" fontWeight="900"
      fill="#FF9900"
      letterSpacing="-1"
    >aws</text>
    {/* curved arrow / smile */}
    <path
      d="M6 34 Q32 43 58 34"
      stroke="#FF9900" strokeWidth="3.5"
      fill="none" strokeLinecap="round"
    />
    <path
      d="M53 31 L59 34 L54 37.5"
      stroke="#FF9900" strokeWidth="3.5"
      fill="none" strokeLinecap="round" strokeLinejoin="round"
    />
  </svg>
);

const AzureLogo = () => (
  <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
    {/* Left blue facet */}
    <path d="M20 4 L4 36 L16 36 L28 16 Z" fill="#0078D4"/>
    {/* Right lighter facet */}
    <path d="M27 14 L38 36 L44 36 L30 4 Z" fill="#50B0F0"/>
    {/* Bottom bar joining */}
    <path d="M4 36 L44 36 L38 44 L10 44 Z" fill="#0050A0"/>
  </svg>
);

const GcpLogo = () => (
  <svg width="52" height="42" viewBox="0 0 52 42" fill="none">
    {/* Cloud body */}
    <path
      d="M38 18 C38 11 33 6 26 6 C20 6 15 10 14 16 C10 16 6 19 6 24 C6 29 10 32 15 32 L38 32 C43 32 46 28 46 23 C46 20 42 18 38 18 Z"
      fill="none"
    />
    {/* Colorful stripes — Google Cloud style */}
    {/* Blue segment */}
    <path
      d="M15 32 C10 32 6 29 6 24 C6 19 10 16 14 16 C14 16 13 32 15 32 Z"
      fill="#4285F4"
    />
    {/* Red segment */}
    <path
      d="M14 16 C15 10 20 6 26 6 C23 6 17 10 16 16 Z"
      fill="#EA4335"
    />
    {/* Yellow segment */}
    <path
      d="M26 6 C33 6 38 11 38 18 C35 14 30 12 26 12 Z"
      fill="#FBBC05"
    />
    {/* Green segment */}
    <path
      d="M38 18 C42 18 46 20 46 23 C46 28 43 32 38 32 L15 32 C13 32 14 16 14 16 L16 16 C17 10 23 6 26 6 L26 12 C30 12 35 14 38 18 Z"
      fill="#34A853"
    />
    {/* White inner circle (cloud hole) */}
    <circle cx="26" cy="24" r="7" fill="#34A853"/>
    <circle cx="26" cy="24" r="4.5" fill="white" fillOpacity="0.15"/>
    {/* "G" cut */}
    <path
      d="M26 18 C29.3 18 32 20.7 32 24 C32 27.3 29.3 30 26 30 C22.7 30 20 27.3 20 24 C20 20.7 22.7 18 26 18 Z"
      fill="none"
    />
  </svg>
);

const OciLogo = () => (
  <svg width="56" height="40" viewBox="0 0 56 40" fill="none">
    {/* Oracle ellipse outline — the iconic OCI shape */}
    <ellipse cx="28" cy="20" rx="26" ry="16" fill="#C74634"/>
    <ellipse cx="28" cy="20" rx="18" ry="8" fill="#0D0D0D"/>
    <text
      x="28" y="24.5"
      fontFamily="Arial, sans-serif"
      fontSize="11" fontWeight="800"
      fill="#C74634" textAnchor="middle"
      letterSpacing="1"
    >OCI</text>
  </svg>
);

const providers = [
  {
    id: 'aws',
    name: 'Amazon Web Services',
    status: 'active',
    logo: <AwsLogo />,
    description: 'Analyze EC2, EBS, S3, RDS costs and identify savings across all AWS regions.',
    features: ['Cost Explorer', 'EC2 Optimization', 'EBS Analysis', 'Savings Plans'],
  },
  {
    id: 'azure',
    name: 'Microsoft Azure',
    status: 'active',
    logo: <AzureLogo />,
    description: 'Virtual Machines, Blob Storage, Azure SQL cost optimization coming soon.',
    features: ['VM Rightsizing', 'Blob Storage', 'Azure SQL', 'Advisor'],
  },
  {
    id: 'gcp',
    name: 'Google Cloud',
    status: 'coming_soon',
    logo: <GcpLogo />,
    description: 'Compute Engine, Cloud Storage, BigQuery cost intelligence coming soon.',
    features: ['Compute Engine', 'Cloud Storage', 'BigQuery', 'Recommender'],
  },
  {
    id: 'oci',
    name: 'Oracle Cloud Infrastructure',
    status: 'coming_soon',
    logo: <OciLogo />,
    description: 'Autonomous Database, Compute, Object Storage analysis coming soon.',
    features: ['Autonomous DB', 'Compute Shapes', 'Object Storage', 'Cost Analysis'],
  },
];

const LandingPage = ({ onSelectProvider }) => {
  return (
    <div className="landing-root">
      <nav className="landing-nav">
        <div className="landing-nav-inner">
          <div className="landing-brand">
            <div className="brand-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="#FF9900" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <span className="brand-name">Multi Cloud Cost Optimizer</span>
          </div>
          <div className="nav-links">
            <a href="#providers" className="nav-link">Providers</a>
            <a href="#features" className="nav-link">Features</a>
            <span className="nav-badge">Beta</span>
          </div>
        </div>
      </nav>

      <section className="landing-hero">
        <div className="hero-eyebrow">Multi-Cloud Intelligence</div>
        <h1 className="hero-title">
          Stop overpaying<br />for cloud.
        </h1>
        <p className="hero-sub">
          Spot idle resources, right-size instances, and cut cloud bills
          across every provider — from one place.
        </p>
        <div className="hero-stat-row">
          <div className="hero-stat">
            <span className="hero-stat-num">34%</span>
            <span className="hero-stat-label">avg. savings identified</span>
          </div>
          <div className="hero-stat-divider" />
          <div className="hero-stat">
            <span className="hero-stat-num">3</span>
            <span className="hero-stat-label">minutes to first insight</span>
          </div>
          <div className="hero-stat-divider" />
          <div className="hero-stat">
            <span className="hero-stat-num">4</span>
            <span className="hero-stat-label">cloud providers (soon)</span>
          </div>
        </div>
      </section>

      <section className="providers-section" id="providers">
        <div className="providers-label">Select your cloud provider to get started</div>
        <div className="providers-grid">
          {providers.map((p) => (
            <div
              key={p.id}
              className={`provider-card ${p.status === 'active' ? 'provider-active' : 'provider-disabled'}`}
              onClick={() => p.status === 'active' && onSelectProvider(p.id)}
            >
              {p.status === 'coming_soon' && (
                <div className="coming-soon-tag">Coming Soon</div>
              )}
              <div className="provider-logo-wrap">{p.logo}</div>
              <div className="provider-info">
                <h3 className="provider-name">{p.name}</h3>
                <p className="provider-desc">{p.description}</p>
                <div className="provider-features">
                  {p.features.map((f) => (
                    <span key={f} className="feature-tag">{f}</span>
                  ))}
                </div>
              </div>
              {p.status === 'active' && (
                <div className="provider-cta">
                  Open Dashboard
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      <footer className="landing-footer">
        <span>Multi Cloud Cost Optimizer</span>
        <span className="footer-dot">·</span>
        <span>AWS active · Azure, GCP, OCI in development</span>
      </footer>
    </div>
  );
};

export default LandingPage;
