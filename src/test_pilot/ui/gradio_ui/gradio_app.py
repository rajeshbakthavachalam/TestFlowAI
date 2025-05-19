import gradio as gr
from typing import Dict, Any
import os
from src.test_pilot.LLMS.groqllm import GroqLLM
from src.test_pilot.LLMS.geminillm import GeminiLLM
from src.test_pilot.LLMS.openai_llm import OpenAILLM
from src.test_pilot.agentic.test_case_agent import TestCaseGeneratorAgent
from src.test_pilot.ui.uiconfigfile import Config
import src.test_pilot.utils.constants as const
from src.test_pilot.nodes.markdown_node import MarkdownArtifactsNode
import json
import pandas as pd

class GradioUI:
    def __init__(self):
        self.config = Config()
        self.test_agent = None
        self.model = None  # Store the model separately
        self.current_stage = const.PROJECT_INITILIZATION
        self.project_name = ""
        self.requirements = []
        self.test_plan = ""
        self.test_cases = ""
        self.test_env = ""
        self.test_execution = ""
        self.test_closure = ""
        
    def initialize_agent(self, llm_choice: str, model_choice: str, api_key: str) -> str:
        """Initialize the test agent with selected LLM"""
        try:
            if llm_choice == "Gemini":
                obj_llm_config = GeminiLLM(user_controls_input={
                    "selected_llm": llm_choice,
                    "selected_gemini_model": model_choice,
                    "GEMINI_API_KEY": api_key
                })
            elif llm_choice == "Groq":
                obj_llm_config = GroqLLM(user_controls_input={
                    "selected_llm": llm_choice,
                    "selected_groq_model": model_choice,
                    "GROQ_API_KEY": api_key
                })
            elif llm_choice == "OpenAI":
                obj_llm_config = OpenAILLM(user_controls_input={
                    "selected_llm": llm_choice,
                    "selected_openai_model": model_choice,
                    "OPENAI_API_KEY": api_key
                })
            
            self.model = obj_llm_config.get_llm_model()
            self.test_agent = TestCaseGeneratorAgent(self.model)
            return "Agent initialized successfully!"
        except Exception as e:
            return f"Error initializing agent: {str(e)}"

    def start_stlc_process(self, project_name: str, requirements: str) -> tuple:
        """Start the STLC process with project details"""
        if not project_name:
            return "Please enter a project name.", None
        if not requirements.strip():
            return "Please enter at least one requirement.", None
            
        self.project_name = project_name
        self.requirements = [req.strip() for req in requirements.split("\n") if req.strip()]
        self.current_stage = const.TEST_PLANNING
        return "Project details saved successfully!", self.generate_test_plan()

    def generate_test_plan(self) -> str:
        """Generate test plan using the LLM"""
        if not self.test_agent or not self.model:
            return "Please initialize the agent first."
            
        prompt = (
            f"Project Name: {self.project_name}\n"
            f"Requirements:\n" + "\n".join(self.requirements) + "\n\n"
            "Based on the above, generate a detailed test plan for this project."
        )
        response = self.model.invoke(prompt)
        self.test_plan = response.content
        return self.test_plan

    def save_test_plan(self, test_plan: str):
        self.test_plan = test_plan
        self.current_stage = const.TEST_CASE_DEVELOPMENT
        # Get the structured result from the agent
        result = self.generate_test_cases()
        # If result is a tuple, unpack it to dict
        if isinstance(result, tuple):
            # Assume the tuple is (test_cases, decision, coverage, goals)
            test_cases, decision, coverage, goals = result
        elif isinstance(result, dict):
            test_cases = result.get('test_cases', [])
            decision = result.get('decision', '')
            coverage = result.get('coverage', '')
            goals = result.get('goals', [])
        else:
            test_cases, decision, coverage, goals = [], '', '', []
        return (
            "Test plan saved!",
            test_cases,
            decision,
            coverage,
            "\n".join(goals) if isinstance(goals, list) else str(goals)
        )

    def generate_test_cases(self) -> tuple:
        """Generate test cases using the agent"""
        if not self.test_agent:
            return "Please initialize the agent first.", None, None, None
            
        task = {
            'type': 'generate_test_cases',
            'requirements': self.requirements
        }
        result = self.test_agent.process_task(task)
        self.test_cases = result['test_cases']
        
        return (
            self.test_cases,
            str(result['decision']),
            str(result['coverage']),
            str(self.test_agent.goals.get_goal_summary())
        )

    def save_test_cases(self, test_cases: str) -> tuple:
        """Save test cases and proceed to test environment setup"""
        self.test_cases = test_cases
        self.current_stage = const.TEST_ENVIRONMENT_SETUP
        return "Test cases saved!", self.generate_test_env()

    def generate_test_env(self) -> str:
        """Generate test environment setup"""
        if not self.test_agent or not self.model:
            return "Please initialize the agent first."
            
        prompt = (
            f"Project Name: {self.project_name}\n"
            f"Requirements:\n" + "\n".join(self.requirements) + "\n"
            f"Test Plan:\n{self.test_plan}\n"
            f"Test Cases:\n{self.test_cases}\n\n"
            "Based on the above, generate a recommended test environment setup for this project."
        )
        response = self.model.invoke(prompt)
        self.test_env = response.content
        return self.test_env

    def save_test_env(self, test_env: str) -> tuple:
        """Save test environment and proceed to test execution"""
        self.test_env = test_env
        self.current_stage = const.TEST_EXECUTION
        return "Test environment saved!", self.generate_test_execution()

    def generate_test_execution(self) -> str:
        """Generate test execution strategy"""
        if not self.test_agent or not self.model:
            return "Please initialize the agent first."
            
        prompt = (
            f"Project Name: {self.project_name}\n"
            f"Requirements:\n" + "\n".join(self.requirements) + "\n"
            f"Test Plan:\n{self.test_plan}\n"
            f"Test Cases:\n{self.test_cases}\n"
            f"Test Environment Setup:\n{self.test_env}\n\n"
            "Based on the above, generate a test execution strategy or checklist for this project."
        )
        response = self.model.invoke(prompt)
        self.test_execution = response.content
        return self.test_execution

    def save_test_execution(self, test_execution: str) -> tuple:
        """Save test execution and proceed to test closure"""
        self.test_execution = test_execution
        self.current_stage = const.TEST_CLOSURE
        return "Test execution saved!", self.generate_test_closure()

    def generate_test_closure(self) -> str:
        """Generate test closure summary"""
        if not self.test_agent or not self.model:
            return "Please initialize the agent first."
            
        prompt = (
            f"Project Name: {self.project_name}\n"
            f"Requirements:\n" + "\n".join(self.requirements) + "\n"
            f"Test Plan:\n{self.test_plan}\n"
            f"Test Cases:\n{self.test_cases}\n"
            f"Test Environment Setup:\n{self.test_env}\n"
            f"Test Execution:\n{self.test_execution}\n\n"
            "Based on the above, generate a test closure summary or report for this project."
        )
        response = self.model.invoke(prompt)
        self.test_closure = response.content
        return self.test_closure

    def save_test_closure(self, test_closure: str) -> str:
        """Save test closure and generate artifacts"""
        self.test_closure = test_closure
        return self.generate_artifacts()

    def generate_artifacts(self) -> str:
        """Generate and return download links for artifacts"""
        markdown_node = MarkdownArtifactsNode()
        state = {
            "project_name": self.project_name,
            "requirements": self.requirements,
            "test_plan": self.test_plan,
            "test_cases": self.test_cases,
            "test_env": self.test_env,
            "test_execution": self.test_execution,
            "test_closure": self.test_closure,
        }
        state = markdown_node.generate_markdown_artifacts(state)
        artifacts = state.get("artifacts", {})
        
        if artifacts:
            return "Artifacts generated successfully! Check the download section."
        return "No artifacts generated."

    def get_agent_monitoring(self) -> tuple:
        """Get agent monitoring information"""
        if not self.test_agent:
            return "Please initialize the agent first.", None, None, None
            
        memory_summary = self.test_agent.memory.get_pattern_summary()
        patterns = self.test_agent.learning_engine.get_pattern_statistics('test_type')
        decisions = self.test_agent.memory.get_relevant_experiences({'type': 'decision_making'})
        goals_summary = self.test_agent.goals.get_goal_summary()
        
        return (
            str(memory_summary),
            str(patterns),
            str(decisions),
            str(goals_summary)
        )

