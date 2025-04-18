import React, { useState } from "react";
import { getCurrentWeather, getForecast, getAstronomy, getTimezone  } from "../services/weatherService";
import SearchBar from "./SearchBar";
import WeatherCard from "./WeatherCard";

const WeatherDashboard = () => {
    const [weatherData, setWeatherData] = useState(null);
    const [forecastData, setForecastData] = useState(null);
    const [astronomyData, setAstronomyData] = useState(null);
    const [timezoneData, setTimezoneData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSearch = async (city) => {
        setLoading(true);
        setError('');
        try {
            const today = new Date().toISOString().split('T')[0];
            const [current, forecast, astronomy, timezone] = await Promise.all([
                getCurrentWeather(city),
                getForecast(city),
                getAstronomy(city, today),
                getTimezone(city),
            ]);
            setWeatherData(current);
            setForecastData(forecast);
            setAstronomyData(astronomy);
            setTimezoneData(timezone);
        } catch (err) {
            setError('Failed to fetch data.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="dashboard">
            <SearchBar onSearch={handleSearch} />
            {loading && <p>Loading...</p>}
            {error && <p className="error">{error}</p>}
            <div className="cards-grid">
                {weatherData && <WeatherCard title="Current Weather" data={weatherData} />}
                {forecastData && <WeatherCard title="Forecast" data={forecastData} />}
                {astronomyData && <WeatherCard title="Astronomy" data={astronomyData} />}
                {timezoneData && <WeatherCard title="Timezone" data={timezoneData} />}
            </div>
        </div>
    );
};

export default WeatherDashboard;