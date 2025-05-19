from langgraph.graph import StateGraph,START, END
from src.test_pilot.state.sdlc_state import STLCState
from src.test_pilot.nodes.stlc_nodes import (
    ProjectRequirementNode,
    TestPlanningNode,
    TestCaseDevelopmentNode,
    TestEnvironmentSetupNode,
    TestExecutionNode,
    TestClosureNode,
    MarkdownArtifactsNode
)
from langgraph.checkpoint.memory import MemorySaver
import os

class GraphBuilder:
    
    def __init__(self, llm):
        self.llm = llm
        self.graph_builder = StateGraph(STLCState)
        self.memory = MemorySaver()
                
    
    def build_stlc_graph(self):
        """
            Configure the graph by adding nodes, edges
        """
        
        self.requirement_analysis_node = ProjectRequirementNode(self.llm)
        self.test_planning_node = TestPlanningNode(self.llm)
        self.test_case_development_node = TestCaseDevelopmentNode(self.llm)
        self.test_environment_setup_node = TestEnvironmentSetupNode(self.llm)
        self.test_execution_node = TestExecutionNode(self.llm)
        self.test_closure_node = TestClosureNode(self.llm)
        self.markdown_node = MarkdownArtifactsNode()
        
        ## Nodes
        self.graph_builder.add_node("requirement_analysis", self.requirement_analysis_node.get_user_requirements)
        self.graph_builder.add_node("test_planning", self.test_planning_node.test_planning)
        self.graph_builder.add_node("test_case_development", self.test_case_development_node.test_case_development)
        self.graph_builder.add_node("test_environment_setup", self.test_environment_setup_node.test_environment_setup)
        self.graph_builder.add_node("test_execution", self.test_execution_node.test_execution)
        self.graph_builder.add_node("test_closure", self.test_closure_node.test_closure)
        self.graph_builder.add_node("download_artifacts", self.markdown_node.generate_markdown_artifacts)
        
        ## Edges
        self.graph_builder.add_edge(START,"requirement_analysis")
        self.graph_builder.add_edge("requirement_analysis","test_planning")
        self.graph_builder.add_edge("test_planning","test_case_development")
        self.graph_builder.add_edge("test_case_development","test_environment_setup")
        self.graph_builder.add_edge("test_environment_setup","test_execution")
        self.graph_builder.add_edge("test_execution","test_closure")
        self.graph_builder.add_edge("test_closure","download_artifacts")
        self.graph_builder.add_edge("download_artifacts", END)
         
        
    def setup_graph(self):
        """
        Sets up the graph
        """
        self.build_stlc_graph()
        return self.graph_builder.compile(
            interrupt_before=[
                'requirement_analysis',
                'test_planning',
                'test_case_development',
                'test_environment_setup',
                'test_execution',
                'test_closure'
            ],checkpointer=self.memory
        )
    
    def save_graph_image(self, graph):
        """Generate a simple text representation of the workflow"""
        workflow = """
STLC Workflow Diagram
====================

START
  │
  ▼
[Requirement Analysis]
  │
  ▼
[Test Planning]
  │
  ▼
[Test Case Development]
  │
  ▼
[Test Environment Setup]
  │
  ▼
[Test Execution]
  │
  ▼
[Test Closure]
  │
  ▼
[Download Artifacts]
  │
  ▼
 END
"""
        # Save the workflow as a text file with UTF-8 encoding
        with open("workflow_graph.txt", "w", encoding='utf-8') as f:
            f.write(workflow)
        
        print("Workflow diagram has been saved as 'workflow_graph.txt'")
        print("\nYou can view the workflow by opening workflow_graph.txt")
        print("For a visual representation, you can use an online Mermaid editor:")
        print("1. Go to https://mermaid.live")
        print("2. Copy and paste the following Mermaid code:")
        
        mermaid_code = """
graph TD
    START[START]
    RA[Requirement Analysis]
    TP[Test Planning]
    TCD[Test Case Development]
    TES[Test Environment Setup]
    TE[Test Execution]
    TC[Test Closure]
    DA[Download Artifacts]
    END[END]

    START --> RA
    RA --> TP
    TP --> TCD
    TCD --> TES
    TES --> TE
    TE --> TC
    TC --> DA
    DA --> END
"""
        print("\n" + mermaid_code)
        
        