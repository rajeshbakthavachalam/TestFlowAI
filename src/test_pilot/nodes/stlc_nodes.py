from src.test_pilot.nodes.project_requirement_node import ProjectRequirementNode
from src.test_pilot.nodes.markdown_node import MarkdownArtifactsNode

class TestPlanningNode:
    def __init__(self, llm): pass
    def test_planning(self, state):
        state['test_planning_data'] = state.get('test_planning_data', '')
        return state

class TestCaseDevelopmentNode:
    def __init__(self, llm): pass
    def test_case_development(self, state):
        state['test_case_development_data'] = state.get('test_case_development_data', '')
        return state

class TestEnvironmentSetupNode:
    def __init__(self, llm): pass
    def test_environment_setup(self, state):
        state['test_environment_setup_data'] = state.get('test_environment_setup_data', '')
        return state

class TestExecutionNode:
    def __init__(self, llm): pass
    def test_execution(self, state):
        state['test_execution_data'] = state.get('test_execution_data', '')
        return state

class TestClosureNode:
    def __init__(self, llm): pass
    def test_closure(self, state):
        state['test_closure_data'] = state.get('test_closure_data', '')
        return state

class MarkdownArtifactsNode:
    def __init__(self): pass
    def generate_markdown_artifacts(self, state): return state