def summarize_memory(memory_summary):
    if not memory_summary or not isinstance(memory_summary, dict):
        return "No memory data available."
    total = memory_summary.get('total_experiences', 0)
    recent = memory_summary.get('recent_experiences', [])
    summary = f"**Memory Summary**\n- Total Experiences: {total}\n"
    if recent:
        last = recent[-1]
        ts = last.get('timestamp', 'N/A')
        content = last.get('content', {})
        desc = content.get('decision', {}).get('decision', '') if isinstance(content.get('decision', {}), dict) else ''
        summary += f"- Most Recent: {ts}\n"
        if desc:
            summary += f"- Last Decision: {desc}\n"
    return summary

def summarize_patterns(patterns):
    if not patterns or not isinstance(patterns, dict):
        return "No learned patterns yet."
    lines = ["**Learned Patterns**"]
    for k, v in patterns.items():
        lines.append(f"- {k}: count={v.get('count', 0)}, success_rate={v.get('success_rate', 0.0):.2f}")
    return "\n".join(lines)

def summarize_decisions(decisions):
    if not decisions:
        return "No decisions made yet."
    if isinstance(decisions, str):
        try:
            decisions = json.loads(decisions.replace("'", '"'))
        except Exception:
            return decisions
    if isinstance(decisions, list):
        lines = ["**Recent Decisions**"]
        for d in decisions[-5:]:
            ts = d.get('timestamp', 'N/A')
            content = d.get('content', {})
            desc = content.get('decision', {}).get('decision', '') if isinstance(content.get('decision', {}), dict) else ''
            lines.append(f"- [{ts}] {desc}")
        return "\n".join(lines)
    return str(decisions)

