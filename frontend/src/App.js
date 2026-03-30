import React, { useState } from 'react';
import LandingPage from './components/LandingPage';
import Dashboard from './components/Dashboard';
import './styles/App.css';

function App() {
  const [selectedProvider, setSelectedProvider] = useState(null);

  if (!selectedProvider) {
    return <LandingPage onSelectProvider={setSelectedProvider} />;
  }

  return (
    <div className="App">
      <Dashboard provider={selectedProvider} onBack={() => setSelectedProvider(null)} />
    </div>
  );
}

export default App;
