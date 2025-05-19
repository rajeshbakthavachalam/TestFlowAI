# TestFlow AI

TestFlow AI is an AI-powered assistant for the Software Testing Life Cycle (STLC). It helps you automate and manage all phases of software testing, from requirements analysis to test closure, using advanced language models.

## Features
- **LLM-powered test planning and case generation**
- **Goal tracking and coverage analysis**
- **Downloadable artifacts for each STLC phase**
- **Modern Gradio UI**

## STLC Phases Supported
- Requirement Analysis
- Test Planning
- Test Case Development
- Test Environment Setup
- Test Execution
- Test Closure
- Download Artifacts (for all phases)

## Installation
1. Clone the repository:
   ```sh
   git clone <your-repo-url>
   cd Agentic-STLC
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```sh
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage
1. Run the Gradio app:
   ```sh
   python app_gradio.py
   ```
2. Open the local URL shown in your terminal (e.g., http://127.0.0.1:7860) in your browser.
3. Go through each STLC phase using the tabs:
   - Configure your LLM and API key
   - Enter requirements, generate test plans and test cases
   - Analyze coverage and save each phase
   - Download artifacts for each phase in the "Download Artifacts" tab

## Downloading Artifacts
After completing the STLC phases, go to the **Download Artifacts** tab. Click "Generate & Refresh Artifacts" and download markdown files for:
- Requirement Analysis
- Test Planning
- Test Case Development
- Test Environment Setup
- Test Execution
- Test Closure

## Notes
- The app is now branded as **TestFlow AI** (formerly AgenticSTLC).
- For LLM features, you must provide a valid API key for your selected provider (OpenAI, Gemini, or Groq).

## License
[MIT License](LICENSE)

# Using the original LLM implementation
llm_agent = AgentFactory.create_agent(
    agent_type="test_case_generator",
    implementation="llm",
    api_key="your_api_key",
    model="gpt-4"
)

# Using the new agentic implementation
agentic_agent = AgentFactory.create_agent(
    agent_type="test_case_generator",
    implementation="agentic",
    api_key="your_api_key",
    model="gpt-4"
)

# The agentic agent can now:
# 1. Learn from experiences
agentic_agent.learn_from_test_results({
    "test_id": "123",
    "result": "passed",
    "coverage": 0.85
})

# 2. Make autonomous decisions
test_cases = agentic_agent.generate_test_cases([
    "User should be able to login",
    "User should be able to logout"
])

# 3. Analyze coverage
coverage = agentic_agent.analyze_coverage(test_cases)

# Example usage
agent = TestCaseGeneratorAgent(llm_model)

# Make a decision
decision = agent.make_decision({
    'type': 'test_prioritization',
    'test_cases': [
        {'id': 'TC1', 'priority': 'high'},
        {'id': 'TC2', 'priority': 'medium'}
    ],
    'time_constraint': '2 hours'
})

"# TestFlowAI" 
