import streamlit as st
from src.test_pilot.LLMS.groqllm import GroqLLM
from src.test_pilot.LLMS.geminillm import GeminiLLM
from src.test_pilot.LLMS.openai_llm import OpenAILLM
from src.test_pilot.graph.graph_builder import GraphBuilder
from src.test_pilot.ui.uiconfigfile import Config
import src.test_pilot.utils.constants as const
from src.test_pilot.graph.graph_executor import GraphExecutor
from src.test_pilot.state.sdlc_state import UserStoryList
from src.test_pilot.agentic.test_case_agent import TestCaseGeneratorAgent
import os
from src.test_pilot.nodes.markdown_node import MarkdownArtifactsNode
from typing import Dict, Any

def initialize_session():
    st.session_state.stage = const.PROJECT_INITILIZATION
    st.session_state.project_name = ""
    st.session_state.requirements = ""
    st.session_state.task_id = ""
    st.session_state.state = {}
    st.session_state.test_agent = None

def show_agent_progress(test_agent):
    """Show agent progress metrics in the sidebar"""
    try:
        st.sidebar.subheader("Agent Progress")
        
        # Show goal completion rate
        goals_summary = test_agent.goals.get_goal_summary()
        completion_rate = goals_summary.get('completion_rate', 0)
        st.sidebar.progress(completion_rate, text="Goal Completion")
        
        # Show learning progress
        learning_summary = test_agent.get_learning_summary()
        total_experiences = learning_summary.get('total_experiences', 0)
        if isinstance(total_experiences, list):
            learning_progress = len(total_experiences) / 100
        else:
            learning_progress = total_experiences / 100
        st.sidebar.progress(min(learning_progress, 1.0), text="Learning Progress")
        
        # Show pattern recognition progress
        pattern_progress = len(test_agent.memory.patterns) / 10
        st.sidebar.progress(min(pattern_progress, 1.0), text="Pattern Recognition")
    except Exception as e:
        st.sidebar.error(f"Error showing agent progress: {str(e)}")

def show_agent_controls(test_agent):
    """Show interactive controls for agent behavior"""
    try:
        st.sidebar.subheader("Agent Controls")
        
        # Allow goal adjustment
        if st.sidebar.button("Add New Goal"):
            st.sidebar.text_input("Goal Description", key="new_goal_desc")
            st.sidebar.selectbox("Priority", ['high', 'medium', 'low'], key="new_goal_priority")
            metrics = st.sidebar.multiselect("Metrics", ['coverage', 'quality', 'speed'], key="new_goal_metrics")
            
            if st.sidebar.button("Save Goal"):
                if not st.session_state.get("new_goal_desc"):
                    st.sidebar.warning("Please enter a goal description")
                    return
                    
                new_goal = {
                    'id': f'CUSTOM-{len(test_agent.goals.current_goals) + 1}',
                    'description': st.session_state.new_goal_desc,
                    'priority': st.session_state.new_goal_priority,
                    'metrics': st.session_state.new_goal_metrics,
                    'targets': {
                        metric: 0.8 for metric in st.session_state.new_goal_metrics
                    }
                }
                test_agent.goals.add_goal(new_goal)
                st.sidebar.success("New goal added!")
    except Exception as e:
        st.sidebar.error(f"Error showing agent controls: {str(e)}")

def show_agent_monitoring(test_agent):
    """Show agent monitoring information"""
    try:
        st.subheader("Agent Monitoring")
        
        # Create columns for different metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Memory Summary")
            memory_summary = test_agent.memory.get_pattern_summary()
            st.json(memory_summary)
            
            st.write("Learned Patterns")
            patterns = test_agent.learning_engine.get_pattern_statistics('test_type')
            st.json(patterns)
        
        with col2:
            st.write("Decision History")
            decisions = test_agent.memory.get_relevant_experiences({'type': 'decision_making'})
            st.json(decisions)
            
            st.write("Goal Progress")
            goals_summary = test_agent.goals.get_goal_summary()
            st.json(goals_summary)
    except Exception as e:
        st.error(f"Error showing agent monitoring: {str(e)}")

