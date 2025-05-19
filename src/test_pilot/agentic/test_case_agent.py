from typing import Dict, List, Any
from .base_agent import BaseAgent
from langchain.tools import Tool
from loguru import logger
import pandas as pd

class TestCaseGeneratorAgent(BaseAgent):
    """
    Specialized agent for generating and managing test cases.
    This agent demonstrates true agentic capabilities by:
    1. Learning from past test cases
    2. Making autonomous decisions about test coverage
    3. Adapting test generation strategies
    4. Setting and tracking test-related goals
    """
    
    def __init__(self, model):
        super().__init__(model, agent_type='test_case_generator')
        self.model = model  # Ensure model is always set as an attribute
        self.current_requirements = []
        self.current_test_cases = []
        self.test_patterns: Dict[str, Any] = {}
        self.coverage_metrics: Dict[str, float] = {}
        self._initialize_test_tools()
        
    def _initialize_test_tools(self) -> None:
        """Initialize tools specific to test case generation"""
        self.add_tool(Tool(
            name="analyze_coverage",
            func=self.analyze_coverage,
            description="Analyze test coverage and identify gaps"
        ))
        
        self.add_tool(Tool(
            name="generate_test_case",
            func=self._generate_single_test_case,
            description="Generate a single test case based on requirements"
        ))
        
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a test case generation task and return structured data for UI display."""
        try:
            self.current_requirements = task.get('requirements', [])
            test_cases = self.generate_test_cases(self.current_requirements)
            self.current_test_cases = test_cases
            coverage = self.analyze_coverage(test_cases)
            decision = self.make_decision({
                'task_type': 'generate_test_cases',
                'requirements': self.current_requirements,
                'coverage': coverage
            })
            coverage_str = f"Coverage: {coverage.get('current_coverage', 0.0)*100:.1f}% ({coverage.get('covered_requirements', 0)}/{coverage.get('total_requirements', 0)})\nRecommended: {coverage.get('recommended_coverage', 0.0)*100:.1f}%\nAdditional cases needed: {coverage.get('additional_cases_needed', 0)}"
            decision_str = decision.get('decision', '')
            goals_list = [g['description'] for g in self.goals.current_goals] if hasattr(self.goals, 'current_goals') else []
            # Convert test_cases to DataFrame for Gradio
            df = pd.DataFrame(test_cases)
            return {
                'test_cases': df,
                'coverage': coverage_str,
                'decision': decision_str,
                'goals': goals_list
            }
        except Exception as e:
            logger.error(f"Error processing task: {str(e)}")
            return {
                'test_cases': pd.DataFrame(),
                'coverage': f'Error: {str(e)}',
                'decision': f'Error: {str(e)}',
                'goals': []
            }

    def analyze_coverage(self, test_cases: list) -> Dict[str, Any]:
        """Analyze test coverage against requirements (test_cases is a list of dicts)."""
        try:
            if not self.current_requirements:
                return {
                    'current_coverage': 0.0,
                    'total_requirements': 0,
                    'covered_requirements': 0,
                    'recommended_coverage': 0.8,
                    'additional_cases_needed': 0
                }
            total_requirements = len(self.current_requirements)
            covered_requirements = 0
            for req in self.current_requirements:
                found = False
                for tc in test_cases:
                    # Check if requirement is mentioned in Description or Steps
                    if req.lower() in tc.get('Description', '').lower() or req.lower() in tc.get('Steps', '').lower():
                        found = True
                        break
                if found:
                    covered_requirements += 1
            current_coverage = covered_requirements / total_requirements if total_requirements > 0 else 0.0
            recommended_coverage = 0.8
            additional_cases_needed = max(0, int((recommended_coverage - current_coverage) * total_requirements))
            return {
                'current_coverage': current_coverage,
                'total_requirements': total_requirements,
                'covered_requirements': covered_requirements,
                'recommended_coverage': recommended_coverage,
                'additional_cases_needed': additional_cases_needed
            }
        except Exception as e:
            logger.error(f"Error in coverage analysis: {str(e)}")
            return {
                'error': str(e),
                'current_coverage': 0.0,
                'total_requirements': 0,
                'covered_requirements': 0,
                'recommended_coverage': 0.8,
                'additional_cases_needed': 0
            }

    def generate_test_cases(self, requirements: List[str]) -> list:
        try:
            test_cases = []
            for idx, req in enumerate(requirements, 1):
                prompt = (
                    f"Generate a test case for the following requirement:\n{req}\n"
                    "Format:\nID: TC-XXX\nDescription: ...\nSteps:\n1. ...\n2. ...\nExpected Result: ...\n"
                )
                response = self.model.invoke(prompt)
                lines = response.content.split('\n')
                tc = {'ID': f'TC-{idx:03d}', 'Description': '', 'Steps': '', 'Expected': ''}
                steps = []
                expected = []
                in_steps = False
                in_expected = False
                for line in lines:
                    if line.lower().startswith('description:'):
                        tc['Description'] = line.split(':', 1)[1].strip()
                        in_steps = False
                        in_expected = False
                    elif line.lower().startswith('steps:'):
                        in_steps = True
                        in_expected = False
                    elif line.lower().startswith('expected result:'):
                        in_steps = False
                        in_expected = True
                    elif in_steps and line.strip().startswith(tuple(str(i) + '.' for i in range(1, 10))):
                        steps.append(line.strip())
                    elif in_expected and line.strip():
                        expected.append(line.strip())
                tc['Steps'] = '\n'.join(steps)
                tc['Expected'] = '\n'.join(expected)
                if not tc['Description']:
                    tc['Description'] = req
                test_cases.append(tc)
            return test_cases
        except Exception as e:
            logger.error(f"Error generating test cases: {str(e)}")
            return []
        
    def _generate_single_test_case(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a single test case based on context and learned patterns.
        
        Args:
            context: Context for test case generation
            
        Returns:
            Generated test case
        """
        # Get recommendations for this specific test case
        recommendations = self.learning_engine.get_recommendations(context)
        
        # Create prompt with recommendations and patterns
        prompt = self._create_test_case_prompt(
            context['requirement'],
            recommendations,
            context.get('patterns', {})
        )
        
        # Generate test case using LLM
        response = self.model.invoke(prompt)
        
        # Parse and structure the test case
        test_case = self._parse_test_case_response(response.content)
        
        # Add metadata
        test_case.update({
            'requirement': context['requirement'],
            'generation_strategy': context.get('strategy', {}),
            'recommendations_used': recommendations
        })
        
        return test_case
        
    def _create_test_case_prompt(self, requirement: str, recommendations: Dict[str, Any], patterns: Dict[str, Any]) -> str:
        """
        Create a prompt for test case generation using recommendations and patterns.
        
        Args:
            requirement: The requirement to generate test case for
            recommendations: Recommendations from learning engine
            patterns: Learned test patterns
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Generate a test case for requirement: {requirement}

        Consider the following patterns from past test cases:
        {self._format_patterns(patterns)}

        Recommended test types: {', '.join(recommendations.get('recommended_test_types', []))}
        Target coverage: {recommendations.get('target_coverage', 0.0)}

        Follow this exact format:
        ```python
        def test_{requirement.lower().replace(' ', '_')}(self):
            \"\"\"
            Test Case ID: TC-{len(self.test_patterns) + 1}
            Description: [Clear description of what is being tested]
            
            Test Steps:
            1. [Step 1]
            2. [Step 2]
            
            Expected Results:
            - [Expected result 1]
            - [Expected result 2]
            \"\"\"
            # Test implementation here
            pass
        ```
        """
        return prompt
        
    def _format_patterns(self, patterns: Dict[str, Any]) -> str:
        """Format test patterns for prompt"""
        formatted = []
        for pattern_type, pattern_list in patterns.items():
            if pattern_list:
                formatted.append(f"{pattern_type}:")
                for pattern in pattern_list[-3:]:  # Show last 3 patterns
                    formatted.append(f"- {pattern}")
        return "\n".join(formatted)
        
    def _parse_test_case_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the LLM response into a structured test case.
        
        Args:
            response: The raw response from the LLM
            
        Returns:
            Structured test case
        """
        # Extract test case information
        test_case = {
            'id': '',
            'description': '',
            'steps': [],
            'expected_results': [],
            'implementation': ''
        }
        
        # Parse the response
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            if 'Test Case ID:' in line:
                test_case['id'] = line.split('Test Case ID:')[1].strip()
            elif 'Description:' in line:
                test_case['description'] = line.split('Description:')[1].strip()
            elif 'Test Steps:' in line:
                current_section = 'steps'
            elif 'Expected Results:' in line:
                current_section = 'results'
            elif line.strip().startswith('def test_'):
                current_section = 'implementation'
                test_case['implementation'] = line
            elif current_section == 'steps' and line.strip().startswith(('1.', '2.', '3.')):
                test_case['steps'].append(line.strip())
            elif current_section == 'results' and line.strip().startswith('-'):
                test_case['expected_results'].append(line.strip()[1:].strip())
            elif current_section == 'implementation':
                test_case['implementation'] += '\n' + line
                
        return test_case 