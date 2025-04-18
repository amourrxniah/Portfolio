import React from "react";

const WeatherCard = ({ title, data }) => {
    return (
        <div className="weather-card">
            <h3>{title}</h3>
            <pre>{JSON.stringify(data, null, 2)}</pre>
        </div>
    );
};

export default WeatherCard;