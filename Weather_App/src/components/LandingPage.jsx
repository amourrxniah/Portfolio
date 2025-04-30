import React from "react";

const LandingPage = ({ onStart }) => {
    return (
        <div className="landing">
            <img src="./public/weather.png" alt="Weather Icon" className="landing-icon" />
            <h1 className="landing-title">Welcome to Weatherly</h1>
            <p className="landing-subtitle">Your modern weather companion</p>
            <button className="start-button" onClick={onStart}>Get Started</button>
        </div>
    );
};

export default LandingPage;