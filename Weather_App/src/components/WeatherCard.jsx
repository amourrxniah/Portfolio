import React from "react";

const WeatherCard = ({ city, temp, condition, iconUrl }) => {
    return (
        <div className="weather-card">
            <h2>{city}</h2>
            <img src={iconUrl} alt={condition} className="weather-icon" />
            <h1>{temp}°C</h1>
            <p>{condition}</p>
        </div>
    );
};

export default WeatherCard;