# LangGraph and LangChain Agent Framework

A modular agent framework built with LangGraph and LangChain that dynamically calls tools based on user input. Currently includes a calculator, a Gmail reader, an HTML game generator, and a Wikipedia information retrieval tool.

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
   
   # Choose one of these implementations:
   # Standard implementation without Gmail
   python lang_no_gmail.py
   # Full implementation with Gmail (requires additional setup)
   python lang.py
   # ReAct implementation (recommended for more complex reasoning)
   python lang_react.py
   
   # Or use the Streamlit UI to access all agents
   streamlit run agent_chat_ui.py
   ```

3. **Try it out**
   - Addition: "What is 5 + 10"
   - Game creation: "Make a game about snake"
   - Wikipedia lookup: "What is Python programming"
   - Email (full version only): "Check my most recent email"

## Streamlit UI

The project includes a unified chat interface built with Streamlit that allows you to interact with all agent implementations in one place:

1. **Start the UI**
   ```bash
   streamlit run agent_chat_ui.py
   ```

2. **Select an agent**
   - Use the dropdown menu in the sidebar to switch between different agent implementations:
     - "Lang Agent" (with Gmail, game creation, and calculator)
     - "Lang React" (ReAct implementation with game creation and calculator)
     - "Lang No Gmail" (standard agent without Gmail)

3. **Chat with the agent**
   - Type your queries in the chat input field
   - View the conversation history in the main area
   - Seamlessly switch between different agent implementations

The UI maintains separate chat sessions for each agent, making it easy to compare their responses to the same queries.

### Making Your Custom Agents UI-Compatible

If you create your own agent implementation, you can integrate it with the Streamlit UI by:

1. **Add a chat function to your agent file**:
   ```python
   def chat(prompt: str) -> str:
       # Call your agent's main function here
       return run_agent(prompt)  # Or whatever your agent's main function is
   ```

2. **Register it in agent_chat_ui.py**:
   ```python
   AGENT_SCRIPTS = {
       # Existing agents...
       "Your Agent Name": "your_agent_file_name_without_py",
   }
   ```

## Core Functionality

This framework creates an agent that routes user requests to the appropriate tool:

- **Calculator**: Adds two numbers from natural language input
- **Game Generator**: Creates HTML5 games using OpenAI's API
- **Wikipedia Tool**: Retrieves summary information from Wikipedia
- **Gmail Reader** (optional): Fetches your most recent email

The agent uses keyword matching to determine which tool to call and maintains state to track which tools have been used.

## Implementation Options

The framework provides three different implementations:

1. **Standard (lang.py)**: Uses LangGraph for workflow management with Gmail integration
2. **Simplified (lang_no_gmail.py)**: Same as standard but without Gmail functionality
3. **ReAct (lang_react.py)**: Uses LangChain's ReAct agent pattern for more sophisticated reasoning

All implementations include the Calculator, Game Generator, and Wikipedia tools, while only the standard implementation includes Gmail functionality.

### Benefits of ReAct Implementation

The ReAct implementation offers several advantages:

- **Better reasoning**: Uses a think-act-observe loop for improved decision-making
- **Dynamic tool selection**: Agent autonomously decides which tool to use based on the query
- **Explainable actions**: Provides reasoning for each step in its decision process
- **More flexible parsing**: Better handling of ambiguous or complex queries

Choose the ReAct implementation when working with complex tasks that require multi-step reasoning.

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

   For ReAct implementation, you only need to register the tool - the agent handles detection automatically.

### Example: Wikipedia Tool Integration

The Wikipedia tool demonstrates how to integrate external APIs:

```python
# 1. Import the underlying functionality
from wiki import wiki_summary

# 2. Create a stateful wrapper function
def wiki_tool(input_string: str, state: AgentState) -> str:
    """A tool that fetches summaries from Wikipedia."""
    if "WikiTool" in state["called_tools"]:
        return "The WikiTool has already been called."
    state["called_tools"].add("WikiTool")
    return wiki_summary(input_string)

# 3. Add to tools dictionary
"WikiTool": Tool(
    name="WikiTool",
    func=lambda x: wiki_tool(x, state),
    description="Gets a summary from Wikipedia. Input: a topic to search for."
)

# 4. Update detection logic (in standard implementations)
elif any(wiki_trigger in last_message.lower() for wiki_trigger in ["what is", "who is", "tell me about", "wikipedia", "wiki"]):
    # Extract the topic after the trigger phrase
    for trigger in ["what is", "who is", "tell me about", "wikipedia", "wiki"]:
        if trigger in last_message.lower():
            topic = last_message.lower().split(trigger)[-1].strip()
            if topic:
                tool_response = tools["WikiTool"].func(topic)
                break
```

## Notes

- Each tool can only be called once per agent run
- The game generator is experimental and demonstrates generative AI capabilities
- The Wikipedia tool provides quick access to factual information
- For simpler setup without Gmail, use `lang_no_gmail.py`
- For more complex reasoning tasks, use `lang_react.py`
- The framework can be extended with more sophisticated routing logic

This project is open source and available under the MIT License. 
