import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import Chatbot from './components/Chatbot';

function App() {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : false;
  });

  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
    document.body.className = darkMode ? 'dark-mode' : 'light-mode';
  }, [darkMode]);

  return (
    <div className={`App ${darkMode ? 'dark-mode' : 'light-mode'}`}>
      <header className="app-header">
        <div className="header-top">
          <h1>🇮🇳 Indian Market Predictor</h1>
          <button 
            className="theme-toggle"
            onClick={() => setDarkMode(!darkMode)}
            title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>
        <p>AI-Powered Real-Time Analysis for Gold, Silver & Stocks</p>
      </header>

      <Dashboard />
      
      <div style={{ height: '40px' }}></div>
      
      <Chatbot />
      
      <footer className="app-footer">
        <p>💡 Powered by AI | Data refreshed every 5 minutes</p>
        <p style={{ marginTop: '8px' }}>⚠️ For informational purposes only. Not financial advice.</p>
      </footer>
    </div>
  );
}

export default App;
