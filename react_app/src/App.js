import React, { useState, useEffect } from 'react';
import './App.css';  // Import the CSS file
import { generateRandomJson } from './utils/randomJson';  // Importing random JSON generator
import { sendJsonToServer } from './utils/api';  // Importing the function to send JSON to the server

function App() {
  // State to hold the generated random JSON
  const [randomJson, setRandomJson] = useState(null);
  const [events, setEvents] = useState([]); // State to hold the events from the server

  // Generate random JSON when the component mounts (and on refresh)
  useEffect(() => {
    setRandomJson(generateRandomJson());

    // Fetch events from the Flask server
    const fetchEvents = async () => {
      try {
        const response = await fetch('http://localhost:8000/events'); // Adjust the URL as needed
        if (response.ok) {
          const data = await response.json();
          console.log(data);
          setEvents(data);  // Update events state with fetched data
        } else {
          console.error('Failed to fetch events');
        }
      } catch (error) {
        console.error('Error fetching events:', error);
      }
    };

    fetchEvents();
    const interval = setInterval(fetchEvents, 5000); // Refresh events every 5 seconds
    return () => clearInterval(interval); // Clean up the interval when the component is unmounted
  }, []); // Empty dependency array means it runs once on mount

  // Function to handle button click (sending JSON to RabbitMQ)
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
      <div className="main-container">
        <div className="events-container">
          <h3>Event Logs</h3>
          <textarea
            className="events-textbox"
            value={events.map(
              (event) =>
                `${event.vm_name}: ${event.event} at ${event.created_at}`
            ).join("\n")}
            readOnly
          />
        </div>

        <div className="content-container">
          <header className="App-header">
            <h1>Random JSON Generator</h1>
            {randomJson && (
              <pre className="json-display">
                {JSON.stringify(randomJson, null, 2)}
              </pre>
            )}
            <button className="App-button" onClick={handleButtonClick}>
              Send the Generated JSON to RabbitMQ
            </button>
            
          </header>
        </div>
      </div>
    </div>

  );
}

export default App;
