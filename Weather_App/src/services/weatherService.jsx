const BASE_URL = 'https://api.weatherapi.com/v1';
const API_KEY = 'd04ecc3cc8b94c53aec204229240612';

const fetchFromAPI = async (endpoint) => {
    const response = await fetch(`${BASE_URL}${endpoint}&key=${API_KEY}`);
    if (!response.ok) {
        throw new Error('API request failed');
    }
    return response.json();
};

export const getCurrentWeather = async (city) => fetchFromAPI(`/current.json?q=${city}`);
export const getForecast = async (city, days = 3) => fetchFromAPI(`/forecast.json?q=${city}&days=${days}`);
export const searchCity = async (query) => fetchFromAPI(`/search.json?q=${query}`);
export const getAstronomy = async (city, date) => fetchFromAPI(`/astronomy.json?q=${city}&dt=${date}`);
export const getTimezone = async (city) => fetchFromAPI(`/timezone.json?q=${city}`);
export const getFutureWeather = async (city, date) => fetchFromAPI(`/future.json?q=${city}&dt=${date}`);
export const getHistory = async (city, date) => fetchFromAPI(`/history.json?q=${city}&dt=${date}`);