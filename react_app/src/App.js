import React, { useState, useEffect } from 'react';
import logo from './logo.svg';
import './App.css';
import { generateRandomJson } from './utils/randomJson';  // Importing random JSON generator
import { sendJsonToServer } from './utils/api';  // Importing the function to send JSON to the server

function App() {
  // State to hold the generated random JSON
  const [randomJson, setRandomJson] = useState(null);

  // Generate random JSON when the component mounts (and on refresh)
  useEffect(() => {
    setRandomJson(generateRandomJson());
  }, []); // Empty dependency array means it runs once on mount

  // Function to handle button click (sending JSON to rabbit mq)
  const handleButtonClick = () => {
    sendJsonToServer(randomJson)
      .then(() => {
        console.log('Success: JSON sent to RabbitMQ');
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  };

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <h1>Random JSON Generator</h1>
        {randomJson && (
          <pre className="json-display">
            {JSON.stringify(randomJson, null, 2)} {/* Format the JSON for display */}
          </pre>
        )}
        <button className="App-button" onClick={handleButtonClick}>
          Send the Generated JSON to RabbitMQ
        </button>
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

export default App;
