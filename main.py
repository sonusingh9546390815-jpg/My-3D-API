from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Data models for incoming requests
class PhysicsInput(BaseModel):
    mass: float
    velocity: float
    angle: float

class LogicInput(BaseModel):
    action: str
    parameters: dict

@app.get("/")
def home():
    return {
        "status": "Online",
        "message": "Physics, Logic & Animation API Server is Live! 🚀"
    }

# 1. Physics Engine Endpoint (e.g., gravity, force, or trajectory calculations)
@app.post("/api/physics")
def run_physics_simulation(data: PhysicsInput):
    # Example physics calculation (Force / Momentum / Trajectory logic)
    momentum = data.mass * data.velocity
    return {
        "module": "physics",
        "input_data": data.dict(),
        "calculated_momentum": momentum,
        "status": "Simulation computed successfully"
    }

# 2. Custom Logic Endpoint (e.g., game rules, state management, or data processing)
@app.post("/api/logic")
def process_custom_logic(data: LogicInput):
    # Add your custom business or game logic here
    result = f"Executed action '{data.action}' successfully."
    return {
        "module": "logic",
        "action": data.action,
        "result": result,
        "processed_parameters": data.parameters
    }

# 3. Animation Data Endpoint (e.g., keyframes, sequences, or rig data)
@app.get("/api/animation/{anim_name}")
def get_animation_sequence(anim_name: str):
    # Return animation metadata, keyframes, or transform data
    animations_database = {
        "walk": {"frames": 30, "loop": True, "speed": 1.2},
        "jump": {"frames": 15, "loop": False, "speed": 1.5},
        "idle": {"frames": 60, "loop": True, "speed": 1.0}
    }
    
    if anim_name not in animations_database:
        raise HTTPException(status_code=404, detail="Animation not found")
        
    return {
        "module": "animation",
        "animation_name": anim_name,
        "data": animations_database[anim_name]
    }
