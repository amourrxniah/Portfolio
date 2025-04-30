import React, { useState } from "react";
import LandingPage from "./components/LandingPage";
import WeatherDashboard from './components/WeatherDashboard';
import ThemeToggle from "./components/ThemeToggle";
import './App.css';

function App() {
  const [started, setStarted] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  const handleStart = () => {
    setStarted(true);
  };

  const toggleDarkMode = () => {
    setDarkMode(prev => !prev);
  };

  return (
    <div className={`app ${darkMode ? "app-dark" : ''}`}>
      <ThemeToggle darkMode={darkMode} toggleDarkMode={toggleDarkMode}/>
      <div className={started ? 'fade-in' : ''}>
        {started ? <WeatherDashboard darkMode={darkMode}/> : <LandingPage onStart={handleStart}/>}
      </div>
    </div>
  );
}

export default App;