from typing import Dict, List, Any
from collections import defaultdict
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LearningEngine:
    """
    Engine that handles learning from experiences and pattern recognition.
    This is used by agents to improve their performance over time.
    """
    
    def __init__(self):
        self.patterns: Dict[str, Any] = {}
        self.experiences: List[Dict[str, Any]] = []
        self.learning_rate = 0.1
        
    def update(self, experience: Dict[str, Any]) -> None:
        """Update learning engine with new experience"""
        try:
            # Store experience
            self.experiences.append(experience)
            
            # Update patterns based on experience type
            exp_type = experience.get('type', 'unknown')
            if exp_type not in self.patterns:
                self.patterns[exp_type] = {
                    'count': 0,
                    'success_rate': 0.0,
                    'last_updated': None
                }
            
            # Update pattern statistics
            pattern = self.patterns[exp_type]
            pattern['count'] += 1
            
            # Update success rate if success is indicated
            if 'success' in experience:
                current_success = pattern['success_rate'] * (pattern['count'] - 1)
                new_success = current_success + (1 if experience['success'] else 0)
                pattern['success_rate'] = new_success / pattern['count']
            
            pattern['last_updated'] = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Error updating learning engine: {str(e)}")
    
    def get_pattern_statistics(self, pattern_type: str) -> Dict[str, Any]:
        """Get statistics for a specific pattern type"""
        try:
            if pattern_type not in self.patterns:
                return {
                    'count': 0,
                    'success_rate': 0.0,
                    'last_updated': None
                }
            return self.patterns[pattern_type]
        except Exception as e:
            logger.error(f"Error getting pattern statistics: {str(e)}")
            return {
                'error': str(e),
                'count': 0,
                'success_rate': 0.0,
                'last_updated': None
            }
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Get a summary of the learning engine's state"""
        try:
            return {
                'total_experiences': len(self.experiences),
                'pattern_types': list(self.patterns.keys()),
                'patterns': self.patterns
            }
        except Exception as e:
            logger.error(f"Error getting learning summary: {str(e)}")
            return {
                'error': str(e),
                'total_experiences': 0,
                'pattern_types': [],
                'patterns': {}
            }
        
    def get_recommendations(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get recommendations based on learned patterns.
        
        Args:
            context: Current context for making recommendations
            
        Returns:
            Dictionary containing recommendations
        """
        recommendations = {}
        
        # Analyze coverage patterns
        coverage_stats = self.get_pattern_statistics('coverage')
        if coverage_stats:
            if 'mean' in coverage_stats:
                recommendations['target_coverage'] = coverage_stats['mean']
            elif 'success_rate' in coverage_stats:
                recommendations['target_coverage'] = coverage_stats['success_rate']
            elif 'current_coverage' in coverage_stats:
                recommendations['target_coverage'] = coverage_stats['current_coverage']
            else:
                recommendations['target_coverage'] = 0.8
            
        # Analyze execution time patterns
        time_stats = self.get_pattern_statistics('execution_time')
        if time_stats and 'mean' in time_stats:
            recommendations['expected_execution_time'] = time_stats['mean']
            
        # Analyze test type patterns
        type_stats = self.get_pattern_statistics('test_type')
        if type_stats and 'recommended_test_types' in type_stats:
            recommendations['recommended_test_types'] = type_stats['recommended_test_types']
        elif 'test_type' in self.patterns:
            recommendations['recommended_test_types'] = list(set(self.patterns['test_type']))
            
        return recommendations 