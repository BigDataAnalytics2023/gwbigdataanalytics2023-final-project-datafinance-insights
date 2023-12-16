import React, { useState, useEffect } from 'react';
import MyForm from './MyForm.js'; // Make sure this path matches the location of your MyForm component
import './App.css';


const App = () => {
  return (
    <div style={{ backgroundColor: '#120323', padding: '20px', color: 'white', }}>
        <h1 class='center'>Data Finance Insights</h1>
        <h2 class='center'>Stock Market Predictor</h2>
      <div class='center'><MyForm /></div>
    </div>
  );
};

export default App;
