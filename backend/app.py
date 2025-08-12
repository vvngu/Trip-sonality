"""
Main backend entry point: Receives user requests, calls the refactored AutoGen Agent workflow 
to generate itineraries, and stores results in MongoDB.

Database:
  - Name: Specified by MONGODB_DB environment variable (default: "trip_agent")
  - Collection: "conversations", stores session_id, user input, final itinerary JSON and timestamps.
"""
import os
import json
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException as FastAPIHTTPException 
from pydantic import BaseModel, Field
from typing import Optional, Any, List, Dict 
import motor.motor_asyncio
from fastapi.middleware.cors import CORSMiddleware

# Import the refactored Agent workflow execution function
from autogen_itinerary import run_autogen_workflow

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "trip_agent")
if not MONGODB_URI:
    raise RuntimeError("Please set the MONGODB_URI environment variable in your .env file")

app = FastAPI(
    title="Trip-sonality API",
    description="API for generating personalized travel itineraries using an AutoGen multi-agent system.",
    version="1.0.0"
)

# Configure CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["GET", "POST"],  
    allow_headers=["*"],  
)

mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
db = mongo_client[MONGODB_DB]
conversations = db.get_collection("conversations")

# Define user input Pydantic model (corresponds to query form in flowchart)
# "User's MBTI type (one of 16 types)"
# "User's budget (optional, USD)"
# "User's natural language query, including destination, days, preferences etc."
# "User's possible existing itinerary (optional, JSON object)"
class UserInput(BaseModel):
    mbti: str = Field(..., description="user's MBTI type ")
    budget: Optional[int] = Field(None, description="User's budget ")
    query: str = Field(..., description="user's natural language query, including destination, number of days, preferences, etc.")
    current_itinerary: Optional[Dict[str, Any]] = Field(None, description="Existing itineraries that the user may provide (optional, JSON object)")

# Define API response model - simplified to only include session_id and raw JSON data
class ItineraryResponse(BaseModel):
    session_id: str
    data: Any = Field(..., description="Original itinerary JSON data")

@app.on_event("startup")
async def startup_db_client():
    try:
        await mongo_client.admin.command('ping')
        print("Successfully connected to MongoDB.")
        await conversations.create_index("session_id", unique=True)
        await conversations.create_index("updated_at")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    print("Closing MongoDB connection...")
    mongo_client.close()

@app.post("/plan", response_model=ItineraryResponse, tags=["Itinerary Planning"])
async def generate_plan(user_input: UserInput):
    """
    # Receive user's itinerary planning request, call Agent workflow to generate itinerary,
    # Store raw JSON result in MongoDB and return directly to frontend
    """
    session_id = str(uuid.uuid4())
    print(f"Received new plan request. Session ID: {session_id}")
    print(f"User Input: {user_input.dict()}")
   
    # Prepare input dictionary to pass to Agent workflow   
    workflow_input = {
        "mbti": user_input.mbti,
        "Budget": user_input.budget,
        "Query": user_input.query,
        "CurrentItinerary": user_input.current_itinerary
    }
    # Remove keys with None values to avoid passing null  
    workflow_input = {k: v for k, v in workflow_input.items() if v is not None}

    try:
        # Execute Agent workflow
        print("--- Calling AutoGen Workflow --- ")
        result_data = await run_autogen_workflow(workflow_input)
        print("--- AutoGen Workflow Finished Successfully --- ")
        # Don't separate data anymore, use raw result directly
        raw_data = result_data

    except FastAPIHTTPException as http_exc:
        print(f"HTTP Exception during workflow: {http_exc.status_code} - {http_exc.detail}")
        raise http_exc
    except Exception as e:
        print(f"Error during AutoGen workflow execution: {e}")
        raise FastAPIHTTPException(
            status_code=500,
            detail=f"An internal error occurred during itinerary generation: {e}"
        )

    record = {
        "session_id": session_id,
        "user_input": user_input.dict(),
        "data": raw_data,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    try:
        insert_result = await conversations.insert_one(record)
        print(f"Successfully inserted record into MongoDB with ID: {insert_result.inserted_id}")
    except Exception as e:
        print(f"Error saving record to MongoDB: {e}")

    response_data = {
        "session_id": session_id,
        "data": raw_data 
    }
    return response_data

@app.get("/health", tags=["Health Check"])
async def health_check():
    return {"status": "ok"}

# Local run (optional)
if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server locally on http://localhost:8000")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)