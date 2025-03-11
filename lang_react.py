import os
from langchain.agents import initialize_agent, Tool, AgentType
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from game_maker import make_game

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Define Tools
def generate_game(game_name: str):
    result = make_game(game_name.lower())
    if result == "Successfully created game":
        return f"Game '{game_name}' created successfully!"
    else:
        return f"Failed to create game '{game_name}'."

def calculator(input_string: str):
    try:
        if ',' in input_string:
            numbers = [int(num.strip()) for num in input_string.split(',')]
        elif '+' in input_string:
            numbers = [int(''.join(filter(str.isdigit, part))) for part in input_string.split('+')]
        else:
            return "Could not parse two numbers clearly."
        
        if len(numbers) != 2:
            return "Provide exactly two numbers."
        return f"The sum of {numbers[0]} and {numbers[1]} is {numbers[0] + numbers[1]}."
    except:
        return "Please provide two valid integers separated by a comma or '+' sign."

# Define tools explicitly with clear descriptions
tools = [
    Tool(
        name="Calculator",
        func=calculator,
        description="Perform addition when exactly two numbers are provided, e.g., 'calculate 2+2'.",
    ),
    Tool(
        name="GameGenerator",
        func=generate_game,
        description="Creates a simple HTML game. Supported games: snake, tetris, flappy bird.",
    ),
]

# Load environment variables and initialize the OpenAI Chat Model
llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o")

# Initialize the Structured ReAct-style agent for multiple tool calls
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True,
    max_iterations=2,  # Avoid repeated calls
    verbose=True,
)

# Chat function to interact with agent
def chat(prompt: str) -> str:
    result = agent.invoke({"input": prompt})
    return result.get("output", "No valid response.")

# Run the agent interactively
if __name__ == "__main__":
    user_input = input("Enter your query (e.g., 'calculate 2+3', 'build a snake game', or 'calculate 2+3 and build a snake game'): ")
    response = chat(user_input)
    print("Response:", response)
