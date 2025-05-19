import os

class MarkdownArtifactsNode:
    """
    Graph Node for generating Markdown artifacts for the SDLC process.
    This node generates Markdown files for:
    - Project Requirements
    - User Stories
    - Design Documents
    - Generated Code
    and saves them to the "artifacts" folder.
    """
    
    def __init__(self): pass
    
    def generate_markdown_artifacts(self, state):
        """
        Generate Markdown files for each step in the SDLC state and save them to the artifacts folder.
        Returns the updated state with a new key 'artifacts' that maps to a dictionary of file paths.
        """
        artifacts_dir = "artifacts"
        os.makedirs(artifacts_dir, exist_ok=True)
        project_name = state.get("project_name", "Project")
        artifacts = {}

        # Project Requirements
        requirements = state.get("requirements", [])
        md_project = f"# Project Requirement for {project_name}\n\n"
        md_project += "## Requirements\n"
        md_project += "\n".join(requirements)
        file_project = os.path.join(artifacts_dir, "Project_Requirement.md")
        with open(file_project, "w") as f:
            f.write(md_project)
        artifacts["Project_Requirements"] = file_project

        # Test Plan
        test_plan = state.get("test_plan", None)
        if test_plan:
            md_test_plan = f"# Test Plan for {project_name}\n\n{test_plan}"
            file_test_plan = os.path.join(artifacts_dir, "Test_Plan.md")
            with open(file_test_plan, "w") as f:
                f.write(md_test_plan)
            artifacts["Test_Plan"] = file_test_plan

        # Test Cases
        test_cases = state.get("test_cases", None)
        if test_cases is not None and (not hasattr(test_cases, 'empty') or not test_cases.empty):
            md_test_cases = f"# Test Cases for {project_name}\n\n{test_cases}"
            file_test_cases = os.path.join(artifacts_dir, "Test_Cases.md")
            with open(file_test_cases, "w") as f:
                f.write(md_test_cases)
            artifacts["Test_Cases"] = file_test_cases

        # Test Environment
        test_env = state.get("test_env", None)
        if test_env:
            md_test_env = f"# Test Environment Setup for {project_name}\n\n{test_env}"
            file_test_env = os.path.join(artifacts_dir, "Test_Environment.md")
            with open(file_test_env, "w") as f:
                f.write(md_test_env)
            artifacts["Test_Environment"] = file_test_env

        # Test Execution
        test_execution = state.get("test_execution", None)
        if test_execution:
            md_test_execution = f"# Test Execution Strategy for {project_name}\n\n{test_execution}"
            file_test_execution = os.path.join(artifacts_dir, "Test_Execution.md")
            with open(file_test_execution, "w") as f:
                f.write(md_test_execution)
            artifacts["Test_Execution"] = file_test_execution

        # Test Closure
        test_closure = state.get("test_closure", None)
        if test_closure:
            md_test_closure = f"# Test Closure Summary for {project_name}\n\n{test_closure}"
            file_test_closure = os.path.join(artifacts_dir, "Test_Closure.md")
            with open(file_test_closure, "w") as f:
                f.write(md_test_closure)
            artifacts["Test_Closure"] = file_test_closure

        state["artifacts"] = artifacts
        return state