import React from "react";

const ForecastCard = ({ date, iconUrl, maxTemp, minTemp, condition }) => {
    return (
        <div className="forecast-card" >
            <p>{date}</p>
            <img src={iconUrl} alt={condition} className="forecast-icon"/>
            <p>{maxTemp}° / {minTemp}°</p>
            <p>{condition}</p>
        </div>
    );
};

export default ForecastCard;