import os
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_openai import OpenAI
from langchain_core.tools import Tool
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
from gmail_helper import get_most_recent_email
from game_maker import make_game  # Assuming this is your updated game_generator.py

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Define the state structure
class AgentState(TypedDict):
    messages: Annotated[Sequence[AIMessage | HumanMessage], "The messages in the conversation"]
    called_tools: Annotated[set, "Tools called during this run"]

# Initialize the language model
llm = OpenAI(temperature=0)

# Tool definitions with state as an explicit parameter
def make_game_tool(input_string: str, state: AgentState) -> str:
    """A tool that generates a simple game based on user input."""
    if "GameGenerator" in state["called_tools"]:
        return "The GameGenerator tool has already been called."
    state["called_tools"].add("GameGenerator")
    result = make_game(input_string)
    return "[FINAL] Game created successfully" if result == "Successfully created game" else result

def recent_email(_: str, state: AgentState) -> str:
    """A tool that reads the most recent email subject line and snippet."""
    if "GmailReader" in state["called_tools"]:
        return "The GmailReader tool has already been called."
    state["called_tools"].add("GmailReader")
    return get_most_recent_email()

def add(input_string: str, state: AgentState) -> str:
    """A simple calculator tool that adds two integers."""
    if "Calculator" in state["called_tools"]:
        return "The Calculator tool has already been called."
    state["called_tools"].add("Calculator")
    
    # First, try parsing numbers separated by commas
    try:
        if ',' in input_string:
            numbers = [int(num.strip()) for num in input_string.split(',')]
            if len(numbers) == 2:
                return f"The sum of {numbers[0]} and {numbers[1]} is {numbers[0] + numbers[1]}."
    except ValueError:
        pass
    
    # Next, try to extract numbers when separated by a + sign
    try:
        if '+' in input_string:
            parts = input_string.split('+')
            # Extract digits from each part
            num1 = int(''.join(c for c in parts[0] if c.isdigit()))
            num2 = int(''.join(c for c in parts[1] if c.isdigit()))
            return f"The sum of {num1} and {num2} is {num1 + num2}."
    except (ValueError, IndexError):
        pass
    
    # Finally, try to extract any two numbers from the string
    import re
    numbers = [int(num) for num in re.findall(r'\d+', input_string)]
    if len(numbers) >= 2:
        return f"The sum of {numbers[0]} and {numbers[1]} is {numbers[0] + numbers[1]}."
    
    return "I couldn't identify two numbers to add. Please provide two numbers separated by a comma or '+' sign."

# Define tools, passing state explicitly
def create_tools(state: AgentState):
    return {
        "Calculator": Tool(
            name="Calculator",
            func=lambda x: add(x, state),
            description="Adds two numbers. Input: two integers separated by a comma (e.g., '3, 4')"
        ),
        "GmailReader": Tool(
            name="GmailReader",
            func=lambda _: recent_email("", state),
            description="Reads the most recent email subject line and snippet. No input needed."
        ),
        "GameGenerator": Tool(
            name="GameGenerator",
            func=lambda x: make_game_tool(x, state),
            description="Generates an HTML game based on input (e.g., 'snake'). Opens in browser when done."
        )
    }

# Define the agent node
def agent_node(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1].content
    tools = create_tools(state)  # Create tools with the current state
    
    # Simple logic to determine which tool to call based on input
    if "addition" in last_message.lower() or "add" in last_message.lower() or "+" in last_message or "plus" in last_message.lower() or "sum" in last_message.lower() or (any(char.isdigit() for char in last_message) and ("what is" in last_message.lower() or "calculate" in last_message.lower())):
        tool_response = tools["Calculator"].func(last_message)
    elif "email" in last_message.lower():
        tool_response = tools["GmailReader"].func("")
    elif "game" in last_message.lower():
        tool_response = tools["GameGenerator"].func(last_message.split("game")[-1].strip())
    else:
        tool_response = "I'm not sure what to do with that input. I can add numbers, check emails, or make games!"

    return {
        "messages": messages + [AIMessage(content=tool_response)],
        "called_tools": state["called_tools"]
    }

# Build the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent", agent_node)

# Set entry point and finish condition
workflow.set_entry_point("agent")
workflow.add_edge("agent", END)

# Compile the graph
graph = workflow.compile()

# Function to run the graph
def run_agent(user_input: str):
    initial_state = {
        "messages": [HumanMessage(content=user_input)],
        "called_tools": set()
    }
    result = graph.invoke(initial_state)
    return result["messages"][-1].content

def run_agent(user_input: str):
    initial_state = {
        "messages": [HumanMessage(content=user_input)],
        "called_tools": set()
    }
    result = graph.invoke(initial_state)
    return result["messages"][-1].content

# Add this function for Streamlit integration:
def chat(prompt: str) -> str:
    return run_agent(prompt)

# Get user input and run
if __name__ == "__main__":
    user_input = input("Enter your query (e.g., do simple addition, check most recent email, build a html game): ")
    response = run_agent(user_input)
    print("Response:", response)