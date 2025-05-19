from typing import Dict, List, Any, Optional
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, Tool
from langchain.prompts import MessagesPlaceholder
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from .learning_engine import LearningEngine
from .memory import AgentMemory
from .goals import AgentGoals
from loguru import logger

class BaseAgent:
    """
    Base class for all agents in the system.
    Implements core agentic capabilities including:
    - Autonomous decision making
    - Learning from experience
    - Goal-oriented behavior
    - Memory management
    """
    
    def __init__(self, model, agent_type: str):
        self.model = model
        self.agent_type = agent_type
        self.memory = AgentMemory()
        self.learning_engine = LearningEngine()
        self.goals = AgentGoals(agent_type)
        self.tools: List[Tool] = []
        self.agent_executor: Optional[AgentExecutor] = None
        
        # Initialize decision-making prompt templates
        self.system_prompt = SystemMessagePromptTemplate.from_template(
            """You are an autonomous AI agent that makes intelligent decisions based on context, goals, and learning history.
            Your goal is to make the best possible decision for the given situation.
            
            Consider the following when making decisions:
            1. Your current goals and objectives
            2. Past experiences and their outcomes
            3. Current context and requirements
            4. Recommendations from the learning engine
            5. Best practices in your domain
            
            Provide your decision in a structured format with:
            1. The decision itself
            2. Reasoning for the decision
            3. Expected outcomes
            4. Potential risks or considerations
            5. Alternative approaches considered
            """
        )
        
        self.human_prompt = HumanMessagePromptTemplate.from_template(
            """Context: {context}
            
            Current Goals:
            {goals}
            
            Learning History Summary:
            {learning_summary}
            
            Recommendations:
            {recommendations}
            
            Please make a decision based on this information."""
        )
        
        self.decision_prompt = ChatPromptTemplate.from_messages([
            self.system_prompt,
            self.human_prompt
        ])
        
    def add_tool(self, tool: Tool) -> None:
        """Add a tool that the agent can use"""
        self.tools.append(tool)
        
    def learn_from_experience(self, experience: Dict[str, Any]) -> None:
        """
        Learn from an experience by storing it in memory and updating goals.
        
        Args:
            experience: The experience to learn from
        """
        try:
            # Store experience in memory
            self.memory.add_to_memory(experience)
            
            # Update goals based on experience
            self.goals.update_from_experience(experience)
            
            # Update learning engine
            self.learning_engine.update(experience)
            
        except Exception as e:
            logger.error(f"Error in learning from experience: {e}")
        
    def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make autonomous decisions based on context, goals, and learning history.
        This method uses the LLM to make intelligent decisions based on:
        1. Current context
        2. Agent goals
        3. Learning history
        4. Recommendations from the learning engine
        
        Args:
            context: Current context for decision making
            
        Returns:
            Dictionary containing the decision and supporting information
        """
        # Get current goals
        current_goals = self.goals.get_current_goals()
        
        # Get recommendations from learning engine
        recommendations = self.learning_engine.get_recommendations(context)
        
        # Get learning summary
        learning_summary = self.learning_engine.get_learning_summary()
        
        # Get relevant past experiences
        relevant_experiences = self.memory.get_relevant_experiences(context)
        
        # Prepare the prompt
        prompt = self.decision_prompt.format_messages(
            context=context,
            goals=current_goals,
            learning_summary=learning_summary,
            recommendations=recommendations
        )
        
        try:
            # Get decision from LLM
            response = self.model.invoke(prompt)
            
            # Parse the response
            decision_text = response.content
            
            # Extract structured information from the response
            decision_parts = self._parse_decision_response(decision_text)
            
            # Create the decision result
            decision_result = {
                'decision': decision_parts.get('decision', ''),
                'reasoning': decision_parts.get('reasoning', ''),
                'expected_outcomes': decision_parts.get('expected_outcomes', []),
                'risks': decision_parts.get('risks', []),
                'alternatives': decision_parts.get('alternatives', []),
                'context': context,
                'goals': current_goals,
                'recommendations': recommendations,
                'learning_summary': learning_summary,
                'relevant_experiences': relevant_experiences
            }
            
            # Learn from this decision
            self.learn_from_experience({
                'type': 'decision_making',
                'context': context,
                'decision': decision_result
            })
            
            return decision_result
            
        except Exception as e:
            logger.error(f"Error in decision making: {str(e)}")
            return {
                'error': str(e),
                'status': 'failed',
                'context': context
            }
            
    def _parse_decision_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse the LLM response into structured decision information.
        
        Args:
            response_text: The raw response from the LLM
            
        Returns:
            Dictionary containing structured decision information
        """
        # Initialize result dictionary
        result = {
            'decision': '',
            'reasoning': '',
            'expected_outcomes': [],
            'risks': [],
            'alternatives': []
        }
        
        # Split response into sections
        sections = response_text.split('\n\n')
        
        for section in sections:
            if section.startswith('Decision:'):
                result['decision'] = section.replace('Decision:', '').strip()
            elif section.startswith('Reasoning:'):
                result['reasoning'] = section.replace('Reasoning:', '').strip()
            elif section.startswith('Expected Outcomes:'):
                outcomes = section.replace('Expected Outcomes:', '').strip()
                result['expected_outcomes'] = [o.strip() for o in outcomes.split('\n') if o.strip()]
            elif section.startswith('Risks:'):
                risks = section.replace('Risks:', '').strip()
                result['risks'] = [r.strip() for r in risks.split('\n') if r.strip()]
            elif section.startswith('Alternatives:'):
                alternatives = section.replace('Alternatives:', '').strip()
                result['alternatives'] = [a.strip() for a in alternatives.split('\n') if a.strip()]
                
        return result
        
    def get_agent_executor(self) -> AgentExecutor:
        """Get or create the agent executor"""
        if not self.agent_executor:
            # Create agent executor with tools and memory
            self.agent_executor = AgentExecutor.from_agent_and_tools(
                agent=self,
                tools=self.tools,
                memory=self.memory.get_conversation_memory(),
                verbose=True
            )
        return self.agent_executor
        
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task with agentic capabilities.
        This method uses the learning engine to improve task processing.
        
        Args:
            task: Dictionary containing task information
            
        Returns:
            Dictionary containing task results
        """
        # Get recommendations for the task
        recommendations = self.learning_engine.get_recommendations(task)
        
        # Make a decision about how to process the task
        decision = self.make_decision({
            'type': 'task_processing',
            'task': task,
            'recommendations': recommendations
        })
        
        # Process the task based on the decision
        # This should be implemented by specific agent types
        return {
            'status': 'pending_implementation',
            'task': task,
            'decision': decision,
            'recommendations': recommendations
        }
        
    def get_learning_summary(self) -> Dict[str, Any]:
        """
        Get a summary of what the agent has learned.
        
        Returns:
            Dictionary containing learning summary
        """
        return self.learning_engine.get_learning_summary() 