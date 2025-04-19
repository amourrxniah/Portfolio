import React, { useState } from "react";
import WeatherDashboard from './components/WeatherDashboard';
import ThemeToggle from "./components/ThemeToggle";

function App() {
  const [darkMode, setDarkMode] = useState(false);

  const toggleDarkMode = () => {
    setDarkMode(prev => !prev);
  };

  return (
    <div className={`app ${darkMode ? 'dark' : ''}`}>
      <ThemeToggle darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
      <main>
        <h1>Weather App</h1>
        <WeatherDashboard />
      </main>
    </div>
  );
}

export default App;