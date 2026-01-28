"""Simple end-to-end demo with math agents and orchestrator."""
import os
from microAgents.llm import LLM
from microAgents.core import MicroAgent, Tool, BaseMessageStore

# Initialize LLM with Qwen 3 Coder as requested
# Using the API key from .env (assuming it's loaded or hardcoded for test)
# For this standalone test, I'll attempt to load from env or use a placeholder if not set
api_key = os.getenv("OPENROUTER_API_KEY", "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") 

math_llm = LLM(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    model="moonshotai/kimi-k2.5", # Using the requested model
    max_tokens=4000,
    temperature=0.1, # Using low temp for reliability
    top_p=0.9
)

# Define tools
def add_numbers(a: float, b: float) -> float:
    """Adds two numbers together."""
    return a + b

def multiply_numbers(a: float, b: float) -> float:
    """Multiplies two numbers together."""
    return a * b

def factorial(n: int) -> int:
    """Calculates factorial of a number."""
    if n == 0:
        return 1
    if n < 0:
        return 0 # Handle edge case
    return n * factorial(n - 1)

# Create agents
simple_math_agent = MicroAgent(
    llm=math_llm,
    prompt="""You are a simple math assistant. Handle basic arithmetic operations.""",
    toolsList=[
        Tool(description="Adds two numbers", func=add_numbers),
        Tool(description="Multiplies two numbers", func=multiply_numbers)
    ]
)

advanced_math_agent = MicroAgent(
    llm=math_llm,
    prompt="""You are an advanced math assistant. Handle complex math operations.""",
    toolsList=[
        Tool(description="Calculates factorial", func=factorial)
    ]
)

class Orchestrator(MicroAgent):
    def __init__(self):
        super().__init__(
            llm=math_llm,
            prompt="""You are a math query analyzer. For each query:
1. If it contains basic arithmetic (addition, subtraction, multiplication, division), output exactly: SIMPLE_MATHS NEEDED
2. If it contains advanced math (factorials, exponents, logarithms, derivatives, integrals), output exactly: ADVANCED_MATHS NEEDED
3. If unsure, output exactly: UNKNOWN_MATH_TYPE

Examples:
- "What is 5 plus 3?" → SIMPLE_MATHS NEEDED
- "Calculate 10 factorial" → ADVANCED_MATHS NEEDED
- "Solve x^2 + 2x + 1 = 0" → UNKNOWN_MATH_TYPE

Always output exactly one of these three options, nothing else.""",
            toolsList=[]
        )
        self.simple_math_agent = simple_math_agent
        self.advanced_math_agent = advanced_math_agent

    def execute_agent(self, query: str, message_store: BaseMessageStore) -> str:
        """Handle full query flow through orchestrator."""
        print(f"\nDebug: Orchestrator analyzing query: {query}")
        
        # Get initial analysis from orchestrator
        # Note: In the user's example they call super().execute_agent
        analysis = super().execute_agent(query, message_store)
        print(f"Debug: Orchestrator analysis result: {analysis}")
        
        if "SIMPLE_MATHS NEEDED" in analysis:
            print("Debug: Routing to Simple Math Agent")
            result = self.simple_math_agent.execute_agent(query, message_store)
            print(f"Debug: Simple Math Agent result: {result}")
            return self._format_result("Simple Math Agent", result)
        elif "ADVANCED_MATHS NEEDED" in analysis:
            print("Debug: Routing to Advanced Math Agent")
            result = self.advanced_math_agent.execute_agent(query, message_store)
            print(f"Debug: Advanced Math Agent result: {result}")
            return self._format_result("Advanced Math Agent", result)
        else:
            return "Orchestrator: Unable to determine the appropriate agent for this query."

    def _format_result(self, agent_name: str, result: str) -> str:
        """Format the final result from an agent."""
        return f"Orchestrator: Result from {agent_name}:\n{result}"

def main():
    message_store = BaseMessageStore()
    orchestrator = Orchestrator()
    
    # Example queries that demonstrate XML-style tool calls
    queries = [
        "What is 15 plus 27?", 
        "Calculate 5 factorial",  
        # "Multiply 8 by 9", 
        # "First add 3 and 5, then multiply the result by 2"
    ]
    
    for query in queries:
        print(f"\nUser: {query}")
        try:
            response = orchestrator.execute_agent(query, message_store)
            print(f"{response}")
        except Exception as e:
            print(f"ERROR executing query: {e}")

if __name__ == "__main__":
    main()
