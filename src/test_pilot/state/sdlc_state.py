from pydantic import BaseModel, Field
from typing import TypedDict, Any, Dict, Literal, Optional
import json
import src.test_pilot.utils.constants as const

    
class UserStories(BaseModel):
    id: int = Field(...,description="The unique identifier of the user story")
    title: str = Field(...,description="The title of the user story")
    description: str = Field(...,description="The description of the user story")
    priority: int = Field(...,description="The priority of the user story")
    acceptance_criteria: str = Field(...,description="The acceptance criteria of the user story")

class UserStoryList(BaseModel):
    user_stories: list[UserStories]

class DesignDocument(BaseModel):
    functional: str = Field(..., description="Holds the functional design Document")
    technical: str = Field(..., description="Holds the technical design Document")
   
class SDLCState(TypedDict):
    """
    Represents the structure of the state used in the SDLC graph

    """    
    next_node: str = const.PROJECT_INITILIZATION
    project_name: str
    requirements: list[str]
    user_stories: UserStoryList
    user_stories_feedback: str
    user_stories_review_status: str
    design_documents: DesignDocument
    design_documents_feedback: str
    design_documents_review_status: str
    code_generated: str
    code_review_comments: str
    code_review_feedback: str
    code_review_status: str
    security_recommendations: str
    security_review_comments: str
    security_review_status: str
    test_cases: str
    test_case_review_status: str
    test_case_review_feedback: str
    qa_testing_comments: str
    qa_testing_status: str
    qa_testing_feedback: str
    deployment_status: str
    deployment_feedback: str
    artifacts: dict[str, str]
    
    
    
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        # Check if the object is any kind of Pydantic model
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        # Or check for specific classes if needed
        # if isinstance(obj, UserStories) or isinstance(obj, DesignDocument):
        #     return obj.model_dump()
        return super().default(obj)
    

class STLCState(TypedDict):
    """
    Represents the structure of the state used in the STLC graph
    """
    next_node: str
    project_name: str
    requirement_analysis_data: str
    requirement_analysis_feedback: str
    requirement_analysis_review_status: str
    test_planning_data: str
    test_planning_feedback: str
    test_planning_review_status: str
    test_case_development_data: str
    test_case_development_feedback: str
    test_case_development_review_status: str
    test_environment_setup_data: str
    test_environment_setup_feedback: str
    test_environment_setup_review_status: str
    test_execution_data: str
    test_execution_feedback: str
    test_execution_review_status: str
    test_closure_data: str
    test_closure_feedback: str
    test_closure_review_status: str
    artifacts: dict[str, str]
    
    
    