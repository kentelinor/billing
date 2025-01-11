export const sendJsonToServer = async (json) => {
    try {
      const response = await fetch('http://localhost:5000/publish', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(json),
      });
  
      if (response.status === 202) {
        console.log('Success: JSON sent to RabbitMQ');
      } else {
        console.error('Failed to send JSON:', response.status);
      }
    } catch (error) {
      console.error('Error sending JSON:', error);
      throw error;  // Rethrow the error to be caught in the calling function
    }
  };
  