import React from 'react';

function App() {
    const handleClick = async () => {
        const data = { message: "Hello, server!" };
        try {
            const response = await fetch('http://localhost:5000/send-json', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });
            const result = await response.json();
            console.log('Server response:', result);
        } catch (error) {
            console.error('Error sending data to the server:', error);
        }
    };

    return (
        <div>
            <button onClick={handleClick}>Send JSON to Server</button>
        </div>
    );
}

export default App;
