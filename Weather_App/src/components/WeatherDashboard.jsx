import React, { useState } from 'react';
import { getCurrentWeather, getForecast, getAstronomy, getTimezone } from '../services/weatherService';
import SearchBar from './SearchBar';
import WeatherCard from './WeatherCard';
import ForecastCard from './ForecastCard';
import Spinner from './Spinner';

const WeatherDashboard = () => {
  const [weather, setWeather] = useState(null);
  const [forecast, setForecast] = useState([]);
  const [astronomy, setAstronomy] = useState(null);
  const [timezone, setTimezone] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (city) => {
    setLoading(true);
    setError('');
    try {
      const weatherData = await getCurrentWeather(city);
      const forecastData = await getForecast(city, 3);
      const astronomyData = await getAstronomy(city);
      const timezoneData = await getTimezone(city);

      setWeather(weatherData);
      setForecast(forecastData.forecast.forecastday);
      setAstronomy(astronomyData);
      setTimezone(timezoneData);
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

  return (
    <div className={`dashboard ${getBackgroundClass()}`}>
      <SearchBar onSearch={handleSearch}/>

      {loading && <Spinner/>}
      {error && <p className='error'>{error}</p>}

      {weather && (
        <WeatherCard 
          city={weather.location.name}
          temp={weather.current.temp_c}
          condition={weather.current.condition.text}
          iconUrl={weather.current.condition.icon} />
      )}

      {forecast.length > 0 && (
        <div className="forecast-grid">
          {forecast.map((day) => (
            <ForecastCard
              key={day.date}
              date={day.date}
              iconUrl={day.day.condition.icon}
              maxTemp={day.day.maxtemp_c}
              minTemp={day.day.mintemp_c}
              condition={day.day.condition.text} />
          ))}
        </div>
      )}
    </div>
  );
};

export default WeatherDashboard;