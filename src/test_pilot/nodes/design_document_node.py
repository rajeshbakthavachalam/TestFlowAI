from src.test_pilot.state.sdlc_state import SDLCState, DesignDocument
from src.test_pilot.utils.Utility import Utility
from loguru import logger

class DesingDocumentNode:
    """
    Graph Node for the Desing Documents
    
    """
    
    def __init__(self, model):
        self.llm = model
        self.utility = Utility()
    
    def create_design_documents(self, state: SDLCState):
        """
        Generates the Design document functional and technical
        """
        logger.info("----- Creating Design Document ----")
        requirements = state.get('requirements', '')
        user_stories = state.get('user_stories', '')
        project_name = state.get('project_name', '')
        design_feedback = None
        
        if 'design_documents' in state:
            design_feedback = state.get('design_documents_feedback','')

        functional_documents = self.generate_functional_design(
            project_name=project_name,
            requirements=requirements,
            user_stories=user_stories,
            design_feedback=design_feedback
        )

        technical_documents = self.generate_technical_design(
            project_name=project_name,
            requirements=requirements,
            user_stories=user_stories,
            design_feedback=design_feedback
        )

        design_documents = DesignDocument(
            functional=functional_documents,
            technical = technical_documents
        )

        return {
            **state,
            "design_documents": design_documents,
            "technical_documents": technical_documents
        }
    
    def generate_functional_design(self, project_name, requirements, user_stories, design_feedback):
        """
        Helper method to generate functional design document
        """
        logger.info("----- Creating Functional Design Document ----")
        prompt = f"""
            Create a comprehensive functional design document for {project_name} in Markdown format.
    
            The document should use proper Markdown syntax with headers (# for main titles, ## for sections, etc.), 
            bullet points, tables, and code blocks where appropriate.
            
            Requirements:
            {self.utility.format_list(requirements)}
            
            User Stories:
            {self.utility.format_user_stories(user_stories)}

             {f"When creating this functional design document, please incorporate the following feedback about the requirements: {design_feedback}" if design_feedback else ""}
            
            The functional design document should include the following sections, each with proper Markdown formatting:
            
            # Functional Design Document: {project_name}
            
            ## 1. Introduction and Purpose
            ## 2. Project Scope
            ## 3. User Roles and Permissions
            ## 4. Functional Requirements Breakdown
            ## 5. User Interface Design Guidelines
            ## 6. Business Process Flows
            ## 7. Data Entities and Relationships
            ## 8. Validation Rules
            ## 9. Reporting Requirements
            ## 10. Integration Points
            
            Make sure to maintain proper Markdown formatting throughout the document.
        """
        # invoke the llm
        response = self.llm.invoke(prompt)
        return response.content    
    
    def generate_technical_design(self, project_name, requirements, user_stories, design_feedback):
            """
                Helper method to generate technical design document in Markdown format
            """
            logger.info("----- Creating Technical Design Document ----")
            prompt = f"""
                Create a comprehensive technical design document for {project_name} in Markdown format.
                
                The document should use proper Markdown syntax with headers (# for main titles, ## for sections, etc.), 
                bullet points, tables, code blocks, and diagrams described in text form where appropriate.
                
                Requirements:
                {self.utility.format_list(requirements)}
            
                User Stories:
                {self.utility.format_user_stories(user_stories)}

                {f"When creating this technical design document, please incorporate the following feedback about the requirements: {design_feedback}" if design_feedback else ""}
                
                The technical design document should include the following sections, each with proper Markdown formatting:
                
                # Technical Design Document: {project_name}

                ## 1. System Architecture
                ## 2. Technology Stack and Justification
                ## 3. Database Schema
                ## 4. API Specifications
                ## 5. Security Considerations
                ## 6. Performance Considerations
                ## 7. Scalability Approach
                ## 8. Deployment Strategy
                ## 9. Third-party Integrations
                ## 10. Development, Testing, and Deployment Environments
                
                For any code examples, use ```language-name to specify the programming language.
                For database schemas, represent tables and relationships using Markdown tables.
                Make sure to maintain proper Markdown formatting throughout the document.
            """
            response = self.llm.invoke(prompt)
            return response.content
    
    def review_design_documents(self, state: SDLCState):
        return state
    
    def revise_design_documents(self, state: SDLCState):
        pass
    
    def review_design_documents_router(self, state: SDLCState):
        """
            Evaluates design review is required or not.
        """
        return state.get("design_documents_review_status", "approved")  # default to "approved" if not present
    