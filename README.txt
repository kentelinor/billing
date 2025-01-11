this projects emulates the part i will say i wrote inmy billing project. 
the client - is a VM sending a json message about it's status
the server - is a server that gets all of the json messages from all of the VMs and publishes them to a rabbit MQ queue
the consumer - reads the messages in the rabbitMQ queue (called 'my_queue') and does 2 things: 
    1. writes them to an s3 bucket for auditing
    2. sends to an end point that i haven't implemented that it's goal is to check if the status of the VM as written in the json message requires writing to DB and if so - writes to DB 




#run command
docker-compose up --build

#verify setup
RabbitMQ: Access the RabbitMQ management interface at http://localhost:15672/ (default credentials: guest / guest).
Server: The Flask server will be running at http://localhost:5000/.
Client: The client will automatically send a JSON message to the server when its container starts.


#Logs: Monitor the logs of all services:
docker-compose logs -f