def summarize_goals(goals):
    if not goals or not isinstance(goals, dict):
        return "No goal data available."
    total = goals.get('total_goals', 0)
    completed = goals.get('completed_goals', 0)
    rate = goals.get('completion_rate', 0.0)
    current = goals.get('current_goals', [])
    completed_list = goals.get('completed_goals_list', [])
    lines = [f"**Goal Progress**\n- Total Goals: {total}\n- Completed: {completed}\n- Completion Rate: {rate*100:.1f}%\n- Current Goals:"]
    for g in current:
        desc = g.get('description', '')
        status = g.get('status', '')
        lines.append(f"  - [{'x' if status=='completed' else ' '}] {desc}")
    if completed_list:
        lines.append("- Completed Goals:")
        for g in completed_list:
            lines.append(f"  - [x] {g.get('description', '')}")
    return "\n".join(lines)

def create_ui():
    """Create and launch the Gradio interface"""
    ui = GradioUI()
    
    with gr.Blocks(title="TestFlow AI") as demo:
        gr.Markdown("# TestFlow AI")
        
        with gr.Tab("Configuration"):
            with gr.Row():
                llm_choice = gr.Dropdown(
                    choices=["Gemini", "Groq", "OpenAI"],
                    label="Select LLM"
                )
                model_choice = gr.Dropdown(
                    choices=ui.config.get_gemini_model_options(),
                    label="Select Model"
                )
            api_key = gr.Textbox(
                label="API Key",
                type="password"
            )
            init_btn = gr.Button("Initialize Agent")
            init_output = gr.Textbox(label="Initialization Status")
            
        with gr.Tab("Requirement Analysis"):
            with gr.Row():
                project_name = gr.Textbox(label="Project Name")
                requirements = gr.Textbox(
                    label="Requirements (one per line)",
                    lines=10
                )
            start_btn = gr.Button("Start STLC Process")
            start_output = gr.Textbox(label="Status")
            
        with gr.Tab("Test Planning"):
            test_plan = gr.Textbox(
                label="Test Plan",
                lines=20
            )
            save_plan_btn = gr.Button("Save Test Plan")
            plan_output = gr.Textbox(label="Status")
            
        with gr.Tab("Test Case Development"):
            with gr.Row():
                test_cases_df = gr.Dataframe(headers=["ID", "Description", "Steps", "Expected"], label="Test Cases")
                with gr.Column():
                    decision_box = gr.Markdown(label="Decision Making Process")
                    coverage_box = gr.Markdown(label="Coverage Analysis")
                    goals_box = gr.Markdown(label="Agent Goals")
            save_cases_btn = gr.Button("Save Test Cases")
            cases_output = gr.Textbox(label="Status")
            
        with gr.Tab("Test Environment Setup"):
            test_env = gr.Textbox(
                label="Test Environment Setup",
                lines=20
            )
            save_env_btn = gr.Button("Save Test Environment")
            env_output = gr.Textbox(label="Status")
            
        with gr.Tab("Test Execution"):
            test_execution = gr.Textbox(
                label="Test Execution Strategy",
                lines=20
            )
            save_exec_btn = gr.Button("Save Test Execution")
            exec_output = gr.Textbox(label="Status")
            
        with gr.Tab("Test Closure"):
            test_closure = gr.Textbox(
                label="Test Closure Summary",
                lines=20
            )
            save_closure_btn = gr.Button("Save Test Closure")
            closure_output = gr.Textbox(label="Status")
            
        with gr.Tab("Download Artifacts"):
            gr.Markdown("## Download Artifacts for Each STLC Phase")
            download_status = gr.Textbox(label="Status", interactive=False)
            req_btn = gr.File(label="Download Requirement Analysis")
            plan_btn = gr.File(label="Download Test Planning")
            cases_btn = gr.File(label="Download Test Case Development")
            env_btn = gr.File(label="Download Test Environment Setup")
            exec_btn = gr.File(label="Download Test Execution")
            closure_btn = gr.File(label="Download Test Closure")

            def generate_and_get_artifacts():
                state = {
                    "project_name": ui.project_name,
                    "requirements": ui.requirements,
                    "test_plan": ui.test_plan,
                    "test_cases": ui.test_cases,
                    "test_env": ui.test_env,
                    "test_execution": ui.test_execution,
                    "test_closure": ui.test_closure,
                }
                markdown_node = MarkdownArtifactsNode()
                state = markdown_node.generate_markdown_artifacts(state)
                artifacts = state.get("artifacts", {})
                return (
                    "Artifacts generated!",
                    artifacts.get("Project_Requirements", None),
                    artifacts.get("Test_Plan", None),
                    artifacts.get("Test_Cases", None),
                    artifacts.get("Test_Environment", None),
                    artifacts.get("Test_Execution", None),
                    artifacts.get("Test_Closure", None),
                )
            gen_btn = gr.Button("Generate & Refresh Artifacts")
            gen_btn.click(
                generate_and_get_artifacts,
                outputs=[download_status, req_btn, plan_btn, cases_btn, env_btn, exec_btn, closure_btn]
            )
        
        # Set up event handlers
        init_btn.click(
            ui.initialize_agent,
            inputs=[llm_choice, model_choice, api_key],
            outputs=init_output
        )
        
        start_btn.click(
            ui.start_stlc_process,
            inputs=[project_name, requirements],
            outputs=[start_output, test_plan]
        )
        
        save_plan_btn.click(
            ui.save_test_plan,
            inputs=[test_plan],
            outputs=[plan_output, test_cases_df, decision_box, coverage_box, goals_box]
        )
        
        save_cases_btn.click(
            ui.save_test_cases,
            inputs=[test_cases_df],
            outputs=[cases_output, test_env]
        )
        
        save_env_btn.click(
            ui.save_test_env,
            inputs=[test_env],
            outputs=[env_output, test_execution]
        )
        
        save_exec_btn.click(
            ui.save_test_execution,
            inputs=[test_execution],
            outputs=[exec_output, test_closure]
        )
        
        save_closure_btn.click(
            ui.save_test_closure,
            inputs=[test_closure],
            outputs=closure_output
        )
    
    return demo

def launch_app():
    """Launch the Gradio interface"""
    try:
        demo = create_ui()
        # Launch without sharing to avoid Windows security issues
        demo.launch(
            server_name="127.0.0.1",
            server_port=7860,
            share=False,
            show_error=True,
            show_api=False
        )
    except Exception as e:
        print(f"Error launching Gradio app: {str(e)}")
        print("Trying alternative launch configuration...")
        try:
            demo.launch(
                server_name="localhost",
                server_port=0,  # Let the system choose an available port
                share=False,
                show_error=True,
                show_api=False
            )
        except Exception as e:
            print(f"Failed to launch Gradio app: {str(e)}")
            print("Please check your firewall settings and ensure no other application is using the required ports.")
            raise

if __name__ == "__main__":
    launch_app() 