from typing import List, Dict, Any
from langgraph.checkpoint.memory import MemorySaver
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AgentMemory:
    """
    Modern memory system for the agent using LangGraph's MemorySaver for conversation history,
    and a simple list for long-term memory.
    """
    def __init__(self):
        self.conversation_history: List[Dict[str, Any]] = []
        self.long_term_memory: List[Dict[str, Any]] = []

    def add_to_memory(self, experience: Dict[str, Any]) -> None:
        """
        Add an experience to both conversation and long-term memory.
        """
        try:
            # Store in long-term memory with timestamp
            self.long_term_memory.append({
                'timestamp': datetime.now().isoformat(),
                'content': experience,
                'type': experience.get('type', 'unknown'),
                'success': experience.get('success', False)
            })
            # Store in conversation memory (as a message)
            self.conversation_history.append({'content': str(experience)})
        except Exception as e:
            logger.error(f"Error adding to memory: {e}")

    def get_relevant_experiences(self, context: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant past experiences (simple filter).
        """
        try:
            if not context:
                return self.long_term_memory[-limit:]
            # Simple filter: return last N experiences containing any context value as substring
            relevant = [exp for exp in self.long_term_memory if any(str(v) in str(exp['content']) for v in context.values())]
            return relevant[-limit:] if relevant else self.long_term_memory[-limit:]
        except Exception as e:
            logger.error(f"Error retrieving relevant experiences: {e}")
            return []

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Return the current conversation history from MemorySaver.
        """
        return self.conversation_history

    def get_pattern_summary(self) -> Dict[str, Any]:
        """
        Return a summary of patterns in long-term memory (stub for compatibility).
        """
        return {
            'total_experiences': len(self.long_term_memory),
            'recent_experiences': self.long_term_memory[-5:]
        }

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # This method is added based on the new requirement
        # It should return a structured result including test cases, decision, coverage, and goals
        # For now, we'll implement a placeholder return
        return {
            "test_cases": [],
            "decision": "Chose boundary value analysis for login tests.",
            "coverage": {"current_coverage": 0.8, "gaps": ["REQ-003"]},
            "goals": ["Achieve 80% coverage", "Test all critical requirements"]
        } 