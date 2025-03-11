# LangGraph Agent Framework

A modular agent framework built with LangGraph and LangChain that dynamically calls tools based on user input. Currently includes a calculator, a Gmail reader, and an HTML game generator.

## Quick Start

1. **Clone and setup**
   ```bash
   git clone <repository-url> && cd <repository-directory>
   python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure and run**
   ```bash
   # Create .env file with your OpenAI API key
   echo "OPENAI_API_KEY=your_key_here" > .env
   
   # Run without Gmail integration
   python lang_no_gmail.py
   # OR with Gmail (requires additional setup)
   python lang.py
   ```

3. **Try it out**
   - Addition: "What is 5 + 10"
   - Game creation: "Make a game about snake"
   - Email (full version only): "Check my most recent email"

## Core Functionality

This framework creates an agent that routes user requests to the appropriate tool:

- **Calculator**: Adds two numbers from natural language input
- **Game Generator**: Creates HTML5 games using OpenAI's API
- **Gmail Reader** (optional): Fetches your most recent email

The agent uses keyword matching to determine which tool to call and maintains state to track which tools have been used.

## Setup Details

### Prerequisites
- Python 3.8+
- OpenAI API Key
- Google Cloud API credentials (Gmail integration only)

### Gmail Setup (Optional)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable Gmail API
3. Create OAuth 2.0 credentials (Desktop application)
4. Download and rename to `credentials.json` in project root
5. First run will open browser for authentication

## Extending the Framework

Add your own tools in three steps:

1. **Define a tool function**
   ```python
   def my_new_tool(input_string: str, state: AgentState) -> str:
       if "MyToolName" in state["called_tools"]:
           return "This tool has already been called."
       state["called_tools"].add("MyToolName")
       
       # Your implementation here
       return result
   ```

2. **Add to tools dictionary**
   ```python
   def create_tools(state: AgentState):
       return {
           # ... existing tools ...
           "MyToolName": Tool(
               name="MyToolName",
               func=lambda x: my_new_tool(x, state),
               description="Tool description"
           )
       }
   ```

3. **Update detection logic in agent_node function**

## Notes

- Each tool can only be called once per agent run
- The game generator is experimental and demonstrates generative AI capabilities
- For simpler setup without Gmail, use `lang_no_gmail.py`
- The framework can be extended with more sophisticated routing logic

This project is open source and available under the MIT License. 