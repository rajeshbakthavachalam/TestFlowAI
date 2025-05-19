import os
import sys
from dotenv import load_dotenv
from src.test_pilot.graph.graph_builder import GraphBuilder

class DummyLLM:
    def invoke(self, *args, **kwargs):
        return None

def main():
    try:
        # Create a dummy LLM instance
        dummy_llm = DummyLLM()
        
        # Create graph builder and generate the diagram
        print("Creating graph builder...")
        graph_builder = GraphBuilder(dummy_llm)
        
        print("Setting up graph...")
        graph = graph_builder.setup_graph()
        
        print("Generating workflow diagram...")
        graph_builder.save_graph_image(graph)
        
    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        print("\nTroubleshooting tips:")
        print("1. Make sure you have write permissions in the current directory")
        print("2. Check if the src directory structure is correct")
        sys.exit(1)

if __name__ == "__main__":
    main()
