import React, { useState } from 'react';

const SearchBar = ({ onSearch }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) {
        onSearch(input);
        setInput('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className='search-bar'>
        <input type='text' value={input} onChange={(e) => setInput(e.target.value)} placeholder='Enter city name...' />
        <button type='submit'>Search</button>
    </form>
  );
};

export default SearchBar;