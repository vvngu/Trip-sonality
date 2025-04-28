# backend/app.py
"""
Main backend entry point using MongoDB to store session context.

Database:
  - Name: specified by the MONGODB_DB env var (default: "trip_agent")
  - Collection: "conversations" stores session records, including session_id, user_input, itinerary, and updated_at timestamp.
"""
import os
import json
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import motor.motor_asyncio

from autogen_itinerary import run_agents

# Load environment variables from .env
load_dotenv()

# MongoDB configuration
MONGODB_URI = os.getenv("MONGODB_URI")  # e.g., mongodb+srv://user:pass@cluster.mongodb.net/dbname
MONGODB_DB = os.getenv("MONGODB_DB", "trip_agent")
if not MONGODB_URI:
    raise RuntimeError(
        "Please set the MONGODB_URI environment variable in your .env file."
    )

# Initialize FastAPI and MongoDB client
app = FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
db = client[MONGODB_DB]
conversations = db.get_collection("conversations")

# Request model for itinerary planning
class ItineraryRequest(BaseModel):
    session_id: Optional[str] = None
    budget: str
    dates: str
    field: str
    location: str
    mbti: str
    theme: str

@app.on_event("shutdown")
async def shutdown_db():
    """Close the MongoDB client when the app shuts down."""
    client.close()

@app.post("/plan")
async def plan(req: ItineraryRequest):
    """
    Receive user input, maintain session context, and return updated itinerary.

    - If session_id is missing, a new one is generated.
    - User input is merged with any previous input.
    - The _previous_itinerary is passed to the agents for context-based revision.
    - The generated itinerary is stored in MongoDB and returned as a TypeScript code string.
    """
    # 1. Generate or retrieve session_id
    session_id = req.session_id or str(uuid.uuid4())

    # 2. Fetch existing session record
    record = await conversations.find_one({"session_id": session_id})

    # 3. Merge new input with existing user_input
    new_input = req.dict(exclude={"session_id"})
    if record:
        merged_input = {**record.get("user_input", {}), **new_input}
        previous_itinerary = record.get("itinerary")
    else:
        merged_input = new_input
        previous_itinerary = None

    # 4. Prepare payload for agents, include previous itinerary if available
    payload = merged_input.copy()
    if previous_itinerary is not None:
        payload["_previous_itinerary"] = previous_itinerary

    # 5. Run multi-agent itinerary generation
    result_str = await run_agents(json.dumps(payload))

    # 6. Attempt to parse the returned JSON itinerary
    try:
        new_itinerary = json.loads(result_str)
    except json.JSONDecodeError:
        new_itinerary = None

    # 7. Upsert the session record in MongoDB with updated data and timestamp
    now = datetime.now(timezone.utc)
    if record:
        await conversations.update_one(
            {"session_id": session_id},
            {"$set": {
                "user_input": merged_input,
                "itinerary": new_itinerary,
                "updated_at": now
            }}
        )
    else:
        await conversations.insert_one({
            "session_id": session_id,
            "user_input": merged_input,
            "itinerary": new_itinerary,
            "updated_at": now
        })

    # 8. Return session_id and the TypeScript code string
    return {"session_id": session_id, "itinerary_ts": result_str}

# To run:
# uvicorn app:app --reload
# Dependencies: fastapi, motor, python-dotenv