def load_sidebar_ui(config):
    user_controls = {}
    
    with st.sidebar:
        # Get options from config
        llm_options = config.get_llm_options()

        # LLM selection
        user_controls["selected_llm"] = st.selectbox("Select LLM", llm_options)

        if user_controls["selected_llm"] == 'Groq':
            # Model selection
            model_options = config.get_groq_model_options()
            user_controls["selected_groq_model"] = st.selectbox("Select Model", model_options)
            # API key input
            os.environ["GROQ_API_KEY"] = user_controls["GROQ_API_KEY"] = st.session_state["GROQ_API_KEY"] = st.text_input("API Key",
                                                                                                    type="password",
                                                                                                    value=os.getenv("GROQ_API_KEY", ""))
            # Validate API key
            if not user_controls["GROQ_API_KEY"]:
                st.warning("⚠️ Please enter your GROQ API key to proceed. Don't have? refer : https://console.groq.com/keys ")
                
        if user_controls["selected_llm"] == 'Gemini':
            # Model selection
            model_options = config.get_gemini_model_options()
            user_controls["selected_gemini_model"] = st.selectbox("Select Model", model_options)
            # API key input
            os.environ["GEMINI_API_KEY"] = user_controls["GEMINI_API_KEY"] = st.session_state["GEMINI_API_KEY"] = st.text_input("API Key",
                                                                                                    type="password",
                                                                                                    value=os.getenv("GEMINI_API_KEY", "")) 
            # Validate API key
            if not user_controls["GEMINI_API_KEY"]:
                st.warning("⚠️ Please enter your GEMINI API key to proceed. Don't have? refer : https://ai.google.dev/gemini-api/docs/api-key ")
                
                
        if user_controls["selected_llm"] == 'OpenAI':
            # Model selection
            model_options = config.get_openai_model_options()
            user_controls["selected_openai_model"] = st.selectbox("Select Model", model_options)
            # API key input
            os.environ["OPENAI_API_KEY"] = user_controls["OPENAI_API_KEY"] = st.session_state["OPENAI_API_KEY"] = st.text_input("API Key",
                                                                                                    type="password",
                                                                                                    value=os.getenv("OPENAI_API_KEY", "")) 
            # Validate API key
            if not user_controls["OPENAI_API_KEY"]:
                st.warning("⚠️ Please enter your OPENAI API key to proceed. Don't have? refer : https://platform.openai.com/api-keys ")
    
        if st.button("Reset Session"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            
            initialize_session()
            st.rerun()
            
        st.subheader("Workflow Overview")
        st.image("workflow_graph.png")
            
    return user_controls

def load_streamlit_ui(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load the Streamlit UI for test case generation.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Dictionary containing user inputs
    """
    # Initialize session state if not already done
    initialize_session()
    
    # Load sidebar UI and get user controls
    user_controls = load_sidebar_ui(config)
    
    # Main content area
    st.title("Agentic Software Testing Life Cycle")
    
    # Create tabs for different stages
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Requirement Analysis",
        "Test Planning",
        "Test Case Development",
        "Test Execution",
        "Test Reporting",
        "Agent Monitoring"
    ])
    
    # Show agent progress and controls in sidebar
    if st.session_state.test_agent:
        show_agent_progress(st.session_state.test_agent)
        show_agent_controls(st.session_state.test_agent)

    # ---------------- Tab 1: Requirement Analysis ----------------
    with tab1:
        st.header("Requirement Analysis")
        st.write("Please enter your project name and requirements to begin your STLC journey.")
        project_name = st.text_input("Enter the project name:", value=st.session_state.get("project_name", ""))
        requirements_input = st.text_area(
            "Enter the requirements. Write each requirement on a new line:",
            value="\n".join(st.session_state.get("requirements", []))
        )
        if st.button("Start STLC Process", key="start_stlc_btn"):
            if not project_name:
                st.error("Please enter a project name.")
            elif not requirements_input.strip():
                st.error("Please enter at least one requirement.")
            else:
                requirements = [req.strip() for req in requirements_input.split("\n") if req.strip()]
                st.session_state.project_name = project_name
                st.session_state.requirements = requirements
                st.success("Project details saved successfully!")
                st.session_state.stage = const.TEST_PLANNING
                st.rerun()

    # ---------------- Tab 2: Test Planning ----------------
    with tab2:
        st.header("Test Planning")
        if st.session_state.stage == const.TEST_PLANNING:
            st.success("You are now in the Test Planning stage!")

            if "generated_test_plan" not in st.session_state:
                prompt = (
                    f"Project Name: {st.session_state.project_name}\n"
                    f"Requirements:\n" + "\n".join(st.session_state.requirements) + "\n\n"
                    "Based on the above, generate a detailed test plan for this project."
                )
                response = model.invoke(prompt)
                st.session_state.generated_test_plan = response.content

            test_plan = st.text_area(
                "Review or edit your generated test plan:",
                value=st.session_state.get("generated_test_plan", ""),
                height=300
            )
            if st.button("Save Test Plan", key="save_test_plan_btn"):
                st.session_state.test_plan = test_plan
                st.success("Test plan saved! Proceeding to Test Case Development...")
                st.session_state.stage = const.TEST_CASE_DEVELOPMENT
                st.rerun()
        elif st.session_state.stage != const.TEST_PLANNING and st.session_state.stage != const.PROJECT_INITILIZATION:
            st.info("Test plan already saved. Please proceed to the next stage.")

    # ---------------- Tab 3: Test Case Development ----------------
    with tab3:
        st.header("Test Case Development")
        if st.session_state.stage == const.TEST_CASE_DEVELOPMENT:
            st.success("You are now in the Test Case Development stage!")

            # Show agent's current goals
            st.subheader("Agent Goals")
            goals_summary = st.session_state.test_agent.goals.get_goal_summary()
            st.json(goals_summary)

            # Show learning progress
            st.subheader("Learning Progress")
            learning_summary = st.session_state.test_agent.get_learning_summary()
            st.json(learning_summary)

            if "generated_test_cases" not in st.session_state:
                # Generate test cases using agentic capabilities
                task = {
                    'type': 'generate_test_cases',
                    'requirements': st.session_state.requirements
                }
                result = st.session_state.test_agent.process_task(task)
                st.session_state.generated_test_cases = result['test_cases']

                # Show decision making process
                st.subheader("Decision Making Process")
                st.json(result['decision'])

                # Show coverage analysis
                st.subheader("Coverage Analysis")
                st.json(result['coverage'])

            test_cases = st.text_area(
                "Review or edit your generated test cases:",
                value=st.session_state.get("generated_test_cases", ""),
                height=300
            )
            if st.button("Save Test Cases", key="save_test_cases_btn"):
                st.session_state.test_cases = test_cases
                st.success("Test cases saved! Proceeding to Test Environment Setup...")
                st.session_state.stage = const.TEST_ENVIRONMENT_SETUP
                st.rerun()
        elif st.session_state.stage != const.TEST_CASE_DEVELOPMENT and st.session_state.stage != const.TEST_PLANNING and st.session_state.stage != const.PROJECT_INITILIZATION:
            st.info("Test cases already saved. Please proceed to the next stage.")

    # ---------------- Tab 4: Test Execution ----------------
    with tab4:
        st.header("Test Execution")
        if st.session_state.stage == const.TEST_EXECUTION:
            st.success("You are now in the Test Execution stage!")

            if "generated_test_execution" not in st.session_state:
                prompt = (
                    f"Project Name: {st.session_state.project_name}\n"
                    f"Requirements:\n" + "\n".join(st.session_state.requirements) + "\n"
                    f"Test Plan:\n{st.session_state.get('test_plan', '')}\n"
                    f"Test Cases:\n{st.session_state.get('test_cases', '')}\n"
                    f"Test Environment Setup:\n{st.session_state.get('test_env', '')}\n\n"
                    "Based on the above, generate a test execution strategy or checklist for this project."
                )
                response = model.invoke(prompt)
                st.session_state.generated_test_execution = response.content

            test_execution = st.text_area(
                "Review or edit your generated test execution strategy:",
                value=st.session_state.get("generated_test_execution", ""),
                height=300
            )
            if st.button("Save Test Execution", key="save_test_execution_btn"):
                st.session_state.test_execution = test_execution
                st.success("Test execution strategy saved! Proceeding to Test Closure...")
                st.session_state.stage = const.TEST_CLOSURE
                st.rerun()
        elif st.session_state.stage != const.TEST_EXECUTION and st.session_state.stage != const.TEST_ENVIRONMENT_SETUP and st.session_state.stage != const.TEST_CASE_DEVELOPMENT and st.session_state.stage != const.TEST_PLANNING and st.session_state.stage != const.PROJECT_INITILIZATION:
            st.info("Test execution strategy already saved. Please proceed to the next stage.")

    # ---------------- Tab 5: Test Closure ----------------
    with tab5:
        st.header("Test Closure")
        if st.session_state.stage == const.TEST_CLOSURE:
            st.success("You are now in the Test Closure stage!")

            if "generated_test_closure" not in st.session_state:
                prompt = (
                    f"Project Name: {st.session_state.project_name}\n"
                    f"Requirements:\n" + "\n".join(st.session_state.requirements) + "\n"
                    f"Test Plan:\n{st.session_state.get('test_plan', '')}\n"
                    f"Test Cases:\n{st.session_state.get('test_cases', '')}\n"
                    f"Test Environment Setup:\n{st.session_state.get('test_env', '')}\n"
                    f"Test Execution:\n{st.session_state.get('test_execution', '')}\n\n"
                    "Based on the above, generate a test closure summary or report for this project."
                )
                response = model.invoke(prompt)
                st.session_state.generated_test_closure = response.content

            test_closure = st.text_area(
                "Review or edit your generated test closure summary:",
                value=st.session_state.get("generated_test_closure", ""),
                height=300
            )
            if st.button("Save Test Closure", key="save_test_closure_btn"):
                st.session_state.test_closure = test_closure
                st.success("Test closure summary saved! You have completed the STLC process.")
        elif st.session_state.stage != const.TEST_CLOSURE and st.session_state.stage != const.TEST_EXECUTION and st.session_state.stage != const.TEST_ENVIRONMENT_SETUP and st.session_state.stage != const.TEST_CASE_DEVELOPMENT and st.session_state.stage != const.TEST_PLANNING and st.session_state.stage != const.PROJECT_INITILIZATION:
            st.info("Test closure already saved. You have completed the STLC process.")
        else:
            st.info("Please complete the previous step to proceed.")

    # ---------------- Tab 6: Agent Monitoring ----------------
    with tab6:
        st.header("Agent Monitoring")
        show_agent_monitoring(st.session_state.test_agent)

    return user_controls

def load_app():
    """
    Main entry point for the Streamlit app using tab-based UI.
    """
    config = Config()
    if 'stage' not in st.session_state:
        initialize_session()

    user_input = load_streamlit_ui(config)
    if not user_input:
        st.error("Error: Failed to load user input from the UI.")
        return

    try:
        # Configure LLM 
        selectedLLM = user_input.get("selected_llm")
        model = None
        if selectedLLM == "Gemini":
            obj_llm_config = GeminiLLM(user_controls_input=user_input)
            model = obj_llm_config.get_llm_model()
        elif selectedLLM == "Groq":
            obj_llm_config = GroqLLM(user_controls_input=user_input)
            model = obj_llm_config.get_llm_model()
        elif selectedLLM == "OpenAI":
            obj_llm_config = OpenAILLM(user_controls_input=user_input)
            model = obj_llm_config.get_llm_model()
        if not model:
            st.error("Error: LLM model could not be initialized.")
            return

        # Initialize TestCaseGeneratorAgent if not already initialized
        if not st.session_state.test_agent:
            try:
                st.session_state.test_agent = TestCaseGeneratorAgent(model)
            except Exception as e:
                st.error(f"Error initializing test agent: {str(e)}")
                return

        # Create tabs for different STLC stages
        tabs = st.tabs([
            "Requirement Analysis", 
            "Test Planning", 
            "Test Case Development",
            "Agent Monitoring",  # New tab for agent monitoring
            "Test Environment Setup", 
            "Test Execution", 
            "Test Closure", 
            "Download Artifacts"
        ])

        # Show agent progress and controls in sidebar
        if st.session_state.test_agent:
            show_agent_progress(st.session_state.test_agent)
            show_agent_controls(st.session_state.test_agent)

        # ---------------- Tab 1: Requirement Analysis ----------------
        with tabs[0]:
            st.header("Requirement Analysis")
            st.write("Please enter your project name and requirements to begin your STLC journey.")
            project_name = st.text_input("Enter the project name:", value=st.session_state.get("project_name", ""))
            requirements_input = st.text_area(
                "Enter the requirements. Write each requirement on a new line:",
                value="\n".join(st.session_state.get("requirements", []))
            )
            if st.button("Start STLC Process", key="start_stlc_btn"):
                if not project_name:
                    st.error("Please enter a project name.")
                elif not requirements_input.strip():
                    st.error("Please enter at least one requirement.")
                else:
                    requirements = [req.strip() for req in requirements_input.split("\n") if req.strip()]
                    st.session_state.project_name = project_name
                    st.session_state.requirements = requirements
                    st.success("Project details saved successfully!")
                    st.session_state.stage = const.TEST_PLANNING
                    st.rerun()

        # ---------------- Tab 2: Test Planning ----------------
        with tabs[1]:
            st.header("Test Planning")
            if st.session_state.stage == const.TEST_PLANNING:
                st.success("You are now in the Test Planning stage!")

                if "generated_test_plan" not in st.session_state:
                    prompt = (
                        f"Project Name: {st.session_state.project_name}\n"
                        f"Requirements:\n" + "\n".join(st.session_state.requirements) + "\n\n"
                        "Based on the above, generate a detailed test plan for this project."
                    )
                    response = model.invoke(prompt)
                    st.session_state.generated_test_plan = response.content

                test_plan = st.text_area(
                    "Review or edit your generated test plan:",
                    value=st.session_state.get("generated_test_plan", ""),
                    height=300
                )
                if st.button("Save Test Plan", key="save_test_plan_btn"):
                    st.session_state.test_plan = test_plan
                    st.success("Test plan saved! Proceeding to Test Case Development...")
                    st.session_state.stage = const.TEST_CASE_DEVELOPMENT
                    st.rerun()
            elif st.session_state.stage != const.TEST_PLANNING and st.session_state.stage != const.PROJECT_INITILIZATION:
                st.info("Test plan already saved. Please proceed to the next stage.")

        # ---------------- Tab 3: Test Case Development ----------------
        with tabs[2]:
            st.header("Test Case Development")
            if st.session_state.stage == const.TEST_CASE_DEVELOPMENT:
                st.success("You are now in the Test Case Development stage!")

                # Show agent's current goals
                st.subheader("Agent Goals")
                goals_summary = st.session_state.test_agent.goals.get_goal_summary()
                st.json(goals_summary)

                # Show learning progress
                st.subheader("Learning Progress")
                learning_summary = st.session_state.test_agent.get_learning_summary()
                st.json(learning_summary)

                if "generated_test_cases" not in st.session_state:
                    # Generate test cases using agentic capabilities
                    task = {
                        'type': 'generate_test_cases',
                        'requirements': st.session_state.requirements
                    }
                    result = st.session_state.test_agent.process_task(task)
                    st.session_state.generated_test_cases = result['test_cases']

                    # Show decision making process
                    st.subheader("Decision Making Process")
                    st.json(result['decision'])

                    # Show coverage analysis
                    st.subheader("Coverage Analysis")
                    st.json(result['coverage'])

                test_cases = st.text_area(
                    "Review or edit your generated test cases:",
                    value=st.session_state.get("generated_test_cases", ""),
                    height=300
                )
                if st.button("Save Test Cases", key="save_test_cases_btn"):
                    st.session_state.test_cases = test_cases
                    st.success("Test cases saved! Proceeding to Test Environment Setup...")
                    st.session_state.stage = const.TEST_ENVIRONMENT_SETUP
                    st.rerun()
            elif st.session_state.stage != const.TEST_CASE_DEVELOPMENT and st.session_state.stage != const.TEST_PLANNING and st.session_state.stage != const.PROJECT_INITILIZATION:
                st.info("Test cases already saved. Please proceed to the next stage.")

        # ---------------- Tab 4: Agent Monitoring ----------------
        with tabs[3]:
            st.header("Agent Monitoring")
            show_agent_monitoring(st.session_state.test_agent)

        # ---------------- Tab 5: Test Environment Setup ----------------
        with tabs[4]:
            st.header("Test Environment Setup")
            if st.session_state.stage == const.TEST_ENVIRONMENT_SETUP:
                st.success("You are now in the Test Environment Setup stage!")

                if "generated_test_env" not in st.session_state:
                    prompt = (
                        f"Project Name: {st.session_state.project_name}\n"
                        f"Requirements:\n" + "\n".join(st.session_state.requirements) + "\n"
                        f"Test Plan:\n{st.session_state.get('test_plan', '')}\n"
                        f"Test Cases:\n{st.session_state.get('test_cases', '')}\n\n"
                        "Based on the above, generate a recommended test environment setup for this project."
                    )
                    response = model.invoke(prompt)
                    st.session_state.generated_test_env = response.content

                test_env = st.text_area(
                    "Review or edit your generated test environment setup:",
                    value=st.session_state.get("generated_test_env", ""),
                    height=300
                )
                if st.button("Save Test Environment Setup", key="save_test_env_btn"):
                    st.session_state.test_env = test_env
                    st.success("Test environment setup saved! Proceeding to Test Execution...")
                    st.session_state.stage = const.TEST_EXECUTION
                    st.rerun()
            elif st.session_state.stage != const.TEST_ENVIRONMENT_SETUP and st.session_state.stage != const.TEST_CASE_DEVELOPMENT and st.session_state.stage != const.TEST_PLANNING and st.session_state.stage != const.PROJECT_INITILIZATION:
                st.info("Test environment setup already saved. Please proceed to the next stage.")

        # ---------------- Tab 6: Test Execution ----------------
        with tabs[5]:
            st.header("Test Execution")
            if st.session_state.stage == const.TEST_EXECUTION:
                st.success("You are now in the Test Execution stage!")

                if "generated_test_execution" not in st.session_state:
                    prompt = (
                        f"Project Name: {st.session_state.project_name}\n"
                        f"Requirements:\n" + "\n".join(st.session_state.requirements) + "\n"
                        f"Test Plan:\n{st.session_state.get('test_plan', '')}\n"
                        f"Test Cases:\n{st.session_state.get('test_cases', '')}\n"
                        f"Test Environment Setup:\n{st.session_state.get('test_env', '')}\n\n"
                        "Based on the above, generate a test execution strategy or checklist for this project."
                    )
                    response = model.invoke(prompt)
                    st.session_state.generated_test_execution = response.content

                test_execution = st.text_area(
                    "Review or edit your generated test execution strategy:",
                    value=st.session_state.get("generated_test_execution", ""),
                    height=300
                )
                if st.button("Save Test Execution", key="save_test_execution_btn"):
                    st.session_state.test_execution = test_execution
                    st.success("Test execution strategy saved! Proceeding to Test Closure...")
                    st.session_state.stage = const.TEST_CLOSURE
                    st.rerun()
            elif st.session_state.stage != const.TEST_EXECUTION and st.session_state.stage != const.TEST_ENVIRONMENT_SETUP and st.session_state.stage != const.TEST_CASE_DEVELOPMENT and st.session_state.stage != const.TEST_PLANNING and st.session_state.stage != const.PROJECT_INITILIZATION:
                st.info("Test execution strategy already saved. Please proceed to the next stage.")

        # ---------------- Tab 7: Test Closure ----------------
        with tabs[6]:
            st.header("Test Closure")
            if st.session_state.stage == const.TEST_CLOSURE:
                st.success("You are now in the Test Closure stage!")

                if "generated_test_closure" not in st.session_state:
                    prompt = (
                        f"Project Name: {st.session_state.project_name}\n"
                        f"Requirements:\n" + "\n".join(st.session_state.requirements) + "\n"
                        f"Test Plan:\n{st.session_state.get('test_plan', '')}\n"
                        f"Test Cases:\n{st.session_state.get('test_cases', '')}\n"
                        f"Test Environment Setup:\n{st.session_state.get('test_env', '')}\n"
                        f"Test Execution:\n{st.session_state.get('test_execution', '')}\n\n"
                        "Based on the above, generate a test closure summary or report for this project."
                    )
                    response = model.invoke(prompt)
                    st.session_state.generated_test_closure = response.content

                test_closure = st.text_area(
                    "Review or edit your generated test closure summary:",
                    value=st.session_state.get("generated_test_closure", ""),
                    height=300
                )
                if st.button("Save Test Closure", key="save_test_closure_btn"):
                    st.session_state.test_closure = test_closure
                    st.success("Test closure summary saved! You have completed the STLC process.")
            elif st.session_state.stage != const.TEST_CLOSURE and st.session_state.stage != const.TEST_EXECUTION and st.session_state.stage != const.TEST_ENVIRONMENT_SETUP and st.session_state.stage != const.TEST_CASE_DEVELOPMENT and st.session_state.stage != const.TEST_PLANNING and st.session_state.stage != const.PROJECT_INITILIZATION:
                st.info("Test closure already saved. You have completed the STLC process.")
            else:
                st.info("Please complete the previous step to proceed.")

        # ---------------- Tab 8: Download Artifacts ----------------
        with tabs[7]:
            st.header("Download Artifacts")
            if st.session_state.stage == const.TEST_CLOSURE and st.session_state.get("test_closure"):
                # Generate artifacts using MarkdownArtifactsNode
                markdown_node = MarkdownArtifactsNode()
                state = {
                    "project_name": st.session_state.get("project_name", "Project"),
                    "requirements": st.session_state.get("requirements", []),
                    "test_plan": st.session_state.get("test_plan", ""),
                    "test_cases": st.session_state.get("test_cases", ""),
                    "test_env": st.session_state.get("test_env", ""),
                    "test_execution": st.session_state.get("test_execution", ""),
                    "test_closure": st.session_state.get("test_closure", ""),
                }
                state = markdown_node.generate_markdown_artifacts(state)
                artifacts = state.get("artifacts", {})
                if artifacts:
                    st.subheader("Download Artifacts")
                    for artifact_name, artifact_path in artifacts.items():
                        if artifact_path:
                            with open(artifact_path, "rb") as f:
                                file_bytes = f.read()
                            st.download_button(
                                label=f"Download {artifact_name}",
                                data=file_bytes,
                                file_name=artifact_path.split("/")[-1],
                                mime="application/octet-stream"
                            )
                        else:
                            st.info(f"{artifact_name} not available.")
                else:
                    st.info("No artifacts generated yet.")
            else:
                st.info("Artifacts will be available after completing all STLC stages.")

    except Exception as e:
        raise ValueError(f"Error occurred with Exception : {e}")
    