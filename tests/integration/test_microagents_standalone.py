import os
import sys
from microAgents.llm import LLM
from microAgents.core import MicroAgent, Tool, BaseMessageStore
from dotenv import load_dotenv

load_dotenv()

# API configuration
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "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")
MODEL = "z-ai/glm-4.5-air:free"

def test_tool_calling():
    print("=" * 60)
    print("Testing microAgents Standalone Tool Calling")
    print("=" * 60)

    # 1. Setup LLM
    # microAgents LLM appends /chat/completions to base_url
    llm = LLM(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_KEY,
        model=MODEL
    )

    # 2. Define a simple tool
    def get_current_time(location: str) -> str:
        """Returns the current time for a given location."""
        print(f"--- [Tool Called]: get_current_time(location='{location}') ---")
        return f"The current time in {location} is 10:30 PM."

    time_tool = Tool(
        description="Get the current time for a specific location. Input: location (str)",
        func=get_current_time
    )

    # 3. Initialize Agent
    agent = MicroAgent(
        llm=llm,
        prompt=(
            "You are a helpful assistant with access to tools. "
            "If you need to know the time, use the 'get_current_time' tool. "
            "Once you have the answer, provide it to the user."
        ),
        toolsList=[time_tool]
    )

    # 4. Message store
    message_store = BaseMessageStore()

    # 5. Execute
    user_query = "What time is it in London?"
    print(f"User Query: {user_query}")
    
    try:
        response = agent.execute_agent(user_query, message_store)
        print(f"\nAgent Final Response: {response}")
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tool_calling()
