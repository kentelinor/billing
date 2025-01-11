export const generateRandomJson = () => {
    const statuses = ['pause', 'active'];
    const randomStatus = statuses[Math.floor(Math.random() * statuses.length)];
  
    return {
      vm: 'vm1',
      status: randomStatus,
      timestamp: new Date().toISOString(), // ISO format of current date and time
    };
  };
  