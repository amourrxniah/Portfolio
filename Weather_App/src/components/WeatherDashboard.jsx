import React, { useEffect, useState } from 'react';
import { getCurrentWeather, getForecast, getAstronomy, getTimezone } from '../services/weatherService';
import SearchBar from './SearchBar';
import WeatherCard from './WeatherCard';
import ForecastCard from './ForecastCard';
import Spinner from './Spinner';
import { Line, Bar, Pie, Radar } from 'react-chartjs-2';
import { Chart as ChartJS } from 'chart.js/auto';

const WeatherDashboard = ({ darkMode }) => {
  const [weather, setWeather] = useState(null);
  const [forecast, setForecast] = useState([]);
  const [astronomy, setAstronomy] = useState(null);
  const [timezone, setTimezone] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [history, setHistory] = useState([]);
  const [currentChartIndex, setCurrentIndex] = useState(0);

  const chartTypes = ['line', 'bar', 'pie', 'radar', 'windSpeed'];

  const handleSearch = async (city) => {
    setLoading(true);
    setError('');
    try {
      const weatherData = await getCurrentWeather(city);
      const forecastData = await getForecast(city, 5);
      const astronomyData = await getAstronomy(city);
      const timezoneData = await getTimezone(city);

      setWeather(weatherData);
      setForecast(forecastData.forecast.forecastday);
      setAstronomy(astronomyData);
      setTimezone(timezoneData);

      //add to history (no duplicates)
      setHistory(prev => prev.includes(city) ? prev : [city, ...prev]);
    } catch (err) {
      console.error(err);
      setError('City not found. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getBackgroundClass = () => {
    const condition = weather?.current?.condition?.text?.toLowerCase();
    if (!condition) return 'default';

    if (condition.includes('rain')) return 'rainy';
    if (condition.includes('snow')) return 'snowy';
    if (condition.includes('clear') || condition.includes('sunny')) return 'sunny';
    if (condition.includes('cloud')) return 'cloudy';
    return 'default';
  };

  //geolocation: fetch users city
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(async (position) => {
        const { latitude, longitude } = position.coords;
        try {
          const response = await fetch(`https://api.weatherapi.com/v1/search.json?key=d04ecc3cc8b94c53aec204229240612&q=${latitude}, ${longitude}`);
          const data = await response.json();
          if (data && data.length > 0) {
            handleSearch(data[0].name);
          }
        } catch (err) {
          console.error('Failed to fetch location city:', err);
        }
      });
    }
  }, []);

  const reloadWeather = () => {
    if (weather) {
      handleSearch(weather.location.name);
    }
  };

  //prepare data for the chart
  const temperatureData = {
    labels: forecast.map(day => day.date),
    datasets: [
      {
        label: 'Temperature (°C)',
        data: forecast.map(day => day.day.avgtemp_c),
        fill: false,
        borderColor: '#3498db',
        tension: 0.1
      }
    ]
  };

  const humidityData = {
    labels: forecast.map(day => day.date),
    datasets: [
      {
        label: 'Humidity (%)',
        data: forecast.map(day => day.day.avghumidity),
        backgroundColor: '#74b9ff',
        borderColor: '#3498db',
        borderWidth: 1,
        fill: true,
      }
    ]
  };

  const windSpeedData = {
    labels: forecast.map(day => day.date),
    datasets: [
      {
        label: 'Wind Speed (km/h)',
        data: forecast.map(day => day.day.maxwind_kph),
        backgroundColor: '#55efc4',
        borderColor: '#2ecc71',
        borderWidth: 1,
        fill: true,
      }
    ]
  };

  const pieData = {
    labels: ['Clear', 'Cloudy', 'Rainy', 'Snowy'],
    datasets: [
      {
        label: 'Weather Conditions',
        data: [
          forecast.filter(day => day.day.condition.text.toLowerCase().includes('clear')).length,
          forecast.filter(day => day.day.condition.text.toLowerCase().includes('cloud')).length,
          forecast.filter(day => day.day.condition.text.toLowerCase().includes('rain')).length,
          forecast.filter(day => day.day.condition.text.toLowerCase().includes('snow')).length,
        ],
        backgroundColor: ['#fdcb6e', '#74b9ff', '#55efc4', '#ff7675'],
        borderColor: ['#f39c12', '#2980b9', '#16a085', '#e74c3c'],
        borderWidth: 1,
      }
    ]
  };

  const radarData = {
    labels: forecast.map(day => day.date),
    datasets: [
      {
        label: 'Temperature',
        data: forecast.map(day => day.day.avgtemp_c),
        backgroundColor: 'rgba(52, 152, 219, 0.2)',
        borderColor: '#3498db',
        borderWidth: 1
      }
    ]
  };

  const renderChart = () => {
    switch (chartTypes[currentChartIndex]) {
      case 'line':
        return <Line data={temperatureData} options={{ responsive: true, scales: { y: { beginAtZero: false } } }} />;
      case 'bar':
        return <Bar data={humidityData} options={{ responsive: true, scales: { y: { beginAtZero: false } } }} />;
      case 'pie':
        return <Pie data={pieData} options={{ responsive: true }} />;
      case 'radar':
        return <Radar data={radarData} options={{ responsive: true }} />;
      case 'windSpeed':
        return <Line data={windSpeedData} options={{ responsive: true, scales: { y: { beginAtZero: false } } }} />;
      default:
        return <Line data={temperatureData} options={{ responsive: true, scales: { y: { beginAtZero: false } } }} />;
    }
  };

  const changeChart = (direction) => {
    if (direction === 'next') {
      setCurrentIndex((prevIndex) => (prevIndex + 1) % chartTypes.length);
    } else {
      setCurrentIndex((prevIndex) => (prevIndex - 1 + chartTypes.length) % chartTypes.length);
    }
  };

  return (
    <div className={`dashboard-container ${getBackgroundClass()} ${darkMode ? "dashboard-dark" : ""}`}>

      {/* top search bar */}
      <div className='top-section'>
        <SearchBar onSearch={handleSearch} history={history} />
        {weather && (
          <button className='reload-button' onClick={reloadWeather}>
            🔄</button>
        )}
      </div>

      {/* history buttons */}
      <div className='history-buttons'>
        {history.map((city, index) => (
          <button
            key={index}
            className='history-btn'
            onClick={() => handleSearch(city)}>
            {city}
          </button>
        ))}
      </div>

      {/* error message */}
      {error && <div className='error'>{error}</div>}

      {/* main content area */}
      <div className='main-content'>
        {loading ? (
          <Spinner />
        ) : (
          <>
            <div className="left-content">
              {weather && (
                <div style={{ maxWidth: '250px' }}>
                  <WeatherCard
                    city={weather.location.name}
                    temp={weather.current.temp_c}
                    condition={weather.current.condition.text}
                    iconUrl={weather.current.condition.icon}
                  />
                </div>
              )}

              <div className="forecast-cards" style={{ display: 'flex', gap: '1rem', flexWrap: 'nowrap', overflowX: 'auto' }}>
                {forecast.map((day, index) => (
                  <ForecastCard
                    key={index}
                    date={new Date(day.date).toLocaleDateString('en-GB')}
                    iconUrl={day.day.condition.icon}
                    maxTemp={day.day.maxtemp_c}
                    minTemp={day.day.mintemp_c}
                    condition={day.day.condition.text}
                    darkMode={darkMode}
                  />
                ))}
              </div>
            </div>

            <div className='right-content'>
              <div className='chart-nav-left'><button onClick={() => changeChart('prev')}>&lt;</button></div>
              <div className='chart-area'>{renderChart()}</div>
              <div className='chart-nav-right'><button onClick={() => changeChart('next')}>&gt;</button></div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default WeatherDashboard;