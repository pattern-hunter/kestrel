import asyncio
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from mcp_use import MCPAgent, MCPClient
from dotenv import load_dotenv, find_dotenv
from langchain_core.callbacks import BaseCallbackHandler
load_dotenv(find_dotenv(), override=True)
from typing import Tuple
import time


class TokenUsageTracker(BaseCallbackHandler):
    """Track and aggregate token usage across LLM calls via LangChain callbacks."""
    
    def __init__(self):
        super().__init__()
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.call_count = 0
    
    def on_llm_end(self, response, **kwargs):
        """Called after an LLM call completes. Extracts token counts from response."""
        self.call_count += 1

        for generation in response.generations:
            for gen in generation:
                if hasattr(gen, 'message') and hasattr(gen.message, 'usage_metadata'):
                    usage = gen.message.usage_metadata
                    self.total_input_tokens += usage.get('input_tokens', 0)
                    self.total_output_tokens += usage.get('output_tokens', 0)

        # For Ollama (if usage metadata is structured differently, adjust accordingly)
        # response.__dict__['generations'][0][0].__dict__['message'].__dict__['usage_metadata']['total_tokens']
    
    def get_total_tokens(self):
        """Return total tokens used (input + output)."""
        return self.total_input_tokens + self.total_output_tokens
    
    def get_summary(self):
        """Return a summary of token usage."""
        return {
            'input_tokens': self.total_input_tokens,
            'output_tokens': self.total_output_tokens,
            'total_tokens': self.get_total_tokens(),
            'llm_calls': self.call_count
        }


async def _run_agent(model: str, prompt: str) -> Tuple[int, int]:
    start = time.time()
    # Create configuration dictionary
    config = {
      "mcpServers": {
        "nasa": {
          "command": "python",
          "args": ["benchmarking/services/nasa_iss_locator/client.py"],
        },
        "geocoding": {
          "command": "python",
          "args": ["benchmarking/services/geocoding/client.py"],
        }
      }
    }

    # Create MCPClient from configuration dictionary
    client = MCPClient.from_dict(config)

    # Create LLM and token tracker callback
    # llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    if model.startswith("gemini"):
        llm = ChatGoogleGenerativeAI(model=model, temperature=0)
    else:
        llm = ChatOllama(model=model)
    token_tracker = TokenUsageTracker()

    # Create agent with callbacks to track token usage
    agent = MCPAgent(llm=llm, client=client, max_steps=30, callbacks=[token_tracker])

    # Run the query
    result = await agent.run(
        prompt,
    )
    
    summary = token_tracker.get_summary()
    return summary['total_tokens'], int(time.time() - start)

def run_agent(model: str, prompt: str) -> Tuple[int, int]:
    return asyncio.run(_run_agent(model=model, prompt=prompt))