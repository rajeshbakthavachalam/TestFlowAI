from src.test_pilot.state.sdlc_state import SDLCState, UserStoryList
from langchain_core.messages import SystemMessage

class ProjectRequirementNode:
    """
    Graph Node for the project requirements
    
    """
    
    def __init__(self, model):
        self.llm = model
      
    def initialize_project(self, state: SDLCState):
        """
            Performs the project initilazation
        """
        return state
    
    def get_user_requirements(self, state: SDLCState):
        """
            Gets the requirements from the user
        """
        pass
    
    def generate_user_stories(self, state: SDLCState):
        """
        Auto-generate highly detailed and accurate user stories for each requirement.
        """
        project_name = state["project_name"]
        requirements = state["requirements"]
        feedback_reason = state.get("user_stories_feedback", None)

        prompt = f"""
        You are a senior software analyst specializing in Agile SDLC and user story generation. 
        Your task is to generate **a separate and detailed user story for EACH requirement** from the project details below.

        ---
        **Project Name:** "{project_name}"

        **Requirements:** "{requirements}

        ---
        **Instructions for User Story Generation:**
        - Create **one user story per requirement**.
        - Assign a **unique identifier** (e.g., US-001, US-002, etc.).
        - Provide a **clear and concise title** summarizing the user story.
        - Write a **detailed description** using the "As a [user role], I want [goal] so that [benefit]" format.
        - Assign a **priority level** (1 = Critical, 2 = High, 3 = Medium, 4 = Low).
        - Define **acceptance criteria** with bullet points to ensure testability.
        - Use **domain-specific terminology** for clarity.
        
        {f"Additionally, consider the following feedback while refining the user stories: {feedback_reason}" if feedback_reason else ""}

        ---
        **Expected Output Format (for each user story):**
        - Unique Identifier: US-XXX
        - Title: [User Story Title]
        - Description:  
        - As a [user role], I want [feature] so that [benefit].
        - Priority: [1-4]
        - Acceptance Criteria:
        - [Criteria 1]
        - [Criteria 2]
        - [Criteria 3]

        Ensure that the user stories are **specific, testable, and aligned with Agile principles**.
        """

        llm_with_structured = self.llm.with_structured_output(UserStoryList)
        response = llm_with_structured.invoke(prompt)
        state["user_stories"] = response
        return state
    
    def review_user_stories(self, state: SDLCState):
        return state
    
    def revise_user_stories(self, state: SDLCState):
        pass
    
    def review_user_stories_router(self, state: SDLCState):
        return state.get("user_stories_review_status", "approved")  # default to "approved" if not present