import React, { useState } from 'react';

const SearchBar = ({ darkMode, onSearch }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) {
        onSearch(input);
        setInput('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className={`search-bar ${darkMode ? 'search-dark' : ''}`}>
        <input 
          type='text' 
          value={input} 
          onChange={(e) => setInput(e.target.value)} 
          placeholder='Enter city name...' />
        <button type='submit'>🔍</button>
    </form>
  );
};

export default SearchBar;