import React from "react";

const ForecastCard = ({ date, iconUrl, maxTemp, minTemp, condition, darkMode }) => {
    return (
        <div className={`forecast-card ${darkMode ? 'forecast-dark' : ''}`}>
            <p>{date}</p>
            <img src={iconUrl} alt={condition} className="forecast-icon"/>
            <p>{maxTemp}° / {minTemp}°</p>
            <p>{condition}</p>
        </div>
    );
};

export default ForecastCard;