import redis
import psycopg2
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from typing import List
import os

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for your app (allow all origins or specific ones)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, you can specify a list of allowed domains
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Redis connection
r = redis.StrictRedis(host=os.getenv('REDIS_HOST', 'localhost'), port=int(os.getenv('REDIS_PORT', 6379)), db=0, decode_responses=True)


# PostgreSQL DB connection
db_config = {
    "host": "readreplica1.cbgysoossqru.eu-north-1.rds.amazonaws.com",
    "port": 5432,
    "dbname": "vms",
    "user": "postgres",
    "password": os.getenv("VMEVENTS_READ_REPLICA_DB_PASSWORD")
}

# Function to get data from PostgreSQL
def get_data_from_db(query: str):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        print(f"Error fetching data from DB: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Function to get data, first checking the Redis cache
def get_data(query: str):
    # Check if the data is in the cache
    cache_result = redis_client.get(query)
    if cache_result:
        print("Cache hit!")
        return json.loads(cache_result)  # Deserialize from JSON
    else:
        print("Cache miss!")
        # Fetch data from DB and store it in Redis
        db_result = get_data_from_db(query)
        if db_result:
            redis_client.set(query, json.dumps(db_result))  # Store in Redis as JSON
            return db_result
        return []

class VM(BaseModel):
    id: int
    name: str
    created_at: str


@app.get("/vms", response_model=List[VM])
def get_events():
    # Sample query, adjust it to fit your schema
    query = "SELECT id, name, created_at FROM vms"
    result = get_data(query)

    # Convert the result to VM model format
    events = [{"vm_id": row[0], "name": row[1], "created_at": row[2]} for row in result]
    return events

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)
