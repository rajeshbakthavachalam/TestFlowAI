from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

class AgentGoals:
    """
    Manages agent goals and objectives.
    Handles goal setting, tracking, and adaptation based on experience.
    """
    
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.current_goals: List[Dict[str, Any]] = []
        self.completed_goals: List[Dict[str, Any]] = []
        self.goal_history: List[Dict[str, Any]] = []
        self._initialize_default_goals()
        
    def _initialize_default_goals(self) -> None:
        """Initialize default goals based on agent type"""
        if self.agent_type == 'test_case_generator':
            default_goals = [
                {
                    'id': 'TC-001',
                    'description': 'Generate comprehensive test cases',
                    'priority': 'high',
                    'metrics': ['coverage', 'quality'],
                    'targets': {'coverage': 0.8, 'quality': 0.9},
                    'progress': 0.0,
                    'status': 'active'
                },
                {
                    'id': 'TC-002',
                    'description': 'Ensure test case diversity',
                    'priority': 'medium',
                    'metrics': ['diversity'],
                    'targets': {'diversity': 0.7},
                    'progress': 0.0,
                    'status': 'active'
                }
            ]
        elif self.agent_type == 'code_reviewer':
            default_goals = [
                {
                    'id': 'CR-001',
                    'description': 'Review code quality',
                    'priority': 'high',
                    'metrics': ['quality', 'security'],
                    'targets': {'quality': 0.9, 'security': 0.95},
                    'progress': 0.0,
                    'status': 'active'
                }
            ]
        else:
            default_goals = [
                {
                    'id': 'GEN-001',
                    'description': 'Improve task completion rate',
                    'priority': 'high',
                    'metrics': ['completion_rate'],
                    'targets': {'completion_rate': 0.8},
                    'progress': 0.0,
                    'status': 'active'
                }
            ]
        
        for goal in default_goals:
            self.add_goal(goal)
        
    def get_current_goals(self) -> List[Dict[str, Any]]:
        """
        Get the current active goals.
        
        Returns:
            List of current goals
        """
        return self.current_goals
        
    def add_goal(self, goal: Dict[str, Any]) -> None:
        """
        Add a new goal to the current goals.
        
        Args:
            goal: Dictionary containing goal information
        """
        if 'progress' not in goal:
            goal['progress'] = 0.0
        if 'status' not in goal:
            goal['status'] = 'active'
        goal['created_at'] = datetime.now().isoformat()
        self.current_goals.append(goal)
        self.goal_history.append({
            'action': 'add',
            'goal_id': goal['id'],
            'timestamp': datetime.now().isoformat()
        })
        
    def complete_goal(self, goal_id: str) -> None:
        """
        Mark a goal as completed.
        
        Args:
            goal_id: ID of the goal to complete
        """
        for goal in self.current_goals:
            if goal['id'] == goal_id:
                goal['status'] = 'completed'
                goal['completed_at'] = datetime.now().isoformat()
                self.completed_goals.append(goal)
                self.current_goals.remove(goal)
                self.goal_history.append({
                    'action': 'complete',
                    'goal_id': goal_id,
                    'timestamp': datetime.now().isoformat()
                })
                break
        
    def update_from_experience(self, experience: Dict[str, Any]) -> None:
        """
        Update goals based on new experience.
        
        Args:
            experience: Dictionary containing experience data
        """
        for goal in self.current_goals:
            if self._is_experience_relevant_to_goal(experience, goal):
                self._update_goal_progress(goal, experience)
                self._check_goal_completion(goal)
                self._adapt_goals(goal, experience)
        
    def _is_experience_relevant_to_goal(self, experience: Dict[str, Any], goal: Dict[str, Any]) -> bool:
        """
        Check if an experience is relevant to a goal.
        
        Args:
            experience: The experience to check
            goal: The goal to check against
            
        Returns:
            Boolean indicating if the experience is relevant
        """
        # Check if experience type matches any goal metrics
        experience_type = experience.get('type', '')
        return any(metric in experience_type.lower() for metric in goal['metrics'])
        
    def _update_goal_progress(self, goal: Dict[str, Any], experience: Dict[str, Any]) -> None:
        """
        Update goal progress based on experience.
        
        Args:
            goal: The goal to update
            experience: The experience to learn from
        """
        if 'progress' not in goal:
            goal['progress'] = 0.0
            
        # Calculate progress based on experience metrics
        metrics_progress = {}
        for metric in goal['metrics']:
            if metric in experience.get('metrics', {}):
                current_value = experience['metrics'][metric]
                target_value = goal['targets'].get(metric, 1.0)
                metrics_progress[metric] = min(current_value / target_value, 1.0)
        
        # Update overall progress as average of metric progresses
        if metrics_progress:
            goal['progress'] = sum(metrics_progress.values()) / len(metrics_progress)
        
    def _check_goal_completion(self, goal: Dict[str, Any]) -> None:
        """Check if a goal is completed based on progress"""
        if goal.get('progress', 0.0) >= 1.0:
            self.complete_goal(goal['id'])
        
    def _adapt_goals(self, goal: Dict[str, Any], experience: Dict[str, Any]) -> None:
        """
        Adapt goals based on experience.
        
        Args:
            goal: The goal to update
            experience: The experience to learn from
        """
        # Adjust targets if consistently exceeding or falling short
        for metric in goal['metrics']:
            if metric in experience.get('metrics', {}):
                current_value = experience['metrics'][metric]
                target_value = goal['targets'].get(metric, 1.0)
                self._adjust_goal_targets(goal, metric, current_value, target_value)
        
    def _adjust_goal_targets(self, goal: Dict[str, Any], metric: str, current_value: float, target_value: float) -> None:
        """
        Adjust goal targets based on performance.
        
        Args:
            goal: The goal to adjust
            metric: The metric to adjust
            current_value: The current value of the metric
            target_value: The target value of the metric
        """
        if current_value > target_value * 1.2:  # Consistently exceeding
            goal['targets'][metric] = min(target_value * 1.1, 1.0)
        elif current_value < target_value * 0.8:  # Consistently falling short
            goal['targets'][metric] = max(target_value * 0.9, 0.5)
        
    def get_goal_summary(self) -> Dict[str, Any]:
        """
        Get a summary of goals and their status.
        
        Returns:
            Dictionary containing goal summary
        """
        total_goals = len(self.current_goals) + len(self.completed_goals)
        completed_count = len(self.completed_goals)
        completion_rate = completed_count / total_goals if total_goals > 0 else 0.0
        
        return {
            'total_goals': total_goals,
            'completed_goals': completed_count,
            'completion_rate': completion_rate,
            'current_goals': self.current_goals,
            'completed_goals_list': self.completed_goals
        } 