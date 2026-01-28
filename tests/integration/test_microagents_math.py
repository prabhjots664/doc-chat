import os
from microAgents.llm import LLM
from microAgents.core import MicroAgent, Tool, BaseMessageStore
from dotenv import load_dotenv

load_dotenv()

# Setup LLM - Using the provided free model
llm = LLM(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="z-ai/glm-4.5-air:free"
)

# Define tools
def add_numbers(a: float, b: float) -> float:
    """Adds two numbers together."""
    print(f"--- [Tool]: add_numbers({a}, {b}) ---")
    return a + b

def multiply_numbers(a: float, b: float) -> float:
    """Multiplies two numbers together."""
    print(f"--- [Tool]: multiply_numbers({a}, {b}) ---")
    return a * b

# Create agent
math_agent = MicroAgent(
    llm=llm,
    prompt="You are a math assistant. Handle basic arithmetic operations using tools.",
    toolsList=[
        Tool(description="Adds two numbers", func=add_numbers),
        Tool(description="Multiplies two numbers", func=multiply_numbers)
    ]
)

def main():
    message_store = BaseMessageStore()
    
    # Test query
    query = "First add 3 and 5, then multiply the result by 2"
    print(f"\nUser: {query}")
    
    try:
        response = math_agent.execute_agent(query, message_store)
        print(f"\nAgent: {response}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
