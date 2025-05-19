from pydantic import BaseModel
from typing import Optional
from src.test_pilot.state.sdlc_state import SDLCState
from typing import Dict, Any

class SDLCResponse(BaseModel):
    status: str
    message: str
    task_id: Optional[str] = None
    state: Optional[Dict[str, Any]] = None
    error: Optional[str] = None