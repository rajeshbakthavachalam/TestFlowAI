from typing import Dict, Any, Optional
from ..LLMS.openai_llm import OpenAILLM
from ..LLMS.geminillm import GeminiLLM
from ..LLMS.groqllm import GroqLLM
from .test_case_agent import TestCaseGeneratorAgent

class AgentFactory:
    """
    Factory class for creating different types of agents.
    This allows us to easily switch between the original LLM implementation
    and the new agentic implementation.
    """
    
    @staticmethod
    def create_agent(agent_type: str, implementation: str = "llm", **kwargs) -> Any:
        """
        Create an agent of the specified type and implementation.
        
        Args:
            agent_type: Type of agent to create (e.g., "test_case_generator")
            implementation: Implementation type ("llm" or "agentic")
            **kwargs: Additional arguments for agent creation
            
        Returns:
            An instance of the requested agent
        """
        if implementation == "llm":
            return AgentFactory._create_llm_agent(agent_type, **kwargs)
        elif implementation == "agentic":
            return AgentFactory._create_agentic_agent(agent_type, **kwargs)
        else:
            raise ValueError(f"Unknown implementation type: {implementation}")
    
    @staticmethod
    def _create_llm_agent(agent_type: str, **kwargs) -> Any:
        """Create an agent using the original LLM implementation"""
        if agent_type == "test_case_generator":
            # Use the original LLM implementation
            llm = OpenAILLM(**kwargs)
            return llm.get_llm_model()
        # Add other agent types as needed
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    @staticmethod
    def _create_agentic_agent(agent_type: str, **kwargs) -> Any:
        """Create an agent using the new agentic implementation"""
        if agent_type == "test_case_generator":
            # Create the LLM first
            llm = OpenAILLM(**kwargs)
            llm_model = llm.get_llm_model()
            # Create the agentic agent
            return TestCaseGeneratorAgent(llm_model)
        # Add other agent types as needed
        raise ValueError(f"Unknown agent type: {agent_type}") 