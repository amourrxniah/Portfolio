import React from "react";

const ThemeToggle = ({ darkMode, toggleDarkMode }) => {
    return (
        <button onClick={toggleDarkMode} className="theme-toggle">
            {darkMode ? '☀️ Light' : '🌙 Dark'}
        </button>
    );
};

export default ThemeToggle;