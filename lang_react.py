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
    result = make_game(game_name)
    return "Game created successfully!" if result == "Successfully created game" else "Failed to create game."

def calculator(input_string: str):
    # Handle commas and plus signs
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

# Define your tools
tools = [
    Tool(
        name="Calculator",
        func=calculator,
        description="Use for performing addition when two numbers are given.",
    ),
    Tool(
        name="GameGenerator",
        func=make_game,
        description="Creates a simple HTML game when requested (e.g., 'snake', 'tetris').",
    ),
]

# Initialize your agent with OpenAI Chat Model
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(api_key=openai_api_key, model="gpt-4o")

# Use ReAct-style agent
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

# Run the agent
if __name__ == "__main__":
    user_input = input("Enter your query (e.g., 'calculate 2+3' or 'build a snake game'): ")
    response = agent.run(user_input)
    print("Response:", response)
