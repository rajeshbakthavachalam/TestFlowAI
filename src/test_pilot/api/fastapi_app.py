from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from functools import lru_cache
from src.test_pilot.LLMS.groqllm import GroqLLM
from src.test_pilot.LLMS.geminillm import GeminiLLM
from src.test_pilot.graph.graph_builder import GraphBuilder
from src.test_pilot.graph.graph_executor import GraphExecutor
from src.test_pilot.dto.sdlc_request import SDLCRequest
from src.test_pilot.dto.sdlc_response import SDLCResponse
import uvicorn
from contextlib import asynccontextmanager
from src.test_pilot.utils.logging_config import setup_logging
from loguru import logger

## Setup logging level
setup_logging(log_level="DEBUG")

gemini_models = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite", 
    "gemini-2.5-pro-exp-03-25"
]

groq_models = [
    "gemma2-9b-it",
    "llama3-8b-8192",
    "llama3-70b-8192"
]

def load_app():
     uvicorn.run(app, host="0.0.0.0", port=8000)

class Settings:
    def __init__(self):
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")        

@lru_cache()
def get_settings():
    return Settings()

def validate_api_keys(settings: Settings = Depends(get_settings)):
    required_keys = {
        'GEMINI_API_KEY': settings.GEMINI_API_KEY,
        'GROQ_API_KEY': settings.GROQ_API_KEY
    }
    
    missing_keys = [key for key, value in required_keys.items() if not value]
    if missing_keys:
        raise HTTPException(
            status_code=500,
            detail=f"Missing required API keys: {', '.join(missing_keys)}"
        )
    return settings


# Initialize the LLM and GraphBuilder instances once and store them in the app state
@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    llm = GeminiLLM(model=gemini_models[0], api_key=settings.GEMINI_API_KEY).get_llm_model()
    graph_builder = GraphBuilder(llm=llm)
    graph = graph_builder.setup_graph()
    graph_executor = GraphExecutor(graph)
    app.state.llm = llm
    app.state.graph = graph
    app.state.graph_executor = graph_executor
    yield
    # Clean up resources if needed
    app.state.llm = None
    app.state.graph = None
    app.state.graph_executor = None

app = FastAPI(
    title="AgenticSDLC API",
    description="API for automating the software development lifecycle",
    version="1.0.0",
    lifespan=lifespan
)

logger.info("Application starting up...")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "success",
        "message": "Welcome to AgenticSDLC API",
        "version": "1.0.0"
    }

@app.post("/api/v1/sdlc/start", response_model=SDLCResponse)
async def start_sdlc(
    sdlc_request: SDLCRequest,
    settings: Settings = Depends(validate_api_keys)
    ):

    try:
        graph_executor = app.state.graph_executor
        
        if isinstance (graph_executor, GraphExecutor) == False:
            raise Exception("Graph Executor not initialized")
        
        graph_response = graph_executor.start_workflow(sdlc_request.project_name)
        
        logger.debug(f"Start Workflow Response: {graph_response}")
        
        return SDLCResponse(
            status="success",
            message="SDLC process started successfully",
            task_id=graph_response["task_id"],
            state=graph_response["state"]
        )
    
    except Exception as e:
        error_response = SDLCResponse(
            status="error",
            message="Failed to start the process",
            error=str(e)
        )
        return JSONResponse(status_code=500, content=error_response.model_dump())
    
    
@app.post("/api/v1/sdlc/user_stories", response_model=SDLCResponse)
async def start_sdlc(
    sdlc_request: SDLCRequest,
    settings: Settings = Depends(validate_api_keys)
    ):

    try:
        graph_executor = app.state.graph_executor
        
        if isinstance (graph_executor, GraphExecutor) == False:
            raise Exception("Graph Executor not initialized")
        
        graph_response = graph_executor.generate_stories(sdlc_request.task_id, sdlc_request.requirements)
        
        logger.debug(f"Generate Stories Response: {graph_response}")
        
        return SDLCResponse(
            status="success",
            message="User Stories generated successfully",
            task_id=graph_response["task_id"],
            state=graph_response["state"]
        )
    
    except Exception as e:
        error_response = SDLCResponse(
            status="error",
            message="Failed to generate user stories",
            error=str(e)
        )
        return JSONResponse(status_code=500, content=error_response.model_dump())
    

@app.post("/api/v1/sdlc/progress_flow", response_model=SDLCResponse)
async def progress_sdlc(
    sdlc_request: SDLCRequest,
    settings: Settings = Depends(validate_api_keys)
    ):

    try:

        graph_executor = app.state.graph_executor
        
        if isinstance (graph_executor, GraphExecutor) == False:
            raise Exception("Graph Executor not initialized")
        
        graph_response = graph_executor.graph_review_flow(
            sdlc_request.task_id, 
            sdlc_request.status, 
            sdlc_request.feedback,
            sdlc_request.next_node)
        
        logger.debug(f"Flow Node: {sdlc_request.next_node}")
        logger.debug(f"Progress Flow Response: {graph_response}")
        
        return SDLCResponse(
            status="success",
            message="Flow progressed successfully to next step",
            task_id=graph_response["task_id"],
            state=graph_response["state"]
        )
    
    except Exception as e:
        error_response = SDLCResponse(
            status="error",
            message="Failed to progress the flow",
            error=str(e)
        )
        return JSONResponse(status_code=500, content=error_response.model_dump())